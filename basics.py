from time import sleep
from math import ceil
from random import randint

from language import *
from log_module import logging
from screen_reader import sp
from sound import *




def ai_join_units(itm, count=1, info=0):
  if (itm.can_join == 0 or itm.hp_total < 1 or itm.goal or itm.leads 
      or itm.goto or len(itm.pos.units) <= 1 or itm.squads >= itm.max_squads): return
  if info: logging.info(f'join units {itm} ({itm.units}).')
  itm.pos.update(itm.nation)
  for i in itm.pos.units:
    if (i == itm or i.garrison != itm.garrison or i.settler or i.leadership
        or i.name != itm.name or i.can_join == 0 or i.hp_total < 1
        or i.goal or i.leader != itm.leader or i.leads or i.scout
        or i.squads >= i.max_squads or itm.squads < i.squads):
      continue
    if info: logging.debug(f'{i}.')
    i.update()
    itm.join_units([itm, i.split()])
    count -= 1
    if count == 0: break


def has_name(items, name):
  names = [i.name for i in items]
  names += [i.nick for i in items]
  for i in items:
    if i.type == building_t and i.base: names += [i.base.name]
  if name in names: return True




def get_cast(itm):
  sleep(loadsound("in1") * 0.5)
  sp.speak(f"hechisos.")
  say = 1
  x = 0
  while True:
    sleep(0.001)
    if say and itm.spells:
      sp.speak(f"{itm.spells[x].name}. {cost_t} {itm.spells[x].cost}.", 1)
      say = 0

    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_F1:
          sp.speak(f"{power_t} {itm.power} {of_t} {itm.power_max}.")
        if event.key == pygame.K_HOME:
          x = 0
          loadsound("s2")
          say = 1
        if event.key == pygame.K_END:
          x = len(itm.spells) - 1
          loadsound("s2")
          say = 1
        if event.key == pygame.K_UP:
          x = basics.selector(itm.spells, x, go="up")
          say = 1
        if event.key == pygame.K_DOWN:
          x = basics.selector(itm.spells, x, go="down")
          say = 1
        if event.key == pygame.K_i:
          pass
        if event.key == pygame.K_RETURN:
          if itm.spells: return itm.spells[x](itm)
        if event.key == pygame.K_F12:
          sp.speak(f"on", 1)
          sp.speak(f"off", 1)
        if event.key == pygame.K_ESCAPE:
          loadsound("back3")
          return



def get_unit(items, nation=None, sound=None):
  if items == []: 
    loadsound('errn1')
    return None
  if sound: loadsound(sound)
  x = 0
  say = 1
  while True:
    sleep(0.001)
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



def get_unrest_mod(num):
  if num < -80: return 5
  if num <= -60: return  4
  if num <= -40: return 3
  if num <= -20: return 2
  if num <= 20: return 1
  else: return 0



def roll_dice(time=1):
  dice = [randint(1, 6) for i in range(time)]
  return sum(dice)


def selector(item, x, go = '', wrap = 0, sound = 's1', snd = 1):
  if len(item) == 0:
    sleep(loadsound('errn2', channel = CHTE2))
    return x
  if go == 'up':
    if x == 0 and wrap == 1:
      x = len(item) - 1
      if snd: loadsound(sound)
      return x

    if x == 0 and wrap == 0:
      sleep(loadsound('errn2', channel = CHTE2) * 0.5)
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
      sleep(loadsound('errn2', channel = CHTE2) * 0.5)
      return x
    else:
      x += 1
      if snd: loadsound(sound)
      return x


def view_log(log, nation, sound="book_open01", x=None):
  if x != None: x = x
  else: x = len(log) - 1
  y = 0
  say = 1
  sleep(loadsound(sound))
  while True:
    sleep(0.001)
    if say:
      if isinstance(log[x][y], str):sp.speak(log[x][y])
      elif isinstance(log[x][y], list): sp.speak(log[x][y][0])
      say = 0
    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN:
        if  event.key == pygame.K_LEFT:
          x = selector(log, x, "up", sound="book_pageturn3")
          y = 0
          say = 1
        if  event.key == pygame.K_RIGHT:
          x = selector(log, x, "down", sound="book_pageturn3")
          y = 0
          say = 1
        if  event.key == pygame.K_UP:
          y = selector(log[x], y, "up", sound="book_pageturn1")
          say = 1
        if  event.key == pygame.K_DOWN:
          y = selector(log[x], y, "down", sound="book_pageturn1")
          say = 1
        if  event.key == pygame.K_HOME:
          y = 0
          loadsound("book_pageturn1")
          say = 1
        if  event.key == pygame.K_END:
          y = len(log[x]) - 1
          loadsound("book_pageturn1")
          say = 1
        if  event.key == pygame.K_TAB:
          say = 1
          view_log(nation.devlog, nation)
        if  event.key == pygame.K_RETURN:
          if isinstance(log[x][y], list): view_log(log[x][y][1], nation, x=0)
        if  event.key == pygame.K_F12:
            sp.speak(f"debug on", 1)
            Pdb().set_trace()
            sp.speak(f"debug off", 1)
        if  event.key == pygame.K_ESCAPE:
          return sleep(loadsound("back1") / 2)



