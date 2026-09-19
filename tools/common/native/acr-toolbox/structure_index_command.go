package main

import (
    "encoding/json"
    "flag"
    "fmt"
    "io"
    "os"
    "path/filepath"
    "sort"
    "strings"
)

const structureIndexFormat = "acr-source-structure-index-v1"

type structureStringList []string

// String はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func (s *structureStringList) String() string { return strings.Join(*s, ",") }
// Set はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func (s *structureStringList) Set(value string) error {
    *s = append(*s, value)
    return nil
}

type structureNode struct {
    ID            string `json:"id"`
    Kind          string `json:"kind"`
    Name          string `json:"name,omitempty"`
    QualifiedName string `json:"qualified_name,omitempty"`
    Path          string `json:"path,omitempty"`
    SymbolKind    string `json:"symbol_kind,omitempty"`
    Line          int    `json:"line,omitempty"`
    EndLine       int    `json:"end_line,omitempty"`
    Distance      *int   `json:"distance,omitempty"`
    FanOut        *int   `json:"fan_out,omitempty"`
    FanIn         *int   `json:"fan_in,omitempty"`
}

type structureEdge struct {
    From string `json:"from"`
    To   string `json:"to"`
    Kind string `json:"kind"`
}

type structureIndex struct {
    Format         string          `json:"format"`
    Nodes          []structureNode `json:"nodes"`
    Edges          []structureEdge `json:"edges"`
    InputTruncated bool            `json:"input_truncated"`
    InputErrors    []string        `json:"input_errors"`
}

// emitStructureJSON は内部結果を安定した利用者向け出力へ変換します。
func emitStructureJSON(value any) {
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    _ = enc.Encode(value)
}

// structureMap はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func structureMap(raw any) (map[string]any, bool) {
    value, ok := raw.(map[string]any)
    return value, ok
}

// structureString はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func structureString(value any) string {
    if text, ok := value.(string); ok {
        return text
    }
    return ""
}

// structureInt はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func structureInt(value any) int {
    switch n := value.(type) {
    case float64:
        return int(n)
    case int:
        return n
    default:
        return 0
    }
}

// normalizeStructurePath は表記揺れを正規化し、後段の比較条件を単純化します。
func normalizeStructurePath(raw, root string) string {
    path := raw
    if root != "" && filepath.IsAbs(path) {
        if rel, err := filepath.Rel(root, path); err == nil && rel != "" && !strings.HasPrefix(rel, "..") {
            path = rel
        }
    }
    return filepath.ToSlash(path)
}

// pythonModuleFromPath はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func pythonModuleFromPath(path string) string {
    if !strings.HasSuffix(strings.ToLower(path), ".py") {
        return ""
    }
    value := strings.TrimSuffix(filepath.ToSlash(path), filepath.Ext(path))
    if strings.HasSuffix(value, "/__init__") {
        value = strings.TrimSuffix(value, "/__init__")
    }
    return strings.ReplaceAll(strings.Trim(value, "/"), "/", ".")
}

// goPackageFromPath はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func goPackageFromPath(module, path string) string {
    if module == "" || !strings.HasSuffix(strings.ToLower(path), ".go") {
        return ""
    }
    parent := filepath.ToSlash(filepath.Dir(path))
    if parent == "." || parent == "" {
        return strings.TrimSuffix(module, "/")
    }
    return strings.TrimSuffix(module, "/") + "/" + strings.Trim(parent, "/")
}

// structureEdgeKey はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func structureEdgeKey(edge structureEdge) string {
    return edge.From + "\x00" + edge.To + "\x00" + edge.Kind
}

// addStructureNode はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func addStructureNode(nodes map[string]structureNode, node structureNode) {
    if node.ID == "" || node.Kind == "" {
        return
    }
    current, ok := nodes[node.ID]
    if !ok {
        nodes[node.ID] = node
        return
    }
    if current.Name == "" { current.Name = node.Name }
    if current.QualifiedName == "" { current.QualifiedName = node.QualifiedName }
    if current.Path == "" { current.Path = node.Path }
    if current.SymbolKind == "" { current.SymbolKind = node.SymbolKind }
    if current.Line == 0 { current.Line = node.Line }
    if current.EndLine == 0 { current.EndLine = node.EndLine }
    nodes[node.ID] = current
}

