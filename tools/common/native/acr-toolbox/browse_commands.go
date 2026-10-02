package main

import (
    "bufio"
    "fmt"
    "io"
    "os"
    "path/filepath"
    "strings"
)

// cmdTree は対象サブコマンドの引数解析・境界I/O・compact出力を統括します。
func cmdTree(args []string) int {
    root := "."
    const maxDepth = 3
    if len(args) > 0 {
        root = args[0]
    }
    files, status := walkBrowseRoot(root, "tree")
    if status != 0 {
        return status
    }
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

// cmdDocIndex は対象サブコマンドの引数解析・境界I/O・compact出力を統括します。
func cmdDocIndex(args []string) int {
    root := "."
    if len(args) > 0 {
        root = args[0]
    }
    return cmdDocIndexWithOpen(root, func(path string) (io.ReadCloser, error) { return os.Open(path) })
}

// cmdDocIndexWithOpen はMarkdown read failureをexit statusへ反映する。
func cmdDocIndexWithOpen(root string, openFile func(string) (io.ReadCloser, error)) int {
    files, status := walkBrowseRoot(root, "doc-index")
    if status != 0 {
        return status
    }
    shown := 0
    for _, f := range files {
        if strings.ToLower(filepath.Ext(f.Path)) != ".md" {
            continue
        }
        h, err := openFile(f.Path)
        if err != nil {
            fmt.Fprintf(os.Stderr, "doc-index: read failed for %s: %v\n", f.Path, err)
            return 2
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
        scanErr := scanner.Err()
        _ = h.Close()
        if scanErr != nil {
            fmt.Fprintf(os.Stderr, "doc-index: read failed for %s: %v\n", f.Path, scanErr)
            return 2
        }
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

// walkBrowseRoot はroot検証と走査error集計を行い、空結果と取得失敗を分ける。
func walkBrowseRoot(root, tool string) ([]fileInfo, int) {
    return walkBrowseRootWith(root, tool, os.Stat, func(path string, includeIgnored bool) (walkResult, error) {
        return walkWithOptions(path, includeIgnored)
    })
}

// walkBrowseRootWith はroot検証とwalk結果を受け取り、走査errorの終了状態を決める。
func walkBrowseRootWith(root, tool string, stat func(string) (os.FileInfo, error), walk func(string, bool) (walkResult, error)) ([]fileInfo, int) {
    info, err := stat(root)
    if err != nil {
        status := "input_read_failed"
        if os.IsNotExist(err) {
            status = "input_missing"
        }
        fmt.Fprintf(os.Stderr, "%s: %s: %v\n", tool, status, err)
        return nil, 2
    }
    if !info.IsDir() {
        fmt.Fprintf(os.Stderr, "%s: input_not_directory: %s\n", tool, root)
        return nil, 2
    }
    result, err := walk(root, false)
    if err != nil {
        fmt.Fprintf(os.Stderr, "%s: walk_failed: %v\n", tool, err)
        return nil, 2
    }
    if result.ErrorCount > 0 {
        fmt.Fprintf(os.Stderr, "%s: walk_failed: %d filesystem errors\n", tool, result.ErrorCount)
        return nil, 2
    }
    return result.Files, 0
}
