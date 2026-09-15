package main

// Keep affected-scope logic in its own file so changes to impact routing do not
// require reading the larger build/query/expand implementation.
func cmdStructureIndexEntry(args []string) int {
    if len(args) > 0 && args[0] == "affected" {
        return cmdStructureIndexAffected(args[1:])
    }
    return cmdStructureIndex(args)
}
