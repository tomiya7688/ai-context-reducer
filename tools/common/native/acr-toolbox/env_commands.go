package main

import (
    "encoding/json"
    "os"
    "os/exec"
    "runtime"
)

func firstAvailable(names ...string) string {
    for _, name := range names {
        if p, err := exec.LookPath(name); err == nil {
            return p
        }
    }
    return ""
}

func cmdLanguageEnv() int {
    env := map[string]any{
        "python": map[string]any{"available": firstAvailable("python3", "python") != "", "command": firstAvailable("python3", "python")},
        "csharp": map[string]any{"available": firstAvailable("dotnet") != "", "command": firstAvailable("dotnet")},
        "go": map[string]any{"available": firstAvailable("go") != "", "command": firstAvailable("go")},
        "c": map[string]any{"available": firstAvailable("gcc", "clang", "cc") != "", "command": firstAvailable("gcc", "clang", "cc")},
        "cpp": map[string]any{"available": firstAvailable("g++", "clang++", "c++") != "", "command": firstAvailable("g++", "clang++", "c++")},
        "gdscript": map[string]any{"available": firstAvailable("godot4", "godot") != "", "command": firstAvailable("godot4", "godot")},
    }
    out := map[string]any{
        "os": runtime.GOOS,
        "arch": runtime.GOARCH,
        "languages": env,
        "policy": "enable language-specific tools only when the matching standard/runtime environment is available; otherwise skip without installing dependencies",
    }
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    _ = enc.Encode(out)
    return 0
}

func cmdEnv() int {
    out := map[string]any{
        "os": runtime.GOOS,
        "arch": runtime.GOARCH,
        "native": true,
        "git": firstAvailable("git") != "",
        "python": firstAvailable("python3", "python") != "",
    }
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    _ = enc.Encode(out)
    return 0
}
