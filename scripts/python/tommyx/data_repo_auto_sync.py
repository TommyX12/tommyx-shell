#!/usr/bin/env python3

import glob
import subprocess
import os
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import pydantic

# verbose flag, controlled via command-line
VERBOSE = False
# pull-only flag, controlled via command-line
PULL_ONLY = False
# max workers, controlled via command-line
MAX_WORKERS = 16

REPOS_TO_CHECK = [
    "~/data/*",
]

# ANSI color codes for terminal output
RED = '\033[31m'
GREEN = '\033[32m'
BLUE = '\033[34m'
RESET = '\033[0m'

REPO_CONFIG_FILE = ".repo_auto_sync.json"


class RepoConfig(pydantic.BaseModel):
    auto_pull: bool = False
    auto_push: bool = False
    auto_rebase_on_failed_push: bool = False


def get_repo_config(repo):
    config_file = os.path.join(repo, REPO_CONFIG_FILE)
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                if hasattr(RepoConfig, 'model_validate_json'):
                    config = RepoConfig.model_validate_json(f.read())
                else:
                    config = RepoConfig.parse_raw(f.read())
                return config

        except pydantic.ValidationError as e:
            print(f"Invalid config file for repo {format_repo(repo)}: {e}")
            return RepoConfig()

    return RepoConfig()


def red(text):
    return f"{RED}{text}{RESET}"


def green(text):
    return f"{GREEN}{text}{RESET}"


def blue(text):
    return f"{BLUE}{text}{RESET}"


def format_repo(repo):
    return f"{blue(f'[{repo}]')}"


def run_command(command, shell=True, check=True, cwd=None):
    if VERBOSE: print(f"Running command: {command}")
    try:
        result = subprocess.run(
            command, shell=shell, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, cwd=cwd
        )
        outtext, outerr = result.stdout, result.stderr
        out = outtext + outerr
        if VERBOSE: print(out)
        return outtext, outerr

    except subprocess.CalledProcessError as e:
        # always print errors
        print(e.stdout, e.stderr)
        raise e


def get_git_dirty_text(cwd=None):
    outtext, outerr = run_command("git status", cwd=cwd)
    out = outtext + (outerr if outerr else "")
    out_lower = out.strip().lower()
    if (
        out_lower.find("nothing to commit") == -1
        or out_lower.find("your branch is ahead of") != -1
    ):
        return out

    return None


def check_upstream_commits(cwd=None):
    try:
        run_command("git fetch origin", cwd=cwd)
        outtext, _ = run_command("git rev-list --count HEAD..@{u}", check=False, cwd=cwd)
        count = int(outtext.strip()) if outtext.strip().isdigit() else 0
        return count

    except Exception as e:
        print(f"Failed to check upstream: {e}")
        return 0


def yn_question(prompt):
    return input(red(f"{prompt} [y/n]: ")).strip().lower() == "y"


def get_repo_list():
    repos = []
    for pattern in REPOS_TO_CHECK:
        for p in glob.glob(
            os.path.abspath(os.path.expanduser(pattern)), recursive=True
        ):
            if not os.path.exists(os.path.join(p, ".git")):
                continue

            repos.append(p)

    return repos


def check_repo_status(repo_path):
    """Check status of a single repository and return (repo_path, needs_action, config)"""
    try:
        config = get_repo_config(repo_path)
        needs_action = False

        if get_git_dirty_text(cwd=repo_path) is not None or check_upstream_commits(cwd=repo_path) > 0:
            needs_action = True

        return repo_path, needs_action, config

    except Exception as e:
        print(f"Error checking repo {format_repo(repo_path)}: {e}")
        return repo_path, False, RepoConfig()


def main():
    print("-----------------------------------------------")
    repo_configs = {}
    repos = get_repo_list()
    if not repos:
        print("No repositories found.")

    action_needed = []

    # Use parallel processing for initial scan with max 8 workers
    max_workers = min(MAX_WORKERS, len(repos))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all repo status checks
        future_to_repo = {executor.submit(check_repo_status, repo): repo for repo in repos}

        # Process results as they complete
        for future in as_completed(future_to_repo):
            repo_path, needs_action, config = future.result()
            repo_configs[repo_path] = config

            print(f"{format_repo(repo_path)} ... ", end="")
            if needs_action:
                print(f"{red('action needed')}")
                action_needed.append(repo_path)
            else:
                print(f"{green('up to date')}")

    print("-----------------------------------------------")
    if not action_needed:
        print("No action needed.")

    for p in action_needed:
        config = repo_configs[p]
        print(f"REPO: {format_repo(p)}")

        upstream_count = check_upstream_commits(cwd=p)
        if upstream_count > 0:
            if config.auto_pull or yn_question(f"There are {upstream_count} commits upstream. Run git pull --ff-only?"):  # noqa
                try:
                    print("Running git pull --ff-only...")
                    run_command("git pull --ff-only", cwd=p)
                    print("Done.")

                except Exception as e:
                    print(f"Fast-forward pull failed: {e}")
                    if yn_question("Skip this repo? "):
                        print("Skipped.")
                        continue

                    else:
                        exit(1)

            else:
                print("Skipped.")

        try:
            dirty_text = get_git_dirty_text(cwd=p)
            if dirty_text is not None:
                print(dirty_text)

            else:
                continue

        except Exception as e:
            print(f"Failed to check git status: {e}")
            if yn_question("Skip this repo?"):
                print("Skipped.")
                continue

            else:
                exit(1)

        if PULL_ONLY:
            print("Pull-only mode: skipping push operations.")
        elif config.auto_push or yn_question(
            f"Repository {format_repo(p)} is dirty. Do you want to push all changes with default commit message?"
        ):
            try:
                print("Running git commit and push...")
                run_command("git add -A", cwd=p)
                run_command('git commit -m "update"', check=False, cwd=p)
                run_command("git push", cwd=p)
                print("Done.")

            except Exception as e:
                print(f"Commit & push failed: {e}")
                if config.auto_rebase_on_failed_push or yn_question("Try git pull --rebase?"):
                    try:
                        print("Running git pull --rebase...")
                        run_command("git pull --rebase", cwd=p)
                        print("Done.")
                        if config.auto_push or yn_question("Commit & push again?"):
                            try:
                                print("Running git commit and push again...")
                                run_command("git add -A", cwd=p)
                                run_command('git commit -m "update"', check=False, cwd=p)
                                run_command("git push", cwd=p)
                                print("Done.")
                                continue

                            except Exception as e:
                                print(f"Push failed again: {e}")
                                if yn_question("Skip this repo?"):
                                    print("Skipped.")
                                    continue

                                else:
                                    exit(1)

                    except Exception as e:
                        print(f"Failed to pull.")
                        if yn_question("Skip this repo?"):
                            print("Skipped.")
                            continue

                        else:
                            exit(1)

                if yn_question("Skip this repo?"):
                    print("Skipped.")
                    continue

                else:
                    exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check repo status and push changes")
    parser.add_argument("-v", "--verbose", action="store_true", help="enable verbose output")
    parser.add_argument("--pull-only", action="store_true", help="only pull changes from remote repos, skip all push operations")
    parser.add_argument("--max-workers", type=int, default=MAX_WORKERS, help="maximum number of workers to use for parallel processing")
    args = parser.parse_args()
    # set global flags
    VERBOSE = args.verbose
    PULL_ONLY = args.pull_only
    MAX_WORKERS = args.max_workers

    main()
