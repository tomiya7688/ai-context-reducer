#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")
ENGLISH_FILENAME_RE = re.compile(r"^[a-z0-9][a-z0-9.-]*\.md$")
EXTERNAL_SCHEMES = {"http", "https", "mailto", "data", "tel"}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def load_mapping(repo_root: Path, errors: list[str]) -> dict:
    path = repo_root / "docs" / "DOCUMENT_MAP.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(errors, f"cannot read docs/DOCUMENT_MAP.json: {exc}")
        return {}
    if data.get("schema_version") != 1:
        fail(errors, "docs/DOCUMENT_MAP.json: schema_version must be 1")
    if data.get("source_of_truth_language") != "ja":
        fail(errors, "docs/DOCUMENT_MAP.json: source_of_truth_language must be ja")
    if data.get("japanese_root") != "docs/jp":
        fail(errors, "docs/DOCUMENT_MAP.json: japanese_root must be docs/jp")
    if data.get("english_root") != "docs/en":
        fail(errors, "docs/DOCUMENT_MAP.json: english_root must be docs/en")
    if data.get("mapping_source_of_truth") != "docs/DOCUMENT_MAP.json":
        fail(errors, "docs/DOCUMENT_MAP.json: mapping_source_of_truth must point to itself")
    if not isinstance(data.get("documents"), list) or not data.get("documents"):
        fail(errors, "docs/DOCUMENT_MAP.json: documents must be a non-empty array")
    return data


def mapped_path(
    repo_root: Path, raw: object, field: str, doc_id: str, errors: list[str]
) -> Path | None:
    if not isinstance(raw, str) or not raw:
        fail(errors, f"{doc_id}: {field} must be a non-empty string")
        return None
    candidate = (repo_root / raw).resolve()
    try:
        candidate.relative_to(repo_root.resolve())
    except ValueError:
        fail(errors, f"{doc_id}: {field} escapes repository root: {raw}")
        return None
    return candidate


def markdown_files(repo_root: Path, root: Path) -> set[str]:
    if not root.is_dir():
        return set()
    return {
        path.relative_to(repo_root).as_posix()
        for path in root.rglob("*.md")
        if path.is_file()
    }


def destination(raw: str) -> str:
    value = raw.strip()
    if value.startswith("<"):
        end = value.find(">")
        return value[1:end] if end >= 0 else value[1:]
    return value.split(maxsplit=1)[0] if value else ""


def resolve_relative_link(repo_root: Path, source: Path, raw: str) -> Path | None:
    dest = destination(raw)
    if not dest or dest.startswith("#"):
        return None
    parsed = urlsplit(dest)
    if parsed.scheme.lower() in EXTERNAL_SCHEMES or parsed.netloc:
        return None
    if parsed.scheme:
        return None
    path_text = unquote(parsed.path)
    if not path_text:
        return None
    return (source.parent / path_text).resolve()


def validate_relative_links(
    repo_root: Path, files: list[Path], errors: list[str]
) -> None:
    root_resolved = repo_root.resolve()
    for source in files:
        try:
            text = source.read_text(encoding="utf-8")
        except OSError as exc:
            fail(
                errors,
                f"cannot read {source.relative_to(repo_root).as_posix()}: {exc}",
            )
            continue
        for match in MARKDOWN_LINK_RE.finditer(text):
            raw = match.group(1)
            target = resolve_relative_link(repo_root, source, raw)
            if target is None:
                continue
            try:
                target.relative_to(root_resolved)
            except ValueError:
                fail(
                    errors,
                    f"{source.relative_to(repo_root).as_posix()}: "
                    f"relative link escapes repository: {destination(raw)}",
                )
                continue
            if not target.exists():
                fail(
                    errors,
                    f"{source.relative_to(repo_root).as_posix()}: "
                    f"broken relative link: {destination(raw)}",
                )


def links_from(source: Path) -> list[Path]:
    text = source.read_text(encoding="utf-8")
    targets: list[Path] = []
    for match in MARKDOWN_LINK_RE.finditer(text):
        target = resolve_relative_link(source.parents[0], source, match.group(1))
        if target is not None:
            targets.append(target)
    return targets


def validate_markdown_code_escapes(source: Path, repo_root: Path, errors: list[str]) -> None:
    text = source.read_text(encoding="utf-8")
    if "\\`" in text:
        fail(
            errors,
            f"{source.relative_to(repo_root).as_posix()}: "
            "escaped backtick breaks Markdown code formatting",
        )


def validate_root_navigation(repo_root: Path, errors: list[str]) -> list[Path]:
    japanese_readme = repo_root / "README.md"
    english_readme = repo_root / "README.en.md"
    for path in (japanese_readme, english_readme):
        if not path.is_file():
            fail(errors, f"missing root language entry: {path.name}")
    if not japanese_readme.is_file() or not english_readme.is_file():
        return [path for path in (japanese_readme, english_readme) if path.is_file()]

    jp_text = japanese_readme.read_text(encoding="utf-8")
    en_text = english_readme.read_text(encoding="utf-8")
    validate_markdown_code_escapes(japanese_readme, repo_root, errors)
    validate_markdown_code_escapes(english_readme, repo_root, errors)
    jp_targets = links_from(japanese_readme)
    en_targets = links_from(english_readme)

    if english_readme.resolve() not in jp_targets:
        fail(errors, "README.md must link to README.en.md")
    if japanese_readme.resolve() not in en_targets:
        fail(errors, "README.en.md must link to README.md")

    jp_root = (repo_root / "docs" / "jp").resolve()
    en_root = (repo_root / "docs" / "en").resolve()
    if not any(target == jp_root or jp_root in target.parents for target in jp_targets):
        fail(errors, "README.md must link to docs/jp")
    if not any(target == en_root or en_root in target.parents for target in en_targets):
        fail(errors, "README.en.md must link to docs/en")

    releases_url = "https://github.com/tomiya7688/ai-context-reducer/releases"
    if releases_url not in jp_text:
        fail(errors, "README.md must link to GitHub Releases")
    if releases_url not in en_text:
        fail(errors, "README.en.md must link to GitHub Releases")
    return [japanese_readme, english_readme]


