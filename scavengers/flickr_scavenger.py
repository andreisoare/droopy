# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: tabara.mihai@gmail.com (Mihai Tabara)

import simplejson
import logging

import global_settings
from scavenger import Scavenger
from scavenger_config import FLICKR_KEY, FLICKR_PWD
from scavenger_utils import http_request, NOT_FOUND_ERROR_CODE, process_profiles
from response import Response

FLICKR = 'flickr'
FLICKR_HOST = "api.flickr.com"
FLICKR_PATH = "/services/rest/"
RESPONSE_PREFIX_LENGTH = 14

class FlickrScavenger(Scavenger):
  def __init__(self, proc_id, in_tube, out_tube):
    super(FlickrScavenger, self).__init__(proc_id, in_tube, out_tube)

  def process_job(self, job):
    email = job.body
    logging.info('%s got email %s' % (FLICKR, email))
    response = self._flickr(email)
    logging.info('%s finished with email %s with status %s' %
          (FLICKR, email, response['status']))
    return simplejson.dumps({
                              'type' : FLICKR,
                              'response' : response
                            })

  def _flickr(self, email):
    queries = {"email": "flickr.people.findByEmail",
               "user": "flickr.people.getInfo"
               }

    params =  {"method": queries['email'],
               "api_key": FLICKR_KEY,
               "find_email": email,
               "format": "json"
               }

    response = http_request(email, "GET", FLICKR_HOST, FLICKR_PATH, params)
    if response.is_error():
     return response

    message = response['raw_data']
    # Jump over the first 14 characters and get the actual JSON
    message = message[RESPONSE_PREFIX_LENGTH:len(message)-1]
    data = simplejson.loads(message)

    if data['stat'] == 'fail':
      response['status'] = NOT_FOUND_ERROR_CODE
      return response

    user_id = data['user']['id']

    params['method'] = queries['user']
    params['user_id'] = str(user_id)
    del params['find_email']

    response = http_request(email, "GET", FLICKR_HOST, FLICKR_PATH, params)
    if response.is_error():
      return response

    return FlickrResponse(response)

class FlickrResponse(Response):
  def __init__(self, response):
    super(FlickrResponse, self).__init__(response['status'],
                         response['raw_data'], response['email'])
    message = response['raw_data']
    message = message[RESPONSE_PREFIX_LENGTH:len(message)-1]
    info = simplejson.loads(message)['person']
    profiles = []

    if 'username' in info and info['username']['_content']:
      self['username'] = info['username']['_content']
    if 'realname' in info and info['realname']['_content']:
      self['display_name'] = info['realname']['_content']
    if 'location' in info and info['location']['_content']:
      self['location'] = info['location']['_content']
    profiles = []
    if 'profileurl' in info and info['profileurl']['_content']:
      profiles = [info['profileurl']['_content']]

    if profiles:
      response = process_profiles(profiles)
      self['profiles'] = profiles
      if response:
        self.enhance_response(response)

