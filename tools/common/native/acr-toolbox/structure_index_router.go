package main

var structureIndexCommands = []string{"build", "query", "expand", "affected"}

// emitStructureAdapterFailure は内部結果を安定した利用者向け出力へ変換します。
func emitStructureAdapterFailure(backend, inputKind string, status string, path string, message string) int {
    outputStatus := "input_read_failed"
    if status == "backend_unavailable" || status == "backend_incompatible" {
        outputStatus = "external_backend_unavailable"
    } else if status == "invalid_arguments" {
        outputStatus = "invalid_arguments"
    }
    payload := map[string]any{
        "tool":       "source-structure-index",
        "status":     outputStatus,
        "input_kind": inputKind,
        "backend":    backend,
        "error":      message,
    }
    if path != "" {
        payload["path"] = path
    }
    emitStructureJSON(payload)
    return 2
}

// Keep affected-scope and external-index adaptation out of the larger
// build/query/expand implementation so each change reason has a smaller working set.
// cmdStructureIndexEntry は対象サブコマンドの引数解析・境界I/O・compact出力を統括します。
func cmdStructureIndexEntry(args []string) int {
    if len(args) == 0 {
        emitStructureJSON(map[string]any{"tool": "source-structure-index", "status": "missing_command", "commands": structureIndexCommands})
        return 2
    }
    switch args[0] {
    case "affected":
        return cmdStructureIndexAffected(args[1:])
    case "build":
        ctagsPrepared, ctagsCleanup, ctagsFailure := prepareStructureCtagsBuildArgs(args[1:])
        if ctagsFailure != nil {
            return emitStructureAdapterFailure("ctags", "ctags_source_or_json", ctagsFailure.Status, ctagsFailure.Path, ctagsFailure.Error)
        }
        defer ctagsCleanup()

        prepared, cleanup, failure := prepareStructureSCIPBuildArgs(ctagsPrepared)
        if failure != nil {
            return emitStructureAdapterFailure("scip", "scip_index", failure.Status, failure.Path, failure.Error)
        }
        defer cleanup()
        return cmdStructureIndexBuild(prepared)
    case "query", "expand":
        return cmdStructureIndex(args)
    default:
        emitStructureJSON(map[string]any{"tool": "source-structure-index", "status": "unknown_command", "command": args[0], "commands": structureIndexCommands})
        return 2
    }
}
