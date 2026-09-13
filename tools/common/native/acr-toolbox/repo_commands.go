package main

import (
    "io/fs"
    "path/filepath"
    "strings"
)

var ignoreDirs = map[string]bool{
    ".git": true,
    ".venv": true,
    "venv": true,
    "node_modules": true,
    "bin": true,
    "obj": true,
    "build": true,
    "dist": true,
    "__pycache__": true,
    ".godot": true,
}

var languageByExt = map[string]string{
    ".py": "Python", ".cs": "CSharp", ".go": "Go", ".c": "C", ".h": "C/C++",
    ".cpp": "C++", ".cc": "C++", ".cxx": "C++", ".hpp": "C++", ".hh": "C++",
    ".gd": "GDScript", ".rs": "Rust", ".js": "JavaScript", ".ts": "TypeScript", ".java": "Java",
}

type fileInfo struct {
    Path string
    Size int64
}

func walk(root string) ([]fileInfo, error) {
    out := []fileInfo{}
    err := filepath.WalkDir(root, func(path string, d fs.DirEntry, err error) error {
        if err != nil {
            return nil
        }
        if d.IsDir() {
            if path != root && ignoreDirs[strings.ToLower(d.Name())] {
                return filepath.SkipDir
            }
            return nil
        }
        info, e := d.Info()
        if e != nil {
            return nil
        }
        out = append(out, fileInfo{Path: path, Size: info.Size()})
        return nil
    })
    return out, err
}
