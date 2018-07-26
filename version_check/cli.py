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

# Import version_check libs
import version_check.config as config
import version_check.core as core


def main():
    '''
    Run!

    Prints results to the screen.
    '''
    # Parse args and define some basic params
    args = parse_args()
    commit = args.commit
    pr_num = args.pull_request

    ret = core.search(
        pr_num=pr_num,
        commit=commit,
        fetch=not args.skip_fetch,
        branch_limiters=args.branch,
        tag_limiters=args.tag
    )
    if ret.get('error'):
        print(ret.get('error'))
        return

    branches = ret.get('branches')
    tags = ret.get('tags')

    found = False
    if branches:
        found = True
        print('Branches:')
        for branch in branches:
            print('  ' + branch)
    if tags:
        found = True
        print('Tags:')
        for tag in tags:
            print('  ' + tag)
    if found is False:
        comment = 'The {0} \'{1}\' was not found.'.format('pull request' if pr_num else 'commit',
                                                          pr_num if pr_num else commit)
        print(comment)


def parse_args():
    '''
    Parse the CLI options.
    '''
    # Define parser and set up basic options
    parser = argparse.ArgumentParser(description='Search for pull requests or commits in Salt')
    parser.add_argument('-v', '--version', action='version', version=config.VERSION, help='Print version and exit.')
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

    return parser.parse_args()


if __name__ == '__main__':
    main()
