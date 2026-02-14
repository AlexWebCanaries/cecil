from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"


def _collect_entries_from_git() -> list[str] | None:
    try:
        proc = subprocess.run(
            ["git", "log", "--pretty=format:%s", "--no-merges", "-n", "100"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.splitlines()


def _collect_entries_from_file(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def _render(entries: list[str]) -> str:
    buckets: dict[str, list[str]] = {"feat": [], "fix": [], "docs": [], "test": [], "chore": []}
    for line in entries:
        for key in buckets:
            prefix = f"{key}:"
            if line.startswith(prefix):
                buckets[key].append(line[len(prefix) :].strip())
                break

    out = ["# Changelog", "", "## Unreleased"]
    for key, items in buckets.items():
        if not items:
            continue
        out.append("")
        out.append(f"### {key}")
        for item in items:
            out.append(f"- {item}")

    if all(not values for values in buckets.values()):
        out.extend(["", "- No categorized changes found."])

    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate changelog from git or fallback notes")
    parser.add_argument(
        "--fallback-file",
        default="RELEASE_NOTES_INPUT.txt",
        help="Path to fallback input when git metadata is unavailable",
    )
    args = parser.parse_args()

    entries = _collect_entries_from_git()
    source = "git"

    if entries is None:
        fallback_path = (ROOT / args.fallback_file).resolve()
        entries = _collect_entries_from_file(fallback_path)
        source = f"fallback:{fallback_path.name}"

    CHANGELOG.write_text(_render(entries))
    print(f"Wrote {CHANGELOG} (source={source})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
