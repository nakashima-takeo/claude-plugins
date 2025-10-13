# review-loop-plugin

Stop時にレビュー→修正ループ→リンター修正を自動化するClaude Codeプラグイン

## 概要

エージェントが停止（Stop/SubagentStop）したタイミングでフックを発火し、以下の処理を自動化：

1. エージェント停止
2. 専用の reviewer エージェントによるレビュー実施
3. レビュー指摘がなくなるまで修正を継続
4. リンターエラー修正
5. 終了

PostToolUseは使用せず、Stop系イベントのみで制御することで、開発テンポを維持します。

## 特徴

- **専用レビューエージェント**: 別エージェントによるフレッシュな視点でのレビュー
- **状態管理**: `.claude/review/context.json`で進捗を追跡
- **自律的な反復**: エージェントが自分でチェックリストを更新しながら修正を継続
- **軽量動作**: Stop フックは指示生成のみに徹し、実作業はエージェントに委譲

## インストール

1. Claude Codeのプラグインディレクトリにクローン：

```bash
cd ~/.claude/plugins  # またはプロジェクト固有のプラグインディレクトリ
git clone <this-repo> review-loop-plugin
```

2. プラグインを有効化：

Claude Codeの設定でプラグインを有効化してください。

## プラグイン構造

```
review-loop-plugin/
├── agents/                    # カスタムエージェント
│   └── reviewer.md           # コードレビュー専用エージェント
├── hooks/
│   └── hooks.json            # Stop/SubagentStop フック定義
├── scripts/
│   ├── diff_utils.py         # Git差分取得ユーティリティ
│   └── review_on_stop.py     # フックスクリプト
└── README.md
```

### reviewer エージェント

プラグインには `reviewer` エージェントが含まれており、以下の処理を自動的に実行します：

- `.claude/review/context.json` を読み込み
- `patchUnified0` と `targets` を基にコードレビュー
- 指摘事項を `review.checklist` に列挙
- チェックリストの各項目を修正
- すべて解消したら `lint.status` を `'in_progress'` に更新

## 使用方法

プラグインを有効化すると、エージェント停止時に自動的にフックが実行されます。

### 基本フロー

1. コードを編集
2. エージェントが停止
3. Stopフックが`context.json`を生成し、次のアクションを指示
4. Task tool で reviewer エージェントを起動
5. reviewer エージェントがレビュー→修正を反復
6. レビュー完了後、リンター修正に進む
7. すべて解消で終了

### 状態ファイル

`.claude/review/context.json`の構造：

```json
{
  "generatedAt": "2025-10-14T00:00:00Z",
  "review": {
    "targets": ["src/a.ts", "src/b.ts"],
    "patchUnified0": "diff --git ...",
    "checklist": [
      "変数名をキャメルケースに統一",
      "エラーハンドリングを追加"
    ]
  },
  "lint": {
    "tools": ["eslint", "ruff"],
    "status": "pending"
  }
}
```

- `review.checklist`: Claudeが自律的に埋めて解消していく項目
- `lint.status`: `pending` → `in_progress` → `done`

## 設定

### タイムアウト

`hooks/hooks.json`でタイムアウトを調整可能（デフォルト45秒）：

```json
{
  "type": "command",
  "command": "${CLAUDE_PLUGIN_ROOT}/scripts/review_on_stop.py",
  "timeout": 45000
}
```

### リンター

`scripts/review_on_stop.py`の`lint.tools`配列でリンターを設定：

```python
"lint": {
    "tools": ["eslint", "ruff", "mypy"],
    "status": "pending"
}
```

## デバッグ

```bash
# フック実行の詳細ログを確認
claude --debug

# 登録されたフックを確認
/hooks
```

## 注意事項

- フックは任意のコマンドを実行できるため、信頼できる環境でのみ使用してください
- Git リポジトリでの使用を推奨（差分検出のため）
- Python 3.6以上が必要

## ライセンス

MIT
