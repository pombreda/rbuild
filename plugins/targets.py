#
# Copyright (c) SAS Institute Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


'''
targets
'''
from rbuild import pluginapi
from rbuild.pluginapi import command


class ListTargetsCommand(command.ListCommand):
    help = 'list targets'
    resource = 'targets'
    fieldMap = (('Name', lambda t: t.name),
                ('Configred', lambda t: t.is_configured),
                ('Credentials', lambda t: t.credentials_valid),
                )


class Targets(pluginapi.Plugin):
    name = 'targets'

    def initialize(self):
        self.handle.Commands.getCommandClass('list').registerSubCommand(
            'targets', ListTargetsCommand)

    def list(self, *args, **kwargs):
        return self.handle.facade.rbuilder.getTargets()
