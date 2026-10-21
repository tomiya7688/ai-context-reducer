"""Build and verify the actual Full Bundle, without installing dependencies."""

import argparse
import hashlib
import json
import shutil
from pathlib import Path


# {責務: [safe_path: 配布ルート外やリンク先への書込みを拒否する], 引数: [root: 基準, relative: 相対パス], 戻り値: [path: 安全なパス]}
def safe_path(root, relative):
    path = root / relative
    if Path(relative).is_absolute() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"path escapes bundle: {relative}")
    if any(part.is_symlink() for part in [path, *path.parents] if part != root.parent):
        raise ValueError(f"symlink is not allowed: {relative}")
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
    return entries


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
def build(repo, normal, gui, output, version):
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
    record = {"version": version, "files": inventory(output)}
    (output / "BUNDLE_FILES.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


# {責務: [verify: 再展開後にも欠落・追加・改変を検出する], 引数: [repo: 契約の原本, bundle: 対象, version: 期待版], 戻り値: [なし]}
def verify(repo, bundle, version):
    manifest = json.loads((repo / "release/FULL_BUNDLE_MANIFEST.json").read_text(encoding="utf-8"))
    suffix = ".exe" if (bundle / "acr-toolbox.exe").is_file() else ""
    expected = set(manifest_entries(repo, manifest, suffix))
    record = json.loads((bundle / "BUNDLE_FILES.json").read_text(encoding="utf-8"))
    actual = inventory(bundle)
    if record["version"] != version or set(actual) != expected or actual != record["files"]:
        raise ValueError("bundle inventory/version/hash mismatch")
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
    args = parser.parse_args()
    if args.action == "build":
        if args.normal is None or args.gui is None:
            parser.error("build requires --normal and --gui")
        build(args.repo.resolve(), args.normal.resolve(), args.gui.resolve(), args.bundle.resolve(), args.version)
    verify(args.repo.resolve(), args.bundle.resolve(), args.version)
    print(f"Full Bundle {args.action} passed: {args.version}")


if __name__ == "__main__":
    main()
