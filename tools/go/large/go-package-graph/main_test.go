package main

import (
    "os"
    "path/filepath"
    "testing"
)

// TestBuildPackageGraphReportsParseFailureでparse失敗・truncation・routing契約が回帰していないことを検証する。
func TestBuildPackageGraphReportsParseFailure(t *testing.T) {
    dir := t.TempDir()
    if err := os.WriteFile(filepath.Join(dir, "go.mod"), []byte("module example.com/demo\n"), 0o644); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(dir, "good.go"), []byte("package demo\n"), 0o644); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(dir, "broken.go"), []byte("package demo\nimport (\n"), 0o644); err != nil {
        t.Fatal(err)
    }
    result, err := buildPackageGraph(dir, 0)
    if err != nil {
        t.Fatal(err)
    }
    if result.Status != "ok_with_warnings" || result.ParseErrorCount != 1 {
        t.Fatalf("unexpected graph result: %#v", result)
    }
    if result.FileCountTotal != 2 || result.FilesScanned != 2 {
        t.Fatalf("unexpected file counts: %#v", result)
    }
}

// TestBuildPackageGraphTruncationIsRealでparse失敗・truncation・routing契約が回帰していないことを検証する。
func TestBuildPackageGraphTruncationIsReal(t *testing.T) {
    dir := t.TempDir()
    if err := os.WriteFile(filepath.Join(dir, "go.mod"), []byte("module example.com/demo\n"), 0o644); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(dir, "a.go"), []byte("package demo\n"), 0o644); err != nil {
        t.Fatal(err)
    }
    exact, err := buildPackageGraph(dir, 1)
    if err != nil {
        t.Fatal(err)
    }
    if exact.ScanTruncated {
        t.Fatalf("exact limit must not truncate: %#v", exact)
    }
    if err := os.WriteFile(filepath.Join(dir, "b.go"), []byte("package demo\n"), 0o644); err != nil {
        t.Fatal(err)
    }
    limited, err := buildPackageGraph(dir, 1)
    if err != nil {
        t.Fatal(err)
    }
    if !limited.ScanTruncated || limited.FileCountTotal != 2 || limited.FilesScanned != 1 {
        t.Fatalf("unexpected limited graph: %#v", limited)
    }
}
