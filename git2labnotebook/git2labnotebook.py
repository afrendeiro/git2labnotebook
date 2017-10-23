#!/usr/bin/env python


import datetime
import os
import sys
from argparse import ArgumentParser

import git
import pandas as pd


def valid_date(s):
    import argparse
    try:
        return datetime.datetime.strptime(s, "%Y%m%d")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


def parse_arguments():
    description = "%(prog)s - Make labnotebook entries from git commits."
    epilog = "For command line options of each command, type: %(prog)s COMMAND -h"
    epilog += "\nhttps://github.com/afrendeiro/git2labnotebook"

    parser = ArgumentParser(description=description, epilog=epilog)
    parser.add_argument("--version", action="version", version="%(prog)s " + "get version")
    parser.add_argument(
        "-d", "--repos-dir",
        dest="repos_dir",
        default=os.path.abspath(os.path.curdir),
        help="Directory with git repositories to inspect. Default=current directory.")
    today = datetime.datetime.now().strftime('%Y%m%d')
    parser.add_argument(
        '-o', '--output-dir', dest="output_dir",
        default=os.path.join(os.path.expanduser("~"), "git2labnotebook", today),
        help="Directory to write output to. Will be created if not existing. Default is the $HOME/git2labnotebook/{}.".format(today))
    parser.add_argument(
        '-f', '--from', dest="date_from",
        type=valid_date, default=None,
        help="Earlier date to filter entries to. Format=YYYYMMDD. Default=None.")
    parser.add_argument(
        '-t', '--to', dest="date_to",
        type=valid_date, default=today,
        help="Later date to filter entries to. Format=YYYYMMDD. Default=None.")
    parser.add_argument(
        '-u', '--git-user', dest="git_user",
        default=None,
        help="Git username to filter commits for (all others will be ignored). Default None.")
    parser.add_argument(
        '-fr', '--filter-repos', dest="repo_filter",
        default=None,
        help="Comma-separated list of repositories to ignore. Default None.")
    parser.add_argument(
        '--no-summary', dest="daily_summary", action="store_false",
        help="Whether daily entries will not contain a summary of lines changed. Default=False.")
    parser.add_argument(
        '--fill', dest="fill", action="store_true",
        help="Whether workdays without entries should be filled with random messages from a pool. Default=False.")

    args = parser.parse_known_args()
    if args[0].repo_filter is not None:
        args[0].repo_filter = args[0].repo_filter.split(",")

    return args


def get_commits(repos_dir):
    """
    """
    output = pd.DataFrame()
    for repo in os.listdir(repos_dir):
        repo_dir = os.path.join(repos_dir, repo, ".git")

        # run git log command
        try:
            g = git.Git(repo_dir)
            out = g.log("--numstat", "--date=iso")
        except:  # will occur if not a git repo
            continue

        # write repo header to file
        parsed = parse_git_log_stats(out)
        parsed["repository"] = repo

        output = output.append(parsed)
    return output


def parse_git_log_stats(log):
    """
    The collected stats will contain (list of lists):
    - commit hash
    - author
    - date
    - commit message
    - file name
    - change_type [ins, del]
    - change (one entry per file)
    """
    entries = list()

    for line in log.split("\n"):
        if line.startswith("commit"):
            # new commit
            commit = line.split(" ")[1]

            # check if previous co

        elif line.startswith("Author:"):
            author = line.split("Author:")[1].strip()

        elif line.startswith("Date:"):
            date = line.split("Date:")[1].strip()

        elif line.startswith(" " * 4):
            msg = line.strip()

        elif line.startswith(tuple([str(i) for i in range(10)]) + ("-", )):
            file_name = line.split("\t")[-1]
            for change, change_type in zip(line.split("\t")[:-1], ("ins", "del")):
                entries.append([commit, author, date, msg, file_name, change_type, change])

    return pd.DataFrame(
        entries, columns=["hash", "author", "date", "message", "file_name", "change_type", "change"])


def gitlog2text(git_log, min_day=None, max_day=None, daily_summary=True, fill_messages=False):
    """
    """
    t_day_header = """# {date}\n"""
    t_repo = """### "{repo}" project.\n"""
    t_commit = """     - {message}"""
    t_day_footer = """Total of {} deleted/modified lines and {} added lines across all projects.\n"""

    git_log["date"] = pd.to_datetime(git_log["date"])
    git_log = git_log.sort_values("date").set_index(['date'])
    git_log.index = git_log.index.date

    # calculate changes (insertion/deletions separately)
    daily_changes = git_log.reset_index().groupby(["index", "change_type"])["change"].apply(
        lambda x: sum([int(i) for i in x if i != "-"]))

    if min_day is None:
        min_day = git_log.index.min()
    else:
        min_day = pd.to_datetime(min_day).to_pydatetime()
    if max_day is None:
        max_day = git_log.index.max()
    else:
        max_day = pd.to_datetime(max_day).to_pydatetime()

    text = list()
    for day in pd.date_range(min_day, max_day, freq="D"):
        try:
            day_commits = git_log.ix[day.date()]
        except KeyError:
            if fill_messages:
                text.append(t_day_header.format(date=day.date()))
                text.append(t_commit.format(message="Reading papers.\n"))
            else:
                continue

        if fill_messages:
            if day_commits.shape[0] < 1:
                if day.isoweekday() < 6:
                    text.append(t_day_header.format(date=day.date()))
                    text.append(t_commit.format(message="Reading papers.\n"))
                    continue
                else:
                    continue

        if day.isoweekday() < 6:
            text.append(t_day_header.format(date=day.date()))

        for repo in day_commits["repository"].drop_duplicates():
            text.append(t_repo.format(repo=repo))
            for commit in day_commits[day_commits["repository"] == repo]["hash"].drop_duplicates():
                text.append(t_commit.format(message=git_log[git_log["hash"] == commit]["message"].drop_duplicates().squeeze()))
        if daily_summary:
            text.append(t_day_footer.format(daily_changes.loc[day.date().isoformat(), "del"], daily_changes.loc[day.date().isoformat(), "ins"]))

    return text


def main():
    # Parse command-line arguments
    args, _ = parse_arguments()

    # Get commits for all repositories
    git_log = get_commits(args.repos_dir)

    # Filter by user if required
    if args.git_user:
        git_log = git_log[git_log["author"].str.contains(args.git_user)]

    # Filter projects if required
    if args.git_user:
        git_log = git_log[~git_log["repository"].str.contains("|".join(args.repo_filter))]

    # Save log
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    git_log.to_csv(os.path.join(args.output_dir, "git_log.csv"), index=False, encoding="utf-8")

    # Make text
    text = gitlog2text(
        git_log,
        min_day=args.date_from, max_day=args.date_to,
        daily_summary=args.daily_summary, fill_messages=args.fill)

    with open(os.path.join(args.output_dir, "notebook.md"), "w") as handle:
        handle.writelines("\n".join(text))


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("Program canceled by user!")
        sys.exit(1)
