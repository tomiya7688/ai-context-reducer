package main

import (
    "fmt"
    "os"
    "os/exec"
    "strings"
)

type gitCommandResult struct {
    Output    string
    ErrorKind string
    ExitCode  int
}

// runGit は標準出力が空でも成功状態を保持し、Git failureを呼び出し側へ返す。
func runGit(root string, args ...string) gitCommandResult {
    executable, err := exec.LookPath("git")
    if err != nil {
        return gitCommandResult{ErrorKind: "git_unavailable"}
    }
    commandArgs := append([]string{"-C", root}, args...)
    output, err := exec.Command(executable, commandArgs...).CombinedOutput()
    if err != nil {
        result := gitCommandResult{ErrorKind: "git_query_failed", ExitCode: -1}
        if exitError, ok := err.(*exec.ExitError); ok {
            result.ExitCode = exitError.ExitCode()
        }
        return result
    }
    return gitCommandResult{Output: strings.TrimSpace(string(output))}
}

// checkGitRepository はGit executable不在とrepository外の入力を区別する。
func checkGitRepository(root string) string {
    result := runGit(root, "rev-parse", "--is-inside-work-tree")
    if result.ErrorKind == "git_unavailable" {
        return result.ErrorKind
    }
    if result.ErrorKind != "" || result.Output != "true" {
        return "git_unavailable_or_not_repository"
    }
    return ""
}

// reportGitFailure はfailure種別をstderrへ短く示し、shellへnon-zeroを返す。
func reportGitFailure(tool, kind string) int {
    fmt.Fprintf(os.Stderr, "%s: %s\n", tool, kind)
    return 2
}

// cmdCompactDiff はcommit/file/stat/diff queryをすべて成功確認してからcompact出力する。
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
    if kind := checkGitRepository(root); kind != "" {
        return reportGitFailure("compact-diff", kind)
    }

    queries := []struct {
        args []string
    }{
        {[]string{"log", "--oneline", base + ".." + head}},
        {[]string{"diff", "--name-status", base, head}},
        {[]string{"diff", "--shortstat", base, head}},
        {[]string{"diff", "--unified=2", base, head}},
    }
    results := make([]gitCommandResult, len(queries))
    for i, query := range queries {
        results[i] = runGit(root, query.args...)
        if results[i].ErrorKind != "" {
            return reportGitFailure("compact-diff", results[i].ErrorKind)
        }
    }

    fmt.Println("## commits")
    printGitSection(results[0].Output)
    fmt.Println("\n## changed files")
    printGitSection(results[1].Output)
    fmt.Println("\n## shortstat")
    printGitSection(results[2].Output)

    fmt.Println("\n## bounded diff")
    if results[3].Output == "" {
        fmt.Println("(none)")
        return 0
    }
    lines := strings.Split(results[3].Output, "\n")
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

// printGitSection は空だと成功したquery結果だけをnoneとして表現する。
func printGitSection(output string) {
    if output == "" {
        fmt.Println("(none)")
        return
    }
    fmt.Println(output)
}

// cmdRemoteDelta はrepository・remote ref・各Git queryの状態を区別して出力する。
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
    if kind := checkGitRepository(root); kind != "" {
        return reportGitFailure("remote-delta", kind)
    }

    status := runGit(root, "status", "--short")
    if status.ErrorKind != "" {
        return reportGitFailure("remote-delta", status.ErrorKind)
    }
    remoteRef := runGit(root, "rev-parse", "--verify", remote)
    if remoteRef.ErrorKind != "" {
        reference := remote
        if !strings.HasPrefix(reference, "refs/") {
            reference = "refs/remotes/" + reference
        }
        showRef := runGit(root, "show-ref", "--verify", "--quiet", reference)
        if showRef.ErrorKind != "" && showRef.ExitCode != 1 {
            return reportGitFailure("remote-delta", "git_query_failed")
        }
        if showRef.ErrorKind == "" {
            return reportGitFailure("remote-delta", "git_query_failed")
        }
        fmt.Printf("status=remote_unavailable remote=%s\n", remote)
        fmt.Printf("local_changes=%s\n", yesNo(status.Output != ""))
        return 0
    }

    queries := []struct {
        args []string
    }{
        {[]string{"rev-list", "--count", remote + ".." + base}},
        {[]string{"rev-list", "--count", base + ".." + remote}},
        {[]string{"diff", "--shortstat", base, remote}},
        {[]string{"diff", "--name-only", base, remote}},
        {[]string{"log", "--oneline", "--max-count=8", base + ".." + remote}},
    }
    results := make([]gitCommandResult, len(queries))
    for i, query := range queries {
        results[i] = runGit(root, query.args...)
        if results[i].ErrorKind != "" {
            return reportGitFailure("remote-delta", results[i].ErrorKind)
        }
    }

    fmt.Printf("status=ok ahead=%s behind=%s dirty=%s\n", results[0].Output, results[1].Output, yesNo(status.Output != ""))
    if results[2].Output != "" {
        fmt.Println("diff=" + results[2].Output)
    }
    fmt.Println("changed_files:")
    names := nonEmptyLines(results[3].Output)
    limit := len(names)
    if limit > 40 {
        limit = 40
    }
    for _, name := range names[:limit] {
        fmt.Println("  " + name)
    }
    if len(names) > limit {
        fmt.Printf("  ... truncated %d more\n", len(names)-limit)
    }
    commits := nonEmptyLines(results[4].Output)
    if len(commits) > 0 {
        fmt.Println("remote_commits:")
        for _, line := range commits {
            fmt.Println("  " + line)
        }
    }
    return 0
}

// yesNo はnative text outputのdirty signalを明示的なboolean語へそろえる。
func yesNo(value bool) string {
    if value {
        return "yes"
    }
    return "no"
}

// nonEmptyLines はGitの空出力を偽の空行file/commitとして扱わない。
func nonEmptyLines(output string) []string {
    lines := []string{}
    for _, line := range strings.Split(output, "\n") {
        if line != "" {
            lines = append(lines, line)
        }
    }
    return lines
}
