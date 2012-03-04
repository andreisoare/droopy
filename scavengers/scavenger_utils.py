# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved
# Authors: tabara.mihai@gmail.com (Mihai Tabara)
#          diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)


from httplib import HTTPConnection, HTTPSConnection, HTTPResponse, HTTP_PORT
from urllib import urlencode

# TODO(Mihai & Diana): Raise exceptions and check server status
# (discuss with Sunnytrail team the recommended method)

def http_request(method, host, service, params, port=HTTP_PORT):

  conn = HTTPConnection(host) if port == HTTP_PORT else HTTPSConnection(host)
  conn.request(method, '%s?%s' % (service, urlencode(params)))
  response = conn.getresponse()

  return response
