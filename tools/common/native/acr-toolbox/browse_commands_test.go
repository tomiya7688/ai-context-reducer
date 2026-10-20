package main

import (
	"errors"
	"io"
	"os"
	"path/filepath"
	"testing"
)

// TestBrowseCommandsDistinguishMissingNonDirectoryAndEmptyRoot は取得失敗を空の成功出力にしない。
func TestBrowseCommandsDistinguishMissingNonDirectoryAndEmptyRoot(t *testing.T) {
	empty := t.TempDir()
	file := filepath.Join(t.TempDir(), "root.txt")
	if err := os.WriteFile(file, []byte("x"), 0o644); err != nil {
		t.Fatal(err)
	}
	missing := filepath.Join(t.TempDir(), "missing")
	commands := []struct {
		name string
		run  func(string) int
	}{
		{"tree", func(root string) int { return cmdTree([]string{root}) }},
		{"doc-index", func(root string) int { return cmdDocIndex([]string{root}) }},
	}
	for _, command := range commands {
		t.Run(command.name, func(t *testing.T) {
			if code := command.run(missing); code != 2 {
				t.Fatalf("missing root must exit 2, got %d", code)
			}
			if code := command.run(file); code != 2 {
				t.Fatalf("file root must exit 2, got %d", code)
			}
			if code := command.run(empty); code != 0 {
				t.Fatalf("existing empty directory should succeed, code=%d", code)
			}
		})
	}
}

// TestBrowseCommandsReportWalkAndDocumentReadFailures はpartial scanをclean成功として返さない。
func TestBrowseCommandsReportWalkAndDocumentReadFailures(t *testing.T) {
	root := t.TempDir()
	_, status := walkBrowseRootWith(root, "tree", os.Stat, func(string, bool) (walkResult, error) {
		return walkResult{ErrorCount: 1, WalkErrorCount: 1}, nil
	})
	if status != 2 {
		t.Fatalf("walk failure must exit 2, got %d", status)
	}

	document := filepath.Join(root, "README.md")
	if err := os.WriteFile(document, []byte("# Heading\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	status = cmdDocIndexWithOpen(root, func(string) (io.ReadCloser, error) {
		return nil, errors.New("permission denied")
	})
	if status != 2 {
		t.Fatalf("document read failure must exit 2, got %d", status)
	}
}
