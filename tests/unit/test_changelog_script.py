from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "generate_changelog.py"
CHANGELOG = ROOT / "CHANGELOG.md"


def test_changelog_fallback_without_git(tmp_path) -> None:
    fallback = ROOT / "RELEASE_NOTES_INPUT.txt"
    fallback.write_text("feat: add fallback mode\nfix: avoid crash\n")

    env = os.environ.copy()
    env["PATH"] = str(tmp_path)

    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--fallback-file", fallback.name],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
    text = CHANGELOG.read_text()
    assert "add fallback mode" in text
    assert "avoid crash" in text


def test_changelog_uses_git_when_available(tmp_path) -> None:
    fake_git = tmp_path / "git"
    fake_git.write_text("#!/bin/sh\necho 'feat: from fake git'\necho 'docs: docs update'\n")
    fake_git.chmod(0o755)

    env = os.environ.copy()
    env["PATH"] = f"{tmp_path}:{env.get('PATH', '')}"

    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
    text = CHANGELOG.read_text()
    assert "from fake git" in text
    assert "docs update" in text
