# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)
#
# This scavenger gets information about a user from LastFm based on username.

import simplejson
import urllib
from bson.objectid import ObjectId

from scavenger import Scavenger
from scavenger_config import LASTFM_KEY
from response import Response
from scavenger_utils import http_request, NOT_FOUND_ERROR_CODE, process_profiles
from base.mongodb_utils import get_mongo_collection

LASTFM = "lastfm"
LASTFM_HOST = 'ws.audioscrobbler.com'
LASTFM_PATH = '/2.0/'

class LastfmScavenger(Scavenger):
  def __init__(self, proc_id, in_tube, out_tube):
    super(LastfmScavenger, self).__init__(proc_id, in_tube, out_tube)

  def process_job(self, job):
    info = simplejson.loads(job.body)
    email = info['email']
    username = info['username']
    response = self._lastfm(username, email)
    if response.is_error():
      return 'not'

    profiles = get_mongo_collection(info['collection'])
    location = 'network_candidates.' + LASTFM
    profiles.find_and_modify({'_id' : ObjectId(info['id'])},
      {'$push' : {location : response}})

    return 'ok'

  def _lastfm(self, username, email):
    params = {
                "method" : "user.getinfo",
                "user" : urllib.quote(username),
                "api_key" :  LASTFM_KEY,
                "format" : "json"
             }

    response = http_request(email, 'GET', LASTFM_HOST, LASTFM_PATH, params)
    if response.is_error():
      return response

    message = response['raw_data']
    data = simplejson.loads(message)

    if 'error' in data:
      response['status'] = NOT_FOUND_ERROR_CODE
      return response

    return LastfmResponse(response)

class LastfmResponse(Response):
  def __init__(self, response):
    super(LastfmResponse, self).__init__(response['status'],
                          response['raw_data'], response['email'])
    info = simplejson.loads(response['raw_data'])['user']
    profiles = []

    if 'realname' in info and info['realname']:
      self['display_name'] = info['realname']
    if 'name' in info and info['name']:
      self['username'] = info['name']
    if 'country' in info and info['country']:
      self['location'] = info['country']
    if 'age' in info and info['age']:
      self['age'] = info['age']
    if 'gender' in info and info['gender']:
      self['gender'] = info['gender']
    if 'url' in info and info['url']:
      profiles = [info['url']]

    if profiles:
      response = process_profiles(profiles)
      self['profiles'] = profiles
      if response:
        self.enhance_response(response)

