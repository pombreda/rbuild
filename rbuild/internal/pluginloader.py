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

from rmake.lib import pluginlib

PLUGIN_PREFIX = 'rbuild_plugins'

class PluginManager(pluginlib.PluginManager):
    def initializeCommands(self, main):
        for plugin in self.plugins:
            plugin.initializeCommands(self, main)

def getPlugins(argv, pluginDirs, disabledPlugins=None):
    # TODO: look for plugin-related options in argv, perhaps with our
    # own lenient parser.
    # until then, ignore unused argv argument
    # pylint: disable-msg=W0613
    pluginMgr = PluginManager(pluginDirs, disabledPlugins,
                              pluginPrefix=PLUGIN_PREFIX)
    pluginMgr.loadPlugins()
    return pluginMgr
