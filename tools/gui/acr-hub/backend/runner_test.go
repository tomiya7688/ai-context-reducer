package backend

import (
    "context"
    "fmt"
    "os"
    "strings"
    "testing"
    "time"
)

type helperResolver struct {
    mode string
    calls *int
}

// Resolve はtest binary自身をCLI fixtureとして再実行し、OS依存shellを避けます。
func (resolver helperResolver) Resolve(program Program) (CommandSpec, error) {
    if resolver.calls != nil {
        *resolver.calls = *resolver.calls + 1
    }
    return CommandSpec{
        Path: os.Args[0],
        PrefixArgs: []string{"-test.run=TestHelperProcess", "--", resolver.mode},
        Env: []string{"ACR_HUB_HELPER=1"},
    }, nil
}

// TestHelperProcess はbackendから見た既存CLIの成功・失敗・timeoutを再現します。
func TestHelperProcess(t *testing.T) {
    if os.Getenv("ACR_HUB_HELPER") != "1" {
        return
    }
    marker := -1
    for index, arg := range os.Args {
        if arg == "--" {
            marker = index
            break
        }
    }
    if marker < 0 || marker+1 >= len(os.Args) {
        os.Exit(90)
    }
    switch os.Args[marker+1] {
    case "ok":
        fmt.Print("{\"tool\":\"fixture\",\"status\":\"ok\",\"value\":1}\n")
        os.Exit(0)
    case "unavailable":
        fmt.Print("{\"tool\":\"fixture\",\"status\":\"external_backend_unavailable\"}\n")
        os.Exit(2)
    case "violations":
        fmt.Print("{\"tool\":\"fixture\",\"status\":\"violations\",\"count\":1}\n")
        os.Exit(1)
    case "malformed":
        fmt.Print("not-json\n")
        os.Exit(0)
    case "large-json":
        fmt.Printf("{\"tool\":\"fixture\",\"status\":\"ok\",\"payload\":\"%s\"}\n", strings.Repeat("x", 4096))
        os.Exit(0)
    case "stderr":
        fmt.Fprint(os.Stderr, strings.Repeat("e", 4096))
        fmt.Print("{\"tool\":\"fixture\",\"status\":\"ok\"}\n")
        os.Exit(0)
    case "text":
        fmt.Print(strings.Repeat("tree-line\n", 200))
        os.Exit(0)
    case "sleep":
        time.Sleep(2 * time.Second)
        fmt.Print("{\"tool\":\"fixture\",\"status\":\"ok\"}\n")
        os.Exit(0)
    default:
        os.Exit(91)
    }
}

// TestOutputKindMatchesNativeToolboxContract はnative CLIのJSON/text境界を固定します。
func TestOutputKindMatchesNativeToolboxContract(t *testing.T) {
    textCommands := []string{"tree", "doc-index", "slice", "compact-log", "compact-diff", "remote-delta", "context-pack-builder", "responsibility-candidates"}
    for _, command := range textCommands {
        request := Request{Program: ProgramACRToolbox, Args: []string{command}}
        if got := outputKind(request); got != OutputText {
            t.Fatalf("%s output kind = %s, want text", command, got)
        }
    }
    jsonCommands := []string{"analyze", "select", "search", "stats", "syntax-health", "context-budget", "language-large-run", "policy-check", "version"}
    for _, command := range jsonCommands {
        request := Request{Program: ProgramACRToolbox, Args: []string{command}}
        if got := outputKind(request); got != OutputJSON {
            t.Fatalf("%s output kind = %s, want json", command, got)
        }
    }
}
// TestInvokePreservesJSONContract はCLI JSONをbackendが再構築しないことを確認します。
func TestInvokePreservesJSONContract(t *testing.T) {
    runner := NewRunner(helperResolver{mode: "ok"})
    result := runner.Invoke(context.Background(), Request{Program: ProgramGoSymbols})
    if result.State != StateSuccess || result.ExitCode != 0 || result.CLIStatus != "ok" {
        t.Fatalf("unexpected result: %+v", result)
    }
    want := "{\"tool\":\"fixture\",\"status\":\"ok\",\"value\":1}"
    if string(result.JSON) != want {
        t.Fatalf("JSON changed: got %q want %q", string(result.JSON), want)
    }
}

// TestInvokeClassifiesUnavailable はCLIのunavailable statusとexit codeを保持します。
func TestInvokeClassifiesUnavailable(t *testing.T) {
    runner := NewRunner(helperResolver{mode: "unavailable"})
    result := runner.Invoke(context.Background(), Request{Program: ProgramGoImportMap})
    if result.State != StateUnavailable || result.ExitCode != 2 || result.CLIStatus != "external_backend_unavailable" {
        t.Fatalf("unexpected result: %+v", result)
    }
}