def validate(repo_root: Path) -> list[str]:
    errors: list[str] = []
    root_readmes = validate_root_navigation(repo_root, errors)
    mapping = load_mapping(repo_root, errors)
    documents = mapping.get("documents", []) if isinstance(mapping, dict) else []
    if not isinstance(documents, list):
        return errors

    ids: set[str] = set()
    japanese_paths: set[str] = set()
    english_paths: set[str] = set()
    pairs: list[tuple[str, Path, Path]] = []

    for index, entry in enumerate(documents):
        if not isinstance(entry, dict):
            fail(errors, f"documents[{index}] must be an object")
            continue
        doc_id = entry.get("id")
        if not isinstance(doc_id, str) or not doc_id:
            fail(errors, f"documents[{index}]: id must be a non-empty string")
            doc_id = f"documents[{index}]"
        elif doc_id in ids:
            fail(errors, f"duplicate document id: {doc_id}")
        else:
            ids.add(doc_id)

        jp = mapped_path(
            repo_root, entry.get("japanese"), "japanese", doc_id, errors
        )
        en = mapped_path(
            repo_root, entry.get("english"), "english", doc_id, errors
        )
        if jp is None or en is None:
            continue

        jp_rel = jp.relative_to(repo_root.resolve()).as_posix()
        en_rel = en.relative_to(repo_root.resolve()).as_posix()
        if not jp_rel.startswith("docs/jp/") or not jp_rel.endswith(".md"):
            fail(
                errors,
                f"{doc_id}: japanese path must be Markdown under docs/jp: {jp_rel}",
            )
        if not en_rel.startswith("docs/en/") or not en_rel.endswith(".md"):
            fail(
                errors,
                f"{doc_id}: english path must be Markdown under docs/en: {en_rel}",
            )
        if jp_rel in japanese_paths:
            fail(errors, f"duplicate Japanese mapping target: {jp_rel}")
        japanese_paths.add(jp_rel)
        if en_rel in english_paths:
            fail(errors, f"duplicate English mapping target: {en_rel}")
        english_paths.add(en_rel)

        if not JAPANESE_RE.search(jp.name):
            fail(
                errors,
                f"{doc_id}: Japanese filename must contain Japanese characters: {jp.name}",
            )
        if not ENGLISH_FILENAME_RE.fullmatch(en.name):
            fail(
                errors,
                f"{doc_id}: English filename must use lowercase ASCII kebab/dot form: {en.name}",
            )
        if not jp.is_file():
            fail(errors, f"{doc_id}: missing Japanese file: {jp_rel}")
        if not en.is_file():
            fail(errors, f"{doc_id}: missing English file: {en_rel}")
        pairs.append((doc_id, jp, en))

    actual_jp = markdown_files(repo_root, repo_root / "docs" / "jp")
    actual_en = markdown_files(repo_root, repo_root / "docs" / "en")
    for path in sorted(actual_jp - japanese_paths):
        fail(errors, f"unregistered Japanese document: {path}")
    for path in sorted(japanese_paths - actual_jp):
        if (repo_root / path).exists():
            fail(errors, f"mapped Japanese path is not a Markdown file: {path}")
    for path in sorted(actual_en - english_paths):
        fail(errors, f"unregistered English document: {path}")
    for path in sorted(english_paths - actual_en):
        if (repo_root / path).exists():
            fail(errors, f"mapped English path is not a Markdown file: {path}")

    for doc_id, jp, en in pairs:
        if not en.is_file() or not jp.is_file():
            continue
        text = en.read_text(encoding="utf-8")
        linked_to_japanese = False
        for match in MARKDOWN_LINK_RE.finditer(text):
            target = resolve_relative_link(repo_root, en, match.group(1))
            if target == jp.resolve():
                linked_to_japanese = True
                break
        if not linked_to_japanese:
            fail(
                errors,
                f"{doc_id}: English document must link to its Japanese "
                f"Source of Truth: {en.relative_to(repo_root).as_posix()}",
            )

    all_docs = [repo_root / path for path in sorted(actual_jp | actual_en)]
    validate_relative_links(repo_root, root_readmes + all_docs, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Japanese/English documentation mapping and relative links."
    )
    parser.add_argument(
        "repo",
        nargs="?",
        default=".",
        help="repository root (default: current directory)",
    )
    args = parser.parse_args()
    repo_root = Path(args.repo).resolve()
    errors = validate(repo_root)
    if errors:
        print(
            f"documentation validation failed: {len(errors)} error(s)",
            file=sys.stderr,
        )
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    mapping = json.loads(
        (repo_root / "docs" / "DOCUMENT_MAP.json").read_text(encoding="utf-8")
    )
    print(
        f"documentation validation passed: "
        f"{len(mapping['documents'])} Japanese/English pairs"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
