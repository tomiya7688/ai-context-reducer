# Tool JSON Contract

Agent-facing machine output is JSON by default when JSON is the tool's natural result format.

## Goals

- The output should be understandable without reopening the tool README or `--help`.
- The same fact should not be repeated as both prose and structured data.
- Empty success, unavailable input, partial/truncated output, and failure must be distinguishable from the JSON alone.
- Field names should carry meaning directly.

## Required conventions

Use a short tool identifier and an explicit status:

```json
{
  "tool": "remote-delta",
  "status": "ok"
}
```

Prefer semantic field names such as:

- `changed_files`
- `changed_files_truncated`
- `scanned_files`
- `remote_available`
- `confidence`
- `reasons`

Avoid opaque keys such as `data`, `result`, `items`, or `value` when a more specific name is practical.

## Status and absence

Do not use an empty list/string to hide an acquisition failure.

```text
successful empty result -> status=ok + empty collection
unavailable dependency  -> explicit unavailable status/field
failed query            -> explicit failure status
bounded partial result  -> truncated=true
unknown value           -> null
```

Do not invent placeholder values such as `0`, `false`, or `[]` when the value is actually unknown.

## Compactness

Do not include both a prose `summary` and fields that encode the same facts.
Do not embed README/help text in normal output.
Do not include full source/log/document content unless the tool's purpose explicitly requires it.

Nested objects are useful only when they reduce ambiguity or repeated prefixes. Shallow JSON is preferred for small results.

## Human usability

JSON intended for both agents and humans should be pretty-printed and use stable, readable names. A separate text mode is not required merely for presentation.

Tools whose actual artifact is Markdown/text (for example a Context Pack generator) may emit that artifact instead of JSON.


## Language analyzer minimum contract

Language-specific symbol analyzers should keep file-level failures distinguishable from a valid file with zero symbols.

```json
{
  "tool": "python-symbols",
  "status": "ok_with_warnings",
  "language": "python",
  "files": [
    {
      "file": "src/example.py",
      "status": "parse_failed",
      "symbols": [],
      "error": "..."
    }
  ],
  "file_count": 1,
  "symbol_count": 0,
  "parse_error_count": 1,
  "read_error_count": 0,
  "unsupported_input_count": 0,
  "unsupported_inputs": []
}
```

A file row with `status=ok` and `symbols=[]` means analysis succeeded and no symbols were found. Parse/read failure must use a different file status. Unsupported or missing explicit inputs must not disappear silently.

Downstream indexes may accept older list-only analyzer output for compatibility, but new analyzer output should use the self-describing object form.

## Compatibility

Treat field removal, renaming, type changes, or status semantic changes as output-contract changes. Validate them with targeted contract tests. Python and Go implementations that advertise the same CLI contract should produce semantically equivalent fields, even when their internals are independent.
