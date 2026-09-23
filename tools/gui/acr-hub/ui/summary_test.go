package ui

import (
	"encoding/json"
	"strings"
	"testing"

	"github.com/tomiya7688/ai-context-reducer/tools/gui/acr-hub/backend"
)

// TestResultViewKeepsLargeArraysInDetails は大量rowをcompact summaryへ展開しません。
func TestResultViewKeepsLargeArraysInDetails(t *testing.T) {
	raw := []byte("{\"tool\":\"context-manifest\",\"status\":\"ok\",\"returned_files\":200,\"files\":[{\"path\":\"a\"},{\"path\":\"b\"}],\"output_path\":\"/tmp/result.json\"}")
	view := resultView(backend.Result{
		State: backend.StateSuccess, OutputKind: backend.OutputJSON, ExitCode: 0, CLIStatus: "ok", JSON: json.RawMessage(raw),
	})
	for _, item := range view.Summary {
		if strings.Contains(item.Value, "\"path\"") {
			t.Fatalf("array leaked into compact summary: %+v", view.Summary)
		}
	}
	if view.Detail != string(raw) {
		t.Fatalf("raw detail changed: %q", view.Detail)
	}
}

// TestHeadlineDistinguishesUnavailable は利用不可を通常failureと分けます。
func TestHeadlineDistinguishesUnavailable(t *testing.T) {
	view := resultView(backend.Result{State: backend.StateUnavailable, OutputKind: backend.OutputJSON, ExitCode: 2})
	if view.Headline != "利用できません" {
		t.Fatalf("headline = %q", view.Headline)
	}
}

// TestTextSummaryIsCompact はtext artifactの全文をsummaryへ複製しません。
func TestTextSummaryIsCompact(t *testing.T) {
	value := strings.Repeat("line\n", 200)
	view := resultView(backend.Result{State: backend.StateSuccess, OutputKind: backend.OutputText, ExitCode: 0, Text: value})
	if len(view.Summary) != 2 || len(view.Detail) != len(strings.TrimSpace(value)) {
		t.Fatalf("unexpected text view: %+v", view)
	}
}
