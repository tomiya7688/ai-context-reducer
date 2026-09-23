package backend

import (
    "bytes"
    "context"
    "encoding/json"
    "errors"
    "fmt"
    "io"
    "os"
    "os/exec"
    "strings"
    "time"
)

const (
    defaultStdoutLimit = 1024 * 1024
    defaultStderrLimit = 64 * 1024
    defaultTimeout     = 30 * time.Second
)

// Runner はprocess実行、bounded capture、timeout/cancel、結果分類を共通化します。
type Runner struct {
    Resolver          Resolver
    MaxStdoutBytes    int
    MaxStderrBytes    int
    DefaultTimeout    time.Duration
}

type captureResult struct {
    data      []byte
    truncated bool
    err       error
}

// NewRunner はGUIが通常使う安全な既定上限でRunnerを作ります。
func NewRunner(resolver Resolver) Runner {
    return Runner{
        Resolver:       resolver,
        MaxStdoutBytes: defaultStdoutLimit,
        MaxStderrBytes: defaultStderrLimit,
        DefaultTimeout: defaultTimeout,
    }
}

// Invoke は既存CLIを直接起動し、生のCLI contractとbackend stateを分離して返します。
func (runner Runner) Invoke(ctx context.Context, request Request) Result {
    result := Result{Program: request.Program, ExitCode: -1, OutputKind: outputKind(request)}
    if ctx == nil {
        ctx = context.Background()
    }
    if err := ctx.Err(); err != nil {
        return contextResult(result, err)
    }
    if err := validateRequest(request); err != nil {
        result.State = StateFailure
        result.FailureKind = FailureInvalidRequest
        result.Error = err.Error()
        return result
    }
    if isHeavyCommand(request) && !request.AllowHeavy {
        result.State = StateConfirmationRequired
        result.CLIStatus = "confirmation_required"
        result.Error = "explicit heavy-command confirmation is required before invocation"
        return result
    }
    if runner.Resolver == nil {
        result.State = StateFailure
        result.FailureKind = FailureResolve
        result.Error = "backend resolver is not configured"
        return result
    }

    spec, err := runner.Resolver.Resolve(request.Program)
    if err != nil {
        if errors.Is(err, ErrExecutableUnavailable) {
            result.State = StateUnavailable
        } else {
            result.State = StateFailure
            result.FailureKind = FailureResolve
        }
        result.Error = err.Error()
        return result
    }

    timeout := request.Timeout
    if timeout <= 0 {
        timeout = runner.DefaultTimeout
    }
    runCtx := ctx
    cancel := func() {}
    if timeout > 0 {
        runCtx, cancel = context.WithTimeout(ctx, timeout)
    }
    defer cancel()

    args := append([]string{}, spec.PrefixArgs...)
    args = append(args, request.Args...)
    command := exec.CommandContext(runCtx, spec.Path, args...)
    if request.WorkingDir != "" {
        command.Dir = request.WorkingDir
    }
    if len(spec.Env) > 0 {
        command.Env = append(os.Environ(), spec.Env...)
    }

    stdout, err := command.StdoutPipe()
    if err != nil {
        result.State = StateFailure
        result.FailureKind = FailureStart
        result.Error = fmt.Sprintf("open stdout pipe: %v", err)
        return result
    }
    stderr, err := command.StderrPipe()
    if err != nil {
        result.State = StateFailure
        result.FailureKind = FailureStart
        result.Error = fmt.Sprintf("open stderr pipe: %v", err)
        return result
    }
    if err := command.Start(); err != nil {
        if errors.Is(err, os.ErrNotExist) {
            result.State = StateUnavailable
        } else {
            result.State = StateFailure
            result.FailureKind = FailureStart
        }
        result.Error = err.Error()
        return result
    }

    stdoutLimit := normalizeLimit(runner.MaxStdoutBytes, defaultStdoutLimit)
    stderrLimit := normalizeLimit(runner.MaxStderrBytes, defaultStderrLimit)
    stdoutCh := make(chan captureResult, 1)
    stderrCh := make(chan captureResult, 1)
    go func() { stdoutCh <- captureBounded(stdout, stdoutLimit) }()
    go func() { stderrCh <- captureBounded(stderr, stderrLimit) }()

    stdoutResult := <-stdoutCh
    stderrResult := <-stderrCh
    waitErr := command.Wait()

    result.StdoutTruncated = stdoutResult.truncated
    result.StderrTruncated = stderrResult.truncated
    result.Stderr = string(stderrResult.data)
    if stdoutResult.err != nil || stderrResult.err != nil {
        result.State = StateFailure
        result.FailureKind = FailureCommand
        result.Error = firstError(stdoutResult.err, stderrResult.err).Error()
        return result
    }
    if err := runCtx.Err(); err != nil {
        return contextResult(result, err)
    }

    result.ExitCode = commandExitCode(waitErr)
    if result.OutputKind == OutputText {
        result.Text = string(stdoutResult.data)
        if result.ExitCode == 0 {
            result.State = StateSuccess
        } else {
            result.State = StateFailure
            result.FailureKind = FailureCommand
            if waitErr != nil {
                result.Error = waitErr.Error()
            }
        }
        return result
    }

    if result.StdoutTruncated {
        result.State = StateFailure
        result.FailureKind = FailureOutputLimit
        result.Error = "JSON stdout exceeded backend capture limit"
        return result
    }
    raw := bytes.TrimSpace(stdoutResult.data)
    if len(raw) == 0 || !json.Valid(raw) {
        result.State = StateFailure
        result.FailureKind = FailureInvalidJSON
        result.Error = "CLI stdout was not valid JSON"
        return result
    }

    result.JSON = append(result.JSON[:0], raw...)
    result.CLIStatus = extractCLIStatus(raw)
    result.State = classifyJSONResult(result.ExitCode, result.CLIStatus)
    if result.State == StateFailure {
        result.FailureKind = FailureCommand
        if waitErr != nil {
            result.Error = waitErr.Error()
        }
    }
    return result
}