// payloadTruncated はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func payloadTruncated(payload map[string]any) bool {
    for key, value := range payload {
        if strings.HasSuffix(key, "truncated") {
            if yes, ok := value.(bool); ok && yes {
                return true
            }
        }
    }
    return false
}

// loadStructureRaw は入力元から必要情報だけを読み込み、後段が扱える形へ整えます。
func loadStructureRaw(path string) (any, error) {
    data, err := os.ReadFile(path)
    if err != nil { return nil, err }
    var value any
    if err := json.Unmarshal(data, &value); err != nil { return nil, err }
    return value, nil
}

// buildStructureIndex は解析結果を後段で再利用できる構造へ組み立てます。
func buildStructureIndex(symbolPaths, graphPaths []string, root string) (structureIndex, error) {
    nodes := map[string]structureNode{}
    edges := map[string]structureEdge{}
    inputErrors := []string{}
    truncated := false

    for _, source := range symbolPaths {
        raw, err := loadStructureRaw(source)
        if err != nil { return structureIndex{}, fmt.Errorf("%s: %w", source, err) }
        rows := []any{}
        switch payload := raw.(type) {
        case []any:
            rows = payload
        case map[string]any:
            if payloadTruncated(payload) { truncated = true }
            warningParts := []string{}
            for _, key := range []string{"parse_error_count", "read_error_count", "unsupported_input_count"} {
                if count := structureInt(payload[key]); count > 0 {
                    warningParts = append(warningParts, fmt.Sprintf("%s=%d", key, count))
                }
            }
            if len(warningParts) > 0 {
                inputErrors = append(inputErrors, source+": analyzer warnings "+strings.Join(warningParts, " "))
            }
            if files, ok := payload["files"].([]any); ok { rows = files } else { inputErrors = append(inputErrors, source+": unsupported symbol payload") }
        default:
            inputErrors = append(inputErrors, source+": unsupported symbol payload")
        }
        for _, rawRow := range rows {
            row, ok := structureMap(rawRow)
            if !ok { continue }
            path := normalizeStructurePath(structureString(row["file"]), root)
            if path == "" { continue }
            fileID := "file:" + path
            addStructureNode(nodes, structureNode{ID: fileID, Kind: "file", Path: path})

            if module := pythonModuleFromPath(path); module != "" {
                moduleID := "module:" + module
                addStructureNode(nodes, structureNode{ID: moduleID, Kind: "module", Name: module})
                edge := structureEdge{From: moduleID, To: fileID, Kind: "contains_file"}
                edges[structureEdgeKey(edge)] = edge
            }

            symbols, _ := row["symbols"].([]any)
            for _, rawSymbol := range symbols {
                symbol, ok := structureMap(rawSymbol)
                if !ok { continue }
                name := structureString(symbol["name"])
                if name == "" { continue }
                qualified := structureString(symbol["qualified_name"])
                if qualified == "" { qualified = path + "::" + name }
                symbolID := "symbol:" + qualified
                addStructureNode(nodes, structureNode{
                    ID: symbolID, Kind: "symbol", Name: name, QualifiedName: qualified,
                    Path: path, SymbolKind: structureString(symbol["kind"]),
                    Line: structureInt(symbol["line"]), EndLine: structureInt(symbol["end_line"]),
                })
                edge := structureEdge{From: fileID, To: symbolID, Kind: "owns"}
                edges[structureEdgeKey(edge)] = edge
            }
        }
    }

    for _, source := range graphPaths {
        raw, err := loadStructureRaw(source)
        if err != nil { return structureIndex{}, fmt.Errorf("%s: %w", source, err) }
        payload, ok := structureMap(raw)
        if !ok {
            inputErrors = append(inputErrors, source+": unsupported graph payload")
            continue
        }
        if payloadTruncated(payload) { truncated = true }
        warningParts := []string{}
        for _, key := range []string{"parse_error_count", "read_error_count", "walk_error_count"} {
            if count := structureInt(payload[key]); count > 0 {
                warningParts = append(warningParts, fmt.Sprintf("%s=%d", key, count))
            }
        }
        if len(warningParts) > 0 {
            inputErrors = append(inputErrors, source+": analyzer warnings "+strings.Join(warningParts, " "))
        }

        explicitNodes, hasExplicitNodes := payload["nodes"].([]any)
        for _, rawNode := range explicitNodes {
            node, ok := structureMap(rawNode)
            if !ok { continue }
            addStructureNode(nodes, structureNode{
                ID: structureString(node["id"]), Kind: structureString(node["kind"]),
                Name: structureString(node["name"]), QualifiedName: structureString(node["qualified_name"]),
                Path: structureString(node["path"]), SymbolKind: structureString(node["symbol_kind"]),
                Line: structureInt(node["line"]), EndLine: structureInt(node["end_line"]),
            })
        }

        goModule := structureString(payload["module"])
        if goModule != "" {
            snapshot := make([]structureNode, 0, len(nodes))
            for _, node := range nodes { snapshot = append(snapshot, node) }
            for _, node := range snapshot {
                if node.Kind != "file" { continue }
                pkg := goPackageFromPath(goModule, node.Path)
                if pkg == "" { continue }
                packageID := "module:" + pkg
                addStructureNode(nodes, structureNode{ID: packageID, Kind: "module", Name: pkg})
                edge := structureEdge{From: packageID, To: node.ID, Kind: "contains_file"}
                edges[structureEdgeKey(edge)] = edge
            }
        }

        rawEdges, _ := payload["edges"].([]any)
        for _, rawEdge := range rawEdges {
            edgeMap, ok := structureMap(rawEdge)
            if !ok { continue }
            from := structureString(edgeMap["from"])
            to := structureString(edgeMap["to"])
            if from == "" || to == "" { continue }
            kind := structureString(edgeMap["kind"])
            if kind == "" { kind = "depends_on" }
            if !hasExplicitNodes {
                from = "module:" + from
                to = "module:" + to
                addStructureNode(nodes, structureNode{ID: from, Kind: "module", Name: strings.TrimPrefix(from, "module:")})
                addStructureNode(nodes, structureNode{ID: to, Kind: "module", Name: strings.TrimPrefix(to, "module:")})
            }
            edge := structureEdge{From: from, To: to, Kind: kind}
            edges[structureEdgeKey(edge)] = edge
        }
    }

    nodeRows := make([]structureNode, 0, len(nodes))
    for _, node := range nodes { nodeRows = append(nodeRows, node) }
    sort.Slice(nodeRows, func(i, j int) bool { return nodeRows[i].ID < nodeRows[j].ID })
    edgeRows := make([]structureEdge, 0, len(edges))
    for _, edge := range edges { edgeRows = append(edgeRows, edge) }
    sort.Slice(edgeRows, func(i, j int) bool {
        if edgeRows[i].From != edgeRows[j].From { return edgeRows[i].From < edgeRows[j].From }
        if edgeRows[i].To != edgeRows[j].To { return edgeRows[i].To < edgeRows[j].To }
        return edgeRows[i].Kind < edgeRows[j].Kind
    })
    return structureIndex{Format: structureIndexFormat, Nodes: nodeRows, Edges: edgeRows, InputTruncated: truncated, InputErrors: inputErrors}, nil
}

