import argparse
import os
import subprocess
import sys
import tempfile


def run(*args: str, **kwargs) -> None:
    subprocess.check_call(list(args), **kwargs)


class chdir:
    """Backport of 3.11's contextlib.chdir"""

    def __init__(self, path: str) -> None:
        self.path = path
        self._old_cwd = []

    def __enter__(self) -> None:
        self._old_cwd.append(os.getcwd())
        os.chdir(self.path)

    def __exit__(self, *excinfo: object) -> None:
        os.chdir(self._old_cwd.pop())


VENV_LOCATION = "venv"
VENV_PYTHON = f"{VENV_LOCATION}/Scripts/python.exe"
MYPY_CLONE_LOCATION = "mypy"
TYPESHED_CLONE_LOCATION = "typeshed"
MYPY_REPO_URL = "https://github.com/python/mypy"
TYPESHED_REPO_URL = "https://github.com/python/typeshed"


def run_stubtest(*, pr_url: str | None = None, path_dump: str) -> str:
    with chdir(MYPY_CLONE_LOCATION):
        if pr_url:
            run("gh", "pr", "checkout", pr_url)
        else:
            run("git", "checkout", "master")
    with open(path_dump, "w") as file:
        run(
            VENV_PYTHON,
            "-m",
            "mypy.stubtest",
            "--check-typeshed",
            "--custom-typeshed-dir",
            TYPESHED_CLONE_LOCATION,
            stdout=file,
        )


def _compare_pr_with_master(pr_url: str) -> str:
    run(sys.executable, "-m", "venv", VENV_LOCATION)
    run(VENV_PYTHON, "-m", "pip", "install", "-e", MYPY_CLONE_LOCATION)
    OLD, NEW = "old.txt", "new.txt"
    run_stubtest(path_dump=OLD)
    run_stubtest(pr_url=pr_url, path_dump=NEW)
    run("git", "diff", NEW, OLD, "--no-index")


def compare_pr_with_master(pr_url: str):
    with tempfile.TemporaryDirectory() as td:
        run("git", "-C", td, "clone", MYPY_REPO_URL)
        run("git", "-C", td, "clone", "--depth", "1", TYPESHED_REPO_URL)
        with chdir(td):
            _compare_pr_with_master(pr_url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    args = parser.parse_args()
    compare_pr_with_master(args.url)
