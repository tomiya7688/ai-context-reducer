# Context Exclusion / Ignore Candidates

この文書は、現在taskの判断に通常不要なgenerated output、logs、vendor、cache、history等をAIの通常contextから外し、必要な原典へ集中するためのContext Exclusion方針を定義します。

重要なのは、**contextから通常除外することと、repositoryから削除したりignore設定へ追加したりすることは別**だという点です。

> 除外候補を先に見つけ、Source of Truth・task relevance・validation用途を確認してから、通常contextから外す。

## 1. 目的

repositoryには、作業対象ではないのに大量のcontextを消費しやすい領域があります。

代表例:

- build / dist / generated output
- logs / traces / reports
- dependency / vendor directories
- cache / temporary directories
- runtime saves / backups
- broad Git history
- generated documentation / indexes
- editor / IDE generated state

これらを毎taskで無条件に読む必要はありません。

~~~text
repository
  -> normal context candidates
  -> default-excluded candidates
  -> task-specific promotion when required
~~~

目的は「見えないようにすること」ではなく、通常のworking setを小さく保つことです。

## 2. Source of Truthは除外しない

path名やfile種別だけで、重要な原典まで除外してはいけません。

例えばprojectによっては次が正式なSource of TruthまたはAcceptanceに必要なartifactになり得ます。

- checked-in generated source
- lockfile
- schema snapshot
- migration file
- golden test data
- fixture
- vendored codeへproject固有patchを持つ領域
- binary / assetが正式入力となるproject
- generated API definitionが配布contractであるproject

そのため、除外判断は次の順で行います。

~~~text
candidate signal
  -> Source of Truth?
  -> current task target?
  -> required validation evidence?
  -> safe to exclude from normal context?
~~~

いずれかがyesなら、機械的なdefault exclusionだけで捨てません。

## 3. 三つの状態に分ける

Context Exclusionは、単純なinclude / ignoreの二値だけで考えない方が安全です。

### Normal context

現在taskで通常読む候補です。

- target source
- matching tests
- authoritative docs / contract
- direct dependencies
- current task / required constraints

### Default-excluded context

通常taskでは読まない候補です。

- build outputs
- cache
- dependency mirror
- large logs
- runtime backup
- unrelated history
- generated reports

必要になれば後から戻せます。

### Validation-only / task-promoted

通常は除外するが、特定taskのAcceptanceで一時的に必要になるものです。

例:

- package archive
- installer
- generated config
- export result
- compiled binary
- generated manifest
- transformed dataset

~~~text
default excluded
  -> Acceptance requires artifact evidence
  -> promote for validation only
  -> inspect bounded evidence
  -> return to default-excluded after task
~~~

この区別により、generated artifactを毎回読むことなく、必要なrelease / packaging taskでは正しく検証できます。

## 4. candidateとconfirmed exclusionを分ける

ignore候補を検出しただけで確定除外にはしません。

~~~text
candidate
  -> review
  -> confirmed context exclusion
  -> optional repository ignore change as separate action
~~~

reviewでは最低限次を確認します。

1. Source of Truthではないか
2. current taskの直接対象ではないか
3. Acceptance / validation evidenceとして必要ではないか
4. repository固有の重要artifactではないか
5. 生成元・再生成方法が分かるか
6. contextから外すだけでよいのか、実際のignore設定も必要なのか

候補検出は安全側のhintであり、apply判断ではありません。

## 5. repository ignore設定とは別

Context ExclusionはAIが通常読まない範囲を決める手法です。

.gitignore、.ignore、.dockerignore、IDE設定、build設定等を変更することとは別です。

~~~text
context exclusion
  -> AI working setから通常外す

repository ignore configuration
  -> version control / tool behaviorを変更する
~~~

後者はrepository behaviorへ影響するwrite actionです。

明示的なtaskとreviewなしに自動適用しません。

特に既にtrackingされているfile、releaseに必要なfile、generated-but-checked-in fileを機械的にignoreへ追加しないでください。

## 6. generated / logs / vendor / caches / history

### Generated output

通常は原典ではなく派生物なのでdefault-excluded候補です。

