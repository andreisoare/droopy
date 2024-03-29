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
from scavengers.scavenger_utils import OK_CODE, NOT_FOUND_ERROR_CODE
from scavengers.github_scavenger import GithubScavenger

NAME = "github"
IN = NAME + "_in"
OUT = NAME + "_out"
TIMEOUT = 5

EMAIL_VALID = "andrei.soare@gmail.com"
EMAIL_INVALID = "asoare13@yahoo.com"
USERNAME = "andreisoare"
DISPLAY_NAME = "Andrei Soare"
LOCATION = "Vancouver, Canada"
PROFILE = "github.com/andreisoare"

class GithubTest(unittest.TestCase):
  def setUp(self):
    self.scavenger = GithubScavenger(NAME, IN, OUT)
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
    self.assertEqual(str(self.response['username']), USERNAME)
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

