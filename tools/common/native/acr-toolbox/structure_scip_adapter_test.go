package main

import (
    "encoding/json"
    "os"
    "path/filepath"
    "strings"
    "testing"
)

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
    byName := map[string]map[string]any{}
    for _, raw := range symbolRows {
        row := raw.(map[string]any)
        byName[row["name"].(string)] = row
    }
    if byName["A"]["line"] != 1 {
        t.Fatalf("expected one-based line, got %#v", byName["A"])
    }
    if byName["do"]["owner_qualified_name"] != "scip-python python pkg 1.0 A#" {
        t.Fatalf("missing owner: %#v", byName["do"])
    }
    if byName["do"]["signature"] != "def do(self) -> B" {
        t.Fatalf("missing signature: %#v", byName["do"])
    }

    edges := graph["edges"].([]any)
    foundDependency := false
    foundContains := false
    for _, raw := range edges {
        edge := raw.(map[string]any)
        if edge["from"] == "module:scip:pkg/a.py" && edge["to"] == "module:scip:pkg/b.py" && edge["kind"] == "depends_on" {
            foundDependency = true
        }
        if edge["from"] == "module:scip:pkg/a.py" && edge["to"] == "file:pkg/a.py" && edge["kind"] == "contains_file" {
            foundContains = true
        }
    }
    if !foundDependency || !foundContains {
        t.Fatalf("expected routing edges, got %#v", edges)
    }

    second := symbols[1].(map[string]any)
    secondSymbols := second["symbols"].([]any)
    if secondSymbols[0].(map[string]any)["kind"] != "unknown" {
        t.Fatalf("missing SCIP kind should normalize to unknown: %#v", secondSymbols[0])
    }
}

func TestPrepareStructureSCIPBuildArgsUsesExistingJSON(t *testing.T) {
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
}

func TestMissingSCIPCLIIsExplicit(t *testing.T) {
    t.Setenv("PATH", "")
    _, failure := loadSCIPPrintJSON("index.scip", true)
    if failure == nil || failure.Status != "backend_unavailable" {
        t.Fatalf("expected backend_unavailable, got %#v", failure)
    }
}

func TestSCIPErrorIsBounded(t *testing.T) {
    value := boundedSCIPError(strings.Repeat("x", structureSCIPErrorLimit+500))
    if len(value) > structureSCIPErrorLimit+32 || !strings.HasSuffix(value, "... truncated") {
        t.Fatalf("unexpected bounded error length/content: %d %q", len(value), value[len(value)-20:])
    }
}