// writeStructureIndex は内部結果を安定した利用者向け出力へ変換します。
func writeStructureIndex(path string, index structureIndex) error {
    if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil { return err }
    data, err := json.MarshalIndent(index, "", "  ")
    if err != nil { return err }
    data = append(data, '\n')
    return os.WriteFile(path, data, 0o644)
}

// readStructureIndex は入力元から必要情報だけを読み込み、後段が扱える形へ整えます。
func readStructureIndex(path string) (structureIndex, error) {
    data, err := os.ReadFile(path)
    if err != nil { return structureIndex{}, err }
    var index structureIndex
    if err := json.Unmarshal(data, &index); err != nil { return structureIndex{}, err }
    if index.Format != structureIndexFormat { return structureIndex{}, fmt.Errorf("unsupported index format; expected %s", structureIndexFormat) }
    return index, nil
}

type structureRanked struct {
    Rank int
    ID string
    Node structureNode
}

// queryStructureNodes は広い探索結果から条件に合う対象だけを絞り込みます。
func queryStructureNodes(index structureIndex, pattern string, limit int) ([]structureNode, bool) {
    needle := strings.ToLower(pattern)
    ranked := []structureRanked{}
    for _, node := range index.Nodes {
        values := []string{node.ID, node.QualifiedName, node.Name, node.Path}
        matched, exact, prefix := false, false, false
        for _, value := range values {
            if value == "" { continue }
            low := strings.ToLower(value)
            if strings.Contains(low, needle) { matched = true }
            if low == needle { exact = true }
            if strings.HasPrefix(low, needle) { prefix = true }
        }
        if !matched { continue }
        rank := 2
        if exact { rank = 0 } else if prefix { rank = 1 }
        ranked = append(ranked, structureRanked{Rank: rank, ID: node.ID, Node: node})
    }
    sort.Slice(ranked, func(i, j int) bool {
        if ranked[i].Rank != ranked[j].Rank { return ranked[i].Rank < ranked[j].Rank }
        return ranked[i].ID < ranked[j].ID
    })
    rows := make([]structureNode, len(ranked))
    for i, row := range ranked { rows[i] = row.Node }
    if limit > 0 && len(rows) > limit { return rows[:limit], true }
    return rows, false
}

