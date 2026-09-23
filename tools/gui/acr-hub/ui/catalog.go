package ui

import (
	"fmt"
	"sort"
	"strings"
	"time"

	"github.com/tomiya7688/ai-context-reducer/tools/gui/acr-hub/backend"
)

// Category は利用者がtool名を知らなくても目的から機能を探せる分類です。
type Category struct {
	ID    string `json:"id"`
	Title string `json:"title"`
}

// Option はselect入力で利用者に見せる値と表示名を分離します。
type Option struct {
	Value string `json:"value"`
	Label string `json:"label"`
}

// Field は1つのactionが必要とする入力だけを画面へ伝えます。
type Field struct {
	ID          string   `json:"id"`
	Label       string   `json:"label"`
	Kind        string   `json:"kind"`
	Required    bool     `json:"required"`
	Placeholder string   `json:"placeholder,omitempty"`
	Help        string   `json:"help,omitempty"`
	Options     []Option `json:"options,omitempty"`
	Default     string   `json:"default,omitempty"`
}

// Action はGUIのカード表示と既存CLI invocationの対応を定義します。
type Action struct {
	ID               string          `json:"id"`
	Category         string          `json:"category"`
	Title            string          `json:"title"`
	Description      string          `json:"description"`
	Fields           []Field         `json:"fields"`
	Heavy            bool            `json:"heavy,omitempty"`
	WritesFiles      bool            `json:"writes_files,omitempty"`
	TechnicalCommand string          `json:"technical_command"`
	Program          backend.Program `json:"-"`
	Timeout          time.Duration   `json:"-"`
}

// Categories はIssue #26で定義した6分類を表示順付きで返します。
func Categories() []Category {
	return []Category{
		{ID: "project-analysis", Title: "Project Analysis"},
		{ID: "context-reduction", Title: "Context Reduction"},
		{ID: "search-structure", Title: "Search / Structure"},
		{ID: "change-validation", Title: "Change / Validation"},
		{ID: "policy-maintenance", Title: "Policy / Maintenance"},
		{ID: "templates", Title: "Templates"},
	}
}

