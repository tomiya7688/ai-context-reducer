#!/usr/bin/env python3
import argparse, fnmatch, json, os, subprocess, sys
from pathlib import Path


def git_changed(root, base):
    cmd = ["git", "-C", root, "diff", "--name-only"]
    if base:
        cmd.append(base)
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or "git diff failed")
    return [x.strip().replace('\\','/') for x in p.stdout.splitlines() if x.strip()]


def load_config(path):
    if not path:
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def defaults_for(path):
    p = path.replace('\\','/')
    stem = Path(p).stem
    parts = p.split('/')
    out = []
    if p.startswith("src/"):
        rel = p[4:]
        out += [f"tests/{rel}", f"tests/test_{stem}.py"]
    if "/src/" in p:
        prefix, rel = p.split('/src/', 1)
        out += [f"{prefix}/tests/{rel}", f"{prefix}/tests/test_{stem}.py"]
    return out


def uniq(items):
    seen, out = set(), []
    for x in items:
        x = x.replace('\\','/')
        if x and x not in seen:
            seen.add(x); out.append(x)
    return out


def analyze(changed, cfg):
    mappings = cfg.get("mappings", [])
    broad = cfg.get("broader_patterns", ["**/core/**", "**/shared/**", "**/schema.*", "**/api/**", "go.mod", "go.sum", "pyproject.toml", "package.json"])
    tests, reasons = [], []
    matched_explicit = False
    broader = False
    for path in changed:
        for m in mappings:
            if fnmatch.fnmatch(path, m.get("source", "")):
                matched_explicit = True
                tests += m.get("tests", [])
                if m.get("broader"):
                    broader = True; reasons.append(f"broader mapping: {path}")
        tests += defaults_for(path)
        if any(fnmatch.fnmatch(path, pat) for pat in broad):
            broader = True; reasons.append(f"broad-impact pattern: {path}")
    tests = uniq(tests)
    if not changed:
        confidence = "low"; reasons.append("no changed files")
    elif broader:
        confidence = "medium"
    elif matched_explicit:
        confidence = "high"
    elif tests:
        confidence = "medium"
    else:
        confidence = "low"; reasons.append("no mapping or naming candidate")
    fallback = "broader" if broader else ("subsystem-or-full" if confidence == "low" else "none")
    return {"changed_files": changed, "test_candidates": tests, "confidence": confidence,
            "fallback": fallback, "reasons": uniq(reasons)}


def main():
    ap = argparse.ArgumentParser(description="Lightweight affected-test selector")
    ap.add_argument("--root", default=".")
    ap.add_argument("--base", help="git diff base, e.g. origin/main...HEAD")
    ap.add_argument("--changed", nargs="*", help="explicit changed files; bypass git")
    ap.add_argument("--config", help="JSON config")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        changed = [x.replace('\\','/') for x in args.changed] if args.changed is not None else git_changed(args.root, args.base)
        result = analyze(changed, load_config(args.config))
    except Exception as e:
        print(f"affected-tests: {e}", file=sys.stderr); return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"confidence: {result['confidence']}")
        print(f"fallback: {result['fallback']}")
        print("tests:")
        for x in result["test_candidates"]: print(f"- {x}")
        if result["reasons"]:
            print("reasons:")
            for x in result["reasons"]: print(f"- {x}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
