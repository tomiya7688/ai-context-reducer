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
}

func boundedErr(data []byte) string {
    s := strings.TrimSpace(string(data))
    if len(s) > 1200 { return s[:1200] }
    return s
}

func writeCommandOutput(path string, stdout []byte) error {
    if err := os.MkdirAll(filepath.Dir(path), 0755); err != nil { return err }
    return os.WriteFile(path, stdout, 0644)
}

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

func cmdLanguageRun(args []string) int {
    fs:=flag.NewFlagSet("language-run",flag.ContinueOnError)
    out:=fs.String("out",".acr/language","directory for analyzer results")
    if err:=fs.Parse(args); err!=nil { return 2 }
    root:="."; if fs.NArg()>0 { root=fs.Arg(0) }
    absRoot,err:=filepath.Abs(root); if err!=nil { fmt.Fprintln(os.Stderr,err); return 2 }
    outDir:=*out
    if !filepath.IsAbs(outDir) { outDir=filepath.Join(absRoot,outDir) }

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
    status:="ok"; failed:=0; skipped:=0
    for _,r:=range results {
        if r.Status=="failed"||r.Status=="write_failed" { failed++ }
        if r.Status=="skipped" { skipped++ }
    }
    if failed>0 { status="ok_with_failures" } else if skipped>0 { status="ok_with_skips" }
    enc:=json.NewEncoder(os.Stdout); enc.SetIndent("","  "); _=enc.Encode(map[string]any{
        "tool":"language-run","status":status,"project_root":absRoot,"output_directory":outDir,
        "results":results,"failure_count":failed,"skip_count":skipped,
        "backend_policy":"all bundled Small symbol analyzers use acr-toolbox native fallback; language SDKs are not required",
        "note":"full analyzer outputs are written to files; stdout stays compact",
    })
    if failed>0 { return 1 }
    return 0
}
