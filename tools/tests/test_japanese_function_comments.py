import ast
import re
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
TARGET_ROOTS = [
    TOOLS / 'python',
    TOOLS / 'go',
    TOOLS / 'c',
    TOOLS / 'cpp',
    TOOLS / 'csharp',
    TOOLS / 'gdscript',
    TOOLS / 'common' / 'small',
    TOOLS / 'common' / 'medium',
    TOOLS / 'common' / 'large',
]
JAPANESE = re.compile(r'[\u3040-\u30ff\u3400-\u9fff]')
GO_FUNC = re.compile(r'^func\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)\s*\(')


def python_comment_present(path: Path, node: ast.AST, lines: list[str]) -> bool:
    doc = ast.get_docstring(node, clean=False)
    if doc and JAPANESE.search(doc):
        return True

    start = getattr(node, 'lineno', 1) - 1
    decorators = getattr(node, 'decorator_list', [])
    if decorators:
        start = min(getattr(item, 'lineno', start + 1) for item in decorators) - 1

    index = start - 1
    while index >= 0 and not lines[index].strip():
        index -= 1

    found_comment = False
    while index >= 0 and lines[index].lstrip().startswith('#'):
        found_comment = True
        if JAPANESE.search(lines[index]):
            return True
        index -= 1
    return False and found_comment


def python_missing(path: Path) -> list[str]:
    try:
        source = path.read_text(encoding='utf-8')
        tree = ast.parse(source)
    except (OSError, SyntaxError, UnicodeError):
        return []

    lines = source.splitlines()
    missing = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not python_comment_present(path, node, lines):
            missing.append(f'{path.relative_to(TOOLS)}:{node.lineno}:{node.name}')
    return sorted(missing)


def go_comment_present(lines: list[str], function_line: int) -> bool:
    index = function_line - 2
    while index >= 0 and not lines[index].strip():
        index -= 1

    while index >= 0:
        stripped = lines[index].strip()
        if not (stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*') or stripped.endswith('*/')):
            break
        if JAPANESE.search(lines[index]):
            return True
        index -= 1
    return False


def go_missing(path: Path) -> list[str]:
    try:
        lines = path.read_text(encoding='utf-8').splitlines()
    except (OSError, UnicodeError):
        return []

    missing = []
    for number, line in enumerate(lines, 1):
        match = GO_FUNC.match(line)
        if match and not go_comment_present(lines, number):
            missing.append(f'{path.relative_to(TOOLS)}:{number}:{match.group(1)}')
    return missing


class JapaneseFunctionCommentTests(unittest.TestCase):
    def test_all_named_functions_have_japanese_context_comment(self):
        missing = []
        for root in TARGET_ROOTS:
            if not root.exists():
                continue
            for path in sorted(root.rglob('*')):
                if not path.is_file():
                    continue
                if 'common/native/acr-toolbox' in path.as_posix():
                    continue
                if path.suffix == '.py':
                    missing.extend(python_missing(path))
                elif path.suffix == '.go':
                    missing.extend(go_missing(path))

        self.assertEqual(
            [],
            missing,
            'named functions without Japanese comments/docstrings:\n' + '\n'.join(missing),
        )


if __name__ == '__main__':
    unittest.main()
