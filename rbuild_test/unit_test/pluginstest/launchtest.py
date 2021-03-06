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

from rbuild import errors
from smartform import descriptor
from testutils import mock

from rbuild_test import rbuildhelp


DESCRIPTOR_XML = '''\
<descriptor xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.rpath.com/permanent/descriptor-1.1.xsd" xsi:schemaLocation="http://www.rpath.com/permanent/descriptor-1.1.xsd descriptor-1.1.xsd" version="1.1">
    <metadata>
        <displayName>VMware Image Upload Parameters</displayName>
        <rootElement>descriptor_data</rootElement>
        <descriptions>
            <desc>VMware Image Upload Parameters</desc>
        </descriptions>
    </metadata>
    <dataFields>
        <field>
            <name>name</name>
            <descriptions>
                <desc>Name</desc>
            </descriptions>
            <type>str</type>
            <constraints>
                <length>4</length>
            </constraints>
            <required>true</required>
            <hidden>false</hidden>
        </field>
    </dataFields>
</descriptor>
'''

DDATA_XML = '''\
<?xml version='1.0' encoding='UTF-8'?>
<descriptor_data>
    <tag>foo</tag>
</descriptor_data>
'''

JOB_XML = '''\
<?xml version='1.0' encoding='UTF-8'?>
<job>
  <descriptor>descriptor</descriptor>
  <descriptor_data>
    <tag>foo</tag>
  </descriptor_data>
  <job_type>job_type</job_type>
</job>
'''


