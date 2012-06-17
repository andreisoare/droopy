# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: tabara.mihai@gmail.com (Mihai Tabara)
# Unit test for Jigsaw scavenger

import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(dirname(abspath(__file__)))))

import unittest
import thread
import beanstalkc
import simplejson
from scavengers.scavenger import Scavenger
from scavengers.scavenger_utils import OK_CODE, NOT_FOUND_ERROR_CODE
from scavengers.jigsaw_scavenger import JigsawScavenger

NAME = "jigsaw"
IN = NAME + "_in"
OUT = NAME + "_out"
TIMEOUT = 5

EMAIL_VALID = "asadat@salesforce.com"
EMAIL_INVALID = "tabara.mihai@gmail.com"
DISPLAY_NAME = "Ali Sadat"
LOCATION = "San Francisco, CA, United States"
PROFILE = "jigsaw.com/BC.xhtml?contactId=45003056"

class JigsawTest(unittest.TestCase):
  def setUp(self):
    self.scavenger = JigsawScavenger(NAME, IN, OUT)
    thread.start_new_thread(self.scavenger.run, ())

  def test_valid(self):
    beanstalk = beanstalkc.Connection()
    beanstalk.use(IN)
    beanstalk.put(EMAIL_VALID)

    beanstalk.watch(OUT)
    job = beanstalk.reserve(timeout=TIMEOUT)
    self.response = simplejson.loads(job.body)['response']
    job.delete()

    self.assertEqual(self.response['status'], OK_CODE)
    self.assertEqual(str(self.response['email']), EMAIL_VALID)
    self.assertEqual(str(self.response['display_name']), DISPLAY_NAME)
    self.assertEqual(str(self.response['location']), LOCATION)
    self.assertEqual(str(self.response['profiles'][0]), PROFILE)

  def test_invalid(self):
    beanstalk = beanstalkc.Connection()
    beanstalk.use(IN)
    beanstalk.put(EMAIL_INVALID)

    beanstalk.watch(OUT)
    job = beanstalk.reserve(timeout=TIMEOUT)
    self.response = simplejson.loads(job.body)['response']
    job.delete()

    self.assertEqual(self.response['status'], NOT_FOUND_ERROR_CODE)
    self.assertEqual(str(self.response['email']), EMAIL_INVALID)

