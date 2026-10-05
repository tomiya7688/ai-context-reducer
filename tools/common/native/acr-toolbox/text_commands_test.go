package main

import (
	"io"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func captureSliceOutput(t *testing.T, args ...string) (int, string) {
	t.Helper()
	previous := os.Stdout
	reader, writer, err := os.Pipe()
	if err != nil {
		t.Fatal(err)
	}
	os.Stdout = writer
	code := cmdSlice(args)
	_ = writer.Close()
	os.Stdout = previous
	output, err := io.ReadAll(reader)
	_ = reader.Close()
	if err != nil {
		t.Fatal(err)
	}
	return code, string(output)
}

// TestSliceReportsOnlyRealTruncation はsliceのexact-limit false positiveを防止します。
func TestSliceReportsOnlyRealTruncation(t *testing.T) {
	dir := t.TempDir()
	source := filepath.Join(dir, "matches.txt")
	for _, tc := range []struct {
		name     string
		content  string
		wantMark bool
	}{
		{name: "under-limit", content: "hit\n", wantMark: false},
		{name: "exact-limit", content: "hit\nhit\n", wantMark: false},
		{name: "over-limit", content: "hit\nhit\nhit\n", wantMark: true},
	} {
		t.Run(tc.name, func(t *testing.T) {
			if err := os.WriteFile(source, []byte(tc.content), 0o644); err != nil {
				t.Fatal(err)
			}
			code, output := captureSliceOutput(t, "--max-matches=2", "hit", source)
			if code != 0 {
				t.Fatalf("slice exit code = %d", code)
			}
			gotMark := strings.Contains(output, "[truncated: max matches reached]")
			if gotMark != tc.wantMark {
				t.Fatalf("truncation marker=%v, want %v; output=%q", gotMark, tc.wantMark, output)
			}
		})
	}
}

// TestSliceNonpositiveLimitMeansUnlimited は0以下のmatch上限を無制限として扱います。
func TestSliceNonpositiveLimitMeansUnlimited(t *testing.T) {
	source := filepath.Join(t.TempDir(), "matches.txt")
	if err := os.WriteFile(source, []byte("hit\nhit\nhit\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	for _, limit := range []string{"0", "-1"} {
		t.Run(limit, func(t *testing.T) {
			code, output := captureSliceOutput(t, "--max-matches="+limit, "hit", source)
			if code != 0 || strings.Contains(output, "[truncated: max matches reached]") {
				t.Fatalf("nonpositive limit should be unlimited: code=%d output=%q", code, output)
			}
		})
	}
}
