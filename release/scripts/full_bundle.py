"""Build and verify the actual Full Bundle, without installing dependencies."""

import argparse
import fnmatch
import hashlib
import json
import re
import shutil
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit


# {責務: [safe_path: 配布ルート外やリンク先への書込みを拒否する], 引数: [root: 基準, relative: 相対パス], 戻り値: [path: 安全なパス]}
def safe_path(root, relative):
    path = root / relative
    if Path(relative).is_absolute() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"path escapes bundle: {relative}")
    for part in [path, *path.parents]:
        if part.is_symlink():
            raise ValueError(f"symlink is not allowed: {relative}")
        if part == root:
            break
    return path


# {責務: [wrapper: 追加環境なしで同梱CLIだけを呼ぶ入口を作る], 引数: [name: ファイル名], 戻り値: [text: ラッパー本文]}
def wrapper(name):
    commands = ["analyze"] if name.startswith("analyze") else [
        "env", "language-env", "analyze", "language-setup", "language-run"
    ]
    if name.endswith(".bat"):
        lines = ['@echo off', 'setlocal', 'set "ROOT=%~1"', 'if not defined ROOT set "ROOT=."']
        for command in commands:
            args = '' if command in ("env", "language-env") else ' "%ROOT%"'
            lines += [f'"%~dp0acr-toolbox.exe" {command}{args}', 'if errorlevel 1 exit /b %errorlevel%']
        return '\r\n'.join(lines + ['exit /b 0', ''])
    lines = ['#!/bin/sh', 'set -eu', 'SELF=${0%/*}', '[ "$SELF" != "$0" ] || SELF=.', 'SELF=$(CDPATH= cd -- "$SELF" && pwd)', 'ROOT=${1:-.}']
    for command in commands:
        args = '' if command in ("env", "language-env") else ' "$ROOT"'
        lines.append(f'"$SELF/acr-toolbox" {command}{args}')
    return '\n'.join(lines) + '\n'


# {責務: [manifest_entries: 明示された配布対象を解決する], 引数: [repo: 原本, manifest: 契約, suffix: 実行形式], 戻り値: [entries: 配布先と原本]}
def manifest_entries(repo, manifest, suffix):
    entries = {}
    for group in ("root_files", "gui_files", "setup_files", "python_fallback_files", "profile_files", "template_files"):
        for item in manifest[group]:
            destination = item["bundle_path"].replace("{exe}", suffix)
            if destination in entries:
                raise ValueError(f"duplicate bundle path: {destination}")
            entries[destination] = item
    for tree in manifest["documentation_trees"]:
        source = safe_path(repo, tree["source"])
        files = sorted(source.glob(tree["include"]))
        if not files and tree.get("required_for_release"):
            raise ValueError(f"empty documentation tree: {source}")
        for file in files:
            destination = (Path(tree["bundle_path"]) / file.relative_to(source)).as_posix()
            if destination in entries:
                raise ValueError(f"duplicate bundle path: {destination}")
            entries[destination] = {"source": file.relative_to(repo).as_posix(), "kind": "document"}
    for destination in entries:
        for pattern in manifest.get("excluded_from_full_bundle", []):
            if fnmatch.fnmatchcase(destination, pattern) or fnmatch.fnmatchcase(destination, pattern.removeprefix("**/")):
                raise ValueError(f"excluded bundle entry: {destination}")
    return entries


# {責務: [document_links: 同梱しない原本への参照を版固定URLへ変換する], 引数: [repo: 原本, bundle: 配布先, entries: 対応表, commit: 参照版], 戻り値: [なし]}
def document_links(repo, bundle, entries, commit):
    for destination, item in entries.items():
        if not destination.endswith(".md") or item.get("normal_bundle_compatible"):
            continue
        source = repo / item["source"]
        target = bundle / destination

        # {責務: [replace: 未同梱の参照先だけを原本URLへ向ける], 引数: [match: Markdownリンク], 戻り値: [text: 置換結果]}
        def replace(match):
            raw = match.group(2).strip().strip("<>")
            parts = urlsplit(raw)
            if parts.scheme or parts.netloc or not parts.path or raw.startswith("/"):
                return match.group(0)
            relative = unquote(parts.path.strip("<>"))
            if (target.parent / relative).exists():
                return match.group(0)
            original = (source.parent / relative).resolve()
            if not original.is_relative_to(repo.resolve()) or not original.exists():
                raise ValueError(f"unresolvable documentation link: {destination}: {raw}")
            route = "raw.githubusercontent.com/tomiya7688/ai-context-reducer" if match.group(1).startswith("!") else "github.com/tomiya7688/ai-context-reducer/blob"
            url = f"https://{route}/{commit}/{quote(original.relative_to(repo).as_posix())}"
            if parts.fragment:
                url += "#" + parts.fragment
            return match.group(1) + url + match.group(3)

        lines, fenced = [], False
        for line in target.read_text(encoding="utf-8").splitlines(keepends=True):
            if line.lstrip().startswith(("```", "~~~")):
                fenced = not fenced
            elif not fenced:
                line = re.sub(r'(!?\[[^\]\n]*\]\()([^\n)]+)(\))', replace, line)
                line = re.sub(r'^(\[[^\]\n]+\]:\s*)(<[^>]+>|[^\s]+)(.*)$', replace, line)
            lines.append(line)
        target.write_text("".join(lines), encoding="utf-8")


