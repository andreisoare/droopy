# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: tabara.mihai@gmail.com (Mihai Tabara)
#         diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)

import beanstalkc
import time
import thread
import simplejson
import logging
from datetime import datetime
from bson.objectid import ObjectId
from pattern_generator import PatternGenerator

import global_settings
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

TIME_SLEEP = 7.5

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
      logging.info('================ Got email %s =================\n' % email)
      social_profile = self.profiles.SocialProfile()
      social_profile['email'] = unicode(email)
      social_profile['time'] = datetime.now()
      social_profile.save()
      self.processing_profiles[email] = str(social_profile['_id'])

      self.forward_email(social_profile)
      job.delete()
      time.sleep(TIME_SLEEP)

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
    response = queue_response['response']
    network_type = queue_response['type']

    logging.info('Got response from %s (%s)' %\
          (network_type, response['email']))

    profile_id = ObjectId(self.processing_profiles[str(response['email'])])

    status = network_type + '_status'
    link = network_type + '_link'
    parsed = network_type + '_parsed'

    try:
      self.profiles.find_and_modify({'_id' : profile_id},
        {'$set' : {status : int(response['status'])}})
      if response['status'] >= 400:
        self.profiles.find_and_modify({'_id' : profile_id},
          {'$set' : {link : unicode('')}})
      else:
        self.profiles.find_and_modify({'_id' : profile_id},
          {'$set' : {link : unicode(response['profiles'][0])}})
      self.profiles.find_and_modify({'_id' : profile_id},
        {'$set' : {parsed: response}})

      if int(response['status']) < 400:
        if 'username' in response and len(response['username']):
          self.profiles.find_and_modify({'_id' : profile_id},
            {'$set' : {'username' : unicode(response['username'])}})
        if 'display_name' in response and \
                                            len(response['display_name']):
          self.profiles.find_and_modify({'_id' : profile_id},
            {'$set' : {'display_name' : unicode(response['display_name'])}})
        if 'age' in response and len(response['age']):
          ages = list(self.profiles.find_one({'_id' : profile_id})['age'])
          ages.append(int(response['age']))
          sorted(ages)
          start = ages[0]
          end = ages[-1]
          self.profiles.find_and_modify({'_id' : profile_id},
            {'$set' : {'age' : [start, end]}})
        if 'location' in response and len(response['location']):
          self.profiles.find_and_modify({'_id' : profile_id},
            {'$set' : {'location' : unicode(response['location'])}})
        if 'gender' in response and len(response['gender']):
          self.profiles.find_and_modify({'_id' : profile_id},
            {'$set' : {'gender' : unicode(response['gender'])}})
        if 'profiles' in response:
          for profile in response['profiles']:
            if len(profile):
              self.profiles.find_and_modify({'_id' : profile_id},
                {'$push' : {'profiles' : unicode(profile)}})
      self.profiles.find_and_modify({'_id' : profile_id},
        {'$set' : {'time' : datetime.now()}})
    except:
      logging.warn('Got a problem  when saving response %s' % response)


    logging.info('Finished processing response from %s (%s)' %\
          (network_type, response['email']))
    self.test_profile_completion(profile_id)

  def test_profile_completion(self, profile_id):
    social_profile = self.profiles.find_one({'_id': profile_id})
    profile_complete = True
    for key in scavengers_dict:
      status = key + '_status'
      if social_profile[status] == 0:
        profile_complete = False
        break

    if profile_complete is True:
      logging.info('+++++++++++++++ Finished with email %s +++++++++++++++\n' %\
              social_profile['email'])

      # delete duplicates from profiles list
      current_profiles = social_profile['profiles']
      current_profiles = list(set(current_profiles))
      self.profiles.find_and_modify({'_id' : profile_id},
              {'$set' : {'profiles' : current_profiles}})

      # delete job from router's currently processing list
      del self.processing_profiles[str(social_profile['email'])]

      # prepare package for sending on mini-router's username_queue
      package = {}
      package['email'] = str(social_profile['email'])
      package['id'] = str(social_profile['_id'])
      package['collection'] = MONGO_COLLECTION

      # gather the current usernames found
      found_usernames = []
      for network_type in scavengers_dict:
        parsed = network_type + '_parsed'
        response_object = social_profile[parsed]
        if 'username' in response_object and len(response_object['username']) \
          and response_object['username'] not in found_usernames:
          try:
            found_usernames.append(response_object['username'].encode('ascii',
                                              'ignore'))
          except:
            logging.warn('Got a problem when encoding username %s' %
                                                  response_object['username'])
            found_usernames.append(response_object['username'])

      # generate if necessary and complete the username's list
      dn = ''
      if 'display_name' in social_profile and social_profile['display_name']:
        dn = social_profile['display_name']
      todo_usernames = PatternGenerator.generate (
                                str(social_profile['email']),\
                              #  social_profile['display_name'],\
                                dn,\
                                found_usernames\
                                                  )
      logging.info('Email: %s -> list of usernames sent to minirouter: %s' % ( \
                          str(social_profile['email']),\
                          str(todo_usernames))\
                  )

      # send a package for every username
      for username in todo_usernames:
        package['username'] = str(unicode(username, errors='ignore'))
        self.username_beanstalk.put(simplejson.dumps(package))

if __name__=="__main__":
  r = Router()
  r.run()
