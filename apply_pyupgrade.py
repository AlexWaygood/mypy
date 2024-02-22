from __future__ import annotations

import subprocess
from pathlib import Path

DIRECTORIES = ("mypy", "mypyc", "scripts", "misc", "docs")
BRANCH_NAME = "future-annotations"
BAD_TEST_FILE = "mypy/test/testinfer.py"


def run(*args, check: bool = True) -> None:
    subprocess.run(list(args), check=check)


def commit(message: str) -> None:
    run("git", "add", *DIRECTORIES)
    run("git", "commit", "-m", message)


def checkout_and_sync_with_master() -> None:
    run("git", "checkout", "master")
    run("git", "pull", "upstream", "master")
    run("git", "push")


def cleanup() -> None:
    run("git", "restore", "--staged", *DIRECTORIES)
    checkout_and_sync_with_master()


def main() -> None:
    checkout_and_sync_with_master()
    run("git", "branch", "-D", BRANCH_NAME, check=False)
    run("git", "checkout", "-b", BRANCH_NAME)

    for directory in DIRECTORIES:
        run("com2ann", directory)
    commit("Convert type comments to annotations using com2ann")

    for directory in DIRECTORIES:
        run("pyupgrade", *Path(directory).rglob("*.py"), check=False)
    commit("Apply pyupgrade")

    with open(BAD_TEST_FILE) as f:
        old = f.read()
    new = old.replace(
        "callee_kinds_: list[ArgKind | tuple[ArgKind, str]],",
        "callee_kinds_: list[ArgKind | Tuple[ArgKind, str]],",
    )
    with open(BAD_TEST_FILE, "w") as f:
        f.write(new)
    commit("Fix name collision in mypy/test/testinfer.py")

    for directory in DIRECTORIES:
        run("autoflake", "--in-place", *Path(directory).rglob("*.py"))
        run("pycln", "--all", "--exclude", r"mypyc/primitives/registry\.py", directory)
    commit("Remove unused imports using autoflake and pycln")

    run("black", ".")
    run("isort", ".")
    commit("black and isort")

    run("git", "push", "--set-upstream", "origin", BRANCH_NAME, "--force")


if __name__ == "__main__":
    try:
        main()
    finally:
        cleanup()