// captureBounded はmemoryへ保持する量だけを制限し、pipe自体は最後までdrainします。
func captureBounded(reader io.Reader, limit int) captureResult {
    buffer := bytes.NewBuffer(make([]byte, 0, minInt(limit, 32*1024)))
    chunk := make([]byte, 32*1024)
    truncated := false
    for {
        count, err := reader.Read(chunk)
        if count > 0 {
            remaining := limit - buffer.Len()
            if remaining > 0 {
                keep := count
                if keep > remaining {
                    keep = remaining
                }
                _, _ = buffer.Write(chunk[:keep])
            }
            if count > remaining {
                truncated = true
            }
        }
        if err == io.EOF {
            return captureResult{data: buffer.Bytes(), truncated: truncated}
        }
        if err != nil {
            return captureResult{data: buffer.Bytes(), truncated: truncated, err: err}
        }
    }
}

// contextResult はdeadlineとuser cancellationを区別します。
func contextResult(result Result, err error) Result {
    result.ExitCode = -1
    result.Error = err.Error()
    if errors.Is(err, context.DeadlineExceeded) {
        result.State = StateTimeout
    } else {
        result.State = StateCancelled
    }
    return result
}

// commandExitCode はprocess未起動と通常のnon-zero exitを区別します。
func commandExitCode(err error) int {
    if err == nil {
        return 0
    }
    var exitErr *exec.ExitError
    if errors.As(err, &exitErr) {
        return exitErr.ExitCode()
    }
    return -1
}

// normalizeLimit は0以下の設定でbounded captureが無効化されないよう既定値へ戻します。
func normalizeLimit(value int, fallback int) int {
    if value <= 0 {
        return fallback
    }
    return value
}

// firstError はcapture側の最初の失敗だけをcompactに返します。
func firstError(values ...error) error {
    for _, value := range values {
        if value != nil {
            return value
        }
    }
    return errors.New("unknown capture error")
}

// minInt はbounded bufferの初期容量だけを小さく保ちます。
func minInt(a int, b int) int {
    if a < b {
        return a
    }
    return b
}

// trimDiagnostic は将来UIへdiagnosticを渡す場合にも無制限な空白を残さないためのhelperです。
func trimDiagnostic(value string) string {
    return strings.TrimSpace(value)
}
