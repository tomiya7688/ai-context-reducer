#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from validate_documentation import validate


class DocumentationValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "docs" / "jp").mkdir(parents=True)
        (self.root / "docs" / "en").mkdir(parents=True)
        self.jp = self.root / "docs" / "jp" / "日本語.md"
        self.en = self.root / "docs" / "en" / "example.md"
        self.jp.write_text("# 日本語\n\n本文。\n", encoding="utf-8")
        self.en.write_text(
            "# Example\n\n"
            "> Japanese Source of Truth: [日本語](../jp/日本語.md)\n",
            encoding="utf-8",
        )
        (self.root / "README.md").write_text(
            "# Example\n\n"
            "日本語 | [English](README.en.md)\n\n"
            "[日本語 docs](docs/jp/)\n\n"
            "[Releases](https://github.com/tomiya7688/ai-context-reducer/releases)\n",
            encoding="utf-8",
        )
        (self.root / "README.en.md").write_text(
            "# Example\n\n"
            "English | [日本語](README.md)\n\n"
            "[English docs](docs/en/)\n\n"
            "[Releases](https://github.com/tomiya7688/ai-context-reducer/releases)\n",
            encoding="utf-8",
        )
        self.write_mapping()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_mapping(self, documents: list[dict] | None = None) -> None:
        data = {
            "schema_version": 1,
            "source_of_truth_language": "ja",
            "japanese_root": "docs/jp",
            "english_root": "docs/en",
            "mapping_source_of_truth": "docs/DOCUMENT_MAP.json",
            "filename_policy": {
                "japanese": "Japanese filenames are required under docs/jp.",
                "english": "English filenames are required under docs/en.",
                "filenames_do_not_need_to_match_across_languages": True,
            },
            "translation_policy": {
                "japanese_documents_are_authoritative": True,
                "english_documents_are_translations": True,
                "english_must_not_add_requirements_absent_from_japanese": True,
            },
            "documents": documents
            or [
                {
                    "id": "example",
                    "japanese": "docs/jp/日本語.md",
                    "english": "docs/en/example.md",
                    "english_status": "translated",
                }
            ],
        }
        (self.root / "docs" / "DOCUMENT_MAP.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def assert_error_contains(self, needle: str) -> None:
        errors = validate(self.root)
        self.assertTrue(any(needle in error for error in errors), errors)

    def test_valid_pair_passes(self) -> None:
        self.assertEqual([], validate(self.root))

    def test_missing_english_file_is_detected(self) -> None:
        self.en.unlink()
        self.assert_error_contains("missing English file")

    def test_missing_japanese_file_is_detected(self) -> None:
        self.jp.unlink()
        self.assert_error_contains("missing Japanese file")

    def test_unregistered_document_is_detected(self) -> None:
        (self.root / "docs" / "en" / "orphan.md").write_text(
            "# Orphan\n", encoding="utf-8"
        )
        self.assert_error_contains("unregistered English document")

    def test_duplicate_mapping_target_is_detected(self) -> None:
        self.write_mapping(
            [
                {
                    "id": "one",
                    "japanese": "docs/jp/日本語.md",
                    "english": "docs/en/example.md",
                },
                {
                    "id": "two",
                    "japanese": "docs/jp/日本語.md",
                    "english": "docs/en/example.md",
                },
            ]
        )
        self.assert_error_contains("duplicate Japanese mapping target")
        self.assert_error_contains("duplicate English mapping target")

    def test_broken_relative_link_is_detected(self) -> None:
        self.en.write_text(
            "# Example\n\n"
            "> Japanese Source of Truth: [日本語](../jp/日本語.md)\n\n"
            "[Missing](missing.md)\n",
            encoding="utf-8",
        )
        self.assert_error_contains("broken relative link")

    def test_missing_language_navigation_is_detected(self) -> None:
        self.en.write_text("# Example\n", encoding="utf-8")
        self.assert_error_contains("must link to its Japanese Source of Truth")

    def test_escaped_markdown_backtick_is_detected(self) -> None:
        (self.root / "README.en.md").write_text(
            "# Example\n\n"
            "English | [日本語](README.md)\n\n"
            "[English docs](docs/en/)\n\n"
            "[Releases](https://github.com/tomiya7688/ai-context-reducer/releases)\n\n"
            "\\\`broken\\\`\n",
            encoding="utf-8",
        )
        self.assert_error_contains("escaped backtick breaks Markdown code formatting")

    def test_missing_root_language_switch_is_detected(self) -> None:
        (self.root / "README.en.md").write_text(
            "# Example\n\n"
            "[English docs](docs/en/)\n\n"
            "[Releases](https://github.com/tomiya7688/ai-context-reducer/releases)\n",
            encoding="utf-8",
        )
        self.assert_error_contains("README.en.md must link to README.md")

    def test_missing_docs_entry_is_detected(self) -> None:
        (self.root / "README.md").write_text(
            "# Example\n\n"
            "[English](README.en.md)\n\n"
            "[Releases](https://github.com/tomiya7688/ai-context-reducer/releases)\n",
            encoding="utf-8",
        )
        self.assert_error_contains("README.md must link to docs/jp")

    def test_missing_release_entry_is_detected(self) -> None:
        (self.root / "README.en.md").write_text(
            "# Example\n\n"
            "[日本語](README.md)\n\n"
            "[English docs](docs/en/)\n",
            encoding="utf-8",
        )
        self.assert_error_contains("README.en.md must link to GitHub Releases")


if __name__ == "__main__":
    unittest.main()
