#!/usr/bin/env python3
import argparse
import json
import os
import re
from pathlib import Path

TOOL = 'godot-scene-graph'
EXT = re.compile(r'^\[ext_resource\s+type="([^"]+)"\s+path="([^"]+)"', re.M)
NODE = re.compile(r'^\[node\s+name="([^"]+)"(?:\s+type="([^"]+)")?', re.M)
IGNORE_DIRS = {'.git', '.godot', 'build', 'dist', '.idea', '.vs'}


def scene_files(root: Path):
    found = []
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d.lower() not in IGNORE_DIRS)
        current_path = Path(current)
        for name in sorted(files):
            path = current_path / name
            if path.suffix.lower() == '.tscn':
                found.append(path)
    return found


def build_result(root: Path, limit: int, max_nodes_per_scene: int):
    all_scenes = scene_files(root)
    limit = max(0, limit)
    truncated = limit > 0 and len(all_scenes) > limit
    selected = all_scenes[:limit] if limit > 0 else all_scenes
    scenes = []
    read_errors = 0
    for path in selected:
        try:
            text = path.read_text(encoding='utf-8', errors='ignore')
            external = [{'type': kind, 'path': target} for kind, target in EXT.findall(text)]
            nodes_all = [{'name': name, 'type': kind or None} for name, kind in NODE.findall(text)]
            status = 'ok'
            error = None
        except OSError as exc:
            external = []
            nodes_all = []
            status = 'read_failed'
            error = str(exc)
            read_errors += 1
        node_limit = max(0, max_nodes_per_scene)
        nodes_truncated = node_limit > 0 and len(nodes_all) > node_limit
        nodes = nodes_all[:node_limit] if node_limit > 0 else nodes_all
        row = {
            'scene': path.relative_to(root).as_posix(),
            'status': status,
            'external_resources': external,
            'nodes': nodes,
            'node_count_total': len(nodes_all),
            'nodes_truncated': nodes_truncated,
        }
        if error:
            row['error'] = error
        scenes.append(row)
    return {
        'tool': TOOL,
        'status': 'ok_with_warnings' if read_errors or truncated else 'ok',
        'language': 'gdscript',
        'root_path': str(root),
        'scenes': scenes,
        'scene_count_total': len(all_scenes),
        'scenes_returned': len(scenes),
        'read_error_count': read_errors,
        'scan_truncated': truncated,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--limit', type=int, default=0, help='maximum scenes to return; 0 means unlimited')
    parser.add_argument('--max-nodes-per-scene', type=int, default=200, help='0 means unlimited')
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.exists():
        print(json.dumps({'tool': TOOL, 'status': 'input_missing', 'root_path': str(root)}, indent=2))
        raise SystemExit(2)
    if not root.is_dir():
        print(json.dumps({'tool': TOOL, 'status': 'input_not_directory', 'root_path': str(root)}, indent=2))
        raise SystemExit(2)
    print(json.dumps(build_result(root, args.limit, args.max_nodes_per_scene), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
