# Context Priority / Hotspot

この文書は、AIへ渡す候補が多いときに「何から確認するか」を決めるためのContext Priorityと、size / churn / concentration等のhotspot signalの使い方を定義します。

最も重要な原則は次です。

> **大きいfile、変更が多いfile、hotspotだから読むのではありません。現在taskとの関連を最優先します。**

hotspotは読む対象の決定ではなく、routing方法や追加調査の必要性を判断する補助signalです。

## 1. Priorityの基本順序

Context Priorityは、原則として次の順で考えます。

~~~text
1. current task relevance
2. Required / Acceptanceへの直接関係
3. target source / matching tests
4. direct dependency / authoritative contract
5. structure / responsibility / change routing evidence
6. size / churn / concentration等のcheap signal
7. broad history / unrelated auxiliary information
~~~

file sizeが大きくてもtaskと無関係なら読みません。

逆に、小さいfileでもpublic contractやAcceptanceに直接関係するなら優先します。

## 2. hotspotとは何か

hotspotは、追加のroutingや注意が有効かもしれない候補を示すsignalです。

例:

- file sizeが大きい
- directory depthが深い
- 変更頻度が高い
- 特定moduleへ変更が集中している
- 多数の責務が1fileへ集まっている
- fan-in / fan-outが大きい
- contextへ入れた場合の推定costが大きい

これらは次のような問いを出すために使います。

~~~text
このfileは全文を読むよりsymbol単位で絞るべきか?
このmoduleはChange Routing / Responsibility Mapが必要か?
この領域はSource Structure Indexの効果が高いか?
この候補はContext Packへ入れる前にsliceすべきか?
~~~

hotspotであること自体は、読む理由にも設計不良の証明にもなりません。

## 3. task relevanceを最優先にする

taskから直接関係が分かる場合、cheap signalよりtask evidenceを優先します。

~~~text
Task: save format bug
  -> save implementation
  -> matching tests
  -> format contract
  -> direct consumer if needed
~~~

repository内で最大のfileがrendering subsystemにあっても、このtaskのworking setへ自動追加しません。

同様にchurnが大きいmoduleでも、今回の変更と無関係なら通常contextから外します。

## 4. 大きいfileを見つけたときの正しい反応

大きいfileを見つけた場合の第一選択は「全文を読む」ではありません。

~~~text
large relevant file
  -> symbol / heading / text search
  -> target slice
  -> direct surrounding context
  -> full file only if still required
~~~

Context Priorityは、**読む順番だけでなく、読む粒度を選ぶ**ためにも使えます。

大きくてtaskに関係するfileほど、Source Structure Index / structural search / target slice等の高精度routingが有効です。

## 5. Context Budgetとworking set

contextへ入れた場合のcost見積もりは、working setから必要情報を削るためのhard capではありません。

使い方は次です。

~~~text
required candidate
  -> estimated context cost
  -> cheap enough: read needed scope
  -> expensive: narrow by symbol / section / query
  -> still required: include enough evidence
~~~

「budgetを超えるから必要なsourceを読まない」ではなく、必要情報へより小さい粒度で到達できないかを先に検討します。

このrepositoryの [Evidence Budget](evidence-budget.md) は、Required evidenceと探索停止条件を管理する手法です。context costの概算とは役割が異なります。

~~~text
Evidence Budget
  -> what evidence is required

Context cost estimate
  -> how expensive a candidate is to include
~~~

## 6. cheap signalと高精度routing

### cheap signal

低コストで取得できる情報です。

- file bytes
- line count
- directory depth
- file count
- recent churn
- change concentration
- file type / path role

cheap signalは、repository全体を深く解析する前に「どこで追加routingが効きそうか」を見るために使えます。

### 高精度routing

taskとの関係をより直接的に判断できる情報です。

- Task / Change Routing
- Responsibility Map
- Architecture Boundary Routing
- symbol / dependency index
- changed-symbol information
- direct import / call relation
- matching tests
- targeted search result

現在taskのworking setを決めるときは、利用可能なら高精度routingを優先します。

~~~text
cheap signal
  -> decide where precision is worth paying for
  -> precise routing
  -> bounded working set
~~~

cheap signalだけで最終working setを決めません。

## 7. churn / concentrationの扱い

churnや変更集中は、次のようなrisk / maintenance signalとして利用できます。

- 同じ領域を何度も再探索している
- 責務やrouting情報を整備すると繰り返しcostが下がりそう
- regression testやtargeted validationの価値が高そう
- unstableな領域なのでcurrent source / tests確認を優先すべき

ただし、過去に頻繁に変わったから今回も関係する、とは限りません。

historyを読むこと自体が高コストなら、current taskに必要な理由がある場合だけchurn詳細へ進みます。

## 8. Context Manifestとの関係

[Context Manifest](context-manifest.md) は候補pointerのboundedな目録です。

Context Priorityは、その候補を現在taskへどう優先付けするかを考えます。

~~~text
Context Manifest
  -> candidate pointers

Context Priority
  -> task-relevant ordering / granularity

Context Pack
  -> actually selected working set
~~~

manifestにP0..P4等のpriorityを持たせても構いませんが、固定のfile種別priorityより現在taskとの関連を優先します。

## 9. 省略してよい条件

次の場合は専用のhotspot / context-cost分析を通常省略できます。

- repositoryが小さい
- target source / testsが明白
- fileが小さく、全文readが十分安価
- routing ambiguityが低い
- repeated context costが問題になっていない
- cheap signalを取ってもworking set選択が変わらない

小さいtaskで毎回repository-wide hotspot scanを行うと、削減効果より分析costが大きくなることがあります。

## 10. 補助実装

このrepositoryには、Context Priority判断を補助するtoolがあります。

### context-budget

tools/common/large/context-budget は、candidate textをagent contextへ入れた場合のcostを概算します。

- exact tokenizerではない
- costが高い候補を「不要」と判定するtoolではない
- 高コストならslice / query / symbol routingを検討するsignalとして使う

### hotspot-report

tools/common/large/hotspot-report は、size / depth等からhotspot候補をboundedに返します。

- 出力上位だから読む、ではない
- task relevanceを判定しない
- architecture品質をscoreしない
- 高精度routingをどこへ適用するか考えるcheap signalとして使う

どちらのtoolも手法の成立条件ではありません。既存IDE、Git metadata、独自script、単純なfile listing等で十分ならそれを使えます。

## 11. 標準推奨

- task relevanceをContext Priorityの最優先にする
- hotspotを「読むべき対象」のランキングにしない
- size / churn / concentrationを補助signalとして使う
- 大きい relevant fileは全文readより先にslice / symbol routingを検討する
- context costを必要情報のhard capにしない
- cheap signalは高精度routingを適用する場所の判断に使う
- working set決定にはTask / Change / Responsibility / structure evidenceを優先する
- Context Manifestの固定priorityよりtask-specific relevanceを優先する
- Small repoや対象明確なtaskでは専用分析を省略する
- context-budget / hotspot-reportのscoreや出力順を手法そのものにしない
