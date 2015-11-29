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

class JNTTModels(JNTTBase):
    """Test the models
    """
    models_conf = "tests/data/janitoo_db.conf"

    def setUp(self):
        JNTTBase.setUp(self)
        options = JNTOptions({'conf_file':self.models_conf})
        options.load()
        engine = create_db_engine(options)
        self.dbmaker = sessionmaker()
        # Bind the sessionmaker to engine
        self.dbmaker.configure(bind=engine)
        self.dbsession = scoped_session(self.dbmaker)
        Base.metadata.create_all(bind=engine)

    def test_001_user(self):
        group = jntmodels.Group(name="test_group")
        user = jntmodels.User(username="test_user", email="test@gmail.com", _password="test", primary_group=group)
        self.dbsession.merge(group, user)
        self.dbsession.commit()

class JNTTFullModels(JNTTBase):
    """Test the models
    """
    def setUp(self):
        JNTTBase.setUp(self)
        import janitoo_db.models

class JNTTFullModelsCommon():
    """Common tests for models
    """

    def test_001_upgrade(self):
        alcommand.upgrade(janitoo_config("sqlite:////tmp/janitoo_test/home/fullmodel.sqlite"), 'heads')

    def test_002_downgrade(self):
        alcommand.upgrade(janitoo_config("sqlite:////tmp/janitoo_test/home/fullmodel.sqlite"), 'heads')
        alcommand.downgrade(janitoo_config("sqlite:////tmp/janitoo_test/home/fullmodel.sqlite"), 'base')

