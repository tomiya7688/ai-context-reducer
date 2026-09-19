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

var policyDocExts = map[string]bool{".md": true, ".txt": true, ".rst": true}

type policyDiscovery struct {
    Files            []string
    MissingInputs    []string
    UnsupportedInputs []string
    WalkErrorCount   int
}

// emitPolicyIndexJSON は内部結果を安定した利用者向け出力へ変換します。
func emitPolicyIndexJSON(value any) {
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    _ = enc.Encode(value)
}

// discoverNativePolicyFiles はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func discoverNativePolicyFiles(inputs []string) policyDiscovery {
    result := policyDiscovery{Files: []string{}, MissingInputs: []string{}, UnsupportedInputs: []string{}}
    seen := map[string]bool{}
    addFile := func(path string) {
        if !policyDocExts[strings.ToLower(filepath.Ext(path))] {
            return
        }
        absolute, err := filepath.Abs(path)
        if err != nil {
            absolute = filepath.Clean(path)
        }
        key := filepath.Clean(absolute)
        if seen[key] {
            return
        }
        seen[key] = true
        result.Files = append(result.Files, path)
    }

    for _, input := range inputs {
        info, err := os.Stat(input)
        if err != nil {
            if os.IsNotExist(err) {
                result.MissingInputs = append(result.MissingInputs, input)
            } else {
                result.UnsupportedInputs = append(result.UnsupportedInputs, input)
            }
            continue
        }
        if !info.IsDir() {
            if info.Mode().IsRegular() && policyDocExts[strings.ToLower(filepath.Ext(input))] {
                addFile(input)
            } else {
                result.UnsupportedInputs = append(result.UnsupportedInputs, input)
            }
            continue
        }

        _ = filepath.WalkDir(input, func(path string, entry fs.DirEntry, visitErr error) error {
            if visitErr != nil {
                result.WalkErrorCount++
                return nil
            }
            if entry.IsDir() {
                if path != input && ignoreDirs[strings.ToLower(entry.Name())] {
                    return filepath.SkipDir
                }
                if strings.EqualFold(entry.Name(), "generated") && path != input {
                    return filepath.SkipDir
                }
                return nil
            }
            addFile(path)
            return nil
        })
    }
    sort.Strings(result.Files)
    return result
}

// readNativePolicyLines は入力元から必要情報だけを読み込み、後段が扱える形へ整えます。
func readNativePolicyLines(path string) ([]string, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, err
    }
    text := strings.ReplaceAll(string(data), "\r\n", "\n")
    text = strings.ReplaceAll(text, "\r", "\n")
    return strings.Split(text, "\n"), nil
}

// cmdPolicyIndex は対象サブコマンドの引数解析・境界I/O・compact出力を統括します。
func cmdPolicyIndex(args []string) int {
    flags := flag.NewFlagSet("policy-index", flag.ContinueOnError)
    flags.SetOutput(io.Discard)
    maxFindings := flags.Int("max-findings", 120, "maximum findings returned; 0 means unlimited")
    if err := flags.Parse(args); err != nil {
        emitPolicyIndexJSON(map[string]any{"tool": "policy-index", "status": "invalid_arguments", "error": err.Error()})
        return 2
    }
    if flags.NArg() == 0 {
        emitPolicyIndexJSON(map[string]any{"tool": "policy-index", "status": "invalid_arguments", "required_argument": "one or more policy file/directory paths"})
        return 2
    }

    discovery := discoverNativePolicyFiles(flags.Args())
    allFindings := []policyFinding{}
    readErrors := []string{}
    scannedFiles := 0
    for _, path := range discovery.Files {
        lines, err := readNativePolicyLines(path)
        if err != nil {
            readErrors = append(readErrors, path)
            continue
        }
        scannedFiles++
        allFindings = append(allFindings, nativePolicyFindings(path, lines)...)
    }

    limit := *maxFindings
    if limit < 0 {
        limit = 0
    }
    returned := allFindings
    if limit > 0 && len(returned) > limit {
        returned = returned[:limit]
    }
    warnings := len(discovery.MissingInputs)+len(discovery.UnsupportedInputs)+len(readErrors)+discovery.WalkErrorCount > 0
    status := "ok"
    if len(discovery.Files) == 0 && len(discovery.MissingInputs) > 0 {
        status = "input_unavailable"
    } else if len(discovery.Files) == 0 {
        status = "no_policy_documents"
    } else if warnings {
        status = "partial"
    }

    emitPolicyIndexJSON(map[string]any{
        "tool": "policy-index",
        "status": status,
        "discovered_policy_files": len(discovery.Files),
        "scanned_policy_files": scannedFiles,
        "finding_count_total": len(allFindings),
        "findings": returned,
        "findings_truncated": len(returned) < len(allFindings),
        "missing_inputs": discovery.MissingInputs,
        "unsupported_inputs": discovery.UnsupportedInputs,
        "read_error_paths": readErrors,
        "walk_error_count": discovery.WalkErrorCount,
    })
    if status == "input_unavailable" {
        return 2
    }
    return 0
}
