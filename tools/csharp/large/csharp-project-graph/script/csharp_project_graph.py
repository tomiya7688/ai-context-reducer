#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

TOOL = 'csharp-project-graph'
REF = re.compile(r'<ProjectReference\s+Include="([^"]+)"')


def build_result(root: Path):
    projects = {}
    read_errors = 0
    project_files = [
        path for path in sorted(root.rglob('*.csproj'))
        if not any(part in {'bin', 'obj'} for part in path.parts)
    ]
    for path in project_files:
        rel = path.relative_to(root).as_posix()
        refs = []
        try:
            text = path.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            read_errors += 1
            projects[rel] = refs
            continue
        for raw in REF.findall(text):
            target = (path.parent / Path(raw.replace('\\', '/'))).resolve()
            try:
                refs.append(target.relative_to(root).as_posix())
            except ValueError:
                refs.append(raw)
        projects[rel] = sorted(set(refs))
    edges = [
        {'from': source, 'to': target}
        for source, refs in sorted(projects.items())
        for target in refs
    ]
    return {
        'tool': TOOL,
        'status': 'ok_with_warnings' if read_errors else 'ok',
        'language': 'csharp',
        'root_path': str(root),
        'projects': sorted(projects),
        'project_count': len(projects),
        'edges': edges,
        'edge_count': len(edges),
        'read_error_count': read_errors,
        'scan_truncated': False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', nargs='?', default='.')
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.exists():
        print(json.dumps({'tool': TOOL, 'status': 'input_missing', 'root_path': str(root)}, indent=2))
        raise SystemExit(2)
    if not root.is_dir():
        print(json.dumps({'tool': TOOL, 'status': 'input_not_directory', 'root_path': str(root)}, indent=2))
        raise SystemExit(2)
    print(json.dumps(build_result(root), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
