try:
  import tell as tellm
except:
  import imp
  tellm = imp.load_source('tell', './modules/tell.py') 

import re

def purge_tells(phenny, input):
  args = input.match.groupdict()
  newreminders = {}
  purged = 0
  if not hasattr(phenny, 'reminders'):
    phenny.reminders = tellm.loadReminders(phenny.tell_filename)

  tonick = args['tonick'] and args['tonick'].lower() or None;
  fromnick = args['fromnick'] and args['fromnick'].lower() or None;
  contains = args['contains'] and args['contains'].lower() or None;
  matches = args['matches'] and args['matches'].lower() or None;
  ematches = args['ematches'] and args['ematches'].lower() or None;
  
  if not input.admin and tonick != input.nick.lower() and fromnick != input.nick.lower():
    return phenny.msg(input.nick, 'You are not allowed to purge messages.')  
  
  for tellee, tells in phenny.reminders.iteritems():
    for tell in tells:
      teller = tell[0]		
     
      if (tonick and tonick != tellee.lower()) or (fromnick and fromnick != teller.lower()) or (contains and contains not in tell[3].lower()) or (matches and not re.search(matches, tell[3], re.I)) or (ematches and not re.match(ematches, tell[3], re.I)):
        if tellee not in newreminders:
          newreminders[tellee] = []				
        newreminders[tellee].append(tell)
      else:
        purged += 1
  
  tellm.dumpReminders(phenny.tell_filename, newreminders)	
  phenny.bot.reminders = newreminders   
  phenny.reply('Purging complete. Purged %d message%s.' % (purged, purged != 1 and 's' or ''))
      
purge_tells.rule = ('$nick', ['purge tells', 'purge all tells'], '(?:from (?P<fromnick>[^\\s]+)\\s*)?(?:to (?P<tonick>[^\\s]+)\\s*)?(?:containing (?P<contains>[^\\s]+)\\s*)?(?:matching (?P<matches>[^\\s]+)\\s*)?(?:matchingexact (?P<ematches>[^\\s]+)\\s*)?\\s*')
purge_tells.priority = 'high'
purge_tells.thread = False
