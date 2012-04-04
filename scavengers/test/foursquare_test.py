# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)
#         tabara.mihai@gmail.com (Mihai Tabara)
#
# Unit test for Foursquare scavenger.

import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(dirname(abspath(__file__)))))

import unittest
import thread
import beanstalkc
import simplejson
from scavengers.scavenger import Scavenger
from scavengers.scavenger_utils import OK_CODE, NOT_FOUND_ERROR_CODE
from scavengers.foursquare_scavenger import FoursquareScavenger

NAME = "foursquare"
IN = NAME + "_in"
OUT = NAME + "_out"
TIMEOUT = 5

EMAIL_VALID = "andrei.soare@gmail.com"
EMAIL_INVALID = "asoare13@yahoo.com"
DISPLAY_NAME = "Andrei Soare"
GENDER = "male"
LOCATION = "Weston, FL"
PROFILE = "https://foursquare.com/user/4999608"

class FoursquareTest(unittest.TestCase):
  def setUp(self):
    self.scavenger = FoursquareScavenger(NAME, IN, OUT)
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
    self.assertEqual(self.response['email'], EMAIL_VALID)
    self.assertEqual(self.response['display_name'], DISPLAY_NAME)
    self.assertEqual(self.response['gender'], GENDER)
    self.assertEqual(self.response['location'], LOCATION)
    self.assertEqual(self.response['profiles'][0], PROFILE)

  def test_invalid(self):
    beanstalk = beanstalkc.Connection()
    beanstalk.use(IN)
    beanstalk.put(EMAIL_INVALID)

    beanstalk.watch(OUT)
    job = beanstalk.reserve(timeout=TIMEOUT)
    self.response = simplejson.loads(job.body)['response']
    job.delete()

    self.assertEqual(self.response['status'], NOT_FOUND_ERROR_CODE)
    self.assertEqual(self.response['email'], EMAIL_INVALID)

