from __future__ import annotations


# _git_failure_line はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def _git_failure_line(error_kind: object, query_name: str) -> str:
    if error_kind == 'git_unavailable':
        return '- Git unavailable\n'
    return f'- unavailable: {query_name} query failed\n'


# render_context_pack は内部結果を安定した利用者向け表現へ変換する。
def render_context_pack(task: dict[str, str], state: dict[str, object]) -> str:
    changed = list(state.get('changed', []))
    status = list(state.get('status', []))
    text = '# Context Pack\n\n## Task\n'
    text += f"- Goal: {task.get('goal', '')}\n"
    text += f"- Required: {task.get('required', '')}\n"
    text += f"- Acceptance: {task.get('acceptance', '')}\n"
    text += f"- Deferred / out of scope: {task.get('deferred', '')}\n"

    text += '\n## Working Set\n- Changed files:\n'
    if not state.get('changed_query_ok', True):
        if state.get('changed_error_kind') == 'git_unavailable':
            text += '  - Git unavailable\n'
        else:
            text += '  - unavailable: git diff query failed\n'
    else:
        text += ''.join(f'  - {item}\n' for item in changed) or '  - none detected\n'
        if state.get('changed_truncated'):
            text += '  - ... truncated\n'

    text += '\n## Git Status\n'
    if not state.get('status_query_ok', True):
        text += _git_failure_line(state.get('status_error_kind'), 'git status')
    else:
        text += ''.join(f'- {item}\n' for item in status) or '- clean\n'
        if state.get('status_truncated'):
            text += '- ... truncated\n'

    text += '\n## Required Constraints\n- \n'
    text += '\n## Validation\n- Targeted evidence:\n- Unverified areas:\n'
    text += '\n## Rules\n- Search first, read second.\n'
    text += '- Stop exploration once Goal / Required / Acceptance / working set are sufficient.\n'
    text += '- Return to source of truth only when details are needed.\n'
    return text
