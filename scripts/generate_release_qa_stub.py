from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "release-qa-summary.md"


def _git_sha() -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return "UNKNOWN_SHA"
    return proc.stdout.strip()


def main() -> int:
    sha = _git_sha()
    now = datetime.now(timezone.utc).isoformat()

    lines = [
        "# Release QA Summary (Stub)",
        "",
        f"Generated at: {now}",
        f"Commit SHA: {sha}",
        "",
        "## Workflow Links",
        "- CI: <ADD_CI_RUN_URL>",
        "- Provider Compat: <ADD_PROVIDER_COMPAT_RUN_URL>",
        "- Release/TestPyPI: <ADD_RELEASE_REHEARSAL_RUN_URL>",
        "",
        "## Validation Matrix",
        "| Check | Status | Notes |",
        "|---|---|---|",
        "| make ci | PENDING | |",
        "| build warning guard | PENDING | |",
        "| twine check | PENDING | |",
        "| wheel smoke check | PENDING | |",
        "| provider compat matrix | PENDING | |",
        "| TestPyPI rehearsal | PENDING | |",
        "",
        "## Signoff",
        "- QA Owner: <NAME>",
        "- Date: <YYYY-MM-DD>",
        "- Decision: <GO/NO-GO>",
    ]
    content = "\n".join(lines) + "\n"
    OUT.write_text(content)
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
