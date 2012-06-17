# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)
#
# Unit test for Aboutme scavenger.

import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(dirname(abspath(__file__)))))

import unittest
import thread
import beanstalkc
import simplejson
from datetime import datetime
from pymongo.objectid import ObjectId
from base.mongodb_utils import get_mongo_collection
from mongodb.models import SocialProfile
from scavengers.scavenger import Scavenger
from scavengers.scavenger_utils import OK_CODE, NOT_FOUND_ERROR_CODE
from scavengers.aboutme_scavenger import AboutmeScavenger

NAME = "aboutme"
IN = NAME + "_in"
OUT = NAME + "_out"
TIMEOUT = 15
COLLECTION = "test"

EMAIL = "test"
USERNAME_VALID = "andreisoare"
USERNAME_INVALID = "andrei.soare"
DISPLAY_NAME = "Andrei Soare"
PROFILE = "about.me/andreisoare"

class AboutmeTest(unittest.TestCase):
  def setUp(self):
    self.scavenger = AboutmeScavenger(NAME, IN, OUT)
    thread.start_new_thread(self.scavenger.run, ())

    self.collection = get_mongo_collection(COLLECTION)
    social_profile = self.collection.SocialProfile()
    social_profile['time'] = datetime.now()
    social_profile['email'] = unicode(EMAIL)
    social_profile.save()

    self.json = {}
    self.json['email'] = EMAIL
    self.json['id'] = str(social_profile['_id'])
    self.json['collection'] = COLLECTION

  def tearDown(self):
    self.collection.remove(ObjectId(self.json['id']))

  def test_valid(self):
    self.json['username'] = USERNAME_VALID

    beanstalk = beanstalkc.Connection()
    beanstalk.use(IN)
    beanstalk.put(simplejson.dumps(self.json))

    beanstalk.watch(OUT)
    job = beanstalk.reserve(timeout=TIMEOUT)
    self.assertEqual(job.body, 'ok')
    job.delete()

    profile = self.collection.find_one({'_id': ObjectId(self.json['id'])})
    response = profile['network_candidates'][NAME][0]
    self.assertEqual(response['status'], OK_CODE)
    self.assertEqual(str(response['email']), EMAIL)
    self.assertEqual(str(response['username']), USERNAME_VALID)
    self.assertEqual(str(response['display_name']), DISPLAY_NAME)
    self.assertEqual(str(response['profiles'][0]), PROFILE)

  def test_invalid(self):
    self.json['username'] = USERNAME_INVALID

    beanstalk = beanstalkc.Connection()
    beanstalk.use(IN)
    beanstalk.put(simplejson.dumps(self.json))

    beanstalk.watch(OUT)
    job = beanstalk.reserve(timeout=TIMEOUT)
    self.assertEqual(job.body, 'not')
    job.delete()

