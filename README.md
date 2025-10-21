# claude-plugins

個人用Claude Codeプラグイン集

## 概要

このリポジトリは複数のClaude Codeプラグインをまとめたコレクションです。

## 含まれるプラグイン

### 1. general (汎用プラグイン)
コードレビュー、コミット作成、リンター修正など、日常的な開発作業を支援するプラグイン。

詳細: [plugins/general/README.md](./plugins/general/README.md)

### 2. test-writer (テストコード作成プラグイン)
テスト計画書の作成からテストコードの実装まで、品質の高いテスト作成をサポートするプラグイン。

詳細: [plugins/test-writer/README.md](./plugins/test-writer/README.md)

## インストール

### グローバルインストール（すべてのプロジェクトで使用）

1. ホームディレクトリにプラグインをクローン：

```bash
cd ~
git clone <this-repo-url> claude-plugins
```

2. Claude Codeの設定ファイル（`~/.claude/config.json`）に追加：

```json
{
  "plugins": [
    "~/claude-plugins"
  ]
}
```

### プロジェクト固有インストール

1. プロジェクトのルートディレクトリで：

```bash
git clone <this-repo-url> .claude-plugins/claude-plugins
```

2. プロジェクトの `.claude/config.json` に追加：

```json
{
  "plugins": [
    ".claude-plugins/claude-plugins"
  ]
}
```

### 動作確認

Claude Codeを起動してコマンドが利用可能か確認：

```bash
# Claude Codeで以下を実行
/help
```

## ライセンス

MIT
