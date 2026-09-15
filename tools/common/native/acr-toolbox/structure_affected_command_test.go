package main

import "testing"

func affectedFixture() structureIndex {
    return structureIndex{
        Format: structureIndexFormat,
        Nodes: []structureNode{
            {ID: "module:a", Kind: "module", Name: "a"},
            {ID: "module:b", Kind: "module", Name: "b"},
            {ID: "module:c", Kind: "module", Name: "c"},
            {ID: "file:a.go", Kind: "file", Path: "a.go"},
            {ID: "file:b.go", Kind: "file", Path: "b.go"},
            {ID: "file:c.go", Kind: "file", Path: "c.go"},
        },
        Edges: []structureEdge{
            {From: "module:a", To: "file:a.go", Kind: "contains_file"},
            {From: "module:b", To: "file:b.go", Kind: "contains_file"},
            {From: "module:c", To: "file:c.go", Kind: "contains_file"},
            {From: "module:a", To: "module:b", Kind: "depends_on"},
            {From: "module:c", To: "module:a", Kind: "depends_on"},
        },
    }
}

func TestAffectedStructureFindsTransitiveDependents(t *testing.T) {
    result := affectedStructure(affectedFixture(), []string{"b.go"}, 80)
    if result["impact_uncertain"].(bool) {
        t.Fatalf("expected certain impact, got %#v", result["uncertainty_reasons"])
    }
    if got := result["affected_module_count_total"].(int); got != 3 {
        t.Fatalf("expected 3 affected modules, got %d", got)
    }
    rows := result["affected_modules"].([]map[string]any)
    want := []string{"module:b", "module:a", "module:c"}
    for i, id := range want {
        if rows[i]["id"].(string) != id {
            t.Fatalf("row %d: expected %s, got %#v", i, id, rows[i]["id"])
        }
        if rows[i]["distance_from_change"].(int) != i {
            t.Fatalf("row %d: expected distance %d, got %#v", i, i, rows[i]["distance_from_change"])
        }
    }
}

func TestAffectedStructureTruncationRequiresBroaderValidation(t *testing.T) {
    result := affectedStructure(affectedFixture(), []string{"b.go"}, 2)
    if !result["affected_modules_truncated"].(bool) {
        t.Fatal("expected truncated affected module output")
    }
    if result["affected_module_count_total"].(int) != 3 {
        t.Fatalf("expected full internal closure count, got %#v", result["affected_module_count_total"])
    }
    if result["recommended_validation_scope"].(string) != "broader_or_full" {
        t.Fatalf("expected broader fallback, got %#v", result["recommended_validation_scope"])
    }
}

func TestAffectedStructureUnmatchedFileIsUncertain(t *testing.T) {
    result := affectedStructure(affectedFixture(), []string{"missing.go"}, 80)
    if !result["impact_uncertain"].(bool) {
        t.Fatal("expected unmatched change to be uncertain")
    }
    unmatched := result["unmatched_changed_files"].([]string)
    if len(unmatched) != 1 || unmatched[0] != "missing.go" {
        t.Fatalf("unexpected unmatched files: %#v", unmatched)
    }
}
