package main

import "testing"

// TestContextTermPresentUsesASCIIWordBoundaries はASCII termをword boundaryで照合し部分語を除くことを確認します。
func TestContextTermPresentUsesASCIIWordBoundaries(t *testing.T) {
    if contextTermPresent("latest", "test") {
        t.Fatal("test must not match inside latest")
    }
    if contextTermPresent("goalkeeper", "goal") {
        t.Fatal("goal must not match inside goalkeeper")
    }
    if !contextTermPresent("goal required tests", "tests") {
        t.Fatal("standalone term should match")
    }
    if !contextTermPresent("目的と検証", "検証") {
        t.Fatal("Japanese term should remain substring-matchable")
    }
}

// TestExtractAcceptanceSectionsAndTruncation はAcceptance本文の抽出と上限到達時の省略signalを確認します。
func TestExtractAcceptanceSectionsAndTruncation(t *testing.T) {
    lines := []string{
        "# Goal",
        "first",
        "second",
        "# Goalkeeper notes",
        "must not become goal",
        "# Acceptance",
        "done",
    }
    sections, truncated := extractAcceptanceSections(lines, 1)
    if len(sections["goal"]) != 1 || sections["goal"][0] != "first" || !truncated["goal"] {
        t.Fatalf("unexpected goal section: %#v truncated=%#v", sections["goal"], truncated)
    }
    if len(sections["acceptance"]) != 1 || sections["acceptance"][0] != "done" || truncated["acceptance"] {
        t.Fatalf("unexpected acceptance section: %#v truncated=%#v", sections["acceptance"], truncated)
    }
}

// TestExplorationStopRejectsSubstringFalsePositive は必須語を含むだけの長い単語を完了条件に数えないことを確認します。
func TestExplorationStopRejectsSubstringFalsePositive(t *testing.T) {
    result := evaluateExplorationStop("Goal Required Acceptance source latest")
    checks := result["checks"].(map[string]bool)
    if checks["tests"] {
        t.Fatalf("latest must not satisfy tests: %#v", result)
    }
    if result["stop_broad_exploration"].(bool) {
        t.Fatalf("exploration must continue when tests context is missing: %#v", result)
    }
}

// TestExplorationStopSupportsJapaneseTerms は日本語の探索条件語も停止判定に使えることを確認します。
func TestExplorationStopSupportsJapaneseTerms(t *testing.T) {
    result := evaluateExplorationStop("目的 要件 完了条件 対象ファイル 検証")
    if !result["stop_broad_exploration"].(bool) {
        t.Fatalf("expected sufficient Japanese context: %#v", result)
    }
}
