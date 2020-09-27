from random import choice, uniform
from time import *

from basics import *
import basics
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



class Looting(Event):
  name = 'raids'
  turns = 0
  type = 0

  def run(self, info = 0):
    for t in self.itm.tiles:
      if info: print(f'checking raiders in {t} {t.cords}.')
      roll = basics.roll_dice(2)
      buildings = [b for b in t.buildings if b.nation != self.itm.nation]
      if buildings: roll += 4
      if info: print(f'{roll = : }')
      if roll >= 8 and t.unrest >= 20:
        raided = randint(ceil(t.income*0.4), ceil(t.income))
        t.raided = raided
        msg = f'{raiders_t} {raids_t} {raided} {in_t} {t} {t.cords}.'
        self.itm.nation.log[-1] += [msg]
        if t.is_city and t.city.capital:
          steal = randint(self.itm.nation.gold*0.1, self.itm.nation.gold*0.5)
          self.itm.nation.gold -= steal
          msg = f'{steal} {gold_t} stealed from nation.'
        buildings = [b for b in t.buildings if b.nation == self.itm.nation]
        if t.unrest >= 50 and buildings:
          building = choice(buildings)
          building.resource_cost[0] -= building.resource_cost[1]*uniform(0.1, 0.5)
          msg = f'{building} has been damaged.'
          self.itm.nation.log[-1] += [msg]
        if self.itm.nation.show_info: sleep(loadsound('spell35') / 4)


class Revolt(Event):
  name = 'revolet'
  turns = 0
  type = 0

  def run(self, info = 0):
    if info: print(f'revisando eventos de {self.itm}.')
    for t in self.itm.tiles:
      if t.pop == 0 or t.is_city: continue
      order = basics.get_unrest_mod(t.public_order)
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
        if rebels and self.itm.nation.show_info: sleep(loadsound('spell35') / 4)


class Unrest(Event):
  name = 'unrest'
  turns = 0
  type = 0

  def run(self, info=0):
    chance = 11
    for t in self.itm.tiles:
      t.update(self.itm.nation)
      if info:print(f'checking unrest in {t} {t.cords}.')
      roll = basics.roll_dice(2)
      buildings = [b for b in t.buildings if b.nation != self.itm.nation]
      if buildings: roll += 2
      if t.public_order <= 80: roll += 1
      if t.public_order <= 40: roll += 1
      if t.public_order <= 0: roll += 1
      if t.is_city: roll -= 1
      if info: print(f'{roll = : }')
      if roll >= chance:
        unrest = randint(1, 10)
        unrest += sum([b.unrest for b in buildings])
        t.unrest += unrest
        #msg = f'{unrest_t} in {t} {t.cords}.'
        #self.itm.nation.log[-1] += [msg]
        #if self.itm.nation.show_info: sleep(loadsound('spell35') / 5)