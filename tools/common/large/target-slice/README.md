# target-slice

Return bounded excerpts around lines matching a regular expression.

```text
python tools/common/large/target-slice/script/target_slice.py PATTERN --max-matches 20 FILE [FILE...]
acr-toolbox slice --max-matches 20 PATTERN FILE [FILE...]
```

Both implementations default to 20 matches. A positive `--max-matches` value limits the returned matches, and truncation is reported only when an additional match exists beyond that limit. A value of `0` or less means unlimited matches.

The Python implementation reports this through `matches_truncated` in its JSON result. The native command prints `[truncated: max matches reached]` only when it finds an omitted match.
