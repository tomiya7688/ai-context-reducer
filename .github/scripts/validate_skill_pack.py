#!/usr/bin/env python3
"""配布スキルの形式と、第三者の原本・ライセンス表示を確認する。"""

import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


# この一覧は実際にObaPickが作成したものだけを記録する。名前の接頭語だけで自作とは判定しない。
FIRST_PARTY_SKILLS = frozenset({
    "obapick-find-code",
    "obapick-small-change",
    "obapick-review-changes",
    "obapick-handoff",
    "obapick-clear-docs",
    "obapick-python-check",
    "obapick-go-check",
})

# 外部から取得した原本の識別情報は、編集可能なライセンス一覧と別に固定する。
THIRD_PARTY_SOURCES = {
    "bug-reproduction-brief": {
        "source_commit": "60764df8b04cec728fd106744f98f90e18479105",
        "source_blob": "add9ca292293ef860cb4cab05063b922c49d3c1f",
    },
}
LICENSE_NOTICE_BLOBS = {
    "licenses/github-awesome-copilot-MIT.txt": "89bc5e962c9944cdb050887062afdaaf89be504a",
    "licenses/skyestrela-ai-agent-skill-preview-MIT.txt": "6e43e475e6cfb77847d06bcb8226f510b8ce8d6e",
}


# {
#   責務: [
#     git_blob_sha: ファイルの内容からGitが付ける識別情報を計算する
#   ],
#   処理: [
#     1: ファイルの内容をそのまま読む,
#     2: 内容の長さと本文から識別情報を計算する
#   ],
#   引数: [
#     file: 確認するファイル
#   ],
#   戻り値: [
#     1: 内容を表す識別情報
#   ]
# }
def git_blob_sha(file: Path) -> str:
    data = file.read_bytes()
    payload = b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    return hashlib.sha1(payload).hexdigest()


# {
#   責務: [
#     registered_skills: ライセンス一覧の表に登録されたスキルの場所を取り出す
#   ],
#   処理: [
#     1: 表の行だけを調べる,
#     2: 各行にある文書リンクの参照先を集める
#   ],
#   引数: [
#     ledger: ライセンス一覧の文章
#   ],
#   戻り値: [
#     1: 一覧の表から読み取れたスキルの場所
#   ]
# }
def registered_skills(ledger: str) -> set[str]:
    links = set()
    for row in ledger.splitlines():
        if not row.lstrip().startswith("|"):
            continue
        for found in re.findall(r"\]\(([^)]+)\)", row):
            parsed = urlsplit(found)
            if not parsed.scheme and not parsed.netloc:
                links.add(unquote(parsed.path))
    return links


