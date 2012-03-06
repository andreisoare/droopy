# Copyright 2012 Droopy @Sunnytrail Insight Labs Inc. All rights reserved
# Author: tabara.mihai@gmail.com (Mihai Tabara)
#       : diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)


from httplib import HTTPConnection, HTTPSConnection, HTTPResponse
from urllib import urlencode

# TODO(Mihai & Diana): Raise exceptions and check server status
# (discuss with Sunnytrail team the recommended method)

def http_request(method, host, service, params, port=80):

  conn = HTTPConnection(host) if port == 80 else HTTPSConnection(host)
  conn.request(method, '%s?%s' % (service, urlencode(params)))
  response = conn.getresponse()

  return response
