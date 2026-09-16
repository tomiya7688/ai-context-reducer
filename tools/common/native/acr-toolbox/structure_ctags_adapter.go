package main

import (
    "bufio"
    "bytes"
    "encoding/json"
    "fmt"
    "os"
    "os/exec"
    "path/filepath"
    "strings"
)

const structureCtagsErrorLimit = 1200

type structureCtagsFailure struct {
    Status string
    Path   string
    Error  string
}

func boundedCtagsError(text string) string {
    text = strings.TrimSpace(text)
    if len(text) <= structureCtagsErrorLimit {
        return text
    }
    return text[:structureCtagsErrorLimit] + "... truncated"
}

func parseCtagsJSONLines(data []byte) ([]any, error) {
    scanner := bufio.NewScanner(bytes.NewReader(data))
    scanner.Buffer(make([]byte, 64*1024), 8*1024*1024)
    rows := []any{}
    line := 0
    for scanner.Scan() {
        line++
        text := strings.TrimSpace(scanner.Text())
        if text == "" {
            continue
        }
        var row any
        if err := json.Unmarshal([]byte(text), &row); err != nil {
            return nil, fmt.Errorf("invalid JSON line %d: %w", line, err)
        }
        rows = append(rows, row)
    }
    if err := scanner.Err(); err != nil {
        return nil, err
    }
    return rows, nil
}

func ctagsQualified(path, scope, name string) string {
    if scope != "" {
        return path + "::" + scope + "::" + name
    }
    return path + "::" + name
}

func normalizeCtagsRows(raw any) (map[string]any, map[string]any, map[string]any, error) {
    rows, ok := raw.([]any)
    if !ok {
        return nil, nil, nil, fmt.Errorf("ctags JSON input must be JSON Lines tag rows")
    }

    files := map[string][]any{}
    graphNodes := map[string]map[string]any{}
    graphEdges := map[string]map[string]any{}
    tagCount := 0
    skipped := 0
    languages := map[string]bool{}

    for _, rawRow := range rows {
        row, ok := rawRow.(map[string]any)
        if !ok {
            skipped++
            continue
        }
        if rowType := structureString(row["_type"]); rowType != "" && rowType != "tag" {
            continue
        }
        name := structureString(row["name"])
        path := structureString(row["path"])
        if path == "" {
            path = structureString(row["input"])
        }
        if name == "" || path == "" {
            skipped++
            continue
        }
        path = filepath.ToSlash(path)
        scope := structureString(row["scope"])
        qualified := ctagsQualified(path, scope, name)
        kind := structureString(row["kind"])
        if kind == "" {
            kind = "unknown"
        }
        line := structureInt(row["line"])
        endLine := structureInt(row["end"])
        if language := structureString(row["language"]); language != "" {
            languages[language] = true
        }

        if _, exists := files[path]; !exists {
            files[path] = []any{}
        }
        if scope == "" {
            symbol := map[string]any{
                "name": name, "qualified_name": qualified, "kind": kind,
            }
            if line > 0 {
                symbol["line"] = line
            }
            if endLine > 0 {
                symbol["end_line"] = endLine
            }
            files[path] = append(files[path], symbol)
        } else {
            symbolID := "symbol:" + qualified
            node := map[string]any{
                "id": symbolID, "kind": "symbol", "name": name,
                "qualified_name": qualified, "path": path, "symbol_kind": kind,
            }
            if line > 0 {
                node["line"] = line
            }
            if endLine > 0 {
                node["end_line"] = endLine
            }
            graphNodes[symbolID] = node
            ownerID := "symbol:" + path + "::" + scope
            key := ownerID + "\x00" + symbolID + "\x00owns"
            graphEdges[key] = map[string]any{"from": ownerID, "to": symbolID, "kind": "owns"}
        }
        tagCount++
    }

    fileRows := []any{}
    paths := make([]string, 0, len(files))
    for path := range files {
        paths = append(paths, path)
    }
    sortStrings(paths)
    for _, path := range paths {
        fileRows = append(fileRows, map[string]any{"file": path, "symbols": files[path]})
    }
    nodeRows := []any{}
    for _, node := range graphNodes {
        nodeRows = append(nodeRows, node)
    }
    edgeRows := []any{}
    for _, edge := range graphEdges {
        edgeRows = append(edgeRows, edge)
    }
    languageRows := make([]string, 0, len(languages))
    for language := range languages {
        languageRows = append(languageRows, language)
    }
    sortStrings(languageRows)

    symbols := map[string]any{
        "files": fileRows, "input_adapter": "universal-ctags-json", "truncated": false,
    }
    graph := map[string]any{
        "nodes": nodeRows, "edges": edgeRows, "source_format": "universal-ctags-json", "truncated": false,
    }
    metadata := map[string]any{
        "tag_count": tagCount, "file_count": len(fileRows), "skipped_row_count": skipped, "languages": languageRows,
    }
    return symbols, graph, metadata, nil
}

func sortStrings(values []string) {
    for i := 1; i < len(values); i++ {
        value := values[i]
        j := i - 1
        for j >= 0 && values[j] > value {
            values[j+1] = values[j]
            j--
        }
        values[j+1] = value
    }
}

