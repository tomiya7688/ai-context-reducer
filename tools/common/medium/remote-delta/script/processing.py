from __future__ import annotations


def render_remote_delta(data: dict[str, object], max_files: int) -> str:
    if not data.get('remote_available'):
        return (
            'remote=unavailable\n'
            + 'local_changes=' + ('yes' if data.get('dirty') else 'no') + '\n'
        )

    lines = [
        f"ahead={data.get('ahead', '0')} behind={data.get('behind', '0')} dirty={'yes' if data.get('dirty') else 'no'}"
    ]
    stat = str(data.get('stat') or '')
    if stat:
        lines.append('diff=' + stat)

    names = list(data.get('changed_files', []))
    lines.append('changed_files:')
    lines.extend('  ' + str(name) for name in names[:max_files])
    if len(names) > max_files:
        lines.append(f'  ... truncated {len(names) - max_files} more')

    commits = list(data.get('remote_commits', []))
    if commits:
        lines.append('remote_commits:')
        lines.extend('  ' + str(item) for item in commits)
    return '\n'.join(lines) + '\n'
