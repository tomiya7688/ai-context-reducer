package main

import (
    "encoding/json"
    "flag"
    "fmt"
    "os"
    "path/filepath"
    "strings"
)

type languageRunResult struct {
    ToolPath string `json:"tool_path"`
    Status string `json:"status"`
    Backend string `json:"backend,omitempty"`
    OutputPath string `json:"output_path,omitempty"`
    Error string `json:"error,omitempty"`
    ReadErrorCount int `json:"read_error_count,omitempty"`
    WalkErrorCount int `json:"walk_error_count,omitempty"`
}

// summarizeLanguageStatuses はanalyzerとrouting scanの警告を上位statusへ集約します。
func summarizeLanguageStatuses(statuses []string, scanWalkErrors int) (string, int, int, int) {
    failed, skipped, warnings := 0, 0, 0
    for _, status := range statuses {
        switch status {
        case "failed", "write_failed":
            failed++
        case "skipped":
            skipped++
        case "ok":
        default:
            warnings++
        }
    }
    resultStatus := "ok"
    if failed > 0 {
        resultStatus = "ok_with_failures"
    } else if warnings > 0 || scanWalkErrors > 0 {
        resultStatus = "ok_with_warnings"
    } else if skipped > 0 {
        resultStatus = "ok_with_skips"
    }
    return resultStatus, failed, skipped, warnings
}

// boundedErr はanalyzerの診断文をstdout JSONのサイズ上限内に収めます。
func boundedErr(data []byte) string {
    s := strings.TrimSpace(string(data))
    if len(s) > 1200 { return s[:1200] }
    return s
}

// writeCommandOutput は内部結果を安定した利用者向け出力へ変換します。
func writeCommandOutput(path string, stdout []byte) error {
    if err := os.MkdirAll(filepath.Dir(path), 0755); err != nil { return err }
    return os.WriteFile(path, stdout, 0644)
}

// runLanguageTool は対象処理を実行し、外部境界の失敗を呼び出し元へ明示します。
func runLanguageTool(toolPath, root, outDir string) languageRunResult {
    languages := map[string]string{
        "python/small/python-symbols":"python",
        "csharp/small/csharp-symbols":"csharp",
        "go/small/go-symbols":"go",
        "c/small/c-symbols":"c",
        "cpp/small/cpp-symbols":"cpp",
        "gdscript/small/gdscript-symbols":"gdscript",
    }
    language, ok := languages[toolPath]
    if !ok { return languageRunResult{ToolPath:toolPath,Status:"skipped",Error:"unsupported language tool"} }
    return writeNativeSymbols(root,language,toolPath,outDir)
}

// cmdLanguageRun は対象サブコマンドの引数解析・境界I/O・compact出力を統括します。
func cmdLanguageRun(args []string) int {
    fs:=flag.NewFlagSet("language-run",flag.ContinueOnError)
    out:=fs.String("out",".acr/language","directory for analyzer results")
    if err:=fs.Parse(args); err!=nil { return 2 }
    root:="."; if fs.NArg()>0 { root=fs.Arg(0) }
    absRoot,err:=filepath.Abs(root); if err!=nil { fmt.Fprintln(os.Stderr,err); return 2 }
    outDir:=*out
    if !filepath.IsAbs(outDir) { outDir=filepath.Join(absRoot,outDir) }

    rootInfo, statErr := os.Stat(absRoot)
    if statErr != nil {
        status := "input_read_failed"
        if os.IsNotExist(statErr) { status = "input_missing" }
        emitLanguageRunInputFailure(status, absRoot, outDir)
        return 2
    }
    if !rootInfo.IsDir() {
        emitLanguageRunInputFailure("input_not_directory", absRoot, outDir)
        return 2
    }

    walked,err:=walkWithOptions(absRoot,false)
    if err!=nil {
        selectorWriteJSON(map[string]any{"tool":"language-run","status":"scan_failed","error":selectorBoundedText(err.Error(),800)})
        return 1
    }
    detected:=map[string]bool{}
    for _,f:=range walked.Files {
        if lang:=selectorLanguages[strings.ToLower(filepath.Ext(f.Path))]; lang!="" { detected[lang]=true }
    }

    order:=[]string{"python","csharp","go","c","cpp","gdscript"}
    small:=map[string]string{
        "python":"python/small/python-symbols","csharp":"csharp/small/csharp-symbols","go":"go/small/go-symbols",
        "c":"c/small/c-symbols","cpp":"cpp/small/cpp-symbols","gdscript":"gdscript/small/gdscript-symbols",
    }
    results:=[]languageRunResult{}
    for _,lang:=range order {
        if detected[lang] { results=append(results,runLanguageTool(small[lang],absRoot,outDir)) }
    }
    statuses:=make([]string,0,len(results))
    for _,r:=range results { statuses=append(statuses,r.Status) }
    status,failed,skipped,warnings:=summarizeLanguageStatuses(statuses,walked.WalkErrorCount)
    enc:=json.NewEncoder(os.Stdout); enc.SetIndent("","  "); _=enc.Encode(map[string]any{
        "tool":"language-run","status":status,"project_root":absRoot,"output_directory":outDir,
        "results":results,"failure_count":failed,"skip_count":skipped,"warning_count":warnings+walked.WalkErrorCount,"walk_error_count":walked.WalkErrorCount,
        "backend_policy":"all bundled Small symbol analyzers use acr-toolbox native fallback; language SDKs are not required",
        "note":"full analyzer outputs are written to files; stdout stays compact",
    })
    if failed>0 { return 1 }
    return 0
}

// emitLanguageRunInputFailure は未取得rootを空の成功scanと混同させないJSONを返す。
func emitLanguageRunInputFailure(status, root, outDir string) {
    selectorWriteJSON(map[string]any{
        "tool":"language-run","status":status,"project_root":root,"output_directory":outDir,
        "results":[]languageRunResult{},"failure_count":1,"skip_count":0,
    })
}
