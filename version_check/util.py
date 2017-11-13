# -*- coding: utf-8 -*-
'''
Miscellaneous utility functions
'''

# Import Python libs
import subprocess


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
