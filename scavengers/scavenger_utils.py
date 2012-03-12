# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved
# Authors: tabara.mihai@gmail.com (Mihai Tabara)
#          diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)


from httplib import HTTPConnection, HTTPSConnection, HTTPResponse, HTTP_PORT
from response import Response
from urllib import urlencode

NOT_FOUND_ERROR_CODE = 404
DROOPY_ERROR_CODE = 600

def http_request(email, method, host, service, params, port=HTTP_PORT):

  try:
    conn = HTTPConnection(host) if port == HTTP_PORT else HTTPSConnection(host)
    conn.request(method, '%s?%s' % (service, urlencode(params)))
    response = conn.getresponse()
    return Response(response.status, response.read(), email)
  except:
    return Response(DROOPY_ERROR_CODE)
