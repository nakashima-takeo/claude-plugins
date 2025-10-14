---
description: コードレビュー→修正ループを自動実行
---

Task ツールを使って orchestrator エージェントを起動してください。

**起動方法:**
```
Task(
  subagent_type="orchestrator",
  description="コードレビュー→修正ループ実行",
  prompt="Git の変更差分を確認し、コードレビュー→修正のループを実行してください。\n\n手順:\n1. Git diff で変更ファイルを特定\n2. reviewer エージェントを使ってレビュー\n3. 重要度「高」「中」の指摘を修正\n4. 重要度「中」以上の指摘がなくなるまで繰り返す（最大5回）\n5. リンター修正\n6. 完了報告"
)
```
