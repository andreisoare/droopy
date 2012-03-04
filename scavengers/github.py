# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)

# This scavenger gets information about a user from Github.

# WARN (diana) This API is deprecated, I emailed the support to see if they will
# continue supporting it.

from xml.dom.minidom import parseString
from scavenger_utils import http_request

GITHUB_HOST = "github.com"
GITHUB_PATH = "/api/v2/xml/user/email/"

def github(email):
  response = http_request("GET", GITHUB_HOST, "%s%s" % (GITHUB_PATH, email), {})

  if response.status == 404:
    return ""
# Info: name, company, location, blog, login/username
  return parseString(response.read())

if __name__=="__main__":
  print github("andrei.soare@gmail.com").getElementsByTagName('name')[0].toxml()
