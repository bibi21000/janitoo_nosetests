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
__copyright__ = "Copyright © 2013-2014-2015 Sébastien GALLET aka bibi21000"

import sys, os
import time, datetime
import unittest
import threading
import logging
from pkg_resources import iter_entry_points

from sqlalchemy.orm import sessionmaker, scoped_session
from alembic import command as alcommand

from janitoo_nosetests import JNTTBase
from janitoo_nosetests.server import JNTTServer, JNTTServerCommon

from janitoo.utils import JanitooNotImplemented, JanitooException
from janitoo.options import JNTOptions
from janitoo_db.base import Base, create_db_engine
from janitoo_db.migrate import Config as alConfig, collect_configs, janitoo_config

##############################################################
#Check that we are in sync with the official command classes
#Must be implemented for non-regression
from janitoo.classes import COMMAND_DESC

COMMAND_DISCOVERY = 0x5000

assert(COMMAND_DESC[COMMAND_DISCOVERY] == 'COMMAND_DISCOVERY')
##############################################################

class JNTTDBServer(JNTTServer):
    """Test the bd server
    """
    pass

class JNTTDBServerCommon(JNTTServerCommon):
    """Common tests for models
    """
    def test_051_dbserver_no_auto_migrate(self):
        options = JNTOptions({'conf_file':self.server_conf})
        options.load()
        self.server.options.set_option('database','auto_migrate', False)
        with self.assertRaises(JanitooException):
            self.start()
            self.assertHeartbeatNode()
            self.stop()

    def test_052_dbserver_auto_migrate(self):
        options = JNTOptions({'conf_file':self.server_conf})
        options.load()
        self.server.options.set_option('database','auto_migrate', True)
        self.start()
        self.assertHeartbeatNode()
        self.stop()
