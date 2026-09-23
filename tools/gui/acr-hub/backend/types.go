package backend

import (
    "encoding/json"
    "time"
)

// Program はGUIから起動できる配布CLIを限定します。
type Program string

const (
    ProgramACRToolbox    Program = "acr-toolbox"
    ProgramGoSymbols     Program = "go-symbols"
    ProgramGoImportMap   Program = "go-import-map"
    ProgramGoPackageGraph Program = "go-package-graph"
    ProgramAffectedTests Program = "affected-tests"
)

// State はCLI結果をGUIが表示するための大分類です。
type State string

const (
    StateSuccess              State = "success"
    StateUnavailable          State = "unavailable"
    StateFailure              State = "failure"
    StateConfirmationRequired State = "confirmation_required"
    StateTimeout              State = "timeout"
    StateCancelled            State = "cancelled"
)

// OutputKind は既存CLIがstdoutへ返す成果物の型を示します。
type OutputKind string

const (
    OutputJSON OutputKind = "json"
    OutputText OutputKind = "text"
)

// FailureKind はbackend自身が検出した失敗理由をCLI statusと分離して保持します。
type FailureKind string

const (
    FailureNone             FailureKind = ""
    FailureInvalidRequest   FailureKind = "invalid_request"
    FailureResolve          FailureKind = "resolve_failed"
    FailureStart            FailureKind = "start_failed"
    FailureInvalidJSON      FailureKind = "invalid_json"
    FailureOutputLimit      FailureKind = "output_limit_exceeded"
    FailureCommand          FailureKind = "command_failed"
)

// Request は1回のCLI呼び出しに必要な情報だけを持ちます。
type Request struct {
    Program    Program
    Args       []string
    WorkingDir string
    Timeout    time.Duration
    AllowHeavy bool
}

// Result はCLIの生契約とGUI用の実行状態を混同せず保持します。
type Result struct {
    State            State
    Program          Program
    OutputKind       OutputKind
    ExitCode         int
    CLIStatus        string
    JSON             json.RawMessage
    Text             string
    Stderr           string
    StdoutTruncated  bool
    StderrTruncated  bool
    FailureKind      FailureKind
    Error            string
}

// CommandSpec はresolverが決定した実行fileと固定prefix引数を表します。
type CommandSpec struct {
    Path       string
    PrefixArgs []string
    Env        []string
}

// Resolver はbundle layoutの知識をprocess起動から分離します。
type Resolver interface {
    Resolve(program Program) (CommandSpec, error)
}
