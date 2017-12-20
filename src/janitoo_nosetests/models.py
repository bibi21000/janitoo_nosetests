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
import threading
import logging
from pkg_resources import iter_entry_points

from nose_parameterized import parameterized
from nose.plugins.skip import SkipTest

from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import Table, Column, String
from alembic import command as alcommand

from janitoo_nosetests import JNTTBase, alembic_version, DBCONFS

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
    def tearDown(self):
        #~ try:
            #~ self.drop_all()
        #~ except Exception:
            #~ pass
        JNTTBase.tearDown(self)

    def setUp(self):
        JNTTBase.setUp(self)
        options = JNTOptions({'conf_file':self.getDataFile(self.models_conf)})
        options.load()
        self.dbengine = create_db_engine(options)
        self.dbmaker = sessionmaker()
        # Bind the sessionmaker to engine
        self.dbmaker.configure(bind=self.dbengine)
        self.dbsession = scoped_session(self.dbmaker)
        self.drop_all()
        self.options = options

    def skipSqliteTest(self):
        """Skip a test for sqlite database
        """
        if self.options.get_option('database', 'sqlalchemy.url').startswith('sqlite:'):
            raise SkipTest("%s" % ("Skipped for sqlite database"))

    def create_all(self):
        Base.metadata.create_all(bind=self.dbengine)

    def drop_all(self):
        Base.metadata.drop_all(bind=self.dbengine)
        try:
            alembic_version.drop(bind=self.dbengine)
        except Exception:
            pass
            
class JNTTModelsCommon(object):
    """Common tests for models
    """
    models_conf = "tests/data/janitoo_db.conf"

    def test_001_versiondb(self):
        self.drop_all()
        config = alConfig(conf_file=self.models_conf)
        config.initdb()
        versions = config.versiondb()
        self.assertTrue(len(versions)>0)

    def test_002_heads(self):
        self.drop_all()
        config = alConfig(conf_file=self.models_conf)
        heads = config.heads()
        self.assertTrue(len(heads)>0)

    def test_003_checkdb(self):
        self.drop_all()
        config = alConfig(conf_file=self.models_conf)
        config.initdb()
        self.assertTrue(config.checkdb())
        config.downgrade()
        self.assertFalse(config.checkdb())

class JNTTDbsModels(JNTTBase):
    """Tests for model on docker
    """
    dbconf = ('sqlite', {'dbconf':'sqlite:////tmp/janitoo_tests.sqlite'})
    def setUp(self):
        JNTTBase.setUp(self)
        tmp_conf = self.cpTempFile(self.models_conf)
        options = JNTOptions(options={'conf_file':tmp_conf})
        options.set_option('database', 'sqlalchemy.url', self.dbconf[1]['dbconf'])
        self.models_conf = tmp_conf
        self.dbengine = create_db_engine(self.dbconf[1]['dbconf'])
        self.dbmaker = sessionmaker()
        # Bind the sessionmaker to engine
        self.dbmaker.configure(bind=self.dbengine)
        self.dbsession = scoped_session(self.dbmaker)
        self.drop_all()

    @classmethod
    def skipSqliteTest(self):
        """Skip a test for sqlite database
        """
        if self.dbconf[1]['dbconf'].startswith('sqlite:'):
            raise SkipTest("%s" % ("Skipped for sqlite database"))

    def tearDown(self):
        #~ try:
            #~ self.drop_all()
        #~ except Exception:
            #~ pass
        JNTTBase.tearDown(self)

    def create_all(self):
        Base.metadata.create_all(bind=self.dbengine)

    def drop_all(self):
        Base.metadata.drop_all(bind=self.dbengine)
        try:
            alembic_version.drop(bind=self.dbengine)
        except Exception:
            pass

class JNTTDockerModels(JNTTDbsModels):
    """Tests for model on docker
    """
    def setUp(self):
        JNTTBase.onlyDockerTest()
        JNTTDbsModels.setUp(self)

def jntt_models(module_name, cls, prefix='Class', dbs=None):
    """Launch cls tests for every supported database
    """
    if dbs is None:
        dbs = DBCONFS
    for name, conf in dbs:
        setattr(sys.modules[module_name], 'TestModels_%s_%s'%(prefix,name), type('TestModels_%s_%s'%(prefix,name), (JNTTDbsModels,cls), {'dbconf': (name, conf)}))

def jntt_docker_models(module_name, cls, prefix='Class', dbs=None):
    """Launch cls tests for every supported database
    """
    if dbs is None:
        dbs = DBCONFS
    for name, conf in dbs:
        setattr(sys.modules[module_name], 'TestModels_%s_%s'%(prefix,name), type('TestModels_%s_%s'%(prefix,name), (JNTTDockerModels,cls), {'dbconf': (name, conf)}))

class JNTTFullModels(JNTTBase):
    """Test the models
    """
    db_uri = "sqlite:////tmp/janitoo_test/home/fullmodel.sqlite"
    def setUp(self):
        JNTTBase.setUp(self)
        import janitoo_db.models

    @classmethod
    def skipSqliteTest(self):
        """Skip a test for sqlite database
        """
        if self.db_uri.startswith('sqlite:'):
            raise SkipTest("%s" % ("Skipped for sqlite database"))

class JNTTDockerFullModels(JNTTFullModels):
    """Tests for full models on docker
    """
    dbconf = ('sqlite', {'dbconf':'sqlite:////tmp/janitoo_tests.sqlite'})
    def setUp(self):
        JNTTFullModels.onlyDockerTest()
        JNTTFullModels.setUp(self)
        self.db_uri = self.dbconf[1]['dbconf']

def jntt_docker_fullmodels(module_name, cls, prefix='Class', dbs=None):
    """Launch cls tests for every supported database
    """
    if dbs is None:
        dbs = DBCONFS
    for name, conf in dbs:
        setattr(sys.modules[module_name], 'TestFullModels_%s_%s'%(prefix,name), type('TestFullModels_%s_%s'%(prefix,name), (JNTTDockerFullModels,cls), {'dbconf': (name, conf)}))

class JNTTFullModelsCommon(object):
    """Common tests for models
    """

    def test_001_upgrade(self):
        alcommand.upgrade(janitoo_config(self.db_uri), 'heads')

    def test_002_downgrade(self):
        alcommand.upgrade(janitoo_config(self.db_uri), 'heads')
        alcommand.downgrade(janitoo_config(self.db_uri), 'base')
