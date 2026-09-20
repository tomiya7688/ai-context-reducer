# Context Reduction Basics / コンテキスト削減の基本

AI向けのコンテキスト削減は、複雑な仕組みに見えても、基本的には次の3つのどれか、または組み合わせです。

> 1. 静的解析できるものは静的解析する  
> 2. よく使う操作をまとめる  
> 3. 一部だけ読ませる

この3つを理解すると、個別のtoolやrouting手法を別々の高度な技術として覚える必要はありません。

## 1. 静的解析できるものは静的解析する

AIにsource全体を読ませて、機械的に取れる情報まで推測させる必要はありません。

たとえば次のような情報は、可能ならAIの外で先に取得します。

- symbol / function / type
- import / dependency
- file structure
- syntax / parser health
- changed files / changed symbols
- testとの対応
- package / module関係

AIには解析結果のうち、現在のtaskに必要な部分だけを渡します。

```text
source
  -> static analysis
  -> compact structure / candidates
  -> AIが必要箇所だけ確認
```

静的解析の目的は、AIの代わりに実装を理解することではありません。  
**AIが読む前に、機械的に確定できる情報を取り除くこと**です。

## 2. よく使う操作をまとめる

毎回同じ探索・確認・判断手順をAIに考えさせると、その手順自体がcontextと推論コストを消費します。

繰り返し使う操作は、script / tool / workflow / compact procedureへまとめます。

例:

```text
search
  -> scope
  -> inspect
  -> validate
  -> stop
```

```text
changed files
  -> related source
  -> matching tests
  -> required validation
```

まとめる対象は、複雑な処理である必要はありません。  
**何度も同じ順序で行う操作なら、まとめる価値があります。**

ただし、自動化のために新しい複雑さを増やしすぎてはいけません。

```text
expected repeated context saving
    > adoption + maintenance cost
```

を満たす範囲でまとめます。

## 3. 一部だけ読ませる

最も直接的なcontext削減は、AIに全部読ませないことです。

最初に対象を絞り、必要なsource / docs / tests / diffだけを読みます。

そのために使えるものは多くあります。

- search
- routing
- index
- manifest
- scoped instructions
- changed-symbol information
- responsibility map
- compact diff
- summary / pointer

ただし、summaryやindexをSource of Truthの代わりにはしません。

```text
pointer / summary / index
  -> 必要箇所を特定
  -> original sourceへ戻る
```

重要なのは、**一部しか読ませないことと、根拠を失うことは別**だという点です。

## 多くの手法は3原則の組み合わせ

このrepositoryで扱う手法も、ほとんどは3原則へ分解できます。

| 手法 | 静的解析 | 操作をまとめる | 一部だけ読ませる |
|---|---:|---:|---:|
| Source Structure Index | ✓ |  | ✓ |
| Change / Test Impact Routing | ✓ | ✓ | ✓ |
| Change Routing Map |  | ✓ | ✓ |
| Responsibility Map |  | ✓ | ✓ |
| Hierarchical Context |  |  | ✓ |
| Remote Delta First | ✓ | ✓ | ✓ |
| Context Manifest / Context Pack |  | ✓ | ✓ |
| Policy Check | ✓ | ✓ | ✓ |
| Boilerplate Generation |  | ✓ |  |
| Syntax Health Validation | ✓ | ✓ |  |

チェックが多いほど高度という意味ではありません。  
どの方法でAIの不要な読み取り・探索・反復判断を減らしているかを示しています。

## toolは原則を実装するための補助

このrepositoryには複数のportable toolがありますが、tool自体が目的ではありません。

```text
context reduction principle
  -> projectに必要な手法を選択
  -> 繰り返し部分だけtoolで補助
```

toolが無くても同じ原則を満たせるなら問題ありません。

逆に、toolを導入しても、

- AIへfull outputをそのまま渡す
- 不要な解析を毎回走らせる
- toolの使い方を毎回大量に読ませる
- 元sourceへ戻れないsummaryだけ残す

のであれば、context reducerとしては逆効果です。

## 導入時の最初の判断

新しい仕組みや外部toolを見るときは、最初に次だけ確認します。

```text
これは何を減らしているか？

1. AIに推測させていた機械的解析か
2. AIに毎回やらせていた反復操作か
3. AIに読ませていた不要な範囲か
```

3つのどれにも当てはまらない場合、本当にcontext削減へ効いているかを再確認します。

## 優先順位

3原則を適用する場合も、正確性を犠牲にはしません。

```text
正確性
  > 作業対象への到達速度
  > コンテキスト削減量
  > 自動化の多さ
```

目的は「できるだけ読ませない」ことではなく、**必要な情報へ正確に、少ないcontextで到達すること**です。
