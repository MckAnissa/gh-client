# src/cli.py
from __future__ import annotations
import argparse
import json
from typing import Any
from dotenv import load_dotenv
import os

from gh_client import GitHubClient, GitHubError


# ---------- pretty printing ----------
def pretty_json(obj: Any) -> None:
    """Colorized, indented JSON without extra deps."""
    text = json.dumps(obj, indent=2, ensure_ascii=False)
    for line in text.splitlines():
        s = line.lstrip()
        if s.startswith('"') and ":" in s:
            # key line
            print(f"\033[96m{line}\033[0m")  # cyan
        elif ":" in line:
            print(f"\033[92m{line}\033[0m")  # green values
        else:
            print(line)


def print_repo_line(repo: dict) -> None:
    name = repo.get("name", "<no name>")
    url = repo.get("html_url", "")
    print(f"\033[93m- {name}\033[0m  →  {url}")  # yellow name


# ---------- subcommand handlers ----------
def cmd_me(args: argparse.Namespace) -> None:
    gh: GitHubClient = args.gh
    pretty_json(gh.get_authenticated_user())


def cmd_user(args: argparse.Namespace) -> None:
    gh: GitHubClient = args.gh
    pretty_json(gh.get_user(args.username))


def cmd_repos(args: argparse.Namespace) -> None:
    gh: GitHubClient = args.gh
    repos = gh.list_user_repos(args.username, per_page=args.per_page)
    for r in repos:
        print_repo_line(r)


def cmd_issues(args: argparse.Namespace) -> None:
    gh: GitHubClient = args.gh
    issues = gh.list_repo_issues(args.owner, args.repo, state=args.state)
    pretty_json(issues)


# ---------- argparse wiring ----------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="gh-client", description="Tiny GitHub API CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("me", help="Show the authenticated user")
    sp.set_defaults(func=cmd_me)

    sp = sub.add_parser("user", help="Show public profile for a username")
    sp.add_argument("username")
    sp.set_defaults(func=cmd_user)

    sp = sub.add_parser("repos", help="List repos for a username")
    sp.add_argument("username")
    sp.add_argument("--per-page", type=int, default=30)
    sp.set_defaults(func=cmd_repos)

    sp = sub.add_parser("issues", help="List issues for a repo")
    sp.add_argument("owner")
    sp.add_argument("repo")
    sp.add_argument("--state", choices=["open", "closed", "all"], default="open")
    sp.set_defaults(func=cmd_issues)

    return p


# ---------- entrypoint ----------
def main() -> None:
    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")
    gh = GitHubClient(token=token)

    parser = build_parser()
    args = parser.parse_args()
    args.gh = gh  # stash client on the args namespace

    try:
        args.func(args)
    except GitHubError as e:
        print(f"\n\033[91m[GitHubError]\033[0m {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
