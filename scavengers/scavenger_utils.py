# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved
# Authors: tabara.mihai@gmail.com (Mihai Tabara)
#          diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)

import logging
import simplejson
import re
from httplib import HTTPConnection, HTTPSConnection, HTTPResponse, HTTP_PORT
from urllib import urlencode
from datetime import datetime

import global_settings
from scavenger_config import FACEBOOK_IDENTITY_COLLECTION
from response import Response
from base.mongodb_utils import get_mongo_collection

OK_CODE = 200
NOT_FOUND_ERROR_CODE = 404
DROOPY_ERROR_CODE = 600

FACEBOOK = "facebook"
FACEBOOK_HOST = "graph.facebook.com"

def http_request(email, method, host, service, params, port=HTTP_PORT):

  try:
    conn = HTTPConnection(host) if port == HTTP_PORT else HTTPSConnection(host)
    conn.request(method, '%s?%s' % (service, urlencode(params)))
    response = conn.getresponse()
    if response.getheader('X-RateLimit-Remaining'):
      logging.info('~~~~~~~~~~~~~~~~~~ %s %s ~~~~~~~~~~~~~~~~' %\
                        (host, response.getheader('X-RateLimit-Remaining')))
    return Response(response.status, response.read(), email)
  except:
    return Response(DROOPY_ERROR_CODE, '', email)

def format_url(url):
  url = url.replace('https://', '')
  url = url.replace('http://', '')
  url = url.replace('www.', '')

  return url

def get_facebook_identity(profile):
  profile = format_url(profile)
  pid, username = get_id_or_username(profile)

  response = check_if_exists(pid, username)
  if response:
    return response

  path = pid or username
  response = http_request('', "GET", FACEBOOK_HOST, '/%s' % path, {})
  if response.is_error():
    return None

  response = simplejson.loads(response['raw_data'])
  identity = {
              'time' : datetime.now(),
              'profile_id' : int(response['id']),
              'profile_user' : unicode(response['username']),
              'response' : response,
            }
  facebook_identities = get_mongo_collection(FACEBOOK_IDENTITY_COLLECTION)
  facebook_identities.insert(identity)

  return response

def get_id_or_username(profile):
  pid = None
  username = None
  if re.search('^facebook\.com/profile\.php\?id=\d+$', profile):
    pid = re.search('\d+$', profile).group(0)
  if re.search('^facebook\.com/[\d\w\.]+$', profile):
    username = re.search('/.+$', profile).group(0)[1:]
  return pid, username

def check_if_exists(pid, username):
  facebook_identities = get_mongo_collection(FACEBOOK_IDENTITY_COLLECTION)
  identity = None
  if pid:
    identity = facebook_identities.find_one({'profile_id' : int(pid)})
  if username:
    identity = facebook_identities.find_one(
                                          {'profile_user' : unicode(username)})
  if identity:
    return identity['response']
  else:
    return None

