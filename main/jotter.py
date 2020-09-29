#! /usr/bin/env python
#
# MicroPython USMART Jotter. Not so much as a logger, rather just jotting a few notes to file.
#
# This file is part of micropython-usmart-gateway-application.
# https://github.com/bensherlock/micropython-usmart-gateway-application
#
#
# MIT License
#
# Copyright (c) 2020 Benjamin Sherlock <benjamin.sherlock@ncl.ac.uk>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""MicroPython USMART Jotter."""

import utime

_jotters = {}


class Jotter:
    """Jotter."""

    def __init__(self, name):
        self._name = name
        self._filename = "logs/" + name + ".log"

    def clear(self):
        """Clear the contents"""
        with open(self._filename, 'w') as f:
            # Open as overwrite
            pass

    def jot(self, msg, source_file="", line_no="", function_name=""):
        """Jot an entry. Use source_file==__name__ when you call this function."""
        # exc_info = sys.exc_info()
        bufsize = 1
        with open(self._filename, 'a', buffering=bufsize) as f:
            timestamp_str = "%d-%02d-%02d %02d:%02d:%02d" % utime.localtime()[:6]
            f.write(timestamp_str + " - ")
            if source_file:
                f.write(source_file + " - ")
            if line_no:
                f.write(line_no + " - ")
            if function_name:
                f.write(function_name + " - ")
            f.write(msg + "\n")

    def jot_exception(self, e):
        bufsize = 1
        with open(self._filename, 'a', buffering=bufsize) as f:
            import sys
            timestamp_str = "%d-%02d-%02d %02d:%02d:%02d" % utime.localtime()[:6]
            f.write(timestamp_str + " ")
            sys.print_exception(e, f)

    def print_all_from_jotter(self):
        """Read and print the whole file to stdout."""
        with open(self._filename, 'r') as f:
            line = f.readline()
            while line:
                l = line.rstrip("\n")
                print(l)
                line = f.readline()



def get_jotter(name="root"):
    global _jotters

    if name in _jotters:
        return _jotters[name]
    jotter = Jotter(name)
    _jotters[name] = jotter
    return jotter