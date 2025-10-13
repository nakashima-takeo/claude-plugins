"""
差分取得・要約のためのユーティリティ

将来的な拡張のための基本構造を提供する。
現在は review_on_stop.py に統合されているが、より複雑な差分処理が必要になった場合に使用。
"""
import pathlib
import subprocess


def run_command(
    cmd: list[str],
    cwd: pathlib.Path | None = None,
    timeout: int = 30
) -> tuple[int, str, str]:
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


def get_git_diff_files(root: pathlib.Path, ref: str = "HEAD") -> list[str]:
    """Git で変更されたファイル一覧を取得"""
    code, _, _ = run_command(["git", "rev-parse", "--git-dir"], cwd=root)
    if code != 0:
        return []

    tracked: list[str] = []
    code, _, _ = run_command(["git", "rev-parse", "--verify", ref], cwd=root)
    if code == 0:
        diff_code, output, _ = run_command(
            ["git", "diff", "--name-only", ref],
            cwd=root
        )
        if diff_code == 0 and output:
            tracked = [f for f in output.splitlines() if f]
    else:
        ls_code, output, _ = run_command(["git", "ls-files"], cwd=root)
        if ls_code == 0 and output:
            tracked = [f for f in output.splitlines() if f]

    untracked: list[str] = []
    others_code, others_out, _ = run_command(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=root
    )
    if others_code == 0 and others_out:
        untracked = [f for f in others_out.splitlines() if f]

    targets = tracked[:]
    for path in untracked:
        if path not in targets:
            targets.append(path)

    return targets


def get_git_diff_unified(
    root: pathlib.Path,
    ref: str = "HEAD",
    unified: int = 0
) -> str:
    """Git で unified 形式の差分を取得"""
    code, _, _ = run_command(["git", "rev-parse", "--git-dir"], cwd=root)
    if code != 0:
        return ""

    patch_parts: list[str] = []
    code, _, _ = run_command(["git", "rev-parse", "--verify", ref], cwd=root)
    if code == 0:
        diff_code, output, _ = run_command(
            ["git", "diff", f"--unified={unified}", ref],
            cwd=root
        )
        if diff_code == 0 and output:
            patch_parts.append(output)

    others_code, others_out, _ = run_command(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=root
    )
    if others_code == 0 and others_out:
        for path in (p for p in others_out.splitlines() if p):
            diff_code, output, _ = run_command(
                ["git", "diff", f"--unified={unified}", "--no-index", "/dev/null", path],
                cwd=root
            )
            if diff_code in (0, 1) and output:
                patch_parts.append(output)

    return "\n\n".join(part for part in patch_parts if part).strip()


def summarize_diff(patch: str, max_lines: int = 100) -> str:
    """差分を要約（将来的な拡張用）"""
    lines = patch.splitlines()
    if len(lines) <= max_lines:
        return patch

    # 先頭部分のみ返す
    return "\n".join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines)"


def filter_files_by_extension(
    files: list[str],
    extensions: list[str]
) -> list[str]:
    """拡張子でファイルをフィルタリング"""
    return [
        f for f in files
        if any(f.endswith(ext) for ext in extensions)
    ]
