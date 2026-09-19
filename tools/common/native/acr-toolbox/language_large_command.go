package main

import (
    "flag"
    "os"
    "path/filepath"
    "sort"
    "strings"
)

type largeBackendPlan struct {
    Language string `json:"language"`
    Available bool `json:"available"`
    Backend string `json:"backend,omitempty"`
    Command []string `json:"command,omitempty"`
    RunSupported bool `json:"run_supported"`
    Execution string `json:"execution"`
    Reason string `json:"reason"`
}

// largeBackendRunSupported はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func largeBackendRunSupported(backend string) bool {
    return backend == "existing-scip-index" || backend == "universal-ctags"
}

// finalizeLargePlan はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func finalizeLargePlan(plan largeBackendPlan) largeBackendPlan {
    plan.RunSupported = largeBackendRunSupported(plan.Backend)
    if plan.RunSupported {
        plan.Execution = "language-large-run"
    } else if plan.Available {
        plan.Execution = "planning_only"
    } else {
        plan.Execution = "unavailable"
    }
    return plan
}

// cmdLanguageLargePlan は対象サブコマンドの引数解析・境界I/O・compact出力を統括します。
func cmdLanguageLargePlan(args []string) int {
    fs:=flag.NewFlagSet("language-large-plan",flag.ContinueOnError)
    if err:=fs.Parse(args);err!=nil{return 2}
    root:=".";if fs.NArg()>0{root=fs.Arg(0)}
    absRoot,err:=filepath.Abs(root)
    if err!=nil{return 2}
    walked,err:=walkWithOptions(absRoot,false)
    if err!=nil{
        selectorWriteJSON(map[string]any{"tool":"language-large-plan","status":"scan_failed","project_root":absRoot,"error":selectorBoundedText(err.Error(),800)})
        return 1
    }
    detected:=map[string]bool{}
    for _,f:=range walked.Files{
        if lang:=selectorLanguages[strings.ToLower(filepath.Ext(f.Path))];lang!=""{detected[lang]=true}
    }
    langs:=[]string{}
    for lang:=range detected{langs=append(langs,lang)}
    sort.Strings(langs)

    ctags:=firstAvailable("ctags")
    scip:=firstAvailable("scip")
    dotnet:=firstAvailable("dotnet")
    goCmd:=firstAvailable("go")
    cc:=firstAvailable("clang","gcc","cc")
    cpp:=firstAvailable("clang++","g++","c++")
    godot:=firstAvailable("godot4","godot")

    plans:=[]largeBackendPlan{}
    for _,lang:=range langs{
        plan:=largeBackendPlan{Language:lang,Available:false,Reason:"no high-precision backend detected; keep portable Medium result and avoid heavy Large analysis"}
        switch {
        case scip!="" && fileExists(filepath.Join(absRoot,"index.scip")):
            plan.Available=true
            plan.Backend="existing-scip-index"
            plan.Command=[]string{"acr-toolbox","structure-index","build","--scip",filepath.Join(absRoot,"index.scip"),"--output",filepath.Join(absRoot,".acr","source-structure-index.json")}
            plan.Reason="existing SCIP index and scip CLI detected; reuse rather than rebuilding semantics"
        case ctags!="":
            plan.Available=true
            plan.Backend="universal-ctags"
            plan.Command=[]string{"acr-toolbox","structure-index","build","--ctags-source",absRoot,"--root",absRoot,"--output",filepath.Join(absRoot,".acr","source-structure-index.json")}
            plan.Reason="Universal Ctags detected; build a reusable symbol index without installing another parser"
        default:
            switch lang {
            case "csharp":
                if dotnet!=""{
                    plan.Available=true;plan.Backend="dotnet"
                    plan.Command=[]string{dotnet,"msbuild",absRoot,"/t:GenerateRestoreGraphFile","/p:RestoreGraphOutputPath="+filepath.Join(absRoot,".acr","dotnet-restore-graph.json")}
                    plan.Reason="dotnet detected; MSBuild restore graph can provide evaluated project dependency evidence"
                }
            case "go":
                if goCmd!=""{
                    plan.Available=true;plan.Backend="go-list"
                    plan.Command=[]string{goCmd,"list","-deps","-json","./..."}
                    plan.Reason="Go runtime detected; go list can provide package dependency evidence"
                }
            case "c":
                if cc!=""{
                    plan.Available=true;plan.Backend="compiler"
                    plan.Command=[]string{cc,"-M","<translation-unit>"}
                    plan.Reason="C compiler detected; compiler dependency output is more accurate than text include routing when a translation unit is known"
                }
            case "cpp":
                if cpp!=""{
                    plan.Available=true;plan.Backend="compiler"
                    plan.Command=[]string{cpp,"-M","<translation-unit>"}
                    plan.Reason="C++ compiler detected; compiler dependency output is more accurate than text include routing when a translation unit is known"
                }
            case "gdscript":
                if godot!=""{
                    plan.Available=true;plan.Backend="godot"
                    plan.Command=[]string{godot,"--headless","--path",absRoot,"--editor","--quit"}
                    plan.Reason="Godot detected; headless project load can validate resource/scene resolution before deeper graph work"
                }
            case "python":
                if firstAvailable("python3","python")!=""{
                    plan.Available=true;plan.Backend="python-runtime"
                    plan.Command=[]string{firstAvailable("python3","python"),"-m","compileall","-q",absRoot}
                    plan.Reason="Python runtime detected; runtime-level validation is available, while source structure can stay on portable/ctags fallback"
                }
            }
        }
        plans=append(plans,finalizeLargePlan(plan))
    }

    status:="ok"
    if walked.ErrorCount>0{status="ok_with_warnings"}
    selectorWriteJSON(map[string]any{
        "tool":"language-large-plan","status":status,"project_root":absRoot,
        "plans":plans,"automatic_execution":false,
        "run_supported_backends":[]string{"existing-scip-index","universal-ctags"},
        "policy":"Large analysis is never auto-installed or auto-run; run_supported=true means language-large-run can execute it, while available=true with execution=planning_only is advisory only; otherwise keep portable Medium evidence",
    })
    return 0
}