class LaunchTest(rbuildhelp.RbuildHelper):
    def testLaunchArgParse(self):
        self.getRbuildHandle()
        self.checkRbuild(
            'launch --list --from-file=fromFile --to-file=toFile --no-launch'
                ' --no-watch Image Target',
            'rbuild_plugins.launch.LaunchCommand.runCommand',
            [None, None, {
                'list': True,
                'from-file': 'fromFile',
                'to-file': 'toFile',
                'no-watch': True,
                'no-launch': True,

                }, ['rbuild', 'launch', 'Image', 'Target']])
        self.checkRbuild(
            'deploy --list --from-file=fromFile --to-file=toFile --no-launch'
                ' --no-watch Image Target',
            'rbuild_plugins.launch.LaunchCommand.runCommand',
            [None, None, {
                'list': True,
                'from-file': 'fromFile',
                'to-file': 'toFile',
                'no-watch': True,
                'no-launch': True,
                }, ['rbuild', 'deploy', 'Image', 'Target']])

    def testLaunchCmdlineList(self):
        handle = self.getRbuildHandle(mock.MockObject())
        handle.Launch.registerCommands()
        handle.Launch.initialize()
        handle.ui = mock.MockObject()

        _target_1 = mock.MockObject()
        _target_1._mock.set(name='foo')

        _target_2 = mock.MockObject()
        _target_2._mock.set(name='bar')

        _targets = [_target_1, _target_2]
        mock.mockMethod(handle.facade.rbuilder.getEnabledTargets, _targets)

        cmd = handle.Commands.getCommandClass('launch')()
        cmd.runCommand(handle, {'list': True}, ['rbuild', 'launch'])

        handle.ui.write._mock.assertCalled('Available targets: foo, bar')

    def testLaunchCmdlineNoArgs(self):
        handle = self.getRbuildHandle(mock.MockObject())
        handle.Launch.registerCommands()
        handle.Launch.initialize()

        cmd = handle.Commands.getCommandClass('launch')()

        self.assertRaises(
            errors.ParseError,
            cmd.runCommand,
            handle,
            {},
            ['rbuild', 'launch'],
            )
        self.assertRaises(
            errors.ParseError,
            cmd.runCommand,
            handle,
            {},
            ['rbuild', 'launch', 'foo'],
            )

    def testLaunchCmdline(self):
        handle = self.getRbuildHandle(mock.MockObject())
        handle.Launch.registerCommands()
        handle.Launch.initialize()
        mock.mockMethod(handle.Launch.deployImage)
        mock.mockMethod(handle.Launch.launchImage)
        mock.mockMethod(handle.Launch.watchJob)

        cmd = handle.Commands.getCommandClass('launch')()
        cmd.runCommand(handle, {}, ['rbuild', 'launch', 'foo', 'bar'])
        handle.Launch.deployImage._mock.assertNotCalled()
        handle.Launch.launchImage._mock.assertCalled('foo', 'bar', True)

        cmd = handle.Commands.getCommandClass('launch')()
        cmd.runCommand(
            handle, {}, ['rbuild', 'deploy', 'foo', 'bar'])
        handle.Launch.deployImage._mock.assertCalled('foo', 'bar', True)
        handle.Launch.launchImage._mock.assertNotCalled()

    def testGetAction(self):
        handle = self.getRbuildHandle(mock.MockObject())
        handle.Launch.registerCommands()
        handle.Launch.initialize()

        self.assertRaises(
            AssertionError, handle.Launch._getAction, None, None, 'foo')

        _action1 = mock.MockObject()
        _action1._mock.set(key=handle.Launch.DEPLOY)
        _action1._mock.set(name="Deploy image on 'foo' (vmware)")
        _action2 = mock.MockObject()
        _action2._mock.set(key=handle.Launch.DEPLOY)
        _action2._mock.set(name="Deploy image on 'bar' (vmware)")

        _image = mock.MockObject()
        _image._mock.set(actions=[_action1, _action2])

        self.assertRaises(
            errors.PluginError,
            handle.Launch._getAction,
            _image,
            'baz',
            handle.Launch.DEPLOY,
            )

        rv = handle.Launch._getAction([_image], 'foo', handle.Launch.DEPLOY)
        self.assertEqual(rv, (_image, _action1))

        rv = handle.Launch._getAction([_image], 'bar', handle.Launch.DEPLOY)
        self.assertEqual(rv, (_image, _action2))

    def testCreateJob(self):
        handle = self.getRbuildHandle(mock.MockObject())
        handle.Launch.registerCommands()
        handle.Launch.initialize()

        _jobs = []

        def _append(x):
            _jobs.append(x)
            return x

        _image = mock.MockObject()
        _image._mock.set(jobs=mock.MockObject())
        _image.jobs._mock.set(append=_append)
        mock.mockMethod(handle.facade.rbuilder.getImages, _image)

        _action = mock.MockObject()
        _action._mock.set(descriptor=DESCRIPTOR_XML)
        _action._root._mock.set(job_type='job_type')
        _action._root._mock.set(descriptor='descriptor')
        mock.mockMethod(handle.Launch._getAction, (_image, _action))

        _ddata = mock.MockObject()
        _ddata.toxml._mock.setDefaultReturn(DDATA_XML)
        mock.mockMethod(handle.DescriptorConfig.createDescriptorData, _ddata)

        mock.mockMethod(
            handle.Launch._getProductStage, ('product', 'branch', 'stage'))
        rv = handle.Launch._createJob(
            handle.Launch.DEPLOY, 'foo', 'bar', True)
        handle.facade.rbuilder.getImages._mock.assertCalled(
            'foo',
            project='product',
            branch='branch',
            stage='stage',
            trailingVersion='',
            )
        handle.Launch._getAction._mock.assertCalled(
            _image, 'bar', handle.Launch.DEPLOY)

        self.assertEqual(len(_jobs), 1)
        self.assertEqual(rv, _jobs[0])
        self.assertEqual(rv.toxml(), JOB_XML)

        rv = handle.Launch._createJob(
            handle.Launch.DEPLOY, 'foo=', 'bar', True)
        handle.facade.rbuilder.getImages._mock.assertCalled(
            'foo',
            project='product',
            branch='branch',
            stage='stage',
            trailingVersion='',
            )
        handle.Launch._getAction._mock.assertCalled(
            _image, 'bar', handle.Launch.DEPLOY)

        self.assertEqual(len(_jobs), 2)
        self.assertEqual(rv, _jobs[1])
        self.assertEqual(rv.toxml(), JOB_XML)

        rv = handle.Launch._createJob(
            handle.Launch.DEPLOY, 'foo=1', 'bar', True)
        handle.facade.rbuilder.getImages._mock.assertCalled(
            'foo',
            project='product',
            branch='branch',
            stage='stage',
            trailingVersion='1',
            )
        handle.Launch._getAction._mock.assertCalled(
            _image, 'bar', handle.Launch.DEPLOY)

        self.assertEqual(len(_jobs), 3)
        self.assertEqual(rv, _jobs[2])
        self.assertEqual(rv.toxml(), JOB_XML)

    def testWatchJob(self):
        from rbuild_plugins.launch import time
        handle = self.getRbuildHandle(mock.MockObject())
        handle.Launch.registerCommands()
        handle.Launch.initialize()

        mock.mock(handle.ui, 'outStream')

        mock.mock(time, 'ctime', '')
        mock.mock(time, 'sleep')

        _job = mock.MockObject()
        _job.job_state._mock.set(name='Failed')
        _job.job_type._mock.set(name='launch system on taraget')

        self.assertRaises(errors.PluginError, handle.Launch.watchJob, _job)

        _status_text = ['Text4', 'Text3 ', 'Text2  ', 'Text1   ']
        _network1 = mock.MockObject()
        _network1._mock.set(dns_name='foo')
        _network2 = mock.MockObject()
        _network2._mock.set(dns_name='bar')
        _resource = mock.MockObject()
        _resource._mock.set(name='baz')
        _resource._mock.set(networks=[_network1, _network2])

        def _refresh():
            try:
                _job._mock.set(status_text=_status_text.pop())
            except IndexError:
                _job.job_state._mock.set(name='Completed')
                _job._mock.set(created_resources=[_resource])

        _job._mock.set(refresh=_refresh)
        _job.job_state._mock.set(name='Running')
        _job._mock.set(status_text='Text0    ')

        handle.ui.outStream.isatty._mock.setDefaultReturn(True)
        handle.Launch.watchJob(_job)
        expected_calls = [
            (('\r[] Text0    ',), ()),
            (('\r[] Text1   ',), ()),
            (('  \b\b',), ()),
            (('\r[] Text2  ',), ()),
            (('  \b\b',), ()),
            (('\r[] Text3 ',), ()),
            (('  \b\b',), ()),
            (('\r[] Text4',), ()),
            (('  \b\b',), ()),
            (('\n',), ()),
            (('Created system baz with addresses: foo, bar\n',), ()),
            ]
        self.assertEqual(handle.ui.outStream.write._mock.calls, expected_calls)

        _status_text = ['Text4', 'Text3 ', 'Text2  ', 'Text1   ']
        _job.job_state._mock.set(name='Running')
        _job._mock.set(status_text='Text0    ')
        handle.ui.outStream.write._mock.calls = []
        handle.ui.outStream.isatty._mock.setDefaultReturn(False)
        handle.Launch.watchJob(_job)
        expected_calls = [
            (('[] Text0    \n',), ()),
            (('[] Text1   \n',), ()),
            (('[] Text2  \n',), ()),
            (('[] Text3 \n',), ()),
            (('[] Text4\n',), ()),
            (('Created system baz with addresses: foo, bar\n',), ()),
            ]
        self.assertEqual(handle.ui.outStream.write._mock.calls, expected_calls)
