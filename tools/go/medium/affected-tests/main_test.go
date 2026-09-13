package main

import "testing"

func TestAnalyzeExplicitMapping(t *testing.T) {
    cfg := config{Mappings: []mapping{{Source: "src/parser/*", Tests: []string{"tests/parser/test_parser.py"}}}}
    got := analyze([]string{"src/parser/lexer.py"}, cfg, depMap{})
    if got.Confidence != "high" { t.Fatalf("confidence=%s", got.Confidence) }
    if got.Fallback != "none" { t.Fatalf("fallback=%s", got.Fallback) }
    found := false
    for _, x := range got.TestCandidates { if x == "tests/parser/test_parser.py" { found = true } }
    if !found { t.Fatalf("explicit test missing: %#v", got.TestCandidates) }
}

func TestAnalyzeBroadImpact(t *testing.T) {
    got := analyze([]string{"packages/core/src/api.go"}, config{}, depMap{})
    if got.Fallback != "broader" { t.Fatalf("fallback=%s", got.Fallback) }
    if got.Confidence != "medium" { t.Fatalf("confidence=%s", got.Confidence) }
}

func TestAnalyzeNoChanges(t *testing.T) {
    got := analyze(nil, config{}, depMap{})
    if got.Confidence != "low" { t.Fatalf("confidence=%s", got.Confidence) }
    if got.Fallback != "subsystem-or-full" { t.Fatalf("fallback=%s", got.Fallback) }
}

func TestGlobRecursiveAndSuffixWildcard(t *testing.T) {
    if !match("**/schema.*", "pkg/data/schema.json") { t.Fatal("recursive schema glob should match") }
    if !match("**/core/**", "packages/core/src/api.go") { t.Fatal("recursive core glob should match") }
}

func TestGoDefaultTestCandidate(t *testing.T) {
    got := defaultsFor("src/parser/lexer.go")
    want := "src/parser/lexer_test.go"
    for _, x := range got { if x == want { return } }
    t.Fatalf("missing %s in %#v", want, got)
}

func TestDependencyConsumersAddCandidates(t *testing.T) {
    deps := depMap{Files: []depRow{{File: "src/app/loader.py", Imports: []string{"pkg.parser.lexer"}}}}
    got := analyze([]string{"pkg/parser/lexer.py"}, config{}, deps)
    foundReason := false
    for _, reason := range got.Reasons {
        if reason == "dependency-map consumers: 1" { foundReason = true }
    }
    if !foundReason { t.Fatalf("dependency-map reason missing: %#v", got.Reasons) }
}