// fileExists はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func fileExists(path string) bool {
    info,err:=os.Stat(path)
    return err==nil && !info.IsDir()
}

// cmdLanguageLargeRun は対象サブコマンドの引数解析・境界I/O・compact出力を統括します。
func cmdLanguageLargeRun(args []string) int {
    fs:=flag.NewFlagSet("language-large-run",flag.ContinueOnError)
    allowHeavy:=fs.Bool("allow-heavy",false,"explicitly permit selected heavy backend execution")
    if err:=fs.Parse(args);err!=nil{return 2}
    root:=".";if fs.NArg()>0{root=fs.Arg(0)}
    absRoot,_:=filepath.Abs(root)
    if !*allowHeavy{
        selectorWriteJSON(map[string]any{
            "tool":"language-large-run","status":"confirmation_required","project_root":absRoot,
            "required_flag":"--allow-heavy",
            "reason":"Large analysis can be expensive; inspect language-large-plan first",
        })
        return 2
    }

    ctags:=firstAvailable("ctags")
    scip:=firstAvailable("scip")
    indexPath:=filepath.Join(absRoot,".acr","source-structure-index.json")
    _=os.MkdirAll(filepath.Dir(indexPath),0755)
    if scip!="" && fileExists(filepath.Join(absRoot,"index.scip")){
        return cmdStructureIndexEntry([]string{"build","--scip",filepath.Join(absRoot,"index.scip"),"--output",indexPath})
    }
    if ctags!=""{
        return cmdStructureIndexEntry([]string{"build","--ctags-source",absRoot,"--root",absRoot,"--output",indexPath})
    }
    selectorWriteJSON(map[string]any{
        "tool":"language-large-run","status":"external_backend_unavailable","project_root":absRoot,
        "fallback":"use language-medium-run and language-large-plan; no heavy backend was executed",
    })
    return 2
}
