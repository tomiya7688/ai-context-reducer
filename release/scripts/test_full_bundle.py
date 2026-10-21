"""Regression checks for release staging and archive integrity."""

import json
import tempfile
import unittest
from pathlib import Path

from full_bundle import build, verify
from archive_tools import extract, pack


# {責務: [FullBundleTests: 欠落・改変・追加ファイルを検出する契約を検証する]}
class FullBundleTests(unittest.TestCase):
    # {責務: [setUp: 実行環境に依存しない最小の配布原本を用意する]}
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo, self.normal, self.out = [self.root / name for name in ("repo", "normal", "out")]
        (self.repo / "release").mkdir(parents=True)
        self.normal.mkdir()
        self.gui = self.root / "acr-hub"
        self.gui.write_text("gui", encoding="utf-8")
        (self.normal / "acr-toolbox").write_text("native", encoding="utf-8")
        (self.normal / "RELEASE_MANIFEST.json").write_text('{"release_version":"1.0.0"}', encoding="utf-8")
        self.manifest = {
            "root_files": [
                {"bundle_path": "acr-toolbox{exe}", "kind": "prebuilt_go_binary"},
                {"bundle_path": "RELEASE_MANIFEST.json", "kind": "document", "normal_bundle_compatible": True},
                {"bundle_path": "FULL_BUNDLE_MANIFEST.json", "kind": "document", "source": "release/FULL_BUNDLE_MANIFEST.json"},
            ],
            "gui_files": [{"bundle_path": "gui/acr-hub{exe}", "kind": "prebuilt_gui_entrypoint"}],
            "setup_files": [{"bundle_path": "setup.sh", "kind": "bundle_wrapper"}],
            "python_fallback_files": [], "profile_files": [], "template_files": [], "documentation_trees": [],
        }
        self.save_manifest()

    # {責務: [save_manifest: テストの明示的な契約を書き込む]}
    def save_manifest(self):
        (self.repo / "release/FULL_BUNDLE_MANIFEST.json").write_text(json.dumps(self.manifest), encoding="utf-8")

    # {責務: [stage: 本物のビルド関数で配布物を作る]}
    def stage(self):
        build(self.repo, self.normal, self.gui, self.out, "1.0.0")

    # {責務: [test_build_and_verify: GUIとラッパーを含む正しい配布物を受け入れる]}
    def test_build_and_verify(self):
        self.stage()
        verify(self.repo, self.out, "1.0.0")
        self.assertEqual("gui", (self.out / "gui/acr-hub").read_text())
        self.assertIn('"$SELF/acr-toolbox" analyze', (self.out / "setup.sh").read_text())

    # {責務: [test_missing_gui_is_rejected_before_output: GUI欠落を半端な出力作成前に検出する]}
    def test_missing_gui_is_rejected_before_output(self):
        self.gui.unlink()
        with self.assertRaises(ValueError):
            self.stage()
        self.assertFalse(self.out.exists())

    # {責務: [test_tampering_missing_and_extra_files: 改変・欠落・余計なファイルを拒否する]}
    def test_tampering_missing_and_extra_files(self):
        self.stage()
        target = self.out / "gui/acr-hub"
        target.write_text("tampered", encoding="utf-8")
        with self.assertRaises(ValueError):
            verify(self.repo, self.out, "1.0.0")
        target.unlink()
        with self.assertRaises(ValueError):
            verify(self.repo, self.out, "1.0.0")
        target.write_text("gui", encoding="utf-8")
        (self.out / "extra").mkdir()
        (self.out / "extra/BUNDLE_FILES.json").write_text("hidden extra", encoding="utf-8")
        with self.assertRaises(ValueError):
            verify(self.repo, self.out, "1.0.0")

    # {責務: [test_version_and_existing_destination: 版違いと既存出力の上書きを拒否する]}
    def test_version_and_existing_destination(self):
        self.stage()
        with self.assertRaises(ValueError):
            verify(self.repo, self.out, "2.0.0")
        with self.assertRaises(ValueError):
            self.stage()

    # {責務: [test_path_escape: マニフェスト経由の配布先外参照を拒否する]}
    def test_path_escape(self):
        self.manifest["template_files"] = [{"source": "../secret", "bundle_path": "secret", "kind": "document"}]
        self.save_manifest()
        with self.assertRaises(ValueError):
            self.stage()
        self.assertFalse(self.out.exists())

    # {責務: [test_document_links_and_exclusions: 未同梱の参照を固定しコード例を保つ]}
    def test_document_links_and_exclusions(self):
        (self.repo / "guide.md").write_text('[source](source.py)\n```markdown\n[example](missing.md)\n```\n', encoding="utf-8")
        (self.repo / "source.py").write_text("pass\n", encoding="utf-8")
        self.manifest["template_files"] = [{"source": "guide.md", "bundle_path": "guide.md", "kind": "document"}]
        self.save_manifest()
        self.stage()
        text = (self.out / "guide.md").read_text(encoding="utf-8")
        self.assertIn('github.com/tomiya7688/ai-context-reducer/blob/main/source.py', text)
        self.assertIn('[example](missing.md)', text)
        verify(self.repo, self.out, "1.0.0")

    # {責務: [test_excluded_sources: 同梱禁止のソースをマニフェストでも許可しない]}
    def test_excluded_sources(self):
        self.manifest["excluded_from_full_bundle"] = ["**/*.go"]
        self.manifest["template_files"] = [{"source": "secret.go", "bundle_path": "secret.go", "kind": "document"}]
        self.save_manifest()
        with self.assertRaises(ValueError):
            self.stage()

    # {責務: [test_archive_roundtrip: 日本語パスを含むzipとtarの再展開を照合する]}
    def test_archive_roundtrip(self):
        (self.repo / "日本語.md").write_text("# 日本語\n", encoding="utf-8")
        self.manifest["template_files"] = [{"source": "日本語.md", "bundle_path": "docs/日本語.md", "kind": "document"}]
        self.save_manifest()
        self.stage()
        for suffix in (".zip", ".tar.gz"):
            archive = self.root / ("candidate" + suffix)
            destination = self.root / ("extracted" + suffix)
            pack(self.out, archive)
            extract(archive, destination)
            verify(self.repo, destination / self.out.name, "1.0.0")

    # {責務: [test_unsafe_archive: 展開先外へのファイル作成を拒否する]}
    def test_unsafe_archive(self):
        import zipfile
        archive = self.root / "unsafe.zip"
        with zipfile.ZipFile(archive, "w") as output:
            output.writestr("../outside", "no")
        with self.assertRaises(ValueError):
            extract(archive, self.root / "extracted")
        self.assertFalse((self.root / "outside").exists())


if __name__ == "__main__":
    unittest.main()
