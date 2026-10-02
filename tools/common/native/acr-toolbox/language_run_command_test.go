package main

import (
	"os"
	"path/filepath"
	"testing"
)

// TestLanguageRunRootFailuresMatchEmptyRootSemantics はmissing/file rootと正常な空directoryを区別する。
func TestLanguageRunRootFailuresMatchEmptyRootSemantics(t *testing.T) {
	base := t.TempDir()
	missing := filepath.Join(base, "missing")
	file := filepath.Join(base, "project.txt")
	if err := os.WriteFile(file, []byte("not a directory"), 0o644); err != nil {
		t.Fatal(err)
	}
	empty := filepath.Join(base, "empty")
	if err := os.Mkdir(empty, 0o755); err != nil {
		t.Fatal(err)
	}
	for _, tc := range []struct {
		name       string
		root       string
		wantStatus string
		wantCode   int
	}{
		{"missing", missing, "input_missing", 2},
		{"file", file, "input_not_directory", 2},
		{"empty", empty, "ok", 0},
	} {
		t.Run(tc.name, func(t *testing.T) {
			code, result := captureJSONCommand(t, func() int { return cmdLanguageRun([]string{tc.root}) })
			if code != tc.wantCode || result["status"] != tc.wantStatus {
				t.Fatalf("unexpected root result: code=%d payload=%#v", code, result)
			}
			if tc.wantStatus == "ok" {
				if result["failure_count"] != float64(0) || len(result["results"].([]any)) != 0 {
					t.Fatalf("empty directory must be a clean empty scan: %#v", result)
				}
				if _, err := os.Stat(filepath.Join(empty, ".acr", "language")); !os.IsNotExist(err) {
					t.Fatalf("empty scan unexpectedly created output: %v", err)
				}
			}
		})
	}
}
