import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_staged_python_files() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True,
    )
    files = result.stdout.strip().split("\n")
    return [
        f
        for f in files
        if f.endswith(".py")
        and not Path(f).name.startswith("test_")
        and "tests/" not in f
        and f != "generate_tests_agent.py"
        and f != "setup_hooks.py"
    ]


def generate_unit_tests(filepath: str, source_code: str) -> str:
    client = OpenAI()
    module_name = Path(filepath).stem

    prompt = f"""Generate comprehensive pytest unit tests for the Python code below.

File: {filepath}
Module: {module_name}

```python
{source_code}
```

Requirements:
- Use pytest with fixtures and parametrize where helpful
- Mock all external dependencies (OpenAI client, env vars, subprocess, file I/O)
- Cover all public functions and methods including edge cases and error paths
- Aim for >80% line coverage so SonarQube does not fail
- Import the module using the correct relative import path
- Return ONLY valid Python test code with no markdown fences or explanations
"""

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert Python test engineer. "
                    "Return only valid pytest code with no markdown or commentary."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )

    test_code = response.choices[0].message.content.strip()
    # Strip accidental markdown fences
    if test_code.startswith("```"):
        test_code = test_code.split("\n", 1)[-1]
    if test_code.endswith("```"):
        test_code = test_code.rsplit("```", 1)[0]
    return test_code.strip()


def write_test_file(source_filepath: str, test_code: str) -> str:
    tests_dir = Path("tests")
    tests_dir.mkdir(exist_ok=True)

    init_file = tests_dir / "__init__.py"
    if not init_file.exists():
        init_file.touch()

    test_filename = f"test_{Path(source_filepath).stem}.py"
    test_filepath = tests_dir / test_filename
    test_filepath.write_text(test_code, encoding="utf-8")
    return str(test_filepath)


def stage_file(filepath: str) -> None:
    subprocess.run(["git", "add", filepath], check=True)


def main() -> int:
    if not os.getenv("OPENAI_API_KEY"):
        print("[test-agent] OPENAI_API_KEY not set — skipping test generation.")
        return 0  # non-blocking: don't abort commit

    staged_files = get_staged_python_files()
    if not staged_files:
        print("[test-agent] No Python source files staged — nothing to do.")
        return 0

    print(f"[test-agent] Generating unit tests for {len(staged_files)} file(s)...")

    for filepath in staged_files:
        if not Path(filepath).exists():
            print(f"[test-agent] Skipping missing file: {filepath}")
            continue

        print(f"[test-agent]   {filepath} ...", end=" ", flush=True)
        source_code = Path(filepath).read_text(encoding="utf-8")

        try:
            test_code = generate_unit_tests(filepath, source_code)
            test_filepath = write_test_file(filepath, test_code)
            stage_file(test_filepath)
            print(f"-> {test_filepath} (staged)")
        except Exception as exc:
            print(f"FAILED ({exc})")
            print("[test-agent] Continuing despite error — commit not blocked.")

    print("[test-agent] Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
