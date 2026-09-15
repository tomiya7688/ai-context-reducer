package main

import (
    "encoding/json"
    "io"
    "os"
    "path/filepath"
)

func atomicNativeCopy(source, destination string) error {
    if err := os.MkdirAll(filepath.Dir(destination), 0o755); err != nil {
        return err
    }
    sourceInfo, err := os.Stat(source)
    if err != nil {
        return err
    }
    input, err := os.Open(source)
    if err != nil {
        return err
    }
    defer input.Close()

    temporary, err := os.CreateTemp(filepath.Dir(destination), ".acr-copy-*")
    if err != nil {
        return err
    }
    temporaryName := temporary.Name()
    defer os.Remove(temporaryName)

    if _, err := io.Copy(temporary, input); err != nil {
        _ = temporary.Close()
        return err
    }
    if err := temporary.Sync(); err != nil {
        _ = temporary.Close()
        return err
    }
    if err := temporary.Close(); err != nil {
        return err
    }
    if err := os.Chmod(temporaryName, sourceInfo.Mode().Perm()); err != nil {
        return err
    }
    return replaceMaterializedFile(temporaryName, destination)
}

func atomicNativeJSON(path string, payload any) error {
    if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
        return err
    }
    data, err := json.MarshalIndent(payload, "", "  ")
    if err != nil {
        return err
    }
    data = append(data, '\n')

    temporary, err := os.CreateTemp(filepath.Dir(path), ".acr-manifest-*")
    if err != nil {
        return err
    }
    temporaryName := temporary.Name()
    defer os.Remove(temporaryName)

    if _, err := temporary.Write(data); err != nil {
        _ = temporary.Close()
        return err
    }
    if err := temporary.Sync(); err != nil {
        _ = temporary.Close()
        return err
    }
    if err := temporary.Close(); err != nil {
        return err
    }
    if err := os.Chmod(temporaryName, 0o644); err != nil {
        return err
    }
    return replaceMaterializedFile(temporaryName, path)
}
