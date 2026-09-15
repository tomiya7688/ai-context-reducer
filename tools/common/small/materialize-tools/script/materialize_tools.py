#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from selection import choose

TOOL = 'materialize-tools'
MANIFEST_FORMAT = 'acr-materialized-tools-v1'
MANIFEST_NAME = '.acr-materialized-tools.json'


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def source_revision(source: Path) -> str | None:
    if not shutil.which('git'):
        return None
    try:
        result = subprocess.run(
            ['git', '-C', str(source), 'rev-parse', 'HEAD'],
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return None
    value = result.stdout.strip()
    return value if result.returncode == 0 and value else None


def source_relative(path: Path, source: Path) -> str:
    try:
        return path.resolve().relative_to(source.resolve()).as_posix()
    except (OSError, ValueError):
        return path.as_posix()


def plan_materialization(source: Path, out: Path, selected: list[dict[str, object]], overwrite: bool) -> tuple[list[dict], list[str]]:
    actions = []
    missing_sources = []
    for row in selected:
        src = Path(row['source'])
        relative = Path(row['destination'])
        destination = out / relative
        if not src.is_file():
            missing_sources.append(source_relative(src, source))
            continue
        source_hash = sha256_file(src)
        if not destination.exists():
            destination_state = 'missing'
            action = 'create'
        elif not destination.is_file():
            destination_state = 'not_a_file'
            action = 'conflict'
        else:
            destination_hash = sha256_file(destination)
            if destination_hash == source_hash:
                destination_state = 'identical'
                action = 'unchanged'
            else:
                destination_state = 'different'
                action = 'overwrite' if overwrite else 'conflict'
        actions.append({
            'source_path': source_relative(src, source),
            'destination_path': relative.as_posix(),
            'role': str(row['role']),
            'source_sha256': source_hash,
            'destination_state': destination_state,
            'planned_action': action,
        })
    return actions, sorted(missing_sources)


def manifest_payload(mode: str, revision: str | None, actions: list[dict]) -> dict:
    return {
        'format': MANIFEST_FORMAT,
        'implementation_mode': mode,
        'source_revision': revision,
        'files': [
            {
                'path': row['destination_path'],
                'role': row['role'],
                'source_path': row['source_path'],
                'sha256': row['source_sha256'],
            }
            for row in actions
        ],
    }


def atomic_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix='.acr-copy-', dir=destination.parent)
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        shutil.copy2(source, temporary)
        os.replace(temporary, destination)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix='.acr-manifest-', dir=path.parent)
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def execute(source: Path, out: Path, apply: bool, overwrite: bool) -> dict:
    base = {
        'tool': TOOL,
        'source_root': str(source),
        'output_root': str(out),
        'apply_requested': apply,
        'overwrite_requested': overwrite,
        'manifest_path': str(out / MANIFEST_NAME),
    }
    if not source.exists():
        return {**base, 'status': 'input_missing', 'implementation_mode': None, 'applied': False, 'actions': []}
    if not source.is_dir():
        return {**base, 'status': 'input_not_directory', 'implementation_mode': None, 'applied': False, 'actions': []}

    mode, selected = choose(source)
    revision = source_revision(source)
    if mode == 'unavailable':
        return {
            **base,
            'status': 'implementation_unavailable',
            'implementation_mode': mode,
            'source_revision': revision,
            'applied': False,
            'actions': [],
        }

    try:
        actions, missing_sources = plan_materialization(source, out, selected, overwrite)
    except OSError as exc:
        return {
            **base,
            'status': 'plan_failed',
            'implementation_mode': mode,
            'source_revision': revision,
            'applied': False,
            'error': str(exc),
            'actions': [],
        }

    result = {
        **base,
        'implementation_mode': mode,
        'source_revision': revision,
        'applied': False,
        'missing_source_files': missing_sources,
        'actions': actions,
    }
    if missing_sources:
        result['status'] = 'source_selection_incomplete'
        return result

    conflicts = [row['destination_path'] for row in actions if row['planned_action'] == 'conflict']
    if conflicts:
        result['status'] = 'conflict'
        result['conflicting_destination_paths'] = conflicts
        return result

    if not apply:
        result['status'] = 'ok'
        return result

    try:
        selected_by_destination = {Path(row['destination']).as_posix(): Path(row['source']) for row in selected}
        for action in actions:
            if action['planned_action'] not in {'create', 'overwrite'}:
                continue
            relative = action['destination_path']
            atomic_copy(selected_by_destination[relative], out / relative)
        atomic_write_json(out / MANIFEST_NAME, manifest_payload(mode, revision, actions))
    except OSError as exc:
        result['status'] = 'apply_failed'
        result['error'] = str(exc)
        return result

    result['status'] = 'ok'
    result['applied'] = True
    return result


def main():
    parser = argparse.ArgumentParser(description='Safely materialize usable portable tool variants as self-describing JSON.')
    parser.add_argument('source', nargs='?', default='.')
    parser.add_argument('--out', required=True)
    parser.add_argument('--apply', action='store_true', help='Apply the plan. Default is preview only.')
    parser.add_argument('--overwrite', action='store_true', help='Plan/allow replacement of different destination files instead of reporting conflict.')
    args = parser.parse_args()

    result = execute(Path(args.source).resolve(), Path(args.out).resolve(), args.apply, args.overwrite)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
