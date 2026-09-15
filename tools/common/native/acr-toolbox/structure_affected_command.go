package main

import (
    "flag"
    "io"
    "sort"
    "strings"
)

func structureAffectedPathKey(raw string) string {
    value := strings.ReplaceAll(raw, "\\", "/")
    for strings.HasPrefix(value, "./") {
        value = strings.TrimPrefix(value, "./")
    }
    return value
}

func affectedStructure(index structureIndex, changedFiles []string, maxResults int) map[string]any {
    nodes := map[string]structureNode{}
    fileIDsByPath := map[string]string{}
    for _, node := range index.Nodes {
        nodes[node.ID] = node
        if node.Kind == "file" && node.Path != "" {
            fileIDsByPath[structureAffectedPathKey(node.Path)] = node.ID
        }
    }

    fileOwners := map[string]map[string]bool{}
    reverseDependencies := map[string]map[string]bool{}
    dependencyEdgeCount := 0
    for _, edge := range index.Edges {
        if edge.Kind == "contains_file" && nodes[edge.From].Kind == "module" {
            if fileOwners[edge.To] == nil { fileOwners[edge.To] = map[string]bool{} }
            fileOwners[edge.To][edge.From] = true
        } else if edge.Kind == "depends_on" {
            if reverseDependencies[edge.To] == nil { reverseDependencies[edge.To] = map[string]bool{} }
            reverseDependencies[edge.To][edge.From] = true
            dependencyEdgeCount++
        }
    }

    changedSet := map[string]bool{}
    matched := []map[string]any{}
    unmatched := []string{}
    ownerless := []string{}
    seeds := map[string]bool{}
    for _, raw := range changedFiles {
        path := structureAffectedPathKey(raw)
        if changedSet[path] { continue }
        changedSet[path] = true
        fileID := fileIDsByPath[path]
        if fileID == "" {
            unmatched = append(unmatched, path)
            continue
        }
        owners := []string{}
        for owner := range fileOwners[fileID] { owners = append(owners, owner) }
        sort.Strings(owners)
        matched = append(matched, map[string]any{
            "path": path,
            "file_node_id": fileID,
            "seed_module_ids": owners,
        })
        if len(owners) == 0 { ownerless = append(ownerless, path) }
        for _, owner := range owners { seeds[owner] = true }
    }
    sort.Strings(unmatched)
    sort.Strings(ownerless)
    sort.Slice(matched, func(i, j int) bool { return matched[i]["path"].(string) < matched[j]["path"].(string) })

    distance := map[string]int{}
    queue := []string{}
    seedIDs := []string{}
    for seed := range seeds { seedIDs = append(seedIDs, seed) }
    sort.Strings(seedIDs)
    for _, seed := range seedIDs {
        distance[seed] = 0
        queue = append(queue, seed)
    }
    for len(queue) > 0 {
        current := queue[0]
        queue = queue[1:]
        nextDistance := distance[current] + 1
        dependents := []string{}
        for dependent := range reverseDependencies[current] { dependents = append(dependents, dependent) }
        sort.Strings(dependents)
        for _, dependent := range dependents {
            previous, exists := distance[dependent]
            if exists && previous <= nextDistance { continue }
            distance[dependent] = nextDistance
            queue = append(queue, dependent)
        }
    }

    affected := []map[string]any{}
    for id, d := range distance {
        node, ok := nodes[id]
        if !ok { node = structureNode{ID: id, Kind: "module"} }
        affected = append(affected, map[string]any{
            "id": node.ID,
            "kind": node.Kind,
            "name": node.Name,
            "distance_from_change": d,
        })
    }
    sort.Slice(affected, func(i, j int) bool {
        di := affected[i]["distance_from_change"].(int)
        dj := affected[j]["distance_from_change"].(int)
        if di != dj { return di < dj }
        return affected[i]["id"].(string) < affected[j]["id"].(string)
    })

    total := len(affected)
    truncated := maxResults > 0 && total > maxResults
    returned := affected
    if truncated { returned = affected[:maxResults] }

    reasons := []string{}
    if index.InputTruncated { reasons = append(reasons, "source_structure_index_input_was_truncated") }
    if len(unmatched) > 0 { reasons = append(reasons, "some_changed_files_are_not_present_in_the_index") }
    if len(ownerless) > 0 { reasons = append(reasons, "some_changed_files_have_no_module_owner_in_the_index") }
    if len(seedIDs) > 0 && dependencyEdgeCount == 0 { reasons = append(reasons, "dependency_relationships_are_absent_or_empty") }
    if truncated { reasons = append(reasons, "affected_module_output_was_truncated") }
    uncertain := len(reasons) > 0

    changed := make([]string, 0, len(changedSet))
    for path := range changedSet { changed = append(changed, path) }
    sort.Strings(changed)
    scope := "targeted_dependents"
    if uncertain { scope = "broader_or_full" }

    return map[string]any{
        "changed_files": changed,
        "matched_changed_files": matched,
        "unmatched_changed_files": unmatched,
        "changed_files_without_module_owner": ownerless,
        "seed_module_ids": seedIDs,
        "dependency_edge_count": dependencyEdgeCount,
        "affected_module_count_total": total,
        "affected_modules_returned": len(returned),
        "affected_modules_truncated": truncated,
        "affected_modules": returned,
        "impact_uncertain": uncertain,
        "uncertainty_reasons": reasons,
        "recommended_validation_scope": scope,
    }
}

func cmdStructureIndexAffected(args []string) int {
    fs := flag.NewFlagSet("structure-index affected", flag.ContinueOnError)
    fs.SetOutput(io.Discard)
    changed := structureStringList{}
    fs.Var(&changed, "changed", "changed repository-relative file path; repeatable")
    maxResults := fs.Int("max-results", 80, "maximum affected modules returned; internal dependency closure is complete; 0 means unlimited")
    if err := fs.Parse(args); err != nil || fs.NArg() < 1 || len(changed) == 0 {
        text := "index and at least one --changed path are required"
        if err != nil { text = err.Error() }
        emitStructureJSON(map[string]any{"tool": "source-structure-index", "status": "invalid_arguments", "error": text})
        return 2
    }

    indexPath := fs.Arg(0)
    index, err := readStructureIndex(indexPath)
    if err != nil {
        emitStructureJSON(map[string]any{"tool": "source-structure-index", "status": "index_read_failed", "index_path": indexPath, "error": err.Error()})
        return 2
    }
    limit := *maxResults
    if limit < 0 { limit = 0 }
    result := affectedStructure(index, changed, limit)
    result["tool"] = "source-structure-index"
    if result["impact_uncertain"].(bool) { result["status"] = "ok_with_uncertainty" } else { result["status"] = "ok" }
    result["index_path"] = indexPath
    result["index_input_truncated"] = index.InputTruncated
    emitStructureJSON(result)
    return 0
}
