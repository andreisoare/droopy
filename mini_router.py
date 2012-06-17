# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author(s): tabara.mihai@gmail.com (Mihai Tabara)
#            diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)

import time
import beanstalkc
import thread
import simplejson
from datetime import datetime
from pymongo.objectid import ObjectId

from networks_scouter import NetworkScouterScavenger
from base.mongodb_utils import get_mongo_collection
from mongodb.models import SocialProfile
from scavengers import AboutmeScavenger, LastfmScavenger, LinkedinScavenger, \
          PinterestScavenger, SoundcloudScavenger, TwitterScavenger
from scavengers.scavenger_config import MONGO_COLLECTION

scavengers_dict = {
                    'aboutme' : AboutmeScavenger,
                    'lastfm' : LastfmScavenger,
                    'linkedin' : LinkedinScavenger,
                    'pinterest' : PinterestScavenger,
                    'soundcloud' : SoundcloudScavenger,
                    'twitter' : TwitterScavenger,
                  }

USERNAME_QUEUE = "mini_eta_queue"
RESPONSE_QUEUE = "mini_response_queue"

SLEEP_TIME = 1.5

class MiniRouter:
  def __init__(self):
    self.scavengers = []
    self.username_beanstalk = beanstalkc.Connection()
    self.response_beanstalk = beanstalkc.Connection()

    self.response_beanstalk.watch(RESPONSE_QUEUE)
    thread.start_new_thread(self.watch_responses, ())

    for key in scavengers_dict:
      scavenger = scavengers_dict[key](key, key + '_in', RESPONSE_QUEUE)
      self.scavengers.append(scavenger)
      thread.start_new_thread(scavenger.run, ())

  def run(self):
    beanstalk = beanstalkc.Connection()
    beanstalk.watch(USERNAME_QUEUE)

    while True:
      job = beanstalk.reserve()
      if job is None:
        continue

      package = job.body
      self.forward_email(package)
      time.sleep(SLEEP_TIME)
      job.delete()

  def forward_email(self, package):
    for key in scavengers_dict:
      self.username_beanstalk.use(key + '_in')
      self.username_beanstalk.put(package)

  def watch_responses(self):
    while True:
      job = self.response_beanstalk.reserve()
      if job is None:
        continue

      job.delete()

if __name__=="__main__":
  r = MiniRouter()
  r.run()
