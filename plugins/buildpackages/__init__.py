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
from rbuild.pluginapi import command

from rbuild_plugins.buildpackages import packages

class BuildPackagesCommand(command.BaseCommand):
    docs = {'no-watch' : 'do not watch the job after starting the build',
            'no-commit' : 'do not automatically commit successful builds',}

    def addParameters(self, argDef):
        argDef['no-watch'] = command.NO_PARAM
        argDef['no-commit'] = command.NO_PARAM

    #pylint: disable-msg=R0201,R0903
    # could be a function, and too few public methods
    def runCommand(self, handle, argSet, args):
        watch = not argSet.pop('no-watch', False)
        commit = not argSet.pop('no-commit', False)
        _, packageList, = self.requireParameters(args, allowExtra=True)
        if not packageList:
            jobId = handle.BuildPackages.buildAllPackages()
        else:
            jobId = handle.BuildPackages.buildPackages(packageList)
        if watch and commit:
            handle.BuildPackages.watchAndCommitJob(jobId)
        elif watch:
            handle.BuildPackages.watchJob(jobId)


class BuildPackages(pluginapi.Plugin):

    def initialize(self):
        self.handle.Commands.getCommandClass('build').registerSubCommand(
                                    'packages', BuildPackagesCommand)

    def buildAllPackages(self):
        job = self.createJobForAllPackages()
        return self.handle.facade.rmake.buildJob(job)

    def buildPackages(self, packageList):
        job = self.createJobForPackages(packageList)
        return self.handle.facade.rmake.buildJob(job)

    def createJobForAllPackages(self):
        return packages.createRmakeJobForAllPackages(self.handle)

    def createJobForPackages(self, packageList):
        return packages.createRmakeJobForPackages(self.handle, packageList)

    def watchAndCommitJob(self, jobId):
        return self.handle.facade.rmake.watchAndCommitJob(jobId)

    def watchJob(self, jobId):
        return self.handle.facade.rmake.watchJob(jobId)