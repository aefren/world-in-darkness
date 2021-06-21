dev = 0
# available languages: en, es.
lang = "en" 
if dev == 0:
  if lang == "es": exec("from data.lang.es import *") 
  elif lang == "en": exec("from data.lang.en import *")
elif dev == 1:
  if lang == "es": from data.lang.es import * 
  elif lang == "en": from data.lang.en import *