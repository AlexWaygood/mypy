import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def run(*args: str, check: bool = True, **kwargs: Any) -> str:
    result = subprocess.run(list(args), check=check, capture_output=True, text=True, **kwargs)
    return result.stdout or ""


def run_stubtest(*, typeshed_dir: str) -> str:
    """This function is basically copied from typeshed's stubtest_stdlib.py."""

    allowlist_dir = Path(typeshed_dir, "tests", "stubtest_allowlists")
    version_allowlist = f"py{sys.version_info.major}{sys.version_info.minor}.txt"
    platform_allowlist = f"{sys.platform}.txt"
    combined_allowlist = f"{sys.platform}-py{sys.version_info.major}{sys.version_info.minor}.txt"

    cmd = [
        sys.executable,
        "-m",
        "mypy.stubtest",
        "--check-typeshed",
        "--custom-typeshed-dir",
        typeshed_dir,
        "--allowlist",
        str(allowlist_dir / "py3_common.txt"),
        "--allowlist",
        str(allowlist_dir / version_allowlist),
    ]
    if (allowlist_dir / platform_allowlist).exists():
        cmd += ["--allowlist", str(allowlist_dir / platform_allowlist)]
    if (allowlist_dir / combined_allowlist).exists():
        cmd += ["--allowlist", str(allowlist_dir / combined_allowlist)]
    if sys.version_info < (3, 10):
        # As discussed in https://github.com/python/typeshed/issues/3693, we only aim for
        # positional-only arg accuracy for the latest Python version.
        cmd.append("--ignore-positional-only")
    return run(*cmd, check=False)


def checkout_and_sync_with_master() -> None:
    run("git", "checkout", "master")
    run("git", "pull", "upstream", "master")
    run("git", "push")


def get_stubtest_diff(*, pr_url: str | None, branch: str | None, typeshed_dir: str) -> str:
    print("Checking out and syncing mypy master...")
    checkout_and_sync_with_master()
    print("Running stubtest using mypy master...")
    old_results = run_stubtest(typeshed_dir=typeshed_dir)
    print("Checking out and syncing the PR...")
    if pr_url is not None:
        run("gh", "pr", "checkout", pr_url)
    else:
        assert branch is not None
        run("git", "checkout", branch)
    print("Running stubtest using the PR...")
    new_results = run_stubtest(typeshed_dir=typeshed_dir)
    print("Getting the diff...")
    with tempfile.TemporaryDirectory() as td:
        old, new = Path(td, "old.txt"), Path(td, "new.txt")
        for path, result in [(old, old_results), (new, new_results)]:
            path.write_text(result)
        diff_results = run("git", "diff", "--no-index", str(old), str(new), check=False)
    print("Cleaning up...")
    checkout_and_sync_with_master()
    return "\n".join(filter(None, diff_results.splitlines()))


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    to_check = parser.add_mutually_exclusive_group(required=True)
    to_check.add_argument("--pr", type=str, help="URL to a stubtest PR to check")
    to_check.add_argument("--branch", type=str, help="Local branch to check")
    parser.add_argument(
        "--typeshed-dir", type=str, required=True, help="Path to a local clone of typeshed"
    )
    parser.add_argument(
        "--output-file", type=str, help="File to write output to (writes to stdout if not set)"
    )
    args = parser.parse_args()

    diff = get_stubtest_diff(pr_url=args.pr, branch=args.branch, typeshed_dir=args.typeshed_dir)

    if args.output_file:
        with open(args.output_file, "w") as f:
            f.write(diff)
        print(f"Success! The diff has been written to {args.output_file!r}")
    else:
        print(diff)


if __name__ == "__main__":
    main()
