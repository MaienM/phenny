#
# @package OBR
# @version $Id: OBR.py v0.1 (14-03-2011 15:07 CET)
# @copyright (c) 2009, 2011 Michon van Dooren
# @license http://www.gnu.org/licenses/gpl-3.0.txt GNU General Public License
#

#
#   This file is part of OBR.
#
#   OBR is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   OBR is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with OBR.  If not, see <http://www.gnu.org/licenses/>.
#

#
# Responses can be forwarded by using the r or l function.
# When forwarded with the r function, the forwarded-to action can be influenced by groups. 
# When forwarded with the l function, any groups for the new action will be ignored.
#   Example: 'noms': r('eats'),
#
#
# If an response is a tupple, one of the values will be chosen at random as response.
#   Example: 'eats': [act('dies'), act('kicks %(nick)s in the face')],
# 
# You can specify a different response for admin/owner as well.
#   Example: 'pets':        act('stares at %(nick)s',
#            'pets admin':  act('purrs'),
#
# You can even specify a different response for other custom groups.
#   Example: 'kicks meanies':  act('nukes %(nick)s'),
#
# You can use '!' to match all actions, or '*' to match all actions with no other actions defined for them.
#   Example '! meanies': act('nukes %(nick)s'),
#

import random   

def act(s):
  return '\x01ACTION ' + s + ' \x01'
def say(s):
  return s
def cmd(s):
  return '#' + s
def r(s):
  return '!' + s
def l(s):
  return '?' + s

responses = {
  # For meanies (bensawsome), override everything and always be mean.
  '! meanies':       (act('nukes %(nick)s'),
                      act('runs from %(nick)s'),
                      act('hides behind %(owner)s'),
                      cmd('KICK %(chan)s %(nick)s :MEANIE!!'),),

  # Unknown actions.
  '*':               (act('looks at %(nick)s, not sure how to respond to this'),
                      act('looks at %(owner)s for help'),
                      act('looks confused'),
                      act('looks puzzled'),
                      act('strokes her hair, unsure what to make of this'),
                      act('wonders what this "%(act)s" stuff is all about'),
                      act("doesn't know what to make of this"),
                      act("isn't certain what that means"),),

  # Basic friendly actions.
  'hugs':             act('%(act)s %(nick)s back %(postf)s'),
  'hugs admin':       act('blushes'),
    'slaps':            l('hugs'),
    'pokes':            l('hugs'),
  'hi-5s':            act('hi-5s %(nick)s'),
    'high-5s':          r('hi-5s'),
    'high5s':           r('hi-5s'),
    'hi5s':             r('hi-5s'),
  'thanks':          (say("you're welcome"),
                      say('yw'),
                      say('welcome'),
                      say('no problem'),
                      say('anytime %(nick)s'),),
    'thx':              r('thanks'),
    'ty':               r('thanks'),

  # Mean actions, like kicking.
  'kicks':           (cmd('KICK %(chan)s %(nick)s :Take that!!'),
                        l('kicks admin'),),
  'kicks admin':     (say('ouch'),
                        l('hugs'),),
    'punches':          r('kicks'),
    'hurts':            r('kicks'),
    'stabs':            r('kicks'),
    'kick':             r('kicks'),

  # A bot ain't food... but well.
  'eats':             act('tastes crunchy'),
    'noms':             r('eats'),
    'nibbles':          r('eats'),

  # A little bit TOO friendly actions.
  'kisses':          (act('convulses violently while shouting to GTFO!'),
                      say('RAPIST!!!'),
                      act('kicks %(nick)s in the groin'),),
  'kisses owner':     act('pushes %(nick)s away'),
    'loves':            r('kisses'),

  'pets':             act('stares at %(nick)s'),
  'pets admin':       act('purrs'),

  'a':             {'b': say('wha...')},
}

def getAct(act, postf, trueact, chain, input, fwild = True):
  if (act, postf) in chain:
    raise Exception('Endless forwarding loop: ' + ' -> '.join(chain) + ' -> ' + (act, postf))
  else:
    chain.append((act, postf))

  # If we are wildcard/global forwarding, append the first matching group to the act.
  if fwild and input.cgroups:
    for group in input.cgroups:
      if act + ' ' + group in responses:
        args = getAct(act + ' ' + group, postf, trueact, chain, input)
        if args[0]:
          return args
  
  # If the act is unknown, try to remove the last word. If only one word remains, we bail.
  if act not in responses:
    if ' ' in act:
      trueact = act[:act.rfind(' ')]
      (act, postf, trueact, chain) = getAct(trueact, postf, trueact, chain, input)

      # If the postf is unknown, try to remove the last word. If only one word remains, we bail.
      if not act and isinstance(responses[act], dict) and postf not in responses[act]:
        while ' ' in postf and not act:
          postf = postf[:postf.rfind(' ')]
          (act, postf, trueact, chain) = getAct(act, postf, trueact, chain, input)
    else:
      return (None, None, None, chain)


  # Get the response.
  if act in responses:
    resp = responses[act]
  else:
    return (act, postf, trueact, chain)

  # If it is a tuple pick a random response to use.
  if isinstance(resp, tuple):
    if input.owner:
      resp = [t for t in resp if '%(owner)s' not in t] or resp
    resp = random.choice(resp)

  # If the response is a forward, get the real action.
  if resp[0] in '!?':
    (act, postf, trueact, chain) = getAct(resp[1:], postf, trueact, chain, input, resp[0] == '!')

  # Return the found action.
  return (act, postf, trueact, chain)

def action(phenny, input):
  act = input.group(1)
  postf = input.group(2)

  # We filter out any custom groups, and admin/owner.
  while hasattr(phenny.config, 'groups'):
    for group in phenny.config.groups.keys() + ['admin', 'owner']:
      if act.endswith(group):
        act = act[:-(len(group)+1)]
        continue
    break
  
  # Get the act.
  for a in ['!', act, '*']:
    a, postf, trueact, chain = getAct(a, postf, act, [], input)
    if a:
      act = responses[a]
      break

  # If it is a tuple pick a random response to use.
  if isinstance(act, tuple):
    act = [t for t in act if t[0] not in '!?'] or act
    if input.owner:
      act = [t for t in act if '%(owner)s' not in t] or act
    print act
    act = random.choice(act)

  act = act % {'nick': input.nick, 
               'chan': input.sender,
               'postf': postf, 
               'act': trueact, 
               'owner': phenny.config.owner,}

  if act[0] == '#':
    phenny.write(act[1:].split(None, 1))
  else:
    phenny.say(act)
      
action.rule = '\x01ACTION (.*?) $nickname\s*(.*?)\x01'
