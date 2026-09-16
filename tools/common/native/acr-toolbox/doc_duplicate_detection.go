package main

import (
    "sort"
    "strings"
)

type docDuplicateOccurrence struct {
    Path string `json:"path"`
    Line int    `json:"line"`
}

type docDuplicateGroup struct {
    RepeatedText string                   `json:"repeated_text"`
    Occurrences  []docDuplicateOccurrence `json:"occurrences"`
}

type docDuplicateDocument struct {
    Path  string
    Lines []string
}

func normalizeDuplicateLine(line string) string {
    text := strings.ToLower(strings.Join(strings.Fields(strings.TrimSpace(line)), " "))
    replacer := strings.NewReplacer("`", "", "*", "", "_", "", ">", "", "#", "", "-", "")
    return strings.TrimSpace(replacer.Replace(text))
}

func truncateRunes(text string, limit int) string {
    runes := []rune(text)
    if len(runes) <= limit {
        return text
    }
    return string(runes[:limit])
}

func collectNativeDocumentDuplicates(documents []docDuplicateDocument, minChars int) []docDuplicateGroup {
    if minChars < 0 {
        minChars = 0
    }
    sort.Slice(documents, func(i, j int) bool { return documents[i].Path < documents[j].Path })
    occurrences := map[string][]docDuplicateOccurrence{}
    representative := map[string]string{}

    for _, document := range documents {
        for index, line := range document.Lines {
            normalized := normalizeDuplicateLine(line)
            if len([]rune(normalized)) < minChars {
                continue
            }
            if _, ok := representative[normalized]; !ok {
                representative[normalized] = strings.TrimSpace(line)
            }
            occurrences[normalized] = append(occurrences[normalized], docDuplicateOccurrence{Path: document.Path, Line: index + 1})
        }
    }

    groups := []docDuplicateGroup{}
    for normalized, rows := range occurrences {
        paths := map[string]bool{}
        for _, row := range rows {
            paths[row.Path] = true
        }
        if len(paths) < 2 {
            continue
        }
        sort.Slice(rows, func(i, j int) bool {
            if rows[i].Path == rows[j].Path {
                return rows[i].Line < rows[j].Line
            }
            return rows[i].Path < rows[j].Path
        })
        groups = append(groups, docDuplicateGroup{
            RepeatedText: truncateRunes(representative[normalized], 180),
            Occurrences: rows,
        })
    }
    sort.Slice(groups, func(i, j int) bool {
        if len(groups[i].Occurrences) != len(groups[j].Occurrences) {
            return len(groups[i].Occurrences) > len(groups[j].Occurrences)
        }
        return strings.ToLower(groups[i].RepeatedText) < strings.ToLower(groups[j].RepeatedText)
    })
    return groups
}
