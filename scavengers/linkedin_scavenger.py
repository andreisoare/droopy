# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)
#
# This scavenger gets information about a user from Linkedin based on username.

import simplejson
import urllib
from bson.objectid import ObjectId

from bs4 import BeautifulSoup
from scavenger import Scavenger
from response import Response
from scavenger_utils import http_request, process_profiles
from base.mongodb_utils import get_mongo_collection

LINKEDIN = 'linkedin'
LINKEDIN_HOST = 'www.linkedin.com'
LINKEDIN_PATH = "/in/"

class LinkedinScavenger(Scavenger):
  def __init__(self, proc_id, in_tube, out_tube):
    super(LinkedinScavenger, self).__init__(proc_id, in_tube, out_tube)

  def process_job(self, job):
    info = simplejson.loads(job.body)
    email = info['email']
    username = info['username']
    response = self._linkedin(username, email)
    if response.is_error():
      return 'not'

    profiles = get_mongo_collection(info['collection'])
    location = 'network_candidates.' + LINKEDIN
    profiles.find_and_modify({'_id' : ObjectId(info['id'])},
      {'$push' : {location : response}})

    return 'ok'

  def _linkedin(self, username, email):
    params = {}
    response = http_request(email, 'GET',
        LINKEDIN_HOST, "%s%s" % (LINKEDIN_PATH, urllib.quote(username)), params)
    if response.is_error():
      return response

    return LinkedinResponse(response, username)

class LinkedinResponse(Response):
  def __init__(self, response, username):
    super(LinkedinResponse, self).__init__(response['status'],
                          response['raw_data'], response['email'])
    data = BeautifulSoup(response['raw_data'])

    profiles = [LINKEDIN_HOST + LINKEDIN_PATH + username]
    self['username'] = username

    name = data.find(id="name")
    if name:
      try:
        family_name = name.find('span', {'class' : "family-name"}).get_text()
      except:
        family_name = ''
      try:
        given_name = name.find('span', {'class' : "given-name"}).get_text()
      except:
        given_name = ''

      if given_name or family_name:
        self['display_name'] = ("%s %s" % (given_name, family_name)).strip()

    headline = data.find(id="headline")
    if headline:
      try:
        self['location'] = \
                headline.find('span', {'class' : 'locality'}).get_text().strip()
      except:
        pass

    if profiles:
      response = process_profiles(profiles)
      self['profiles'] = profiles
      if response:
        self.enhance_response(response)

