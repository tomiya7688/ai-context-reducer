package main

import (
	"net"
	"strings"
	"testing"
)

// TestSessionTokenIsNonEmpty はlocalhost API保護tokenが十分な長さで生成されることを確認します。
func TestSessionTokenIsNonEmpty(t *testing.T) {
	token, err := sessionToken()
	if err != nil {
		t.Fatal(err)
	}
	if len(token) != 48 || strings.Trim(token, "0123456789abcdef") != "" {
		t.Fatalf("unexpected token: %q", token)
	}
}

// TestListenLoopbackAcceptsOnlyLocalAddressesは指定addressと解決後IPがloopbackに限られることを確認します。
func TestListenLoopbackAcceptsOnlyLocalAddresses(t *testing.T) {
	allowed := []string{"127.0.0.1:0", "localhost:0", "[::1]:0"}
	for _, address := range allowed {
		t.Run(address, func(t *testing.T) {
			listener, err := listenLoopback(address)
			if err != nil {
				if address == "[::1]:0" {
					t.Skipf("IPv6 loopback is unavailable: %v", err)
				}
				t.Fatal(err)
			}
			defer listener.Close()
			bound, ok := listener.Addr().(*net.TCPAddr)
			if !ok || bound.IP == nil || !bound.IP.IsLoopback() {
				t.Fatalf("listener bound outside loopback: %#v", listener.Addr())
			}
		})
	}
}

// TestListenLoopbackRejectsWildcardAndRemoteAddressesは外部接続可能なbind指定を拒否します。
func TestListenLoopbackRejectsWildcardAndRemoteAddresses(t *testing.T) {
	rejected := []string{
		":0",
		"0.0.0.0:0",
		"[::]:0",
		"192.0.2.1:8080",
		"example.com:80",
		"localhost.example.com:80",
		"127.0.0.1",
	}
	for _, address := range rejected {
		t.Run(address, func(t *testing.T) {
			listener, err := listenLoopback(address)
			if listener != nil {
				listener.Close()
			}
			if err == nil {
				t.Fatalf("listenLoopback(%q) unexpectedly succeeded", address)
			}
		})
	}
}
