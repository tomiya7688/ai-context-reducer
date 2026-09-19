package main

import (
    "flag"
    "fmt"
    "io"
    "os"
    "os/exec"
    "path/filepath"
    "strings"
)

type contextPackGitResult struct {
    OK        bool
    Lines     []string
    ErrorKind string
}

type contextPackTask struct {
    Goal       string
    Required   string
    Acceptance string
    Deferred   string
}

type contextPackState struct {
    Changed          []string
    Status           []string
    ChangedQueryOK   bool
    StatusQueryOK    bool
    ChangedErrorKind string
    StatusErrorKind  string
    ChangedTruncated bool
    StatusTruncated  bool
}

// contextPackGitLines はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func contextPackGitLines(root string, args ...string) contextPackGitResult {
    executable, err := exec.LookPath("git")
    if err != nil {
        return contextPackGitResult{ErrorKind: "git_unavailable"}
    }
    commandArgs := append([]string{"-C", root}, args...)
    cmd := exec.Command(executable, commandArgs...)
    output, err := cmd.Output()
    if err != nil {
        return contextPackGitResult{ErrorKind: "git_query_failed"}
    }
    lines := []string{}
    for _, line := range strings.Split(string(output), "\n") {
        line = strings.TrimSpace(line)
        if line != "" {
            lines = append(lines, line)
        }
    }
    return contextPackGitResult{OK: true, Lines: lines}
}

// boundedContextPackLines はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func boundedContextPackLines(lines []string, limit int) ([]string, bool) {
    if limit < 0 {
        limit = 0
    }
    if limit == 0 {
        return []string{}, len(lines) > 0
    }
    if len(lines) <= limit {
        return lines, false
    }
    return lines[:limit], true
}

// buildContextPackState は解析結果を後段で再利用できる構造へ組み立てます。
func buildContextPackState(root string, limit int) contextPackState {
    changed := contextPackGitLines(root, "diff", "--name-only", "HEAD")
    status := contextPackGitLines(root, "status", "--short")
    changedLines, changedTruncated := boundedContextPackLines(changed.Lines, limit)
    statusLines, statusTruncated := boundedContextPackLines(status.Lines, limit)
    return contextPackState{
        Changed: changedLines,
        Status: statusLines,
        ChangedQueryOK: changed.OK,
        StatusQueryOK: status.OK,
        ChangedErrorKind: changed.ErrorKind,
        StatusErrorKind: status.ErrorKind,
        ChangedTruncated: changedTruncated,
        StatusTruncated: statusTruncated,
    }
}

// contextPackFailureLine はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func contextPackFailureLine(errorKind, queryName string) string {
    if errorKind == "git_unavailable" {
        return "- Git unavailable\n"
    }
    return "- unavailable: " + queryName + " query failed\n"
}

// renderNativeContextPack は内部結果を安定した利用者向け出力へ変換します。
func renderNativeContextPack(task contextPackTask, state contextPackState) string {
    var out strings.Builder
    out.WriteString("# Context Pack\n\n## Task\n")
    fmt.Fprintf(&out, "- Goal: %s\n", task.Goal)
    fmt.Fprintf(&out, "- Required: %s\n", task.Required)
    fmt.Fprintf(&out, "- Acceptance: %s\n", task.Acceptance)
    fmt.Fprintf(&out, "- Deferred / out of scope: %s\n", task.Deferred)

    out.WriteString("\n## Working Set\n- Changed files:\n")
    if !state.ChangedQueryOK {
        if state.ChangedErrorKind == "git_unavailable" {
            out.WriteString("  - Git unavailable\n")
        } else {
            out.WriteString("  - unavailable: git diff query failed\n")
        }
    } else if len(state.Changed) == 0 {
        out.WriteString("  - none detected\n")
    } else {
        for _, item := range state.Changed {
            fmt.Fprintf(&out, "  - %s\n", item)
        }
        if state.ChangedTruncated {
            out.WriteString("  - ... truncated\n")
        }
    }

    out.WriteString("\n## Git Status\n")
    if !state.StatusQueryOK {
        out.WriteString(contextPackFailureLine(state.StatusErrorKind, "git status"))
    } else if len(state.Status) == 0 {
        out.WriteString("- clean\n")
    } else {
        for _, item := range state.Status {
            fmt.Fprintf(&out, "- %s\n", item)
        }
        if state.StatusTruncated {
            out.WriteString("- ... truncated\n")
        }
    }

    out.WriteString("\n## Required Constraints\n- \n")
    out.WriteString("\n## Validation\n- Targeted evidence:\n- Unverified areas:\n")
    out.WriteString("\n## Rules\n- Search first, read second.\n")
    out.WriteString("- Stop exploration once Goal / Required / Acceptance / working set are sufficient.\n")
    out.WriteString("- Return to source of truth only when details are needed.\n")
    return out.String()
}

// cmdContextPackBuilder は対象サブコマンドの引数解析・境界I/O・compact出力を統括します。
func cmdContextPackBuilder(args []string) int {
    flags := flag.NewFlagSet("context-pack-builder", flag.ContinueOnError)
    flags.SetOutput(io.Discard)
    goal := flags.String("goal", "", "task goal")
    required := flags.String("required", "", "required behavior or constraints")
    acceptance := flags.String("acceptance", "", "acceptance criteria")
    deferred := flags.String("deferred", "", "deferred or out-of-scope work")
    maxStateLines := flags.Int("max-state-lines", 60, "maximum changed/status lines included; 0 includes no state rows")
    output := flags.String("output", "", "optional output Markdown file")
    if err := flags.Parse(args); err != nil {
        fmt.Fprintf(os.Stderr, "context-pack-builder: invalid_arguments: %v\n", err)
        return 2
    }

    root := "."
    if flags.NArg() > 0 {
        root = flags.Arg(0)
    }
    rootAbs, err := filepath.Abs(root)
    if err != nil {
        fmt.Fprintf(os.Stderr, "context-pack-builder: input_read_failed: %v\n", err)
        return 2
    }
    info, err := os.Stat(rootAbs)
    if err != nil {
        if os.IsNotExist(err) {
            fmt.Fprintf(os.Stderr, "context-pack-builder: input_missing: %s\n", rootAbs)
        } else {
            fmt.Fprintf(os.Stderr, "context-pack-builder: input_read_failed: %v\n", err)
        }
        return 2
    }
    if !info.IsDir() {
        fmt.Fprintf(os.Stderr, "context-pack-builder: input_not_directory: %s\n", rootAbs)
        return 2
    }

    limit := *maxStateLines
    if limit < 0 {
        limit = 0
    }
    task := contextPackTask{Goal: *goal, Required: *required, Acceptance: *acceptance, Deferred: *deferred}
    text := renderNativeContextPack(task, buildContextPackState(rootAbs, limit))
    if *output != "" {
        if err := os.WriteFile(*output, []byte(text), 0o644); err != nil {
            fmt.Fprintf(os.Stderr, "context-pack-builder: output_write_failed: %v\n", err)
            return 2
        }
        return 0
    }
    fmt.Print(text)
    return 0
}
