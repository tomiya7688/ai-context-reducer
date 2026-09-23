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

const affectedTool = "affected-tests"

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
    Status  string   `json:"status,omitempty"`
    Imports []string `json:"imports"`
}

type depMap struct {
    Status          string   `json:"status,omitempty"`
    Files           []depRow `json:"files"`
    ParseErrorCount int      `json:"parse_error_count,omitempty"`
    ReadErrorCount  int      `json:"read_error_count,omitempty"`
    WalkErrorCount  int      `json:"walk_error_count,omitempty"`
    ScanTruncated   bool     `json:"scan_truncated,omitempty"`
    Truncated       bool     `json:"truncated,omitempty"`
}

type dependencyMapState struct {
    Used     bool     `json:"used"`
    Complete bool     `json:"complete,omitempty"`
    Reasons  []string `json:"reasons,omitempty"`
}

type result struct {
    Tool            string             `json:"tool"`
    Status          string             `json:"status"`
    ChangedFiles    []string           `json:"changed_files"`
    TestCandidates  []string           `json:"test_candidates"`
    Confidence      string             `json:"confidence"`
    Fallback        string             `json:"fallback"`
    ImpactUncertain bool               `json:"impact_uncertain"`
    DependencyMap   dependencyMapState `json:"dependency_map"`
    Reasons         []string           `json:"reasons"`
}

type stringList []string

// CLI flagの複数指定値を安定した文字列表現へ戻す。
func (s *stringList) String() string { return strings.Join(*s, ",") }
// CLIで繰り返し指定された値を順序を保って蓄積する。
func (s *stringList) Set(v string) error {
    if v != "" {
        *s = append(*s, normalize(v))
    }
    return nil
}

// path separatorを統一し、platform差でrouting候補がずれないようにする。
func normalize(s string) string { return filepath.ToSlash(strings.TrimSpace(s)) }

// Git境界から変更fileだけを取得し、test routingの入力working setを狭める。
func gitChanged(root, base string) ([]string, error) {
    args := []string{"-C", root, "diff", "--name-only"}
    if base != "" {
        args = append(args, base)
    }
    out, err := exec.Command("git", args...).CombinedOutput()
    if err != nil {
        msg := strings.TrimSpace(string(out))
        if msg == "" {
            msg = "git diff failed"
        }
        return nil, errors.New(msg)
    }
    files := []string{}
    for _, line := range strings.Split(string(out), "\n") {
        if line = normalize(line); line != "" {
            files = append(files, line)
        }
    }
    return files, nil
}

// 任意JSON設定を読み込み、未指定と読み込み失敗を呼び出し側で区別できるようにする。
func loadJSON(path string, dst any) error {
    if path == "" {
        return nil
    }
    data, err := os.ReadFile(path)
    if err != nil {
        return err
    }
    return json.Unmarshal(data, dst)
}

// 命名規則からcheapなtest候補を作り、明示mappingがなくても最初の候補を返す。
func defaultsFor(path string) []string {
    p := normalize(path)
    ext := strings.ToLower(filepath.Ext(filepath.FromSlash(p)))
    base := filepath.Base(filepath.FromSlash(p))
    stem := strings.TrimSuffix(base, filepath.Ext(base))
    out := []string{}
    addForRel := func(prefix, rel string) {
        rel = normalize(rel)
        relDir := filepath.ToSlash(filepath.Dir(filepath.FromSlash(rel)))
        if relDir == "." {
            relDir = ""
        }
        switch ext {
        case ".py":
            if prefix == "" {
                out = append(out, "tests/"+rel, "tests/test_"+stem+".py")
            } else {
                out = append(out, prefix+"/tests/"+rel, prefix+"/tests/test_"+stem+".py")
            }
        case ".go":
            testName := stem + "_test.go"
            if prefix == "" {
                out = append(out, joinSlash("src", relDir, testName), joinSlash("tests", relDir, testName))
            } else {
                out = append(out, joinSlash(prefix, "src", relDir, testName), joinSlash(prefix, "tests", relDir, testName))
            }
        default:
            if prefix == "" {
                out = append(out, "tests/"+rel)
            } else {
                out = append(out, prefix+"/tests/"+rel)
            }
        }
    }
    if strings.HasPrefix(p, "src/") {
        addForRel("", strings.TrimPrefix(p, "src/"))
    }
    if idx := strings.Index(p, "/src/"); idx >= 0 {
        addForRel(p[:idx], p[idx+5:])
    }
    return uniq(out)
}

