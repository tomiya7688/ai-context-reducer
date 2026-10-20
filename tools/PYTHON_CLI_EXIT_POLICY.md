# Python CLI status and process exit policy

The JSON `status` and the process exit code are one contract for these Python
CLIs. A consumer may use either field to decide whether the requested
operation succeeded.

| Status | Exit code | Meaning |
| --- | ---: | --- |
| `ok` | 0 | Requested analysis completed. |
| `ok_with_warnings` | 0 | Analysis completed with explicitly reported partial-read warnings. Results remain usable; inspect warning counters/paths. |
| `remote_unavailable` (`remote-delta` only) | 0 | The local repository was inspected, but the optional remote ref is absent or unavailable. Remote comparison is intentionally optional. |
| `backend_unavailable`, `backend_unavailable_for_language` (`structural-search` only) | 0 | The optional ast-grep backend or requested language is unavailable. The JSON explains that no search was performed and lists available fallback languages. |
| Any other result status | 2 | The requested operation could not be completed, including invalid input/query, missing or non-directory roots, Git failures, or a failed search. |
| argparse syntax/type errors | 2 | The command line itself is invalid; argparse writes its diagnostic to stderr. |

All bounded numeric options reject negative values. `0` retains the documented
meaning for unlimited/empty limits. This policy covers:

| CLI | Entrypoint | Optional zero-exit status |
| --- | --- | --- |
| analyze-and-recommend | `tools/common/small/analyze-and-recommend/script/analyze_and_recommend.py` | — |
| tree-view | `tools/common/small/tree-view/script/tree_view.py` | — |
| doc-index | `tools/common/small/doc-index/script/doc_index.py` | — |
| file-role-map | `tools/common/small/file-role-map/script/file_role_map.py` | — |
| tool-selector | `tools/common/small/tool-selector/script/tool_selector.py` | — |
| source-of-truth-candidates | `tools/common/small/source-of-truth-candidates/script/source_of_truth_candidates.py` | — |
| context-budget | `tools/common/large/context-budget/script/context_budget.py` | — |
| hotspot-report | `tools/common/large/hotspot-report/script/hotspot_report.py` | — |
| structural-search | `tools/common/medium/structural-search/script/structural_search.py` | `backend_unavailable`, `backend_unavailable_for_language` |
| compact-diff | `tools/common/medium/compact-diff/script/compact_diff.py` | — |
| remote-delta | `tools/common/medium/remote-delta/script/remote_delta.py` | `remote_unavailable` |

The cross-CLI subprocess regression check is
`python -m unittest tools.common.tests.test_python_cli_exit_policy`.
