package main

import (
    "encoding/json"
    "os"
    "path/filepath"
    "strings"
    "testing"
)

// scipTestPayload はtest setupや検証を局所化し、各testの意図を読みやすく保ちます。
func scipTestPayload() map[string]any {
    return map[string]any{
        "documents": []any{
            map[string]any{
                "relativePath": "pkg/a.py",
                "language":     "Python",
                "symbols": []any{
                    map[string]any{
                        "symbol":      "scip-python python pkg 1.0 A#",
                        "displayName": "A",
                        "kind":        "Class",
                    },
                    map[string]any{
                        "symbol":          "scip-python python pkg 1.0 A#do().",
                        "displayName":     "do",
                        "kind":            "Method",
                        "enclosingSymbol": "scip-python python pkg 1.0 A#",
                        "signatureDocumentation": map[string]any{"text": "def do(self) -> B"},
                    },
                },
                "occurrences": []any{
                    map[string]any{
                        "range":       []any{float64(0), float64(0), float64(1)},
                        "symbol":      "scip-python python pkg 1.0 A#",
                        "symbolRoles": float64(1),
                    },
                    map[string]any{
                        "range":       []any{float64(2), float64(4), float64(6)},
                        "symbol":      "scip-python python pkg 1.0 B#",
                        "symbolRoles": float64(8),
                    },
                },
            },
            map[string]any{
                "relativePath": "pkg/b.py",
                "language":     "Python",
                "symbols": []any{
                    map[string]any{
                        "symbol":      "scip-python python pkg 1.0 B#",
                        "displayName": "B",
                    },
                },
                "occurrences": []any{
                    map[string]any{
                        "range":       []any{float64(4), float64(0), float64(1)},
                        "symbol":      "scip-python python pkg 1.0 B#",
                        "symbolRoles": float64(1),
                    },
                },
            },
        },
    }
}

// TestNormalizeSCIPPrintBuildsRoutingDependencies は対象機能の契約と回帰条件が維持されることを確認します。
func TestNormalizeSCIPPrintBuildsRoutingDependencies(t *testing.T) {
    symbols, graph, err := normalizeSCIPPrint(scipTestPayload())
    if err != nil {
        t.Fatal(err)
    }
    if len(symbols) != 2 {
        t.Fatalf("unexpected symbol rows: %#v", symbols)
    }

    first := symbols[0].(map[string]any)
    symbolRows := first["symbols"].([]any)
    if len(symbolRows) != 1 {
        t.Fatalf("nested symbols should be routed through explicit ownership graph nodes: %#v", symbolRows)
    }
    topLevel := symbolRows[0].(map[string]any)
    if topLevel["name"] != "A" || topLevel["line"] != 1 {
        t.Fatalf("unexpected top-level symbol: %#v", topLevel)
    }

    nodes := graph["nodes"].([]any)
    foundMethod := false
    for _, raw := range nodes {
        node := raw.(map[string]any)
        if node["id"] == "symbol:scip-python python pkg 1.0 A#do()." {
            foundMethod = node["name"] == "do" && node["line"] == 0
        }
    }
    if !foundMethod {
        t.Fatalf("nested method node missing: %#v", nodes)
    }

    edges := graph["edges"].([]any)
    foundDependency := false
    foundContains := false
    foundOwner := false
    for _, raw := range edges {
        edge := raw.(map[string]any)
        if edge["from"] == "module:scip:pkg/a.py" && edge["to"] == "module:scip:pkg/b.py" && edge["kind"] == "depends_on" {
            foundDependency = true
        }
        if edge["from"] == "module:scip:pkg/a.py" && edge["to"] == "file:pkg/a.py" && edge["kind"] == "contains_file" {
            foundContains = true
        }
        if edge["from"] == "symbol:scip-python python pkg 1.0 A#" && edge["to"] == "symbol:scip-python python pkg 1.0 A#do()." && edge["kind"] == "owns" {
            foundOwner = true
        }
    }
    if !foundDependency || !foundContains || !foundOwner {
        t.Fatalf("expected routing and ownership edges, got %#v", edges)
    }

    second := symbols[1].(map[string]any)
    secondSymbols := second["symbols"].([]any)
    if secondSymbols[0].(map[string]any)["kind"] != "unknown" {
        t.Fatalf("missing SCIP kind should normalize to unknown: %#v", secondSymbols[0])
    }
}

// TestPrepareStructureSCIPBuildArgsPreservesOwnershipInFinalIndex は対象機能の契約と回帰条件が維持されることを確認します。
func TestPrepareStructureSCIPBuildArgsPreservesOwnershipInFinalIndex(t *testing.T) {
    root := t.TempDir()
    input := filepath.Join(root, "index.json")
    output := filepath.Join(root, "index.acr.json")
    data, err := json.Marshal(scipTestPayload())
    if err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(input, data, 0o644); err != nil {
        t.Fatal(err)
    }

    prepared, cleanup, failure := prepareStructureSCIPBuildArgs([]string{"--scip-json", input, "--output", output})
    if failure != nil {
        t.Fatalf("unexpected failure: %#v", failure)
    }
    defer cleanup()

    joined := strings.Join(prepared, " ")
    if !strings.Contains(joined, "--symbols") || !strings.Contains(joined, "--graph") || !strings.Contains(joined, "--output "+output) {
        t.Fatalf("unexpected prepared args: %#v", prepared)
    }

    symbolPath := ""
    graphPath := ""
    for i := 0; i+1 < len(prepared); i++ {
        if prepared[i] == "--symbols" {
            symbolPath = prepared[i+1]
        }
        if prepared[i] == "--graph" {
            graphPath = prepared[i+1]
        }
    }
    if symbolPath == "" || graphPath == "" {
        t.Fatalf("prepared paths missing: %#v", prepared)
    }

    index, err := buildStructureIndex([]string{symbolPath}, []string{graphPath}, "")
    if err != nil {
        t.Fatal(err)
    }
    ownerEdge := false
    fileOwnsNested := false
    for _, edge := range index.Edges {
        if edge.From == "symbol:scip-python python pkg 1.0 A#" && edge.To == "symbol:scip-python python pkg 1.0 A#do()." && edge.Kind == "owns" {
            ownerEdge = true
        }
        if edge.From == "file:pkg/a.py" && edge.To == "symbol:scip-python python pkg 1.0 A#do()." && edge.Kind == "owns" {
            fileOwnsNested = true
        }
    }
    if !ownerEdge || fileOwnsNested {
        t.Fatalf("ownership was not preserved cleanly: owner=%v fileOwnsNested=%v edges=%#v", ownerEdge, fileOwnsNested, index.Edges)
    }
}

// TestMissingSCIPCLIIsExplicit は対象機能の契約と回帰条件が維持されることを確認します。
func TestMissingSCIPCLIIsExplicit(t *testing.T) {
    t.Setenv("PATH", "")
    _, failure := loadSCIPPrintJSON("index.scip", true)
    if failure == nil || failure.Status != "backend_unavailable" {
        t.Fatalf("expected backend_unavailable, got %#v", failure)
    }
}

// TestSCIPErrorIsBounded は対象機能の契約と回帰条件が維持されることを確認します。
func TestSCIPErrorIsBounded(t *testing.T) {
    value := boundedSCIPError(strings.Repeat("x", structureSCIPErrorLimit+500))
    if len(value) > structureSCIPErrorLimit+32 || !strings.HasSuffix(value, "... truncated") {
        t.Fatalf("unexpected bounded error length/content: %d %q", len(value), value[len(value)-20:])
    }
}
