from __future__ import annotations

import subprocess
import sys

TARGET_PATTERNS = [
    "SetuptoolsDeprecationWarning",
    "project.license",
    "License classifiers are deprecated",
]


def main() -> int:
    proc = subprocess.run(
        [sys.executable, "-m", "build"],
        capture_output=True,
        text=True,
        check=False,
    )

    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if proc.returncode != 0:
        print(combined)
        return proc.returncode

    for pattern in TARGET_PATTERNS:
        if pattern in combined:
            print("Build output contains disallowed warning pattern:", pattern)
            return 1

    print("Build warning guard passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
