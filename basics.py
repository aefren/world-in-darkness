from time import sleep
from math import ceil
from random import randint

from data.lang.es import *
from log_module import logging
from screen_reader import sp
from sound import *



def ai_join_units(itm):
  if itm.can_join == 0 or itm.hp_total < 1 or itm.goal or itm.group or itm.goto: return
  logging.info(f'join units {itm} ({itm.units}).')
  itm.pos.update(itm.nation)
  dice = roll_dice(1)
  needs = ceil(itm.ranking / 30)
  if itm.pos.around_threat * 1.3 > itm.pos.defense: needs -= 2
  if itm.rng + itm.rng_mod > 5: needs -= 2
  if itm.garrison and itm.pos.around_threat < itm.pos.defense: needs += 2
  if itm.pos.food_need > itm.pos.food: needs += 3
  logging.debug(f'dice {dice} needs {needs}.')
  if dice >= needs:
    for i in itm.pos.units:
      if (i == itm or i.garrison != itm.garrison or i.settler or i.comm
          or i.name != itm.name or i.can_join == 0 or i.hp_total < 1
          or i.goal or i.leader != itm.leader or i.group):
        continue
      logging.debug(f'{i}.')
      i.update()
      dice = roll_dice(1)
      needs = ceil(i.ranking / 20)
      if itm.pos.around_threat * 1.3 > itm.ranking: needs -= 2
      logging.debug(f'dice {dice} needs {needs}.')
      if dice >= needs:
        join_units([itm, i])



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
  elif num >= -6: return 5 
  else: return 6



def get_item(items, nation=None, sound=None):
  if items == []: 
    loadsound('errn1')
    return None
  if sound: loadsound(sound)
  x = 0
  say = 1
  while True:
    sleep(0.1)
    if say:
      sp.speak(f'{items[x]}.',1)
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


def get_wound_mod(num):
  if num >= 2: return 2
  elif num >= 1: return 3
  elif num >= 0: return 4
  elif num >= -1: return 5 
  else: return 6



def get_unrest_mod(num):
  if num > 10: return 0
  if num <= 10: return 1
  if num <= 0: return 2
  if num <= -10: return 3
  if num <= -20: return 4
  if num <= -30: return  5
  if num < -50: return 6



def join_units(units, info=0):
  name = units[0].name
  units.sort(key=lambda x: x.history.turns, reverse=True)
  for i in units:
    if i.name != name or i.can_join == 0: return
  unit = units[0]
  for i in units[1:]:
    unit.hp_total += i.hp_total
    unit.mp[0] = min(unit.mp[0], i.mp[0])
    unit.pop += i.pop
    unit.squads += i.squads
    unit.other_skills += i.other_skills
    msg = f'{i} has joined.'
    unit.log[-1] += [msg]
    i.hp_total = 0
  unit.update()
  unit.pos.update()



def roll_dice(time=1):
  dice = [randint(1, 6) for i in range(time)]
  return sum(dice)


def selector(item, x, go = '', wrap = 0, sound = 's1', snd = 1):
  if len(item) == 0:
    sleep(loadsound('errn1', channel = ch4))
    return x
  if go == 'up':
    if x == 0 and wrap == 1:
      x = len(item) - 1
      if snd: loadsound(sound)
      return x

    if x == 0 and wrap == 0:
      sleep(loadsound('errn1', channel = ch4) * 0.5)
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
      sleep(loadsound('errn1', channel = ch4) * 0.5)
      return x
    else:
      x += 1
      if snd: loadsound(sound)
      return x

