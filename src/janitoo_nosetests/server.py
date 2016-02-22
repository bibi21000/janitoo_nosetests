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

import sys, os, errno
import time
import unittest
import json as mjson
import threading
import shutil
import mock
import re

from janitoo_nosetests import JNTTBase

from janitoo.mqtt import MQTTClient
from janitoo.dhcp import JNTNetwork, HeartbeatMessage
from janitoo.utils import json_dumps, json_loads
from janitoo.utils import HADD_SEP, HADD, NETWORK_REQUESTS
from janitoo.utils import TOPIC_HEARTBEAT
from janitoo.utils import TOPIC_NODES, TOPIC_NODES_REPLY, TOPIC_NODES_REQUEST
from janitoo.utils import TOPIC_BROADCAST_REPLY, TOPIC_BROADCAST_REQUEST
from janitoo.utils import TOPIC_VALUES_USER, TOPIC_VALUES_CONFIG, TOPIC_VALUES_SYSTEM, TOPIC_VALUES_BASIC
from janitoo.runner import jnt_parse_args
from janitoo.options import JNTOptions

##############################################################
#Check that we are in sync with the official command classes
#Must be implemented for non-regression
from janitoo.classes import COMMAND_DESC

COMMAND_DISCOVERY = 0x5000

assert(COMMAND_DESC[COMMAND_DISCOVERY] == 'COMMAND_DISCOVERY')
##############################################################

