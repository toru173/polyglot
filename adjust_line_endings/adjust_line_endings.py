#!/usr/bin/env python3
#
# Copyright (c) 2024-present toru173 and contributors
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted (subject to the limitations in the disclaimer
# below) provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of the copyright holder nor the names of the contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
# NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY
# THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# This is intended to adjust the line endings of a polyglot script file
# that can be run in either Windows using cmd.exe, or linux/macOS using bash.
# We can combine the two because a line starting with ':;' is treated as a single
# line by cmd.exe, but as two lines by bash. That means we can put in a second
# command specific to bash, such as a command that captures all of the
# contents of the script up to a delimiter keyword and redirecting it to
# /dev/null. This means we can have two versions of a script in the same file.
#
# An example script would be:
#
# : << END_WIN
# ECHO I'm being executed by cmd.exe!
# EXIT /B 0
# END_WIN
#
# echo "I'm being executed by bash!"
# exit 0
#
# However, in batch files labels may not work reliably when using LF only
# (https://www.dostips.com/forum/viewtopic.php?t=8988) and bash doesn't like CRLF
# (https://unix.stackexchange.com/questions/577663/handling-bash-script-with-crlf-carriage-return-in-linux-as-in-msys2)
# So we have to go through and insert the correct line endings in each section.
# It's also critical that Git doesn't try to normallise the line endings of
# any polyglot script, so the script name needs to be added to .gitattributes
# to disable line ending normalisation:
#
# script_name -text

import argparse
import os
import glob
import fnmatch

def adjust_line_endings(polyglot_file, delimiter):
    try:
        # Check if file exists
        if not os.path.exists(polyglot_file):
            raise FileNotFoundError(f"File '{polyglot_file}' does not exist.")

        # Check if file is readable and writable
        if not os.access(polyglot_file, os.R_OK):
            raise PermissionError(f"Cannot read file '{polyglot_file}'. Permission denied.")
        if not os.access(polyglot_file, os.W_OK):
            raise PermissionError(f"Cannot write to file '{polyglot_file}'. Permission denied.")

        # Read the file content
        with open(polyglot_file, 'r', newline = '') as file:
            lines = file.readlines()

        # Write back to the same file, with appropriate line endings
        with open(polyglot_file, 'w', newline = '') as file:
            for line in lines:
                # We are expecting our polyglot script to start with the
                # batch section for cmd.exe, then the bash section after
                # the delimiter
                if delimiter in line:
                    # Check for the initial delimiter defining the heredoc.
                    # The heredoc is sensitive to line endings. Use CRLF as the
                    # CR ('\r') will be interpreted as part of the heredoc delimiter
                    file.write(line.replace('\n', '\r\n').replace('\r\r\n', '\r\n'))
                    if line.startswith(delimiter):
                        # Once the end of the heredoc is found, switch to LF
                        # Write out the remaining lines in the file with LF only
                        file.writelines([l.replace('\r\n', '\n').replace('\r', '\n') for l in lines[lines.index(line) + 1: ]])
                        break
                else:
                    # Ensure CRLF before the delimiter
                    file.write(line.replace('\n', '\r\n').replace('\r\r\n', '\r\n'))

        print(f"Line endings adjusted succesfully in '{polyglot_file}'")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except PermissionError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def get_files_from_gitattributes():
    files_from_gitattributes = set()
    if not os.path.exists('.gitattributes'):
        print("No .gitattributes file found.")
        return list(files_from_gitattributes)

    with open('.gitattributes', 'r') as f:
        lines = f.readlines()

    patterns = []
    # Process each line in .gitattributes
    for line in lines:
        line = line.strip()
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
        tokens = line.split()
        # Skip invalid lines
        if len(tokens) < 2:
            continue
        pattern = tokens[0]
        attrs = tokens[1:]

        # Check if '-text' is among the attributes
        for attr in attrs:
            if attr == '-text':
                patterns.append(pattern)
                break

    # For each pattern with -text attribute, find matching files
    for pattern in patterns:
        # Handle negation patterns starting with '!'
        # Here we just skip them
        if pattern.startswith('!'):
            continue

        glob_pattern = pattern.replace('/', os.sep)
        # Handle recursive patterns
        if '**' in glob_pattern:
            files = glob.glob(glob_pattern, recursive=True)
        else:
            # For non-recursive patterns, match files in current directory and subdirectories
            for root, dirs, files in os.walk('.'):
                # Build the relative path of the directory
                rel_dir = os.path.relpath(root, '.')

                for filename in files:
                    # Skip files with os.sep or '..' in the filename
                    # This should prevent directory traversals
                    if os.sep in filename or '..' in filename:
                        print(f"Skipping file with unsafe name: {filename}")
                        continue

                    # Build the relative path to the file
                    if rel_dir == '.':
                        relpath = filename
                    else:
                        relpath = os.path.join(rel_dir, filename)
                    # Use fnmatch to match the pattern
                    if fnmatch.fnmatch(relpath, glob_pattern):
                        files_from_gitattributes.add(relpath)

    return list(files_from_gitattributes)


def do_pre_commit(delimiter):
    files_to_normalise = get_files_from_gitattributes()
    if not files_to_normalise:
        print("No files with '-text' attribute found.")
        return

    for polyglot_file in files_to_normalise:
        adjust_line_endings(polyglot_file, delimiter)


# Setting up argument parsing
def main():
    parser = argparse.ArgumentParser(description="Ensure CRLF before a delimiter and LF after in a polyglot (batch/bash) script")
    parser.add_argument('--pre-commit', action='store_true',
                        help='Run in pre-commit mode, processing all files marked with -text attribute in .gitattributes.')
    parser.add_argument('polyglot_file', nargs='?', default=None,
                        help="Path to the polyglot script that requires adjusted line endings")
    parser.add_argument('delimiter', nargs='?', default='END_WIN',
                        help="Delimiter that separates the batch portion of a script from the bash portion (default: END_WIN)")

    args = parser.parse_args()

    if args.pre_commit:
        # Run in pre-commit mode
        do_pre_commit(args.delimiter)
    else:
        if args.polyglot_file is None:
            parser.error('polyglot_file is required unless --pre-commit is specified.')
        adjust_line_endings(args.polyglot_file, args.delimiter)

if __name__ == "__main__":
    main()
