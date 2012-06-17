# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)
#
# This scavenger gets information about a user from Linkedin based on username.

import simplejson
import urllib
from pymongo.objectid import ObjectId

from bs4 import BeautifulSoup
from scavenger import Scavenger
from response import Response
from scavenger_utils import http_request, format_url
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
    profile = profiles.find_one({"_id" : ObjectId(info['id'])})
    try:
      profile['network_candidates'][LINKEDIN].append(response)
    except:
      profile['network_candidates'][LINKEDIN] = [response]
    profiles.save(profile)

    #TODO(diana) what to return
    return 'ok'
    return simplejson.dumps({
                              'type' : LINKEDIN,
                              'response' : response
                            })

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

    name = data.find(id="name")
    given_name = name.find('span', {'class' : "given-name"}).get_text()
    family_name = name.find('span', {'class' : "family-name"}).get_text()
    self['display_name'] = "%s %s" % (given_name, family_name)

    headline = data.find(id="headline")
    self['location'] = \
                headline.find('span', {'class' : 'locality'}).get_text().strip()

    other_profiles = [LINKEDIN_HOST + "/" + username]
    for profile_url in other_profiles:
      self['profiles'].append(format_url(profile_url))

    self['username'] = username
