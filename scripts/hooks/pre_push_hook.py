#!/usr/bin/env python3

import os
import subprocess
import sys
from typing import List

import colorama
import git


def get_changed_files_since_remote_master() -> List[str]:
    """ Get the changed files locally as compared to remote master """
    local_repo = git.repo.Repo(".")
    remote_master = local_repo.heads.master.tracking_branch()

    if not remote_master or not remote_master.is_valid():
        raise Exception("Could not find tracking branch for master")

    local_branch = local_repo.active_branch
    common_ancestor = local_repo.merge_base(local_branch, remote_master)[0]

    diffs = common_ancestor.diff(local_branch.commit)

    return [
        os.path.join(local_repo.working_dir, changed_file.b_path)
        for changed_file in diffs
        if not changed_file.deleted_file and is_valid_python_file(changed_file.b_path)
    ]


def is_valid_python_file(file_path: str) -> bool:
    """ Check if the passed file path is a python file """
    if file_path.endswith(".py"):
        return True
    # Is it a script?
    try:
        with open(file_path, "r") as file_p:
            shebang = file_p.read()
            return shebang.startswith("#!") and "python" in shebang
    except UnicodeDecodeError:
        return False

    return False


def run_pylint(files: List[str], repo_cwd: str) -> None:
    """ Execute pylint. Exits the program with 1 if pylint finishes with a non-zero exit status. """
    print("Running pylint.")
    try:
        subprocess.run(["scripts/linting", *files],
                       stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT,
                       cwd=repo_cwd,
                       check=True)
    except subprocess.CalledProcessError as exc:
        print("Pylint failed:")
        print()
        print(colorama.Fore.RED, exc.output.decode("utf-8"), colorama.Style.RESET_ALL)
        print("You can manually run pylint with `scripts/pylint`")
        sys.exit(1)


def run_mypy(files: List[str], repo_cwd: str) -> None:
    """ Execute mypy. Exits the program with 1 if mypy finishes with a non-zero exit status. """
    print("Running typing check.")
    try:
        subprocess.run(["scripts/typing", *files],
                       stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT,
                       cwd=repo_cwd,
                       check=True)
    except subprocess.CalledProcessError as exc:
        print("Mypy failed:")
        print()
        print(colorama.Fore.RED, exc.output.decode("utf-8"), colorama.Style.RESET_ALL)
        print("You can manually run mypy with `scripts/typing`")
        sys.exit(1)


def run_autofix(files: List[str], repo_cwd: str) -> None:
    """ Execute autofix. Exits the program with 1 if autofix finishes with a non-zero exit status. """
    print("Running autofixes.")
    try:
        subprocess.run(["scripts/autofix", *files],
                       stderr=subprocess.STDOUT,
                       stdout=subprocess.PIPE,
                       cwd=repo_cwd,
                       check=True)
    except subprocess.CalledProcessError as exc:
        print("Autofix failed:")
        print()
        print(colorama.Fore.RED, exc.output.decode("utf-8"), colorama.Style.RESET_ALL)
        print("You can manually run autofix with `scripts/autofix`")
        sys.exit(1)


def get_uncommited_files() -> List[str]:
    """ Get any currently uncommited files """
    local_repo = git.repo.Repo(".")
    repo_cwd = local_repo.working_dir
    diff_list = local_repo.index.diff(None)
    return [
        os.path.join(repo_cwd, diff.b_path) for diff in
        diff_list
    ]


def main() -> None:
    """ Main entrypoint"""
    colorama.init()
    repo_cwd = git.repo.Repo(".").working_dir
    changed_files = get_changed_files_since_remote_master()
    if len(changed_files) != 0:
        print("Checking:")
        for path in changed_files:
            print(f"    {os.path.relpath(path, repo_cwd)}")
        print()
        run_autofix(changed_files, repo_cwd)
        run_mypy(changed_files, repo_cwd)
        run_pylint(changed_files, repo_cwd)
        uncomitted = get_uncommited_files()
        # Are any of the uncommited files also files that we have changed?
        # Those were probably changed during autofix and need to be comitted.
        uncommited_changed_files = [
            os.path.relpath(path, repo_cwd)
            for path in set(uncomitted).intersection(set(changed_files))
        ]
        if uncommited_changed_files:
            print("Please commit changes to the following files:")
            for uncommited_file in uncommited_changed_files:
                print(f"    {uncommited_file}")

            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
