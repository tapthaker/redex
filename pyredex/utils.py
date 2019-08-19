# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import print_function

import errno
import glob
import shutil
import subprocess
import sys
import tempfile

from os.path import join
from os import getenv


temp_dirs = []


def abs_glob(directory, pattern='*'):
    """
    Returns all files that match the specified glob inside a directory.
    Returns absolute paths. Does not return files that start with '.'
    """
    for result in glob.glob(join(directory, pattern)):
        yield join(directory, result)


def make_temp_dir(name='', debug=False):
    """ Make a temporary directory which will be automatically deleted """
    global temp_dirs
    directory = tempfile.mkdtemp(name)
    if not debug:
        temp_dirs.append(directory)
    return directory


def remove_temp_dirs():
    global temp_dirs
    for directory in temp_dirs:
        shutil.rmtree(directory)


def sign_apk(keystore, keypass, keyalias, apk):
    try:
        java_home = getenv('JAVA_HOME')
        if java_home:
            jarsigner_binary = join(java_home, 'bin','jarsigner')
        else:
            jarsigner_binary = 'jarsigner'
        subprocess.check_call(
            [
                jarsigner_binary, '-sigalg', 'SHA1withRSA', '-digestalg', 'SHA1',
                '-keystore', keystore, '-storepass', keypass, apk, keyalias
            ],
            stdout=sys.stderr
        )
    except OSError as e:
        # Future migration note: In Python 3, this will throw a
        # FileNotFoundError instead. We could also use shutil.which().
        if e.errno == errno.ENOENT:
            FAIL_COLOR = '\033[91m'
            END_COLOR = '\033[0m'
            print(
                ('{}Failed to execute jarsigner: please check if jarsigner '
                 'is on your $PATH.{}').format(FAIL_COLOR, END_COLOR),
                file=sys.stderr,
            )
        raise


def remove_comments_from_line(l):
    (found_backslash, in_quote) = (False, False)
    for idx, c in enumerate(l):
        if c == "\\" and not found_backslash:
            found_backslash = True
        elif c == "\"" and not found_backslash:
            found_backslash = False
            in_quote = not in_quote
        elif c == "#" and not in_quote:
            return l[:idx]
        else:
            found_backslash = False
    return l


def remove_comments(lines):
    return "".join([remove_comments_from_line(l) + "\n" for l in lines])
