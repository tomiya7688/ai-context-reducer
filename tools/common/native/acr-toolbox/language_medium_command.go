package main

import (
    "bufio"
    "encoding/json"
    "flag"
    "os"
    "path/filepath"
    "regexp"
    "sort"
    "strings"
)

type dependencyFile struct {
    File string `json:"file"`
    Status string `json:"status"`
    Dependencies []string `json:"dependencies"`
    Error string `json:"error,omitempty"`
}
type dependencyResult struct {
    Tool string `json:"tool"`
    Status string `json:"status"`
    Language string `json:"language"`
    RootPath string `json:"root_path"`
    Files []dependencyFile `json:"files"`
    FileCountTotal int `json:"file_count_total"`
    DependencyCount int `json:"dependency_count"`
    ReadErrorCount int `json:"read_error_count"`
    Approximate bool `json:"approximate"`
}

var pyImport = regexp.MustCompile(`^\s*import\s+([A-Za-z0-9_\.]+)`)
var pyFrom = regexp.MustCompile(`^\s*from\s+([A-Za-z0-9_\.]+)\s+import\s+`)
var goImportSingle = regexp.MustCompile(`^\s*import\s+(?:[A-Za-z_][A-Za-z0-9_]*\s+)?["\x60]([^"\x60]+)["\x60]`)
var goImportBlock = regexp.MustCompile(`^\s*(?:[A-Za-z_][A-Za-z0-9_]*\s+)?["\x60]([^"\x60]+)["\x60]`)
var includeLine = regexp.MustCompile(`^\s*#\s*include\s*[<"]([^>"]+)[>"]`)
var gdLoad = regexp.MustCompile(`(?:load|preload)\(\s*["']([^"']+)["']\s*\)`)
var gdExtends = regexp.MustCompile(`^\s*extends\s+["']([^"']+)["']`)
var csProjectRef = regexp.MustCompile(`<ProjectReference\s+Include=["']([^"']+)["']`)

func mediumExtensions(language string) map[string]bool {
    switch language {
    case "python": return map[string]bool{".py":true}
    case "go": return map[string]bool{".go":true}
    case "c": return map[string]bool{".c":true,".h":true}
    case "cpp": return map[string]bool{".cpp":true,".cc":true,".cxx":true,".hpp":true,".hh":true,".hxx":true,".h":true}
    case "gdscript": return map[string]bool{".gd":true}
    }
    return map[string]bool{}
}

func collectDependencyFiles(root, language string) ([]string,error) {
    files:=[]string{}
    if language=="csharp" {
        err:=filepath.WalkDir(root,func(path string,d os.DirEntry,err error) error{
            if err!=nil{return nil}
            if d.IsDir(){if path!=root&&ignoreDirs[strings.ToLower(d.Name())]{return filepath.SkipDir};return nil}
            if strings.EqualFold(filepath.Ext(path),".csproj"){files=append(files,path)}
            return nil
        })
        sort.Strings(files); return files,err
    }
    exts:=mediumExtensions(language)
    err:=filepath.WalkDir(root,func(path string,d os.DirEntry,err error) error{
        if err!=nil{return nil}
        if d.IsDir(){if path!=root&&ignoreDirs[strings.ToLower(d.Name())]{return filepath.SkipDir};return nil}
        if exts[strings.ToLower(filepath.Ext(path))]{files=append(files,path)}
        return nil
    })
    sort.Strings(files); return files,err
}

func uniqueSorted(values []string) []string {
    seen:=map[string]bool{}
    out:=[]string{}
    for _,v:=range values{if v!=""&&!seen[v]{seen[v]=true;out=append(out,v)}}
    sort.Strings(out); return out
}

func scanDependencyFile(path, language string) dependencyFile {
    if language=="csharp" {
        data,err:=os.ReadFile(path)
        if err!=nil{return dependencyFile{File:filepath.ToSlash(path),Status:"read_failed",Dependencies:[]string{},Error:err.Error()}}
        deps:=[]string{}
        for _,m:=range csProjectRef.FindAllStringSubmatch(string(data),-1){if len(m)>1{deps=append(deps,filepath.ToSlash(m[1]))}}
        return dependencyFile{File:filepath.ToSlash(path),Status:"ok",Dependencies:uniqueSorted(deps)}
    }
    h,err:=os.Open(path)
    if err!=nil{return dependencyFile{File:filepath.ToSlash(path),Status:"read_failed",Dependencies:[]string{},Error:err.Error()}}
    defer h.Close()
    deps:=[]string{}
    s:=bufio.NewScanner(h); buf:=make([]byte,64*1024); s.Buffer(buf,2*1024*1024)
    inGoImport:=false
    for s.Scan(){
        line:=s.Text()
        switch language{
        case "python":
            if m:=pyImport.FindStringSubmatch(line);len(m)>1{deps=append(deps,m[1])}
            if m:=pyFrom.FindStringSubmatch(line);len(m)>1{deps=append(deps,m[1])}
        case "go":
            trimmed:=strings.TrimSpace(line)
            if strings.HasPrefix(trimmed,"import ("){inGoImport=true;continue}
            if inGoImport&&trimmed==")"{inGoImport=false;continue}
            if inGoImport{if m:=goImportBlock.FindStringSubmatch(line);len(m)>1{deps=append(deps,m[1])}}
            if m:=goImportSingle.FindStringSubmatch(line);len(m)>1{deps=append(deps,m[1])}
        case "c","cpp":
            if m:=includeLine.FindStringSubmatch(line);len(m)>1{deps=append(deps,m[1])}
        case "gdscript":
            for _,m:=range gdLoad.FindAllStringSubmatch(line,-1){if len(m)>1{deps=append(deps,m[1])}}
            if m:=gdExtends.FindStringSubmatch(line);len(m)>1{deps=append(deps,m[1])}
        }
    }
    if err:=s.Err();err!=nil{return dependencyFile{File:filepath.ToSlash(path),Status:"read_failed",Dependencies:uniqueSorted(deps),Error:err.Error()}}
    return dependencyFile{File:filepath.ToSlash(path),Status:"ok",Dependencies:uniqueSorted(deps)}
}

