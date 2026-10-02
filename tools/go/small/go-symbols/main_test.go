package main

import (
    "os"
    "path/filepath"
    "testing"
)

// TestBuildResultDistinguishesParseFailureでparse失敗・unsupported input・truncation契約が回帰していないことを検証する。
func TestBuildResultDistinguishesParseFailure(t *testing.T) {
    dir := t.TempDir()
    path := filepath.Join(dir, "broken.go")
    if err := os.WriteFile(path, []byte("package broken\nfunc bad( {\n"), 0o644); err != nil {
        t.Fatal(err)
    }
    result, err := buildResult([]string{path})
    if err != nil {
        t.Fatal(err)
    }
    if result.Status != "ok_with_warnings" || result.ParseErrorCount != 1 {
        t.Fatalf("unexpected result: %#v", result)
    }
    if len(result.Files) != 1 || result.Files[0].Status != "parse_failed" {
        t.Fatalf("parse failure was not preserved: %#v", result.Files)
    }
}

// TestScanReportsReadFailureでsource read失敗がparse失敗へ混同されないことを検証する。
func TestScanReportsReadFailure(t *testing.T) {
    result := scan(filepath.Join(t.TempDir(), "missing.go"))
    if result.Status != "read_failed" || result.Error == "" {
        t.Fatalf("read failure was not preserved: %#v", result)
    }
    aggregate := resultFromRows([]fileSymbols{result}, nil)
    if aggregate.Status != "ok_with_warnings" || aggregate.ReadErrorCount != 1 || aggregate.ParseErrorCount != 0 {
        t.Fatalf("read failure was reported as clean or as parse failure: %#v", aggregate)
    }
}

// TestBuildResultReportsUnsupportedAndMissingInputsでparse失敗・unsupported input・truncation契約が回帰していないことを検証する。
func TestBuildResultReportsUnsupportedAndMissingInputs(t *testing.T) {
    dir := t.TempDir()
    txt := filepath.Join(dir, "notes.txt")
    if err := os.WriteFile(txt, []byte("hello\n"), 0o644); err != nil {
        t.Fatal(err)
    }
    result, err := buildResult([]string{txt, filepath.Join(dir, "missing.go")})
    if err != nil {
        t.Fatal(err)
    }
    if result.UnsupportedInputCount != 2 || result.Status != "ok_with_warnings" {
        t.Fatalf("unexpected result: %#v", result)
    }
    reasons := map[string]bool{}
    for _, row := range result.UnsupportedInputs {
        reasons[row.Reason] = true
    }
    if !reasons["unsupported_input"] || !reasons["input_missing"] {
        t.Fatalf("missing reasons: %#v", result.UnsupportedInputs)
    }
}
