# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)

# This scavenger gets information about a user from Github.

# WARN (diana) This API is deprecated, I emailed the support to see if they will
# continue supporting it.

import simplejson
from xml.dom.minidom import parseString
from scavenger_utils import http_request

GITHUB_HOST = "github.com"
GITHUB_PATH = "/api/v2/xml/user/email/"


def getText(nodelist):
  rc = []
  for node in nodelist:
    if node.nodeType == node.TEXT_NODE:
      rc.append(node.data)
  return ''.join(rc)

def github(email):
  response = http_request(email, "GET", GITHUB_HOST,
             "%s%s" % (GITHUB_PATH, email), {})

  if response.is_error():
    return response

# Info: name, company, location, blog, login/username
  print response['raw_data']
# TODO(diana) parse to json
  dom = parseString(response['raw_data'])
  x = dom.getElementsByTagName("user")
  y = x[0].getElementsByTagName("name")
  print getText(y[0].childNodes)
  return dom

if __name__=="__main__":
  print github("andrei.soare@gmail.com")