# {責務: [inventory: 配布物の全ファイルをハッシュ付きで記録する], 引数: [bundle: 配布ルート], 戻り値: [files: 相対パスとハッシュ]}
def inventory(bundle):
    files = {}
    for path in sorted(bundle.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symlink in distribution: {path}")
        if path.is_file() and path.relative_to(bundle).as_posix() != "BUNDLE_FILES.json":
            files[path.relative_to(bundle).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


# {責務: [build: 原本とビルド済み成果物から同梱版を作る], 引数: [repo: 原本, normal: 通常版, gui: GUI, output: 新規出力先, version: 版], 戻り値: [なし]}
def build(repo, normal, gui, output, version, commit="main"):
    if output.exists():
        raise ValueError(f"output already exists: {output}")
    manifest = json.loads((repo / "release/FULL_BUNDLE_MANIFEST.json").read_text(encoding="utf-8"))
    suffix = ".exe" if (normal / "acr-toolbox.exe").is_file() else ""
    entries = manifest_entries(repo, manifest, suffix)
    # Validate every source before creating a partially populated candidate.
    sources = {}
    for destination, item in entries.items():
        if item["kind"] == "bundle_wrapper":
            continue
        if item["kind"] == "prebuilt_go_binary":
            source = safe_path(normal, destination)
        elif item["kind"] == "prebuilt_gui_entrypoint":
            source = gui
        elif item.get("normal_bundle_compatible"):
            source = safe_path(normal, destination)
        else:
            source = safe_path(repo, item["source"])
        safe_path(output, destination)
        if not source.is_file() or source.is_symlink():
            raise ValueError(f"missing or linked source: {source}")
        sources[destination] = source
    output.mkdir(parents=True)
    for destination, item in entries.items():
        target = safe_path(output, destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        if item["kind"] == "bundle_wrapper":
            target.write_bytes(wrapper(destination).encode("utf-8"))
            target.chmod(0o755)
        else:
            shutil.copy2(sources[destination], target)
    candidate_manifest = output / "FULL_BUNDLE_MANIFEST.json"
    manifest["target_release_version"] = version
    manifest["artifact_status"] = "candidate_under_validation"
    candidate_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    document_links(repo, output, entries, commit)
    record = {"version": version, "source_commit": commit, "files": inventory(output)}
    (output / "BUNDLE_FILES.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


# {責務: [verify: 再展開後にも欠落・追加・改変を検出する], 引数: [repo: 契約の原本, bundle: 対象, version: 期待版], 戻り値: [なし]}
def verify(repo, bundle, version):
    manifest = json.loads((repo / "release/FULL_BUNDLE_MANIFEST.json").read_text(encoding="utf-8"))
    suffix = ".exe" if (bundle / "acr-toolbox.exe").is_file() else ""
    expected = set(manifest_entries(repo, manifest, suffix))
    record = json.loads((bundle / "BUNDLE_FILES.json").read_text(encoding="utf-8"))
    actual = inventory(bundle)
    missing = sorted(expected - set(actual))
    extra = sorted(set(actual) - expected)
    changed = sorted(path for path in actual if actual[path] != record["files"].get(path))
    if record["version"] != version or missing or extra or changed or set(record["files"]) != expected:
        raise ValueError(f"bundle mismatch: missing={missing}, extra={extra}, changed={changed}")
    for path in ("RELEASE_MANIFEST.json", "FULL_BUNDLE_MANIFEST.json"):
        data = json.loads((bundle / path).read_text(encoding="utf-8"))
        key = "release_version" if path == "RELEASE_MANIFEST.json" else "target_release_version"
        if data[key] != version:
            raise ValueError(f"manifest version mismatch: {path}")


# {責務: [main: ビルドと検証を明示的に切り替える], 戻り値: [なし]}
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "verify"))
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--normal", type=Path)
    parser.add_argument("--gui", type=Path)
    parser.add_argument("--source-commit", default="main")
    args = parser.parse_args()
    if args.action == "build":
        if args.normal is None or args.gui is None:
            parser.error("build requires --normal and --gui")
        build(args.repo.resolve(), args.normal.resolve(), args.gui.resolve(), args.bundle.resolve(), args.version, args.source_commit)
    verify(args.repo.resolve(), args.bundle.resolve(), args.version)
    print(f"Full Bundle {args.action} passed: {args.version}")


if __name__ == "__main__":
    main()
