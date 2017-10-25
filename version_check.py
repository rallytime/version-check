# -*- coding: utf-8 -*-
'''
A simple tool to search the Salt GitHub repository branches and tags
for pull request numbers or git commits.

This tool outputs the list of branches and/or tags that the provided
pull request or git commit is found in.

A git fetch is performed at the beginning of the main function. This
provides the most up-to-date search results for the given pull request
or commit sha.

The salt repository is located at: https://github.com/saltstack/salt

NOTE: This script relies on the Dockerfile contained in this repository
and makes some assumptions about the git repository clone and setup.
Most of these assumptions can be mitigated by updating the ``GIT_DIR``
and ``REMOTE`` global variables. However, support for this tool relies
on the script's functionality in tandem with the Dockerfile.
'''

# Import Python libs
import argparse
import getopt
import subprocess
import sys

# Define global variables
GIT_DIR = '--git-dir=/salt/.git'
REMOTE = 'origin'
VERSION = 'v0.1.0'


def main(args):
    '''
    Run!

    Prints results to the screen, as well as returning a result dict.
    '''
    branches = []
    tags = []

    # Parse args and define some basic params
    args = parse_args(args)
    commit = args.commit
    pr_num = args.pull_request
    branch_lims = args.branch
    tag_lims = args.tag

    # Fetch latest from GitHub
    if not args.skip_fetch:
        cmd_run(['git', GIT_DIR, 'fetch', REMOTE])

    # Get commit sha from PR number
    if pr_num:
        commit = get_sha(pr_num)

        # Return if an error occurred in get_sha call
        if isinstance(commit, dict):
            print(commit.get('error'))
            return commit

    # Get matching branches and tags based on limiters (if any)
    if branch_lims:
        # Branch limiter is passed
        branches = get_branch_matches(commit, limiters=branch_lims)
        if tag_lims:
            # Tag limiter is passed with a branch limiter
            tags = get_tag_matches(commit, limiters=tag_lims)
    elif tag_lims:
        # Only a tag limiter is passed
        tags = get_tag_matches(commit, limiters=tag_lims)
    else:
        # Search all branches and tags
        branches = get_branch_matches(commit)
        tags = get_tag_matches(commit)

    ret = {}

    found = False
    if branches:
        found = True
        ret['Branches'] = branches
        print('Branches:')
        for branch in branches:
            print('  ' + branch)

    if tags:
        found = True
        ret['Tags'] = tags
        print('Tags:')
        for tag in tags:
            print('  ' + tag)

    if found is False:
        comment = 'The {0} \'{1}\' was not found.'.format('pull request' if pr_num else 'commit',
                                                          pr_num if pr_num else commit)
        print(comment)
        ret['comment'] = comment

    return ret


def cmd_run(cmd_args):
    '''
    Runs the given command in a subprocess and returns a dictionary containing
    the subprocess pid, retcode, stdout, and stderr.

    cmd_args
        The list of program arguments constructing the command to run.
    '''
    ret = {}
    try:
        proc = subprocess.Popen(
            cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
    except (OSError, ValueError) as exc:
        ret['stdout'] = str(exc)
        ret['stderr'] = ''
        ret['retcode'] = 1
        ret['pid'] = None
        return ret

    ret['stdout'], ret['stderr'] = proc.communicate()
    ret['pid'] = proc.pid
    ret['retcode'] = proc.returncode
    return ret


def get_branch_matches(commit, limiters=None):
    '''
    Returns a list of branches that contain the given commit.

    commit
        The commit sha to search for or match against.

    limiters
        The list of branches to limit the search. Default: search all branches.
    '''
    branches = []
    cmd_ret = cmd_run(['git', GIT_DIR, 'branch', '-a', '--contains', commit])
    strip_len = len('/'.join(['remotes', REMOTE])) + 1
    for line in cmd_ret['stdout'].splitlines():
        line = line.strip()
        if line.startswith('remotes/'):
            # strip off remotes/REMOTE/
            line = line[strip_len:]
            if line.startswith('HEAD'):
                continue
            branches.append(line)

    if limiters:
        ret = []
        for limiter in limiters:
            if limiter in branches:
                ret.append(limiter)
        return ret

    return branches


def get_tag_matches(commit, limiters=None):
    '''
    Returns the list of published tags that contain the given commit.

    commit
        The commit sha to search for or match against.

    limiters
        The list of tags to limit the search. Default: search all tags.
    '''
    tags = []
    cmd_ret = cmd_run(['git', GIT_DIR, 'tag', '--contains', commit])
    for line in cmd_ret['stdout'].splitlines():
        if line.startswith('v'):
            tags.append(line)

    if limiters:
        ret = []
        for limiter in limiters:
            if limiter in tags:
                ret.append(limiter)
        return ret

    return tags


def get_sha(pr_num):
    '''
    Returns a git commit sha from the provided pull request number.

    pr_num
        The number of the PR.
    '''
    pr_num = pr_num.lstrip('#')
    branch_name = 'pr-{0}'.format(pr_num)

    # Create local branch from PR number
    branch_cmd = cmd_run(['git',
                          GIT_DIR,
                          'fetch',
                          REMOTE,
                          'pull/{0}/head:{1}'.format(pr_num, branch_name)])
    if branch_cmd['retcode'] != 0:
        return {'error': 'ERROR: {0}'.format(branch_cmd['stdout'])}

    # Get the commit at the HEAD of the local branch
    cmd_ret = cmd_run(['git', GIT_DIR, 'rev-parse', branch_name])
    sha = cmd_ret['stdout'].strip()

    # Clean up the newly created branch
    cmd_run(['git', GIT_DIR, 'branch', '-D', branch_name])

    return sha


def parse_args(args):
    '''
    Parse the CLI options.
    '''
    # Define parser and set up basic options
    parser = argparse.ArgumentParser(description='Search for pull requests or commits in Salt')
    parser.add_argument('-v', '--version', action='version', version=VERSION, help='Print version and exit.')
    parser.add_argument('--skip-fetch', action='store_true', help='Do not fetch latest from upstream.')

    # Define mutually exclusive group: Can only search for a PR or commit, not both.
    search_items = parser.add_mutually_exclusive_group(required=True)
    search_items.add_argument('-p', '--pull-request', help='Pull request number to search for.')
    search_items.add_argument('-c', '--commit', help='Commit hash to search for.')

    # Set up search specifications
    search_specs = parser.add_argument_group(title='search specifications',
                                             description='Limit where to search for the pull request or commit. '
                                                         'Default searches all tags and branches.')
    search_specs.add_argument('-b', '--branch', action='append', help='Branch(es) to search specifically.')
    search_specs.add_argument('-t', '--tag', action='append', help='Release tag(s) to search specifically.')

    return parser.parse_args(args)


if __name__ == '__main__':
    main(sys.argv[1:])