// resolveStructureTarget はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func resolveStructureTarget(index structureIndex, target string) (string, []structureNode) {
    matches, _ := queryStructureNodes(index, target, 0)
    needle := strings.ToLower(target)
    exact := []structureNode{}
    for _, node := range matches {
        for _, value := range []string{node.ID, node.QualifiedName, node.Name, node.Path} {
            if value != "" && strings.ToLower(value) == needle {
                exact = append(exact, node)
                break
            }
        }
    }
    if len(exact) == 1 { return "ok", exact }
    if len(exact) > 1 { return "target_ambiguous", exact }
    if len(matches) == 1 { return "ok", matches }
    if len(matches) > 1 { return "target_ambiguous", matches }
    return "target_not_found", nil
}

// structureCycleGroups はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func structureCycleGroups(nodeIDs map[string]bool, edges []structureEdge) [][]string {
    graph := map[string][]string{}
    for _, edge := range edges {
        if nodeIDs[edge.From] && nodeIDs[edge.To] { graph[edge.From] = append(graph[edge.From], edge.To) }
    }
    nextIndex := 0
    stack := []string{}
    onStack := map[string]bool{}
    indices := map[string]int{}
    low := map[string]int{}
    groups := [][]string{}

    var strongconnect func(string)
    strongconnect = func(node string) {
        indices[node] = nextIndex
        low[node] = nextIndex
        nextIndex++
        stack = append(stack, node)
        onStack[node] = true
        for _, target := range graph[node] {
            if _, ok := indices[target]; !ok {
                strongconnect(target)
                if low[target] < low[node] { low[node] = low[target] }
            } else if onStack[target] && indices[target] < low[node] {
                low[node] = indices[target]
            }
        }
        if low[node] == indices[node] {
            component := []string{}
            for {
                last := stack[len(stack)-1]
                stack = stack[:len(stack)-1]
                onStack[last] = false
                component = append(component, last)
                if last == node { break }
            }
            selfLoop := false
            if len(component) == 1 {
                for _, target := range graph[node] { if target == node { selfLoop = true; break } }
            }
            if len(component) > 1 || selfLoop {
                sort.Strings(component)
                groups = append(groups, component)
            }
        }
    }

    ids := make([]string, 0, len(nodeIDs))
    for id := range nodeIDs { ids = append(ids, id) }
    sort.Strings(ids)
    for _, id := range ids {
        if _, ok := indices[id]; !ok { strongconnect(id) }
    }
    sort.Slice(groups, func(i, j int) bool { return strings.Join(groups[i], "\x00") < strings.Join(groups[j], "\x00") })
    return groups
}

