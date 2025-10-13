# テスト計画

## 動作確認チェックリスト

### 1. プラグインのインストール確認

- [ ] `.claude-plugin/plugin.json` が正しく配置されている
- [ ] `claude plugin validate .` が成功する
- [ ] プラグインが Claude Code に認識される

### 2. 基本動作テスト

#### 2.1 基本的なレビューフロー
- [ ] 1ファイルを編集
- [ ] エージェントを停止
- [ ] Stop フックが `decision:"block"` を返す
- [ ] `reason` に次の手順が明示される
- [ ] Claude が自動的にレビューを開始

#### 2.2 レビュー反復
- [ ] `review.checklist` が空でない状態で停止
- [ ] 停止がブロックされ、修正継続が指示される
- [ ] `review.checklist` を 1→0 にして停止
- [ ] リンター修正フェーズに遷移

#### 2.3 リンター完了
- [ ] `lint.status` を `"pending"` → `"in_progress"` に更新
- [ ] eslint/ruff でエラー0を達成
- [ ] `lint.status` を `"done"` に更新
- [ ] 停止が許可される

#### 2.4 変更なしケース
- [ ] 編集せずに停止
- [ ] 即座に停止が許可される

### 3. サブエージェントテスト

- [ ] サブエージェントを起動
- [ ] サブエージェントが停止
- [ ] `SubagentStop` フックが動作
- [ ] メインエージェントと同様のフローで動作

### 4. コンテキストファイルの検証

- [ ] `.claude/review/context.json` が生成される
- [ ] `review.targets` にファイルリストが含まれる
- [ ] `review.patchUnified0` に差分が含まれる
- [ ] `review.checklist` が正しく更新される
- [ ] `lint.status` が適切に遷移する

### 5. エラーハンドリング

- [ ] Git リポジトリでない環境での動作
- [ ] Python が利用できない環境でのエラーメッセージ
- [ ] スクリプト実行権限がない場合の挙動
- [ ] タイムアウト発生時の動作

### 6. パフォーマンステスト

- [ ] 大量のファイル変更時（100+ファイル）の動作
- [ ] 大きなファイル（10000+行）の差分処理
- [ ] タイムアウト（45秒）内に処理が完了

### 7. セキュリティチェック

- [ ] `.env` ファイルが差分に含まれない
- [ ] 機密情報が `context.json` に含まれない
- [ ] スクリプトが意図しないコマンドを実行しない

### 8. デバッグ機能

- [ ] `claude --debug` でフック実行ログが確認できる
- [ ] `/hooks` で登録フックが表示される
- [ ] エラーが stderr に正しく出力される

## マニュアルテスト手順

### テスト環境のセットアップ

```bash
# テスト用リポジトリを作成
mkdir test-project
cd test-project
git init
echo "console.log('hello');" > test.js
git add test.js
git commit -m "Initial commit"
```

### テスト1: 基本動作

```bash
# ファイルを編集
echo "console.log('world');" >> test.js

# Claude Code を起動してエージェントを停止
# Stop フックが発火することを確認
```

### テスト2: レビュー反復

```bash
# context.json を確認
cat .claude/review/context.json

# checklist に項目を追加
# Claude が自動的に修正を継続することを確認
```

### テスト3: リンター修正

```bash
# eslint をインストール
npm init -y
npm install --save-dev eslint

# Claude がリンターエラーを修正することを確認
```

## 自動テスト（将来の拡張）

現在は手動テストのみですが、以下の自動テストを追加することを検討：

- [ ] `review_on_stop.py` のユニットテスト
- [ ] `diff_utils.py` のユニットテスト
- [ ] hooks.json の JSON スキーマ検証
- [ ] 統合テスト（モックフックイベント）

## バリデーション

```bash
# プラグインのバリデーション
claude plugin validate .

# JSON構文チェック
jq . .claude-plugin/plugin.json
jq . .claude-plugin/marketplace.json
jq . hooks/hooks.json
```

## デバッグコマンド

```bash
# フックの実行を確認
claude --debug

# 登録されたフックを表示
/hooks

# context.json を確認
cat .claude/review/context.json
```
