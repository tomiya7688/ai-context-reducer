# External Tool Reference Policy

外部ツールを具体例として掲載する場合は、原則として次の条件をすべて満たすものに限定します。

- 無料で利用できる
- 商用利用できる
- 通常利用時に成果物やUIへのクレジット表示を要求されない
- ポータブル、または導入が容易

条件が不明なツールは掲載しません。

ここでいう「明示不要」は、通常利用時にツール名やクレジットを成果物・UI・README等へ表示する義務がないことを指します。

MIT / BSD / Apache-2.0 等で、ツール本体を再配布する場合にライセンス文等の保持が必要になるケースは別扱いとします。開発時に利用するだけの場合と、配布物へ同梱する場合を分けて確認します。

導入性は、単体バイナリ、package manager、repository-local wrapper等で簡単に利用できることを優先します。

## 現在の具体例

現在の文書で具体例として扱う候補は、次のような無料・商用利用可能・導入容易なOSSを優先します。

- [Nx](https://github.com/nrwl/nx): affected project / test routing
- [Pants](https://github.com/pantsbuild/pants): changed target / dependency based validation routing
- [SCIP](https://github.com/scip-code/scip): code intelligence index
- [Tree-sitter](https://github.com/tree-sitter/tree-sitter): portable syntax parsing
- [ast-grep](https://github.com/ast-grep/ast-grep): structural search / lint / rewrite
- [Copier](https://github.com/copier-org/copier): versioned project templates
- [Cookiecutter](https://github.com/cookiecutter/cookiecutter): lightweight project templates

個別文書では、その手法と直接関係するものだけを具体例として掲載します。

## 掲載しない例

次のような場合は、ツール自体が優秀でも具体例リンクから外します。

- 無料利用が保証されない
- 商用利用条件が用途によって制限される
- 利用時に明示的なクレジット表示が必要
- 導入に常時サービス契約や重いサーバー構築が必要で、同等の軽量代替がある
- ライセンスや利用条件を確認できない

外部ツールを追加する前に、公式情報を優先して無料利用、商用利用、表示義務、導入方法を確認します。条件変更が判明した場合は掲載を削除または置換します。

標準の原則自体は外部ツールに依存させません。


## External / fallback / unsupported matrix

外部toolは必須依存ではありません。AI Context Reducer側で軽量に代替できるsubsetだけをportable fallbackとして持ち、高度機能は外部toolへ委譲します。

| Capability | External example | Repository-local fallback | Intentionally unsupported / delegated |
|---|---|---|---|
| fast text search | ripgrep | `acr-toolbox search` | ripgrep完全互換CLI / 全最適化 |
| file discovery | fd | `acr-toolbox find` | fd完全互換filter / UX |
| syntax / structural search | ast-grep | `structural-search`（Python AST fallback） | multi-language AST rule engine / rewrite engine |
| affected test routing | Nx / Pants | `affected-tests`, `structure-index affected` | build graph / coverage engine完全再実装 |
| scoped AI instructions | agent-native scoped instructions | `scoped-guides` | agent固有precedenceの再現 |
| policy checking | ast-grep / Semgrep等 | `policy-check` | AST / dataflow / taint / semantic rule engine |
| canonical templates | Copier / Cookiecutter | `template` | Jinja2互換、Copier update algorithm |
| source / semantic index | SCIP / Universal Ctags | `structure-index` adapters + portable language analyzers | SCIP compiler/indexer完全再実装 |
| syntax health | Tree-sitter | existing Tree-sitter integration where available | grammar/runtimeの自動install |
| Git repository health | git-sizer | `git-history-health` adapter/fallback routing | Git object analyzer完全再実装 |

### 判断ルール

```text
external backend already available and higher quality
  -> reuse it

not installed / portable environment
  -> use repository-local fallback

task requires unsupported semantic/deep feature
  -> explicitly escalate to external backend

backend unavailable
  -> do not auto-install; keep the result unavailable / approximate / unverified
```

この表は「外部toolを置き換える一覧」ではなく、どこまでをこのrepositoryが責任範囲とするかを示すboundaryです。既存fallbackと重複する新規toolは追加せず、完全互換を目指さないことを標準とします。
