package main

import (
    "encoding/json"
    "errors"
    "flag"
    "fmt"
    "os"
    "os/exec"
    "path/filepath"
    "sort"
    "strings"
)

type mapping struct {
    Source  string   `json:"source"`
    Tests   []string `json:"tests"`
    Broader bool     `json:"broader"`
}

type config struct {
    Mappings        []mapping `json:"mappings"`
    BroaderPatterns []string  `json:"broader_patterns"`
}

type result struct {
    ChangedFiles   []string `json:"changed_files"`
    TestCandidates []string `json:"test_candidates"`
    Confidence     string   `json:"confidence"`
    Fallback       string   `json:"fallback"`
    Reasons        []string `json:"reasons"`
}

type stringList []string

func (s *stringList) String() string { return strings.Join(*s, ",") }
func (s *stringList) Set(v string) error {
    if v == "" { return nil }
    *s = append(*s, normalize(v))
    return nil
}

func normalize(s string) string { return filepath.ToSlash(strings.TrimSpace(s)) }

func gitChanged(root, base string) ([]string, error) {
    args := []string{"-C", root, "diff", "--name-only"}
    if base != "" { args = append(args, base) }
    cmd := exec.Command("git", args...)
    out, err := cmd.CombinedOutput()
    if err != nil {
        msg := strings.TrimSpace(string(out))
        if msg == "" { msg = "git diff failed" }
        return nil, errors.New(msg)
    }
    var files []string
    for _, line := range strings.Split(string(out), "\n") {
        line = normalize(line)
        if line != "" { files = append(files, line) }
    }
    return files, nil
}

func loadConfig(path string) (config, error) {
    var cfg config
    if path == "" { return cfg, nil }
    b, err := os.ReadFile(path)
    if err != nil { return cfg, err }
    if err := json.Unmarshal(b, &cfg); err != nil { return cfg, err }
    return cfg, nil
}

func defaultsFor(path string) []string {
    p := normalize(path)
    base := filepath.Base(filepath.FromSlash(p))
    stem := strings.TrimSuffix(base, filepath.Ext(base))
    var out []string
    if strings.HasPrefix(p, "src/") {
        rel := strings.TrimPrefix(p, "src/")
        out = append(out, "tests/"+rel, "tests/test_"+stem+".py")
    }
    if idx := strings.Index(p, "/src/"); idx >= 0 {
        prefix := p[:idx]
        rel := p[idx+5:]
        out = append(out, prefix+"/tests/"+rel, prefix+"/tests/test_"+stem+".py")
    }
    return out
}

func uniq(items []string) []string {
    seen := map[string]bool{}
    out := make([]string, 0, len(items))
    for _, item := range items {
        item = normalize(item)
        if item == "" || seen[item] { continue }
        seen[item] = true
        out = append(out, item)
    }
    return out
}

func match(pattern, path string) bool {
    pattern, path = normalize(pattern), normalize(path)
    if pattern == "" { return false }
    // filepath.Match does not treat ** specially, so support the common recursive form explicitly.
    if strings.Contains(pattern, "**") {
        parts := strings.Split(pattern, "**")
        pos := 0
        if !strings.HasPrefix(pattern, "**") {
            if !strings.HasPrefix(path, parts[0]) { return false }
            pos = len(parts[0])
        }
        for i, part := range parts {
            if part == "" || (i == 0 && !strings.HasPrefix(pattern, "**")) { continue }
            idx := strings.Index(path[pos:], part)
            if idx < 0 { return false }
            pos += idx + len(part)
        }
        if !strings.HasSuffix(pattern, "**") && parts[len(parts)-1] != "" {
            return strings.HasSuffix(path, parts[len(parts)-1])
        }
        return true
    }
    ok, err := filepath.Match(filepath.FromSlash(pattern), filepath.FromSlash(path))
    return err == nil && ok
}

func analyze(changed []string, cfg config) result {
    broad := cfg.BroaderPatterns
    if len(broad) == 0 {
        broad = []string{"**/core/**", "**/shared/**", "**/schema.*", "**/api/**", "go.mod", "go.sum", "pyproject.toml", "package.json"}
    }
    var tests, reasons []string
    matchedExplicit := false
    broader := false

    for _, path := range changed {
        path = normalize(path)
        for _, m := range cfg.Mappings {
            if match(m.Source, path) {
                matchedExplicit = true
                tests = append(tests, m.Tests...)
                if m.Broader {
                    broader = true
                    reasons = append(reasons, "broader mapping: "+path)
                }
            }
        }
        tests = append(tests, defaultsFor(path)...)
        for _, pat := range broad {
            if match(pat, path) {
                broader = true
                reasons = append(reasons, "broad-impact pattern: "+path)
                break
            }
        }
    }

    tests = uniq(tests)
    reasons = uniq(reasons)
    confidence := "low"
    switch {
    case len(changed) == 0:
        reasons = append(reasons, "no changed files")
    case broader:
        confidence = "medium"
    case matchedExplicit:
        confidence = "high"
    case len(tests) > 0:
        confidence = "medium"
    default:
        reasons = append(reasons, "no mapping or naming candidate")
    }

    fallback := "none"
    if broader { fallback = "broader" } else if confidence == "low" { fallback = "subsystem-or-full" }
    return result{ChangedFiles: uniq(changed), TestCandidates: tests, Confidence: confidence, Fallback: fallback, Reasons: uniq(reasons)}
}

func main() {
    root := flag.String("root", ".", "repository root")
    base := flag.String("base", "", "git diff base, e.g. origin/main...HEAD")
    configPath := flag.String("config", "", "JSON config path")
    jsonOut := flag.Bool("json", false, "emit JSON")
    var changed stringList
    flag.Var(&changed, "changed", "explicit changed file; repeat flag to provide multiple files")
    flag.Parse()

    var files []string
    var err error
    if changed != nil {
        files = changed
    } else {
        files, err = gitChanged(*root, *base)
        if err != nil {
            fmt.Fprintln(os.Stderr, "affected-tests:", err)
            os.Exit(2)
        }
    }

    cfg, err := loadConfig(*configPath)
    if err != nil {
        fmt.Fprintln(os.Stderr, "affected-tests:", err)
        os.Exit(2)
    }
    r := analyze(files, cfg)
    sort.Strings(r.TestCandidates)

    if *jsonOut {
        enc := json.NewEncoder(os.Stdout)
        enc.SetIndent("", "  ")
        if err := enc.Encode(r); err != nil {
            fmt.Fprintln(os.Stderr, "affected-tests:", err)
            os.Exit(2)
        }
        return
    }

    fmt.Println("confidence:", r.Confidence)
    fmt.Println("fallback:", r.Fallback)
    fmt.Println("tests:")
    for _, t := range r.TestCandidates { fmt.Println("-", t) }
    if len(r.Reasons) > 0 {
        fmt.Println("reasons:")
        for _, reason := range r.Reasons { fmt.Println("-", reason) }
    }
}
