# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved
# Authors: tabara.mihai@gmail.com (Mihai Tabara)
#          diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)

import logging

import global_settings
from httplib import HTTPConnection, HTTPSConnection, HTTPResponse, HTTP_PORT
from response import Response
from urllib import urlencode

OK_CODE = 200
NOT_FOUND_ERROR_CODE = 404
DROOPY_ERROR_CODE = 600

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
