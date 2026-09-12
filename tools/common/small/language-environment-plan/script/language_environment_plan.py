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


def first_available(names):
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    return ''


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
