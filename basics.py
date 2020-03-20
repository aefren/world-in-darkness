from math import ceil
from random import randint

from log_module import *
from screen_reader import *
from sound import *
from data.lang.es import building_t


def ai_join_units(itm):
  if itm.can_join == 0 or itm.hp_total < 1 or itm.goal or itm.group: return
  logging.info(f'join units {itm} ({itm.units}).')
  itm.pos.update(itm.nation)
  dice = roll_dice(1)
  needs = ceil(itm.ranking / 20)
  if itm.pos.around_threat: needs -= 2
  logging.debug(f'dice {dice} needs {needs}.')
  if dice >= needs:
    for i in itm.pos.units:
      if (i == itm or i.garrison != itm.garrison or i.settler or i.comm
          or i.name != itm.name or i.can_join == 0 or i.hp_total < 1
          or i.goal or i.leader != itm.leader or i.group):
        continue
      logging.debug(f'{i}.')
      itm.update()
      i.update()
      dice = roll_dice(1)
      needs = ceil(i.ranking / 20)
      if itm.pos.around_threat: needs -= 2
      if i.scout: needs += 1
      logging.debug(f'dice {dice} needs {needs}.')
      if dice >= needs:
        join_units([itm,i])


def has_name(items, name):
  names = [i.name for i in items]
  for i in items:
    if i.type == building_t and i.base: names.append(i.base.name)
    else: names.append(i.name)
  if name in names: return True


def get_armor_mod(num):
  if num >= 5: return 2
  if num >=4: return 3
  if num >= 3: return 4
  if num >= 2: return 5
  if num >= 1: return 6
  if num <= 0: return 0


def get_hit_mod(num):
  if num >= 4: return 2
  elif num >= 1: return 3
  elif num >= -3: return 4
  elif num >= -7: return 5 
  elif num <= -8: return 6


def get_wound_mod(num):
  if num >= 2: return 2
  elif num >= 1: return 3
  elif num >= 0: return 4
  elif num >= -1: return 5 
  elif num <= -2: return 6


def get_unrest_mod(num):
  if num >= 50: return 0
  if num >= 30: return 1
  if num >= 10: return 2
  if num >= -10: return 3
  if num >= -30: return 4
  if num >= -50: return  5
  if num < -50: return 6


def join_units(units, info=0):
  name = units[0].name
  for i in units:
    if i.name != name or i.can_join == 0: return
  unit = units[0]
  for i in units[1:]:
    unit.hp_total += i.hp_total
    unit.mp[0] = min(unit.mp[0], i.mp[0])
    unit.pop += i.pop
    unit.initial_units += i.initial_units
    i.hp_total = 0
  unit.update()
  unit.pos.update()


def roll_dice(time=1):
  dice = [randint(1, 6) for i in range(time)]
  return sum(dice)