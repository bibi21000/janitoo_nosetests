# -*- coding: utf-8 -*-

"""Unittests for socketio.
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

#~ from flask import Flask, session, request
from flask_socketio import SocketIO, send, emit, join_room, leave_room

from janitoo_nosetests import JNTTBase

from janitoo.options import JNTOptions
from janitoo_db.base import Base, create_db_engine
from janitoo_db.migrate import Config as alConfig, collect_configs, janitoo_config


class JNTTSocketIO(JNTTBase):
    """Test the flask
    """
    flask_conf = "tests/data/janitoo_flask.conf"

    def create_app(self):
        """
        Create your Flask app here, with any
        configuration you need.
        """
        raise NotImplementedError

    def assertConnect(self, namespace="/janitoo"):
        app, socketio = self.create_app()
        client = socketio.test_client(app, namespace=namespace)
        received = client.get_received(namespace)
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['args'], ({'data': 'Connected'},))
        client.disconnect(namespace)

class JNTTSocketIOCommon():
    """Common tests for flask
    """
    pass
