import beanstalkc
import thread
import simplejson
import sys
import time
import thread
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))

from lastfm_scavenger import LastfmScavenger
from soundcloud_scavenger import SoundcloudScavenger
from twitter_scavenger import TwitterScavenger
from aboutme_scavenger import AboutmeScavenger
from pinterest_scavenger import PinterestScavenger
from linkedin_scavenger import LinkedinScavenger
from base.mongodb_utils import get_mongo_collection
from datetime import datetime

networks = {
            'lastfm': LastfmScavenger,
            'soundcloud': SoundcloudScavenger,
            'twitter': TwitterScavenger,
            'aboutme': AboutmeScavenger,
            'pinterest': PinterestScavenger,
            'linkedin': LinkedinScavenger,
          }

if __name__=="__main__":
  profiles = get_mongo_collection()

  social_profile = profiles.SocialProfile()
  jsn = {}
  jsn['email'] = 'andrei.soare@gmail.com'
  jsn['username'] = 'andreisoare'
  jsn['collection'] = 'test'
  social_profile['email'] = unicode(jsn['email'])
  social_profile['time'] = datetime.now()
  social_profile.save()
  jsn['id'] = str(social_profile['_id'])

  scavs = []
  for k, v in networks.iteritems():
    sc = v(k, k + "_in", "out")
    scavs.append(sc)
    thread.start_new_thread(sc.run, ())

  email_beanstalk = beanstalkc.Connection()
  for key in networks:
    email_beanstalk.use(key + '_in')
    email_beanstalk.put(simplejson.dumps(jsn))

  time.sleep(20)

