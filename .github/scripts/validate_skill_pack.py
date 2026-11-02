#!/usr/bin/env python3
"""同梱スキルの形式・参照・ライセンス記録を確認する。"""

import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import unquote


# {
#   責務: [check_skill: スキルの宣言と公開者の記録を確かめる],
#   処理: [1: 名前と説明を読む, 2: フォルダー名と一致するか調べる, 3: 第三者の原本とライセンス記録を照合する],
#   引数: [file: 対象の説明ファイル, ledger: ライセンス一覧],
#   戻り値: [1: 見つかった問題の一覧]
# }
def check_skill(file: Path, ledger: str) -> list[str]:
    errors = []
    content = file.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", content, re.DOTALL)
    if not match:
        return [f"{file}: 先頭の宣言がありません"]
    fields = {}
    for line in match.group(1).splitlines():
        if not line or line[0].isspace():
            continue
        entry = re.fullmatch(r"([a-z][a-z-]*):\s*(.*)", line)
        if entry is None:
            errors.append(f"{file}: 宣言の行が正しくありません")
            continue
        key, val = entry.groups()
        if key in fields:
            errors.append(f"{file}: {key} が重複しています")
        fields[key] = val

    name = fields.get("name", "")
    desc = fields.get("description", "").strip().strip("'\"")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
        errors.append(f"{file}: スキル名の形式が正しくありません")
    if name != file.parent.name:
        errors.append(f"{file}: フォルダー名とスキル名が異なります")
    if not 1 <= len(desc) <= 1024 or not match.group(2).strip():
        errors.append(f"{file}: 説明または手順が不足しています")
    if f"({name}/SKILL.md)" not in ledger:
        errors.append(f"{file}: ライセンス一覧に登録されていません")

    if name.startswith("obapick-"):
        if fields.get("license") != "MIT":
            errors.append(f"{file}: 自作スキルのライセンス表示が正しくありません")
    else:
        section = re.search(rf"(?ms)^### {re.escape(name)}\s*\n(.*?)(?=^## |\Z)", ledger)
        if section is None:
            return errors + [f"{file}: 第三者の公開元と許可条件が記録されていません"]
        record = section.group(1)
        for required in ("配布元・公開者", "実際に取得したファイル",
                         "取得元のコミット", "適用ライセンス",
                         "改変の有無", "licenses/"):
            if required not in record:
                errors.append(f"{file}: {required} が記録されていません")
        if "未改変" in record:
            original = re.search(r"未改変の原本のGit blob SHA[^\n]*?([0-9a-f]{40})", record)
            if original is None:
                errors.append(f"{file}: 原本の内容の識別情報がありません")
            else:
                raw = file.read_bytes()
                digest = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
                if digest != original.group(1):
                    errors.append(f"{file}: 未改変と記載されていますが原本と異なります")
    return errors


# {
#   責務: [check_links: 説明文内の相対リンクが実在するか確かめる],
#   処理: [1: 参照先を抽出する, 2: 外部の場所を除く, 3: 存在しない参照先を記録する],
#   引数: [file: 対象の説明文],
#   戻り値: [1: 見つかった問題の一覧]
# }
def check_links(file: Path) -> list[str]:
    errors = []
    for match in re.finditer(r"!?\[[^\]]*\]\(([^)]+)\)", file.read_text(encoding="utf-8")):
        url = match.group(1).split("#")[0]
        if url and not re.match(r"^(?:https?://|mailto:)", url):
            if not (file.parent / unquote(url)).exists():
                errors.append(f"{file}: リンク先がありません: {url}")
    return errors


# {
#   責務: [main: スキルの全件検証を行い、問題の有無を終了状態で示す],
#   処理: [1: 必要なファイルを確認する, 2: 各スキルの宣言と出典を確認する, 3: 案内のリンクを調べる],
#   引数: [],
#   戻り値: [1: 成功したらゼロ、問題があれば一]
# }
def main() -> int:
    root = Path(__file__).resolve().parents[2] / "skills"
    required = [
        "README.md", "README.en.md", "LICENSES.md",
        "licenses/github-awesome-copilot-MIT.txt",
        "licenses/skyestrela-ai-agent-skill-preview-MIT.txt",
    ]
    errors = [f"必要なファイルがありません: {name}" for name in required
              if not (root / name).is_file()]
    if not (root / "LICENSES.md").is_file():
        print("\n".join(errors), file=sys.stderr)
        return 1

    ledger = (root / "LICENSES.md").read_text(encoding="utf-8")
    folders = sorted(p for p in root.iterdir() if p.is_dir() and p.name != "licenses")
    if not folders:
        errors.append("スキルが見つかりません")
    for folder in folders:
        file = folder / "SKILL.md"
        if file.is_file():
            errors.extend(check_skill(file, ledger))
        else:
            errors.append(f"{folder}: SKILL.md がありません")
    for name in ("README.md", "README.en.md", "LICENSES.md"):
        file = root / name
        if file.is_file():
            errors.extend(check_links(file))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"{len(folders)}件のスキルの宣言・参照・ライセンス記録を確認しました")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
