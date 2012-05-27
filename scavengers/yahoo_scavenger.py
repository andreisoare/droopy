# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: tabara.mihai@gmail.com (Mihai Tabara)

import yql
import simplejson

from response import Response
from scavenger import Scavenger
from scavenger_config import YAHOO_KEY, YAHOO_PWD
from scavenger_utils import NOT_FOUND_ERROR_CODE, OK_CODE

YAHOO = "yahoo"

class YahooScavenger(Scavenger):
  def __init__(self, proc_id, in_tube, out_tube):
    super(YahooScavenger, self).__init__(proc_id, in_tube, out_tube)

  def process_job(self, job):
    email = job.body
    response = self._yahoo(email)
    return simplejson.dumps({
                              'type' : YAHOO,
                              'response' : response
                            })

  def _yahoo(self, email):
    username = email[0:email.find('@')]

    y = yql.TwoLegged(YAHOO_KEY, YAHOO_PWD)
    yql_object = y.execute("select * from social.profile where guid in \
                          (select guid from yahoo.identity \
                          where yid='%s')" % username)

    if yql_object.count == None:
      return Response(NOT_FOUND_ERROR_CODE, '', email)

    return YahooResponse(Response(OK_CODE, yql_object.one(), email))

class YahooResponse(Response):
  def __init__(self, response):
    super(YahooResponse, self).__init__(response['status'],
                                        response['raw_data'],
                                        response['email'])

    data = response['raw_data']

    # TODO(mihai): Add a proper method to validate yahoo addresses
    self['username'] = response['email'][0:response['email'].find('@')]
    if 'location' in data:
      self['location'] = data['location']
    if 'gender' in data:
      self['gender'] = data['gender']
    if 'displayAge' in data:
      self['age'] = data['displayAge']
    if 'profileUrl' in data:
      self['profiles'] = [data['profileUrl']]

    display_name = None
    if 'nickname' in data:
      display_name = data['nickname']
    if 'familyName' in data and 'givenName' in data:
      display_name = ' '.join([data['familyName'], data['givenName']])

    if display_name is not None:
      self['display_name'] = display_name

