package main

import (
    "bufio"
    "fmt"
    "io"
    "os"
    "regexp"
)

func readLines(path string) ([]string, error) {
    h, err := os.Open(path)
    if err != nil {
        return nil, err
    }
    defer h.Close()
    out := []string{}
    s := bufio.NewScanner(h)
    buf := make([]byte, 64*1024)
    s.Buffer(buf, 2*1024*1024)
    for s.Scan() {
        out = append(out, s.Text())
    }
    return out, s.Err()
}

func cmdSlice(args []string) int {
    if len(args) < 2 {
        fmt.Fprintln(os.Stderr, "usage: acr-toolbox slice PATTERN FILE [FILE...]")
        return 2
    }
    rx, err := regexp.Compile("(?i)" + args[0])
    if err != nil {
        fmt.Fprintln(os.Stderr, err)
        return 2
    }
    shown := 0
    for _, name := range args[1:] {
        lines, err := readLines(name)
        if err != nil {
            continue
        }
        for i, line := range lines {
            if !rx.MatchString(line) {
                continue
            }
            start := i - 3
            if start < 0 {
                start = 0
            }
            end := i + 6
            if end > len(lines) {
                end = len(lines)
            }
            fmt.Printf("--- %s:%d ---\n", name, i+1)
            for n := start; n < end; n++ {
                fmt.Printf("%6d: %s\n", n+1, lines[n])
            }
            shown++
            if shown >= 20 {
                fmt.Println("[truncated: max matches reached]")
                return 0
            }
        }
    }
    return 0
}

var logSignal = regexp.MustCompile(`(?i)(error|failed|failure|fatal|exception|warning|warn|assert|traceback|ng\b)`)

func cmdCompactLog(args []string) int {
    var r io.Reader = os.Stdin
    if len(args) > 0 {
        h, err := os.Open(args[0])
        if err != nil {
            fmt.Fprintln(os.Stderr, err)
            return 1
        }
        defer h.Close()
        r = h
    }

    lines := []string{}
    s := bufio.NewScanner(r)
    buf := make([]byte, 64*1024)
    s.Buffer(buf, 2*1024*1024)
    for s.Scan() {
        lines = append(lines, s.Text())
    }

    findings := []int{}
    for i, line := range lines {
        if logSignal.MatchString(line) {
            findings = append(findings, i)
        }
    }

    fmt.Printf("lines=%d findings=%d\n", len(lines), len(findings))
    if len(findings) > 0 {
        fmt.Println("findings:")
        limit := len(findings)
        if limit > 80 {
            limit = 80
        }
        for _, idx := range findings[:limit] {
            line := lines[idx]
            if len(line) > 240 {
                line = line[:240]
            }
            fmt.Printf("  %d: %s\n", idx+1, line)
        }
        if len(findings) > limit {
            fmt.Printf("  ... truncated %d more findings\n", len(findings)-limit)
        }
    }

    fmt.Println("tail:")
    start := len(lines) - 20
    if start < 0 {
        start = 0
    }
    for i := start; i < len(lines); i++ {
        line := lines[i]
        if len(line) > 240 {
            line = line[:240]
        }
        fmt.Printf("  %d: %s\n", i+1, line)
    }
    return 0
}
