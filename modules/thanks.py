#!/usr/bin/env python
"""
ping.py - Phenny Ping Module
Author: Sean B. Palmer, inamidst.com
About: http://inamidst.com/phenny/
"""

import random

def thanks(phenny, input):
   greeting = random.choice(('Yw', 'Welcome', 'You\'re Welcome'))
   punctuation = random.choice(('', '!'))
   phenny.say(greeting + ' ' + input.nick + punctuation)
thanks.rule = r'(?i)(thanks|thx|ty) $nickname\b'

def interjection(phenny, input):
   phenny.say(input.nick + '!')
interjection.rule = r'$nickname!'
interjection.priority = 'high'
interjection.thread = False

if __name__ == '__main__':
   print __doc__.strip()
