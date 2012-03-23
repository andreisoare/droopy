# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: mihai.tabara@gmail.com (Mihai Tabara)

import beanstalkc
import thread
import simplejson

from datetime import datetime
from scavengers import FlickrScavenger, GithubScavenger, GooglePlusScavenger, \
                      JigsawScavenger, MyspaceScavenger, YahooScavenger

scavengers_dict = {
                    'flickr' : FlickrScavenger,
                    'github' : GithubScavenger,
                    'google_plus' : GooglePlusScavenger,
                    'jigsaw' : JigsawScavenger,
                    'myspace' : MyspaceScavenger,
                    'yahoo' : YahooScavenger
                  }

RESPONSE_QUEUE = "response_queue"

class Router:
  def __init__(self):
    self.scavengers = []
    self.processing_profiles = {}
    self.email_beanstalk = beanstalkc.Connection()
    self.response_beanstalk = beanstalkc.Connection()

    self.response_beanstalk.watch(RESPONSE_QUEUE)
    thread.start_new_thread(self.watch_responses, ())

    for key in scavengers_dict:
      scavenger = scavengers_dict[key](key, key + '_in', RESPONSE_QUEUE)
      self.scavengers.append(scavenger)
      thread.start_new_thread(scavenger.run, ())

  def forward_email(self, social_profile):
    self.processing_profiles[str(social_profile.email)] = social_profile

    for key in scavengers_dict:
      self.email_beanstalk.use(key + '_in')
      self.email_beanstalk.put(str(social_profile.email))

  def watch_responses(self):
    while True:
      job = self.response_beanstalk.reserve()
      if job is None:
        continue

      queue_response = simplejson.loads(job.body)
      self.process_response(queue_response)

      job.delete()

  def process_response(self, queue_response):
    response_object = queue_response['response']
    network_type = queue_response['type']

    social_profile = self.processing_profiles[response_object['email']]

    status = network_type + '_status'
    link = network_type + '_link'
    parsed = network_type + '_parsed'

    social_profile.status = response_object['status']
    social_profile.link = unicode(response_object['profiles'][0])
    social_profile.parsed = response_object
    social_profile.time = datetime.now()

    social_profile.save()

    self.test_profile_completion(social_profile)

  def test_profile_completion(self, social_profile):
    profile_complete = True
    for key in scavengers_dict:
      status = key + '_status'
      if social_profile.status == 0:
        profile_complete = False
        break

    if profile_complete is True:
      # TODO(mihai): join data to complete personal data information
      social_profile.save()
      del self.processing_profiles[str(social_profile.email)]
