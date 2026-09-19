package main

import (
    "regexp"
    "strings"
)

var policyEnglishRulePattern = regexp.MustCompile(`(?i)\b(?:must not|should not|must|should|required|recommended)\b`)
var policyHeadingPattern = regexp.MustCompile(`^#{1,6}\s+`)
var policyJapaneseRuleTerms = []string{"禁止", "必須", "推奨", "してはならない", "すること"}

type policyFinding struct {
    Path     string `json:"path"`
    Line     int    `json:"line"`
    Heading  string `json:"heading"`
    RuleText string `json:"rule_text"`
}

// isNativePolicyLine はroutingや安全側fallbackに使う条件を判定します。
func isNativePolicyLine(line string) bool {
    if policyEnglishRulePattern.MatchString(line) {
        return true
    }
    for _, term := range policyJapaneseRuleTerms {
        if strings.Contains(line, term) {
            return true
        }
    }
    return false
}

// nativePolicyFindings はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func nativePolicyFindings(path string, lines []string) []policyFinding {
    heading := ""
    findings := []policyFinding{}
    for index, line := range lines {
        if policyHeadingPattern.MatchString(line) {
            heading = strings.TrimSpace(strings.TrimLeft(line, "#"))
        }
        if !isNativePolicyLine(line) {
            continue
        }
        ruleText := strings.TrimSpace(line)
        runes := []rune(ruleText)
        if len(runes) > 220 {
            ruleText = string(runes[:220])
        }
        currentHeading := heading
        if currentHeading == "" {
            currentHeading = "no-heading"
        }
        findings = append(findings, policyFinding{
            Path: path,
            Line: index + 1,
            Heading: currentHeading,
            RuleText: ruleText,
        })
    }
    return findings
}
