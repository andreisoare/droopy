# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)

import re
import httplib
from scavenger_utils import http_request

PICASA_HOST = "picasaweb.google.com"
GOOGLE_HOST = "www.googleapis.com"
GOOGLE_PLUS_PATH = "/plus/v1/people/"
GOOGLE_PLUS_KEY = "AIzaSyACfowiWrJPaxS5EFvI6-N07CjctMdIqhE"
INFO_MATCH = "var _user"

def google_plus(email):
  username = email[:email.find("@gmail.com")]
  response = http_request("GET", PICASA_HOST, "/%s" % username, {})

  if response.status == 404
    return ""
  user_id = get_user_id(response.read())

  params = {'key':GOOGLE_PLUS_KEY}
  response = http_request("GET", GOOGLE_HOST, "%s%s" % (GOOGLE_PLUS_PATH,
    user_id), params, httplib.HTTPS_PORT)
# TODO (Diana) parse response
  return response.read()

def get_user_id(page):
  index = page.find(INFO_MATCH)
  info = page[page.find("{", index):page.find("};", index)]
  match = re.search('name(\s)*:\'(\d)*\'', info)
  return match.group(0).split('\'')[1]

if __name__=="__main__":
  print google_plus("diana.tiriplica@gmail.com")
