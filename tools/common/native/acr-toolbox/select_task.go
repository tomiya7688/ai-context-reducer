package main

import (
    "path/filepath"
    "strings"
)

// {
//   責務: [
//     selectorTaskOptions: 作業に合う補助ツールを選ぶための条件を保持する
//   ],
//   フィールド: [
//     Root: 調査対象のフォルダー,
//     Goal: 今回の目的,
//     TaskFile: 作業内容の記録場所,
//     ChangedFiles: 変更対象のファイル一覧,
//     ValidationIntent: 必要な検証の範囲
//   ],
//   処理: []
// }
type selectorTaskOptions struct {
    Root             string
    Goal             string
    TaskFile         string
    ChangedFiles     []string
    ValidationIntent string
}

// {
//   責務: [
//     parseSelectorTaskArgs: 引数から調査対象と選択条件を取り出す
//   ],
//   処理: [
//     1: 調査対象の初期値を用意する,
//     2: 引数に書かれた作業条件を順に保存する,
//     3: 組み立てた条件を返す
//   ],
//   引数: [
//     args: コマンドから渡された引数の一覧
//   ],
//   戻り値: [
//     1: 調査対象と作業条件をまとめた情報
//   ],
//   補足: [
//     1: 値が足りない引数や未知の指定のすべてを検証する関数ではない
//   ]
// }
func parseSelectorTaskArgs(args []string) selectorTaskOptions {
    out := selectorTaskOptions{Root: ".", ValidationIntent: "unknown"}
    for i := 0; i < len(args); i++ {
        switch args[i] {
        case "--goal":
            if i+1 < len(args) { i++; out.Goal = args[i] }
        case "--task-file":
            if i+1 < len(args) { i++; out.TaskFile = args[i] }
        case "--changed":
            if i+1 < len(args) { i++; out.ChangedFiles = append(out.ChangedFiles, filepath.ToSlash(args[i])) }
        case "--validation-intent":
            if i+1 < len(args) { i++; out.ValidationIntent = args[i] }
        default:
            if !strings.HasPrefix(args[i], "-") { out.Root = args[i] }
        }
    }
    return out
}

// {
//   責務: [
//     selectorApplyTaskContext: 作業条件に合う補助ツールだけを既存候補から選び出す
//   ],
//   処理: [
//     1: 条件がなければ元の候補一覧を返す,
//     2: 元の候補をファイルの場所で対応付ける,
//     3: 目的と変更対象と検証条件から必要な種類を選ぶ,
//     4: 元の候補に存在するものだけを並べ替えて返す
//   ],
//   引数: [
//     recommended: 利用できると判断された候補,
//     conditional: 条件付きで使える候補,
//     options: 今回の作業条件
//   ],
//   戻り値: [
//     1: 作業条件に合う候補,
//     2: 条件が指定された場合は空になる条件付き候補一覧,
//     3: 選択理由と見送った件数
//   ]
// }
func selectorApplyTaskContext(recommended, conditional []map[string]any, options selectorTaskOptions) ([]map[string]any, []map[string]any, map[string]any) {
    applied := strings.TrimSpace(options.Goal) != "" || options.TaskFile != "" || len(options.ChangedFiles) > 0 || options.ValidationIntent != "unknown"
    if !applied {
        // 条件がなければ選び直さず、元の候補一覧を保持する。
        return recommended, conditional, map[string]any{"applied": false}
    }

    // 元の候補一覧を変えないため、複製した一覧から候補を対応付ける。
    rows := map[string]map[string]any{}
    for _, row := range append(append([]map[string]any{}, recommended...), conditional...) {
        path, _ := row["tool_path"].(string)
        rows[path] = row
    }
    selectedPaths := map[string]bool{}
    reasons := []string{}
    if strings.TrimSpace(options.Goal) != "" {
        selectedPaths["common/small/text-search"] = true
        selectedPaths["common/small/path-find"] = true
        reasons = append(reasons, "goal_provided")
    }
    if options.TaskFile != "" {
        selectedPaths["common/medium/acceptance-extractor"] = true
        selectedPaths["common/small/doc-index"] = true
        selectedPaths["common/medium/exploration-stop-check"] = true
        reasons = append(reasons, "task_file_provided")
    }
    if len(options.ChangedFiles) > 0 {
        selectedPaths["common/medium/compact-diff"] = true
        selectedPaths["common/medium/change-router"] = true
        selectedPaths["common/large/source-structure-index"] = true
        selectedPaths["common/large/target-slice"] = true
        reasons = append(reasons, "changed_files_provided")
    }
    if options.ValidationIntent == "targeted" || options.ValidationIntent == "full" {
        selectedPaths["common/medium/validation-plan"] = true
        selectedPaths["common/small/syntax-health"] = true
        reasons = append(reasons, "validation_"+options.ValidationIntent)
    }

    // 作業条件で選んだ種類も、利用できる候補にあるものだけ返す。
    selected := []map[string]any{}
    for path := range selectedPaths {
        if row, ok := rows[path]; ok {
            copied := map[string]any{}
            for key, value := range row { copied[key] = value }
            copied["task_relevance"] = "direct"
            selected = append(selected, copied)
        }
    }
    selected = selectorDedupeSort(selected, "tool_path")
    uniqueTotal := map[string]bool{}
    for path := range rows { uniqueTotal[path] = true }
    deferred := len(uniqueTotal) - len(selected)
    if deferred < 0 { deferred = 0 }
    return selected, []map[string]any{}, map[string]any{
        "applied": true,
        "goal_present": strings.TrimSpace(options.Goal) != "",
        "task_file": options.TaskFile,
        "changed_files": options.ChangedFiles,
        "validation_intent": options.ValidationIntent,
        "routing_reasons": reasons,
        "deferred_tool_count": deferred,
    }
}
