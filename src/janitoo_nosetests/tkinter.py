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
from janitoo.thread import JNTBusThread

from janitoo_tkinter import JanitooTk

class JNTTTkinter(JNTTBase):
    """TKinter base test
    """
    client_conf = ""
    section = "tkinter"

    def create_root(self):
        root = JanitooTk(options=self.options, section=self.section)
        return root

    def setUp(self):
        JNTTBase.setUp(self)
        self.options = JNTOptions({'conf_file' : self.getDataFile(self.client_conf)})
        self.root = self.create_root()

    def tearDown(self):
        JNTTBase.tearDown(self)


class Common(object):
    """Common tests for tkinter and docker
    """
    pass

class JNTTServerCommon(Common):
    """Common tests for tkinter
    """
    pass

class JNTTDockerTkinterCommon(Common):
    """Common tests for tkinter on docker
    """
    pass

class JNTTDockerTkinter(JNTTTkinter):
    """Tests for tkinter on docker
    """

    def setUp(self):
        JNTTTkinter.onlyDockerTest()
        JNTTTkinter.setUp(self)