// path要素をslash区切りで連結し、platform非依存のmatching keyを作る。
func joinSlash(parts ...string) string {
    cleaned := []string{}
    for _, part := range parts {
        if part = strings.Trim(normalize(part), "/"); part != "" {
            cleaned = append(cleaned, part)
        }
    }
    return strings.Join(cleaned, "/")
}

// 候補順を維持したまま重複を除き、出力と探索の冗長化を防ぐ。
func uniq(items []string) []string {
    seen := map[string]bool{}
    out := make([]string, 0, len(items))
    for _, item := range items {
        item = normalize(item)
        if item != "" && !seen[item] {
            seen[item] = true
            out = append(out, item)
        }
    }
    return out
}

// 設定globを正規表現へ変換し、routing ruleを決定論的に評価できるようにする。
func globRegexp(pattern string) (*regexp.Regexp, error) {
    pattern = normalize(pattern)
    var b strings.Builder
    b.WriteString("^")
    for i := 0; i < len(pattern); i++ {
        switch pattern[i] {
        case '*':
            if i+1 < len(pattern) && pattern[i+1] == '*' {
                b.WriteString(".*")
                i++
            } else {
                b.WriteString("[^/]*")
            }
        case '?':
            b.WriteString("[^/]")
        default:
            b.WriteString(regexp.QuoteMeta(string(pattern[i])))
        }
    }
    b.WriteString("$")
    return regexp.Compile(b.String())
}

// 正規化済みpathへglob ruleを適用し、mapping一致だけを判定する。
func match(pattern, path string) bool {
    if pattern == "" {
        return false
    }
    re, err := globRegexp(pattern)
    return err == nil && re.MatchString(normalize(path))
}

// dependency mapから変更fileのconsumerを拾い、見落としやすいtest候補を補う。
func dependencyConsumers(changed []string, deps depMap) []string {
    needles := []string{}
    for _, p := range changed {
        p = normalize(p)
        noExt := strings.TrimSuffix(p, filepath.Ext(filepath.FromSlash(p)))
        stem := filepath.Base(filepath.FromSlash(noExt))
        dir := filepath.ToSlash(filepath.Dir(filepath.FromSlash(noExt)))
        needles = append(needles, noExt, strings.ReplaceAll(noExt, "/", "."), stem)
        if dir != "." {
            needles = append(needles, dir, strings.ReplaceAll(dir, "/", "."))
        }
    }
    needles = uniq(needles)
    consumers := []string{}
    for _, row := range deps.Files {
        for _, imp := range row.Imports {
            for _, needle := range needles {
                if needle != "" && (imp == needle || strings.HasSuffix(imp, "/"+needle) || strings.HasSuffix(imp, "."+needle)) {
                    consumers = append(consumers, normalize(row.File))
                }
            }
        }
    }
    return uniq(consumers)
}

// dependency mapのtruncation/errorを完全性signalへ変換し、安全側fallback判断に使う。
func dependencyState(deps depMap, used bool) dependencyMapState {
    if !used {
        return dependencyMapState{Used: false}
    }
    reasons := []string{}
    if deps.ScanTruncated || deps.Truncated {
        reasons = append(reasons, "dependency_map_truncated")
    }
    if deps.ParseErrorCount > 0 {
        reasons = append(reasons, fmt.Sprintf("parse_error_count=%d", deps.ParseErrorCount))
    }
    if deps.ReadErrorCount > 0 {
        reasons = append(reasons, fmt.Sprintf("read_error_count=%d", deps.ReadErrorCount))
    }
    if deps.WalkErrorCount > 0 {
        reasons = append(reasons, fmt.Sprintf("walk_error_count=%d", deps.WalkErrorCount))
    }
    return dependencyMapState{Used: true, Complete: len(reasons) == 0, Reasons: reasons}
}

