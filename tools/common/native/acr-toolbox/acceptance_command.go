package main

import (
    "flag"
    "io"
    "os"
    "strings"
)

var acceptanceHeadings = map[string][]string{
    "goal":       {"goal", "目的", "概要"},
    "required":   {"required", "requirements", "要件", "必須", "制約"},
    "acceptance": {"acceptance", "受け入れ", "完了条件", "completion", "done"},
    "deferred":   {"deferred", "out of scope", "非対象", "対象外", "今後", "future"},
}

func markdownHeadingTitle(line string) (string, bool) {
    trimmed := strings.TrimSpace(line)
    count := 0
    for count < len(trimmed) && count < 6 && trimmed[count] == '#' {
        count++
    }
    if count == 0 || count >= len(trimmed) || trimmed[count] != ' ' {
        return "", false
    }
    return strings.TrimSpace(trimmed[count+1:]), true
}

func acceptanceSection(lines []string, start, limit int) ([]string, bool) {
    if limit < 0 {
        limit = 0
    }
    all := []string{}
    for i := start + 1; i < len(lines); i++ {
        if _, ok := markdownHeadingTitle(lines[i]); ok {
            break
        }
        if strings.TrimSpace(lines[i]) != "" {
            all = append(all, strings.TrimRight(lines[i], "\r\n"))
        }
    }
    if len(all) > limit {
        return append([]string{}, all[:limit]...), true
    }
    return all, false
}

func extractAcceptanceSections(lines []string, limit int) (map[string][]string, map[string]bool) {
    sections := map[string][]string{}
    truncated := map[string]bool{}
    for key := range acceptanceHeadings {
        sections[key] = []string{}
        truncated[key] = false
    }
    for i, line := range lines {
        title, ok := markdownHeadingTitle(line)
        if !ok {
            continue
        }
        lowered := strings.ToLower(title)
        for key, terms := range acceptanceHeadings {
            matched := false
            for _, term := range terms {
                if contextTermPresent(lowered, term) {
                    matched = true
                    break
                }
            }
            if !matched {
                continue
            }
            values, cut := acceptanceSection(lines, i, limit)
            sections[key] = append(sections[key], values...)
            truncated[key] = truncated[key] || cut
        }
    }
    return sections, truncated
}

func cmdAcceptanceExtractor(args []string) int {
    fs := flag.NewFlagSet("acceptance-extractor", flag.ContinueOnError)
    fs.SetOutput(io.Discard)
    maxLines := fs.Int("max-lines-per-section", 40, "maximum non-empty lines returned per matched section")
    if err := fs.Parse(args); err != nil {
        emitStructureJSON(map[string]any{"tool": "acceptance-extractor", "status": "invalid_arguments", "error": err.Error()})
        return 2
    }
    if fs.NArg() != 1 {
        emitStructureJSON(map[string]any{"tool": "acceptance-extractor", "status": "invalid_arguments", "required_argument": "markdown_file"})
        return 2
    }
    path := fs.Arg(0)
    info, err := os.Stat(path)
    if err != nil {
        status := "read_failed"
        if os.IsNotExist(err) {
            status = "input_missing"
        }
        emitStructureJSON(map[string]any{"tool": "acceptance-extractor", "status": status, "input_file": path})
        return 2
    }
    if !info.Mode().IsRegular() {
        emitStructureJSON(map[string]any{"tool": "acceptance-extractor", "status": "input_not_file", "input_file": path})
        return 2
    }
    data, err := os.ReadFile(path)
    if err != nil {
        emitStructureJSON(map[string]any{"tool": "acceptance-extractor", "status": "read_failed", "input_file": path})
        return 2
    }
    text := strings.ToValidUTF8(string(data), "")
    lines := strings.Split(text, "\n")
    limit := *maxLines
    if limit < 0 {
        limit = 0
    }
    sections, truncated := extractAcceptanceSections(lines, limit)
    emitStructureJSON(map[string]any{
        "tool":              "acceptance-extractor",
        "status":            "ok",
        "input_file":        path,
        "sections":          sections,
        "section_truncated": truncated,
    })
    return 0
}
