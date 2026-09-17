package main

import (
    "bytes"
    "encoding/json"
    "flag"
    "io"
    "os"
    "os/exec"
    "path/filepath"
    "sort"
    "strings"
)

type gitHealthFinding struct {
    Metric            string  `json:"metric"`
    Value             float64 `json:"value"`
    LevelOfConcern    float64 `json:"level_of_concern"`
    Unit              string  `json:"unit,omitempty"`
    Description       string  `json:"description,omitempty"`
    ObjectDescription string  `json:"object_description,omitempty"`
}

func boundedGitHealthError(text string) string {
    text = strings.TrimSpace(text)
    if len(text) <= 1200 {
        return text
    }
    return text[:1200]
}

func emitGitHealthJSON(value any) {
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    _ = enc.Encode(value)
}

func numberValue(value any) (float64, bool) {
    switch typed := value.(type) {
    case float64:
        return typed, true
    case int:
        return float64(typed), true
    case int64:
        return float64(typed), true
    case json.Number:
        n, err := typed.Float64()
        return n, err == nil
    default:
        return 0, false
    }
}

func collectGitSizerMetrics(node any, prefix string, out *[]gitHealthFinding) {
    switch typed := node.(type) {
    case map[string]any:
        level, hasLevel := numberValue(typed["levelOfConcern"])
        value, hasValue := numberValue(typed["value"])
        if hasLevel && hasValue {
            metric := prefix
            if metric == "" {
                metric = "unknown"
            }
            item := gitHealthFinding{Metric: metric, Value: value, LevelOfConcern: level}
            if text, ok := typed["unit"].(string); ok {
                item.Unit = text
            }
            if text, ok := typed["description"].(string); ok {
                item.Description = text
            }
            if text, ok := typed["objectDescription"].(string); ok {
                item.ObjectDescription = text
            }
            *out = append(*out, item)
        }
        skip := map[string]bool{
            "value": true, "levelOfConcern": true, "unit": true, "description": true,
            "referenceValue": true, "prefixes": true, "objectName": true, "objectDescription": true,
        }
        keys := make([]string, 0, len(typed))
        for key := range typed {
            if !skip[key] {
                keys = append(keys, key)
            }
        }
        sort.Strings(keys)
        for _, key := range keys {
            child := key
            if prefix != "" {
                child = prefix + "." + key
            }
            collectGitSizerMetrics(typed[key], child, out)
        }
    case []any:
        for index, value := range typed {
            child := "[" + intString(index) + "]"
            if prefix != "" {
                child = prefix + child
            }
            collectGitSizerMetrics(value, child, out)
        }
    }
}

func summarizeGitSizer(payload any, minConcern float64, maxFindings int) map[string]any {
    metrics := []gitHealthFinding{}
    collectGitSizerMetrics(payload, "", &metrics)
    findings := []gitHealthFinding{}
    for _, item := range metrics {
        if item.LevelOfConcern >= minConcern {
            findings = append(findings, item)
        }
    }
    sort.Slice(findings, func(i, j int) bool {
        if findings[i].LevelOfConcern != findings[j].LevelOfConcern {
            return findings[i].LevelOfConcern > findings[j].LevelOfConcern
        }
        return findings[i].Metric < findings[j].Metric
    })
    limit := maxFindings
    if limit < 0 {
        limit = 0
    }
    truncated := limit > 0 && len(findings) > limit
    returned := findings
    if truncated {
        returned = findings[:limit]
    }
    return map[string]any{
        "metric_count_total": len(metrics),
        "concern_count_total": len(findings),
        "min_level_of_concern": minConcern,
        "findings": returned,
        "findings_truncated": truncated,
    }
}

