package main

import (
    "os"
    "path/filepath"
    "testing"
)

// TestValidationPlanAvoidsUISubstringFalsePositive は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestValidationPlanAvoidsUISubstringFalsePositive(t *testing.T) {
    result := classifyValidationPath("build/core.py")
    for _, value := range result {
        if value == "visual confirmation when acceptance is visual" {
            t.Fatalf("build path must not be treated as UI: %#v", result)
        }
    }
    foundTests := false
    for _, value := range result {
        if value == "targeted tests" {
            foundTests = true
        }
    }
    if !foundTests {
        t.Fatalf("source validation missing: %#v", result)
    }
}

// TestValidationPlanCompoundParserTerm は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestValidationPlanCompoundParserTerm(t *testing.T) {
    result := classifyValidationPath("tools/parser_rules.py")
    found := false
    for _, value := range result {
        if value == "contract/spec check" {
            found = true
        }
    }
    if !found {
        t.Fatalf("compound parser term not recognized: %#v", result)
    }
}

// TestChangeRouterTestCandidateAvoidsSubstringFalsePositive は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestChangeRouterTestCandidateAvoidsSubstringFalsePositive(t *testing.T) {
    if changeRouterIsTestCandidate("latest.py", nil) || changeRouterIsTestCandidate("contest.py", nil) {
        t.Fatal("substring test false positive")
    }
    if !changeRouterIsTestCandidate("test_widget.py", nil) || !changeRouterIsTestCandidate("widget.test.js", nil) {
        t.Fatal("expected test filename pattern")
    }
    if !changeRouterIsTestCandidate("widget.py", []string{"tests"}) {
        t.Fatal("tests directory must mark candidate")
    }
}

// TestChangeRouterIndexTruncationRequiresAdditionalCandidate は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestChangeRouterIndexTruncationRequiresAdditionalCandidate(t *testing.T) {
    root := t.TempDir()
    testsDir := filepath.Join(root, "tests")
    if err := os.MkdirAll(testsDir, 0o755); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(testsDir, "test_a.py"), []byte(""), 0o644); err != nil {
        t.Fatal(err)
    }
    docsDir := filepath.Join(root, "docs")
    if err := os.MkdirAll(docsDir, 0o755); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(docsDir, "a.md"), []byte(""), 0o644); err != nil {
        t.Fatal(err)
    }

    rows, truncated, errors, err := scanChangeRouterCandidates(root, 2)
    if err != nil || len(rows) != 2 || truncated || errors != 0 {
        t.Fatalf("exact cap should be complete: rows=%#v truncated=%v errors=%d err=%v", rows, truncated, errors, err)
    }

    rows, truncated, errors, err = scanChangeRouterCandidates(root, 1)
    if err != nil || len(rows) != 1 || !truncated || errors != 0 {
        t.Fatalf("additional candidate should mark truncation: rows=%#v truncated=%v errors=%d err=%v", rows, truncated, errors, err)
    }
}

// TestChangeRouterCLIExplicitChangedIsSelfDescribing は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestChangeRouterCLIExplicitChangedIsSelfDescribing(t *testing.T) {
    root := t.TempDir()
    if err := os.MkdirAll(filepath.Join(root, "tests"), 0o755); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(root, "tests", "test_widget.py"), []byte(""), 0o644); err != nil {
        t.Fatal(err)
    }
    if err := os.MkdirAll(filepath.Join(root, "docs"), 0o755); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(root, "docs", "widget.md"), []byte(""), 0o644); err != nil {
        t.Fatal(err)
    }

    code, payload := captureJSONCommand(t, func() int {
        return cmdChangeRouter([]string{"--changed", "src/widget.py", "--per-kind", "1", root})
    })
    if code != 0 || payload["status"] != "ok" || payload["changed_source"] != "explicit" {
        t.Fatalf("unexpected CLI result: code=%d payload=%#v", code, payload)
    }
    routes := payload["routes"].([]any)
    route := routes[0].(map[string]any)
    if route["changed_file"] != "src/widget.py" {
        t.Fatalf("unexpected route: %#v", route)
    }
}
