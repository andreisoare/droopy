# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)
#
# This scavenger gets information about a user from AboutMe based on username.

import simplejson
import urllib
from pymongo.objectid import ObjectId

from bs4 import BeautifulSoup
from scavenger import Scavenger
from response import Response
from scavenger_utils import http_request
from base.mongodb_utils import get_mongo_collection

#TODO(diana) check for facebook, twitter etc buttons

ABOUTME = 'aboutme'
ABOUTME_HOST = 'about.me'

class AboutmeScavenger(Scavenger):
  def __init__(self, proc_id, in_tube, out_tube):
    super(AboutmeScavenger, self).__init__(proc_id, in_tube, out_tube)
    self.profiles = get_mongo_collection()

  def process_job(self, job):
    info = simplejson.loads(job.body)
    email = info['email']
    username = info['username']
    response = self._aboutme(username, email)

    profile = self.profiles.find_one({"_id" : ObjectId(info['id'])})
    try:
      profile['network_candidates'][ABOUTME].append(response)
    except:
      profile['network_candidates'][ABOUTME] = [response]
    self.profiles.save(profile)

    #TODO(diana) what to return
    return ''
    return simplejson.dumps({
                              'type' : ABOUTME,
                              'response' : response
                            })

  def _aboutme(self, username, email):
    params = {}
    response = http_request(email, 'GET',
                          ABOUTME_HOST, "/%s" % urllib.quote(username), params)
    if response.is_error():
      return response

    return AboutmeResponse(response, username)

class AboutmeResponse(Response):
  def __init__(self, response, username):
    super(AboutmeResponse, self).__init__(response['status'],
                          response['raw_data'], response['email'])
    data = BeautifulSoup(response['raw_data'])
    self['profiles'] = [ABOUTME_HOST + "/" + username]
    self['username'] = username
    self['display_name'] = data.find(id='profile_box').div.h1.string
