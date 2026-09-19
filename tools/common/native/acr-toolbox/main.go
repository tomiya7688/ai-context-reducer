package main

import (
    "fmt"
    "os"
)

func usage() {
    fmt.Println("acr-toolbox <analyze|select|search|find|tree|stats|doc-index|slice|compact-log|compact-diff|remote-delta|git-history-health|syntax-health|structure-index|context-budget|hotspot-report|context-manifest|context-pack-builder|change-router|validation-plan|responsibility-candidates|policy-index|doc-duplicate-hints|ignore-candidates|acceptance-extractor|exploration-stop-check|materialize|language-setup|language-run|language-medium-run|language-large-plan|language-large-run|scoped-guides|policy-check|template|version|language-env|env> ...")
}

func main() {
    if len(os.Args) < 2 {
        usage()
        os.Exit(2)
    }

    var code int
    switch os.Args[1] {
    case "analyze":
        code = cmdAnalyze(os.Args[2:])
    case "select":
        code = cmdSelect(os.Args[2:])
    case "search":
        code = cmdSearch(os.Args[2:])
    case "find":
        code = cmdFind(os.Args[2:])
    case "tree":
        code = cmdTree(os.Args[2:])
    case "stats":
        code = cmdStats(os.Args[2:])
    case "doc-index":
        code = cmdDocIndex(os.Args[2:])
    case "slice":
        code = cmdSlice(os.Args[2:])
    case "compact-log":
        code = cmdCompactLog(os.Args[2:])
    case "compact-diff":
        code = cmdCompactDiff(os.Args[2:])
    case "remote-delta":
        code = cmdRemoteDelta(os.Args[2:])
    case "git-history-health":
        code = cmdGitHistoryHealth(os.Args[2:])
    case "syntax-health":
        code = cmdSyntaxHealth(os.Args[2:])
    case "structure-index":
        code = cmdStructureIndexEntry(os.Args[2:])
    case "context-budget":
        code = cmdContextBudget(os.Args[2:])
    case "hotspot-report":
        code = cmdHotspotReport(os.Args[2:])
    case "context-manifest":
        code = cmdContextManifest(os.Args[2:])
    case "context-pack-builder":
        code = cmdContextPackBuilder(os.Args[2:])
    case "change-router":
        code = cmdChangeRouter(os.Args[2:])
    case "validation-plan":
        code = cmdValidationPlan(os.Args[2:])
    case "responsibility-candidates":
        code = cmdResponsibilityCandidates(os.Args[2:])
    case "policy-index":
        code = cmdPolicyIndex(os.Args[2:])
    case "doc-duplicate-hints":
        code = cmdDocDuplicateHints(os.Args[2:])
    case "ignore-candidates":
        code = cmdIgnoreCandidates(os.Args[2:])
    case "acceptance-extractor":
        code = cmdAcceptanceExtractor(os.Args[2:])
    case "exploration-stop-check":
        code = cmdExplorationStopCheck(os.Args[2:])
    case "materialize":
        code = cmdMaterialize(os.Args[2:])
    case "language-setup":
        code = cmdLanguageSetup(os.Args[2:])
    case "language-run":
        code = cmdLanguageRun(os.Args[2:])
    case "language-medium-run":
        code = cmdLanguageMediumRun(os.Args[2:])
    case "language-large-plan":
        code = cmdLanguageLargePlan(os.Args[2:])
    case "language-large-run":
        code = cmdLanguageLargeRun(os.Args[2:])
    case "scoped-guides":
        code = cmdScopedGuides(os.Args[2:])
    case "policy-check":
        code = cmdPolicyCheck(os.Args[2:])
    case "template":
        code = cmdTemplate(os.Args[2:])
    case "version":
        code = cmdVersion()
    case "language-env":
        code = cmdLanguageEnv()
    case "env":
        code = cmdEnv()
    default:
        usage()
        code = 2
    }
    os.Exit(code)
}
