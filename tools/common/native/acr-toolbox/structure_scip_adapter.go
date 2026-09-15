package main

import (
    "encoding/json"
    "fmt"
    "os"
    "os/exec"
    "path/filepath"
    "strings"
)

const structureSCIPErrorLimit = 2000

type structureSCIPFailure struct {
    Status string
    Path   string
    Error  string
}

func boundedSCIPError(text string) string {
    text = strings.TrimSpace(text)
    if len(text) <= structureSCIPErrorLimit {
        return text
    }
    return text[:structureSCIPErrorLimit] + "... truncated"
}

func scipMapField(row map[string]any, camel, snake string) any {
    if value, ok := row[camel]; ok {
        return value
    }
    return row[snake]
}

func scipRoles(row map[string]any) int {
    return structureInt(scipMapField(row, "symbolRoles", "symbol_roles"))
}

func scipRangeLines(raw any) (int, int) {
    values, ok := raw.([]any)
    if !ok || (len(values) != 3 && len(values) != 4) {
        return 0, 0
    }
    start := structureInt(values[0]) + 1
    end := start
    if len(values) == 4 {
        end = structureInt(values[2]) + 1
    }
    return start, end
}

func normalizeSCIPPrint(raw any) ([]any, map[string]any, error) {
    payload, ok := raw.(map[string]any)
    if !ok {
        return nil, nil, fmt.Errorf("SCIP print JSON must be an object")
    }
    documents, ok := payload["documents"].([]any)
    if !ok {
        return nil, nil, fmt.Errorf("SCIP print JSON is missing documents[]")
    }

    symbolDocuments := map[string]string{}
    definitionLines := map[string][2]int{}
    docRows := []struct {
        Path string
        Raw  map[string]any
    }{}

    for _, rawDocument := range documents {
        document, ok := rawDocument.(map[string]any)
        if !ok {
            continue
        }
        path := structureString(scipMapField(document, "relativePath", "relative_path"))
        if path == "" {
            continue
        }
        path = filepath.ToSlash(path)
        docRows = append(docRows, struct {
            Path string
            Raw  map[string]any
        }{Path: path, Raw: document})

        symbols, _ := document["symbols"].([]any)
        for _, rawSymbol := range symbols {
            symbol, ok := rawSymbol.(map[string]any)
            if !ok {
                continue
            }
            qualified := structureString(symbol["symbol"])
            if qualified != "" {
                symbolDocuments[qualified] = path
            }
        }
        occurrences, _ := document["occurrences"].([]any)
        for _, rawOccurrence := range occurrences {
            occurrence, ok := rawOccurrence.(map[string]any)
            if !ok || scipRoles(occurrence)&0x1 == 0 {
                continue
            }
            qualified := structureString(occurrence["symbol"])
            if qualified == "" {
                continue
            }
            if _, exists := definitionLines[qualified]; !exists {
                start, end := scipRangeLines(occurrence["range"])
                definitionLines[qualified] = [2]int{start, end}
            }
        }
    }

    symbolRows := []any{}
    nodes := map[string]map[string]any{}
    edgeRows := map[string]map[string]any{}
    addEdge := func(from, to, kind string) {
        key := from + "\x00" + to + "\x00" + kind
        edgeRows[key] = map[string]any{"from": from, "to": to, "kind": kind}
    }

    for _, doc := range docRows {
        fileID := "file:" + doc.Path
        moduleID := "module:scip:" + doc.Path
        nodes[moduleID] = map[string]any{
            "id": moduleID, "kind": "module", "name": doc.Path, "source_kind": "scip_document",
        }
        addEdge(moduleID, fileID, "contains_file")

        symbolsOut := []any{}
        symbols, _ := doc.Raw["symbols"].([]any)
        for _, rawSymbol := range symbols {
            symbol, ok := rawSymbol.(map[string]any)
            if !ok {
                continue
            }
            qualified := structureString(symbol["symbol"])
            if qualified == "" {
                continue
            }
            name := structureString(scipMapField(symbol, "displayName", "display_name"))
            if name == "" {
                name = qualified
            }
            kind := "unknown"
            if rawKind, exists := symbol["kind"]; exists && rawKind != nil {
                text := fmt.Sprint(rawKind)
                if text != "" && text != "<nil>" {
                    kind = text
                }
            }
            item := map[string]any{
                "name":           name,
                "qualified_name": qualified,
                "kind":           kind,
            }
            if language := structureString(doc.Raw["language"]); language != "" {
                item["language"] = language
            }
            if line := definitionLines[qualified]; line[0] > 0 {
                item["line"] = line[0]
                item["end_line"] = line[1]
            }
            if owner := structureString(scipMapField(symbol, "enclosingSymbol", "enclosing_symbol")); owner != "" {
                item["owner_qualified_name"] = owner
            }
            if signature, ok := scipMapField(symbol, "signatureDocumentation", "signature_documentation").(map[string]any); ok {
                if text := structureString(signature["text"]); text != "" {
                    item["signature"] = text
                }
            }
            symbolsOut = append(symbolsOut, item)

            relationships, _ := symbol["relationships"].([]any)
            for _, rawRelationship := range relationships {
                relationship, ok := rawRelationship.(map[string]any)
                if !ok {
                    continue
                }
                targetPath := symbolDocuments[structureString(relationship["symbol"])]
                if targetPath != "" && targetPath != doc.Path {
                    addEdge(moduleID, "module:scip:"+targetPath, "depends_on")
                }
            }
        }
        symbolRows = append(symbolRows, map[string]any{"file": doc.Path, "symbols": symbolsOut})

        occurrences, _ := doc.Raw["occurrences"].([]any)
        for _, rawOccurrence := range occurrences {
            occurrence, ok := rawOccurrence.(map[string]any)
            if !ok || scipRoles(occurrence)&0x1 != 0 {
                continue
            }
            targetPath := symbolDocuments[structureString(occurrence["symbol"])]
            if targetPath != "" && targetPath != doc.Path {
                addEdge(moduleID, "module:scip:"+targetPath, "depends_on")
            }
        }
    }

    nodeList := []any{}
    for _, node := range nodes {
        nodeList = append(nodeList, node)
    }
    edgeList := []any{}
    for _, edge := range edgeRows {
        edgeList = append(edgeList, edge)
    }
    graph := map[string]any{
        "nodes":         nodeList,
        "edges":         edgeList,
        "truncated":     false,
        "source_format": "scip-print-json",
    }
    return symbolRows, graph, nil
}

