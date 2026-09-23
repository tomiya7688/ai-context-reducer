package backend

import (
    "errors"
    "fmt"
    "os"
    "path/filepath"
    "runtime"
)

// ErrExecutableUnavailable はbundle内に対象binaryが存在しない状態を示します。
var ErrExecutableUnavailable = errors.New("bundle executable unavailable")

// BundleResolver はFull Bundle rootから既存CLIを解決します。
type BundleResolver struct {
    Root string
}

// Resolve はPATH検索へ逃げず、配布archive内のbinaryだけを返します。
func (resolver BundleResolver) Resolve(program Program) (CommandSpec, error) {
    name, ok := binaryNames[program]
    if !ok {
        return CommandSpec{}, fmt.Errorf("unsupported program: %q", program)
    }
    if resolver.Root == "" {
        return CommandSpec{}, fmt.Errorf("bundle root is empty")
    }
    suffix := ""
    if runtime.GOOS == "windows" {
        suffix = ".exe"
    }
    path := filepath.Join(resolver.Root, name+suffix)
    info, err := os.Stat(path)
    if err != nil {
        if os.IsNotExist(err) {
            return CommandSpec{}, fmt.Errorf("%w: %s", ErrExecutableUnavailable, path)
        }
        return CommandSpec{}, fmt.Errorf("stat bundle executable %s: %w", path, err)
    }
    if info.IsDir() {
        return CommandSpec{}, fmt.Errorf("%w: %s is a directory", ErrExecutableUnavailable, path)
    }
    return CommandSpec{Path: path}, nil
}
