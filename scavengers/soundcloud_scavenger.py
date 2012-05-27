# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)
#
# This scavenger gets information about a user from soundcloud based on username.

import simplejson
import urllib
from pymongo.objectid import ObjectId

from scavenger import Scavenger
from scavenger_config import SOUNDCLOUD_KEY
from response import Response
from scavenger_utils import http_request, NOT_FOUND_ERROR_CODE
from base.mongodb_utils import get_mongo_collection

SOUNDCLOUD = 'soundcloud'
SOUNDCLOUD_HOST = 'api.soundcloud.com'
SOUNDCLOUD_PATH = '/users.json'
SOUNDCLOUD_LIMIT = 10

class SoundcloudScavenger(Scavenger):
  def __init__(self, proc_id, in_tube, out_tube):
    super(SoundcloudScavenger, self).__init__(proc_id, in_tube, out_tube)

  def process_job(self, job):
    info = simplejson.loads(job.body)
    email = info['email']
    username = info['username']
    response = self._soundcloud(username, email)
    if response.is_error():
      return 'not'

    profiles = get_mongo_collection(info['collection'])
    profile = profiles.find_one({"_id" : ObjectId(info['id'])})
    try:
      profile['network_candidates'][SOUNDCLOUD].append(response)
    except:
      profile['network_candidates'][SOUNDCLOUD] = [response]
    profiles.save(profile)

    #TODO(diana) what to return
    return 'ok'
    return simplejson.dumps({
                              'type' : SOUNDCLOUD,
                              'response' : response
                            })

  def _soundcloud(self, username, email):
    params = {
                "client_id" : SOUNDCLOUD_KEY,
                "q" : urllib.quote(username),
                "limit" : SOUNDCLOUD_LIMIT
             }

    response = http_request(email, 'GET', SOUNDCLOUD_HOST, \
                                         SOUNDCLOUD_PATH, params)
    if response.is_error():
      return response

    message = response['raw_data']
    data = simplejson.loads(message)

    if len(data) == 0:
      response['status'] = NOT_FOUND_ERROR_CODE
      return response

    return SoundcloudResponse(response, username)

class SoundcloudResponse(Response):
  def __init__(self, response, username):
    super(SoundcloudResponse, self).__init__(response['status'],
                          response['raw_data'], response['email'])

    users_list = simplejson.loads(response['raw_data'])
    found = False
    for info in users_list:
      if info['permalink'] != username:
        continue

      found = True
      self['username'] = username
      self['raw_data'] = info
      self['display_name'] = info['full_name']
      self['location'] = "%s %s" % (info['city'], info['country'])
      self['profiles'] = [info['permalink_url']]
      if info['website']:
        self['profiles'].append(info['website'])
      break

    if not found:
      self['status'] = NOT_FOUND_ERROR_CODE

