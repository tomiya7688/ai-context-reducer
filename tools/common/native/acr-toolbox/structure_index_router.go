package main

var structureIndexCommands = []string{"build", "query", "expand", "affected"}

// Keep affected-scope logic in its own file so changes to impact routing do not
// require reading the larger build/query/expand implementation.
func cmdStructureIndexEntry(args []string) int {
    if len(args) == 0 {
        emitStructureJSON(map[string]any{"tool": "source-structure-index", "status": "missing_command", "commands": structureIndexCommands})
        return 2
    }
    switch args[0] {
    case "affected":
        return cmdStructureIndexAffected(args[1:])
    case "build", "query", "expand":
        return cmdStructureIndex(args)
    default:
        emitStructureJSON(map[string]any{"tool": "source-structure-index", "status": "unknown_command", "command": args[0], "commands": structureIndexCommands})
        return 2
    }
}
