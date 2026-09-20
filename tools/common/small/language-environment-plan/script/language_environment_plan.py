#!/usr/bin/env python3
import json
import platform
import shutil

LANGS = {
    'python': ('python3', 'python'),
    'csharp': ('dotnet',),
    'go': ('go',),
    'c': ('gcc', 'clang', 'cc'),
    'cpp': ('g++', 'clang++', 'c++'),
    'gdscript': ('godot4', 'godot'),
}


# first_available はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def first_available(names):
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    return ''


# main はCLI入力を解釈し、自己説明的な出力と終了状態を確定する。
def main():
    languages = {}
    for name, commands in LANGS.items():
        command = first_available(commands)
        languages[name] = {
            'available': bool(command),
            'command': command,
            'policy': 'enable if available; otherwise skip without installing dependencies',
        }
    print(json.dumps({
        'os': platform.system().lower(),
        'arch': platform.machine().lower(),
        'languages': languages,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