func loadCtagsRows(path string, invokeCLI bool) ([]any, *structureCtagsFailure) {
    if !invokeCLI {
        data, err := os.ReadFile(path)
        if err != nil {
            return nil, &structureCtagsFailure{Status: "read_failed", Path: path, Error: boundedCtagsError(err.Error())}
        }
        rows, err := parseCtagsJSONLines(data)
        if err != nil {
            return nil, &structureCtagsFailure{Status: "invalid_backend_output", Path: path, Error: boundedCtagsError(err.Error())}
        }
        return rows, nil
    }

    executable, err := exec.LookPath("ctags")
    if err != nil {
        return nil, &structureCtagsFailure{Status: "backend_unavailable", Path: path, Error: "ctags executable was not found on PATH"}
    }
    probe, err := exec.Command(executable, "--list-output-formats").CombinedOutput()
    supported := false
    for _, token := range strings.Fields(strings.ToLower(string(probe))) {
        if token == "json" {
            supported = true
            break
        }
    }
    if err != nil || !supported {
        return nil, &structureCtagsFailure{Status: "backend_incompatible", Path: path, Error: "installed ctags does not advertise Universal Ctags JSON output support"}
    }

    command := []string{"--output-format=json", "--fields=+nSlesp", "--recurse=yes", "-o", "-"}
    for _, name := range []string{".git", ".hg", ".svn", ".venv", "venv", "node_modules", "__pycache__", "bin", "obj", "build", "dist", ".godot", ".idea", ".vs", "vendor", "generated"} {
        command = append(command, "--exclude="+name)
    }
    command = append(command, path)
    cmd := exec.Command(executable, command...)
    var stdout, stderr bytes.Buffer
    cmd.Stdout = &stdout
    cmd.Stderr = &stderr
    if err := cmd.Run(); err != nil {
        return nil, &structureCtagsFailure{Status: "command_failed", Path: path, Error: boundedCtagsError(stderr.String())}
    }
    rows, err := parseCtagsJSONLines(stdout.Bytes())
    if err != nil {
        return nil, &structureCtagsFailure{Status: "invalid_backend_output", Path: path, Error: boundedCtagsError(err.Error())}
    }
    return rows, nil
}

func writeCtagsAdapterJSON(path string, payload any) error {
    data, err := json.Marshal(payload)
    if err != nil {
        return err
    }
    return os.WriteFile(path, data, 0o644)
}

func prepareStructureCtagsBuildArgs(args []string) ([]string, func(), *structureCtagsFailure) {
    remaining := []string{}
    sources := []string{}
    jsonFiles := []string{}
    for i := 0; i < len(args); i++ {
        arg := args[i]
        switch {
        case arg == "--ctags-source" || arg == "--ctags-json":
            if i+1 >= len(args) {
                return nil, func() {}, &structureCtagsFailure{Status: "invalid_arguments", Error: arg + " requires a path"}
            }
            i++
            if arg == "--ctags-source" {
                sources = append(sources, args[i])
            } else {
                jsonFiles = append(jsonFiles, args[i])
            }
        case strings.HasPrefix(arg, "--ctags-source="):
            sources = append(sources, strings.TrimPrefix(arg, "--ctags-source="))
        case strings.HasPrefix(arg, "--ctags-json="):
            jsonFiles = append(jsonFiles, strings.TrimPrefix(arg, "--ctags-json="))
        default:
            remaining = append(remaining, arg)
        }
    }
    if len(sources) == 0 && len(jsonFiles) == 0 {
        return args, func() {}, nil
    }

    tempDir, err := os.MkdirTemp("", "acr-ctags-*")
    if err != nil {
        return nil, func() {}, &structureCtagsFailure{Status: "adapter_failed", Error: boundedCtagsError(err.Error())}
    }
    cleanup := func() { _ = os.RemoveAll(tempDir) }

    inputs := []struct {
        Path      string
        InvokeCLI bool
    }{}
    for _, path := range jsonFiles {
        inputs = append(inputs, struct {
            Path      string
            InvokeCLI bool
        }{Path: path})
    }
    for _, path := range sources {
        inputs = append(inputs, struct {
            Path      string
            InvokeCLI bool
        }{Path: path, InvokeCLI: true})
    }

    for i, input := range inputs {
        rows, failure := loadCtagsRows(input.Path, input.InvokeCLI)
        if failure != nil {
            cleanup()
            return nil, func() {}, failure
        }
        symbols, graph, _, err := normalizeCtagsRows(rows)
        if err != nil {
            cleanup()
            return nil, func() {}, &structureCtagsFailure{Status: "invalid_backend_output", Path: input.Path, Error: boundedCtagsError(err.Error())}
        }
        symbolPath := filepath.Join(tempDir, fmt.Sprintf("symbols-%d.json", i))
        graphPath := filepath.Join(tempDir, fmt.Sprintf("graph-%d.json", i))
        if err := writeCtagsAdapterJSON(symbolPath, symbols); err != nil {
            cleanup()
            return nil, func() {}, &structureCtagsFailure{Status: "adapter_failed", Path: input.Path, Error: boundedCtagsError(err.Error())}
        }
        if err := writeCtagsAdapterJSON(graphPath, graph); err != nil {
            cleanup()
            return nil, func() {}, &structureCtagsFailure{Status: "adapter_failed", Path: input.Path, Error: boundedCtagsError(err.Error())}
        }
        remaining = append(remaining, "--symbols", symbolPath, "--graph", graphPath)
    }
    return remaining, cleanup, nil
}
