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
import traceback

class JNTTComponent(JNTTBase):
    """Component base test
    """

    component_name = None

    def setUp(self):
        JNTTBase.setUp(self)
        self.factory = {}
        for entry in iter_entry_points(group='janitoo.components'):
            try:
                loaded = entry.load()
                self.factory[entry.name] = loaded
            except:
                #traceback.print_exc()
                pass
        print "Component %s" % self.component_name

    def tearDown(self):
        self.factory = None
        JNTTBase.tearDown(self)

    def assertComponentEntryPoint(self, entry):
        mkth = None
        for entry in iter_entry_points(group='janitoo.components', name=entry):
            mkth = entry.load()
        self.assertNotEqual(mkth, None)

class JNTTComponentCommon():
    """Common tests for components
    """

    def test_001_component_entry_point(self):
        self.assertFalse(self.component_name is None)
        self.assertComponentEntryPoint(self.component_name)

