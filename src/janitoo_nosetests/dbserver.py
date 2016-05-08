# -*- coding: utf-8 -*-

"""Unittests for models.
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

import sys, os
import time, datetime
import unittest

from sqlalchemy.orm import sessionmaker, scoped_session
from alembic import command as alcommand

from janitoo_nosetests import JNTTBase
from janitoo_nosetests.server import JNTTServer, JNTTServerCommon, JNTTDockerServerCommon
from janitoo_nosetests.models import DBCONFS

from janitoo.utils import JanitooNotImplemented, JanitooException
from janitoo.options import JNTOptions
from janitoo_db.base import Base, create_db_engine
from janitoo_db.migrate import Config as alConfig, collect_configs, janitoo_config

class JNTTDBServer(JNTTServer):
    """Test the bd server
    """
    pass

class Common():
    """Common tests for models
    """
    def test_051_dbserver_no_auto_migrate(self):
        self.rmFile('/tmp/janitoo_test/home/test_dhcpd.db')
        options = JNTOptions({'conf_file':self.getDataFile(self.server_conf)})
        options.load()
        options.set_option('database','auto_migrate', False)
        try:
            with self.assertRaises(JanitooException):
                self.start()
                self.assertHeartbeatNode()
                self.stop()
        finally:
            options.set_option('database','auto_migrate', True)

    def test_052_dbserver_auto_migrate(self):
        self.rmFile('/tmp/janitoo_test/home/test_dhcpd.db')
        options = JNTOptions({'conf_file':self.getDataFile(self.server_conf)})
        options.load()
        options.set_option('database','auto_migrate', True)
        self.start()
        self.assertHeartbeatNode()
        self.stop()

class JNTTDBServerCommon(Common, JNTTServerCommon):
    """Common tests for models
    """
    def test_051_dbserver_no_auto_migrate(self):
        self.rmFile('/tmp/janitoo_test/home/test_dhcpd.db')
        options = JNTOptions({'conf_file':self.getDataFile(self.server_conf)})
        options.load()
        options.set_option('database','auto_migrate', False)
        try:
            with self.assertRaises(JanitooException):
                self.start()
                self.assertHeartbeatNode()
                self.stop()
        finally:
            options.set_option('database','auto_migrate', True)

    def test_052_dbserver_auto_migrate(self):
        self.rmFile('/tmp/janitoo_test/home/test_dhcpd.db')
        options = JNTOptions({'conf_file':self.getDataFile(self.server_conf)})
        options.load()
        options.set_option('database','auto_migrate', True)
        self.start()
        self.assertHeartbeatNode()
        self.stop()

class JNTTDBDockerServer(JNTTDBServer):
    """Tests for database servers on docker
    """
    dbconf = ('sqlite', {'dbconf':'sqlite:////tmp/janitoo_tests.sqlite'})

    def setUp(self):
        JNTTDBServer.onlyDockerTest()
        JNTTDBServer.setUp(self)
        tmp_conf = cpTempFile(self.server_conf)
        options = JNTOptions(options={'conf_file':tmp_conf})
        options.set_option('database', 'sqlalchemy.url', self.dbconf[1]['dbconf'])
        self.server_conf = tmp_conf

class JNTTDBDockerServerCommon(Common, JNTTDockerServerCommon):
    """Common tests for servers on docker
    """
    longdelay = 90
    shortdelay = 90

    def test_040_server_start_no_error_in_log(self):
        JNTTDBServer.onlyDockerTest()
        JNTTDockerServerCommon.test_040_server_start_no_error_in_log(self)

def jntt_docker_dbserver(module_name, cls):
    """Launch cls tests for every supported database
    """
    for name, conf in DBCONFS:
        setattr(sys.modules[module_name], 'JNTTDBDockerServer%s'%name, type(name, (JNTTDBDockerServer,cls), {'dbconf': (name, conf)}))