// 変更file・mapping・dependency情報を統合し、test候補とbroader fallback方針を決める。
func analyze(changed []string, cfg config, deps depMap, dependencyMapUsed ...bool) result {
    broad := cfg.BroaderPatterns
    if len(broad) == 0 {
        broad = []string{"**/core/**", "**/shared/**", "**/schema.*", "**/api/**", "go.mod", "go.sum", "pyproject.toml", "package.json"}
    }

    tests, reasons := []string{}, []string{}
    matchedExplicit, broader := false, false
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
        for _, pattern := range broad {
            if match(pattern, path) {
                broader = true
                reasons = append(reasons, "broad-impact pattern: "+path)
                break
            }
        }
    }

    consumers := dependencyConsumers(changed, deps)
    for _, consumer := range consumers {
        tests = append(tests, defaultsFor(consumer)...)
    }
    if len(consumers) > 0 {
        reasons = append(reasons, fmt.Sprintf("dependency-map consumers: %d", len(consumers)))
    }

    tests, reasons = uniq(tests), uniq(reasons)
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

    used := len(deps.Files) > 0 || deps.ScanTruncated || deps.Truncated || deps.ParseErrorCount > 0 || deps.ReadErrorCount > 0 || deps.WalkErrorCount > 0
    if len(dependencyMapUsed) > 0 {
        used = dependencyMapUsed[0]
    }
    depState := dependencyState(deps, used)
    impactUncertain := depState.Used && !depState.Complete

    fallback := "none"
    if impactUncertain {
        reasons = append(reasons, depState.Reasons...)
        if confidence == "high" {
            confidence = "medium"
        }
        fallback = "broader-or-full"
    } else if broader {
        fallback = "broader"
    } else if confidence == "low" {
        fallback = "subsystem-or-full"
    }

    status := "ok"
    if impactUncertain {
        status = "ok_with_warnings"
    }
    return result{
        Tool: affectedTool, Status: status, ChangedFiles: uniq(changed), TestCandidates: tests,
        Confidence: confidence, Fallback: fallback, ImpactUncertain: impactUncertain,
        DependencyMap: depState, Reasons: uniq(reasons),
    }
}

// affected-test結果を単一JSON契約で出力し、表現の重複を避ける。
func emitAffected(value any) {
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    _ = enc.Encode(value)
}

// CLI入力を検証し、通常routingと明示的failureを同じ機械可読契約で返す。
func main() {
    root := flag.String("root", ".", "repository root")
    base := flag.String("base", "", "git diff base, e.g. origin/main...HEAD")
    configPath := flag.String("config", "", "JSON config path")
    dependencyMapPath := flag.String("dependency-map", "", "optional import/dependency map JSON")
    _ = flag.Bool("json", false, "deprecated; JSON is always emitted")
    var changed stringList
    flag.Var(&changed, "changed", "explicit changed file; repeat flag to provide multiple files")
    flag.Parse()

    files := []string{}
    var err error
    if changed != nil {
        files = changed
    } else if files, err = gitChanged(*root, *base); err != nil {
        emitAffected(map[string]any{"tool": affectedTool, "status": "git_query_failed", "error": err.Error()})
        os.Exit(2)
    }

    var cfg config
    if err := loadJSON(*configPath, &cfg); err != nil {
        emitAffected(map[string]any{"tool": affectedTool, "status": "config_read_failed", "error": err.Error()})
        os.Exit(2)
    }
    var deps depMap
    if err := loadJSON(*dependencyMapPath, &deps); err != nil {
        emitAffected(map[string]any{"tool": affectedTool, "status": "dependency_map_read_failed", "error": err.Error()})
        os.Exit(2)
    }

    r := analyze(files, cfg, deps, *dependencyMapPath != "")
    sort.Strings(r.TestCandidates)
    emitAffected(r)
}
