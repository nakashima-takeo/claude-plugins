#!/usr/bin/env python3
"""
Stop/SubagentStop フック: レビュー→修正ループ→リンター修正を自動化

停止時に差分を検出し、context.json を生成して Claude に次のアクションを指示する。
"""
import json
import os
import sys
import subprocess
import pathlib
import time
from typing import Tuple, List, Dict, Any

ROOT = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
CTX_DIR = ROOT / ".claude" / "review"
CTX_PATH = CTX_DIR / "context.json"


def run(cmd: List[str]) -> Tuple[int, str, str]:
    """コマンドを実行して結果を返す"""
    try:
        p = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30
        )
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except subprocess.TimeoutExpired:
        return 1, "", "Command timeout"
    except Exception as e:
        return 1, "", str(e)


def is_git_repo() -> bool:
    """Git リポジトリかどうかを判定"""
    code, _, _ = run(["git", "rev-parse", "--git-dir"])
    return code == 0


def changed_files_unified0() -> Tuple[List[str], str]:
    """変更されたファイルと unified=0 の差分を取得"""
    if not is_git_repo():
        return [], ""

    # HEAD が存在するか確認
    code, _, _ = run(["git", "rev-parse", "--verify", "HEAD"])
    if code != 0:
        # 初回コミット前の場合、追跡されているファイルをすべて対象にする
        code, files, _ = run(["git", "ls-files"])
        if code == 0 and files:
            targets = [f for f in files.splitlines() if f]
            return targets, ""
        return [], ""

    # 変更ファイル一覧を取得
    code, files, _ = run(["git", "diff", "--name-only", "HEAD"])
    if code != 0:
        return [], ""

    # unified=0 の差分を取得
    code, patch, _ = run(["git", "diff", "--unified=0", "HEAD"])
    if code != 0:
        patch = ""

    targets = [f for f in files.splitlines() if f]
    return targets, patch


def load_context() -> Dict[str, Any]:
    """既存の context.json を読み込む（存在しない場合は空の構造を返す）"""
    if not CTX_PATH.exists():
        return {
            "generatedAt": "",
            "review": {"targets": [], "patchUnified0": "", "checklist": []},
            "lint": {"tools": ["eslint", "ruff"], "status": "pending"}
        }

    try:
        with open(CTX_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "generatedAt": "",
            "review": {"targets": [], "patchUnified0": "", "checklist": []},
            "lint": {"tools": ["eslint", "ruff"], "status": "pending"}
        }


def build_context() -> Dict[str, Any]:
    """コンテキストを構築して保存"""
    targets, patch = changed_files_unified0()

    CTX_DIR.mkdir(parents=True, exist_ok=True)

    ctx = {
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "review": {
            "targets": targets,
            "patchUnified0": patch,
            "checklist": []
        },
        "lint": {
            "tools": ["eslint", "ruff"],
            "status": "pending"
        }
    }

    with open(CTX_PATH, "w", encoding="utf-8") as f:
        json.dump(ctx, f, ensure_ascii=False, indent=2)

    return ctx


def should_allow_stop(ctx: Dict[str, Any]) -> bool:
    """停止を許可すべきかどうかを判定"""
    # 変更がない場合は停止を許可
    if not ctx["review"]["targets"]:
        return True

    # チェックリストが空でリンターステータスが done の場合は停止を許可
    if not ctx["review"]["checklist"] and ctx["lint"]["status"] == "done":
        return True

    return False


def generate_reason(ctx: Dict[str, Any]) -> str:
    """次に実行すべきアクションを生成"""
    ctx_path_rel = CTX_PATH.relative_to(ROOT)

    # チェックリストが空でない場合はレビュー修正を継続
    if ctx["review"]["checklist"]:
        return (
            f"レビュー指摘が残っています。次の順序で進めてください：\n"
            f"1) Read ツールで {ctx_path_rel} を読み込む\n"
            f"2) `review.checklist` の各項目を修正する\n"
            f"3) 修正完了した項目は checklist から削除する\n"
            f"4) すべて解消したら次の停止でリンター修正に進む"
        )

    # チェックリストが空でリンターが pending の場合
    if ctx["lint"]["status"] == "pending":
        return (
            f"レビューが完了しました。次の順序でリンター修正を行ってください：\n"
            f"1) /clear でコンテキストをリセットする\n"
            f"2) Read ツールで {ctx_path_rel} を読み込む\n"
            f"3) `review.patchUnified0` と `targets` を基にレビュー実施\n"
            f"4) 指摘は `review.checklist` に列挙し、空になるまで修正と再レビューを反復\n"
            f"5) checklist が空になったら `lint.status` を 'in_progress' に更新\n"
            f"6) リンター（eslint/ruff等）を実行してエラーを修正\n"
            f"7) エラー0を確認したら `lint.status` を 'done' に更新\n"
            f"8) 次の停止で終了"
        )

    # リンターが in_progress の場合
    if ctx["lint"]["status"] == "in_progress":
        return (
            f"リンター修正を継続してください：\n"
            f"1) リンター（eslint/ruff等）を実行\n"
            f"2) エラーを修正\n"
            f"3) エラー0を確認したら {ctx_path_rel} の `lint.status` を 'done' に更新\n"
            f"4) 次の停止で終了"
        )

    # デフォルト（通常は到達しない）
    return "状態が不明です。context.json を確認してください。"


def main():
    """メイン処理"""
    try:
        # stdin から入力を読み込む
        hook_in = json.load(sys.stdin)

        # 既存のコンテキストを読み込む
        existing_ctx = load_context()

        # 新しいコンテキストを構築
        ctx = build_context()

        # 既存のチェックリストとリンターステータスを引き継ぐ
        if existing_ctx.get("review", {}).get("checklist"):
            ctx["review"]["checklist"] = existing_ctx["review"]["checklist"]
        if existing_ctx.get("lint", {}).get("status"):
            ctx["lint"]["status"] = existing_ctx["lint"]["status"]

        # 更新したコンテキストを保存
        with open(CTX_PATH, "w", encoding="utf-8") as f:
            json.dump(ctx, f, ensure_ascii=False, indent=2)

        # 停止を許可すべきか判定
        if should_allow_stop(ctx):
            print(json.dumps({"decision": None}))
            return

        # 停止をブロックして次のアクションを指示
        reason = generate_reason(ctx)
        print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))

    except Exception as e:
        # エラーは stderr に出力し、exit 1 で非ブロック
        print(f"Error in review_on_stop.py: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