ただし生成物そのものが配布・互換性・format Acceptanceの対象ならvalidation-onlyへ昇格します。

### Logs / traces / reports

正常系のfull logは通常contextへ入れません。

失敗原因やruntime Acceptanceに必要な場合だけ、関連区間やstructured observationへ絞って読みます。

### Vendor / dependency directories

通常は外部依存の複製なのでdefault-excluded候補です。

ただしprojectが直接patchしているvendor領域、license / NOTICE確認、security investigation等ではtask-specificに必要になる場合があります。

### Cache / temporary files

再生成可能でtaskの根拠にならないcacheは通常除外します。

cache invalidation自体がbug対象なら例外です。

### History

Git history全体は通常contextへ含めません。

Remote Delta、blame、regression investigation、design rationale確認など、現在taskに必要な問いがある場合だけboundedに取得します。

## 7. Artifact Boundary Validationとの関係

generated artifactは通常contextでは除外候補ですが、source treeと最終成果物が異なるprojectでは、artifactそのものがvalidation evidenceになります。

[Validation Routing](validation-routing.md) のartifact-boundary validationとは次の関係です。

~~~text
normal implementation context
  -> source / config / tests are primary
  -> build / dist artifacts default excluded

package / release / export validation
  -> source validation
  -> artifact generation
  -> generated artifact promoted for validation
  -> artifact smoke / required-files check
  -> compact result
~~~

ここで重要なのは、artifactをSource of Truthへ昇格させることではありません。

- generator / config / sourceは引き続き原典
- generated artifactはAcceptanceを直接確認するevidence
- 成功後にartifact全文や大量fileをContext Packへ保持しない
- 必要な結果と問題箇所だけ残す

## 8. disposable validation workspace

検証のためだけに生成するartifactは、可能ならdisposable workspaceへ出します。

これにより:

- working treeへnoiseを残さない
- changed filesへ混ざらない
- 次taskで誤ってcontextへ入らない
- 再現可能な初期状態を保ちやすい

長期保存が必要なvalidation artifactだけ明示的な保存先へ移します。

## 9. project固有の重要artifactを守る

genericなdirectory名だけで確定除外しません。

例えば build、dist、generated、vendor、data という名前でも、project固有のSource of Truthである可能性があります。

導入時はshallow inspectionで次を確認します。

- README / build instructions
- release / package manifest
- tracked file status
- generator source
- testsが参照するfixture / golden data
- project-specific AI / contributor guide

不明なら除外を確定せずcandidateのままにします。

## 10. AI_CONTEXTとの関係

小規模projectでは専用ignore mapを作らず、AI_CONTEXTの Ignore Normally に短いdefault exclusionだけを書くことで十分です。

例:

~~~text
Ignore Normally
- build outputs
- cache
- generated reports
- large logs
- unrelated history
~~~

例外やtask-specific promotionは必要時だけ記述します。

exclude list自体を巨大なcatalogにしません。

## 11. 補助実装

このrepositoryには tools/common/medium/ignore-candidates があります。

これは、agent contextへ入れる価値が低い可能性が高いpathを**候補として提示する補助実装**です。

- candidateを返すだけ
- review_required_before_ignoring を明示する
- Source of Truthかどうかを最終判断しない
- .gitignore等を書き換えない
- fileを削除しない
- repository固有の重要artifactを自動除外しない
- validation-only artifactの必要性はtask側で判断する

別のproject metadataや既存ignore設定で十分なら、このtoolを使う必要はありません。

## 12. 標準推奨

- generated / logs / vendor / caches / broad historyを通常contextから外す
- path名だけでSource of Truthを除外しない
- candidate detectionとconfirmed exclusionを分ける
- context exclusionとrepository ignore設定の変更を分ける
- .gitignore等を自動書換えしない
- task / Acceptanceに必要なartifactはvalidation-onlyとして一時的に戻す
- artifact validation後もgenerated artifactを通常contextへ常駐させない
- logsは必要なfailure区間やstructured resultだけ読む
- historyは具体的な問いがある場合だけboundedに取得する
- Small repoではAI_CONTEXTの短いIgnore Normallyで十分なら専用仕組みを増やさない
- ignore-candidatesをapply toolとして扱わない
