from pathlib import Path
import json

class SettingsLoadError(ValueError):
    """Raised when settings.json cannot be decoded."""

def load_settings(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise SettingsLoadError(f"invalid settings.json: {exc.msg}") from exc

def save_settings(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
