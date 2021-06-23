dev_mode = 0
# available languages: en, es.
lang = "en" 
if dev_mode == 0:
  if lang == "es": exec("from data.lang.es import *") 
  elif lang == "en": exec("from data.lang.en import *")
elif dev_mode == 1:
  if lang == "es": from data.lang.es import * 
  elif lang == "en": from data.lang.en import *