#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

TEXT_SUFFIXES = {".py", ".md"}


def load_tasks(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("tasks.json must contain a list")
    return data


def eligible_files(project_root: Path) -> list[Path]:
    return sorted(
        path
        for path in project_root.rglob("*")
        if path.is_file() and path.suffix in TEXT_SUFFIXES
    )


def relative_paths(project_root: Path, files: list[Path]) -> list[str]:
    return [path.relative_to(project_root).as_posix() for path in files]


def select_with_literal_search(files: list[Path], terms: list[str]) -> list[Path]:
    selected: list[Path] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        if any(term in text for term in terms):
            selected.append(path)
    return selected


def measure(files: list[Path], chars_per_token: float | None) -> dict:
    texts = [path.read_text(encoding="utf-8") for path in files]
    characters = sum(len(text) for text in texts)
    result = {
        "files": len(files),
        "characters": characters,
        "utf8_bytes": sum(len(text.encode("utf-8")) for text in texts),
    }
    if chars_per_token is None:
        result["estimated_tokens"] = None
    else:
        result["estimated_tokens"] = math.ceil(characters / chars_per_token)
    return result


def reduction_percent(baseline: int, reduced: int) -> float:
    if baseline == 0:
        return 0.0
    return round(100 * (1 - reduced / baseline), 1)


def build_result(root: Path, chars_per_token: float | None = None) -> dict:
    project_root = root / "fixture"
    tasks = load_tasks(root / "tasks.json")
    all_files = eligible_files(project_root)
    all_paths = relative_paths(project_root, all_files)
    task_results: list[dict] = []

    for task in tasks:
        reduced_files = select_with_literal_search(all_files, task["search_terms"])
        reduced_paths = relative_paths(project_root, reduced_files)
        required = sorted(task["required_evidence"])
        baseline_metrics = measure(all_files, chars_per_token)
        reduced_metrics = measure(reduced_files, chars_per_token)

        task_results.append(
            {
                "id": task["id"],
                "request": task["request"],
                "search_terms": task["search_terms"],
                "required_evidence": required,
                "baseline": {
                    "strategy": "read-all-eligible-files",
                    "ai_context_files": all_paths,
                    "ai_opened_files": len(all_files),
                    "mechanical_search_commands": 0,
                    "mechanically_scanned_files": 0,
                    "metrics": baseline_metrics,
                    "required_evidence_complete": set(required).issubset(all_paths),
                },
                "context_reduced": {
                    "strategy": "literal-search-then-read-matches",
                    "ai_context_files": reduced_paths,
                    "ai_opened_files": len(reduced_files),
                    "mechanical_search_commands": 1,
                    "mechanically_scanned_files": len(all_files),
                    "metrics": reduced_metrics,
                    "required_evidence_complete": set(required).issubset(reduced_paths),
                },
                "reduction": {
                    "files_percent": reduction_percent(
                        baseline_metrics["files"], reduced_metrics["files"]
                    ),
                    "characters_percent": reduction_percent(
                        baseline_metrics["characters"], reduced_metrics["characters"]
                    ),
                    "utf8_bytes_percent": reduction_percent(
                        baseline_metrics["utf8_bytes"], reduced_metrics["utf8_bytes"]
                    ),
                },
            }
        )

    baseline_files_total = sum(
        item["baseline"]["metrics"]["files"] for item in task_results
    )
    reduced_files_total = sum(
        item["context_reduced"]["metrics"]["files"] for item in task_results
    )
    baseline_chars_total = sum(
        item["baseline"]["metrics"]["characters"] for item in task_results
    )
    reduced_chars_total = sum(
        item["context_reduced"]["metrics"]["characters"] for item in task_results
    )
    baseline_bytes_total = sum(
        item["baseline"]["metrics"]["utf8_bytes"] for item in task_results
    )
    reduced_bytes_total = sum(
        item["context_reduced"]["metrics"]["utf8_bytes"] for item in task_results
    )

    return {
        "schema_version": 1,
        "fixture": {
            "eligible_extensions": sorted(TEXT_SUFFIXES),
            "eligible_files": len(all_files),
            "tasks": len(tasks),
        },
        "measurement": {
            "characters": "Python len() over UTF-8 decoded file text",
            "utf8_bytes": "len(text.encode('utf-8'))",
            "tokens": (
                "not measured; pass --chars-per-token only for an explicitly labeled estimate"
                if chars_per_token is None
                else f"estimated as ceil(characters / {chars_per_token})"
            ),
            "mechanical_search": (
                "search scans fixture files, but only matched files are counted as AI context"
            ),
        },
        "tasks": task_results,
        "aggregate": {
            "baseline_ai_context_files": baseline_files_total,
            "context_reduced_ai_context_files": reduced_files_total,
            "baseline_characters": baseline_chars_total,
            "context_reduced_characters": reduced_chars_total,
            "baseline_utf8_bytes": baseline_bytes_total,
            "context_reduced_utf8_bytes": reduced_bytes_total,
            "files_reduction_percent": reduction_percent(
                baseline_files_total, reduced_files_total
            ),
            "characters_reduction_percent": reduction_percent(
                baseline_chars_total, reduced_chars_total
            ),
            "utf8_bytes_reduction_percent": reduction_percent(
                baseline_bytes_total, reduced_bytes_total
            ),
            "baseline_all_required_evidence_complete": all(
                item["baseline"]["required_evidence_complete"] for item in task_results
            ),
            "context_reduced_all_required_evidence_complete": all(
                item["context_reduced"]["required_evidence_complete"]
                for item in task_results
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Measure AI-visible context for a fixed synthetic fixture."
    )
    parser.add_argument(
        "--chars-per-token",
        type=float,
        default=None,
        help=(
            "Optional explicit heuristic for token estimates. The committed reference "
            "does not use this because token counts are model/tokenizer specific."
        ),
    )
    parser.add_argument(
        "--check-reference",
        action="store_true",
        help="Compare the default measurement with reference-results.json.",
    )
    args = parser.parse_args()
    if args.chars_per_token is not None and args.chars_per_token <= 0:
        parser.error("--chars-per-token must be greater than zero")
    if args.check_reference and args.chars_per_token is not None:
        parser.error("--check-reference uses the tokenizer-independent default measurement")

    root = Path(__file__).resolve().parent
    result = build_result(root, args.chars_per_token)

    if args.check_reference:
        reference = json.loads(
            (root / "reference-results.json").read_text(encoding="utf-8")
        )
        if result != reference:
            print("benchmark result differs from reference-results.json")
            return 1
        print("context-reduction benchmark reference matches")
        return 0

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
