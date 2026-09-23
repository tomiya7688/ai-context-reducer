# Adaptive Adoption / 導入優先度

この文書は、Codex / Claude Code / ChatGPT などが対象プロジェクトを短時間で観察し、`ai-context-reducer` のどの手法を導入するか自律的に選ぶための判断基準です。

目的は **全部導入することではありません**。

導入判断の前に、[`context-reduction-basics.md`](context-reduction-basics.md) の3原則を確認します。

1. 静的解析できるものは静的解析する
2. よく使う操作をまとめる
3. 一部だけ読ませる

個別手法はこの3原則の具体化として扱い、toolの数や名前をそのまま導入価値とはみなしません。

> 最小コアを先に導入し、追加手法は期待効果が導入・維持コストを上回る場合だけ使う。

## 1. 導入優先度

### A — Core / 原則ほぼ全プロジェクト

最初に導入する最小構成です。

- 小さい `AI_CONTEXT.md` または同等のAI入口
- Search first, read second
- Goal / Required / Acceptance が揃ったら探索停止
- Source of Truth の明示
- 現在タスクと unrelated refactor の分離
- targeted validation と Unverified areas
- [Context Exclusion](context-exclusion.md): generated files / logs / vendor / caches / broad historyを通常コンテキストから除外し、Source of Truthやvalidationに必要なartifactは除外しない

Aだけで十分な小規模プロジェクトもあります。

### B — High ROI / 条件が合えば優先導入

比較的低コストで大きな削減効果が期待できます。

| 手法 | 導入するとよい兆候 |
|---|---|
| Current State summary | 実装済み機能・制約・未実装が増え、READMEだけでは現状を把握しにくい |
| [Context Manifest](context-manifest.md) | source / tests / docs等の参照候補が多く、毎taskで候補を広く探し直している |
| Task Routing | Issue / docs / subsystem が多く、タスクごとに読む資料が変わる |
| Change Routing Map | 変更カテゴリから source / tests / docs を対応付けられる |
| [Architecture Boundary Routing](architecture-boundary-routing.md) | project内に信頼できる責務境界・層・component・正式な通信経路がすでにあり、それを使えば最初のworking setを狭められる |
| Responsibility Map | file / module が増え、名前だけでは責務を判断しづらい |
| Hierarchical Context | monorepo / multi-appでsubsystem固有ルールがあり、root AI guideが肥大化している |
| Evidence Budget | Required evidenceが揃っても検索が続く、history / broad docsへ「念のため」で横展開しやすい |
| Remote Delta First | 複数AI・複数チャット・複数開発者が同じremoteを更新する |
| Validation Routing | 変更によって必要な検証方法が大きく異なる |
| Change / Test Impact Routing | test suiteが大きい・遅い、source/test対応やdependency情報があり毎回full suiteを回している |
| compact policy checks | 規約が長い、または機械判定できる規則が多い |
| [Documentation Duplication Control](documentation-duplication-control.md) | README / AI guide / docs間で同じ規則や説明が増え、更新driftや再読costが目立つ |

### C — Conditional / 特定プロジェクト向け

効果は大きいですが、必要なプロジェクトだけ導入します。

| 手法 | 向いているプロジェクト |
|---|---|
| [Context Priority / Hotspot](context-priority.md) | 大きいfileや変更集中領域があり、全文readより先にrouting粒度を選びたい |
| Source Structure Index | 非常に大きいコードベース、巨大ファイル、多数のcall/dependency関係 |
| changed-symbol routing | 大きいファイル内の一部symbolだけを頻繁に変更する |
| artifact-boundary validation | build / package / distribution がsource treeと異なる |
| headless-first validation | GUI / editor / game / interactive application |
| disposable validation workspace | export / save / conversion が多数の一時ファイルを生成する |
| deterministic seam | random / clock / network / environment など非決定入力が多い |
| structured runtime observation | runtime挙動を巨大ログではなく少数の状態値で確認できる |
| Boilerplate Generation | license / NOTICE / header / 定型文を多数プロジェクトへ展開する |
| Policy Routing | Required / Recommended / Advisory など規約の強さが複数ある |

