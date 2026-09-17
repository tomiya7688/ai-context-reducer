package main

import (
    "os"
    "path/filepath"
    "testing"
)

func TestBuildImportMapDistinguishesParseFailure(t *testing.T) {
    dir := t.TempDir()
    if err := os.WriteFile(filepath.Join(dir, "good.go"), []byte("package demo\nimport \"fmt\"\nvar _ = fmt.Println\n"), 0o644); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(dir, "broken.go"), []byte("package demo\nimport (\n"), 0o644); err != nil {
        t.Fatal(err)
    }
    result, err := buildImportMap(dir, 0)
    if err != nil {
        t.Fatal(err)
    }
    if result.Status != "ok_with_warnings" || result.ParseErrorCount != 1 {
        t.Fatalf("unexpected result: %#v", result)
    }
    found := false
    for _, row := range result.Files {
        if row.File == "broken.go" {
            found = true
            if row.Status != "parse_failed" || len(row.Imports) != 0 {
                t.Fatalf("parse failure collapsed into success: %#v", row)
            }
        }
    }
    if !found {
        t.Fatal("broken.go was not returned")
    }
}

func TestBuildImportMapTruncationIsReal(t *testing.T) {
    dir := t.TempDir()
    if err := os.WriteFile(filepath.Join(dir, "a.go"), []byte("package demo\n"), 0o644); err != nil {
        t.Fatal(err)
    }
    exact, err := buildImportMap(dir, 1)
    if err != nil {
        t.Fatal(err)
    }
    if exact.ScanTruncated {
        t.Fatalf("exact limit must not truncate: %#v", exact)
    }
    if err := os.WriteFile(filepath.Join(dir, "b.go"), []byte("package demo\n"), 0o644); err != nil {
        t.Fatal(err)
    }
    limited, err := buildImportMap(dir, 1)
    if err != nil {
        t.Fatal(err)
    }
    if !limited.ScanTruncated || limited.FileCountTotal != 2 || limited.FilesReturned != 1 {
        t.Fatalf("unexpected limited result: %#v", limited)
    }
}
