package main

import (
    "bufio"
    "encoding/json"
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

// collectNativeLanguageFiles は対象scopeを走査し、agentへ渡す候補情報を収集します。
func collectNativeLanguageFiles(root, language string) ([]string, error) {
    exts := nativeSymbolExtensions[language]
    files := []string{}
    err := filepath.WalkDir(root, func(path string, d os.DirEntry, err error) error {
        if err != nil { return nil }
        if d.IsDir() {
            if path != root && ignoreDirs[strings.ToLower(d.Name())] { return filepath.SkipDir }
            return nil
        }
        if exts[strings.ToLower(filepath.Ext(path))] { files = append(files,path) }
        return nil
    })
    sort.Strings(files)
    return files, err
}

// scanNativeSymbols は対象scopeを走査し、agentへ渡す候補情報を収集します。
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
    files,err:=collectNativeLanguageFiles(root,language)
    if err!=nil { return nativeSymbolResult{},err }
    out:=nativeSymbolResult{
        Tool:tool,Status:"ok",Language:language,Files:[]nativeSymbolFile{},
        UnsupportedInputs:[]map[string]string{},Approximate:true,
    }
    for _,p:=range files {
        row:=scanNativeSymbols(p,language)
        out.Files=append(out.Files,row)
        out.SymbolCount+=len(row.Symbols)
        if row.Status=="read_failed" { out.ReadErrorCount++ }
    }
    out.FileCount=len(out.Files)
    if out.ReadErrorCount>0 { out.Status="ok_with_warnings" }
    return out,nil
}

// writeNativeSymbols は内部結果を安定した利用者向け出力へ変換します。
func writeNativeSymbols(root, language, tool, outDir string) languageRunResult {
    r:=languageRunResult{ToolPath:tool,Backend:"acr-toolbox-native-symbols"}
    payload,err:=buildNativeSymbolResult(root,language,filepath.Base(tool))
    if err!=nil { r.Status="failed"; r.Error=boundedErr([]byte(err.Error())); return r }
    data,err:=json.MarshalIndent(payload,"","  ")
    if err!=nil { r.Status="failed"; r.Error=err.Error(); return r }
    name:=strings.ReplaceAll(strings.ReplaceAll(tool,"/","_"),"-","_")+".json"
    output:=filepath.Join(outDir,name)
    if err:=writeCommandOutput(output,append(data,'\n')); err!=nil { r.Status="write_failed"; r.Error=err.Error(); return r }
    r.Status="ok"; r.OutputPath=output
    return r
}