func loadSCIPPrintJSON(path string, invokeCLI bool) (any, *structureSCIPFailure) {
    if !invokeCLI {
        raw, err := loadStructureRaw(path)
        if err != nil {
            return nil, &structureSCIPFailure{Status: "read_failed", Path: path, Error: boundedSCIPError(err.Error())}
        }
        return raw, nil
    }

    executable, err := exec.LookPath("scip")
    if err != nil {
        return nil, &structureSCIPFailure{
            Status: "backend_unavailable", Path: path, Error: "scip executable was not found on PATH",
        }
    }
    output, err := exec.Command(executable, "print", "--json", path).CombinedOutput()
    if err != nil {
        return nil, &structureSCIPFailure{Status: "command_failed", Path: path, Error: boundedSCIPError(string(output))}
    }
    var raw any
    if err := json.Unmarshal(output, &raw); err != nil {
        return nil, &structureSCIPFailure{Status: "invalid_backend_output", Path: path, Error: boundedSCIPError(err.Error())}
    }
    return raw, nil
}

func writeSCIPAdapterJSON(path string, payload any) error {
    data, err := json.Marshal(payload)
    if err != nil {
        return err
    }
    return os.WriteFile(path, data, 0o644)
}

func prepareStructureSCIPBuildArgs(args []string) ([]string, func(), *structureSCIPFailure) {
    remaining := []string{}
    scipIndexes := []string{}
    scipJSON := []string{}

    for i := 0; i < len(args); i++ {
        arg := args[i]
        switch {
        case arg == "--scip" || arg == "--scip-json":
            if i+1 >= len(args) {
                return nil, func() {}, &structureSCIPFailure{Status: "invalid_arguments", Error: arg + " requires a path"}
            }
            i++
            if arg == "--scip" {
                scipIndexes = append(scipIndexes, args[i])
            } else {
                scipJSON = append(scipJSON, args[i])
            }
        case strings.HasPrefix(arg, "--scip="):
            scipIndexes = append(scipIndexes, strings.TrimPrefix(arg, "--scip="))
        case strings.HasPrefix(arg, "--scip-json="):
            scipJSON = append(scipJSON, strings.TrimPrefix(arg, "--scip-json="))
        default:
            remaining = append(remaining, arg)
        }
    }

    if len(scipIndexes) == 0 && len(scipJSON) == 0 {
        return args, func() {}, nil
    }

    tempDir, err := os.MkdirTemp("", "acr-scip-*")
    if err != nil {
        return nil, func() {}, &structureSCIPFailure{Status: "adapter_failed", Error: boundedSCIPError(err.Error())}
    }
    cleanup := func() { _ = os.RemoveAll(tempDir) }

    inputs := []struct {
        Path      string
        InvokeCLI bool
    }{}
    for _, path := range scipJSON {
        inputs = append(inputs, struct {
            Path      string
            InvokeCLI bool
        }{Path: path})
    }
    for _, path := range scipIndexes {
        inputs = append(inputs, struct {
            Path      string
            InvokeCLI bool
        }{Path: path, InvokeCLI: true})
    }

    for i, input := range inputs {
        raw, failure := loadSCIPPrintJSON(input.Path, input.InvokeCLI)
        if failure != nil {
            cleanup()
            return nil, func() {}, failure
        }
        symbols, graph, err := normalizeSCIPPrint(raw)
        if err != nil {
            cleanup()
            return nil, func() {}, &structureSCIPFailure{Status: "invalid_backend_output", Path: input.Path, Error: boundedSCIPError(err.Error())}
        }
        symbolPath := filepath.Join(tempDir, fmt.Sprintf("symbols-%d.json", i))
        graphPath := filepath.Join(tempDir, fmt.Sprintf("graph-%d.json", i))
        if err := writeSCIPAdapterJSON(symbolPath, symbols); err != nil {
            cleanup()
            return nil, func() {}, &structureSCIPFailure{Status: "adapter_failed", Path: input.Path, Error: boundedSCIPError(err.Error())}
        }
        if err := writeSCIPAdapterJSON(graphPath, graph); err != nil {
            cleanup()
            return nil, func() {}, &structureSCIPFailure{Status: "adapter_failed", Path: input.Path, Error: boundedSCIPError(err.Error())}
        }
        remaining = append(remaining, "--symbols", symbolPath, "--graph", graphPath)
    }
    return remaining, cleanup, nil
}
