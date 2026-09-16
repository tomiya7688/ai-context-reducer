package main

import (
    "encoding/json"
    "flag"
    "io"
    "os"
    "path/filepath"
    "strings"
    "unicode"
)

var validationVisualTerms = map[string]bool{"ui": true, "view": true, "scene": true, "widget": true, "layout": true}
var validationArtifactTerms = map[string]bool{"package": true, "installer": true, "publish": true, "release": true, "dist": true}
var validationContractTerms = map[string]bool{"parser": true, "lexer": true, "rule": true, "rules": true, "validator": true, "protocol": true}
var validationRuntimeTerms = map[string]bool{"random": true, "simulation": true, "physics": true, "agent": true}
var validationDataExts = map[string]bool{".json": true, ".yaml": true, ".yml": true, ".toml": true, ".csv": true}
var validationSourceExts = map[string]bool{".py": true, ".cs": true, ".go": true, ".c": true, ".h": true, ".cpp": true, ".hpp": true, ".gd": true}

type validationPlanRow struct {
    ChangedFile           string   `json:"changed_file"`
    RecommendedValidation []string `json:"recommended_validation"`
}

func emitValidationPlanJSON(value any) {
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    _ = enc.Encode(value)
}

func validationPathTerms(path string) map[string]bool {
    lower := strings.ToLower(path)
    parts := strings.FieldsFunc(lower, func(r rune) bool {
        return !(unicode.IsLetter(r) || unicode.IsDigit(r))
    })
    out := map[string]bool{}
    for _, part := range parts {
        if part != "" {
            out[part] = true
        }
    }
    return out
}

func validationHasAny(terms map[string]bool, wanted map[string]bool) bool {
    for term := range wanted {
        if terms[term] {
            return true
        }
    }
    return false
}

func validationAppendUnique(out []string, seen map[string]bool, values ...string) []string {
    for _, value := range values {
        if !seen[value] {
            out = append(out, value)
            seen[value] = true
        }
    }
    return out
}

func classifyValidationPath(path string) []string {
    lower := strings.ToLower(path)
    terms := validationPathTerms(lower)
    suffix := strings.ToLower(filepath.Ext(lower))
    out := []string{}
    seen := map[string]bool{}

    if validationHasAny(terms, validationVisualTerms) || suffix == ".gd" {
        out = validationAppendUnique(out, seen, "headless smoke if possible", "visual confirmation when acceptance is visual")
    }
    if validationHasAny(terms, validationArtifactTerms) {
        out = validationAppendUnique(out, seen, "artifact generation", "artifact smoke")
    }
    if validationHasAny(terms, validationContractTerms) {
        out = validationAppendUnique(out, seen, "targeted regression tests", "contract/spec check")
    }
    if validationHasAny(terms, validationRuntimeTerms) {
        out = validationAppendUnique(out, seen, "deterministic seam or fixed seed", "bounded runtime")
    }
    if validationDataExts[suffix] {
        out = validationAppendUnique(out, seen, "schema/parser validation", "representative data check")
    }
    if validationSourceExts[suffix] {
        out = validationAppendUnique(out, seen, "targeted tests", "syntax/build check")
    }
    if len(out) == 0 {
        out = append(out, "targeted validation")
    }
    return out
}

func cmdValidationPlan(args []string) int {
    flags := flag.NewFlagSet("validation-plan", flag.ContinueOnError)
    flags.SetOutput(io.Discard)
    if err := flags.Parse(args); err != nil {
        emitValidationPlanJSON(map[string]any{"tool": "validation-plan", "status": "invalid_arguments", "error": err.Error()})
        return 2
    }
    if flags.NArg() == 0 {
        emitValidationPlanJSON(map[string]any{"tool": "validation-plan", "status": "invalid_arguments", "required_argument": "one or more changed file paths"})
        return 2
    }
    rows := make([]validationPlanRow, 0, flags.NArg())
    for _, path := range flags.Args() {
        rows = append(rows, validationPlanRow{ChangedFile: path, RecommendedValidation: classifyValidationPath(path)})
    }
    emitValidationPlanJSON(map[string]any{
        "tool": "validation-plan",
        "status": "ok",
        "validation_by_file": rows,
    })
    return 0
}
