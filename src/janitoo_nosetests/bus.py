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
except Exception:  # pragma: no cover
    # bootstrapping
    pass # pragma: no cover

import sys, os
import shutil
import mock
import logging
from logging.config import fileConfig as logging_fileConfig

from janitoo_nosetests import JNTTBase

from janitoo.dhcp import HeartbeatMessage
from janitoo.utils import json_dumps
from janitoo.utils import HADD_SEP, HADD
from janitoo.utils import TOPIC_NODES, TOPIC_NODES_REPLY
from janitoo.utils import TOPIC_BROADCAST_REPLY
from janitoo.utils import TOPIC_VALUES_USER, TOPIC_VALUES_CONFIG, TOPIC_VALUES_SYSTEM
from janitoo.options import string_to_bool

class JNTTBus(JNTTBase):
    """Bus base test
    """

    bus = None
    oid = None
    generic ='generic'

    def setUp(self):
        JNTTBase.setUp(self)

    def tearDown(self):
        self.factory = None
        JNTTBase.tearDown(self)

class JNTTBusCommon(object):
    """Common tests for buss
    """

    def test_001_bus_oid(self):
        bus = self.bus()
        self.assertFalse(bus is None)
        self.assertEqual(self.generic, bus.oid)
        bus = self.bus(oid=self.oid)
        self.assertFalse(bus is None)
        self.assertEqual(self.oid, bus.oid)

    def test_002_bus_values(self):
        bus = self.bus()
        #Bus values must starts with
        for value in bus.values:
            print("Check bus value : {:s}_".format(self.oid))
            self.assertTrue(value.startswith("{:s}_".format(self.oid)))
            self.assertNotEqual(0, bus.values[value].cmd_class)

