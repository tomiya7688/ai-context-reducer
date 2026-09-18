package main

import (
    "bytes"
    "encoding/json"
    "flag"
    "fmt"
    "os"
    "os/exec"
    "path/filepath"
    "runtime"
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

func findToolsRoot(explicit string) string {
    if explicit != "" { if p, err := filepath.Abs(explicit); err == nil { return p } }
    if wd, err := os.Getwd(); err == nil {
        candidates := []string{wd, filepath.Dir(wd)}
        for _, c := range candidates {
            if _, err := os.Stat(filepath.Join(c, "tools")); err == nil { return c }
            if filepath.Base(c) == "tools" { return filepath.Dir(c) }
        }
    }
    return ""
}

func writeCommandOutput(path string, stdout []byte) error {
    if err := os.MkdirAll(filepath.Dir(path), 0755); err != nil { return err }
    return os.WriteFile(path, stdout, 0644)
}

func runLanguageTool(toolPath, root, acrRoot, outDir string) languageRunResult {
    result := languageRunResult{ToolPath: toolPath}
    var cmd *exec.Cmd
    var backend string

    python := firstAvailable("python3", "python")
    switch toolPath {
    case "python/small/python-symbols":
        script := filepath.Join(acrRoot, "tools", "python", "small", "python-symbols", "script", "python_symbols.py")
        if python == "" { result.Status="skipped"; result.Error="python runtime unavailable"; return result }
        if _, err := os.Stat(script); err != nil { result.Status="skipped"; result.Error="python-symbols script unavailable in this installation"; return result }
        cmd=exec.Command(python, script, root); backend="python-stdlib-ast"
    case "csharp/small/csharp-symbols":
        script := filepath.Join(acrRoot, "tools", "csharp", "small", "csharp-symbols", "script", "csharp_symbols.py")
        if python == "" { result.Status="skipped"; result.Error="python fallback unavailable for current csharp-symbols implementation"; return result }
        if _, err := os.Stat(script); err != nil { result.Status="skipped"; result.Error="csharp-symbols script unavailable in this installation"; return result }
        cmd=exec.Command(python, script, root); backend="python-portable"
    case "c/small/c-symbols":
        script := filepath.Join(acrRoot, "tools", "c", "small", "c-symbols", "script", "c_symbols.py")
        if python == "" { result.Status="skipped"; result.Error="python fallback unavailable for current c-symbols implementation"; return result }
        if _, err := os.Stat(script); err != nil { result.Status="skipped"; result.Error="c-symbols script unavailable in this installation"; return result }
        cmd=exec.Command(python, script, root); backend="python-portable"
    case "cpp/small/cpp-symbols":
        script := filepath.Join(acrRoot, "tools", "cpp", "small", "cpp-symbols", "script", "cpp_symbols.py")
        if python == "" { result.Status="skipped"; result.Error="python fallback unavailable for current cpp-symbols implementation"; return result }
        if _, err := os.Stat(script); err != nil { result.Status="skipped"; result.Error="cpp-symbols script unavailable in this installation"; return result }
        cmd=exec.Command(python, script, root); backend="python-portable"
    case "gdscript/small/gdscript-symbols":
        script := filepath.Join(acrRoot, "tools", "gdscript", "small", "gdscript-symbols", "script", "gdscript_symbols.py")
        if python == "" { result.Status="skipped"; result.Error="python fallback unavailable for current gdscript-symbols implementation"; return result }
        if _, err := os.Stat(script); err != nil { result.Status="skipped"; result.Error="gdscript-symbols script unavailable in this installation"; return result }
        cmd=exec.Command(python, script, root); backend="python-portable"
    case "go/small/go-symbols":
        exe := "go-symbols"
        if runtime.GOOS=="windows" { exe += ".exe" }
        candidates := []string{
            filepath.Join(filepath.Dir(os.Args[0]), exe),
            filepath.Join(acrRoot, "tools", "bin", exe),
        }
        native := ""
        for _, p := range candidates { if _, err := os.Stat(p); err == nil { native=p; break } }
        if native != "" {
            cmd=exec.Command(native, root); backend="standalone-go-binary"
        } else if goCmd:=firstAvailable("go"); goCmd!="" {
            source:=filepath.Join(acrRoot,"tools","go","small","go-symbols")
            if _, err:=os.Stat(filepath.Join(source,"go.mod")); err!=nil { result.Status="skipped"; result.Error="go-symbols binary/source unavailable"; return result }
            cmd=exec.Command(goCmd,"run",".",root); cmd.Dir=source; backend="go-run"
        } else { result.Status="skipped"; result.Error="go-symbols binary and Go runtime unavailable"; return result }
    default:
        result.Status="skipped"; result.Error="unsupported language tool"; return result
    }

    var stdout, stderr bytes.Buffer
    cmd.Stdout=&stdout; cmd.Stderr=&stderr
    if err:=cmd.Run(); err!=nil {
        result.Status="failed"; result.Backend=backend
        result.Error=boundedErr(append(stderr.Bytes(), []byte("\n"+err.Error())...))
        return result
    }
    name:=strings.ReplaceAll(strings.ReplaceAll(toolPath,"/","_"),"-","_")+".json"
    output:=filepath.Join(outDir,name)
    if err:=writeCommandOutput(output,stdout.Bytes()); err!=nil {
        result.Status="write_failed"; result.Backend=backend; result.Error=err.Error(); return result
    }
    result.Status="ok"; result.Backend=backend; result.OutputPath=output
    return result
}

func cmdLanguageRun(args []string) int {
    fs:=flag.NewFlagSet("language-run",flag.ContinueOnError)
    acrRoot:=fs.String("acr-root","","ai-context-reducer source root; auto-detect when omitted")
    out:=fs.String("out",".acr/language","directory for analyzer results")
    if err:=fs.Parse(args); err!=nil { return 2 }
    root:="."; if fs.NArg()>0 { root=fs.Arg(0) }
    absRoot,err:=filepath.Abs(root); if err!=nil { fmt.Fprintln(os.Stderr,err); return 2 }
    ar:=findToolsRoot(*acrRoot)
    if ar=="" {
        selectorWriteJSON(map[string]any{"tool":"language-run","status":"tools_root_unavailable","project_root":absRoot})
        return 2
    }
    outDir:=*out
    if !filepath.IsAbs(outDir) { outDir=filepath.Join(absRoot,outDir) }

    walked,err:=walkWithOptions(absRoot,false)
    if err!=nil { selectorWriteJSON(map[string]any{"tool":"language-run","status":"scan_failed","error":selectorBoundedText(err.Error(),800)}); return 1 }
    detected:=map[string]bool{}
    for _,f:=range walked.Files { if lang:=selectorLanguages[strings.ToLower(filepath.Ext(f.Path))]; lang!="" { detected[lang]=true } }

    order:=[]string{"python","csharp","go","c","cpp","gdscript"}
    small:=map[string]string{
        "python":"python/small/python-symbols","csharp":"csharp/small/csharp-symbols","go":"go/small/go-symbols",
        "c":"c/small/c-symbols","cpp":"cpp/small/cpp-symbols","gdscript":"gdscript/small/gdscript-symbols",
    }
    results:=[]languageRunResult{}
    for _,lang:=range order { if detected[lang] { results=append(results,runLanguageTool(small[lang],absRoot,ar,outDir)) } }
    status:="ok"; failed:=0; skipped:=0
    for _,r:=range results { if r.Status=="failed"||r.Status=="write_failed" { failed++ }; if r.Status=="skipped" { skipped++ } }
    if failed>0 { status="ok_with_failures" } else if skipped>0 { status="ok_with_skips" }
    enc:=json.NewEncoder(os.Stdout); enc.SetIndent("","  "); _=enc.Encode(map[string]any{
        "tool":"language-run","status":status,"project_root":absRoot,"output_directory":outDir,
        "results":results,"failure_count":failed,"skip_count":skipped,
        "note":"full analyzer outputs are written to files; stdout stays compact",
    })
    if failed>0 { return 1 }
    return 0
}
