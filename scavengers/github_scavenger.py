# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)
#
# This scavenger gets information about a user from Github.
#
# WARN (diana) This API is deprecated. Migrate to v3 when it will support
# search by email.

import simplejson
from scavenger import Scavenger
from response import Response
from scavenger_utils import http_request
from xml.dom import minidom

GITHUB_HOST = "github.com"
GITHUB_PATH = "/api/v2/xml/user/email/"

class GithubScavenger(Scavenger):
  def __init__(self, proc_id, in_tube, out_tube):
    super(GithubScavenger, self).__init__(proc_id, in_tube, out_tube)

  def process_job(self, job):
    email = job.body
    response = self._github(email)
    return simplejson.dumps(response)

  def _github(self, email):
    response = http_request(email, "GET", GITHUB_HOST,
               "%s%s" % (GITHUB_PATH, email), {})

    if response.is_error():
      return response

    return GithubResponse(response)

class GithubResponse(Response):
  def __init__(self, response):
    super(GithubResponse, self).__init__(response['status'],
                          response['raw_data'], response['email'])
    dom = minidom.parseString(self['raw_data'])
    info = dom.getElementsByTagName("user")[0]
    self['display_name'] = self._get_info(info, "name")
    self['location'] = self._get_info(info, "location")
    self['profiles'] = self._get_info(info, "blog")
    self['username'] = self._get_info(info, "login")

  def _get_info(self, info, parameter):
    elem = info.getElementsByTagName(parameter)[0]
    return self._get_text(elem.childNodes)

  def _get_text(self, nodelist):
    rc = []
    for node in nodelist:
      if node.nodeType == node.TEXT_NODE:
        rc.append(node.data)
    return ''.join(rc)
