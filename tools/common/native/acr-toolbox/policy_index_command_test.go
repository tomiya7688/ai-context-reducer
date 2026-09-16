package main

import (
    "os"
    "path/filepath"
    "testing"
)

func TestNativePolicyWordsUseBoundaries(t *testing.T) {
    if !isNativePolicyLine("You must run targeted tests.") || !isNativePolicyLine("This should not be skipped.") {
        t.Fatal("expected policy terms")
    }
    if isNativePolicyLine("Mustard belongs in the recipe.") || isNativePolicyLine("Shoulder width is metadata.") {
        t.Fatal("substring false positive")
    }
    if !isNativePolicyLine("変更後の検証は必須です。") {
        t.Fatal("expected Japanese policy term")
    }
}

func TestNativePolicyDiscoveryDedupesAndIgnoresDependencies(t *testing.T) {
    root := t.TempDir()
    docs := filepath.Join(root, "docs")
    if err := os.MkdirAll(docs, 0o755); err != nil {
        t.Fatal(err)
    }
    policy := filepath.Join(docs, "policy.md")
    if err := os.WriteFile(policy, []byte("Must test."), 0o644); err != nil {
        t.Fatal(err)
    }
    ignored := filepath.Join(root, "node_modules", "pkg")
    if err := os.MkdirAll(ignored, 0o755); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(ignored, "README.md"), []byte("must ignore"), 0o644); err != nil {
        t.Fatal(err)
    }

    result := discoverNativePolicyFiles([]string{root, policy})
    if len(result.Files) != 1 || filepath.Clean(result.Files[0]) != filepath.Clean(policy) {
        t.Fatalf("unexpected files: %#v", result.Files)
    }
    if len(result.MissingInputs) != 0 || len(result.UnsupportedInputs) != 0 || result.WalkErrorCount != 0 {
        t.Fatalf("unexpected discovery warnings: %#v", result)
    }
}

func TestNativePolicyIndexZeroLimitIsUnlimited(t *testing.T) {
    root := t.TempDir()
    policy := filepath.Join(root, "policy.md")
    if err := os.WriteFile(policy, []byte("# Rules\nMust test.\nShould document.\n"), 0o644); err != nil {
        t.Fatal(err)
    }

    code, payload := captureJSONCommand(t, func() int {
        return cmdPolicyIndex([]string{"--max-findings", "0", policy})
    })
    if code != 0 || payload["status"] != "ok" {
        t.Fatalf("unexpected result code=%d payload=%#v", code, payload)
    }
    if payload["finding_count_total"] != float64(2) || payload["findings_truncated"] != false {
        t.Fatalf("unexpected findings contract: %#v", payload)
    }
    findings := payload["findings"].([]any)
    if len(findings) != 2 {
        t.Fatalf("expected all findings: %#v", findings)
    }
}

func TestNativePolicyIndexMissingOnlyInputFailsExplicitly(t *testing.T) {
    missing := filepath.Join(t.TempDir(), "missing.md")
    code, payload := captureJSONCommand(t, func() int {
        return cmdPolicyIndex([]string{missing})
    })
    if code != 2 || payload["status"] != "input_unavailable" {
        t.Fatalf("unexpected missing result code=%d payload=%#v", code, payload)
    }
}
