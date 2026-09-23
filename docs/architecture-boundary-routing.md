# Architecture Boundary Routing

この文書は、対象projectがすでに持っている責務境界・層・component・正式な通信経路を、AIが最初に読む範囲を絞るためのrouting情報として再利用する手法を定義します。

重要なのは、**architectureを新しく推測したり、特定の設計へ適合しているか判定したりすることではありません**。既存の設計情報が信頼できる場合だけ、それを最初のworking set選択へ使います。

## 1. 目的

大きなprojectでは、変更対象が1file分かっても、その周辺をどこまで読むべきか判断するために広い探索が発生します。

既存architectureに責務や境界が明示されている場合は、最初からrepository全体へ広げず、関係する責務と必要な境界だけを先に確認します。

~~~text
Task / changed path
  -> project-owned architecture boundary
  -> first working set
  -> target source / matching tests
  -> direct collaborators
  -> broader expansion only if needed
~~~

この手法の目的は、正しさを落とさずに最初の探索範囲を狭くすることです。

## 2. 利用できる既存情報

専用profileは必須ではありません。projectがすでに持っている次のような情報を利用できます。

- architecture / design document
- module / package ownership
- Responsibility Map
- layer / component definition
- API / message / event boundary
- directory ownership rule
- dependency direction
- project固有のrouting metadata

これらは原典を置き換えません。

短いrouting用の表やprofileを作る場合も、正式なarchitecture/specificationへのpointerを残し、原典と矛盾したら原典を優先します。

## 3. 適用するとよい条件

次の条件が複数当てはまる場合に有効です。

- module / subsystemが複数あり、最初に読む範囲の判断が難しい
- project内に責務境界や層の定義がすでにある
- component間の正式な通信経路やcontractが明示されている
- 同じarchitecture情報を毎回source探索から再構成している
- 境界を使えば無関係なsubsystemを最初のworking setから外せる

導入判断は「architectureがあるから使う」ではなく、次を満たすかで行います。

~~~text
expected repeated context saving
    > routing metadata maintenance cost
~~~

## 4. 最初のworking setを選ぶ

基本の流れは次です。

### 同一責務の変更

変更が1つの責務内に閉じている場合は、その責務と直接のcollaboratorから始めます。

~~~text
target
  -> owning responsibility
  -> direct collaborators
  -> matching tests
~~~

別componentは、contract変更や影響の証拠が出た場合だけ追加します。

### 境界そのものの変更

API、message、event、serialization formatなど境界contractを変更する場合は、境界の片側だけで完了しません。

~~~text
boundary change
  -> sender / caller side
  -> contract
  -> receiver / callee side
  -> matching validation
~~~

### 分類できない場合

既存情報で分類できないpathやtaskを無理にarchitectureへ当てはめません。

~~~text
unclassified
  -> generic Task / Change Routing
  -> Responsibility Map
  -> search / Source Structure Index
  -> source details
~~~

「たぶんこの層」という推測でworking setを狭めるとfalse negativeを生むため、未分類はfallbackへ送ります。

## 5. 特定architectureのcheckerにしない

Architecture Boundary Routingは、layered architecture、Clean Architecture、MVC、frontend/backend分割など、特定の構造を標準化しません。

また、次の判定を目的にしません。

- この設計が良いか
- 正しいarchitectureへ適合しているか
- layer違反が存在するか
- moduleを分割すべきか
- どのarchitectureを採用すべきか

projectが採用している境界を**探索の入力**として使うだけです。

architecture ruleの適合確認が必要なら、既存のlinter / checker / targeted reviewなど別のvalidationとして扱います。

## 6. 他の手法との役割分担

### Responsibility Map

[Responsibility Map](responsibility-map.md) は「どのfile / moduleが何を担当するか」を短く示します。

Architecture Boundary Routingは、その責務同士の境界や正式な接続関係を使って「最初にどこまで読むか」を決めます。

~~~text
Responsibility Map
  -> who owns what

Architecture Boundary Routing
  -> which boundary limits the first working set
~~~

Responsibility Mapだけで十分に対象へ到達できるprojectでは、別のarchitecture routingを追加する必要はありません。

### Change Routing Map

[Change Routing Map](change-routing-map.md) は変更カテゴリからsource / tests / docsへ直接routingします。

Architecture Boundary Routingは、そのrouting判断に既存architectureの境界情報を利用できます。

~~~text
change type
  -> Change Routing Map
  -> architecture boundary if relevant
  -> target source / tests
~~~

変更カテゴリだけで十分に対象が決まる場合は、architecture情報を追加で読む必要はありません。

### Source Structure Index

[Source Structure Index](source-structure-index.md) はsymbol / import / dependency等の機械的な構造情報から、必要な原典へ到達するための索引です。

Architecture Boundary Routingは通常、その前段で粗いscopeを絞るために使います。

~~~text
project-owned boundary
  -> candidate scope
  -> Source Structure Index
  -> target symbol / direct dependency
~~~

境界情報が無い場合や曖昧な場合は、Source Structure Indexや通常のsearchから入って構いません。

## 7. fallback

次の場合はArchitecture Boundary Routingを使わず、既存の汎用routingへ戻ります。

- architecture情報が存在しない
- profileやmapが古く、現行sourceと整合しない
- taskを既存境界へ分類できない
- 境界を使ってもworking setがほとんど小さくならない
- 小規模projectでtarget source / testsが最初から明白

fallback例:

~~~text
Task Routing
  -> Change Routing Map
  -> Responsibility Map
  -> search / Source Structure Index
  -> targeted source / tests
~~~

専用profileが無いことを欠陥とはみなしません。profile作成のためにarchitectureを推測することもしません。

## 8. Small repoでは省略する

次のようなprojectでは専用のArchitecture Boundary Routingは通常不要です。

- 主要実装が少数file
- source / testsの対応が明白
- subsystem間の境界が探索コストになっていない
- Responsibility MapやChange Routing Mapだけで十分

小さいprojectにrouting layerを追加すると、削減できるcontextより維持する文書やmetadataの方が増えることがあります。

## 9. 維持方法

routing情報を持つ場合は、原典とのdriftを避けます。

- 原典architecture/specificationをSource of Truthにする
- routing用profileには必要最小限のboundary情報だけ持つ
- architecture変更時は同じchange setで更新する
- 古いことが分かったprofileはrouting sourceから外す
- 不明な分類を推測で埋めない

summaryやprofileは、原典を複製した新しい仕様書にしません。

## 10. 補助実装

このrepositoryには、project側が用意したarchitecture routing profileをpath分類とcompactなrouting hintへ変換する補助実装として tools/common/medium/architecture-boundary-router があります。

このtoolは手法の成立条件ではありません。

- profileがある場合だけ利用する
- profileが無ければgeneric routingへfallbackする
- 特定architectureの適合checkerとして使わない
- profileは原典architecture/specificationを置き換えない

別形式のmap、既存build metadata、IDE情報、project固有scriptなどで同じroutingができるなら、それを利用して構いません。

## 11. 標準推奨

- projectがすでに持つ責務・境界情報だけをroutingへ再利用する
- 特定architectureを標準化しない
- 最初のworking setを狭める用途に限定する
- boundary contract変更では両側を確認する
- 分類不能な対象を推測で狭めずgeneric routingへ戻す
- Responsibility Map / Change Routing Map / Source Structure Indexと役割を重複させない
- Small repoでは専用routingを追加しない
- routing metadataより原典architecture/specificationを優先する
- toolやprofile formatを手法そのものにしない
