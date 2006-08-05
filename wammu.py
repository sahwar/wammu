#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Wammu - Phone manager
Execution script
'''
__author__ = 'Michal Čihař'
__email__ = 'michal@cihar.com'
__license__ = '''
Copyright (c) 2003 - 2006 Michal Čihař

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License version 2 as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
'''

import os
import gettext
import sys
import getopt
import Wammu

gettext.install('wammu', unicode=1)

def version():
    print _('Wammu - Windowed Gammu version %s') % Wammu.__version__

def usage():
    version()
    print _('Usage: wammu [OPTION...]')
    print
    print _('Options:')
    print _('-h/--help          ... show this help')
    print _('-v/--version       ... show program version')
    print _('-l/--local-locales ... use locales from current directory rather than system ones')
    print

try:
    opts, args = getopt.getopt(sys.argv[1:], 'hvl', ['help', 'version', 'local-locales'])
except getopt.GetoptError, val:
    usage()
    print _('Command line parsing failed with error:')
    print val
    sys.exit(2)

if len(args) != 0:
    usage()
    print _('Extra unrecognized parameters passed to program')
    sys.exit(3)

for o, a in opts:
    if o in ('-l', '--local-locales'):
        gettext.install('wammu','./locale/', unicode=1)
    if o in ('-h', '--help'):
        usage()
        sys.exit()
    if o in ('-v', '--version'):
        version()
        sys.exit()

# need to be imported after locales are initialised
import Wammu.App
Wammu.App.Run()
