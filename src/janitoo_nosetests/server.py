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
__copyright__ = "Copyright © 2013-2014 Sébastien GALLET aka bibi21000"
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
from pkg_resources import iter_entry_points
from nose.plugins.skip import SkipTest
from janitoo.mqtt import MQTTClient
from janitoo.dhcp import JNTNetwork, HeartbeatMessage
from janitoo.utils import json_dumps, json_loads
from janitoo.utils import HADD_SEP, HADD
from janitoo.utils import TOPIC_HEARTBEAT
from janitoo.utils import TOPIC_NODES, TOPIC_NODES_REPLY, TOPIC_NODES_REQUEST
from janitoo.utils import TOPIC_BROADCAST_REPLY, TOPIC_BROADCAST_REQUEST
from janitoo.utils import TOPIC_VALUES_USER, TOPIC_VALUES_CONFIG, TOPIC_VALUES_SYSTEM, TOPIC_VALUES_BASIC
from janitoo.runner import jnt_parse_args
from janitoo_nosetests import JNTTBase

class JNTTServer(JNTTBase):
    """Server base test
    """
    server_class = None
    server_conf = ""

    def setUp(self):
        JNTTBase.setUp(self)
        self.mqttc = None
        self.message = None
        self.message_received = False
        self.hearbeat_mqttc = None
        self.heartbeat_message = None
        self.heartbeat_waiting = None
        self.heartbeat_received = False
        self.server = None
        self.add_ctrl = None

    def tearDown(self):
        self.stopClient()
        self.mqttc = None
        self.mqtthearbeat = None
        self.stopClient()
        self.stopServer()
        self.mqttc = None
        self.message = None
        self.message_received = False
        self.hearbeat_mqttc = None
        self.heartbeat_message = None
        self.heartbeat_waiting = None
        self.heartbeat_received = False
        self.server = None
        JNTTBase.tearDown(self)

    def startClient(self):
        if self.mqttc is None:
            self.mqttc = MQTTClient(options=self.server.options.data)
            self.mqttc.connect()
            self.mqttc.start()
        if self.hearbeat_mqttc is None:
            self.hearbeat_mqttc = MQTTClient(options=self.server.options.data)
            self.hearbeat_mqttc.connect()
            self.hearbeat_mqttc.start()
            self.hearbeat_mqttc.subscribe(topic=TOPIC_HEARTBEAT, callback=self.mqtt_on_heartbeat_message)

    def stopClient(self):
        if self.mqttc != None:
            self.mqttc.stop()
            if self.mqttc.is_alive():
                self.mqttc.join()
            self.mqttc = None
        if self.hearbeat_mqttc != None:
            self.hearbeat_mqttc.unsubscribe(topic=TOPIC_HEARTBEAT)
            self.hearbeat_mqttc.stop()
            if self.hearbeat_mqttc.is_alive():
                self.hearbeat_mqttc.join()
            self.hearbeat_mqttc = None

    def startServer(self):
        self.server = None
        with mock.patch('sys.argv', ['%s'%self.server_class, 'start', '--conf_file=%s' % self.server_conf]):
            options = vars(jnt_parse_args())
            self.server = self.server_class(options)
        self.server.start()
        time.sleep(1.5)
        self.message = None

    def stopServer(self):
        if self.server is not None:
            self.server.stop()
            time.sleep(2.5)
        self.server = None
        self.message = None

    def start(self):
        self.startServer()
        self.startClient()

    def stop(self):
        self.stopClient()
        self.stopServer()

    def mqtt_on_heartbeat_message(self, client, userdata, message):
        """On generic message
        """
        self.heartbeat_message = message
        hb = HeartbeatMessage(self.heartbeat_message)
        hbadd_ctrl, hbadd_node, state = hb.get_heartbeat()
        if hbadd_ctrl is not None and hbadd_node is not None:
            if self.heartbeat_waiting is None:
                self.heartbeat_waiting = HADD%(hbadd_ctrl, hbadd_node)
            elif self.heartbeat_waiting == HADD%(hbadd_ctrl, hbadd_node):
                self.heartbeat_received = True
        print "HADD : %s/%s = %s"%(hbadd_ctrl, hbadd_node, state)

    def assertHeartbeatNode(self, hadd=None, timeout=90):
        print "Waiting for %s" % (hadd)
        self.heartbeat_waiting = hadd
        self.heartbeat_message = None
        i = 0
        while i< timeout*10000 and not self.heartbeat_received:
            time.sleep(0.0001)
            i += 1
        self.assertTrue(self.heartbeat_received)

    def assertNodeRequest(self, cmd_class=0, genre=0x04, uuid='request_info_nodes', node_hadd=None, client_hadd=None, data=None, is_writeonly=False, is_readonly=False, timeout=5):
        self.message_received = False
        print "Waiting for %s : %s" % (node_hadd,uuid)
        def mqtt_on_message(client, userdata, message):
            """On generic message
            """
            self.message = message
            self.message_received = True
        self.mqttc.subscribe(topic=TOPIC_NODES_REPLY%client_hadd, callback=mqtt_on_message)
        time.sleep(0.5)
        msg={ 'cmd_class': cmd_class, 'genre':genre, 'uuid':uuid, 'reply_hadd':client_hadd, 'data':data, 'hadd':node_hadd, 'is_writeonly':is_writeonly, 'is_readonly':is_readonly}
        self.mqttc.publish('/nodes/%s/request' % (node_hadd), json_dumps(msg))
        i = 0
        while i< timeout*10000 and not self.message_received:
            time.sleep(0.0001)
            i += 1
        self.assertTrue(self.message_received)
        self.mqttc.unsubscribe(topic=TOPIC_NODES_REPLY%client_hadd)

    def assertBroadcastRequest(self, cmd_class=0, genre=0x04, uuid='request_info_nodes', node_hadd=None, client_hadd=None, data=None, is_writeonly=False, is_readonly=False, timeout=5):
        self.message_received = False
        def mqtt_on_message(client, userdata, message):
            """On generic message
            """
            self.message = message
            self.message_received = True
        self.mqttc.subscribe(topic=TOPIC_BROADCAST_REPLY%client_hadd, callback=mqtt_on_message)
        time.sleep(0.5)
        msg={ 'cmd_class': cmd_class, 'genre':genre, 'uuid':uuid, 'reply_hadd':client_hadd, 'data':data, 'is_writeonly':is_writeonly, 'is_readonly':is_readonly}
        self.mqttc.publish(TOPIC_BROADCAST_REQUEST, json_dumps(msg))
        i = 0
        while i< timeout*10000 and not self.message_received:
            time.sleep(0.0001)
            i += 1
        self.assertTrue(self.message_received)
        self.mqttc.unsubscribe(topic=TOPIC_BROADCAST_REPLY%client_hadd)

class JNTTServerCommon():
    """Common tests for servers
    """
    def test_010_start_heartbeat_stop(self):
        self.start()
        self.assertHeartbeatNode()
        self.stop()

    def test_011_start_reload_stop(self):
        self.start()
        self.assertHeartbeatNode()
        time.sleep(2.5)
        self.server.reload()
        time.sleep(2.5)
        self.assertHeartbeatNode()
        self.stop()

    def test_012_start_reload_threads_stop(self):
        self.start()
        self.assertHeartbeatNode()
        time.sleep(2.5)
        self.server.reload_threads()
        time.sleep(2.5)
        self.assertHeartbeatNode()
        self.stop()
