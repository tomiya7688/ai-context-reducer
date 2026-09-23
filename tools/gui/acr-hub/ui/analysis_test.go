package ui

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/tomiya7688/ai-context-reducer/tools/gui/acr-hub/backend"
)

type sequenceInvoker struct {
	results  []backend.Result
	requests []backend.Request
}

// Invoke はAnalyze -> Selectの呼び出し順と自動実行数を検証するfixtureです。
func (fixture *sequenceInvoker) Invoke(_ context.Context, request backend.Request) backend.Result {
	fixture.requests = append(fixture.requests, request)
	index := len(fixture.requests) - 1
	if index >= len(fixture.results) {
		return backend.Result{State: backend.StateFailure, OutputKind: backend.OutputJSON, ExitCode: -1, Error: "unexpected invocation"}
	}
	return fixture.results[index]
}

// selectorResult はtool-selectorのJSON fixtureを既存CLI resultとして包みます。
func selectorResult(payload any) backend.Result {
	raw, _ := json.Marshal(payload)
	return backend.Result{State: backend.StateSuccess, OutputKind: backend.OutputJSON, ExitCode: 0, CLIStatus: "ok", JSON: raw}
}

// TestProjectAnalysisRunsOnlyAnalyzeAndSelect は推奨されたtoolを勝手に実行しません。
func TestProjectAnalysisRunsOnlyAnalyzeAndSelect(t *testing.T) {
	fixture := &sequenceInvoker{results: []backend.Result{
		selectorResult(map[string]any{"tool": "analyze-and-recommend", "status": "ok", "project_root": "/repo"}),
		selectorResult(map[string]any{
			"tool": "tool-selector", "status": "ok", "project_size_class": "small",
			"recommended_tools": []any{
				map[string]any{"tool_path": "common/small/text-search", "availability": "portable_fallback_ready", "reason": "search first"},
				map[string]any{"tool_path": "common/small/path-find", "availability": "portable_fallback_ready", "reason": "find first"},
			},
			"conditional_tools": []any{},
		}),
	}}
	view := projectAnalysis(context.Background(), fixture, "/repo")
	if view.State != backend.StateSuccess || len(fixture.requests) != 2 {
		t.Fatalf("view=%+v requests=%d", view, len(fixture.requests))
	}
	if fixture.requests[0].Args[0] != "analyze" || fixture.requests[1].Args[0] != "select" {
		t.Fatalf("unexpected flow: %+v", fixture.requests)
	}
	if len(view.Recommended) != 2 || view.Recommended[0].ActionID == "" || view.Recommended[1].ActionID == "" {
		t.Fatalf("unexpected recommendations: %+v", view.Recommended)
	}
}

// TestSmallProjectDoesNotInjectLargeRecommendations はGUI側からLarge候補を追加しません。
func TestSmallProjectDoesNotInjectLargeRecommendations(t *testing.T) {
	fixture := &sequenceInvoker{results: []backend.Result{
		selectorResult(map[string]any{"tool": "analyze-and-recommend", "status": "ok"}),
		selectorResult(map[string]any{
			"tool": "tool-selector", "status": "ok", "project_size_class": "small",
			"recommended_tools": []any{map[string]any{"tool_path": "common/small/text-search", "availability": "portable_fallback_ready", "reason": "search first"}},
			"conditional_tools": []any{},
		}),
	}}
	view := projectAnalysis(context.Background(), fixture, "/repo")
	for _, row := range append(view.Recommended, view.Conditional...) {
		if row.ToolPath == "common/large/source-structure-index" || row.ToolPath == "common/large/context-budget" {
			t.Fatalf("large recommendation was injected: %+v", row)
		}
	}
}

// TestUnmappedRecommendationIsUnavailable はGUI backendにないPython-only候補を偽って実行可能にしません。
func TestUnmappedRecommendationIsUnavailable(t *testing.T) {
	rows := recommendationRows([]selectorTool{
		{ToolPath: "common/small/source-of-truth-candidates", Availability: "ready", Reason: "find authority"},
		{ToolPath: "common/medium/structural-search", Availability: "python_ast_fallback_limited", Reason: "syntax search"},
	}, "recommended")
	if len(rows) != 2 {
		t.Fatalf("rows=%+v", rows)
	}
	for _, row := range rows {
		if row.Kind != "unavailable" || row.ActionID != "" || row.Availability != "gui_backend_unavailable" {
			t.Fatalf("unexpected unavailable mapping: %+v", row)
		}
	}
}

// TestSelectorMappingUsesRunnableGUIAction はnative counterpart候補を既存GUI actionへ接続します。
func TestSelectorMappingUsesRunnableGUIAction(t *testing.T) {
	rows := recommendationRows([]selectorTool{
		{ToolPath: "common/medium/compact-diff", Availability: "ready", Reason: "bounded diff"},
		{ToolPath: "common/large/source-structure-index", Availability: "ready", Reason: "bounded structure"},
	}, "conditional")
	if rows[0].ActionID != "compact-diff" || rows[1].ActionID != "structure-query" {
		t.Fatalf("unexpected mappings: %+v", rows)
	}
}