// Actions はGUIから明示実行できる主要機能を目的名で定義します。
func Actions() []Action {
	project := Field{ID: "project_root", Label: "Project root", Kind: "project_root", Required: true, Placeholder: "/path/to/project"}
	pathList := func(id, label, help string) Field {
		return Field{ID: id, Label: label, Kind: "multiline", Required: true, Placeholder: "1行に1path", Help: help}
	}
	return []Action{
		{ID: "project-overview", Category: "project-analysis", Title: "プロジェクト概要を確認", Description: "repositoryの規模・言語・runtime等の事実を確認します。", Fields: []Field{project}, TechnicalCommand: "acr-toolbox analyze", Program: backend.ProgramACRToolbox},
		{ID: "tool-routing", Category: "project-analysis", Title: "使う機能を選ぶ", Description: "現在のrepositoryに合う機能候補と探索停止条件を確認します。", Fields: []Field{project}, TechnicalCommand: "acr-toolbox select", Program: backend.ProgramACRToolbox},
		{ID: "language-setup", Category: "project-analysis", Title: "言語解析の利用可否を確認", Description: "既存runtime/compilerを確認し、利用できる言語解析だけを候補化します。", Fields: []Field{project}, TechnicalCommand: "acr-toolbox language-setup", Program: backend.ProgramACRToolbox},
		{ID: "context-manifest", Category: "context-reduction", Title: "参照候補を小さく一覧化", Description: "source・test・docsの候補をboundedなpointer一覧へ圧縮します。", Fields: []Field{project}, TechnicalCommand: "acr-toolbox context-manifest", Program: backend.ProgramACRToolbox},
		{
			ID: "context-budget", Category: "context-reduction", Title: "コンテキスト量を見積もる", Description: "大きな候補を読む前に概算コストを確認します。",
			Fields: []Field{project, {ID: "mode", Label: "Estimate mode", Kind: "select", Default: "fast", Options: []Option{{Value: "fast", Label: "Fast"}, {Value: "accurate", Label: "Accurate (reads text)"}}}},
			TechnicalCommand: "acr-toolbox context-budget", Program: backend.ProgramACRToolbox,
		},
		{
			ID: "context-pack", Category: "context-reduction", Title: "作業用Context Packを作る", Description: "現在taskのGoal / Acceptanceとpointerを短いMarkdownへまとめます。",
			Fields: []Field{project, {ID: "goal", Label: "Goal", Kind: "text", Required: true, Placeholder: "今回実現すること"}, {ID: "acceptance", Label: "Acceptance", Kind: "text", Required: true, Placeholder: "完了条件"}, {ID: "output", Label: "Output file", Kind: "path", Required: true, Default: "CONTEXT_PACK.md"}},
			WritesFiles: true, TechnicalCommand: "acr-toolbox context-pack-builder", Program: backend.ProgramACRToolbox,
		},
		{
			ID: "text-search", Category: "search-structure", Title: "文字列から候補を探す", Description: "full fileを読む前に一致箇所だけを絞ります。",
			Fields: []Field{project, {ID: "query", Label: "Search text", Kind: "text", Required: true, Placeholder: "ServiceName"}, {ID: "glob", Label: "File glob", Kind: "text", Placeholder: "*.go", Help: "空なら全対象"}},
			TechnicalCommand: "acr-toolbox search", Program: backend.ProgramACRToolbox,
		},
		{
			ID: "path-find", Category: "search-structure", Title: "file pathを探す", Description: "path patternから必要file候補を絞ります。",
			Fields: []Field{project, {ID: "pattern", Label: "Path pattern", Kind: "text", Required: true, Placeholder: "*.go"}},
			TechnicalCommand: "acr-toolbox find", Program: backend.ProgramACRToolbox,
		},
		{ID: "tree-view", Category: "search-structure", Title: "directory構造を小さく見る", Description: "repository全体を展開せずbounded treeを表示します。", Fields: []Field{project}, TechnicalCommand: "acr-toolbox tree", Program: backend.ProgramACRToolbox},
		{
			ID: "target-slice", Category: "search-structure", Title: "対象箇所だけ読む", Description: "pattern周辺のsourceだけをboundedに取り出します。",
			Fields: []Field{{ID: "pattern", Label: "Pattern", Kind: "text", Required: true}, {ID: "file", Label: "Source file", Kind: "path", Required: true}},
			TechnicalCommand: "acr-toolbox slice", Program: backend.ProgramACRToolbox,
		},
		{ID: "large-plan", Category: "search-structure", Title: "高精度解析の利用可否を確認", Description: "重い処理を実行せず、既存のSCIP / Ctags / SDK等が使えるかだけ確認します。", Fields: []Field{project}, TechnicalCommand: "acr-toolbox language-large-plan", Program: backend.ProgramACRToolbox},
		{ID: "large-run", Category: "search-structure", Title: "高精度解析を明示実行", Description: "利用可能な既存backendでLarge解析を実行します。実行前に明示確認が必要です。", Fields: []Field{project}, Heavy: true, TechnicalCommand: "acr-toolbox language-large-run", Program: backend.ProgramACRToolbox, Timeout: 2 * time.Minute},
		{
			ID: "change-routing", Category: "change-validation", Title: "変更から関連箇所を絞る", Description: "changed pathからsource / tests / docs候補へrouteします。",
			Fields: []Field{project, {ID: "changed", Label: "Changed paths", Kind: "multiline", Placeholder: "src/foo.go\\ntests/foo_test.go", Help: "空ならGit差分を利用"}},
			TechnicalCommand: "acr-toolbox change-router", Program: backend.ProgramACRToolbox,
		},
		{ID: "validation-plan", Category: "change-validation", Title: "必要な検証を選ぶ", Description: "変更pathから最小のvalidation種類を選びます。", Fields: []Field{pathList("paths", "Changed paths", "project rootからの相対pathでも可")}, TechnicalCommand: "acr-toolbox validation-plan", Program: backend.ProgramACRToolbox},
		{ID: "affected-tests", Category: "change-validation", Title: "影響するtestを選ぶ", Description: "changed pathから実行候補testを絞ります。", Fields: []Field{project, pathList("changed", "Changed paths", "1件以上指定")}, TechnicalCommand: "affected-tests", Program: backend.ProgramAffectedTests},
		{ID: "syntax-health", Category: "change-validation", Title: "構文状態をcheapに確認", Description: "既存Tree-sitter等が利用可能な場合だけsyntax evidenceを取得します。", Fields: []Field{pathList("paths", "Target files", "parser未導入時はunavailableとして表示")}, TechnicalCommand: "acr-toolbox syntax-health", Program: backend.ProgramACRToolbox},
		{ID: "policy-index", Category: "policy-maintenance", Title: "規則を索引化", Description: "長い規約全文を読む前に機械的なrule候補を一覧化します。", Fields: []Field{project}, TechnicalCommand: "acr-toolbox policy-index", Program: backend.ProgramACRToolbox},
		{ID: "ignore-candidates", Category: "policy-maintenance", Title: "通常contextから外す候補を確認", Description: "generated / logs / cache等の候補だけを提示し、自動ignoreはしません。", Fields: []Field{project}, TechnicalCommand: "acr-toolbox ignore-candidates", Program: backend.ProgramACRToolbox},
		{ID: "duplicate-hints", Category: "policy-maintenance", Title: "文書重複の候補を確認", Description: "類似文書を自動削除せず、drift確認が必要な候補だけを返します。", Fields: []Field{project}, TechnicalCommand: "acr-toolbox doc-duplicate-hints", Program: backend.ProgramACRToolbox},
		{
			ID: "policy-check", Category: "policy-maintenance", Title: "機械判定できる規則を確認", Description: "明示されたrule fileに従って確定可能な規則だけを検査します。",
			Fields: []Field{project, {ID: "rules", Label: "Rules JSON", Kind: "path", Required: true}},
			TechnicalCommand: "acr-toolbox policy-check", Program: backend.ProgramACRToolbox,
		},
		{
			ID: "template", Category: "templates", Title: "定型fileを生成・確認", Description: "canonical templateとvarsからdeterministicに生成またはdrift確認します。",
			Fields: []Field{project, {ID: "template", Label: "Template", Kind: "path", Required: true}, {ID: "vars", Label: "Variables JSON", Kind: "path", Required: true}, {ID: "output", Label: "Output", Kind: "path", Required: true}, {ID: "check", Label: "Check only", Kind: "boolean", Default: "false", Help: "ONならfileを書き換えずdriftだけ確認"}},
			WritesFiles: true, TechnicalCommand: "acr-toolbox template", Program: backend.ProgramACRToolbox,
		},
	}
}

