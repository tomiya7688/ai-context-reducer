package main

import (
    "encoding/json"
    "flag"
    "io"
    "io/fs"
    "os"
    "path/filepath"
    "sort"
    "strings"
)

var duplicateDocExts = map[string]bool{".md": true, ".txt": true, ".rst": true}

type nativeDocumentDiscovery struct {
    Paths          []string
    WalkErrorCount int
}

func emitDocDuplicateJSON(value any) {
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    _ = enc.Encode(value)
}

func discoverNativeDocuments(root string) nativeDocumentDiscovery {
    result := nativeDocumentDiscovery{Paths: []string{}}
    _ = filepath.WalkDir(root, func(path string, entry fs.DirEntry, visitErr error) error {
        if visitErr != nil {
            result.WalkErrorCount++
            return nil
        }
        if entry.IsDir() {
            if path != root && (ignoreDirs[strings.ToLower(entry.Name())] || strings.EqualFold(entry.Name(), "generated")) {
                return filepath.SkipDir
            }
            return nil
        }
        if duplicateDocExts[strings.ToLower(filepath.Ext(path))] {
            result.Paths = append(result.Paths, path)
        }
        return nil
    })
    sort.Strings(result.Paths)
    return result
}

func readDocumentLines(path string) ([]string, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, err
    }
    text := strings.ReplaceAll(string(data), "\r\n", "\n")
    text = strings.ReplaceAll(text, "\r", "\n")
    return strings.Split(text, "\n"), nil
}

func cmdDocDuplicateHints(args []string) int {
    flags := flag.NewFlagSet("doc-duplicate-hints", flag.ContinueOnError)
    flags.SetOutput(io.Discard)
    minChars := flags.Int("min-chars", 50, "minimum normalized line length")
    maxGroups := flags.Int("max-groups", 80, "maximum duplicate groups returned; 0 means unlimited")
    maxOccurrences := flags.Int("max-occurrences-per-group", 10, "maximum occurrences returned per group; 0 means unlimited")
    if err := flags.Parse(args); err != nil {
        emitDocDuplicateJSON(map[string]any{"tool": "doc-duplicate-hints", "status": "invalid_arguments", "error": err.Error()})
        return 2
    }
    root := "."
    if flags.NArg() > 0 {
        root = flags.Arg(0)
    }
    if flags.NArg() > 1 {
        emitDocDuplicateJSON(map[string]any{"tool": "doc-duplicate-hints", "status": "invalid_arguments", "error": "expected at most one root path"})
        return 2
    }
    absoluteRoot, err := filepath.Abs(root)
    if err == nil {
        root = absoluteRoot
    }
    info, err := os.Stat(root)
    if err != nil {
        status := "input_unavailable"
        if os.IsNotExist(err) {
            status = "input_missing"
        }
        emitDocDuplicateJSON(map[string]any{"tool": "doc-duplicate-hints", "status": status, "root_path": root})
        return 2
    }
    if !info.IsDir() {
        emitDocDuplicateJSON(map[string]any{"tool": "doc-duplicate-hints", "status": "input_not_directory", "root_path": root})
        return 2
    }

    discovery := discoverNativeDocuments(root)
    documents := []docDuplicateDocument{}
    readErrors := []string{}
    for _, path := range discovery.Paths {
        lines, readErr := readDocumentLines(path)
        relative, relErr := filepath.Rel(root, path)
        if relErr != nil {
            relative = path
        }
        relative = filepath.ToSlash(relative)
        if readErr != nil {
            readErrors = append(readErrors, relative)
            continue
        }
        documents = append(documents, docDuplicateDocument{Path: relative, Lines: lines})
    }
    groups := collectNativeDocumentDuplicates(documents, *minChars)

    groupLimit := *maxGroups
    if groupLimit < 0 {
        groupLimit = 0
    }
    occurrenceLimit := *maxOccurrences
    if occurrenceLimit < 0 {
        occurrenceLimit = 0
    }
    selected := groups
    if groupLimit > 0 && len(selected) > groupLimit {
        selected = selected[:groupLimit]
    }

    outputGroups := make([]map[string]any, 0, len(selected))
    for _, group := range selected {
        returned := group.Occurrences
        if occurrenceLimit > 0 && len(returned) > occurrenceLimit {
            returned = returned[:occurrenceLimit]
        }
        outputGroups = append(outputGroups, map[string]any{
            "repeated_text": group.RepeatedText,
            "occurrence_count_total": len(group.Occurrences),
            "occurrences": returned,
            "occurrences_truncated": len(returned) < len(group.Occurrences),
        })
    }

    status := "ok"
    if len(readErrors) > 0 || discovery.WalkErrorCount > 0 {
        status = "partial"
    }
    emitDocDuplicateJSON(map[string]any{
        "tool": "doc-duplicate-hints",
        "status": status,
        "root_path": root,
        "discovered_documents": len(discovery.Paths),
        "scanned_documents": len(documents),
        "duplicate_group_count_total": len(groups),
        "duplicate_groups": outputGroups,
        "duplicate_groups_truncated": len(outputGroups) < len(groups),
        "read_error_paths": readErrors,
        "walk_error_count": discovery.WalkErrorCount,
    })
    return 0
}
