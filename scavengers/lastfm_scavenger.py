# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)
#
# This scavenger gets information about a user from LastFm based on username.

import simplejson
import urllib
from pymongo.objectid import ObjectId

from scavenger import Scavenger
from scavenger_config import LASTFM_KEY
from response import Response
from scavenger_utils import http_request, NOT_FOUND_ERROR_CODE, format_url
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
    profile = profiles.find_one({"_id" : ObjectId(info['id'])})
    try:
      profile['network_candidates'][LASTFM].append(response)
    except:
      profile['network_candidates'][LASTFM] = [response]
    profiles.save(profile)

    #TODO(diana) what to return
    return 'ok'
    return simplejson.dumps({
                              'type' : LASTFM,
                              'response' : response
                            })

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
    self['display_name'] = info['realname']
    self['location'] = info['country']
    self['age'] = info['age']
    self['gender'] = info['gender']
    self['profiles'] = [format_url(info['url'])]
    self['username'] = info['name']

