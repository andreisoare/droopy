# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)
#
# Unit test for Github scavenger.

import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(dirname(abspath(__file__)))))

import unittest
import thread
import beanstalkc
import simplejson
from scavengers.scavenger import Scavenger
from scavengers.scavenger_utils import OK_CODE
from scavengers.github_scavenger import GithubScavenger

NAME = "github"
IN = NAME + "_in"
OUT = NAME + "_out"
EMAIL = "andrei.soare@gmail.com"
TIMEOUT = 5

class GithubTest(unittest.TestCase):
  def setUp(self):
    self.scavenger = GithubScavenger(NAME, IN, OUT)
    thread.start_new_thread(self.scavenger.run, ())

    beanstalk = beanstalkc.Connection()
    beanstalk.use(IN)
    beanstalk.put(EMAIL)

    beanstalk.watch(OUT)
    job = beanstalk.reserve(timeout=TIMEOUT)
    self.response = simplejson.loads(job.body)
    job.delete()

  def test_status(self):
    self.assertEqual(self.response['status'], OK_CODE)

  def test_email(self):
    self.assertEqual(self.response['email'], EMAIL)