class JNTTServer(JNTTBase):
    """Server base test
    """
    server_class = None
    server_conf = ""
    hadd_ctrl = None
    hadds = None

    def setUp(self):
        JNTTBase.setUp(self)
        self.mqttc = None
        self.message = None
        self.message_received = False
        self.hearbeat_mqttc = None
        self.heartbeat_message = None
        self.heartbeat_waiting = None
        self.heartbeat_waitings = None
        self.heartbeat_received = False
        self.server = None
        self.running_server = None
        if self.hadd_ctrl is None and self.hadds is not None and len(self.hadds)>0:
            self.hadd_ctrl = self.hadds[0]

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
        self.heartbeat_waitings = None
        self.heartbeat_received = False
        self.server = None
        self.running_server = None
        JNTTBase.tearDown(self)

    def startClient(self, conf=None):
        if conf is None:
            conf = self.server.options.data
        if self.mqttc is None:
            self.mqttc = MQTTClient(options=conf)
            self.mqttc.connect()
            self.mqttc.start()
        if self.hearbeat_mqttc is None:
            self.hearbeat_mqttc = MQTTClient(options=conf)
            self.hearbeat_mqttc.connect()
            self.hearbeat_mqttc.start()
            self.hearbeat_mqttc.subscribe(topic=TOPIC_HEARTBEAT, callback=self.mqtt_on_heartbeat_message)

    def stopClient(self):
        if self.mqttc != None:
            self.mqttc.stop()
        if self.hearbeat_mqttc != None:
            self.hearbeat_mqttc.unsubscribe(topic=TOPIC_HEARTBEAT)
            self.hearbeat_mqttc.stop()
        if self.mqttc != None:
            if self.mqttc.is_alive():
                self.mqttc.join()
            self.mqttc = None
        if self.hearbeat_mqttc != None:
            if self.hearbeat_mqttc.is_alive():
                self.hearbeat_mqttc.join()
            self.hearbeat_mqttc = None

    def startServer(self):
        if self.server is None:
            with mock.patch('sys.argv', ['%s'%self.server_class, 'start', '--conf_file=%s' % self.getDataFile(self.server_conf)]):
                options = vars(jnt_parse_args())
                self.server = self.server_class(options)
            self.server.start()
            self.running_server = threading.Timer(0.01, self.server.run)
            self.running_server.start()
            time.sleep(1.5)

    def stopServer(self):
        if self.server is not None:
            self.server.stop()
            time.sleep(5)
            self.server = None
        if self.running_server is not None:
            self.running_server.cancel()
            time.sleep(5)
            self.running_server = None
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
                if self.heartbeat_waitings is None:
                    self.heartbeat_received = True
                elif HADD%(hbadd_ctrl, hbadd_node) in self.heartbeat_waitings:
                    self.heartbeat_waitings.remove(HADD%(hbadd_ctrl, hbadd_node))
                    if len(self.heartbeat_waitings)==0:
                        self.heartbeat_received = True
            elif self.heartbeat_waiting == HADD%(hbadd_ctrl, hbadd_node):
                self.heartbeat_received = True
        print "HADD : %s/%s = %s"%(hbadd_ctrl, hbadd_node, state)

    def assertInLogfile(self, expr='^ERROR '):
        """Assert an expression is in logifle
        Must be called at the end of process, when the server has closed the logfile.
        """
        self.assertTrue(self.server_conf is not None)
        options = JNTOptions(options={'conf_file':self.getDataFile(self.server_conf)})
        log_file_from_config = options.get_option('handler_file','args',None)
        self.assertTrue(log_file_from_config is not None)
        #I know, it's bad
        log_args = eval(log_file_from_config)
        log_file_from_config = log_args[0]
        self.assertFile(log_file_from_config)
        found = False
        with open(log_file_from_config, 'r') as hand:
            for line in hand:
                print line
                if re.search(expr, line):
                    found = True
        self.assertTrue(found)

    def assertNotInLogfile(self, expr='^ERROR '):
        """Assert an expression is not in logifle.
        Must be called at the end of process, when the server has closed the logfile.
        """
        self.assertTrue(self.server_conf is not None)
        options = JNTOptions(options={'conf_file':self.getDataFile(self.server_conf)})
        log_file_from_config = options.get_option('handler_file','args',None)
        self.assertTrue(log_file_from_config is not None)
        #I know, it's bad
        log_args = eval(log_file_from_config)
        log_file_from_config = log_args[0]
        self.assertFile(log_file_from_config)
        found = False
        with open(log_file_from_config, 'r') as hand:
            for line in hand:
                print line
                if re.search(expr, line):
                    found = True
        self.assertFalse(found)

    def assertHeartbeatNode(self, hadd=None, timeout=90):
        print "Waiting for %s" % (hadd)
        self.heartbeat_waiting = hadd
        self.heartbeat_waitings = None
        self.heartbeat_message = None
        self.heartbeat_received = False
        i = 0
        while i< timeout*10000 and not self.heartbeat_received:
            time.sleep(0.0001)
            i += 1
        self.assertTrue(self.heartbeat_received)
        time.sleep(0.5)

    def assertHeartbeatNodes(self, hadds=[], timeout=90):
        if hadds is None:
            hadds = self.hadds
        print "Waiting for %s" % (hadds)
        self.heartbeat_waiting = None
        self.heartbeat_waitings = list(hadds)
        self.heartbeat_message = None
        self.heartbeat_received = False
        i = 0
        while i< timeout*10000 and not self.heartbeat_received:
            time.sleep(0.0001)
            i += 1
        print "Unreceived heartbeats %s" % self.heartbeat_waitings
        self.assertTrue(self.heartbeat_received)
        time.sleep(0.5)

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
        time.sleep(0.5)

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
        time.sleep(0.5)

    def assertUpdateValue(self, type='user', data=None, cmd_class=0, genre=0x04, uuid='request_info_nodes', node_hadd=None, client_hadd=None, is_writeonly=False, is_readonly=False, timeout=5):
        self.message_received = False
        self.message = None
        print "Waiting for %s : %s" % (node_hadd,uuid)
        def mqtt_on_message(client, userdata, message):
            """On generic message
            """
            msg = json_loads(message.payload)
            print "Received message %s"%msg
            if msg['uuid'] == uuid and msg['hadd'] == node_hadd:
                self.message = message
                self.message_received = True
        self.mqttc.subscribe(topic='/values/%s/%s/#'%(type, node_hadd), callback=mqtt_on_message)
        print 'Subscribe to /values/%s/%s/#'%(type, node_hadd)
        time.sleep(0.5)
        msg={ 'cmd_class': cmd_class, 'genre':genre, 'uuid':uuid, 'reply_hadd':client_hadd, 'data':data, 'hadd':node_hadd, 'is_writeonly':is_writeonly, 'is_readonly':is_readonly}
        self.mqttc.publish('/nodes/%s/request' % (node_hadd), json_dumps(msg))
        i = 0
        while i< timeout*10000 and not self.message_received:
            time.sleep(0.0001)
            i += 1
        self.assertTrue(self.message_received)
        self.assertTrue(self.message is not None)
        self.assertTrue(self.message.payload is not None)
        if data is not None:
            msg = json_loads(self.message.payload)
            self.assertEqual(msg['data'], data)
        self.mqttc.unsubscribe(topic='/values/%s/%s/#'%(type, node_hadd))
        time.sleep(0.5)

    def assertNotUpdateValue(self, type='user', data=None, cmd_class=0, genre=0x04, uuid='request_info_nodes', node_hadd=None, client_hadd=None, is_writeonly=False, is_readonly=False, timeout=5):
        self.message_received = False
        self.message = None
        print "Waiting for %s : %s" % (node_hadd,uuid)
        def mqtt_on_message(client, userdata, message):
            """On generic message
            """
            msg = json_loads(message.payload)
            print "Received message %s"%msg
            if msg['uuid'] == uuid and msg['hadd'] == node_hadd:
                self.message = message
                self.message_received = True
        self.mqttc.subscribe(topic='/values/%s/%s/#'%(type, node_hadd), callback=mqtt_on_message)
        print 'Subscribe to /values/%s/%s/#'%(type, node_hadd)
        time.sleep(0.5)
        msg={ 'cmd_class': cmd_class, 'genre':genre, 'uuid':uuid, 'reply_hadd':client_hadd, 'data':data, 'hadd':node_hadd, 'is_writeonly':is_writeonly, 'is_readonly':is_readonly}
        self.mqttc.publish('/nodes/%s/request' % (node_hadd), json_dumps(msg))
        i = 0
        while i< timeout*10000 and not self.message_received:
            time.sleep(0.0001)
            i += 1
        self.assertTrue(self.message is None)
        self.assertFalse(self.message_received)
        self.mqttc.unsubscribe(topic='/values/%s/%s/#'%(type, node_hadd))
        time.sleep(0.5)

    def assertWaitValue(self, type='user', data=None, cmd_class=0, genre=0x04, uuid='request_info_nodes', node_hadd=None, client_hadd=None, is_writeonly=False, is_readonly=False, timeout=5):
        self.message_received = False
        self.message = None
        print "Waiting for %s : %s" % (node_hadd,uuid)
        def mqtt_on_message(client, userdata, message):
            """On generic message
            """
            msg = json_loads(message.payload)
            print "Received message %s"%msg
            if msg['uuid'] == uuid and msg['hadd'] == node_hadd:
                self.message = message
                self.message_received = True
        self.mqttc.subscribe(topic='/values/%s/%s/#'%(type, node_hadd), callback=mqtt_on_message)
        print 'Subscribe to /values/%s/%s/#'%(type, node_hadd)
        time.sleep(0.5)
        i = 0
        while i< timeout*10000 and not self.message_received:
            time.sleep(0.0001)
            i += 1
        self.assertTrue(self.message_received)
        self.assertTrue(self.message is not None)
        self.assertTrue(self.message.payload is not None)
        if data is not None:
            msg = json_loads(self.message.payload)
            self.assertEqual(msg['data'], data)
        self.mqttc.unsubscribe(topic='/values/%s/%s/#'%(type, node_hadd))
        time.sleep(0.5)

    def assertNotWaitValue(self, type='user', data=None, cmd_class=0, genre=0x04, uuid='request_info_nodes', node_hadd=None, client_hadd=None, is_writeonly=False, is_readonly=False, timeout=5):
        self.message_received = False
        self.message = None
        print "Waiting for %s : %s" % (node_hadd,uuid)
        def mqtt_on_message(client, userdata, message):
            """On generic message
            """
            msg = json_loads(message.payload)
            print "Received message %s"%msg
            if msg['uuid'] == uuid and msg['hadd'] == node_hadd:
                self.message = message
                self.message_received = True
        self.mqttc.subscribe(topic='/values/%s/%s/#'%(type, node_hadd), callback=mqtt_on_message)
        print 'Subscribe to /values/%s/%s/#'%(type, node_hadd)
        time.sleep(0.5)
        i = 0
        while i< timeout*10000 and not self.message_received:
            time.sleep(0.0001)
            i += 1
        self.assertTrue(self.message is None)
        self.assertFalse(self.message_received)
        self.mqttc.unsubscribe(topic='/values/%s/%s/#'%(type, node_hadd))
        time.sleep(0.5)

