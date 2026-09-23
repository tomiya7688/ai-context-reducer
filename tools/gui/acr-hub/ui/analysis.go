package ui

import (
	"context"
	"encoding/json"
	"fmt"
	"path/filepath"
	"strings"

	"github.com/tomiya7688/ai-context-reducer/tools/gui/acr-hub/backend"
)

// Recommendation はtool-selectorの候補をGUIで実行可能なactionへ接続します。
type Recommendation struct {
	Kind         string `json:"kind"`
	ToolPath     string `json:"tool_path"`
	ActionID     string `json:"action_id,omitempty"`
	Title        string `json:"title"`
	Reason       string `json:"reason"`
	Activation   string `json:"activation,omitempty"`
	Availability string `json:"availability"`
	Heavy        bool   `json:"heavy,omitempty"`
}

// ProjectAnalysisInput はワンクリック分析に必要なproject rootだけを受け取ります。
type ProjectAnalysisInput struct {
	ProjectRoot string `json:"project_root"`
}

// ProjectAnalysisView はAnalyze -> Selectの結果と候補だけをcompactに返します。
type ProjectAnalysisView struct {
	State                backend.State    `json:"state"`
	Headline             string           `json:"headline"`
	ProjectSizeClass     string           `json:"project_size_class,omitempty"`
	DetectedProjectTypes []string         `json:"detected_project_types,omitempty"`
	Analysis             ResultView       `json:"analysis"`
	Selection            ResultView       `json:"selection"`
	Recommended          []Recommendation `json:"recommended"`
	Conditional          []Recommendation `json:"conditional"`
	Error                string           `json:"error,omitempty"`
}

type selectorTool struct {
	ToolPath     string `json:"tool_path"`
	Phase        string `json:"phase"`
	Activation   string `json:"activation"`
	Availability string `json:"availability"`
	Reason       string `json:"reason"`
}

type selectorProjectPayload struct {
	Status               string         `json:"status"`
	ProjectSizeClass     string         `json:"project_size_class"`
	DetectedProjectTypes []string       `json:"detected_project_types"`
	RecommendedTools     []selectorTool `json:"recommended_tools"`
	ConditionalTools     []selectorTool `json:"conditional_tools"`
}

var recommendationActionIDs = map[string]string{
	"common/small/repo-profile":              "project-overview",
	"common/small/text-search":                "text-search",
	"common/small/path-find":                  "path-find",
	"common/small/doc-index":                  "doc-index",
	"common/small/git-history-health":         "git-history-health",
	"common/small/syntax-health":              "syntax-health",
	"common/medium/compact-diff":              "compact-diff",
	"common/medium/remote-delta":              "remote-delta",
	"common/medium/change-router":             "change-routing",
	"common/medium/context-pack-builder":      "context-pack",
	"common/medium/validation-plan":           "validation-plan",
	"common/medium/compact-log":               "compact-log",
	"common/medium/acceptance-extractor":      "acceptance-extractor",
	"common/medium/exploration-stop-check":    "exploration-stop",
	"common/medium/responsibility-candidates": "responsibility-candidates",
	"common/medium/doc-duplicate-hints":        "duplicate-hints",
	"common/large/hotspot-report":             "hotspot-report",
	"common/large/context-manifest":            "context-manifest",
	"common/large/source-structure-index":      "structure-query",
	"common/large/target-slice":                "target-slice",
	"common/large/context-budget":              "context-budget",
	"common/medium/policy-index":               "policy-index",
}

// projectAnalysis はrepository factsとselectorだけを実行し候補の実処理は起動しません。
func projectAnalysis(ctx context.Context, invoker Invoker, projectRoot string) ProjectAnalysisView {
	root := strings.TrimSpace(projectRoot)
	if root == "" {
		return ProjectAnalysisView{State: backend.StateFailure, Headline: "Project rootが必要です", Error: "project root is required"}
	}
	root = filepath.Clean(root)
	analyzeResult := invoker.Invoke(ctx, backend.Request{
		Program: backend.ProgramACRToolbox, Args: []string{"analyze", root}, WorkingDir: root,
	})
	analysisView := resultView(analyzeResult)
	if analyzeResult.State != backend.StateSuccess {
		return ProjectAnalysisView{
			State: analyzeResult.State, Headline: "Project Analysisを完了できませんでした",
			Analysis: analysisView, Error: analyzeResult.Error,
		}
	}
	if err := ctx.Err(); err != nil {
		return ProjectAnalysisView{State: backend.StateCancelled, Headline: "Project Analysisをキャンセルしました", Analysis: analysisView, Error: err.Error()}
	}

	selectResult := invoker.Invoke(ctx, backend.Request{
		Program: backend.ProgramACRToolbox, Args: []string{"select", root}, WorkingDir: root,
	})
	selectionView := resultView(selectResult)
	if selectResult.State != backend.StateSuccess {
		return ProjectAnalysisView{
			State: selectResult.State, Headline: "推奨機能を選択できませんでした",
			Analysis: analysisView, Selection: selectionView, Error: selectResult.Error,
		}
	}

	var payload selectorProjectPayload
	if err := json.Unmarshal(selectResult.JSON, &payload); err != nil {
		return ProjectAnalysisView{
			State: backend.StateFailure, Headline: "推奨結果を読み取れませんでした",
			Analysis: analysisView, Selection: selectionView, Error: fmt.Sprintf("parse selector result: %v", err),
		}
	}
	return ProjectAnalysisView{
		State: backend.StateSuccess, Headline: "Project Analysis 完了",
		ProjectSizeClass: payload.ProjectSizeClass, DetectedProjectTypes: payload.DetectedProjectTypes,
		Analysis: analysisView, Selection: selectionView,
		Recommended: recommendationRows(payload.RecommendedTools, "recommended"),
		Conditional: recommendationRows(payload.ConditionalTools, "conditional"),
	}
}

// recommendationRows はselector候補をGUI actionへ結びつけ、未対応機能を明示します。
func recommendationRows(rows []selectorTool, kind string) []Recommendation {
	out := make([]Recommendation, 0, len(rows))
	for _, row := range rows {
		actionID := recommendationActionIDs[row.ToolPath]
		action, actionOK := actionByID(actionID)
		availability := row.Availability
		if availability == "" {
			availability = "ready"
		}
		rowKind := kind
		if strings.Contains(availability, "unavailable") || !actionOK {
			rowKind = "unavailable"
			if !actionOK {
				availability = "gui_backend_unavailable"
				actionID = ""
			}
		}
		title := recommendationTitle(row.ToolPath)
		heavy := false
		if actionOK {
			title = action.Title
			heavy = action.Heavy
		}
		out = append(out, Recommendation{
			Kind: rowKind, ToolPath: row.ToolPath, ActionID: actionID, Title: title,
			Reason: row.Reason, Activation: row.Activation, Availability: availability, Heavy: heavy,
		})
	}
	return out
}

// recommendationTitle はGUI actionを持たない候補にも意味の分かる表示名を与えます。
func recommendationTitle(toolPath string) string {
	switch toolPath {
	case "common/small/source-of-truth-candidates":
		return "Source of Truth候補を探す"
	case "common/medium/structural-search":
		return "構造検索で候補を絞る"
	default:
		parts := strings.Split(toolPath, "/")
		if len(parts) == 0 {
			return toolPath
		}
		return parts[len(parts)-1]
	}
}
