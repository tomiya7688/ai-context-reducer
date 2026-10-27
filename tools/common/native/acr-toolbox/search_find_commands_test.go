package main

import (
	"os"
	"path/filepath"
	"reflect"
	"testing"
)

// TestSearchPortableJSONContract はportable検索が機械可読rowと終了statusを返すことを確認します。
func TestSearchPortableJSONContract(t *testing.T) {
	root := t.TempDir()
	if err := os.MkdirAll(filepath.Join(root, "src"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(root, "src", "a.txt"), []byte("alpha\nneedle here\nomega\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.MkdirAll(filepath.Join(root, "node_modules"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(root, "node_modules", "hidden.txt"), []byte("needle hidden\n"), 0o644); err != nil {
		t.Fatal(err)
	}

	code, payload := captureJSONCommand(t, func() int {
		return cmdSearch([]string{"--backend", "portable", "needle", root})
	})
	if code != 0 {
		t.Fatalf("unexpected exit code %d: %#v", code, payload)
	}
	if payload["tool"] != "text-search" || payload["backend"] != "portable" || payload["status"] != "ok" {
		t.Fatalf("unexpected contract: %#v", payload)
	}
	matches, ok := payload["matches"].([]any)
	if !ok || len(matches) != 1 {
		t.Fatalf("expected one non-ignored match: %#v", payload)
	}
	match := matches[0].(map[string]any)
	if match["path"] != "src/a.txt" || match["line"] != float64(2) || match["text"] != "needle here" {
		t.Fatalf("unexpected match: %#v", match)
	}
}

// TestSearchTruncationContextAndInvalidRegex はmatch周辺行の省略表示とregex errorを確認します。
func TestSearchTruncationContextAndInvalidRegex(t *testing.T) {
	root := t.TempDir()
	if err := os.WriteFile(filepath.Join(root, "a.txt"), []byte("before\nneedle one\nafter\nneedle two\n"), 0o644); err != nil {
		t.Fatal(err)
	}

	code, payload := captureJSONCommand(t, func() int {
		return cmdSearch([]string{"--backend", "portable", "--max-results", "1", "--context", "1", "needle", root})
	})
	if code != 0 || payload["matches_truncated"] != true {
		t.Fatalf("expected bounded search: code=%d payload=%#v", code, payload)
	}
	matches := payload["matches"].([]any)
	match := matches[0].(map[string]any)
	before := match["before"].([]any)
	after := match["after"].([]any)
	if before[0].(map[string]any)["text"] != "before" || after[0].(map[string]any)["text"] != "after" {
		t.Fatalf("unexpected context: %#v", match)
	}

	code, payload = captureJSONCommand(t, func() int {
		return cmdSearch([]string{"--backend", "portable", "(", root})
	})
	if code != 2 || payload["status"] != "invalid_pattern" {
		t.Fatalf("invalid regex must not look like empty success: code=%d payload=%#v", code, payload)
	}
}

// TestFindPortableDefaultIsDeepAndPrunesDependencies は既定で深く検索しdependency directoryを除くことを確認します。
func TestFindPortableDefaultIsDeepAndPrunesDependencies(t *testing.T) {
	root := t.TempDir()
	deep := root
	for i := 0; i < 24; i++ {
		deep = filepath.Join(deep, "d")
	}
	if err := os.MkdirAll(deep, 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(deep, "target.txt"), []byte("x"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.MkdirAll(filepath.Join(root, "node_modules"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(root, "node_modules", "target.txt"), []byte("x"), 0o644); err != nil {
		t.Fatal(err)
	}

	code, payload := captureJSONCommand(t, func() int {
		return cmdFind([]string{"--backend", "portable", "target.txt", root})
	})
	if code != 0 || payload["scan_truncated"] != false {
		t.Fatalf("unexpected find result: code=%d payload=%#v", code, payload)
	}
	results := payload["results"].([]any)
	if len(results) != 1 {
		t.Fatalf("expected one result: %#v", payload)
	}
	result := results[0].(map[string]any)
	if result["kind"] != "file" {
		t.Fatalf("expected file result: %#v", result)
	}
}

// TestFindSeparatesOutputAndScanTruncation は返却件数上限と走査省略signalを別fieldで示すことを確認します。
func TestFindSeparatesOutputAndScanTruncation(t *testing.T) {
	root := t.TempDir()
	for _, name := range []string{"a.txt", "b.txt", "c.txt"} {
		if err := os.WriteFile(filepath.Join(root, name), []byte("x"), 0o644); err != nil {
			t.Fatal(err)
		}
	}

	code, payload := captureJSONCommand(t, func() int {
		return cmdFind([]string{"--backend", "portable", "--max-results", "1", "*.txt", root})
	})
	if code != 0 || payload["results_truncated"] != true || payload["scan_truncated"] != false {
		t.Fatalf("output truncation contract mismatch: code=%d payload=%#v", code, payload)
	}

	code, payload = captureJSONCommand(t, func() int {
		return cmdFind([]string{"--backend", "portable", "--max-results", "0", "--max-visited", "1", "*", root})
	})
	if code != 0 || payload["scan_truncated"] != true || payload["status"] != "partial" {
		t.Fatalf("scan truncation contract mismatch: code=%d payload=%#v", code, payload)
	}
}

// {責務: [TestFindPortableIgnoresGeneratedAndVisitsSelectedKinds: 生成場所の除外と種類別の走査上限を確認する], 処理: [1: 入れ子と生成場所を作る, 2: ファイルとフォルダーの検索順・打ち切りを照合する], 引数: [t: テスト状態], 戻り値: []}
func TestFindPortableIgnoresGeneratedAndVisitsSelectedKinds(t *testing.T) {
	root := t.TempDir()
	for _, name := range []string{"a-dir/inner.txt", "generated/hidden.txt", "z.txt"} {
		file := filepath.Join(root, filepath.FromSlash(name))
		if err := os.MkdirAll(filepath.Dir(file), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(file, []byte("x"), 0o644); err != nil {
			t.Fatal(err)
		}
	}
	for _, tc := range []struct {
		kind      string
		limit     int
		want      []findResult
		truncated bool
	}{
		{"file", 0, []findResult{{"z.txt", "file"}, {"a-dir/inner.txt", "file"}}, false},
		{"file", 1, []findResult{{"z.txt", "file"}}, true},
		{"dir", 1, []findResult{{"a-dir", "dir"}}, false},
		{"any", 1, []findResult{{"a-dir", "dir"}}, true},
	} {
		t.Run(tc.kind, func(t *testing.T) {
			got, _, truncated, stats, err := portableFind(root, "*", tc.kind, 0, 0, tc.limit)
			if err != nil || stats.WalkErrorCount != 0 || truncated != tc.truncated || !reflect.DeepEqual(got, tc.want) {
				t.Fatalf("unexpected search: got=%#v truncated=%v stats=%#v err=%v", got, truncated, stats, err)
			}
		})
	}
}

// {責務: [TestFindPortableDirectoryLinkIsNotFollowed: フォルダーへのリンクを結果に含めても再帰しないことを確認する], 処理: [1: 検索先とリンクを作る, 2: フォルダーとファイルの結果を照合する], 引数: [t: テスト状態], 戻り値: []}
func TestFindPortableDirectoryLinkIsNotFollowed(t *testing.T) {
	root := t.TempDir()
	target := filepath.Join(root, "a-source")
	if err := os.Mkdir(target, 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(target, "item.txt"), []byte("x"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.Symlink(target, filepath.Join(root, "z-link")); err != nil {
		t.Skipf("directory symlink unavailable: %v", err)
	}
	files, _, _, _, err := portableFind(root, "*.txt", "file", 0, 0, 0)
	if err != nil || !reflect.DeepEqual(files, []findResult{{Path: "a-source/item.txt", Kind: "file"}}) {
		t.Fatalf("unexpected file results: got=%#v err=%v", files, err)
	}
	dirs, _, _, _, err := portableFind(root, "*", "dir", 0, 0, 0)
	if err != nil || !reflect.DeepEqual(dirs, []findResult{{Path: "a-source", Kind: "dir"}, {Path: "z-link", Kind: "dir"}}) {
		t.Fatalf("unexpected directory results: got=%#v err=%v", dirs, err)
	}
}
