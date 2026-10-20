package main

import (
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
)

// captureGitCommand はGit CLI出力と終了codeを同時に取得しfailure表示を検証する。
func captureGitCommand(t *testing.T, run func() int) (int, string, string) {
	t.Helper()
	oldOut, oldErr := os.Stdout, os.Stderr
	outReader, outWriter, err := os.Pipe()
	if err != nil {
		t.Fatal(err)
	}
	errReader, errWriter, err := os.Pipe()
	if err != nil {
		t.Fatal(err)
	}
	os.Stdout, os.Stderr = outWriter, errWriter
	code := run()
	_ = outWriter.Close()
	_ = errWriter.Close()
	os.Stdout, os.Stderr = oldOut, oldErr
	out, readErr := io.ReadAll(outReader)
	if readErr != nil {
		t.Fatal(readErr)
	}
	errText, readErr := io.ReadAll(errReader)
	if readErr != nil {
		t.Fatal(readErr)
	}
	_ = outReader.Close()
	_ = errReader.Close()
	return code, string(out), string(errText)
}

// createGitFixture はローカルcommitとremote-tracking refを持つ再現可能なrepositoryを作る。
func createGitFixture(t *testing.T) string {
	t.Helper()
	root := t.TempDir()
	commands := [][]string{
		{"init", root},
		{"-C", root, "config", "user.name", "Test"},
		{"-C", root, "config", "user.email", "test@example.invalid"},
	}
	for _, args := range commands {
		if output, err := exec.Command("git", args...).CombinedOutput(); err != nil {
			t.Fatalf("git %v failed: %v: %s", args, err, output)
		}
	}
	if err := os.WriteFile(filepath.Join(root, "README.md"), []byte("# fixture\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	for _, args := range [][]string{
		{"-C", root, "add", "README.md"},
		{"-C", root, "commit", "-m", "fixture"},
		{"-C", root, "update-ref", "refs/remotes/origin/main", "HEAD"},
	} {
		if output, err := exec.Command("git", args...).CombinedOutput(); err != nil {
			t.Fatalf("git %v failed: %v: %s", args, err, output)
		}
	}
	return root
}

// TestCompactDiffDistinguishesEmptyDiffFromInvalidRevision は有効な空差分とGit query failureを区別する。
func TestCompactDiffDistinguishesEmptyDiffFromInvalidRevision(t *testing.T) {
	root := createGitFixture(t)
	code, output, diagnostic := captureGitCommand(t, func() int {
		return cmdCompactDiff([]string{root, "HEAD", "HEAD"})
	})
	if code != 0 || !strings.Contains(output, "## bounded diff") || !strings.Contains(output, "(none)") {
		t.Fatalf("same revision should produce a clean empty diff: code=%d output=%q error=%q", code, output, diagnostic)
	}
	code, output, diagnostic = captureGitCommand(t, func() int {
		return cmdCompactDiff([]string{root, "missing-base", "HEAD"})
	})
	if code != 2 || output != "" || !strings.Contains(diagnostic, "git_query_failed") {
		t.Fatalf("invalid revision must fail explicitly: code=%d output=%q error=%q", code, output, diagnostic)
	}
}

// TestRemoteDeltaSeparatesMissingRemoteFromQueryFailure はremote ref不在と不正baseを異なるstatusにする。
func TestRemoteDeltaSeparatesMissingRemoteFromQueryFailure(t *testing.T) {
	root := createGitFixture(t)
	code, output, diagnostic := captureGitCommand(t, func() int {
		return cmdRemoteDelta([]string{root, "origin/missing", "HEAD"})
	})
	if code != 0 || !strings.Contains(output, "status=remote_unavailable") {
		t.Fatalf("missing remote must remain explicit: code=%d output=%q error=%q", code, output, diagnostic)
	}
	code, output, diagnostic = captureGitCommand(t, func() int {
		return cmdRemoteDelta([]string{root, "origin/main", "missing-base"})
	})
	if code != 2 || output != "" || !strings.Contains(diagnostic, "git_query_failed") {
		t.Fatalf("invalid base must not look like empty delta: code=%d output=%q error=%q", code, output, diagnostic)
	}
}

// TestGitCommandsRejectNonRepositoryAndUnavailableExecutable は外部Git取得失敗を区別してnon-zeroにする。
func TestGitCommandsRejectNonRepositoryAndUnavailableExecutable(t *testing.T) {
	nonRepo := t.TempDir()
	code, output, diagnostic := captureGitCommand(t, func() int {
		return cmdRemoteDelta([]string{nonRepo})
	})
	if code != 2 || output != "" || !strings.Contains(diagnostic, "git_unavailable_or_not_repository") {
		t.Fatalf("non-repository must fail explicitly: code=%d output=%q error=%q", code, output, diagnostic)
	}
	root := createGitFixture(t)
	t.Setenv("PATH", "")
	code, output, diagnostic = captureGitCommand(t, func() int {
		return cmdCompactDiff([]string{root})
	})
	if code != 2 || output != "" || !strings.Contains(diagnostic, "git_unavailable") {
		t.Fatalf("missing Git executable must fail explicitly: code=%d output=%q error=%q", code, output, diagnostic)
	}
}
