#
# @copyright (c) 2009 2010 Michon van Dooren
# @license http://www.gnu.org/licenses/gpl-3.0.txt GNU General Public License
#

import os

def load(fn):
   result = {}
   f = open(fn)
   for line in f:
      line = line.strip()
      if line:
         user, setbynick, setbyhost, define = line.split('\t', 4)
         user = user.lower()
         result[user] = {'setbynick': setbynick, 'setbyhost': setbyhost, 'define': define}
   f.close()
   return result

def save(fn, data):
   f = open(fn, 'w')
   for k, v in data.items():
      line = k + '\t' + data[k]['setbynick'] + '\t' + data[k]['setbyhost'] + '\t' + data[k]['define']
      try: f.write(line + '\n')
      except IOError: break
   try: f.close()
   except IOError: pass
   return True

def setup(self):
   fn = self.nick + '-' + self.config.host + '.define.db'
   self.def_filename = os.path.join(os.path.dirname(self.config.filename), fn)
   if not os.path.exists(self.def_filename):
      try: f = open(self.def_filename, 'w')
      except OSError: pass
      else:
         f.write('')
         f.close()
   self.defines = load(self.def_filename)
   
   self.config.define_channels = getattr(self.config, 'define_channels', self.config.channels)
   self.config.define_channels = [chan.lower() for chan in self.config.define_channels]
         
   self.config.define_blacklist_users = getattr(self.config, 'define_blacklist_users', [])
   self.config.define_blacklist_users = [user.lower() for user in self.config.define_blacklist_users]
      
   self.config.define_blacklist_defs = getattr(self.config, 'define_blacklist_defs', [])
   self.config.define_blacklist_defs = [name.lower() for name in self.config.define_blacklist_defs]  

def joindef(phenny, input):
   if input.nick.lower() in phenny.defines:
      phenny.say(input.nick + ' ' + phenny.defines[input.nick.lower()]['define'])
joindef.rule = '(.*)'
joindef.event = 'JOIN'

def define(phenny, input):
   nick    = input.match.groupdict()['nick'] or input.nick
   define  = input.match.groupdict()['def']

   if define:
      if input.nick.lower() in phenny.config.define_blacklist_users:
         phenny.reply('You are not allowed to change defs.')
         
      elif input.sender[0] != '#' and not getattr(phenny.config, 'define_pm', False):
         phenny.reply('Def manipulation is not allowed through PM.')
         
      elif input.sender[0] == '#' and input.sender.lower() not in phenny.config.define_channels:
         phenny.reply('Def manipulation is only allowed in ' + ', '.join(phenny.config.define_channels))
         
      elif nick.lower() in phenny.config.define_blacklist_defs:
         phenny.reply('Defs may not be set for ' + nick)
      
      elif define.startswith('is an alias for ') and getattr(phenny.config, 'define_aliasadminonly', False) and not input.admin:
         phenny.reply('You are not allowed to set aliases.')
      
      else:
         phenny.defines[nick.lower()] = {'define': define, 'setbynick': input.nick, 'setbyhost': getattr(input, 'host', 'Unknown')}
         save(phenny.def_filename, phenny.defines)
         phenny.say(nick + ' ' + define)

   else:
      if nick.lower() in phenny.defines and nick.lower not in phenny.config.define_blacklist_defs:
         define = phenny.defines[nick.lower()]['define']
         if define.startswith('is an alias for '):
            if define[16:].lower() not in phenny.defines:
               define += ', which is not defined.'
            else:
               define = phenny.defines[define[16:].lower()]['define']
         phenny.say(nick + ' ' + define)

         # This part is for the admins only, if they request a .def from PM, they will get additional info.
         if input.admin and input.sender[0] != '#':
            phenny.say('  Define set by: %s (Host: %s)' % (phenny.defines[nick.lower()]['setbynick'], phenny.defines[nick.lower()]['setbyhost']))

      elif nick.lower() == input.nick.lower():
         phenny.reply('Sorry, but I don\'t know you.')

      else:
         phenny.reply('Sorry, but I don\'t know about ' + nick)

define.rule = (['def', 'define'], '(?:(?P<nick>[^\\s]*)(?: (?P<def>.*))?)?')

def forget(phenny, input):
   nick = input.match.groupdict()['nick'] or input.nick

   # Check if the nick has a def.
   if nick.lower() in phenny.defines:

      # Delete the def.
      del phenny.defines[nick.lower()]

   # Tell about it.
   phenny.say('Who is that "' + nick + '" you\'re talking about?')

forget.rule = (['forget'], '(?:(?P<nick>[^\\s]*)(?: (?P<def>.*))?)?')

if __name__ == '__main__':
   print __doc__.strip()
