# Settings storage

The application stores preferences in `settings.json`.

`load_settings` reads the file and raises `SettingsLoadError` when JSON decoding fails.
The user-facing error should identify which settings file failed so support can distinguish
a broken project file from a different settings file.
