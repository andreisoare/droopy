# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: tabara.mihai@gmail.com (Mihai Tabara)
#         diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)

import beanstalkc
import thread
import simplejson
from datetime import datetime
from pymongo.objectid import ObjectId

from networks_scouter import NetworkScouterScavenger
from base.mongodb_utils import get_mongo_collection
from mongodb.models import SocialProfile
from scavengers import FlickrScavenger, GithubScavenger, GooglePlusScavenger, \
          JigsawScavenger, MyspaceScavenger, YahooScavenger, FoursquareScavenger
from scavengers.scavenger_config import MONGO_COLLECTION

scavengers_dict = {
                    'flickr' : FlickrScavenger,
                    'github' : GithubScavenger,
                    'google_plus' : GooglePlusScavenger,
                    'jigsaw' : JigsawScavenger,
                    'myspace' : MyspaceScavenger,
                    'yahoo' : YahooScavenger,
                    'foursquare' : FoursquareScavenger
                  }

EMAIL_QUEUE = "eta_queue"
RESPONSE_QUEUE = "response_queue"
USERNAME_QUEUE = "mini_eta_queue"

class Router:
  def __init__(self):
    self.scavengers = []
    self.processing_profiles = {}
    self.email_beanstalk = beanstalkc.Connection()
    self.response_beanstalk = beanstalkc.Connection()
    self.username_beanstalk = beanstalkc.Connection()
    self.username_beanstalk.use(USERNAME_QUEUE)

    self.response_beanstalk.watch(RESPONSE_QUEUE)
    thread.start_new_thread(self.watch_responses, ())

    self.profiles = get_mongo_collection(MONGO_COLLECTION)

    for key in scavengers_dict:
      scavenger = scavengers_dict[key](key, key + '_in', RESPONSE_QUEUE)
      self.scavengers.append(scavenger)
      thread.start_new_thread(scavenger.run, ())

  def run(self):
    beanstalk = beanstalkc.Connection()
    beanstalk.watch(EMAIL_QUEUE)

    while True:
      job = beanstalk.reserve()
      if job is None:
        continue

      email = job.body
      social_profile = self.profiles.SocialProfile()
      social_profile['email'] = unicode(email)
      social_profile['time'] = datetime.now()
      social_profile.save()
      self.processing_profiles[email] = str(social_profile['_id'])

      self.forward_email(social_profile)
      job.delete()

  def forward_email(self, social_profile):
    for key in scavengers_dict:
      self.email_beanstalk.use(key + '_in')
      self.email_beanstalk.put(str(social_profile['email']))

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

    profile_id = self.processing_profiles[str(response_object['email'])]
    social_profile = self.profiles.find_one({'_id': ObjectId(profile_id)})

    status = network_type + '_status'
    link = network_type + '_link'
    parsed = network_type + '_parsed'

    social_profile[status] = int(response_object['status'])
    if social_profile[status] >= 400:
      social_profile[link] = unicode("")
    else:
      social_profile[link] = unicode(response_object['profiles'][0])
    social_profile[parsed] = response_object

    if int(response_object['status']) < 400:
      if 'username' in response_object and len(response_object['username']):
        social_profile['username'] = (unicode(response_object['username']))
      if 'display_name' in response_object and \
                                          len(response_object['display_name']):
        social_profile['display_name'] = unicode(response_object['display_name'])
      if 'age' in response_object and len(response_object['age']):
        ages = list(social_profile['age'])
        ages.append(int(response_object['age']))
        sorted(ages)
        start = ages[0]
        end = ages[-1]
        social_profile['age'] = [start, end]
      if 'location' in response_object and len(response_object['location']):
        social_profile['location'] = unicode(response_object['location'])
      if 'gender' in response_object and len(response_object['gender']):
        social_profile['gender'] = unicode(response_object['gender'])
      if 'profiles' in response_object:
        for profile in response_object['profiles']:
          if len(profile):
            social_profile['profiles'].append(unicode(profile))

    social_profile['time'] = datetime.now()
    self.profiles.save(social_profile)

    self.test_profile_completion(social_profile)

  def test_profile_completion(self, social_profile):
    profile_complete = True
    for key in scavengers_dict:
      status = key + '_status'
      if social_profile[status] == 0:
        profile_complete = False
        break

    if profile_complete is True:
      # send package on mini-router's username_queue
      package = {}
      package['email'] = str(social_profile['email'])
      package['id'] = str(social_profile['_id'])
      package['collection'] = MONGO_COLLECTION

      # send a package for every found username in certain network
      for network_type in scavengers_dict:
        parsed = network_type + '_parsed'
        response_object = social_profile[parsed]
        if 'username' in response_object and len(response_object['username']):
          package['username'] = response_object['username']
          self.username_beanstalk.put(simplejson.dumps(package))

      del self.processing_profiles[str(social_profile['email'])]

if __name__=="__main__":
  r = Router()
  r.run()
