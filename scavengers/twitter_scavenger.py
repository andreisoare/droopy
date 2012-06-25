# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)
#
# This scavenger gets information about a user from Twitter based on username.

import simplejson
import urllib
from bson.objectid import ObjectId

from bs4 import BeautifulSoup
from scavenger import Scavenger
from response import Response
from scavenger_utils import http_request, process_profiles
from base.mongodb_utils import get_mongo_collection

TWITTER = 'twitter'
TWITTER_HOST = 'twitter.com'

class TwitterScavenger(Scavenger):
  def __init__(self, proc_id, in_tube, out_tube):
    super(TwitterScavenger, self).__init__(proc_id, in_tube, out_tube)

  def process_job(self, job):
    info = simplejson.loads(job.body)
    email = info['email']
    username = info['username']
    response = self._twitter(username, email)
    if response.is_error():
      return 'not'

    profiles = get_mongo_collection(info['collection'])
    location = 'network_candidates.' + TWITTER
    profiles.find_and_modify({'_id' : ObjectId(info['id'])},
      {'$push' : {location : response}})

    return 'ok'

  def _twitter(self, username, email):
    params = {}
    response = http_request(email, 'GET',
                          TWITTER_HOST, "/%s" % urllib.quote(username), params)
    if response.is_error():
      return response

    return TwitterResponse(response, username)

class TwitterResponse(Response):
  def __init__(self, response, username):
    super(TwitterResponse, self).__init__(response['status'],
                          response['raw_data'], response['email'])
    data = BeautifulSoup(response['raw_data'])

    self['username'] = username
    profiles = [TWITTER_HOST + "/" + username]
    profile = data.find(id='profile')
    if profile:
      for x in profile.address.ul.find_all('li'):
        spans = x.find_all('span')
        if not len(spans):
          continue
        if spans[0].string == 'Name':
          self['display_name'] = spans[1].string
        elif spans[0].string == 'Location':
          self['location'] = spans[1].string
        elif spans[0].string == 'Web':
          profiles.append(x.a.get('href'))

    if profiles:
      response = process_profiles(profiles)
      self['profiles'] = profiles
      if response:
        self.enhance_response(response)