class JNTTServerCommon():
    """Common tests for servers
    """
    def test_010_start_heartbeat_stop(self):
        self.start()
        try:
            self.assertHeartbeatNode(hadd=self.hadd_ctrl)
            time.sleep(5)
        finally:
            self.stop()

    def test_011_start_reload_stop(self):
        self.start()
        try:
            self.assertHeartbeatNodes(hadds=self.hadds)
            time.sleep(2)
            self.server.reload()
            time.sleep(1)
            self.assertHeartbeatNodes(hadds=self.hadds)
            time.sleep(1)
        finally:
            self.stop()

    def test_012_start_reload_threads_stop(self):
        self.start()
        try:
            self.assertHeartbeatNodes(hadds=self.hadds)
            time.sleep(2)
            self.server.reload_threads()
            time.sleep(1)
            self.assertHeartbeatNodes(hadds=self.hadds)
            time.sleep(1)
        finally:
            self.stop()

    def test_020_broadcast_nodes_and_values(self):
        self.start()
        try:
            self.assertHeartbeatNode(hadd=self.hadd_ctrl)
            time.sleep(5)
            self.assertHeartbeatNode(hadd=self.hadd_ctrl)
            for request in NETWORK_REQUESTS:
                self.assertBroadcastRequest(cmd_class=COMMAND_DISCOVERY, uuid=request, client_hadd=HADD%(9999,0))
                time.sleep(2)
        finally:
            self.stop()

    def test_021_request_nodes_and_values(self):
        if self.hadd_ctrl is None:
            self.skipTest("No hadd_ctrl defined. Skip test")
        self.start()
        try:
            self.assertHeartbeatNode(hadd=self.hadd_ctrl)
            time.sleep(5)
            self.assertHeartbeatNode(hadd=self.hadd_ctrl)
            for request in NETWORK_REQUESTS:
                self.assertNodeRequest(cmd_class=COMMAND_DISCOVERY, uuid=request, node_hadd=self.hadd_ctrl, client_hadd=HADD%(9999,0))
                time.sleep(2)
        finally:
            self.stop()

    def test_030_wait_for_all_nodes(self):
        if self.hadds is None:
            self.skipTest("No hadds defined. Skip test")
        self.start()
        try:
            self.assertHeartbeatNodes(hadds=self.hadds)
        finally:
            self.stop()

    def test_040_server_start_no_error_in_log(self):
        self.start()
        self.assertHeartbeatNodes(hadds=self.hadds)
        time.sleep(65)
        self.assertNotInLogfile('^ERROR ')
        self.assertInLogfile('Start the server')
        self.assertInLogfile('Connected to broker')
        self.assertInLogfile('Found heartbeats in timeout')

    def test_041_server_reload_no_error_in_log(self):
        self.test_040_server_start_no_error_in_log()
        self.server.reload()
        time.sleep(2)
        self.assertHeartbeatNodes(hadds=self.hadds)
        time.sleep(30)
        self.assertInLogfile('Reload the server')
        self.assertNotInLogfile('^ERROR ')

    def test_042_server_reload_threads_no_error_in_log(self):
        self.test_040_server_start_no_error_in_log()
        self.server.reload_threads()
        time.sleep(2)
        self.assertHeartbeatNodes(hadds=self.hadds)
        time.sleep(30)
        self.assertInLogfile('Reload threads')
        self.assertNotInLogfile('^ERROR ')
