# src/cli.py
from __future__ import annotations
import argparse
import json
from typing import Any

from .gh_client import GitHubClient, GitHubError


def jprint(data: Any):
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_me(args):
    gh = GitHubClient()
    jprint(gh.get_authenticated_user())


def cmd_user(args):
    gh = GitHubClient()
    jprint(gh.get_user(args.username))


def cmd_repos(args):
    gh = GitHubClient()
    jprint(gh.list_user_repos(args.username, per_page=args.per_page))


def cmd_issues(args):
    gh = GitHubClient()
    jprint(gh.list_repo_issues(args.owner, args.repo, state=args.state))


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


def main():
    try:
        args = build_parser().parse_args()
        args.func(args)
    except GitHubError as e:
        print(f"[GitHubError] {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