// expandStructure はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func expandStructure(index structureIndex, start string, depth, maxNodes int, direction string) map[string]any {
    nodes := map[string]structureNode{}
    outgoing := map[string][]structureEdge{}
    incoming := map[string][]structureEdge{}
    for _, node := range index.Nodes { nodes[node.ID] = node }
    for _, edge := range index.Edges {
        outgoing[edge.From] = append(outgoing[edge.From], edge)
        incoming[edge.To] = append(incoming[edge.To], edge)
    }

    visited := map[string]bool{start: true}
    levels := map[string]int{start: 0}
    queue := []string{start}
    truncated := false
    for len(queue) > 0 {
        current := queue[0]
        queue = queue[1:]
        if levels[current] >= depth { continue }
        candidates := map[string]bool{}
        if direction == "out" || direction == "both" {
            for _, edge := range outgoing[current] { candidates[edge.To] = true }
        }
        if direction == "in" || direction == "both" {
            for _, edge := range incoming[current] { candidates[edge.From] = true }
        }
        ids := make([]string, 0, len(candidates))
        for id := range candidates { ids = append(ids, id) }
        sort.Strings(ids)
        for _, id := range ids {
            if visited[id] { continue }
            if maxNodes > 0 && len(visited) >= maxNodes { truncated = true; continue }
            visited[id] = true
            levels[id] = levels[current] + 1
            queue = append(queue, id)
        }
    }

    selectedEdges := []structureEdge{}
    for _, edge := range index.Edges {
        if visited[edge.From] && visited[edge.To] { selectedEdges = append(selectedEdges, edge) }
    }
    ids := make([]string, 0, len(visited))
    for id := range visited { ids = append(ids, id) }
    sort.Slice(ids, func(i, j int) bool {
        if levels[ids[i]] != levels[ids[j]] { return levels[ids[i]] < levels[ids[j]] }
        return ids[i] < ids[j]
    })
    selectedNodes := make([]structureNode, 0, len(ids))
    for _, id := range ids {
        node, ok := nodes[id]
        if !ok { node = structureNode{ID: id, Kind: "unknown"} }
        distance, fanOut, fanIn := levels[id], len(outgoing[id]), len(incoming[id])
        node.Distance, node.FanOut, node.FanIn = &distance, &fanOut, &fanIn
        selectedNodes = append(selectedNodes, node)
    }
    return map[string]any{
        "start_node_id": start,
        "depth": depth,
        "direction": direction,
        "nodes": selectedNodes,
        "edges": selectedEdges,
        "nodes_truncated": truncated,
        "cycle_groups": structureCycleGroups(visited, selectedEdges),
    }
}

// cmdStructureIndexBuild は対象サブコマンドの引数解析・境界I/O・compact出力を統括します。
func cmdStructureIndexBuild(args []string) int {
    fs := flag.NewFlagSet("structure-index build", flag.ContinueOnError)
    fs.SetOutput(io.Discard)
    symbols := structureStringList{}
    graphs := structureStringList{}
    fs.Var(&symbols, "symbols", "symbol analyzer JSON; repeatable")
    fs.Var(&graphs, "graph", "graph analyzer JSON; repeatable")
    root := fs.String("root", "", "optional repository root")
    output := fs.String("output", "", "index file to write")
    if err := fs.Parse(args); err != nil {
        emitStructureJSON(map[string]any{"tool": "source-structure-index", "status": "invalid_arguments", "error": err.Error()})
        return 2
    }
    if len(symbols) == 0 && len(graphs) == 0 {
        emitStructureJSON(map[string]any{"tool": "source-structure-index", "status": "no_inputs", "required_input": "--symbols and/or --graph"})
        return 2
    }
    if *output == "" {
        emitStructureJSON(map[string]any{"tool": "source-structure-index", "status": "missing_output", "required_argument": "--output"})
        return 2
    }
    absRoot := ""
    if *root != "" {
        value, err := filepath.Abs(*root)
        if err != nil {
            emitStructureJSON(map[string]any{"tool": "source-structure-index", "status": "input_read_failed", "error": err.Error()})
            return 2
        }
        absRoot = value
    }
    index, err := buildStructureIndex(symbols, graphs, absRoot)
    if err != nil {
        emitStructureJSON(map[string]any{"tool": "source-structure-index", "status": "input_read_failed", "error": err.Error()})
        return 2
    }
    if err := writeStructureIndex(*output, index); err != nil {
        emitStructureJSON(map[string]any{"tool": "source-structure-index", "status": "index_write_failed", "index_path": *output, "error": err.Error()})
        return 2
    }
    status := "ok"
    if len(index.InputErrors) > 0 { status = "ok_with_warnings" }
    emitStructureJSON(map[string]any{
        "tool": "source-structure-index", "status": status, "index_path": *output,
        "format": index.Format, "node_count": len(index.Nodes), "edge_count": len(index.Edges),
        "input_truncated": index.InputTruncated, "input_errors": index.InputErrors,
    })
    return 0
}

