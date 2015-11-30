# -*- coding: utf-8 -*-

"""Unittests for flask.
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
import urllib2


from sqlalchemy.orm import sessionmaker, scoped_session
from alembic import command as alcommand

from flask_testing import TestCase
from flask_testing import LiveServerTestCase

from janitoo_nosetests import JNTTBase

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

class JNTTFlaskMain():
    """Common function for flask
    """

    def list_routes(self):
        output = []
        for rule in self.app.url_map.iter_rules():
            methods = ','.join(rule.methods)
            line = urllib2.unquote("{:50s} {:30s} {}".format(rule.endpoint, methods, rule))
            output.append(line)
        for line in sorted(output):
            print(line)

class JNTTFlask(JNTTBase, TestCase, JNTTFlaskMain):
    """Test the flask
    """
    flask_conf = "tests/data/janitoo_flask.conf"

class JNTTFlaskCommon():
    """Common tests for flask
    """
    pass

class JNTTFlaskLive(JNTTBase, LiveServerTestCase, JNTTFlaskMain):
    """Test the flask server in live
    """
    flask_conf = "tests/data/janitoo_flask.conf"

    def assertUrl(self, url='/', code=200):
        response = urllib2.urlopen(self.get_server_url()+url)
        self.assertEqual(response.code, code)

class JNTTFlaskLiveCommon():
    """Common tests for flask server in live
    """
    pass

