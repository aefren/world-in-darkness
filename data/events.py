from random import choice, uniform
from time import *

from basics import *
from data.lang.es import *
from log_module import *
from screen_reader import *
from sound import *


class Event:
  name = ''
  desc = ''
  turns = 0
  type = 0

  def __init__(self, itm):
    self.itm = itm


class Unrest(Event):
  name = 'unrest'
  turns = 0
  type = 0

  def run(self, info = 0):
    if info: print(f'revisando eventos de {self.itm}.')
    for t in self.itm.tiles:
      if t.pop == 0 or t.is_city: continue
      order = get_unrest_mod(t.public_order)
      if info: print(f'{t} {t.cords}. order {order}. public order {t.public_order}')
      if roll_dice(1) <= order:
        # t.effects.append(self.name)
        rebels = []
        rebelions = 1
        units = [i for i in self.itm.nation.units_rebels]
        if order >= 4: 
          units = [i for i in units if i.resolve <= 7]
          rebelions += 1
        elif order >= 2: 
          units = [i for i in units if i.resolve <= 6]
          rebelions += 1
        elif order >= 1: units = [i for i in units if i.resolve <= 5]
        if info: print(rebelions)
        for r in range(rebelions):
          unit = choice(units)
          if t.pop >= unit.pop:
            unit = t.add_unit(unit, self.itm.nation.name)
            for nt in t.world.random_nations:
              if nt.name == unit.align.name: unit.nation = nt
            t.world.units += [unit]
            rebels += [unit]
            extra = randint(1, rebelions)
            unit.hp_total *= rebelions
            unit.pop *= rebelions
            t.pop -= unit.pop
            unit.update() 
            unit.set_default_align()

        if rebels:
          logging.debug(f'evento {self.name} (order) en {t} {t.cords}.')
          total_units = [str(i) for i in rebels]
          msg = f'{total_units} se alzan en {t} {t.cords}, {t.city}.'
          self.itm.nation.log[-1].append(msg)
        if rebels and self.itm.nation.show_info:sleep(loadsound('spell35') / 4)
    
