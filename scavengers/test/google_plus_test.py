# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)
#
# Unit test for GooglePlus scavenger.

import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(dirname(abspath(__file__)))))

import unittest
import thread
import beanstalkc
import simplejson
from scavengers.scavenger import Scavenger
from scavengers.scavenger_utils import OK_CODE
from scavengers.google_plus_scavenger import GooglePlusScavenger

NAME = "google_plus"
IN = NAME + "_in"
OUT = NAME + "_out"
EMAIL = "andrei.soare@gmail.com"
TIMEOUT = 5

class GooglePlusTest(unittest.TestCase):
  def setUp(self):
    self.scavenger = GooglePlusScavenger(NAME, IN, OUT)
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
