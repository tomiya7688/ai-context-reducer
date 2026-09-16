package main

import (
    "encoding/json"
    "os"
    "path/filepath"
    "testing"
)

func sampleCtagsJSONLines(t *testing.T, path string) {
    t.Helper()
    rows := []map[string]any{
        {"_type": "ptag", "name": "JSON_OUTPUT_VERSION", "path": "1.0"},
        {"_type": "tag", "name": "Klass", "path": "src/app.py", "line": 1, "language": "Python", "kind": "class"},
        {"_type": "tag", "name": "method", "path": "src/app.py", "line": 3, "language": "Python", "kind": "member", "scope": "Klass", "scopeKind": "class", "signature": "(self)"},
    }
    file, err := os.Create(path)
    if err != nil {
        t.Fatal(err)
    }
    encoder := json.NewEncoder(file)
    for _, row := range rows {
        if err := encoder.Encode(row); err != nil {
            _ = file.Close()
            t.Fatal(err)
        }
    }
    if err := file.Close(); err != nil {
        t.Fatal(err)
    }
}

func TestNormalizeCtagsRowsPreservesNestedOwnership(t *testing.T) {
    raw := []any{
        map[string]any{"_type": "tag", "name": "Klass", "path": "src/app.py", "line": float64(1), "language": "Python", "kind": "class"},
        map[string]any{"_type": "tag", "name": "method", "path": "src/app.py", "line": float64(3), "language": "Python", "kind": "member", "scope": "Klass"},
    }
    symbols, graph, metadata, err := normalizeCtagsRows(raw)
    if err != nil {
        t.Fatal(err)
    }
    if metadata["tag_count"] != 2 {
        t.Fatalf("unexpected metadata: %#v", metadata)
    }
    files := symbols["files"].([]any)
    if len(files) != 1 {
        t.Fatalf("unexpected symbols: %#v", symbols)
    }
    edges := graph["edges"].([]any)
    found := false
    for _, rawEdge := range edges {
        edge := rawEdge.(map[string]any)
        if edge["from"] == "symbol:src/app.py::Klass" && edge["to"] == "symbol:src/app.py::Klass::method" && edge["kind"] == "owns" {
            found = true
        }
    }
    if !found {
        t.Fatalf("nested ownership edge missing: %#v", graph)
    }
}

func TestCtagsJSONBuildRoundTripPreservesOwnership(t *testing.T) {
    root := t.TempDir()
    tags := filepath.Join(root, "tags.jsonl")
    sampleCtagsJSONLines(t, tags)
    output := filepath.Join(root, "index.json")

    code, summary := captureJSONCommand(t, func() int {
        return cmdStructureIndexEntry([]string{"build", "--ctags-json", tags, "--output", output})
    })
    if code != 0 {
        t.Fatalf("unexpected exit code %d: %#v", code, summary)
    }
    index, err := readStructureIndex(output)
    if err != nil {
        t.Fatal(err)
    }
    nodes := map[string]bool{}
    for _, node := range index.Nodes {
        nodes[node.ID] = true
    }
    if !nodes["symbol:src/app.py::Klass"] || !nodes["symbol:src/app.py::Klass::method"] {
        t.Fatalf("expected Ctags symbols in index: %#v", index.Nodes)
    }
    found := false
    for _, edge := range index.Edges {
        if edge.From == "symbol:src/app.py::Klass" && edge.To == "symbol:src/app.py::Klass::method" && edge.Kind == "owns" {
            found = true
        }
    }
    if !found {
        t.Fatalf("ownership did not survive final index: %#v", index.Edges)
    }
}

func TestCtagsJSONInvalidLineIsExplicit(t *testing.T) {
    root := t.TempDir()
    tags := filepath.Join(root, "bad.jsonl")
    if err := os.WriteFile(tags, []byte("{not-json}\n"), 0o644); err != nil {
        t.Fatal(err)
    }
    code, payload := captureJSONCommand(t, func() int {
        return cmdStructureIndexEntry([]string{"build", "--ctags-json", tags, "--output", filepath.Join(root, "index.json")})
    })
    if code == 0 || payload["status"] != "input_read_failed" || payload["backend"] != "ctags" {
        t.Fatalf("invalid Ctags JSON must be explicit: code=%d payload=%#v", code, payload)
    }
}
