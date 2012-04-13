# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: tabara.mihai@gmail.com (Mihai Tabara)
#         diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)

import beanstalkc
import thread
import simplejson

from networks_scouter import NetworkScouterScavenger
from datetime import datetime
from base.mongodb_utils import get_mongo_connection
from mongodb.models import SocialProfile
from scavengers import FlickrScavenger, GithubScavenger, GooglePlusScavenger, \
          JigsawScavenger, MyspaceScavenger, YahooScavenger, FoursquareScavenger

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

class Router:
  def __init__(self):
    self.scavengers = []
    self.processing_profiles = {}
    self.email_beanstalk = beanstalkc.Connection()
    self.response_beanstalk = beanstalkc.Connection()

    self.response_beanstalk.watch(RESPONSE_QUEUE)
    thread.start_new_thread(self.watch_responses, ())

    conn = get_mongo_connection()
    self.profiles = conn.droopy.profiles

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
      self.processing_profiles[email] = social_profile
      social_profile.email = unicode(email)
      social_profile.time = datetime.now()
      social_profile.save()

      self.forward_email(social_profile)
      job.delete()

  def forward_email(self, social_profile):
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

    social_profile = self.processing_profiles[str(response_object['email'])]

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
        social_profile.username = unicode(response_object['username'])
      if 'display_name' in response_object and \
                                          len(response_object['display_name']):
        social_profile.display_name = unicode(response_object['display_name'])
      if 'age' in response_object and len(response_object['age']):
        ages = list(social_profile.age)
        ages.append(int(response_object['age']))
        sorted(ages)
        start = ages[0]
        end = ages[-1]
        social_profile.age = [start, end]
      if 'location' in response_object and len(response_object['location']):
        social_profile.location = unicode(response_object['location'])
      if 'gender' in response_object and len(response_object['gender']):
        social_profile.gender = unicode(response_object['gender'])
      if 'profiles' in response_object:
        for profile in response_object['profiles']:
          social_profile.profiles.append(unicode(profile))

    social_profile.time = datetime.now()
    social_profile.save()

    self.test_profile_completion(social_profile)

  def test_profile_completion(self, social_profile):
    profile_complete = True
    for key in scavengers_dict:
      status = key + '_status'
      if social_profile[status] == 0:
        profile_complete = False
        break

    if profile_complete is True:
      del self.processing_profiles[str(social_profile.email)]
      self.test_usernames(social_profile)

  def test_usernames(self, social_profile):
    usernames = []
    for key in scavengers_dict:
      parsed = key + '_parsed'
      parsed_dict = social_profile[parsed]
      if 'username' in parsed_dict and \
              usernames.count(parsed_dict['username']) == 0:
        usernames.append(parsed_dict['username'])

    for username in usernames:
      ns = NetworkScouterScavenger(social_profile.email, username)
      response_dict = ns.run()

      for key, value in response_dict.items():
        if value is True:
          # add username to corresponding social network in social profile
          if key in social_profile.networks:
            social_profile.networks[key].append(username)
          else:
            social_profile.networks[key] = [username]

    social_profile.time = datetime.now()
    social_profile.save()

if __name__=="__main__":
  r = Router()
  r.run()
