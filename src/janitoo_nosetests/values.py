# -*- coding: utf-8 -*-

"""Unittests for Janitoo-common.
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

import warnings
warnings.filterwarnings("ignore")

import sys, os
import time
import unittest
import threading
import logging
from pkg_resources import iter_entry_points
import mock
import ConfigParser
from ConfigParser import RawConfigParser

sys.path.insert(0,os.path.dirname(__name__))

from janitoo_nosetests import JNTTBase

from janitoo.runner import Runner, jnt_parse_args
from janitoo.server import JNTServer
from janitoo.options import JNTOptions

class JNTTFactory(JNTTBase):
    """Test the value factory
    """
    prog = 'test'
    entry_name = 'generic'
    conf_file = 'tests/data/test_value_factory.conf'

    def get_main_value(self, node_uuid='test_node', **kwargs):
        print "entry_name ", self.entry_name
        entry_points = { }
        for entrypoint in iter_entry_points(group = 'janitoo.values'):
            entry_points[entrypoint.name] = entrypoint.load()
        options = {}
        with mock.patch('sys.argv', [self.prog, 'start', '--conf_file=%s'%self.conf_file]):
            options = vars(jnt_parse_args())
        return entry_points[self.entry_name](options=JNTOptions(options), node_uuid=node_uuid, **kwargs)

    def assertSetgetConfig(self, node_uuid, data=10):
        main_value = self.get_main_value(node_uuid=node_uuid)
        main_value.set_data_index(node_uuid=node_uuid, index=0, data=data)
        self.assertEqual(data, main_value.get_data_index(node_uuid=node_uuid, index=0))
        config = RawConfigParser()
        config.read([self.conf_file])
        opt = config.get(node_uuid, 'value_entry_uuid_0')
        self.assertEqual(opt, "%s"%main_value.get_data_index(node_uuid=node_uuid, index=0))
        self.assertEqual(type(data), type(main_value.get_data_index(node_uuid=node_uuid, index=0)))

class JNTTFactoryCommon():
    """Test the value factory
    """
    def test_001_collect_values_entries(self):
        print "entry_name ", self.entry_name
        entry_points = { }
        for entrypoint in iter_entry_points(group = 'janitoo.values'):
            entry_points[entrypoint.name] = entrypoint.load()
        self.assertTrue(self.entry_name in entry_points)

class JNTTFactoryPollCommon(JNTTFactoryCommon):
    """Test the value factory
    """
    def test_011_value_entry_poll(self, **kwargs):
        node_uuid='test_node'
        main_value = self.get_main_value(node_uuid=node_uuid, **kwargs)
        self.assertFalse(main_value.is_writeonly)
        print main_value
        poll_value = main_value.create_poll_value()
        print poll_value
        main_value._set_poll(node_uuid, 0, 0)
        self.assertEqual(0, main_value._get_poll(node_uuid, 0))
        main_value._set_poll(node_uuid, 0, 5)
        self.assertEqual(5, main_value._get_poll(node_uuid, 0))
        self.assertEqual(5, main_value.poll_delay)
        self.assertEqual(True, main_value.is_polled)
        main_value._set_poll(node_uuid, 0, 0)
        self.assertEqual(0, main_value._get_poll(node_uuid, 0))
        self.assertEqual(0, main_value.poll_delay)
        self.assertEqual(False, main_value.is_polled)

class JNTTFactoryConfigCommon(JNTTFactoryCommon):
    """Test the value factory
    """

    def test_021_value_entry_config(self, **kwargs):
        node_uuid='test_node'
        main_value = self.get_main_value(node_uuid=node_uuid, **kwargs)
        print main_value
        config_value = main_value.create_config_value()
        print config_value
        main_value.set_config(node_uuid, 0, '0')
        self.assertEqual('0', main_value.get_config(node_uuid, 0))
        main_value.set_config(node_uuid, 0, '5')
        self.assertEqual('5', main_value.get_config(node_uuid, 0))
