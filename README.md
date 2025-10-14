# review-loop-plugin

コードレビュー→修正ループを自動化するClaude Codeプラグイン

## 概要

`/changes-review` コマンドで起動し、以下の処理を自動化：

1. Git差分から変更ファイルを特定
2. reviewer エージェントによる重要度付きレビュー
3. 重要度「高」「中」の指摘を修正
4. 重要度「中」以上の指摘がなくなるまで2-3を繰り返す
5. リンター修正
6. 完了

## 特徴

- **明示的な起動**: `/changes-review` コマンドで実行（フック不要）
- **重要度付きレビュー**: 高・中・低の3段階で優先度を明確化
- **関心の分離**: reviewerはレビューのみ、orchestratorが修正を担当
- **自動ループ**: 重要度「中」以上がなくなるまで自動反復

## インストール

### グローバルインストール（すべてのプロジェクトで使用）

1. ホームディレクトリにプラグインをクローン：

```bash
cd ~
git clone <this-repo-url> review-loop-plugin
```

2. Claude Code の設定ファイル（`~/.claude/config.json`）に追加：

```json
{
  "plugins": [
    "~/review-loop-plugin"
  ]
}
```

### プロジェクト固有インストール

1. プロジェクトのルートディレクトリで：

```bash
git clone <this-repo-url> .claude-plugins/review-loop-plugin
```

2. プロジェクトの `.claude/config.json` に追加：

```json
{
  "plugins": [
    ".claude-plugins/review-loop-plugin"
  ]
}
```

### 動作確認

Claude Code を起動して `/changes-review` コマンドが利用可能か確認：

```bash
# Claude Code で以下を実行
/help
# /changes-review が表示されることを確認
```

## プラグイン構造

```
review-loop-plugin/
├── .claude-plugin/
│   ├── plugin.json           # プラグイン定義
│   └── marketplace.json      # マーケットプレイス情報
├── .claude/
│   └── commands/
│       └── changes-review.md # /changes-review コマンド定義
├── agents/
│   ├── orchestrator.md       # ループ制御エージェント
│   └── reviewer.md           # レビュー専門エージェント
└── README.md
```

**ディレクトリの役割:**
- `.claude-plugin/`: プラグインのメタデータ
- `.claude/commands/`: Slash コマンド定義
- `agents/`: カスタムエージェント定義

### エージェント構成

#### orchestrator エージェント
- レビュー→修正ループ全体を制御
- Git差分から変更ファイルを特定
- reviewer エージェントを起動してレビューを依頼
- 重要度「高」「中」の指摘を修正
- リンター実行・修正

#### reviewer エージェント
- コードレビュー専門（修正は行わない）
- 重要度付き指摘を出力
- 使用可能ツール: Read, Grep, Glob, Bash（Gitのみ）

## 使用方法

### 基本的な使い方

1. コードを編集
2. Claude Codeで `/changes-review` コマンドを実行
3. orchestrator エージェントが自動的に：
   - 変更ファイルを特定
   - reviewer エージェントでレビュー
   - 重要度「高」「中」の指摘を修正
   - 重要度「中」以上がなくなるまで繰り返す
   - リンター修正
   - 完了報告

### フロー図

```mermaid
flowchart TD
    start[/changes-review コマンド] --> orchestrator[orchestrator起動]
    orchestrator --> git[Git差分取得]
    git --> reviewer[reviewer起動]
    reviewer --> check{重要度中以上<br/>の指摘あり？}
    check -- あり --> fix[orchestratorが修正]
    fix --> reviewer
    check -- なし --> lint[リンター修正]
    lint --> done[完了]
```

## レビュー重要度

### 重要度「高」
セキュリティリスク、重大なバグ、データ損失リスク等

### 重要度「中」
コーディング規約違反、変数名の不明瞭さ、エラーハンドリング不足等

### 重要度「低」
コメント不足、リファクタリング提案等

**ループ終了条件**: 重要度「中」以上の指摘がなくなった時点で終了

## 設定

### リンター

orchestrator.md で使用するリンターを変更可能：

- TypeScript/JavaScript: `npx eslint . --fix`
- Python: `ruff check . --fix`

### 最大反復回数

orchestrator.md でループの最大反復回数を調整可能（デフォルト: 5回）

## 注意事項

- Git リポジトリでの使用を推奨（差分検出のため）
- 大規模な変更の場合、レビューに時間がかかる可能性があります
- 無限ループを避けるため、最大5回の反復で強制終了します

## ライセンス

MIT
