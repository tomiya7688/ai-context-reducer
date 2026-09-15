package main

import (
    "fmt"
    "os"
)

func usage() {
    fmt.Println("acr-toolbox <analyze|search|find|tree|stats|doc-index|slice|compact-log|compact-diff|remote-delta|structure-index|language-env|env> ...")
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
    case "structure-index":
        code = cmdStructureIndex(os.Args[2:])
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
