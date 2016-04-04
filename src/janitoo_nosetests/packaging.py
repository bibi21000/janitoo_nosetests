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
import janitoo_packaging.packaging

class JNTTPackaging(JNTTBase):
    """packages base test
    """
    setuppy = 'setup'
    directory = '.'

    def setUp(self):
        JNTTBase.setUp(self)

    def tearDown(self):
        JNTTBase.tearDown(self)


    def create_package(self):
        return janitoo_packaging.packaging.Package(setuppy=self.setuppy, directory=self.directory)

    def assertComponent(self, component):
        package = self.create_package()
        components = package.get_janitoo_components()
        self.assertTrue(component in components)

    def assertThread(self, thread):
        package = self.create_package()
        threads = package.get_janitoo_threads()
        self.assertTrue(thread in threads)

    def assertValue(self, value):
        package = self.create_package()
        values = package.get_janitoo_values()
        self.assertTrue(value in values)

class JNTTPackagingCommon():
    """Common tests for packages
    """

    def test_001_check_package(self):
        warnings, errors = self.create_package().check_package()
        self.assertEqual(warnings, [])
        self.assertEqual(errors, [])
