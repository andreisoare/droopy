# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: tabara.mihai@gmail.com (Mihai Tabara)

import yql
from scavenger import Scavenger
from scavenger_utils import NOT_FOUND_ERROR_MESSAGE, OK_CODE

YAHOO_KEY = "dj0yJmk9WHBlY2dOVGNjdmtMJmQ9WVdrOVQyUmFPWE5TTm5FbWNHbzl" \
              "NVFl5TlRnNE9EUTJNZy0tJnM9Y29uc3VtZXJzZWNyZXQmeD0wNg--"
YAHOO_PWD = '4e76035fb8fc87922616b04917e2cafeda0b3c0a'

class YahooScavenger(Scavenger):
  def __init__(self, proc_id, in_tube, out_tube):
    super(YahooScavenger, self).__init__(proc_id, in_tube, out_tube)

  def process_job(self, job):
    email = job.body
    response = self._yahoo(email)
    return simplejson.dumps(response)

  def _yahoo(self, email):
    # TODO(mihai): Add a proper method to validate yahoo addresses
    username = email[0:email.find('@')]

    y = yql.TwoLegged(CONSUMER_KEY, CONSUMER_SECRET)
    yql_object = y.execute("select * from social.profile where guid in \
                          (select guid from yahoo.identity \
                          where yid='%s')" % username)

    if yql_object.count == None:
      return Response(NOT_FOUND_ERROR_MESSAGE, '', email)

    return YahooResponse(Response(OK_CODE, yql_object.one(), email))

class YahooResponse(Response):
  def __init__(self, response):
    super(YahooResponse, self).__init__(response['status'],
                        response['raw_data'], response['email'])

    # TODO(mihai): Add a proper method to validate yahoo addresses
    self['username'] = email[0:email.find('@')]

    data = response['raw_data']

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

