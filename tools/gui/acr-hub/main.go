package main

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"flag"
	"fmt"
	"log"
	"net"
	"net/http"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"runtime"
	"strings"
	"syscall"
	"time"

	"github.com/tomiya7688/ai-context-reducer/tools/gui/acr-hub/backend"
	"github.com/tomiya7688/ai-context-reducer/tools/gui/acr-hub/ui"
)

const defaultListenAddress = "127.0.0.1:0"

// main はself-contained GUI Hub serverをloopback interfaceへ起動します。
func main() {
	if err := run(); err != nil {
		log.Printf("acr-hub: %v", err)
		os.Exit(1)
	}
}

// run はbundle root解決・HTTP起動・graceful shutdownをまとめます。
func run() error {
	var bundleRoot string
	var listenAddress string
	var initialProject string
	var noOpen bool
	flag.StringVar(&bundleRoot, "bundle-root", "", "Full Bundle root containing acr-toolbox and standalone binaries")
	flag.StringVar(&listenAddress, "listen", defaultListenAddress, "localhost or loopback IP listen address")
	flag.StringVar(&initialProject, "project", "", "initial project root shown in the UI")
	flag.BoolVar(&noOpen, "no-open", false, "do not attempt to open the default browser")
	flag.Parse()
	listener, err := listenLoopback(listenAddress)
	if err != nil {
		return err
	}
	defer listener.Close()

	if bundleRoot == "" {
		resolved, err := detectBundleRoot()
		if err != nil {
			return err
		}
		bundleRoot = resolved
	}
	token, err := sessionToken()
	if err != nil {
		return err
	}
	runner := backend.NewRunner(backend.BundleResolver{Root: bundleRoot})
	handler, err := (ui.Server{Invoker: runner, SessionToken: token, InitialProject: initialProject}).Handler()
	if err != nil {
		return err
	}
	server := &http.Server{Handler: handler, ReadHeaderTimeout: 5 * time.Second}
	url := "http://" + listener.Addr().String() + "/"
	fmt.Printf("AI Context Reducer Hub: %s\n", url)
	fmt.Printf("Bundle root: %s\n", bundleRoot)
	if !noOpen {
		if err := openBrowser(url); err != nil {
			log.Printf("browser was not opened automatically: %v", err)
		}
	}

	errCh := make(chan error, 1)
	go func() {
		errCh <- server.Serve(listener)
	}()

	signals := make(chan os.Signal, 1)
	signal.Notify(signals, os.Interrupt, syscall.SIGTERM)
	defer signal.Stop(signals)

	select {
	case err := <-errCh:
		if err != nil && err != http.ErrServerClosed {
			return err
		}
		return nil
	case <-signals:
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		return server.Shutdown(ctx)
	}
}

// listenLoopbackはloopback以外へbindしないよう入力hostと実際の解決先の両方を検査します。
func listenLoopback(address string) (net.Listener, error) {
	host, _, err := net.SplitHostPort(address)
	if err != nil {
		return nil, fmt.Errorf("invalid listen address: %w", err)
	}
	ip := net.ParseIP(host)
	if !strings.EqualFold(host, "localhost") && (ip == nil || !ip.IsLoopback()) {
		return nil, fmt.Errorf("listen address must use localhost or a loopback IP address")
	}
	tcpAddress, err := net.ResolveTCPAddr("tcp", address)
	if err != nil {
		return nil, fmt.Errorf("resolve listen address: %w", err)
	}
	if tcpAddress.IP == nil || !tcpAddress.IP.IsLoopback() {
		return nil, fmt.Errorf("resolved listen address must be a loopback IP address")
	}
	listener, err := net.ListenTCP("tcp", tcpAddress)
	if err != nil {
		return nil, fmt.Errorf("listen: %w", err)
	}
	return listener, nil
}

// detectBundleRoot はgui/acr-hub実行fileの1階層上をFull Bundle rootとして解決します。
func detectBundleRoot() (string, error) {
	executable, err := os.Executable()
	if err != nil {
		return "", fmt.Errorf("resolve executable: %w", err)
	}
	executable, err = filepath.EvalSymlinks(executable)
	if err != nil {
		return "", fmt.Errorf("resolve executable symlink: %w", err)
	}
	guiDir := filepath.Dir(executable)
	return filepath.Clean(filepath.Join(guiDir, "..")), nil
}

// sessionToken はloopback上の別originからCLI実行APIを直接叩けないようrandom tokenを作ります。
func sessionToken() (string, error) {
	raw := make([]byte, 24)
	if _, err := rand.Read(raw); err != nil {
		return "", fmt.Errorf("create session token: %w", err)
	}
	return hex.EncodeToString(raw), nil
}

// openBrowser はOS標準のURL openerをbest-effortで呼び、失敗してもserver自体は維持します。
func openBrowser(url string) error {
	var command *exec.Cmd
	switch runtime.GOOS {
	case "windows":
		command = exec.Command("cmd", "/c", "start", "", url)
	case "darwin":
		command = exec.Command("open", url)
	default:
		command = exec.Command("xdg-open", url)
	}
	return command.Start()
}
