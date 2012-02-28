# Copyright 2011 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: vlad@thesunnytrail.com (Vlad Berteanu)
#
# Database related utilities.

import global_settings
from mongokit import Connection

from mongodb.models import Client, MessageBatch, Digest, \
                           Company, APIUsage, UserEvent, \
                           ApiMessage, MessageThread, \
                           TwitterStreamEvent, TwitterStreamRoute

def register_all(conn):
  """Register models to mongodb connection."""
  conn.register([Client, MessageBatch, Digest,
                 Company, APIUsage, UserEvent,
                 ApiMessage, MessageThread,
                 TwitterStreamEvent, TwitterStreamRoute
                 ])

def get_mongo_connection(host=None, port=None):
  """ Open a connection to the MongoDB server """
  if not host and not port:
    try:
      host, port = global_settings.MONGODB.split(':')
    except (AttributeError, ValueError):
      host, port = None, None

  if host and port:
    conn = Connection(host, int(port))
    register_all(conn)
    return conn

  else:
    raise Exception('You need to configure the host and port '\
      'of the MongoDB document server')
