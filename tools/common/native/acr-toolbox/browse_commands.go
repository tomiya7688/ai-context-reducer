package main

import (
    "bufio"
    "fmt"
    "os"
    "path/filepath"
    "sort"
    "strings"
)

func cmdTree(args []string) int {
    root := "."
    const maxDepth = 3
    if len(args) > 0 {
        root = args[0]
    }
    files, _ := walk(root)
    seen := map[string]bool{}
    n := 0
    for _, f := range files {
        rel, _ := filepath.Rel(root, f.Path)
        parts := strings.Split(filepath.ToSlash(rel), "/")
        if len(parts) > maxDepth {
            parts = parts[:maxDepth]
        }
        key := strings.Join(parts, "/")
        if !seen[key] {
            seen[key] = true
            fmt.Println(key)
            n++
            if n >= 500 {
                break
            }
        }
    }
    return 0
}

func cmdStats(args []string) int {
    root := "."
    if len(args) > 0 {
        root = args[0]
    }
    files, _ := walk(root)
    counts := map[string]int{}
    lines := map[string]int{}
    for _, f := range files {
        lang := languageByExt[strings.ToLower(filepath.Ext(f.Path))]
        if lang == "" {
            continue
        }
        counts[lang]++
        h, err := os.Open(f.Path)
        if err != nil {
            continue
        }
        s := bufio.NewScanner(h)
        for s.Scan() {
            lines[lang]++
        }
        _ = h.Close()
    }
    keys := make([]string, 0, len(counts))
    for k := range counts {
        keys = append(keys, k)
    }
    sort.Strings(keys)
    for _, k := range keys {
        fmt.Printf("%s files=%d lines=%d\n", k, counts[k], lines[k])
    }
    fmt.Printf("total_files=%d\n", len(files))
    return 0
}

func cmdDocIndex(args []string) int {
    root := "."
    if len(args) > 0 {
        root = args[0]
    }
    files, _ := walk(root)
    shown := 0
    for _, f := range files {
        if strings.ToLower(filepath.Ext(f.Path)) != ".md" {
            continue
        }
        h, err := os.Open(f.Path)
        if err != nil {
            continue
        }
        rel, _ := filepath.Rel(root, f.Path)
        scanner := bufio.NewScanner(h)
        headings := []string{}
        lineNo := 0
        for scanner.Scan() {
            lineNo++
            line := scanner.Text()
            if strings.HasPrefix(line, "# ") || strings.HasPrefix(line, "## ") || strings.HasPrefix(line, "### ") {
                headings = append(headings, fmt.Sprintf("  L%d %s", lineNo, line))
                if len(headings) >= 60 {
                    break
                }
            }
        }
        _ = h.Close()
        if len(headings) == 0 {
            continue
        }
        fmt.Println(filepath.ToSlash(rel))
        for _, x := range headings {
            fmt.Println(x)
        }
        shown++
        if shown >= 200 {
            break
        }
    }
    return 0
}
