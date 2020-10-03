from time import sleep
from math import ceil
from random import randint

from data.lang.es import *
from log_module import logging
from screen_reader import sp
from sound import *




def ai_join_units(itm, count=1, info=0):
  if (itm.can_join == 0 or itm.hp_total < 1 or itm.goal or itm.group 
      or itm.goto or len(itm.pos.units) <= 1 or itm.squads >= itm.max_squads): return
  if info: logging.info(f'join units {itm} ({itm.units}).')
  itm.pos.update(itm.nation)
  for i in itm.pos.units:
    if (i == itm or i.garrison != itm.garrison or i.settler or i.comm
        or i.name != itm.name or i.can_join == 0 or i.hp_total < 1
        or i.goal or i.leader != itm.leader or i.group or i.scout
        or i.squads >= i.max_squads or itm.squads < i.squads):
      continue
    if info: logging.debug(f'{i}.')
    i.update()
    itm.join_units([itm, i.split()])
    count -= 1
    if count == 0: break


def has_name(items, name):
  names = [i.name for i in items]
  for i in items:
    if i.type == building_t and i.base: names.append(i.base.name)
    else: names.append(i.name)
  if name in names: return True



def get_armor_mod(num):
  if num >= 5: return 2
  if num >= 4: return 3
  if num >= 3: return 4
  if num >= 2: return 5
  if num >= 1: return 6
  if num <= 0: return 0



def get_hit_mod(num):
  if num >= 4: return 2
  elif num >= 1: return 3
  elif num >= -2: return 4
  elif num >= -5: return 5 
  else: return 6



def get_unit(items, nation=None, sound=None):
  if items == []: 
    loadsound('errn1')
    return None
  if sound: loadsound(sound)
  x = 0
  say = 1
  while True:
    sleep(0.1)
    if say:
      items[x].basic_info()
      say = 0

    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
        say = 1
        items[x].info(nation)
      if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
        say = 1
        x = selector(items, x, go = "up")    
      if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
        say = 1
        x = selector(items, x, go = "down")    
      if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
        loadsound('set6')
        return items[x]
      if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        return


def get_wound_mod(num):
  if num >= 2: return 2
  elif num >= 1: return 3
  elif num >= 0: return 4
  elif num >= -1: return 5 
  else: return 6



def get_unrest_mod(num):
  if num < -80: return 5
  if num <= -60: return  4
  if num <= -40: return 3
  if num <= -20: return 2
  if num <= 0: return 1
  else: return 0


def roll_dice(time=1):
  dice = [randint(1, 6) for i in range(time)]
  return sum(dice)


def selector(item, x, go = '', wrap = 0, sound = 's1', snd = 1):
  if len(item) == 0:
    sleep(loadsound('errn2', channel = ch4))
    return x
  if go == 'up':
    if x == 0 and wrap == 1:
      x = len(item) - 1
      if snd: loadsound(sound)
      return x

    if x == 0 and wrap == 0:
      sleep(loadsound('errn2', channel = ch4) * 0.5)
      return x
    else:
      x -= 1
      if snd: loadsound(sound)
      return x

  if go == 'down':
    if x == len(item) - 1 and wrap:
      x = 0
      if snd: loadsound(sound)
      return x

    if x == len(item) - 1 and wrap == 0:
      sleep(loadsound('errn2', channel = ch4) * 0.5)
      return x
    else:
      x += 1
      if snd: loadsound(sound)
      return x

