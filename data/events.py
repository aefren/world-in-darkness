
import basics
import math

from data import skills
from data.lang.es import *
from log_module import *
from random import choice, randint, shuffle, uniform
from screen_reader import *
from sound import *
from time import *

class Event:
  name = ''
  desc = ''
  turns = 0
  type = 0

  def __init__(self, itm):
    self.itm = itm
  def __str__(self):
    return self.name



class Looting(Event):
  name = 'raids'
  turns = 0
  type = 0

  def run(self, info = 0):
    if self.itm.pos.world.turn < 2: return
    for t in self.itm.tiles:
      if info: print(f'checking raiders in {t} {t.cords}.')
      roll = basics.roll_dice(2)
      buildings = [b for b in t.buildings if b.nation != self.itm.nation]
      if buildings: roll += 4
      if info: print(f'{roll = : }')
      if roll >= 10 and t.unrest >= 20:
        raided = randint(math.ceil(t.income*0.2), math.ceil(t.income*0.4))
        kills = randint(1,10)*t.pop/100
        if t.unrest >= 50: raided *= 2
        kills *= 2 
        t.raided = raided
        t.pop -= kills
        msg = f"pillage {in_t} {t} {t.cords}. loss {raided} {gold_t}."
        self.itm.nation.log[-1] += [msg]
        if kills >= 1:
          t.add_corpses(choice(t.nation.population_type), kills) 
          msg = f'loss {kills} population.'
          self.itm.nation.log[-1] += [msg]
        if t.is_city and t.city.capital and t.city.nation.gold >= 500:
          try:
            steal = randint(int(self.itm.nation.gold*0.1), int(self.itm.nation.gold*0.5))
          except: Pdb().set_trace()
          self.itm.nation.gold -= steal
          msg = f'{steal} {gold_t} stealed from nation.'
        buildings = [b for b in t.buildings if b.nation == self.itm.nation]
        if t.unrest >= 50 and buildings:
          building = choice(buildings)
          building.resource_cost[0] -= building.resource_cost[1]*uniform(0.3, 0.6)
          msg = f'{building} has been damaged.'
          self.itm.nation.log[-1] += [msg]
        if self.itm.nation.show_info: sleep(loadsound('spell35') / 4)


class Reanimation(Event):
  name = 'reanimation'
  turns = 0
  type = 0

  def run(self, info = 1):
    if info: logging.info(f'revisando eventos de {self.itm}.')
    if self.itm.pos.world.turn < 2: return
    for t in self.itm.tiles:
      if t.corpses == []: continue
      total_hp = randint(40,80)
      corpses = []
      dead = None
      for it in t.corpses: corpses += [it]
      for it in corpses: it._go = 1
      for it in corpses:
        for cr in it.corpses:
          if cr.aligment != malignant_t: it._go = 0
      corpses = [it for it in corpses if it._go]
      shuffle(corpses)
      for it in corpses:
        shuffle(it.corpses)
        for cr in it.corpses:
          if cr.aligment == malignant_t: 
            dead = it
            raised = cr(t.nation)
          break
      if dead == None: break
      if sum(dead.deads)*dead.hp >= total_hp: 
        raised.hp_total = total_hp
        dead.deads[0] -= total_hp / dead.hp
      else: 
        raised.hp_total = sum(dead.deads) *dead.hp
        t.corpses.remove(dead)
      raised.update()
      
      msg = f"{raised} raised from {dead} in {t} {t.cords}."
      logging.info(msg)
      raised.pos = t
      raised.pos.units.append(raised)
      t.nation.log[-1].append(msg)
      if t.nation.show_info: sleep(loadsound("raiseundead1") / 2)
      t.update(t.nation)
      raised.combat_pre(raised.pos)


class Revolt(Event):
  name = 'revolt'
  turns = 0
  type = 0

  def run(self, info = 1):
    if info: print(f'revisando eventos de {self.itm}.')
    if self.itm.pos.world.turn < 2: return
    for t in self.itm.tiles:
      if t.pop == 0: continue
      roll = basics.roll_dice(1)
      order = basics.get_unrest_mod(t.public_order)
      if info: print(f'{t} {t.cords}. {roll = :}, {order =:}, {t.public_order =:}.')
      if roll  <= order:
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
          percent = randint(20, 50)
          unit = t.add_unit(unit, unit.aligment)
          unit.hp_total = percent*unit.hp_total/100
          unit.update()
          rebels += [unit]
          t.pop -= unit.total_pop

        if rebels:
          logging.debug(f'evento {self.name} (order) en {t} {t.cords}.')
          total_units = [str(i) for i in rebels]
          msg = f'{total_units} se alzan en {t} {t.cords}, {t.city}.'
          self.itm.nation.log[-1].append(msg)
        if rebels and self.itm.nation.show_info: sleep(loadsound('spell35') / 2)


class Starving(Event):
  name = "starving"
  
  def run(self, info=0):
    for t in self.itm.tiles:
      if t.pop < 1: continue
      if t.populated >= 120:
        t.unrest += randint(3, 7)
      elif t.populated >= 80:
        t.unrest += randint(1, 2)
      if t.populated >= 150 and basics.roll_dice(2) >= 11:
        deads = randint(5, 20)*t.pop/100
        if deads > t.pop: deads = t.pop
        t.unrest += deads * t.pop / 100
        t.pop -= deads
        t.add_corpses(choice(t.nation.population_type), deads)
        msg = f'starving in {t} {t.cords} deads {deads}.'
        self.itm.nation.log[-1] += [msg]
        if self.itm.nation.show_info: sleep(loadsound('spell36', channel=CHTE3) // 1.3)


class Unrest(Event):
  name = 'unrest'
  turns = 0
  type = 0

  def run(self, info=0):
    if self.itm.pos.world.turn < 2: return
    chance = 10
    for t in self.itm.tiles:
      t.update(self.itm.nation)
      if info:print(f'checking unrest in {t} {t.cords}.')
      roll = basics.roll_dice(2)
      buildings = [b for b in t.buildings if b.nation != self.itm.nation]
      if buildings: roll += 3
      if t.public_order <= 70: roll += 1
      if t.public_order <= 40: roll += 1
      if t.public_order <= 0: roll += 1
      if t.around_threat + t.threat > 0: roll += 1
      if t.is_city: roll -= 2
      if info: print(f'{roll = : }')
      if roll >= chance:
        unrest = randint(1, 5)
        unrest += sum([b.unrest for b in buildings])
        t.unrest += unrest
        t.last_unrest = f'{turn_t} {t.world.turn} {unrest}.'
        #msg = f'{unrest_t} in {t} {t.cords}.'
        #self.itm.nation.log[-1] += [msg]
        #if self.itm.nation.show_info: sleep(loadsound('spell35') / 5)