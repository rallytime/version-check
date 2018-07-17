# -*- coding: utf-8 -*-
'''
Core program functionality.
'''

# Import version_check libs
import config
import util


def search(pr_num=None,
           commit=None,
           fetch=False,
           branch_limiters=None,
           tag_limiters=None):
    '''
    Searches for matching branches and tags based on the given PR or commit
    hash. Either a PR or commit must be provided.

    pr_num
        The pull request number to search for.

    commit
        The commit to search for.

    fetch
        Specify whether or not to perform a ``git fetch`` from upstream.
        Defaults to ``False``.

    branch_limiters
        The branch or branches to search specifically. Should be passed as
        a list. Defaults to None, which searches all branches.

    tag_limiters
        The tag or tags to search specifically. Should be passed as a list.
        Defaults to None, which searches all branches.
    '''
    ret = {}

    # Fetch latest from GitHub
    if fetch:
        util.cmd_run(['git', config.GIT_DIR, 'fetch', config.REMOTE])

    # Get commit sha from PR number
    if pr_num:
        commit = get_sha(pr_num)

    # Return if an error occurred in get_sha call
    if isinstance(commit, dict):
        return commit

    # Get matching branches and tags based on limiters (if any)
    if branch_limiters:
        # Branch limiter is passed
        ret['branches'] = get_branch_matches(commit, limiters=branch_limiters)
        if tag_limiters:
            # Tag limiter is passed with a branch limiter
            ret['tags'] = get_tag_matches(commit, limiters=tag_limiters)
    elif tag_limiters:
        # Only a tag limiter is passed
        ret['tags'] = get_tag_matches(commit, limiters=tag_limiters)
    else:
        # Search all branches and tags
        ret['branches'] = get_branch_matches(commit)
        ret['tags'] = get_tag_matches(commit)

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
    cmd_ret = util.cmd_run(['git', config.GIT_DIR, 'branch', '-a', '--contains', commit])
    cmd_ret = cmd_ret['stdout'].decode()
    strip_len = len('/'.join(['remotes', config.REMOTE])) + 1
    for line in cmd_ret.splitlines():
        line = line.strip()
        if line.startswith('remotes/'):
            # strip off remotes/REMOTE/
            line = line[strip_len:]
            # handle other possible remotes - don't include them
            if '/' in line:
                continue
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
    cmd_ret = util.cmd_run(['git', config.GIT_DIR, 'tag', '--contains', commit])
    cmd_ret = cmd_ret['stdout'].decode()
    for line in cmd_ret.splitlines():
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
    branch_cmd = util.cmd_run(
        ['git',
         config.GIT_DIR,
         'fetch',
         config.REMOTE,
         'pull/{0}/head:{1}'.format(pr_num, branch_name)])
    if branch_cmd['retcode'] != 0:
        return {'error': 'ERROR: {0}'.format(branch_cmd['stdout'])}

    # Get the commit at the HEAD of the local branch
    cmd_ret = util.cmd_run(['git', config.GIT_DIR, 'rev-parse', branch_name])
    sha = cmd_ret['stdout'].strip()

    # Clean up the newly created branch
    util.cmd_run(['git', config.GIT_DIR, 'branch', '-D', branch_name])

    return sha