// cmdStructureIndexQuery は対象サブコマンドの引数解析・境界I/O・compact出力を統括します。
func cmdStructureIndexQuery(args []string) int {
    fs := flag.NewFlagSet("structure-index query", flag.ContinueOnError)
    fs.SetOutput(io.Discard)
    maxResults := fs.Int("max-results", 40, "maximum matches; 0 means unlimited")
    if err := fs.Parse(args); err != nil || fs.NArg() < 2 {
        text := "index and pattern are required"
        if err != nil { text = err.Error() }
        emitStructureJSON(map[string]any{"tool": "source-structure-index", "status": "invalid_arguments", "error": text})
        return 2
    }
    indexPath, pattern := fs.Arg(0), fs.Arg(1)
    index, err := readStructureIndex(indexPath)
    if err != nil {
        emitStructureJSON(map[string]any{"tool": "source-structure-index", "status": "index_read_failed", "index_path": indexPath, "error": err.Error()})
        return 2
    }
    limit := *maxResults
    if limit < 0 { limit = 0 }
    matches, truncated := queryStructureNodes(index, pattern, limit)
    emitStructureJSON(map[string]any{
        "tool": "source-structure-index", "status": "ok", "index_path": indexPath,
        "pattern": pattern, "matches": matches, "matches_truncated": truncated,
        "index_input_truncated": index.InputTruncated,
    })
    return 0
}

// cmdStructureIndexExpand は対象サブコマンドの引数解析・境界I/O・compact出力を統括します。
func cmdStructureIndexExpand(args []string) int {
    fs := flag.NewFlagSet("structure-index expand", flag.ContinueOnError)
    fs.SetOutput(io.Discard)
    depth := fs.Int("depth", 1, "graph traversal depth")
    maxNodes := fs.Int("max-nodes", 80, "maximum nodes; 0 means unlimited")
    direction := fs.String("direction", "both", "in, out, or both")
    maxCandidates := fs.Int("max-candidates", 20, "maximum ambiguous target candidates")
    if err := fs.Parse(args); err != nil || fs.NArg() < 2 {
        text := "index and target are required"
        if err != nil { text = err.Error() }
        emitStructureJSON(map[string]any{"tool": "source-structure-index", "status": "invalid_arguments", "error": text})
        return 2
    }
    if *direction != "in" && *direction != "out" && *direction != "both" {
        emitStructureJSON(map[string]any{"tool": "source-structure-index", "status": "invalid_arguments", "error": "direction must be in, out, or both"})
        return 2
    }
    indexPath, target := fs.Arg(0), fs.Arg(1)
    index, err := readStructureIndex(indexPath)
    if err != nil {
        emitStructureJSON(map[string]any{"tool": "source-structure-index", "status": "index_read_failed", "index_path": indexPath, "error": err.Error()})
        return 2
    }
    status, matches := resolveStructureTarget(index, target)
    if status != "ok" {
        limit := *maxCandidates
        if limit < 1 { limit = 1 }
        truncated := len(matches) > limit
        if truncated { matches = matches[:limit] }
        emitStructureJSON(map[string]any{
            "tool": "source-structure-index", "status": status, "index_path": indexPath,
            "target": target, "candidate_matches": matches, "candidate_matches_truncated": truncated,
            "index_input_truncated": index.InputTruncated,
        })
        if status == "target_not_found" { return 1 }
        return 2
    }
    depthValue, maxNodesValue := *depth, *maxNodes
    if depthValue < 0 { depthValue = 0 }
    if maxNodesValue < 0 { maxNodesValue = 0 }
    result := expandStructure(index, matches[0].ID, depthValue, maxNodesValue, *direction)
    result["tool"] = "source-structure-index"
    result["status"] = "ok"
    result["index_path"] = indexPath
    result["target"] = target
    result["index_input_truncated"] = index.InputTruncated
    emitStructureJSON(result)
    return 0
}

// cmdStructureIndex は対象サブコマンドの引数解析・境界I/O・compact出力を統括します。
func cmdStructureIndex(args []string) int {
    if len(args) == 0 {
        emitStructureJSON(map[string]any{"tool": "source-structure-index", "status": "missing_command", "commands": []string{"build", "query", "expand"}})
        return 2
    }
    switch args[0] {
    case "build":
        return cmdStructureIndexBuild(args[1:])
    case "query":
        return cmdStructureIndexQuery(args[1:])
    case "expand":
        return cmdStructureIndexExpand(args[1:])
    default:
        emitStructureJSON(map[string]any{"tool": "source-structure-index", "status": "unknown_command", "command": args[0], "commands": []string{"build", "query", "expand"}})
        return 2
    }
}
