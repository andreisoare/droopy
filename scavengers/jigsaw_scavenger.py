# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: tabara.mihai@gmail.com (Mihai Tabara)

import simplejson
import httplib
import logging

import global_settings
from scavenger import Scavenger
from scavenger_config import JIGSAW_KEY
from scavenger_utils import http_request, NOT_FOUND_ERROR_CODE, process_profiles
from response import Response

JIGSAW = "jigsaw"
JIGSAW_HOST = "www.jigsaw.com"
JIGSAW_PATH = "/rest/searchContact.json"

class JigsawScavenger(Scavenger):
  def __init__(self, proc_id, in_tube, out_tube):
    super(JigsawScavenger, self).__init__(proc_id, in_tube, out_tube)

  def process_job(self, job):
    email = job.body
    logging.info('%s got email %s' % (JIGSAW, email))
    response = self._jigsaw(email)
    logging.info('%s finished with email %s with status %s' %
          (JIGSAW, email, response['status']))
    return simplejson.dumps({
                              'type' : JIGSAW,
                              'response' : response
                            })

  def _jigsaw(self, email):
    params = {"token": JIGSAW_KEY,
              "email": email,
              }

    response = http_request(email, "GET", JIGSAW_HOST, JIGSAW_PATH,
                            params, httplib.HTTPS_PORT)
    if response.is_error():
      return response

    message = response['raw_data']
    data = simplejson.loads(message)

    if data['totalHits'] == 0:
      response['status'] = NOT_FOUND_ERROR_CODE
      return response

    return JigsawResponse(response)

class JigsawResponse(Response):
  def __init__(self, response):
    super(JigsawResponse, self).__init__(response['status'],
                         response['raw_data'], response['email'])
    message = response['raw_data']
    info = simplejson.loads(message)['contacts'][0]
    profiles = []

    firstName = ''
    lastName = ''
    if 'firstname' in info and info['firstname']:
      firstName = info['firstname']
    if 'lastname' in info and info['lastname']:
      lastName = info['lastname']
    if firstName or lastName:
      self['display_name'] = ('%s %s' % (firstName, lastName)).strip()

    #TODO(diana) maybe add address?
    city = ''
    state = ''
    country = ''
    if 'city' in info and info['city']:
      city = info['city']
    if 'state' in info and info['state']:
      state = info['state']
    if 'country' in info and info['country']:
      country = info['country']
    if city or state or country:
      self['location'] = ('%s %s %s' % (city, state, country)).strip()

    if 'contactURL' in info and info['contactURL']:
      profiles = [info['contactURL']]

    if profiles:
      response = process_profiles(profiles)
      self['profiles'] = profiles
      if response:
        self.enhance_response(response)

