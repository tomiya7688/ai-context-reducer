# architecture-boundary-router

Project-provided architecture profileを、agentの最初のworking setを選ぶrouting hintへ変換します。特定architectureの適合checkerではありません。手法そのものは [`docs/jp/既存の設計境界で読む範囲を絞る.md`](../../../../docs/jp/既存の設計境界で読む範囲を絞る.md) を参照してください。

## Development routing

- CLI / output変更: `script/architecture_boundary_router.py`
- profile読込・外部I/O変更: `script/messenger.py`
- path分類・hint意味論変更: `script/processing.py`
- profile→routesのflow変更: `script/commander.py`

この構造により、Task Routing / Responsibility Map / Exploration Stopをtool開発自身へ適用できます。
