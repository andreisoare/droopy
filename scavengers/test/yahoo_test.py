# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)
#
# Unit test for Yahoo scavenger.

import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(dirname(abspath(__file__)))))

import unittest
import thread
import beanstalkc
import simplejson
from scavengers.scavenger import Scavenger
from scavengers.scavenger_utils import OK_CODE
from scavengers.yahoo_scavenger import YahooScavenger

NAME = "yahoo"
IN = NAME + "_in"
OUT = NAME + "_out"
EMAIL = "camp101988@yahoo.com"
TIMEOUT = 5

class YahooTest(unittest.TestCase):
  def setUp(self):
    self.scavenger = YahooScavenger(NAME, IN, OUT)
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
