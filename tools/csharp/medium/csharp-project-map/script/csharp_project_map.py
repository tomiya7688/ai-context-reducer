#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

TOOL = 'csharp-project-map'
REF = re.compile(r'<ProjectReference\s+Include="([^"]+)"')


# C# project参照をbounded mapへ集約し、対象外や失敗をclean結果と混同しない。
def build_result(root: Path, max_source_files: int):
    projects = []
    read_errors = 0
    for csproj in sorted(root.rglob('*.csproj')):
        if any(part in {'bin', 'obj'} for part in csproj.parts):
            continue
        try:
            text = csproj.read_text(encoding='utf-8', errors='ignore')
            refs = sorted(set(REF.findall(text)))
            project_status = 'ok'
            error = None
        except OSError as exc:
            refs = []
            project_status = 'read_failed'
            error = str(exc)
            read_errors += 1
        source_files = sorted(
            p.relative_to(root).as_posix()
            for p in csproj.parent.rglob('*.cs')
            if not any(part in {'bin', 'obj'} for part in p.parts)
        )
        limit = max(0, max_source_files)
        truncated = limit > 0 and len(source_files) > limit
        returned = source_files[:limit] if limit > 0 else source_files
        row = {
            'project': csproj.relative_to(root).as_posix(),
            'status': project_status,
            'project_references': refs,
            'source_files': returned,
            'source_file_count_total': len(source_files),
            'source_files_truncated': truncated,
        }
        if error:
            row['error'] = error
        projects.append(row)
    return {
        'tool': TOOL,
        'status': 'ok_with_warnings' if read_errors else 'ok',
        'language': 'csharp',
        'root_path': str(root),
        'projects': projects,
        'project_count': len(projects),
        'read_error_count': read_errors,
    }


# CLI入力を検証し、通常結果と失敗状態を同じ機械可読JSON契約で返す。
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--max-source-files-per-project', type=int, default=300, help='0 means unlimited')
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.exists():
        print(json.dumps({'tool': TOOL, 'status': 'input_missing', 'root_path': str(root)}, indent=2))
        raise SystemExit(2)
    if not root.is_dir():
        print(json.dumps({'tool': TOOL, 'status': 'input_not_directory', 'root_path': str(root)}, indent=2))
        raise SystemExit(2)
    print(json.dumps(build_result(root, args.max_source_files_per_project), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
