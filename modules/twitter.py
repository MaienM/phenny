#!/usr/bin/env python
"""
twitter.py - Phenny Twitter Module
Copyright 2008, Ryan McCue
Copyright 2010, Michon van Dooren
Modified it to remove the background checking, allow the use of .twitter without a parameter, and allowing you to view other tweets than the most recent one.
"""

import re, urllib
import web, time

timeline_url = 'http://twitter.com/statuses/user_timeline/%s.xml?count=1&page=%d'
r_status = re.compile(r'(?ims)<status>(.+?)<id>(.+?)<\/id>(.+?)<text>(.+?)<\/text>(.+?)<\/status>')

def twitter_get(user, num = 1): 
   global timeline_url
   if not '%' in user:
      if isinstance(user, unicode): 
         t = user.encode('utf-8')
      else: t = user
      q = urllib.quote(t)
      u = timeline_url % (q, num)
      bytes = web.get(u)
   else: bytes = web.get(timeline_url % (user, num))
   status = r_status.search(bytes)

   if not status or not status.group(4):
      return None

   return '%s: %s' % (user, status.group(4))

def twitter(phenny, input):
   try:
      origuser, num, = input.groups()[1].split(None, 3)
   except:
      origuser = input.groups()[1]
      num = 1
   if not origuser: 
      origuser = input.nick
   origuser = origuser.encode('utf-8')

   user = urllib.unquote(origuser)
   user = user.replace(' ', '_')

   try: result = twitter_get(user, int(num))
   except IOError: 
      error = "Can't connect to Twitter (%s)" % (timeline_url % user)
      return phenny.say(error)

   if result is not None: 
      phenny.say(result)
   else: phenny.say('%s has not yet updated or doesn\'t exist.' % origuser)
twitter.commands = ['twitter']

if __name__ == '__main__': 
   print __doc__.strip()

