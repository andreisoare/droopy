# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: tabara.mihai@gmail.com (Mihai Tabara)

import simplejson
import urllib
from scavengers.scavenger_utils import http_request, NOT_FOUND_ERROR_CODE
from scavengers.scavenger_utils import OK_CODE

#TODO(diana) file no longer needed

class NetworkScouterScavenger:
  def __init__(self, email, username):
    self.email = email
    self.username = username
    self.networks_dict = {
                            'lastfm' : self.lastfm_scavenger,
                            'soundcloud' : self.soundcloud_scavenger,
                            'twitter' : self.twitter_scavenger,
                            'aboutme' : self.aboutme_scavenger,
                            'pinterest' : self.pinterest_scavenger,
                         }

  def run(self):
    d = {}
    for key in self.networks_dict:
      answer = self.networks_dict[key]()
      d[key] = answer
    return d

  def lastfm_scavenger(self):
    LASTFM_KEY = 'e5c40cb75a092823db9378c1437c3ec0'
    LASTFM_HOST = 'ws.audioscrobbler.com'
    LASTFM_PATH = '/2.0/'

    params = {
                "method" : "user.getinfo",
                "user" : urllib.quote(self.username),
                "api_key" :  LASTFM_KEY,
                "format" : "json"
             }

    response = http_request(self.email, 'GET', LASTFM_HOST, LASTFM_PATH, params)
    if response.is_error():
      return False

    message = response['raw_data']
    data = simplejson.loads(message)

    if 'error' in data:
      response['status'] = NOT_FOUND_ERROR_CODE

    return True if response['status'] < 400 else False

  def soundcloud_scavenger(self):
    SOUNDCLOUD_KEY = 'ef463fabfe015083c72515e72bde117f'
    SOUNDCLOUD_HOST = 'api.soundcloud.com'
    SOUNDCLOUD_PATH = '/users.json'
    SOUNDCLOUD_LIMIT = 10

    params = {
                "client_id" : SOUNDCLOUD_KEY,
                "q" : urllib.quote(self.username),
                "limit" : SOUNDCLOUD_LIMIT
             }

    response = http_request(self.email, 'GET', SOUNDCLOUD_HOST, \
                                         SOUNDCLOUD_PATH, params)
    if response.is_error():
      return False

    message = response['raw_data']
    data = simplejson.loads(message)

    if len(data) == 0:
      response['status'] = NOT_FOUND_ERROR_CODE

    return True if response['status'] < 400 else False

  def twitter_scavenger(self):
    TWIITER_HOST = 'twitter.com'
    TWITTER_PATH = '/%s' % (urllib.quote(self.username))
    params = {}
    response = http_request(self.email, 'HEAD', TWIITER_HOST, TWITTER_PATH, params)

    return False if response.is_error() else True

  def aboutme_scavenger(self):
    ABOUTME_HOST = 'about.me'
    ABOUTME_PATH = '/%s' % (urllib.quote(self.username))
    params = {}
    response = http_request(self.email, 'GET', ABOUTME_HOST, ABOUTME_PATH, params)

    if response['status'] != OK_CODE:
      return False
    print response['raw_data']
    return True

  def pinterest_scavenger(self):
    PIN_HOST = 'pinterest.com'
    PIN_PATH = '/%s/' % (urllib.quote(self.username))
    params = {}
    response = http_request(self.email, 'GET', PIN_HOST, PIN_PATH, params)

    if response['status'] != OK_CODE:
      return False

    print response['raw_data']
    return True

if __name__=="__main__":
  email = 'camp101988@yahoo.com'
  username = '__mihaitabara__'

  ns = NetworkScouterScavenger(email, 'dianatiriplica')
  d = ns.run()
#  for key, value in d.items():
#    print key, value