// TestDomainFindingIsNotBackendFailure はfinding用exit 1をprocess failureと混同しないことを確認します。
func TestDomainFindingIsNotBackendFailure(t *testing.T) {
    runner := NewRunner(helperResolver{mode: "violations"})
    result := runner.Invoke(context.Background(), Request{Program: ProgramAffectedTests})
    if result.State != StateSuccess || result.ExitCode != 1 || result.CLIStatus != "violations" {
        t.Fatalf("unexpected result: %+v", result)
    }
}

// TestInvalidJSONFailsSafely はJSON commandの壊れたstdoutを成功扱いしません。
func TestInvalidJSONFailsSafely(t *testing.T) {
    runner := NewRunner(helperResolver{mode: "malformed"})
    result := runner.Invoke(context.Background(), Request{Program: ProgramGoPackageGraph})
    if result.State != StateFailure || result.FailureKind != FailureInvalidJSON {
        t.Fatalf("unexpected result: %+v", result)
    }
}

// TestHeavyCommandNeedsConfirmation は明示確認前にprocess自体を起動しません。
func TestHeavyCommandNeedsConfirmation(t *testing.T) {
    calls := 0
    runner := NewRunner(helperResolver{mode: "ok", calls: &calls})
    result := runner.Invoke(context.Background(), Request{Program: ProgramACRToolbox, Args: []string{"language-large-run", "."}})
    if result.State != StateConfirmationRequired || calls != 0 {
        t.Fatalf("unexpected result/calls: %+v calls=%d", result, calls)
    }
}

// TestHeavyCommandRunsAfterConfirmation は確認済みrequestだけ既存CLIへ渡します。
func TestHeavyCommandRunsAfterConfirmation(t *testing.T) {
    calls := 0
    runner := NewRunner(helperResolver{mode: "ok", calls: &calls})
    result := runner.Invoke(context.Background(), Request{
        Program: ProgramACRToolbox,
        Args: []string{"language-large-run", "--allow-heavy", "."},
        AllowHeavy: true,
    })
    if result.State != StateSuccess || calls != 1 {
        t.Fatalf("unexpected result/calls: %+v calls=%d", result, calls)
    }
}

// TestInvokeTimeout はtimeoutを通常failureやcancelと混同しません。
func TestInvokeTimeout(t *testing.T) {
    runner := NewRunner(helperResolver{mode: "sleep"})
    result := runner.Invoke(context.Background(), Request{Program: ProgramGoSymbols, Timeout: 20 * time.Millisecond})
    if result.State != StateTimeout {
        t.Fatalf("unexpected result: %+v", result)
    }
}

// TestInvokeCancellation はcallerからのcancelをprocess起動前でも識別します。
func TestInvokeCancellation(t *testing.T) {
    ctx, cancel := context.WithCancel(context.Background())
    cancel()
    runner := NewRunner(helperResolver{mode: "ok"})
    result := runner.Invoke(ctx, Request{Program: ProgramGoSymbols})
    if result.State != StateCancelled {
        t.Fatalf("unexpected result: %+v", result)
    }
}

// TestStderrIsBounded はstderr全量をGUI memoryへ保持しません。
func TestStderrIsBounded(t *testing.T) {
    runner := NewRunner(helperResolver{mode: "stderr"})
    runner.MaxStderrBytes = 32
    result := runner.Invoke(context.Background(), Request{Program: ProgramGoSymbols})
    if result.State != StateSuccess || !result.StderrTruncated || len(result.Stderr) != 32 {
        t.Fatalf("unexpected result: %+v stderr=%d", result, len(result.Stderr))
    }
}

// TestTruncatedJSONIsNotAccepted はcapture上限で欠けたJSONを成功結果にしません。
func TestTruncatedJSONIsNotAccepted(t *testing.T) {
    runner := NewRunner(helperResolver{mode: "large-json"})
    runner.MaxStdoutBytes = 64
    result := runner.Invoke(context.Background(), Request{Program: ProgramGoSymbols})
    if result.State != StateFailure || result.FailureKind != FailureOutputLimit || !result.StdoutTruncated {
        t.Fatalf("unexpected result: %+v", result)
    }
}

// TestTextOutputIsBounded は既存text artifactもboundedに保持できます。
func TestTextOutputIsBounded(t *testing.T) {
    runner := NewRunner(helperResolver{mode: "text"})
    runner.MaxStdoutBytes = 40
    result := runner.Invoke(context.Background(), Request{Program: ProgramACRToolbox, Args: []string{"tree", "."}})
    if result.State != StateSuccess || result.OutputKind != OutputText || !result.StdoutTruncated || len(result.Text) != 40 {
        t.Fatalf("unexpected result: %+v text=%d", result, len(result.Text))
    }
}

// TestUnsupportedProgramIsRejected はGUI入力から任意binaryを起動できないことを確認します。
func TestUnsupportedProgramIsRejected(t *testing.T) {
    runner := NewRunner(helperResolver{mode: "ok"})
    result := runner.Invoke(context.Background(), Request{Program: Program("sh")})
    if result.State != StateFailure || result.FailureKind != FailureInvalidRequest {
        t.Fatalf("unexpected result: %+v", result)
    }
}
