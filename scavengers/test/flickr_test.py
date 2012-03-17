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
from scavengers.scavenger_utils import OK_CODE
from scavengers.flickr_scavenger import FlickrScavenger

NAME = "flickr"
IN = NAME + "_in"
OUT = NAME + "_out"
EMAIL = "camp101988@yahoo.com"
TIMEOUT = 10

class FlickrTest(unittest.TestCase):
  def setUp(self):
    self.scavenger = FlickrScavenger(NAME, IN, OUT)
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

if __name__=="__main__":
  unittest.main()
