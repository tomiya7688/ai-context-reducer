package main

var structureIndexCommands = []string{"build", "query", "expand", "affected"}

// Keep affected-scope and external-index adaptation out of the larger
// build/query/expand implementation so each change reason has a smaller working set.
func cmdStructureIndexEntry(args []string) int {
    if len(args) == 0 {
        emitStructureJSON(map[string]any{"tool": "source-structure-index", "status": "missing_command", "commands": structureIndexCommands})
        return 2
    }
    switch args[0] {
    case "affected":
        return cmdStructureIndexAffected(args[1:])
    case "build":
        prepared, cleanup, failure := prepareStructureSCIPBuildArgs(args[1:])
        if failure != nil {
            status := "input_read_failed"
            if failure.Status == "backend_unavailable" {
                status = "external_backend_unavailable"
            } else if failure.Status == "invalid_arguments" {
                status = "invalid_arguments"
            }
            payload := map[string]any{
                "tool":       "source-structure-index",
                "status":     status,
                "input_kind": "scip_index",
                "backend":    "scip",
                "error":      failure.Error,
            }
            if failure.Path != "" {
                payload["path"] = failure.Path
            }
            emitStructureJSON(payload)
            return 2
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
