# -*- coding: utf-8 -*-
"""Unittests for Janitoo.
"""
__license__ = """
    This file is part of Janitoo.

    Janitoo is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Janitoo is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Janitoo. If not, see <http://www.gnu.org/licenses/>.

"""
__author__ = 'Sébastien GALLET aka bibi21000'
__email__ = 'bibi21000@gmail.com'
__copyright__ = "Copyright © 2013-2014-2015-2016 Sébastien GALLET aka bibi21000"

# Update this value when running on raspberry
# 1.5 is a good choice
SLEEP = 0.50

import sys, os, errno
import time
import unittest
import threading
import json as mjson
import shutil
from pkg_resources import iter_entry_points
from nose.plugins.skip import SkipTest

from janitoo.mqtt import MQTTClient
from janitoo.dhcp import JNTNetwork, HeartbeatMessage
from janitoo.utils import json_dumps, json_loads
from janitoo.utils import HADD_SEP, HADD
from janitoo.utils import TOPIC_HEARTBEAT

##############################################################
#Check that we are in sync with the official command classes
#Must be implemented for non-regression
from janitoo.classes import COMMAND_DESC

COMMAND_DISCOVERY = 0x5000

assert(COMMAND_DESC[COMMAND_DISCOVERY] == 'COMMAND_DISCOVERY')
##############################################################


class JNTCommon():
    """Common tests for JNTServer
    """
    def test_000_server_start_wait_stop(self):
        self.wipTest("Pass but freeze nosetests")
        self.startServer()
        time.sleep(1.5)
        self.stopServer()


class JNTControllerServer(JNTCommon):
    """Tests for JNTServer acting as a controller
    """
    message = None

    def mqtt_on_message(self, client, userdata, message):
        """On generic message
        """
        self.message = message

    def mqtt_on_heartbeat_message(self, client, userdata, message):
        """On generic message
        """
        self.heartbeat_message = message

    def startHeartbeat(self):
        self.startClient(options=self.server.options.data)
        self.mqtthearbeat.subscribe(topic='/dhcp/heartbeat', callback=self.mqtt_on_heartbeat_message)

    def assertHeartbeat(self, timeout=90):
        self.heartbeat_message = None
        for i in range(0,timeout*1000):
            if self.heartbeat_message is not None:
                break
            else:
                time.sleep(0.001)
        self.assertTrue(self.heartbeat_message is not None)
        self.assertTrue(self.heartbeat_message.payload is not None)

    def assertHeartbeatNode(self, hadd, timeout=90, status=None):
        self.heartbeat_message = None
        checked = False
        state = None
        add_ctrl, add_node = hadd.split(HADD_SEP)
        for i in range(0,timeout*1000):
            if self.heartbeat_message is not None:
                #~ print self.heartbeat_message
                hb = HeartbeatMessage(self.heartbeat_message)
                hbadd_ctrl, hbadd_node, state = hb.get_heartbeat()
                #~ print hbadd_ctrl, hbadd_node, state
                #msg = json_loads(self.heartbeat_message.payload)
                if int(hbadd_ctrl) == int(add_ctrl) and int(hbadd_node) == int(add_node):
                    if status is not None:
                        if state == status:
                            checked = True
                            break
                    else:
                        checked = True
                        break
                self.heartbeat_message = None
            else:
                time.sleep(0.001)
        print "HADD : ", add_ctrl, add_node, state
        self.assertTrue(checked)

    def assertNodeRequest(self, cmd_class=0, uuid='request_info_nodes', node_hadd=None, client_hadd=None):
        self.mqttc.subscribe(topic='/nodes/%s/reply'%client_hadd, callback=self.mqtt_on_message)
        time.sleep(0.5)
        msg={ 'cmd_class': cmd_class, 'genre':0x04, 'uuid':uuid, 'reply_hadd':client_hadd}
        self.mqttc.publish('/nodes/%s/request' % (node_hadd), json_dumps(msg))
        for i in range(0,300):
            if self.message is not None:
                break
            else:
                time.sleep(0.05)
        self.assertTrue(self.message is not None)
        self.assertTrue(self.message.payload is not None)
        self.mqttc.unsubscribe(topic='/nodes/%s/reply'%client_hadd)

    def assertBroadcastRequest(self, cmd_class=0, uuid='request_info_nodes', client_hadd=None):
        self.mqttc.subscribe(topic='/broadcast/reply/%s'%client_hadd, callback=self.mqtt_on_message)
        time.sleep(0.5)
        msg={ 'cmd_class': cmd_class, 'genre':0x04, 'uuid':uuid, 'data':client_hadd}
        self.mqttc.publish('/broadcast/request', json_dumps(msg))
        for i in range(0,300):
            if self.message is not None:
                break
            else:
                time.sleep(0.05)
        self.assertTrue(self.message is not None)
        self.assertTrue(self.message.payload is not None)
        self.mqttc.unsubscribe(topic='/broadcast/reply/%s'%client_hadd)

    def test_050_start_heartbeat_stop(self):
        self.startServer()
        time.sleep(0.5)
        self.startHeartbeat()
        time.sleep(0.5)
        self.assertHeartbeat()
        self.stopServer()

    def test_052_start_reload_stop(self):
        self.startServer()
        time.sleep(0.5)
        self.startHeartbeat()
        time.sleep(0.5)
        self.assertHeartbeat()
        time.sleep(2.5)
        self.assertHeartbeat()
        self.server.reload()
        time.sleep(2.5)
        self.assertHeartbeat()
        self.stopServer()

    def test_055_start_reload_threads_stop(self):
        self.startServer()
        time.sleep(0.5)
        self.startHeartbeat()
        time.sleep(0.5)
        self.assertHeartbeat()
        time.sleep(0.5)
        self.assertHeartbeat()
        self.server.reload_threads()
        time.sleep(2.5)
        self.assertHeartbeat()
        self.stopServer()

class JNTDBCommon():
    """Common tests for JNTDBServer
    """
    def test_040_server_check_db_auto_migrate(self):
        self.startServer()
        self.server.check_db(migrate=True)
        self.stopServer()

    def test_041_server_check_db_auto_migrate_from_conf(self):
        self.startServer()
        self.server.check_db(migrate=None)
        self.stopServer()

