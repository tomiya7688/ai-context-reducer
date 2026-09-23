package backend

import (
    "encoding/json"
    "fmt"
    "strings"
)

var binaryNames = map[Program]string{
    ProgramACRToolbox:     "acr-toolbox",
    ProgramGoSymbols:      "go-symbols",
    ProgramGoImportMap:    "go-import-map",
    ProgramGoPackageGraph: "go-package-graph",
    ProgramAffectedTests:  "affected-tests",
}

var textToolboxCommands = map[string]bool{
    "tree":                      true,
    "compact-diff":              true,
    "remote-delta":              true,
    "context-pack-builder":      true,
    "responsibility-candidates": true,
}

// validateRequest は任意process実行へ広がらないよう配布CLIだけを許可します。
func validateRequest(request Request) error {
    if _, ok := binaryNames[request.Program]; !ok {
        return fmt.Errorf("unsupported program: %q", request.Program)
    }
    if request.Program == ProgramACRToolbox && len(request.Args) == 0 {
        return fmt.Errorf("acr-toolbox subcommand is required")
    }
    return nil
}

// outputKind はCLIの既存契約に従いJSONとtext artifactを区別します。
func outputKind(request Request) OutputKind {
    if request.Program != ProgramACRToolbox || len(request.Args) == 0 {
        return OutputJSON
    }
    if textToolboxCommands[request.Args[0]] {
        return OutputText
    }
    return OutputJSON
}

// isHeavyCommand は明示確認なしで起動してはいけない既存CLIを判定します。
func isHeavyCommand(request Request) bool {
    return request.Program == ProgramACRToolbox && len(request.Args) > 0 && request.Args[0] == "language-large-run"
}

// extractCLIStatus はJSONを再構築せずstatus fieldだけを読み取ります。
func extractCLIStatus(raw []byte) string {
    var value map[string]any
    if err := json.Unmarshal(raw, &value); err != nil {
        return ""
    }
    status, _ := value["status"].(string)
    return status
}

// classifyJSONResult はCLIのdomain resultとprocess失敗を分けてGUI用stateへ写像します。
func classifyJSONResult(exitCode int, status string) State {
    if status == "confirmation_required" {
        return StateConfirmationRequired
    }
    if status == "input_missing" || status == "input_not_directory" || status == "backend_query_unsupported" || strings.Contains(status, "unavailable") {
        return StateUnavailable
    }
    if status == "violations" || status == "drift_detected" {
        return StateSuccess
    }
    if exitCode == 0 {
        return StateSuccess
    }
    return StateFailure
}
