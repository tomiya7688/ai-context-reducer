package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

func main() {
	if len(os.Args) == 2 && (strings.EqualFold(os.Args[1], "py") || strings.EqualFold(os.Args[1], "python")) {
		if strings.EqualFold(os.Args[1], "python") {
			os.Exit(0)
		}
		os.Exit(1)
	}

	command := ""
	if len(os.Args) > 1 {
		command = os.Args[1]
	}
	pythonLauncher := strings.EqualFold(filepath.Base(os.Args[0]), "py.exe") || (len(os.Args) > 2 && os.Args[1] == "-3")
	pythonExecutable := pythonLauncher || strings.EqualFold(filepath.Base(os.Args[0]), "python.exe") || (len(os.Args) > 1 && strings.EqualFold(filepath.Ext(os.Args[1]), ".py"))
	if pythonExecutable {
		argIndex := 1
		if pythonLauncher {
			if len(os.Args) < 3 || os.Args[1] != "-3" {
				os.Exit(91)
			}
			argIndex = 2
		}
		if len(os.Args) <= argIndex {
			os.Exit(91)
		}
		command = filepath.Base(os.Args[argIndex])
	}
	if path := os.Getenv("ACR_SETUP_STUB_LOG"); path != "" {
		file, err := os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o600)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(90)
		}
		_, _ = fmt.Fprintln(file, command)
		_ = file.Close()
	}
	if command != "" && command == os.Getenv("ACR_SETUP_STUB_FAIL") {
		os.Exit(23)
	}
	if pythonExecutable && strings.EqualFold(command, os.Getenv("ACR_SETUP_STUB_PY_FAIL")) {
		os.Exit(24)
	}
}
