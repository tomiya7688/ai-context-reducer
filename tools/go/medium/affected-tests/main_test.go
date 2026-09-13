package main

import "testing"

func TestAnalyzeExplicitMapping(t *testing.T) {
    cfg := config{Mappings: []mapping{{Source: "src/parser/*", Tests: []string{"tests/parser/test_parser.py"}}}}
    got := analyze([]string{"src/parser/lexer.py"}, cfg)
    if got.Confidence != "high" { t.Fatalf("confidence=%s", got.Confidence) }
    if got.Fallback != "none" { t.Fatalf("fallback=%s", got.Fallback) }
    found := false
    for _, x := range got.TestCandidates { if x == "tests/parser/test_parser.py" { found = true } }
    if !found { t.Fatalf("explicit test missing: %#v", got.TestCandidates) }
}

func TestAnalyzeBroadImpact(t *testing.T) {
    got := analyze([]string{"packages/core/src/api.go"}, config{})
    if got.Fallback != "broader" { t.Fatalf("fallback=%s", got.Fallback) }
    if got.Confidence != "medium" { t.Fatalf("confidence=%s", got.Confidence) }
}

func TestAnalyzeNoChanges(t *testing.T) {
    got := analyze(nil, config{})
    if got.Confidence != "low" { t.Fatalf("confidence=%s", got.Confidence) }
    if got.Fallback != "subsystem-or-full" { t.Fatalf("fallback=%s", got.Fallback) }
}