### D — Optional / 効果確認後

次は標準必須にしません。

- 高コストな生成索引
- 常時更新する大規模call graph
- 複雑な要約キャッシュ
- AI専用ファイルの大量追加
- 小規模repoへの過剰なrouting table
- 導入・保守コストが削減効果より大きい自動化

実測または明確な反復コストがある場合だけ追加します。

## 2. プロジェクト規模別の目安

LOCやファイル数だけで機械的に判定しません。AIが迷わず対象箇所へ到達できるかを基準にします。

### Small

特徴:

- 主要実装が少数ファイル
- docs が少ない
- source と tests の対応が明白
- 単独開発・単一セッション中心

推奨:

```text
A Core
+ 必要なら Validation Routing
```

Context Manifest、Context Priority / Hotspot、Task Routing や Source Structure Index は通常不要です。target source / tests / docsが明白な小taskでは、manifestを作らず直接pointerを渡します。Hierarchical Contextも、rootの小さいAI入口だけで十分なら導入しません。test suiteが小さくfull runが安価ならChange / Test Impact Routingも不要です。Evidence Budgetも、target source / testsが明白な小taskでは形式化しません。

### Medium

特徴:

- 複数module / subsystem
- docs / tests / scripts が増えている
- Issueや変更カテゴリによって読む場所が異なる

推奨:

```text
A Core
+ Responsibility Map
+ Change / Task Routing
+ Current State
+ Validation Routing
+ 探索が長くなりやすい場合だけ Evidence Budget
+ test suiteが重い場合だけ Change / Test Impact Routing
+ subsystem固有ルールが多い場合だけ Hierarchical Context
```

### Large

特徴:

- AIがroot listingだけでは対象箇所を判断しにくい
- subsystem・docs・tests・generated artifacts が多数
- 同じファイルを毎回読み直すコストが目立つ

推奨:

```text
A Core
+ B High ROI の該当項目
+ Evidence Budget（探索停止が曖昧なtask）
+ Hierarchical Context（multi-app / local ruleがある場合）
+ Change / Test Impact Routing（test suiteが大きい場合）
+ Context Priority / Hotspot（size等を読む対象のランキングにはしない）
+ Source Structure Index
+ changed-symbol routing
+ split Context Pack
```

### Multi-agent / Concurrent

規模に関係なく、複数AIや人間が同じremoteを触る場合:

```text
Remote Delta First
+ compact change summary
+ current task / handoff reference
```

を優先します。

## 3. 性質別プロファイル

### Monorepo / Multi-app

優先:

- Hierarchical Context / Scoped AI Instructions
- Task / Change Routing
- Responsibility Map
- package / app単位のValidation Routing
- test suiteが大きい場合はChange / Test Impact Routing
- broad inspectionが頻発する場合はEvidence Budget

rootへ全subsystemの詳細を集約せず、repository-wide invariantだけを残します。local guideは上位文書を複製せず、そのscope固有の差分だけを書きます。

### GUI / Game / Editor

優先:

- headless-first validation
- deterministic runtime
- structured observation
- visual confirmation は Acceptance に必要な場合だけ
- disposable validation workspace

### Compiler / Language / Static Tool

優先:

- Responsibility Map
- Change Routing Map
- targeted tests
- test suiteが大きい場合はChange / Test Impact Routing
- Policy checker
- Source Structure Index は規模が大きくなってから

### Data / Conversion Tool

優先:

- dry-run
- reproducible transformation
- disposable workspace
- bounded output / compact diff
- source of truth の明示

### Packaged / Distributed Application

優先:

- source validation
- artifact generation
- artifact smoke
- required files / initialization validation

### Random / Time-dependent / Simulation

優先:

- fixed seed / fixed input
- deterministic seam で RNG / clock 等を注入可能にする
- bounded runtime
- structured evaluation output

### Rule-heavy Project

優先:

