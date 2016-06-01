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

import sys, os, errno
import time, datetime
import unittest
import threading
import json as mjson
import shutil
import mock
import platform
import pwd
import grp
import socket
import tempfile
from netifaces import interfaces, ifaddresses, AF_INET
from pkg_resources import iter_entry_points

from nose.plugins.skip import SkipTest
from janitoo.mqtt import MQTTClient
from janitoo.dhcp import JNTNetwork, HeartbeatMessage
from janitoo.utils import json_dumps, json_loads
from janitoo.utils import HADD_SEP, HADD
from janitoo.utils import TOPIC_HEARTBEAT
from janitoo.utils import TOPIC_NODES, TOPIC_NODES_REPLY, TOPIC_NODES_REQUEST
from janitoo.utils import TOPIC_BROADCAST_REPLY, TOPIC_BROADCAST_REQUEST
from janitoo.utils import TOPIC_VALUES_USER, TOPIC_VALUES_CONFIG, TOPIC_VALUES_SYSTEM, TOPIC_VALUES_BASIC
from janitoo.runner import jnt_parse_args

class JNTTBase(unittest.TestCase):
    """Grand mother
    """
    path = '/tmp/janitoo_test'
    broker_user = 'toto'
    broker_password = 'toto'

    @classmethod
    def setUpClass(self):
        self.skip = True
        if 'NOSESKIP' in os.environ:
            self.skip = eval(os.environ['NOSESKIP'])
        if 'MANUALSKIP' in os.environ:
            self.skipManual = eval(os.environ['MANUALSKIP'])
        else:
            self.skipManual = True
        self.tmp_files = []

    @classmethod
    def tearDownClass(self):
        try:
            pass
            #shutil.rmtree(self.path)
        except OSError as exc: # Python >2.5
            pass

    def setUp(self):
        try:
            shutil.rmtree(self.path)
        except OSError as exc: # Python >2.5
            time.sleep(1.0)
            try:
                shutil.rmtree(self.path)
            except OSError as exc: # Python >2.5
                time.sleep(5.0)
                try:
                    shutil.rmtree(self.path)
                except OSError as exc: # Python >2.5
                    pass
        os.makedirs(self.path)
        os.makedirs(os.path.join(self.path, 'etc'))
        os.makedirs(os.path.join(self.path, 'cache'))
        os.makedirs(os.path.join(self.path, 'home'))
        os.makedirs(os.path.join(self.path, 'log'))
        os.makedirs(os.path.join(self.path, 'run'))

    def tearDown(self):
        try:
            pass
            #shutil.rmtree(self.path)
        except OSError:
            pass

    @classmethod
    def skipManualTest(self, message=''):
        """Skip a manual test (need human intervention)
        """
        if self.skipManual:
            raise SkipTest("%s" % ("manual test (%s)" % message))

    @classmethod
    def skipTest(self, message=''):
        """Skip a test
        """
        raise SkipTest("%s" % (message))

    @classmethod
    def skipAllTests(self):
        """Skip a test when JANITOO_ALLTESTS is in env.
        """
        if 'JANITOO_ALLTESTS' in os.environ:
            raise SkipTest("%s" % ("Skipped on JANITOO_ALLTESTS"))

    @classmethod
    def onlyAllTests(self):
        """Run a test only when JANITOO_ALLTESTS is in env
        """
        if 'JANITOO_ALLTESTS' not in os.environ:
            raise SkipTest("%s" % ("Only on JANITOO_ALLTESTS"))

    @classmethod
    def skipTravisTest(self):
        """Skip a test on travis.
        """
        if 'TRAVIS_OS_NAME' in os.environ:
            raise SkipTest("%s" % ("Skipped on travis"))

    @classmethod
    def onlyTravisTest(self):
        """Run a test only on travis
        """
        if 'TRAVIS_OS_NAME' not in os.environ:
            raise SkipTest("%s" % ("Only on travis"))

    @classmethod
    def skipCircleTest(self):
        """Skip a test on circle
        """
        if 'CIRCLE_USERNAME' in os.environ:
            raise SkipTest("%s" % ("Skipped on circle"))

    @classmethod
    def onlyCircleTest(self):
        """Run a test only on circle
        """
        if 'CIRCLE_USERNAME' not in os.environ:
            raise SkipTest("%s" % ("Only on circle"))

    @classmethod
    def skipCITest(self):
        """Skip a test on continouos integration
        """
        if 'TRAVIS_OS_NAME' in os.environ:
            raise SkipTest("%s" % ("Skipped on Continuous Integration"))
        if 'CIRCLE_USERNAME' in os.environ:
            raise SkipTest("%s" % ("Skipped on Continuous Integration"))

    @classmethod
    def onlyCITest(self):
        """Run a test only on continuous integration
        """
        if 'TRAVIS_OS_NAME' not in os.environ and \
           'CIRCLE_USERNAME' not in os.environ:
            raise SkipTest("%s" % ("Only on Continuous Integration"))

    @classmethod
    def skipDockerTest(self):
        """Skip a test on docker
        """
        if 'JANITOO_DOCKER' in os.environ:
            raise SkipTest("%s" % ("Skipped on Docker"))

    @classmethod
    def onlyDockerTest(self):
        """Run a test only on docker
        """
        if 'JANITOO_DOCKER' not in os.environ:
            raise SkipTest("%s" % ("Only on docker"))

    @classmethod
    def skipRasperryTest(self):
        """Skip a test when not on raspy
        """
        if platform.machine().startswith('armv6'):
            raise SkipTest("%s" % ('Skipped on Raspberry pi'))

    @classmethod
    def onlyRasperryTest(self):
        """Skip a test when not on raspy
        """
        if not platform.machine().startswith('armv6'):
            raise SkipTest("%s" % ('Only on a Raspberry pi'))

    @classmethod
    def skipNoPingTest(self, ip):
        """Skip a test when when no ping response
        """
        response = os.system("ping -c 1 -w2 " + ip + " > /dev/null 2>&1")
        if response != 0:
            raise SkipTest("No ping response from %s" % (ip))

    @classmethod
    def wipTest(self, message=''):
        """Work In Progress test
        """
        raise SkipTest("Work in progress : %s" % message)

    def touchFile(self, path):
        """Touch a file
        """
        with open(path, 'a'):
            os.utime(path, None)

    def rmFile(self, path):
        """Remove a file
        """
        if os.path.isfile(path):
            os.remove(path)

    def assertFile(self, path):
        """Check a file exists
        """
        print "Check file %s" % path
        self.assertTrue(os.path.isfile(path))

    def assertDir(self, path):
        """Check a directory exists
        """
        print "Check directory %s" % path
        self.assertTrue(os.path.isdir(path))

    def assertUser(self, usr):
        """Check a user exists on the system
        """
        print "Check user %s" % usr
        try:
            pwd.getpwnam(usr)
            res = True
        except KeyError:
            print('User %s does not exist.' % usr)
            res = False
        self.assertTrue(res)

    def assertGroup(self, grp):
        """Check a group exists on the system
        """
        print "Check group %s" % grp
        try:
            grp.getgrnam('somegrp')
        except KeyError:
            print('Group %s does not exist.' % grp)
            res = False
        self.assertTrue(res)

    def assertDateInterval(self, which, dateref, delta=1):
        """
        """
        print "Check date %s in interval : %s  +/-  %ss" % (which, dateref, delta)
        self.assertTrue(which > dateref - datetime.timedelta(seconds=delta))
        self.assertTrue(which < dateref + datetime.timedelta(seconds=delta))

    def assertTCP(self, server='localhost', port=80):
        """
        """
        # Create a TCP socket
        try:
            ip  = socket.gethostbyname(server)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect_ex((ip, port))
            s.send('test')
            s.close()
        except socket.error, e:
            raise AssertionError("Can't connect to %s(%s):%s"%(server, ip, port))
        except socket.gaierror:
            raise AssertionError("Can't connect to %s(%s):%s"%(server, 'unknown', port))

    def assertFsmBoot(self, bus=None, state='booting', timeout=20):
        """Assert Finish State Machine can boot
        """
        if bus is None:
            self.skipTest("Can't test state of a None bus")
        i = 0
        while i<timeout*2 and bus.state == state:
            time.sleep(0.5)
            i += 1
        print "Bus state %s"%bus.state
        self.assertNotEqual(state, bus.state)

    def mkDir(self, path):
        """Create a directory
        """
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise

    def mkTempFile(self, prefix="tmp"):
        """Create a temporary file and return ist name
        """
        tmpfile,tmpname = tempfile.mkstemp(prefix='janitoo_%s'%prefix)
        self.tmp_files.append(tmpname)
        os.close(tmpfile)
        return tmpname

    def cpTempFile(self, src):
        """Copy the path_src fil to a tmp file.
        Return the path of the tmp file
        """
        dst = None
        try:
            dst = self.mkTempFile()
            shutil.copyfile(src, dst)
        finally:
            try:
                src.close()
            except Exception:
                pass
            try:
                dst.close()
            except Exception:
                pass
        return dst

    def rmDir(self, path):
        """Remove a directory
        """
        #try:
        shutil.rmtree(path)
        #except OSError as exc: # Python >2.5
        #    pass

    def startServer(self):
        pass

    def stopServer(self):
        pass

    def getDataFile(self, path):
        """Retrieve a datafile. Look in the current dir and if not found look in the __file__ directory
        """
        if os.path.isfile(path):
            return path
        path = os.path.join(os.path.dirname(__name__), path)
        if os.path.isfile(path):
            return path
        raise RuntimeError("[%s] : Can't find data file %s"%(self.__class__.__name__, path))

    @property
    def ip4Addresses(self):
        """Retrieve all ip4 adresses as a list
        """
        ip_list = []
        for interface in interfaces():
            for link in ifaddresses(interface).get(AF_INET, ()):
                ip_list.append(link['addr'])
        print "Found ip4 addresses %s" % ip_list
        return ip_list

class JNTTDockerBase(JNTTBase):
    """Tests for servers on docker
    """

    def setUp(self):
        JNTTBase.onlyDockerTest()
        JNTTBase.setUp(self)

