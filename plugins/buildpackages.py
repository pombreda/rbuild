#
# Copyright (c) 2008 rPath, Inc.
#
# This program is distributed under the terms of the Common Public License,
# version 1.0. A copy of this license should have been distributed with this
# source file in a file called LICENSE. If it is not present, the license
# is always available at http://www.rpath.com/permanent/licenses/CPL-1.0.
#
# This program is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the Common Public License for
# full details.
#

from rbuild import pluginapi

class BuildPackages(object):
    #pylint: disable-msg=R0201,W0613,R0903
    # could be a function, unused variables, and too few public methods
    def runCommand(self, handle, argSet, args):
        print 'Building packages: %s' % ', '.join(args[1:])

class BuildPackagesPlugin(pluginapi.Plugin):

    def initialize(self):
        self.handle.Commands.getCommandClass('build').registerSubCommand(
                                                    'packages', BuildPackages)

