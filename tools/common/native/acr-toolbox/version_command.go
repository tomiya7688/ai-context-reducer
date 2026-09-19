package main

import "runtime"

var buildVersion = "dev"
var buildCommit = ""

func cmdVersion() int {
    selectorWriteJSON(map[string]any{
        "tool": "version",
        "status": "ok",
        "version": buildVersion,
        "commit": buildCommit,
        "go_version": runtime.Version(),
        "goos": runtime.GOOS,
        "goarch": runtime.GOARCH,
    })
    return 0
}
