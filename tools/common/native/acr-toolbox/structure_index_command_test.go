package main

import (
    "os"
    "path/filepath"
    "testing"
)

// TestBuildStructureIndexNormalizesPythonInputs は対象機能の契約と回帰条件が維持されることを確認します。
func TestBuildStructureIndexNormalizesPythonInputs(t *testing.T) {
    dir := t.TempDir()
    symbols := filepath.Join(dir, "symbols.json")
    graph := filepath.Join(dir, "graph.json")
    if err := os.WriteFile(symbols, []byte(`[
      {"file":"pkg/a.py","symbols":[{"kind":"ClassDef","name":"Service","line":3}]}
    ]`), 0o644); err != nil { t.Fatal(err) }
    if err := os.WriteFile(graph, []byte(`{
      "edges":[{"from":"pkg.a","to":"pkg.b"}],
      "truncated":false
    }`), 0o644); err != nil { t.Fatal(err) }

    index, err := buildStructureIndex([]string{symbols}, []string{graph}, "")
    if err != nil { t.Fatal(err) }
    nodes := map[string]bool{}
    for _, node := range index.Nodes { nodes[node.ID] = true }
    if !nodes["file:pkg/a.py"] { t.Fatal("missing file node") }
    if !nodes["module:pkg.a"] { t.Fatal("missing python module node") }
    if !nodes["symbol:pkg/a.py::Service"] { t.Fatal("missing symbol node") }
    if !nodes["module:pkg.b"] { t.Fatal("missing dependency node") }

    edgeFound := false
    for _, edge := range index.Edges {
        if edge.From == "module:pkg.a" && edge.To == "module:pkg.b" && edge.Kind == "depends_on" {
            edgeFound = true
        }
    }
    if !edgeFound { t.Fatal("missing dependency edge") }
}

// TestBuildStructureIndexBridgesGoPackageToFile は対象機能の契約と回帰条件が維持されることを確認します。
func TestBuildStructureIndexBridgesGoPackageToFile(t *testing.T) {
    dir := t.TempDir()
    symbols := filepath.Join(dir, "symbols.json")
    graph := filepath.Join(dir, "graph.json")
    if err := os.WriteFile(symbols, []byte(`[
      {"file":"internal/store/store.go","symbols":[{"kind":"func","name":"Open","line":8}]}
    ]`), 0o644); err != nil { t.Fatal(err) }
    if err := os.WriteFile(graph, []byte(`{
      "module":"example.com/project",
      "edges":[],
      "truncated":false
    }`), 0o644); err != nil { t.Fatal(err) }

    index, err := buildStructureIndex([]string{symbols}, []string{graph}, "")
    if err != nil { t.Fatal(err) }
    found := false
    for _, edge := range index.Edges {
        if edge.From == "module:example.com/project/internal/store" && edge.To == "file:internal/store/store.go" && edge.Kind == "contains_file" {
            found = true
        }
    }
    if !found { t.Fatal("missing Go package to file bridge") }
}


// TestBuildStructureIndexPropagatesAnalyzerWarnings は対象機能の契約と回帰条件が維持されることを確認します。
func TestBuildStructureIndexPropagatesAnalyzerWarnings(t *testing.T) {
    dir := t.TempDir()
    symbols := filepath.Join(dir, "symbols.json")
    if err := os.WriteFile(symbols, []byte(`{
      "tool":"go-symbols",
      "status":"ok_with_warnings",
      "files":[{"file":"broken.go","status":"parse_failed","symbols":[]}],
      "parse_error_count":1,
      "read_error_count":0,
      "unsupported_input_count":2
    }`), 0o644); err != nil { t.Fatal(err) }

    index, err := buildStructureIndex([]string{symbols}, nil, "")
    if err != nil { t.Fatal(err) }
    if len(index.InputErrors) != 1 {
        t.Fatalf("expected one analyzer warning, got %#v", index.InputErrors)
    }
    want := symbols + ": analyzer warnings parse_error_count=1 unsupported_input_count=2"
    if index.InputErrors[0] != want {
        t.Fatalf("unexpected analyzer warning: %q want %q", index.InputErrors[0], want)
    }
}



// TestBuildStructureIndexPropagatesGraphWarnings は対象機能の契約と回帰条件が維持されることを確認します。
func TestBuildStructureIndexPropagatesGraphWarnings(t *testing.T) {
    dir := t.TempDir()
    graph := filepath.Join(dir, "graph.json")
    if err := os.WriteFile(graph, []byte(`{
      "tool":"go-package-graph",
      "status":"ok_with_warnings",
      "module":"example.com/demo",
      "edges":[],
      "parse_error_count":1,
      "read_error_count":2,
      "scan_truncated":false
    }`), 0o644); err != nil { t.Fatal(err) }

    index, err := buildStructureIndex(nil, []string{graph}, "")
    if err != nil { t.Fatal(err) }
    if len(index.InputErrors) != 1 {
        t.Fatalf("expected one graph warning, got %#v", index.InputErrors)
    }
    want := graph + ": analyzer warnings parse_error_count=1 read_error_count=2"
    if index.InputErrors[0] != want {
        t.Fatalf("unexpected graph warning: %q want %q", index.InputErrors[0], want)
    }
}


// TestStructureQueryAndExpansion は対象機能の契約と回帰条件が維持されることを確認します。
func TestStructureQueryAndExpansion(t *testing.T) {
    index := structureIndex{
        Format: structureIndexFormat,
        Nodes: []structureNode{
            {ID: "module:a", Kind: "module", Name: "a"},
            {ID: "module:b", Kind: "module", Name: "b"},
            {ID: "module:c", Kind: "module", Name: "c"},
        },
        Edges: []structureEdge{
            {From: "module:a", To: "module:b", Kind: "depends_on"},
            {From: "module:b", To: "module:a", Kind: "depends_on"},
            {From: "module:b", To: "module:c", Kind: "depends_on"},
        },
    }
    matches, truncated := queryStructureNodes(index, "a", 10)
    if truncated || len(matches) != 1 || matches[0].ID != "module:a" {
        t.Fatalf("unexpected query result: %#v truncated=%v", matches, truncated)
    }
    result := expandStructure(index, "module:a", 2, 2, "both")
    nodes, ok := result["nodes"].([]structureNode)
    if !ok || len(nodes) != 2 { t.Fatalf("unexpected nodes: %#v", result["nodes"]) }
    if truncatedValue, _ := result["nodes_truncated"].(bool); !truncatedValue {
        t.Fatal("expected bounded expansion to truncate")
    }
    groups, ok := result["cycle_groups"].([][]string)
    if !ok || len(groups) != 1 || len(groups[0]) != 2 {
        t.Fatalf("unexpected cycle groups: %#v", result["cycle_groups"])
    }
}
