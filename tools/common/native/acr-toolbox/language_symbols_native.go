package main

import (
    "bufio"
    "encoding/json"
    "io/fs"
    "os"
    "path/filepath"
    "regexp"
    "sort"
    "strings"
)

type nativeSymbol struct {
    Kind string `json:"kind"`
    Name string `json:"name"`
    Line int `json:"line"`
}
type nativeSymbolFile struct {
    File string `json:"file"`
    Status string `json:"status"`
    Symbols []nativeSymbol `json:"symbols"`
    Error string `json:"error,omitempty"`
}
type nativeSymbolResult struct {
    Tool string `json:"tool"`
    Status string `json:"status"`
    Language string `json:"language"`
    Files []nativeSymbolFile `json:"files"`
    FileCount int `json:"file_count"`
    SymbolCount int `json:"symbol_count"`
    ParseErrorCount int `json:"parse_error_count"`
    ReadErrorCount int `json:"read_error_count"`
    WalkErrorCount int `json:"walk_error_count"`
    WalkErrorPaths []string `json:"walk_error_paths,omitempty"`
    UnsupportedInputCount int `json:"unsupported_input_count"`
    UnsupportedInputs []map[string]string `json:"unsupported_inputs"`
    Approximate bool `json:"approximate"`
}

type symbolPattern struct {
    Kind string
    RX *regexp.Regexp
}

var nativeSymbolExtensions = map[string]map[string]bool{
    "python": {".py":true},
    "csharp": {".cs":true},
    "go": {".go":true},
    "c": {".c":true, ".h":true},
    "cpp": {".cpp":true, ".cc":true, ".cxx":true, ".hpp":true, ".hh":true, ".hxx":true, ".h":true},
    "gdscript": {".gd":true},
}

var nativePatterns = map[string][]symbolPattern{
    "python": {
        {"class", regexp.MustCompile(`^\s*class\s+([A-Za-z_]\w*)`)},
        {"async_func", regexp.MustCompile(`^\s*async\s+def\s+([A-Za-z_]\w*)\s*\(`)},
        {"func", regexp.MustCompile(`^\s*def\s+([A-Za-z_]\w*)\s*\(`)},
    },
    "csharp": {
        {"namespace", regexp.MustCompile(`^\s*namespace\s+([A-Za-z_][\w\.]*)`)},
        {"class", regexp.MustCompile(`^\s*(?:public|private|internal|protected|static|sealed|abstract|partial|\s)*\s*class\s+([A-Za-z_]\w*)`)},
        {"interface", regexp.MustCompile(`^\s*(?:public|private|internal|protected|partial|\s)*\s*interface\s+([A-Za-z_]\w*)`)},
        {"method", regexp.MustCompile(`^\s*(?:public|private|internal|protected|static|virtual|override|async|sealed|partial|extern|new|\s)+[\w<>,\[\]\.?]+\s+([A-Za-z_]\w*)\s*\(`)},
    },
    "go": {
        {"type", regexp.MustCompile(`^\s*type\s+([A-Za-z_]\w*)\s+`)},
        {"func", regexp.MustCompile(`^\s*func\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)\s*\(`)},
    },
    "c": {
        {"type", regexp.MustCompile(`^\s*(?:typedef\s+)?(?:struct|enum|union)\s+([A-Za-z_]\w*)`)},
        {"func", regexp.MustCompile(`^\s*(?:[A-Za-z_]\w*[\s\*]+)+([A-Za-z_]\w*)\s*\([^;]*\)\s*\{?\s*$`)},
    },
    "cpp": {
        {"namespace", regexp.MustCompile(`^\s*namespace\s+([A-Za-z_]\w*)`)},
        {"class", regexp.MustCompile(`^\s*(?:class|struct)\s+([A-Za-z_]\w*)`)},
        {"func", regexp.MustCompile(`^\s*(?:template\s*<[^>]+>\s*)?(?:[\w:<>,~*&\[\]\s]+)\s+([A-Za-z_~]\w*)\s*\([^;]*\)\s*(?:const\s*)?(?:\{|$)`)},
    },
    "gdscript": {
        {"class_name", regexp.MustCompile(`^\s*class_name\s+([A-Za-z_]\w*)`)},
        {"class", regexp.MustCompile(`^\s*class\s+([A-Za-z_]\w*)`)},
        {"func", regexp.MustCompile(`^\s*func\s+([A-Za-z_]\w*)\s*\(`)},
        {"signal", regexp.MustCompile(`^\s*signal\s+([A-Za-z_]\w*)`)},
        {"var", regexp.MustCompile(`^\s*(?:@\w+(?:\([^)]*\))?\s*)*(?:var|const)\s+([A-Za-z_]\w*)`)},
    },
}

