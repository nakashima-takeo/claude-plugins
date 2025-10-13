"""
差分取得・要約のためのユーティリティ

将来的な拡張のための基本構造を提供する。
現在は review_on_stop.py に統合されているが、より複雑な差分処理が必要になった場合に使用。
"""
import subprocess
import pathlib
from typing import List, Tuple, Optional


def run_command(
    cmd: List[str],
    cwd: Optional[pathlib.Path] = None,
    timeout: int = 30
) -> Tuple[int, str, str]:
    """コマンドを実行して結果を返す"""
    try:
        p = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except subprocess.TimeoutExpired:
        return 1, "", "Command timeout"
    except Exception as e:
        return 1, "", str(e)


def get_git_diff_files(root: pathlib.Path, ref: str = "HEAD") -> List[str]:
    """Git で変更されたファイル一覧を取得"""
    code, output, _ = run_command(
        ["git", "diff", "--name-only", ref],
        cwd=root
    )
    if code != 0:
        return []
    return [f for f in output.splitlines() if f]


def get_git_diff_unified(
    root: pathlib.Path,
    ref: str = "HEAD",
    unified: int = 0
) -> str:
    """Git で unified 形式の差分を取得"""
    code, output, _ = run_command(
        ["git", "diff", f"--unified={unified}", ref],
        cwd=root
    )
    if code != 0:
        return ""
    return output


def summarize_diff(patch: str, max_lines: int = 100) -> str:
    """差分を要約（将来的な拡張用）"""
    lines = patch.splitlines()
    if len(lines) <= max_lines:
        return patch

    # 先頭部分のみ返す
    return "\n".join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines)"


def filter_files_by_extension(
    files: List[str],
    extensions: List[str]
) -> List[str]:
    """拡張子でファイルをフィルタリング"""
    return [
        f for f in files
        if any(f.endswith(ext) for ext in extensions)
    ]