func loadGitSizerJSON(root, jsonInput string) (any, string, string) {
    var data []byte
    if jsonInput != "" {
        path, err := filepath.Abs(jsonInput)
        if err != nil {
            return nil, "input_invalid", boundedGitHealthError(err.Error())
        }
        content, err := os.ReadFile(path)
        if err != nil {
            if os.IsNotExist(err) {
                return nil, "input_missing", ""
            }
            return nil, "input_invalid", boundedGitHealthError(err.Error())
        }
        data = content
    } else {
        executable, err := exec.LookPath("git-sizer")
        if err != nil {
            return nil, "external_backend_unavailable", ""
        }
        cmd := exec.Command(executable, "--json", "--json-version=2", "--no-progress")
        cmd.Dir = root
        var stderr bytes.Buffer
        cmd.Stderr = &stderr
        output, err := cmd.Output()
        if err != nil {
            message := stderr.String()
            if strings.TrimSpace(message) == "" {
                message = err.Error()
            }
            return nil, "external_backend_failed", boundedGitHealthError(message)
        }
        data = output
    }
    decoder := json.NewDecoder(bytes.NewReader(data))
    decoder.UseNumber()
    var payload any
    if err := decoder.Decode(&payload); err != nil {
        return nil, "input_invalid", boundedGitHealthError(err.Error())
    }
    return payload, "ok", ""
}

func intString(value int) string {
    const digits = "0123456789"
    if value == 0 {
        return "0"
    }
    buf := make([]byte, 0, 20)
    for value > 0 {
        buf = append(buf, digits[value%10])
        value /= 10
    }
    for left, right := 0, len(buf)-1; left < right; left, right = left+1, right-1 {
        buf[left], buf[right] = buf[right], buf[left]
    }
    return string(buf)
}

func cmdGitHistoryHealth(args []string) int {
    flags := flag.NewFlagSet("git-history-health", flag.ContinueOnError)
    flags.SetOutput(io.Discard)
    jsonInput := flags.String("json-input", "", "saved git-sizer JSON input")
    minConcern := flags.Float64("min-concern", 1.0, "minimum git-sizer levelOfConcern")
    maxFindings := flags.Int("max-findings", 30, "maximum returned findings; 0 means unlimited")
    if err := flags.Parse(args); err != nil {
        emitGitHealthJSON(map[string]any{"tool": "git-history-health", "status": "invalid_arguments", "error": boundedGitHealthError(err.Error())})
        return 2
    }
    root := "."
    if flags.NArg() > 0 {
        root = flags.Arg(0)
    }
    absoluteRoot, err := filepath.Abs(root)
    if err != nil {
        emitGitHealthJSON(map[string]any{"tool": "git-history-health", "status": "input_unavailable", "project_root": root, "error": boundedGitHealthError(err.Error())})
        return 2
    }
    info, err := os.Stat(absoluteRoot)
    if err != nil {
        status := "input_unavailable"
        if os.IsNotExist(err) {
            status = "input_missing"
        }
        emitGitHealthJSON(map[string]any{"tool": "git-history-health", "status": status, "project_root": absoluteRoot})
        return 2
    }
    if !info.IsDir() {
        emitGitHealthJSON(map[string]any{"tool": "git-history-health", "status": "input_not_directory", "project_root": absoluteRoot})
        return 2
    }

    payload, status, detail := loadGitSizerJSON(absoluteRoot, *jsonInput)
    backend := "git-sizer"
    if *jsonInput != "" {
        backend = "git-sizer-json-input"
    }
    if status != "ok" {
        result := map[string]any{"tool": "git-history-health", "status": status, "project_root": absoluteRoot, "backend": backend}
        if detail != "" {
            result["error"] = detail
        }
        emitGitHealthJSON(result)
        return 2
    }
    threshold := *minConcern
    if threshold < 0 {
        threshold = 0
    }
    result := map[string]any{"tool": "git-history-health", "status": "ok", "project_root": absoluteRoot, "backend": backend}
    for key, value := range summarizeGitSizer(payload, threshold, *maxFindings) {
        result[key] = value
    }
    emitGitHealthJSON(result)
    return 0
}
