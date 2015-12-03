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
__copyright__ = "Copyright © 2013-2014-2015 Sébastien GALLET aka bibi21000"
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
import logging
import json as mjson
import shutil
import mock

from janitoo_nosetests.server import JNTTServer

from janitoo.mqtt import MQTTClient
from janitoo.dhcp import JNTNetwork, HeartbeatMessage
from janitoo.utils import json_dumps, json_loads
from janitoo.utils import HADD_SEP, HADD
from janitoo.utils import TOPIC_HEARTBEAT
from janitoo.utils import TOPIC_NODES, TOPIC_NODES_REPLY, TOPIC_NODES_REQUEST
from janitoo.utils import TOPIC_BROADCAST_REPLY, TOPIC_BROADCAST_REQUEST
from janitoo.utils import TOPIC_VALUES_USER, TOPIC_VALUES_CONFIG, TOPIC_VALUES_SYSTEM, TOPIC_VALUES_BASIC
from janitoo.runner import jnt_parse_args

class JNTTCertification(JNTTServer):
    """Certification base test
    """
    ip = '127.0.0.1'
    hadds = ['1111/0000']
    client_hadd = "9999/0000"
    conf = {'broker_ip': '127.0.0.1', 'broker_port': '1883'}
    
    def setUp(self):
        JNTTServer.setUp(self)
        self.startClient(self.conf)

    def tearDown(self):
        self.stopClient()
        JNTTServer.tearDown(self)

class JNTTCertificationCommon():
    """Common tests for certification
    """

    def test_001_heartbeat_hadds(self):
        self.skipNoPingTest(self.ip)
        for hadd in self.hadds:
            self.assertHeartbeatNode(hadd=hadd)

    def test_005_heartbeat_delay_hadds(self):
        self.skipNoPingTest(self.ip)
        for hadd in self.hadds:
            self.assertHeartbeatNode(hadd=hadd)
            wait = 15
            self.assertUpdateValue(type="system", cmd_class=0x70, uuid='heartbeat', data=wait, genre=0x04, is_writeonly=True, node_hadd=hadd, client_hadd=self.client_hadd)
            self.assertHeartbeatNode(hadd=hadd, timeout=wait+2)
            wait = 60
            self.assertUpdateValue(type="system", cmd_class=0x70, uuid='heartbeat', data=wait, genre=0x04, is_writeonly=True, node_hadd=hadd, client_hadd=self.client_hadd)
            self.assertHeartbeatNode(hadd=hadd, timeout=wait+3)

    def test_051_config_timeout(self):
        self.skipNoPingTest(self.ip)
        for hadd in self.hadds:
            self.assertHeartbeatNode(hadd=hadd)
            wait = 15
            self.assertUpdateValue(type="system", cmd_class=0x70, uuid='config_timeout', data=wait, genre=0x04, is_writeonly=True, node_hadd=hadd, client_hadd=self.client_hadd)
            wait = 5
            self.assertUpdateValue(type="system", cmd_class=0x70, uuid='config_timeout', data=wait, genre=0x04, is_writeonly=True, node_hadd=hadd, client_hadd=self.client_hadd)

    def test_061_name(self):
        self.skipNoPingTest(self.ip)
        for hadd in self.hadds:
            self.assertHeartbeatNode(hadd=hadd)
            self.assertUpdateValue(type="config", cmd_class=0x70, uuid='name', data='testname', genre=0x03, is_writeonly=True, node_hadd=hadd, client_hadd=self.client_hadd)

    def test_071_location(self):
        self.skipNoPingTest(self.ip)
        for hadd in self.hadds:
            self.assertHeartbeatNode(hadd=hadd)
            self.assertUpdateValue(type="config", cmd_class=0x70, uuid='location', data='testlocation', genre=0x03, is_writeonly=True, node_hadd=hadd, client_hadd=self.client_hadd)
