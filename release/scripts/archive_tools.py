"""Portable archive creation and safe extraction for release candidates."""

import argparse
import stat
import tarfile
import zipfile
from pathlib import Path


# {責務: [pack: OS固有の隠しメタデータを足さず配布物を圧縮する], 引数: [bundle: 配布先, archive: 新規アーカイブ], 戻り値: [なし]}
def pack(bundle, archive):
    if archive.exists():
        raise ValueError(f"archive exists: {archive}")
    if not bundle.is_dir() or any(path.is_symlink() for path in bundle.rglob("*")):
        raise ValueError("bundle must be a directory without symlinks")
    if archive.suffix == ".zip":
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
            for path in sorted(bundle.rglob("*")):
                if path.is_file():
                    output.write(path, path.relative_to(bundle.parent).as_posix())
    elif archive.name.endswith(".tar.gz"):
        with tarfile.open(archive, "w:gz", format=tarfile.PAX_FORMAT) as output:
            output.add(bundle, arcname=bundle.name)
    else:
        raise ValueError("unsupported archive type")


# {責務: [extract: 出力先外の参照や既存内容の上書きを拒否して展開する], 引数: [archive: 対象, destination: 空の展開先], 戻り値: [なし]}
def extract(archive, destination):
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("extraction requires an empty destination")
    destination.mkdir(parents=True, exist_ok=True)
    if archive.suffix == ".zip":
        with zipfile.ZipFile(archive) as source:
            for item in source.infolist():
                path = destination / item.filename
                if not path.resolve().is_relative_to(destination.resolve()) or stat.S_ISLNK(item.external_attr >> 16):
                    raise ValueError(f"unsafe zip member: {item.filename}")
            source.extractall(destination)
    elif archive.name.endswith(".tar.gz"):
        with tarfile.open(archive, "r:gz") as source:
            for item in source.getmembers():
                if not (item.isfile() or item.isdir()):
                    raise ValueError(f"unsafe tar member: {item.name}")
            source.extractall(destination, filter="data")
    else:
        raise ValueError("unsupported archive type")


# {責務: [main: 圧縮と展開の引数を検証する], 戻り値: [なし]}
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("pack", "extract"))
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    if args.action == "pack":
        pack(args.source.resolve(), args.destination.resolve())
    else:
        extract(args.source.resolve(), args.destination.resolve())


if __name__ == "__main__":
    main()
