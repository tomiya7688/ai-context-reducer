package ui

import (
	"encoding/json"
	"fmt"
	"sort"
	"strings"

	"github.com/tomiya7688/ai-context-reducer/tools/gui/acr-hub/backend"
)

// SummaryItem はraw outputを大量表示せず、判断に必要なscalarだけを示します。
type SummaryItem struct {
	Label string `json:"label"`
	Value string `json:"value"`
}

// ResultView はGUIが最初に表示するcompact resultと折りたたみ詳細を分けます。
type ResultView struct {
	State           backend.State      `json:"state"`
	Headline        string             `json:"headline"`
	CLIStatus       string             `json:"cli_status,omitempty"`
	ExitCode        int                `json:"exit_code"`
	Summary         []SummaryItem      `json:"summary"`
	Detail          string             `json:"detail,omitempty"`
	Stderr          string             `json:"stderr,omitempty"`
	DetailTruncated bool               `json:"detail_truncated,omitempty"`
	Error           string             `json:"error,omitempty"`
	OutputKind      backend.OutputKind `json:"output_kind"`
}

// resultView はbackend resultを表示専用のcompact viewへ変換します。
func resultView(result backend.Result) ResultView {
	view := ResultView{
		State:           result.State,
		Headline:        headline(result),
		CLIStatus:       result.CLIStatus,
		ExitCode:        result.ExitCode,
		Stderr:          strings.TrimSpace(result.Stderr),
		DetailTruncated: result.StdoutTruncated || result.StderrTruncated,
		Error:           result.Error,
		OutputKind:      result.OutputKind,
	}
	if result.OutputKind == backend.OutputJSON && len(result.JSON) > 0 {
		view.Detail = string(result.JSON)
		view.Summary = summarizeJSON(result.JSON)
	} else {
		view.Detail = strings.TrimSpace(result.Text)
		view.Summary = summarizeText(result.Text)
	}
	return view
}

// headline はprocess stateとCLI statusを短い人間向け表示へ変換します。
func headline(result backend.Result) string {
	switch result.State {
	case backend.StateSuccess:
		switch result.CLIStatus {
		case "ok_with_warnings":
			return "完了（警告あり）"
		case "violations":
			return "確認項目あり"
		case "drift_detected":
			return "差分あり"
		default:
			return "完了"
		}
	case backend.StateUnavailable:
		return "利用できません"
	case backend.StateConfirmationRequired:
		return "明示確認が必要です"
	case backend.StateTimeout:
		return "時間上限に達しました"
	case backend.StateCancelled:
		return "キャンセルしました"
	default:
		return "実行に失敗しました"
	}
}

// summarizeJSON はtop-level scalarだけを最大10件取り出し巨大array/objectを通常表示から外します。
func summarizeJSON(raw []byte) []SummaryItem {
	var object map[string]any
	if err := json.Unmarshal(raw, &object); err != nil {
		return nil
	}
	priority := []string{"tool", "status", "backend", "project_root", "root_path", "language", "reason", "error", "output_path", "index_path"}
	seen := map[string]bool{}
	items := []SummaryItem{}
	add := func(key string) {
		if len(items) >= 10 || seen[key] {
			return
		}
		value, ok := scalarString(object[key])
		if !ok {
			return
		}
		seen[key] = true
		items = append(items, SummaryItem{Label: key, Value: value})
	}
	for _, key := range priority {
		add(key)
	}
	keys := make([]string, 0, len(object))
	for key := range object {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	for _, key := range keys {
		add(key)
	}
	return items
}

// scalarString はcompact viewに安全なscalarだけを文字列化します。
func scalarString(value any) (string, bool) {
	switch typed := value.(type) {
	case string:
		if len(typed) > 240 {
			return typed[:240] + "…", true
		}
		return typed, true
	case float64:
		return fmt.Sprintf("%v", typed), true
	case bool:
		return fmt.Sprintf("%t", typed), true
	case nil:
		return "null", true
	default:
		return "", false
	}
}

// summarizeText はtext artifactの先頭行と保持bytesだけを通常表示へ出します。
func summarizeText(value string) []SummaryItem {
	trimmed := strings.TrimSpace(value)
	if trimmed == "" {
		return []SummaryItem{{Label: "output", Value: "(empty)"}}
	}
	first := trimmed
	if index := strings.IndexByte(first, '\n'); index >= 0 {
		first = first[:index]
	}
	if len(first) > 240 {
		first = first[:240] + "…"
	}
	return []SummaryItem{
		{Label: "first_line", Value: first},
		{Label: "captured_bytes", Value: fmt.Sprintf("%d", len(value))},
	}
}
