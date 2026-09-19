package main

import (
    "encoding/json"
    "flag"
    "os"
    "path/filepath"
    "sort"
    "strings"
)

type languageSetupTool struct {
    ToolPath string `json:"tool_path"`
    Level string `json:"level"`
    Enabled bool `json:"enabled"`
    Reason string `json:"reason"`
}

// cmdLanguageSetup は対象サブコマンドの引数解析・境界I/O・compact出力を統括します。
func cmdLanguageSetup(args []string) int {
    fs := flag.NewFlagSet("language-setup", flag.ContinueOnError)
    runSmall := fs.Bool("run-small", false, "mark shallow language analyzers for immediate execution")
    if err := fs.Parse(args); err != nil { return 2 }
    root := "."
    if fs.NArg() > 0 { root = fs.Arg(0) }

    absRoot, _ := filepath.Abs(root)
    walked, err := walkWithOptions(absRoot, false)
    if err != nil {
        selectorWriteJSON(map[string]any{"tool":"language-setup","status":"scan_failed","project_root":absRoot,"error":selectorBoundedText(err.Error(),800)})
        return 1
    }

    counts := map[string]int{}
    for _, f := range walked.Files {
        ext := strings.ToLower(filepath.Ext(f.Path))
        if lang := selectorLanguages[ext]; lang != "" {
            counts[lang]++
        }
    }
    size := "small"
    if len(walked.Files) >= 2000 { size = "large" } else if len(walked.Files) >= 200 { size = "medium" }

    runtimeCmd := map[string]string{
        "python": firstAvailable("python3","python"),
        "csharp": firstAvailable("dotnet"),
        "go": firstAvailable("go"),
        "c": firstAvailable("gcc","clang","cc"),
        "cpp": firstAvailable("g++","clang++","c++"),
        "gdscript": firstAvailable("godot4","godot"),
    }

    toolNames := map[string][3]string{
        "python": {"python/small/python-symbols","python/medium/python-import-map","python/large/python-module-graph"},
        "csharp": {"csharp/small/csharp-symbols","csharp/medium/csharp-project-map","csharp/large/csharp-project-graph"},
        "go": {"go/small/go-symbols","go/medium/go-import-map","go/large/go-package-graph"},
        "c": {"c/small/c-symbols","c/medium/c-include-map","c/large/c-include-graph"},
        "cpp": {"cpp/small/cpp-symbols","cpp/medium/cpp-include-map","cpp/large/cpp-include-graph"},
        "gdscript": {"gdscript/small/gdscript-symbols","gdscript/medium/gdscript-dependency-map","gdscript/large/godot-scene-graph"},
    }

    langs := make([]string,0,len(counts))
    for lang := range counts { langs = append(langs, lang) }
    sort.Slice(langs, func(i,j int) bool {
        if counts[langs[i]] == counts[langs[j]] { return langs[i] < langs[j] }
        return counts[langs[i]] > counts[langs[j]]
    })

    enabled := []languageSetupTool{}
    skipped := []map[string]any{}
    for _, lang := range langs {
        names, supported := toolNames[lang]
        if !supported {
            skipped = append(skipped, map[string]any{"language":lang,"file_count":counts[lang],"reason":"no bundled language-specific tool group"})
            continue
        }
        cmd := runtimeCmd[lang]
        enabled = append(enabled, languageSetupTool{ToolPath:names[0],Level:"small",Enabled:true,Reason:"source detected; bundled acr-toolbox native shallow analyzer is available"})
        if size == "medium" || size == "large" {
            reason := "repository size may justify dependency/project mapping; bundled portable Medium fallback is available"
            if cmd != "" {
                reason += "; matching runtime/compiler is also available for higher-precision follow-up"
            }
            enabled = append(enabled, languageSetupTool{ToolPath:names[1],Level:"medium",Enabled:true,Reason:reason})
        }
        if size == "large" {
            if cmd != "" {
                enabled = append(enabled, languageSetupTool{ToolPath:names[2],Level:"large",Enabled:true,Reason:"large repository and matching runtime/compiler justify bounded graph analysis"})
            } else {
                skipped = append(skipped, map[string]any{"language":lang,"level":"large","tool_path":names[2],"reason":"matching runtime/compiler unavailable; dependencies are not auto-installed"})
            }
        }
    }

    run := []string{}
    if *runSmall {
        for _, t := range enabled {
            if t.Level == "small" { run = append(run, t.ToolPath) }
        }
    }

    out := map[string]any{
        "tool":"language-setup",
        "status":"ok",
        "project_root":absRoot,
        "project_size_class":size,
        "language_file_counts":counts,
        "runtime_commands":runtimeCmd,
        "enabled_tools":enabled,
        "skipped_languages":skipped,
        "run_small_requested":*runSmall,
        "small_tools_to_run":run,
        "policy":"Small and Medium routing analyzers have bundled native fallbacks; Large or higher-precision analysis may use suitable existing runtimes/compilers; never auto-install dependencies",
    }
    if walked.ErrorCount > 0 {
        out["status"]="ok_with_warnings"
        out["scan_error_count"]=walked.ErrorCount
    }
    enc:=json.NewEncoder(os.Stdout); enc.SetIndent("","  "); _=enc.Encode(out)
    return 0
}