func buildDependencyResult(root,language,tool string)(dependencyResult,error){
    files,err:=collectDependencyFiles(root,language)
    if err!=nil{return dependencyResult{},err}
    out:=dependencyResult{Tool:tool,Status:"ok",Language:language,RootPath:filepath.ToSlash(root),Files:[]dependencyFile{},Approximate:true}
    for _,p:=range files{
        row:=scanDependencyFile(p,language)
        if rel,e:=filepath.Rel(root,p);e==nil{row.File=filepath.ToSlash(rel)}
        out.Files=append(out.Files,row);out.DependencyCount+=len(row.Dependencies)
        if row.Status=="read_failed"{out.ReadErrorCount++}
    }
    out.FileCountTotal=len(files)
    if out.ReadErrorCount>0{out.Status="ok_with_warnings"}
    return out,nil
}

func cmdLanguageMediumRun(args []string) int {
    fs:=flag.NewFlagSet("language-medium-run",flag.ContinueOnError)
    outDirArg:=fs.String("out",".acr/language-medium","directory for dependency/project maps")
    if err:=fs.Parse(args);err!=nil{return 2}
    root:=".";if fs.NArg()>0{root=fs.Arg(0)}
    absRoot,err:=filepath.Abs(root);if err!=nil{return 2}
    walked,err:=walkWithOptions(absRoot,false)
    if err!=nil{selectorWriteJSON(map[string]any{"tool":"language-medium-run","status":"scan_failed","error":selectorBoundedText(err.Error(),800)});return 1}
    detected:=map[string]bool{}
    for _,f:=range walked.Files{if lang:=selectorLanguages[strings.ToLower(filepath.Ext(f.Path))];lang!=""{detected[lang]=true}}
    outDir:=*outDirArg;if !filepath.IsAbs(outDir){outDir=filepath.Join(absRoot,outDir)}
    toolsByLang:=map[string]string{
        "python":"python/medium/python-import-map","csharp":"csharp/medium/csharp-project-map","go":"go/medium/go-import-map",
        "c":"c/medium/c-include-map","cpp":"cpp/medium/cpp-include-map","gdscript":"gdscript/medium/gdscript-dependency-map",
    }
    runtimeCmd:=map[string]string{
        "python":firstAvailable("python3","python"),"csharp":firstAvailable("dotnet"),"go":firstAvailable("go"),
        "c":firstAvailable("gcc","clang","cc"),"cpp":firstAvailable("g++","clang++","c++"),"gdscript":firstAvailable("godot4","godot"),
    }
    order:=[]string{"python","csharp","go","c","cpp","gdscript"}
    results:=[]map[string]any{}; failures:=0
    for _,lang:=range order{
        if !detected[lang]{continue}
        tool:=toolsByLang[lang]
        payload,e:=buildDependencyResult(absRoot,lang,filepath.Base(tool))
        if e!=nil{results=append(results,map[string]any{"tool_path":tool,"status":"failed","error":boundedErr([]byte(e.Error()))});failures++;continue}
        data,e:=json.MarshalIndent(payload,"","  ")
        if e!=nil{results=append(results,map[string]any{"tool_path":tool,"status":"failed","error":e.Error()});failures++;continue}
        name:=strings.ReplaceAll(strings.ReplaceAll(tool,"/","_"),"-","_")+".json"
        output:=filepath.Join(outDir,name)
        if e:=writeCommandOutput(output,append(data,'\n'));e!=nil{results=append(results,map[string]any{"tool_path":tool,"status":"write_failed","error":e.Error()});failures++;continue}
        backend:="acr-toolbox-native-fallback"
        if runtimeCmd[lang]!=""{backend="acr-toolbox-native-fallback; standard_runtime_available"}
        results=append(results,map[string]any{"tool_path":tool,"status":"ok","backend":backend,"runtime_command":runtimeCmd[lang],"output_path":output,"approximate":true})
    }
    status:="ok";if failures>0{status="ok_with_failures"}
    selectorWriteJSON(map[string]any{"tool":"language-medium-run","status":status,"project_root":absRoot,"output_directory":outDir,"results":results,"failure_count":failures,"note":"portable dependency/project maps are approximate; use standard SDK/compiler backends when task precision requires them"})
    if failures>0{return 1};return 0
}