// actionByID はclientから渡されたIDを固定catalogへ戻し任意command化を防ぎます。
func actionByID(id string) (Action, bool) {
	for _, action := range Actions() {
		if action.ID == id {
			return action, true
		}
	}
	return Action{}, false
}

// RunInput はbrowserから受け取る実行入力をaction catalogの値だけに限定します。
type RunInput struct {
	ActionID    string            `json:"action_id"`
	ProjectRoot string            `json:"project_root"`
	Values      map[string]string `json:"values"`
	AllowHeavy  bool              `json:"allow_heavy"`
}

// buildRequest は利用者入力を既存CLIの引数契約へ変換します。
func buildRequest(input RunInput) (backend.Request, Action, error) {
	action, ok := actionByID(input.ActionID)
	if !ok {
		return backend.Request{}, Action{}, fmt.Errorf("unknown action: %q", input.ActionID)
	}
	values := input.Values
	if values == nil {
		values = map[string]string{}
	}
	for _, field := range action.Fields {
		value := inputValue(field, input.ProjectRoot, values)
		if field.Required && strings.TrimSpace(value) == "" {
			return backend.Request{}, action, fmt.Errorf("%s is required", field.Label)
		}
	}
	root := strings.TrimSpace(input.ProjectRoot)
	request := backend.Request{Program: action.Program, WorkingDir: root, Timeout: action.Timeout, AllowHeavy: input.AllowHeavy}
	value := func(key string) string {
		for _, field := range action.Fields {
			if field.ID == key {
				return inputValue(field, input.ProjectRoot, values)
			}
		}
		return strings.TrimSpace(values[key])
	}

	switch action.ID {
	case "project-overview":
		request.Args = []string{"analyze", root}
	case "tool-routing":
		request.Args = []string{"select", root}
	case "language-setup":
		request.Args = []string{"language-setup", root}
	case "context-manifest":
		request.Args = []string{"context-manifest", root}
	case "context-budget":
		request.Args = []string{"context-budget", "--mode", value("mode"), "--top", "40", root}
	case "context-pack":
		request.Args = []string{"context-pack-builder", "--goal", value("goal"), "--acceptance", value("acceptance"), "--output", value("output"), root}
	case "text-search":
		request.Args = []string{"search", "--max-results", "50"}
		if glob := value("glob"); glob != "" {
			request.Args = append(request.Args, "--glob", glob)
		}
		request.Args = append(request.Args, value("query"), root)
	case "path-find":
		request.Args = []string{"find", "--type", "file", "--max-results", "80", value("pattern"), root}
	case "tree-view":
		request.Args = []string{"tree", root}
	case "target-slice":
		request.Args = []string{"slice", value("pattern"), value("file")}
	case "large-plan":
		request.Args = []string{"language-large-plan", root}
	case "large-run":
		request.Args = []string{"language-large-run"}
		if input.AllowHeavy {
			request.Args = append(request.Args, "--allow-heavy")
		}
		request.Args = append(request.Args, root)
	case "change-routing":
		request.Args = []string{"change-router"}
		for _, changed := range splitLines(value("changed")) {
			request.Args = append(request.Args, "--changed", changed)
		}
		request.Args = append(request.Args, root)
	case "validation-plan":
		request.Args = append([]string{"validation-plan"}, splitLines(value("paths"))...)
	case "affected-tests":
		request.Args = []string{"--root", root}
		for _, changed := range splitLines(value("changed")) {
			request.Args = append(request.Args, "--changed", changed)
		}
	case "syntax-health":
		request.Args = append([]string{"syntax-health"}, splitLines(value("paths"))...)
	case "policy-index":
		request.Args = []string{"policy-index", "--max-findings", "120", root}
	case "ignore-candidates":
		request.Args = []string{"ignore-candidates", "--limit", "80", root}
	case "duplicate-hints":
		request.Args = []string{"doc-duplicate-hints", "--max-groups", "80", root}
	case "policy-check":
		request.Args = []string{"policy-check", "--rules", value("rules"), root}
	case "template":
		request.Args = []string{"template", "--template", value("template"), "--vars", value("vars"), "--out", value("output")}
		if strings.EqualFold(value("check"), "true") {
			request.Args = append(request.Args, "--check")
		}
	default:
		return backend.Request{}, action, fmt.Errorf("action is not implemented: %s", action.ID)
	}
	return request, action, nil
}

// inputValue はproject共通入力とaction固有入力を同じ規則で解決します。
func inputValue(field Field, projectRoot string, values map[string]string) string {
	if field.Kind == "project_root" {
		return strings.TrimSpace(projectRoot)
	}
	value := strings.TrimSpace(values[field.ID])
	if value == "" {
		value = field.Default
	}
	return value
}

// splitLines はmultiline入力を順序を保ったCLI argument列へ変換します。
func splitLines(value string) []string {
	lines := []string{}
	for _, line := range strings.Split(value, "\n") {
		line = strings.TrimSpace(line)
		if line != "" {
			lines = append(lines, line)
		}
	}
	return lines
}

// categoryIDs はcatalogが未知categoryを含まないことをtestしやすい形へ整えます。
func categoryIDs() []string {
	ids := make([]string, 0, len(Categories()))
	for _, category := range Categories() {
		ids = append(ids, category.ID)
	}
	sort.Strings(ids)
	return ids
}
