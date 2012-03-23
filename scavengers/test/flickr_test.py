# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: tabara.mihai@gmail.com (Mihai Tabara)
# Unit test for Flickr scavenger

import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(dirname(abspath(__file__)))))

import unittest
import thread
import beanstalkc
import simplejson
from scavengers.scavenger import Scavenger
from scavengers.scavenger_utils import OK_CODE, NOT_FOUND_ERROR_CODE
from scavengers.flickr_scavenger import FlickrScavenger

NAME = "flickr"
IN = NAME + "_in"
OUT = NAME + "_out"
TIMEOUT = 5

EMAIL_VALID = "camp101988@yahoo.com"
EMAIL_INVALID = "tabara.mihai@gmail.com"
USERNAME = "tabara mihai"
DISPLAY_NAME = ""
LOCATION = ""
PROFILE = "http://www.flickr.com/people/9910681@N02/"

class FlickrTest(unittest.TestCase):
  def setUp(self):
    self.scavenger = FlickrScavenger(NAME, IN, OUT)
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
    self.assertEqual(self.response['username'], USERNAME)
    self.assertEqual(self.response['display_name'], DISPLAY_NAME)
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

