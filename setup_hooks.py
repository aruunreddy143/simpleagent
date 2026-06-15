"""
Run once to wire up the pre-commit hook:
    python setup_hooks.py
"""
import subprocess
import sys
from pathlib import Path

HOOK_SCRIPT = """\
#!/bin/sh
# Pre-commit hook: auto-generate unit tests for staged Python files
echo "[pre-commit] Running unit test generator agent..."

# Prefer venv Python so all dependencies are available
if [ -f ".venv/Scripts/python" ]; then
    PYTHON=".venv/Scripts/python"
elif [ -f ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
else
    PYTHON="python"
fi

$PYTHON generate_tests_agent.py
STATUS=$?
if [ $STATUS -ne 0 ]; then
    echo "[pre-commit] Test generation failed (exit $STATUS). Commit aborted."
    exit 1
fi
"""


def main() -> None:
    repo_root = Path(".")

    if not (repo_root / ".git").exists():
        print("No .git directory found. Initialising git repository...")
        subprocess.run(["git", "init"], check=True)

    hooks_dir = repo_root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    hook_path = hooks_dir / "pre-commit"
    hook_path.write_text(HOOK_SCRIPT, encoding="utf-8")

    # chmod +x on Unix/Mac; Windows Git honours the shebang via Git Bash
    if sys.platform != "win32":
        hook_path.chmod(0o755)

    print(f"Pre-commit hook installed: {hook_path}")
    print("From now on, unit tests will be auto-generated and staged before every commit.")
    print("Run  pytest --cov=. --cov-report=xml  to produce coverage.xml for SonarQube.")


if __name__ == "__main__":
    main()
