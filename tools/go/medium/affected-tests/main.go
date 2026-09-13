package main

import (
    "encoding/json"
    "errors"
    "flag"
    "fmt"
    "os"
    "os/exec"
    "path/filepath"
    "regexp"
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

type depRow struct {
    File    string   `json:"file"`
    Imports []string `json:"imports"`
}

type depMap struct {
    Files []depRow `json:"files"`
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
    if v != "" { *s = append(*s, normalize(v)) }
    return nil
}

func normalize(s string) string { return filepath.ToSlash(strings.TrimSpace(s)) }

func gitChanged(root, base string) ([]string, error) {
    args := []string{"-C", root, "diff", "--name-only"}
    if base != "" { args = append(args, base) }
    out, err := exec.Command("git", args...).CombinedOutput()
    if err != nil {
        msg := strings.TrimSpace(string(out))
        if msg == "" { msg = "git diff failed" }
        return nil, errors.New(msg)
    }
    var files []string
    for _, line := range strings.Split(string(out), "\n") {
        if line = normalize(line); line != "" { files = append(files, line) }
    }
    return files, nil
}

func loadJSON(path string, dst any) error {
    if path == "" { return nil }
    b, err := os.ReadFile(path)
    if err != nil { return err }
    return json.Unmarshal(b, dst)
}

func defaultsFor(path string) []string {
    p := normalize(path)
    ext := strings.ToLower(filepath.Ext(filepath.FromSlash(p)))
    base := filepath.Base(filepath.FromSlash(p))
    stem := strings.TrimSuffix(base, filepath.Ext(base))
    var out []string
    addForRel := func(prefix, rel string) {
        rel = normalize(rel)
        relDir := filepath.ToSlash(filepath.Dir(filepath.FromSlash(rel)))
        if relDir == "." { relDir = "" }
        switch ext {
        case ".py":
            if prefix == "" { out = append(out, "tests/"+rel, "tests/test_"+stem+".py")
            } else { out = append(out, prefix+"/tests/"+rel, prefix+"/tests/test_"+stem+".py") }
        case ".go":
            testName := stem + "_test.go"
            if prefix == "" { out = append(out, joinSlash("src", relDir, testName), joinSlash("tests", relDir, testName))
            } else { out = append(out, joinSlash(prefix, "src", relDir, testName), joinSlash(prefix, "tests", relDir, testName)) }
        default:
            if prefix == "" { out = append(out, "tests/"+rel) } else { out = append(out, prefix+"/tests/"+rel) }
        }
    }
    if strings.HasPrefix(p, "src/") { addForRel("", strings.TrimPrefix(p, "src/")) }
    if idx := strings.Index(p, "/src/"); idx >= 0 { addForRel(p[:idx], p[idx+5:]) }
    return uniq(out)
}

func joinSlash(parts ...string) string {
    var cleaned []string
    for _, p := range parts {
        if p = strings.Trim(normalize(p), "/"); p != "" { cleaned = append(cleaned, p) }
    }
    return strings.Join(cleaned, "/")
}

func uniq(items []string) []string {
    seen := map[string]bool{}
    out := make([]string, 0, len(items))
    for _, item := range items {
        item = normalize(item)
        if item != "" && !seen[item] { seen[item] = true; out = append(out, item) }
    }
    return out
}

func globRegexp(pattern string) (*regexp.Regexp, error) {
    pattern = normalize(pattern)
    var b strings.Builder
    b.WriteString("^")
    for i := 0; i < len(pattern); i++ {
        switch pattern[i] {
        case '*':
            if i+1 < len(pattern) && pattern[i+1] == '*' { b.WriteString(".*"); i++ } else { b.WriteString("[^/]*") }
        case '?': b.WriteString("[^/]")
        default: b.WriteString(regexp.QuoteMeta(string(pattern[i])))
        }
    }
    b.WriteString("$")
    return regexp.Compile(b.String())
}

func match(pattern, path string) bool {
    if pattern == "" { return false }
    re, err := globRegexp(pattern)
    return err == nil && re.MatchString(normalize(path))
}

func dependencyConsumers(changed []string, deps depMap) []string {
    var needles []string
    for _, p := range changed {
        p = normalize(p)
        noExt := strings.TrimSuffix(p, filepath.Ext(filepath.FromSlash(p)))
        stem := filepath.Base(filepath.FromSlash(noExt))
        dir := filepath.ToSlash(filepath.Dir(filepath.FromSlash(noExt)))
        needles = append(needles, noExt, strings.ReplaceAll(noExt, "/", "."), stem)
        if dir != "." { needles = append(needles, dir, strings.ReplaceAll(dir, "/", ".")) }
    }
    needles = uniq(needles)
    var consumers []string
    for _, row := range deps.Files {
        for _, imp := range row.Imports {
            for _, n := range needles {
                if n != "" && (imp == n || strings.HasSuffix(imp, "/"+n) || strings.HasSuffix(imp, "."+n)) {
                    consumers = append(consumers, normalize(row.File))
                }
            }
        }
    }
    return uniq(consumers)
}

func analyze(changed []string, cfg config, deps depMap) result {
    broad := cfg.BroaderPatterns
    if len(broad) == 0 { broad = []string{"**/core/**", "**/shared/**", "**/schema.*", "**/api/**", "go.mod", "go.sum", "pyproject.toml", "package.json"} }

    var tests, reasons []string
    matchedExplicit, broader := false, false
    for _, path := range changed {
        path = normalize(path)
        for _, m := range cfg.Mappings {
            if match(m.Source, path) {
                matchedExplicit = true
                tests = append(tests, m.Tests...)
                if m.Broader { broader = true; reasons = append(reasons, "broader mapping: "+path) }
            }
        }
        tests = append(tests, defaultsFor(path)...)
        for _, pat := range broad {
            if match(pat, path) { broader = true; reasons = append(reasons, "broad-impact pattern: "+path); break }
        }
    }

    consumers := dependencyConsumers(changed, deps)
    for _, consumer := range consumers { tests = append(tests, defaultsFor(consumer)...) }
    if len(consumers) > 0 { reasons = append(reasons, fmt.Sprintf("dependency-map consumers: %d", len(consumers))) }

    tests, reasons = uniq(tests), uniq(reasons)
    confidence := "low"
    switch {
    case len(changed) == 0: reasons = append(reasons, "no changed files")
    case broader: confidence = "medium"
    case matchedExplicit: confidence = "high"
    case len(tests) > 0: confidence = "medium"
    default: reasons = append(reasons, "no mapping or naming candidate")
    }

    fallback := "none"
    if broader { fallback = "broader" } else if confidence == "low" { fallback = "subsystem-or-full" }
    return result{ChangedFiles: uniq(changed), TestCandidates: tests, Confidence: confidence, Fallback: fallback, Reasons: uniq(reasons)}
}

func main() {
    root := flag.String("root", ".", "repository root")
    base := flag.String("base", "", "git diff base, e.g. origin/main...HEAD")
    configPath := flag.String("config", "", "JSON config path")
    dependencyMapPath := flag.String("dependency-map", "", "optional import/dependency map JSON")
    jsonOut := flag.Bool("json", false, "emit JSON")
    var changed stringList
    flag.Var(&changed, "changed", "explicit changed file; repeat flag to provide multiple files")
    flag.Parse()

    var files []string
    var err error
    if changed != nil { files = changed } else if files, err = gitChanged(*root, *base); err != nil { fmt.Fprintln(os.Stderr, "affected-tests:", err); os.Exit(2) }

    var cfg config
    if err := loadJSON(*configPath, &cfg); err != nil { fmt.Fprintln(os.Stderr, "affected-tests:", err); os.Exit(2) }
    var deps depMap
    if err := loadJSON(*dependencyMapPath, &deps); err != nil { fmt.Fprintln(os.Stderr, "affected-tests:", err); os.Exit(2) }

    r := analyze(files, cfg, deps)
    sort.Strings(r.TestCandidates)
    if *jsonOut {
        enc := json.NewEncoder(os.Stdout); enc.SetIndent("", "  ")
        if err := enc.Encode(r); err != nil { fmt.Fprintln(os.Stderr, "affected-tests:", err); os.Exit(2) }
        return
    }
    fmt.Println("confidence:", r.Confidence)
    fmt.Println("fallback:", r.Fallback)
    fmt.Println("tests:")
    for _, t := range r.TestCandidates { fmt.Println("-", t) }
    if len(r.Reasons) > 0 { fmt.Println("reasons:"); for _, reason := range r.Reasons { fmt.Println("-", reason) } }
}
