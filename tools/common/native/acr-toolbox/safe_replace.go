package main

import (
    "fmt"
    "os"
    "path/filepath"
)

// replaceMaterializedFile prefers the platform's direct same-directory rename.
// On platforms where replacing an existing destination is not supported by
// os.Rename, it preserves the old file in a temporary backup and restores it
// if installing the new file fails.
func replaceMaterializedFile(temporaryName, destination string) error {
    if err := os.Rename(temporaryName, destination); err == nil {
        return nil
    } else {
        if _, statErr := os.Stat(destination); statErr != nil {
            return err
        }

        backup, backupErr := os.CreateTemp(filepath.Dir(destination), ".acr-backup-*")
        if backupErr != nil {
            return fmt.Errorf("prepare destination backup: %w", backupErr)
        }
        backupName := backup.Name()
        if closeErr := backup.Close(); closeErr != nil {
            _ = os.Remove(backupName)
            return fmt.Errorf("prepare destination backup: %w", closeErr)
        }
        if removeErr := os.Remove(backupName); removeErr != nil {
            return fmt.Errorf("prepare destination backup: %w", removeErr)
        }

        if moveErr := os.Rename(destination, backupName); moveErr != nil {
            return fmt.Errorf("backup existing destination: %w", moveErr)
        }

        if installErr := os.Rename(temporaryName, destination); installErr != nil {
            if restoreErr := os.Rename(backupName, destination); restoreErr != nil {
                return fmt.Errorf("install replacement: %v; restore previous destination: %w", installErr, restoreErr)
            }
            return fmt.Errorf("install replacement: %w", installErr)
        }

        if removeErr := os.Remove(backupName); removeErr != nil {
            return fmt.Errorf("replacement installed but backup cleanup failed: %w", removeErr)
        }
        return nil
    }
}
