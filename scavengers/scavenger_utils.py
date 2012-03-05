# Copyright 2012 Droopy @Sunnytrail Insight Labs Inc. All rights reserved
# Author: tabara.mihai@gmail.com (Mihai Tabara)
#       : diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)


from httplib import HTTPConnection, HTTPResponse
from urllib import urlencode

# TODO raise exceptions, check status
def http_request(method, host, service, params):
  conn = HTTPConnection(host)

  conn.request(method, '%s?%s' % (service, urlencode(params)))
  response = conn.getresponse()

  return response
