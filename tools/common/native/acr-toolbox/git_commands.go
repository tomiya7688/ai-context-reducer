package main

import (
    "fmt"
    "os/exec"
    "strings"
)

// gitOutput はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func gitOutput(root string, args ...string) string {
    all := append([]string{"-C", root}, args...)
    out, err := exec.Command("git", all...).CombinedOutput()
    if err != nil {
        return ""
    }
    return strings.TrimSpace(string(out))
}

// cmdCompactDiff は対象サブコマンドの引数解析・境界I/O・compact出力を統括します。
func cmdCompactDiff(args []string) int {
    root, base, head := ".", "HEAD~1", "HEAD"
    if len(args) > 0 {
        root = args[0]
    }
    if len(args) > 1 {
        base = args[1]
    }
    if len(args) > 2 {
        head = args[2]
    }

    fmt.Println("## commits")
    if x := gitOutput(root, "log", "--oneline", base+".."+head); x != "" {
        fmt.Println(x)
    } else {
        fmt.Println("(none)")
    }

    fmt.Println("\n## changed files")
    if x := gitOutput(root, "diff", "--name-status", base, head); x != "" {
        fmt.Println(x)
    } else {
        fmt.Println("(none)")
    }

    fmt.Println("\n## shortstat")
    if x := gitOutput(root, "diff", "--shortstat", base, head); x != "" {
        fmt.Println(x)
    } else {
        fmt.Println("(none)")
    }

    fmt.Println("\n## bounded diff")
    lines := strings.Split(gitOutput(root, "diff", "--unified=2", base, head), "\n")
    if len(lines) == 1 && lines[0] == "" {
        return 0
    }
    limit := len(lines)
    if limit > 120 {
        limit = 120
    }
    for _, line := range lines[:limit] {
        fmt.Println(line)
    }
    if len(lines) > limit {
        fmt.Printf("... TRUNCATED %d lines; inspect full diff only if needed\n", len(lines)-limit)
    }
    return 0
}

// cmdRemoteDelta は対象サブコマンドの引数解析・境界I/O・compact出力を統括します。
func cmdRemoteDelta(args []string) int {
    root, base, remote := ".", "HEAD", "origin/HEAD"
    if len(args) > 0 {
        root = args[0]
    }
    if len(args) > 1 {
        remote = args[1]
    }
    if len(args) > 2 {
        base = args[2]
    }

    dirty := gitOutput(root, "status", "--short") != ""
    if gitOutput(root, "rev-parse", "--verify", remote) == "" {
        fmt.Println("remote=unavailable")
        if dirty {
            fmt.Println("local_changes=yes")
        } else {
            fmt.Println("local_changes=no")
        }
        return 0
    }

    ahead := gitOutput(root, "rev-list", "--count", remote+".."+base)
    if ahead == "" {
        ahead = "0"
    }
    behind := gitOutput(root, "rev-list", "--count", base+".."+remote)
    if behind == "" {
        behind = "0"
    }
    dirtyText := "no"
    if dirty {
        dirtyText = "yes"
    }
    fmt.Printf("ahead=%s behind=%s dirty=%s\n", ahead, behind, dirtyText)

    if stat := gitOutput(root, "diff", "--shortstat", base, remote); stat != "" {
        fmt.Println("diff=" + stat)
    }

    names := strings.Split(gitOutput(root, "diff", "--name-only", base, remote), "\n")
    fmt.Println("changed_files:")
    limit := len(names)
    if limit > 40 {
        limit = 40
    }
    for _, n := range names[:limit] {
        if n != "" {
            fmt.Println("  " + n)
        }
    }
    if len(names) > limit {
        fmt.Printf("  ... truncated %d more\n", len(names)-limit)
    }

    if commits := gitOutput(root, "log", "--oneline", "--max-count=8", base+".."+remote); commits != "" {
        fmt.Println("remote_commits:")
        for _, line := range strings.Split(commits, "\n") {
            fmt.Println("  " + line)
        }
    }
    return 0
}
