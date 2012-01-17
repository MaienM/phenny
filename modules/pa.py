try:
  import search
except:
  import imp
  search = imp.load_source('search', './modules/search.py') 

def pa(phenny, input): 
   """Queries PortableApps.com for the specified input."""
   query = input.group(2)
   if not query: 
      return phenny.reply('.pa what?')
   result = search.search('site:portableapps.com ' + query)
   
   try: uri = result['responseData']['results'][0]['unescapedUrl']
   except: uri = None
   
   if uri:
      if not hasattr(phenny.bot, 'last_seen_uri'):
         phenny.bot.last_seen_uri = {}
      phenny.bot.last_seen_uri[input.sender] = uri
      
      phenny.reply('%s: %s' % ((result['responseData']['results'][0]['titleNoFormatting'].split('|'))[0][:-1], uri))
   else: phenny.reply("No results found for '%s'." % query)
pa.commands = ['pa']
pa.priority = 'high'
pa.example = '.pa firefox portable flash'

def pahelp(phenny, input):
   """Help function for the portableapps.com chatroom"""
   if input.sender.lower() == '#portableapps':
      phenny.reply('Welcome to the PortableApps.com official chatroom. Ask your question and someone should be able to help you shortly. If you still don\'t get an answer, try posting on the forums: http://portableapps.com/forums')
pahelp.rule = 'help([!?])?'
