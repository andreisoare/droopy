# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)
#
# This scavenger gets information about a user from AboutMe based on username.

import simplejson
import urllib
from bson.objectid import ObjectId

from bs4 import BeautifulSoup
from scavenger import Scavenger
from response import Response
from scavenger_utils import http_request, NOT_FOUND_ERROR_CODE, process_profiles
from base.mongodb_utils import get_mongo_collection

#TODO(diana) check if there are more buttons in CONTENT

ABOUTME = 'aboutme'
ABOUTME_HOST = 'about.me'
ABOUTME_CONTENT = ['twitter', 'facebook', 'googleplus', 'linkedin', 'tumblr',
                    'foursquare', 'wordpress', 'flickr', 'vimeo', 'youtube']

class AboutmeScavenger(Scavenger):
  def __init__(self, proc_id, in_tube, out_tube):
    super(AboutmeScavenger, self).__init__(proc_id, in_tube, out_tube)

  def process_job(self, job):
    info = simplejson.loads(job.body)
    email = info['email']
    username = info['username']
    response = self._aboutme(username, email)
    if response.is_error():
      return 'not'

    profiles = get_mongo_collection(info['collection'])
    location = 'network_candidates.' + ABOUTME
    profiles.find_and_modify({'_id' : ObjectId(info['id'])},
      {'$push' : {location : response}})

    return 'ok'

  def _aboutme(self, username, email):
    params = {}
    response = http_request(email, 'GET',
                          ABOUTME_HOST, "/%s" % urllib.quote(username), params)
    if '302 Found' in response['raw_data']:
      response['status'] = NOT_FOUND_ERROR_CODE
      return response

    return AboutmeResponse(response, username)

class AboutmeResponse(Response):
  def __init__(self, response, username):
    super(AboutmeResponse, self).__init__(response['status'],
                          response['raw_data'], response['email'])
    data = BeautifulSoup(response['raw_data'])

    profiles = [ABOUTME_HOST + "/" + username]
    self['username'] = username

    profile_box = data.find(id='profile_box')
    if profile_box:
      try:
        if profile_box.div.h1.string:
          self['display_name'] = profile_box.div.h1.string
      except:
        pass

    for website in data.find_all('a', {'class': 'website'}):
      profiles.append(website.get('href'))

    for content in ABOUTME_CONTENT:
      content_response = http_request(self['email'], 'GET', ABOUTME_HOST,
                      "/content/%s/%s" % (urllib.quote(username), content), {})
      data = BeautifulSoup(content_response['raw_data'])
      body = data.find('body', {'class':'aboutmeapp'})
      try:
        profile = body.find('div', {'class':'top_section'}).h1.a.get('href')
        if profile:
          profiles.append(profile)
      except:
        pass

    if profiles:
      response = process_profiles(profiles)
      self['profiles'] = profiles
      if response:
        self.enhance_response(response)

