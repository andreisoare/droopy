# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)
#
# This scavenger gets information about a user from MySpace.

import simplejson
import logging

import global_settings
from scavenger import Scavenger
from response import Response
from scavenger_utils import http_request, process_profiles

MYSPACE = "myspace"
MYSPACE_HOST = "api.myspace.com"
MYSPACE_PATH = "/opensearch/people/"

class MyspaceScavenger(Scavenger):
  def __init__(self, proc_id, in_tube, out_tube):
    super(MyspaceScavenger, self).__init__(proc_id, in_tube, out_tube)

  def process_job(self, job):
    email = job.body
    logging.info('%s got email %s' % (MYSPACE, email))
    response = self._myspace(email)
    logging.info('%s finished with email %s with status %s' %
          (MYSPACE, email, response['status']))
    return simplejson.dumps({
                              'type' : MYSPACE,
                              'response' : response
                            })

  def _myspace(self, email):
    params = {'searchTerms': email,
              'searchBy': 'email',
              'format': 'json'
              }
    response = http_request(email, "GET", MYSPACE_HOST, MYSPACE_PATH, params)

    if response.is_error():
      return response

    return MyspaceResponse(response)

class MyspaceResponse(Response):
  def __init__(self, response):
    super(MyspaceResponse, self).__init__(response['status'],
                          response['raw_data'], response['email'])
    # TODO(diana) check if profiles are given back
    data = simplejson.loads(self['raw_data'])
    info = data['entry'][0]
    profiles = []

    if 'displayName' in info and info['displayName']:
      self['display_name'] = info['displayName']
    if 'gender' in info and info['gender']:
      self['gender'] = info['gender']
    if 'age' in info and info['age']:
      self['age'] = info['age']
    if 'location' in info and info['location']:
      self['location'] = info['location']
    if 'profileUrl' in info and info['profileUrl']:
      profiles = [info['profileUrl']]

    if profiles:
      response = process_profiles(profiles)
      self['profiles'] = profiles
      if response:
        self.enhance_response(response)

