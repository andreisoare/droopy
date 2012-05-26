# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)
#
# This scavenger gets information about a user from Pinterest based on username.

import simplejson
import urllib
from pymongo.objectid import ObjectId

from bs4 import BeautifulSoup
from scavenger import Scavenger
from response import Response
from scavenger_utils import http_request
from base.mongodb_utils import get_mongo_collection

PINTEREST = 'pinterest'
PINTEREST_HOST = 'pinterest.com'

class PinterestScavenger(Scavenger):
  def __init__(self, proc_id, in_tube, out_tube):
    super(PinterestScavenger, self).__init__(proc_id, in_tube, out_tube)
    self.profiles = get_mongo_collection()

  def process_job(self, job):
    info = simplejson.loads(job.body)
    email = info['email']
    username = info['username']
    response = self._pinterest(username, email)

    profile = self.profiles.find_one({"_id" : ObjectId(info['id'])})
    try:
      profile['network_candidates'][PINTEREST].append(response)
    except:
      profile['network_candidates'][PINTEREST] = [response]
    self.profiles.save(profile)

    #TODO(diana) what to return
    return ''
    return simplejson.dumps({
                              'type' : PINTEREST,
                              'response' : response
                            })

  def _pinterest(self, username, email):
    params = {}
    response = http_request(email, 'GET',
                        PINTEREST_HOST, "/%s/" % urllib.quote(username), params)
    if response.is_error():
      return response

    return PinterestResponse(response, username)

class PinterestResponse(Response):
  def __init__(self, response, username):
    super(PinterestResponse, self).__init__(response['status'],
                          response['raw_data'], response['email'])
    data = BeautifulSoup(response['raw_data'])
    self['username'] = username
    self['display_name'] = data.find(id='ProfileHeader').h1.string
    self['profiles'] = ["%s/%s/" % (PINTEREST_HOST, username)]
    profiles = data.find(id='ProfileLinks')
    for elem in profiles.find_all('li'):
      try:
        self['profiles'].append(elem.a.get('href'))
      except:
        if elem.get('id') == 'ProfileLocation':
          self['location'] = elem.get_text().strip()