// collectNativeLanguageFilesWithWalker はfile候補とnested walk failureを別々に収集します。
func collectNativeLanguageFilesWithWalker(root, language string, walk func(string, fs.WalkDirFunc) error) ([]string, []string, error) {
    exts := nativeSymbolExtensions[language]
    files := []string{}
    walkErrorPaths := []string{}
    err := walk(root, func(path string, d os.DirEntry, err error) error {
        if err != nil {
            if path == root { return err }
            relative, relErr := filepath.Rel(root, path)
            if relErr != nil { relative = path }
            walkErrorPaths = append(walkErrorPaths, filepath.ToSlash(relative))
            return nil
        }
        if d.IsDir() {
            if path != root && ignoreDirs[strings.ToLower(d.Name())] { return filepath.SkipDir }
            return nil
        }
        if exts[strings.ToLower(filepath.Ext(path))] { files = append(files,path) }
        return nil
    })
    sort.Strings(files)
    sort.Strings(walkErrorPaths)
    return files, walkErrorPaths, err
}

// scanNativeSymbols は各source fileのsymbolを抽出し、warningと未完了状態を集約します。
func scanNativeSymbols(path, language string) nativeSymbolFile {
    h, err := os.Open(path)
    if err != nil { return nativeSymbolFile{File:filepath.ToSlash(path),Status:"read_failed",Symbols:[]nativeSymbol{},Error:err.Error()} }
    defer h.Close()
    rows:=[]nativeSymbol{}
    s:=bufio.NewScanner(h)
    buf:=make([]byte,64*1024); s.Buffer(buf,2*1024*1024)
    line:=0
    for s.Scan() {
        line++
        text:=s.Text()
        for _,p:=range nativePatterns[language] {
            if m:=p.RX.FindStringSubmatch(text); len(m)>1 {
                if language=="c" && (m[1]=="if"||m[1]=="for"||m[1]=="while"||m[1]=="switch") { continue }
                rows=append(rows,nativeSymbol{Kind:p.Kind,Name:m[1],Line:line})
                break
            }
        }
    }
    if err:=s.Err(); err!=nil { return nativeSymbolFile{File:filepath.ToSlash(path),Status:"read_failed",Symbols:rows,Error:err.Error()} }
    return nativeSymbolFile{File:filepath.ToSlash(path),Status:"ok",Symbols:rows}
}

// buildNativeSymbolResult は解析結果を後段で再利用できる構造へ組み立てます。
func buildNativeSymbolResult(root, language, tool string) (nativeSymbolResult,error) {
    return buildNativeSymbolResultWithWalker(root, language, tool, filepath.WalkDir)
}

// buildNativeSymbolResultWithWalker は注入された走査結果からanalyzer completenessを組み立てます。
func buildNativeSymbolResultWithWalker(root, language, tool string, walk func(string, fs.WalkDirFunc) error) (nativeSymbolResult,error) {
    files,walkErrorPaths,err:=collectNativeLanguageFilesWithWalker(root,language,walk)
    if err!=nil { return nativeSymbolResult{},err }
    out:=nativeSymbolResult{
        Tool:tool,Status:"ok",Language:language,Files:[]nativeSymbolFile{},
        UnsupportedInputs:[]map[string]string{},Approximate:true,
        WalkErrorCount:len(walkErrorPaths),WalkErrorPaths:walkErrorPaths,
    }
    for _,p:=range files {
        row:=scanNativeSymbols(p,language)
        out.Files=append(out.Files,row)
        out.SymbolCount+=len(row.Symbols)
        if row.Status=="read_failed" { out.ReadErrorCount++ }
    }
    out.FileCount=len(out.Files)
    if out.ReadErrorCount>0 || out.WalkErrorCount>0 { out.Status="ok_with_warnings" }
    return out,nil
}

// writeNativeSymbols は内部結果を安定した利用者向け出力へ変換します。
func writeNativeSymbols(root, language, tool, outDir string) languageRunResult {
    return writeNativeSymbolsWithWalker(root, language, tool, outDir, filepath.WalkDir)
}

// writeNativeSymbolsWithWalker はanalyzer payloadと同じstatusをlanguage-run rowへ伝えます。
func writeNativeSymbolsWithWalker(root, language, tool, outDir string, walk func(string, fs.WalkDirFunc) error) languageRunResult {
    r:=languageRunResult{ToolPath:tool,Backend:"acr-toolbox-native-symbols"}
    payload,err:=buildNativeSymbolResultWithWalker(root,language,filepath.Base(tool),walk)
    if err!=nil { r.Status="failed"; r.Error=boundedErr([]byte(err.Error())); return r }
    data,err:=json.MarshalIndent(payload,"","  ")
    if err!=nil { r.Status="failed"; r.Error=err.Error(); return r }
    name:=strings.ReplaceAll(strings.ReplaceAll(tool,"/","_"),"-","_")+".json"
    output:=filepath.Join(outDir,name)
    if err:=writeCommandOutput(output,append(data,'\n')); err!=nil { r.Status="write_failed"; r.Error=err.Error(); return r }
    r.Status=payload.Status; r.ReadErrorCount=payload.ReadErrorCount; r.WalkErrorCount=payload.WalkErrorCount; r.OutputPath=output
    return r
}
