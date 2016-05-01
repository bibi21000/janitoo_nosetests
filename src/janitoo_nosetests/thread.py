# -*- coding: utf-8 -*-
__license__ = """

This file is part of **janitoo** project https://github.com/bibi21000/janitoo.

License : GPL(v3)

**janitoo** is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

**janitoo** is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with janitoo. If not, see http://www.gnu.org/licenses.
"""
__copyright__ = "Copyright © 2013-2014-2015-2016 Sébastien GALLET aka bibi21000"
__author__ = 'Sébastien GALLET aka bibi21000'
__email__ = 'bibi21000@gmail.com'

try:
    __import__('pkg_resources').declare_namespace(__name__)
except:  # pragma: no cover
    # bootstrapping
    pass # pragma: no cover

import sys, os, errno
import time
import unittest
import threading
import json as mjson
import shutil
import mock
from pkg_resources import iter_entry_points
import logging
from logging.config import fileConfig as logging_fileConfig

from janitoo_nosetests import JNTTBase

from janitoo.mqtt import MQTTClient
from janitoo.dhcp import JNTNetwork, HeartbeatMessage
from janitoo.utils import json_dumps, json_loads
from janitoo.utils import HADD_SEP, HADD
from janitoo.utils import TOPIC_HEARTBEAT
from janitoo.utils import TOPIC_NODES, TOPIC_NODES_REPLY, TOPIC_NODES_REQUEST
from janitoo.utils import TOPIC_BROADCAST_REPLY, TOPIC_BROADCAST_REQUEST
from janitoo.utils import TOPIC_VALUES_USER, TOPIC_VALUES_CONFIG, TOPIC_VALUES_SYSTEM, TOPIC_VALUES_BASIC
from janitoo.runner import jnt_parse_args
from janitoo.options import JNTOptions, string_to_bool

class JNTTThread(JNTTBase):
    """Thread base test
    """

    thread_name = None

    def setUp(self):
        JNTTBase.setUp(self)
        self.factory = {}
        try:
            for entry in iter_entry_points(group='janitoo.threads'):
                print "Load entry name %s" % entry.name
                try:
                    self.factory[entry.name] = entry.load()
                except:
                    pass
        except:
            pass
        print "Thread %s" % self.thread_name
        self.thread = None

    def tearDown(self):
        self.factory = None
        JNTTBase.tearDown(self)

    def assertThreadEntryPoint(self, entry):
        mkth = None
        for entry in iter_entry_points(group='janitoo.threads', name=entry):
            mkth = entry.load()
        self.assertNotEqual(mkth, None)

class JNTTThreadRun(JNTTThread):
    """Thread base test
    """

    conf_file = None
    prog = "test"
    timeout = 120

    def setUp(self):
        JNTTThread.setUp(self)
        logging_fileConfig(self.conf_file)
        with mock.patch('sys.argv', [self.prog, 'start', '--conf_file=%s'%self.getDataFile(self.conf_file)]):
            options = vars(jnt_parse_args())
        self.options = JNTOptions(options)
        self.thread = self.factory[self.thread_name](options)

    def tearDown(self):
        if self.thread is not None:
            time.sleep(5)
            try:
                self.thread.stop()
            except:
                pass
        self.options = None
        JNTTThread.tearDown(self)

    def wait_for_nodeman(self):
        """Wait for the nodemanager to be ready"""
        if not self.thread.is_alive():
            self.thread.start()
        i = 0
        while i< self.timeout and not self.thread.nodeman.is_started:
            time.sleep(1)
            i += 1
            print self.thread.nodeman.state

    def assertNodeOnBus(self, node_uuid):
        """Assert a node is on the bus"""
        print 'Look for node %s' % node_uuid
        self.assertNotEqual(None, self.thread.bus.nodeman.find_node(node_uuid))

    def assertValueOnBus(self, node_uuid, value_uuid):
        """Assert a value is on the bus"""
        self.assertNodeOnBus(node_uuid)
        print 'Look for value %s' % value_uuid
        self.assertNotEqual(None, self.thread.bus.nodeman.find_value(node_uuid,value_uuid))

class JNTTThreadCommon():
    """Common tests for components
    """

    def test_001_thread_entry_point(self):
        self.assertFalse(self.thread_name is None)
        self.assertThreadEntryPoint(self.thread_name)

class JNTTThreadRunCommon(JNTTThreadCommon):
    """Common tests for components
    """

    def test_011_thread_start_wait_stop(self):
        #~ self.skipTest("Freeze on docker, travis and circle")
        try:
            self.thread.start()
            time.sleep(10)
        finally:
            self.thread.stop()

    def test_031_cron_hourly(self):
        #~ self.skipTest("Freeze on docker, travis and circle")
        cron = string_to_bool(self.options.get_option(self.thread_name, 'hourly_timer', default = False))
        if cron:
            self.wait_for_nodeman()
            try:
                time.sleep(2)
                self.assertNotEqual(self.thread.nodeman.hourly_timer, None)
                self.thread.nodeman.stop_hourly_timer()
                self.assertEqual(self.thread.nodeman.hourly_timer, None)
                self.thread.nodeman.start_hourly_timer()
                self.assertNotEqual(self.thread.nodeman.hourly_timer, None)
                self.thread.nodeman.do_hourly_timer()
                time.sleep(5)
            finally:
                self.thread.stop()
        else:
            self.skipTest("Hourly timer not used for this thread")
