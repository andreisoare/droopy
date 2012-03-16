# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)
#
# This scavenger gets the user id for the persons with gmail account from Picasa
# and returns information from their Google+ profiles.

import re
import simplejson
import httplib
from scavenger import Scavenger
from response import Response
from scavenger_utils import http_request

PICASA_HOST = "picasaweb.google.com"
GOOGLE_HOST = "www.googleapis.com"
GOOGLE_PLUS_PATH = "/plus/v1/people/"
GOOGLE_PLUS_KEY = "AIzaSyACfowiWrJPaxS5EFvI6-N07CjctMdIqhE"
INFO_MATCH = "var _user"

class GooglePlusScavenger(Scavenger):
  def __init__(self, proc_id, in_tube, out_tube):
    super(GooglePlusScavenger, self).__init__(proc_id, in_tube, out_tube)

  def process_job(self, job):
    email = job.body
    response = self._google_plus(email)
    return simplejson.dumps(response)

  def _google_plus(self, email):
    username = email[:email.find("@gmail.com")]
    response = http_request(email, "GET", PICASA_HOST, "/%s" % username, {})

    if response.is_error():
      return response
    user_id = self._get_user_id(response['raw_data'])

    params = {'key': GOOGLE_PLUS_KEY}
    response = http_request(email, "GET", GOOGLE_HOST,
      "%s%s" % (GOOGLE_PLUS_PATH, user_id), params, httplib.HTTPS_PORT)

    if response.is_error():
      return response

    return GooglePlusResponse(response)

  def _get_user_id(self, page):
    index = page.find(INFO_MATCH)
    start_info = page.find("{", index)
    end_info = page.find("};", index)
    info = page[start_info:end_info]
    match = re.search('name(\s)*:\'(\d)*\'', info)
    return match.group(0).split('\'')[1]

class GooglePlusResponse(Response):
  def __init__(self, response):
    super(GooglePlusResponse, self).__init__(response['status'],
                          response['raw_data'], response['email'])
    info = simplejson.loads(self['raw_data'])

    if info['name']['givenName'] == "" or info['name']['familyName'] == "":
      self['display_name'] = info['displayName']
    else:
      self['display_name'] = \
              "%s %s" % (info['name']['givenName'], info['name']['familyName'])
    self['gender'] = info['gender']

    info['profiles'] = []
    for url in info['urls']:
      if 'type' in url.keys():
        continue
      info['profiles'].append(url['value'])