# {
#   責務: [
#     check_skill: 一つのスキルの名前、説明、作者と原典の記録を確かめる
#   ],
#   処理: [
#     1: 先頭の宣言と本文を読み込む,
#     2: 名前と使用する場面の説明を確認する,
#     3: 自作か外部のものかを明示的な一覧から調べる,
#     4: 外部のものは取得元の版と、未改変の原本が一致するか調べる
#   ],
#   引数: [
#     file: 確認する説明ファイル,
#     ledgers: 日本語と英語のライセンス一覧,
#     registered: 両方の一覧に登録された場所
#   ],
#   戻り値: [
#     1: 見つかった問題の一覧
#   ]
# }
def check_skill(file: Path, ledgers: tuple[str, str], registered: tuple[set[str], set[str]]) -> list[str]:
    errors = []
    content = file.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", content, re.DOTALL)
    if not match:
        return [f"{file}: 先頭の宣言がありません"]

    fields = {}
    for line in match.group(1).splitlines():
        if not line or line[0].isspace():
            continue
        item = re.fullmatch(r"([a-z][a-z-]*):\s*(.*)", line)
        if item is None:
            errors.append(f"{file}: 宣言の行が正しくありません")
            continue
        name, value = item.groups()
        if name in fields:
            errors.append(f"{file}: {name} が重複しています")
        fields[name] = value

    name = fields.get("name", "")
    description = fields.get("description", "").strip().strip("'\"")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
        errors.append(f"{file}: スキル名の形式が正しくありません")
    if name != file.parent.name:
        errors.append(f"{file}: 名前とフォルダー名が異なります")
    if not 1 <= len(description) <= 1024 or not match.group(2).strip():
        errors.append(f"{file}: 説明または手順が不足しています")

    link = f"{name}/SKILL.md"
    for language, links in zip(("日本語", "英語"), registered):
        if link not in links:
            errors.append(f"{file}: {language}のライセンス一覧の表に登録されていません")

    if name in FIRST_PARTY_SKILLS:
        if fields.get("license") != "MIT":
            errors.append(f"{file}: 自作スキルのライセンスが一致しません")
        return errors

    source = THIRD_PARTY_SOURCES.get(name)
    if source is None:
        return errors + [f"{file}: 第三者の出典が未審査です"]

    jp, en = ledgers
    for language, ledger in (("日本語", jp), ("英語", en)):
        section = re.search(rf"(?ms)^### {re.escape(name)}\s*\n(.*?)(?=^## |^### |\Z)", ledger)
        if section is None:
            errors.append(f"{file}: {language}の一覧に第三者の個別記録がありません")
            continue
        info = section.group(1)
        if source["source_commit"] not in info:
            errors.append(f"{file}: {language}の一覧に取得元の版がありません")
        if "https://github.com/" not in info:
            errors.append(f"{file}: {language}の一覧に出典URLがありません")

    section_jp = re.search(rf"(?ms)^### {re.escape(name)}\s*\n(.*?)(?=^## |^### |\Z)", jp)
    if section_jp is None:
        return errors
    notice = section_jp.group(1)
    for required in ("配布元・公開者", "実際に取得したファイル",
                     "適用ライセンス", "改変の有無", "licenses/"):
        if required not in notice:
            errors.append(f"{file}: {required} がありません")
    if "未改変" in notice:
        recorded = re.search(r"未改変の原本のGit blob SHA[^\n]*?([0-9a-f]{40})", notice)
        if recorded is None or recorded.group(1) != source["source_blob"]:
            errors.append(f"{file}: 原本の識別情報が公開元と一致しません")
        if git_blob_sha(file) != source["source_blob"]:
            errors.append(f"{file}: 未改変という記録と実際の内容が異なります")
    elif "改変あり" not in notice or "変更内容" not in notice:
        errors.append(f"{file}: 改変した場合は変更内容を明記してください")
    return errors


# {
#   責務: [
#     check_links: スキルの説明から参照するローカル文書の存在を確かめる
#   ],
#   処理: [
#     1: 文書中のリンクを読む,
#     2: 外部の場所と文書内の位置指定を除外する,
#     3: 実在しない参照先を記録する
#   ],
#   引数: [
#     file: 調べる文書
#   ],
#   戻り値: [
#     1: 存在しない参照先の一覧
#   ]
# }
def check_links(file: Path) -> list[str]:
    errors = []
    for matched in re.finditer(r"!?\[[^\]]*\]\(([^)]+)\)", file.read_text(encoding="utf-8")):
        parsed = urlsplit(matched.group(1))
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        if not (file.parent / unquote(parsed.path)).exists():
            errors.append(f"{file}: リンク先がありません: {parsed.path}")
    return errors


# {
#   責務: [
#     main: スキルの形式と第三者の再配布記録を全件検査する
#   ],
#   処理: [
#     1: 案内とライセンス文の存在を確かめる,
#     2: 元のライセンス文に変更がないことを確認する,
#     3: スキルの情報と日英のライセンス登録を検査する,
#     4: 相対リンクを調べて失敗を表示する
#   ],
#   引数: [],
#   戻り値: [
#     1: 問題がなければゼロ、あれば一
#   ]
# }
def main() -> int:
    root = Path(__file__).resolve().parents[2] / "skills"
    required = ["README.md", "README.en.md", "LICENSES.md", "LICENSES.en.md"]
    required.extend(LICENSE_NOTICE_BLOBS)
    errors = [f"必要なファイルがありません: {x}" for x in required
              if not (root / x).is_file()]
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    for name, original in LICENSE_NOTICE_BLOBS.items():
        if git_blob_sha(root / name) != original:
            errors.append(f"{name}: 元のライセンス文と一致しません")

    jp = (root / "LICENSES.md").read_text(encoding="utf-8")
    en = (root / "LICENSES.en.md").read_text(encoding="utf-8")
    registered = (registered_skills(jp), registered_skills(en))
    folders = sorted(p for p in root.iterdir() if p.is_dir() and p.name != "licenses")
    if not folders:
        errors.append("スキルが一つもありません")
    for folder in folders:
        file = folder / "SKILL.md"
        if file.is_file():
            errors.extend(check_skill(file, (jp, en), registered))
        else:
            errors.append(f"{folder}: SKILL.md がありません")

    for name in required[:4]:
        errors.extend(check_links(root / name))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"{len(folders)}件のスキルの宣言・参照・ライセンス記録を確認しました")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