- Policy Routing
- machine-checkable rules -> checker
- semantic / architectural rules -> targeted review
- compact exception record

## 4. AIによる自動導入手順

Codex / Claude Code 等は、導入時に次の順で進めます。

### Step 1: shallow inspection

最初は次だけ確認します。

- root file / directory names
- README
- 既存の `AGENTS.md` / `CLAUDE.md` / AI向け入口
- docs のファイル名・見出し
- test directory / test naming
- build / package metadata
- Git / remote の運用が分かる最小情報

この時点で全source・全docs・全Issuesを読みません。

### Step 2: classify signals

次を短く判定します。

```text
size: small / medium / large
concurrent remote edits: yes / no
many docs or issues: yes / no
routing ambiguity: low / high
explicit architecture boundary available: yes / no
exploration drift risk: low / high
multiple apps/packages: yes / no
subsystem-specific instructions: yes / no
test suite cost: low / high
test impact mapping available: yes / no
GUI / interactive: yes / no
runtime nondeterminism: yes / no
generated / packaged artifact: yes / no
rule-heavy: yes / no
```

厳密な数値分類は不要です。

### Step 3: choose smallest useful set

必ず A Core から始め、B / C は該当signalがある場合だけ選択します。

「将来便利そう」という理由だけで追加しません。

Hierarchical Contextは、複数scopeへ異なる指示を置く明確な理由がある場合だけ選択します。directory数が多いだけでは導入理由にしません。

Architecture Boundary Routingは、対象projectがすでに持つ信頼できる責務・境界情報を再利用できる場合だけ選択します。profileを作るためにarchitectureを推測したり、特定architectureへの適合checkerとして導入したりしません。Small repoやResponsibility Map / Change Routing Mapだけで十分な場合は追加しません。

Evidence Budgetは、通常のGoal / Required / Acceptance停止条件だけで十分なら導入しません。使う場合もtoken hard capではなくRequired / Optional evidenceの不足管理に限定します。

Change / Test Impact Routingは、full suiteが十分安価なら導入しません。導入する場合も、shared/core/public contract変更時のbroader fallbackを削りません。

### Step 4: modify minimally

原則として最初の導入変更は小さくします。

- 既存AI入口があれば改善する
- なければ小さい `AI_CONTEXT.md` を作る
- 既存docsを再配置しない
- 詳細仕様を複製しない
- 必要なrouting map等だけ追加する
- local guideが必要なら、そのscope固有の差分だけを置く
- Evidence Ledgerは必要なtaskだけpointer中心で短く持つ
- test impact routingは既存の命名・dependency情報から始め、専用解析器を先に作らない

### Step 5: verify usefulness

導入後、少なくとも次を確認します。

- AI入口から現在の作業対象へ到達できる
- source of truth が分かる
- 無関係な巨大領域を読まずに済む
- completion / validation の入口が分かる
- 追加ファイル自身が過剰に大きくない
- Evidence Budgetを導入した場合、Required evidenceが揃った時点で探索停止できる
- local guideを導入した場合、無関係なsubsystemの指示を読まずに済む
- test impact routingを導入した場合、必要なbroader fallbackが残っている

## 5. 導入結果のcompact report

AIは導入後、長い説明ではなく次を報告します。

```text
Adopted:
- Core AI index
- Change Routing Map
- Validation Routing

Skipped:
- Source Structure Index: repository is still small
- Remote Delta First: single-writer workflow
- Hierarchical Context: no subsystem-specific rules
- Evidence Budget: normal stop conditions are already sufficient
- Change / Test Impact Routing: full test suite is already cheap

Why:
- source/test routing was the main repeated lookup cost
```

**導入しなかった手法と理由も短く残す**ことで、全部入りを防ぎます。

## 6. 判断原則

優先順位は次です。

```text
正確性
  > 作業対象への到達速度
  > コンテキスト削減量
  > 自動化の多さ
```

そして、導入判断は次で行います。

```text
expected repeated context saving
    > adoption + maintenance cost
```

を満たす手法だけ追加します。
