package main

import (
    "io/fs"
    "path/filepath"
    "strings"
)

var ignoreDirs = map[string]bool{
    ".git": true,
    ".hg": true,
    ".svn": true,
    ".venv": true,
    "venv": true,
    "node_modules": true,
    "bin": true,
    "obj": true,
    "build": true,
    "dist": true,
    "__pycache__": true,
    ".godot": true,
    ".idea": true,
    ".vs": true,
    "vendor": true,
}

var languageByExt = map[string]string{
    ".py": "Python", ".cs": "CSharp", ".go": "Go", ".c": "C", ".h": "C/C++",
    ".cpp": "C++", ".cc": "C++", ".cxx": "C++", ".hpp": "C++", ".hh": "C/C++",
    ".gd": "GDScript", ".rs": "Rust", ".js": "JavaScript", ".ts": "TypeScript", ".java": "Java",
}

type fileInfo struct {
    Path string
    Size int64
}

type walkResult struct {
    Files      []fileInfo
    ErrorCount int
}

func walkWithOptions(root string, includeIgnored bool) (walkResult, error) {
    out := walkResult{Files: []fileInfo{}}
    err := filepath.WalkDir(root, func(path string, d fs.DirEntry, err error) error {
        if err != nil {
            if path == root {
                return err
            }
            out.ErrorCount++
            return nil
        }
        if d.IsDir() {
            if !includeIgnored && path != root && ignoreDirs[strings.ToLower(d.Name())] {
                return filepath.SkipDir
            }
            return nil
        }
        info, infoErr := d.Info()
        if infoErr != nil {
            out.ErrorCount++
            return nil
        }
        out.Files = append(out.Files, fileInfo{Path: path, Size: info.Size()})
        return nil
    })
    return out, err
}

func walk(root string) ([]fileInfo, error) {
    result, err := walkWithOptions(root, false)
    return result.Files, err
}
