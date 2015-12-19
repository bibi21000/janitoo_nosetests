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

from gevent import monkey
monkey.patch_all()

import sys, os
import time, datetime
import unittest
import urllib
import urllib2

from flask_bower import Bower
from flask_cache import Cache

from flask_testing import TestCase, LiveServerTestCase

from janitoo_nosetests import JNTTBase

from janitoo.options import JNTOptions
from janitoo_db.base import Base, create_db_engine
from janitoo_db.migrate import Config as alConfig, collect_configs, janitoo_config


class JNTTFlaskMain():
    """Common function for flask
    """

    def get_routes(self):
        res = {}
        for rule in self.app.url_map.iter_rules():
            res["{}".format(rule.endpoint)] = {'methods':rule.methods, 'rule':"{}".format(rule)}
        return res

    def list_routes(self):
        output = []
        routes = self.get_routes()
        for route in routes:
            line = urllib.unquote("{:50s} {:30s} {}".format(route, routes[route]['methods'], routes[route]['rule']))
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

    def test_001_server_is_up(self):
        self.assertEqual(type(self.app.extensions['cache']), type(Cache()))
        self.assertEqual(type(self.app.extensions['bower']), type(Bower()))
        routes = self.get_routes()
        print routes
        self.assertTrue('bower.serve' in routes)
        self.assertTrue('static' in routes)

class JNTTFlaskLive(JNTTBase, LiveServerTestCase, JNTTFlaskMain):
    """Test the flask server in live
    """
    flask_conf = "tests/data/janitoo_flask.conf"


class JNTTFlaskLiveCommon():
    """Common tests for flask server in live
    """

    def assertUrl(self, url='/', code=200):
        response = urllib2.urlopen(self.get_server_url()+url, timeout=60)
        print response
        self.assertEqual(response.code, code)

