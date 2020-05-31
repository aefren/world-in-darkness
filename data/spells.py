#!/usr/bin/env python
# -*- coding: utf-8 -*-
import basics
from data.lang.es import *
from data.items import *



class Spell:
  name = 'skill'
  desc = str()
  cast = 6
  cost = 1
  ranking = 0
  tags = []
  type = 'spell' 

  tile_area = -1
  target = None
  traits = None

  ambient_day = 0
  ambient_night = 0
  corpses = 0
  season_autum = 0
  season_sammer = 0
  seasson_sprint = 0
  season_winter = 0
  tile_forest = 0
  tile_swamp = 0
  tile_grass = 0
  tile_plains = 0
  tile_waste = 0
  tile_hill = 0
  tile_tundra = 0
  tile_ocean = 0

  def __init__(self, itm):
    self.itm = itm

  def __str__(self):
    return self.name
  
  def check_cast(self, itm):
    if roll_dice(2) >= self.cast: return 1
    else: 
      msg = f'{self} {failed_t}.'
      if itm.show_info: sp.speak(msg, 1)
      return msg

  def check_conditions(self, itm, target):
    msg = ''
    if self.target and target.type not in self.target: msg += f'not {self.target} selected.'
    if self.traits: pass
    if self.tile_forest and itm.pos.surf.name != forest_t: msg += f'{self.name} needs forest.'
    if self.corpses and itm.pos.corpses == []: msg += f'{self.name} needs corpses.'
    if msg: return msg
    else: return None

  def check_cost(self, itm):
    if itm.power < self.cost:
      msg = f'{self}. {needs_t} {power_t}.'
      logging.debug(msg)
      itm.log[-1] += [msg]
      if itm.show_info: sp.speak(msg, 1)
      return msg
    else: 
      itm.power -= self.cost
      return 1
  
  def init(self, itm, target=None):
    target = target
    if self.target:
      if (any(i in self.target for i in ['beast', 'cavalry', 'infantry', 'civil']) 
          and target == None):
           
       
        units = [i for i in itm.pos.units 
                 if i.nation == itm.nation and i != itm]
        target = basics.get_item(units, itm.nation)
    conditions = self.check_conditions(itm, target)
    if conditions != None: return conditions
    check = self.check_cost(itm)
    if check != 1: return check
    cast = self.check_cast(itm)
    if cast != 1: return cast
    if target:self.run(itm, target)
    else: self.run(itm)
    
  def run(self):
    pass



class BloodHeal(Spell):
  desc = 'sacrifica un número aleatoreo de población para curarse.'


class BreathOfTheDesert(Spell):
  desc = 'Envía aires del desierto a una casilla elegida. esto subirá la temperatura y dañara la producción de alimentos.'



class CastBloodRain(Spell):
  name = 'blood rain'
  cast = 10
  cost = 3#0
  type = spell_t
  tags = ['weather']

  def ai_run(self, itm):
    tiles = itm.pos.get_near_tiles(1)
    raining = 0
    for t in tiles:
      if self.name in [ev.name for ev in t.events]: raining = 1
    if raining == 0: self.init(itm)

  def run(self, itm):
    sleep(loadsound('spell27', channel=ch5, vol=0.7) / 2)
    msg = f'spell {self.name}'
    itm.log[-1] += [msg]
    logging.debug(msg)
    dist = 2
    roll = roll_dice(1)
    if roll >= 6: dist += 4
    elif roll >= 5: dist += 2
    pos = itm.pos
    sq = pos.get_near_tiles(dist)
    for s in sq:
      if self.name not in [ev.name for ev in s.events]:
        s.events += [BloodRaining(s)]
        s.events[-1].turns = randint(3,5)


class CastWailingWinds(Spell):
  name = 'wailing winds'
  desc = '-1 resolve for all units. ignores (death, malignant.'
  cast = 6
  cost = 1#5
  ranking = 0
  tags = ['morale']
  type = 'spell'

  def ai_run(self, itm):
    tiles = itm.pos.get_near_tiles(1)
    wailing = 0
    for t in tiles:
      if self.name in [ev.name for ev in t.events]: wailing= 1
    if wailing == 0: self.init(itm)

  def run(self, itm):
    sleep(loadsound('spell38', channel=ch5, vol=0.7))
    msg = f'spell {self.name}'
    itm.log[-1] += [msg]
    logging.debug(msg)
    dist = 1
    roll = roll_dice(1)
    if roll >= 6: dist += 2
    elif roll >= 5: dist += 1
    pos = itm.pos
    sq = pos.get_near_tiles(dist)
    for s in sq:
      if self.name not in [ev.name for ev in s.events]:
        s.events += [WailingWinds(s)]
        s.events[-1].turns = randint(2,3)


class HealingMists(Spell):
  desc = 'summons a mist in unit position. this mist heals all units into.'



class HealingRoots(Spell):
  name = 'raices curativas.'
  cost = 10
  cast = 4
  type = 'spell'
  tags = [health_t]

  target = ['beast', 'cavalry', 'civil', 'infantry']
  tags = ['healing']

  def ai_run(self, itm):
    units = [i for i in itm.pos.units if i.nation == itm.nation
             and intoxicated_t in i.global_skills]
    
    if units: self.init(itm, units[0])

  def run(self, itm, target):
    target.other_skills = [sk for sk in target.other_skills if sk.name != intoxicated_t]
    msg = f'{itm} has removed {intoxicated_t} {from_t} {target}.'
    logging.debug(msg)
    itm.log[-1] += [msg]
    target.log[-1] += [msg]



class Eartquake(Spell):
  pass



class EnchantedForests(Spell):
  pass



class FeastOfFlesh(Spell):
  desc = 'sacrifica x población para invocar ogros a su servicio.'



class FireDarts(Spell):
  pass



class MagicDuel(Spell):
  pass



class Mist(Spell):
  pass



class PoisonCloud(Spell):
  pass



class RaiseDead(Spell):
  name = raise_dead_t
  cost = 20
  cast = 6
  ranking = 10
  type = 'spell34'
  tags = ['reanimating']

  corpses = 1

  def ai_run(self, itm):
    self.run(itm)

  def run(self, itm):
    if itm.pos.corpses == [] or itm.power < self.cost:
      if itm.show_info: sleep(loadsound('errn1'))
      msg = f'{itm} no puede lanzar hechiso {self.name}'
      logging.debug(msg)
      if msg not in itm.log[-1]: itm.log[-1].append(msg)
      return
    
    logging.info(f'{self.name}. ({itm}).')
    itm.power -= self.cost
    roll1 = roll_dice(2)
    tile = itm.pos
    
    dead = choice(tile.corpses)
    raised = choice(dead.corpses)(itm.nation)
    raised.hp_total = sum(dead.deads) * raised.hp
    raised.update()
    logging.debug(f'unidades totales de {dead} {sum(dead.deads)}.')
    logging.debug(f'{raised} unidades {raised.units}. hp {raised.hp}.')
    roll2 = roll_dice(2)
    needs = ceil(raised.ranking / 12)
    logging.debug(f'roll1 {roll1}. cast {self.cast}, roll2 {roll2} need {needs}.')
    if roll2 >= needs and roll1 >= self.cast:
      msg = f'{itm} lanza {self.name}.'
      logging.info(msg)
      tile.corpses.remove(dead)
      raised.auto_attack = 1
      raised.pos = tile
      raised.pos.units.append(raised)
      msg = f'reanimados {raised}.'
      itm.log[-1].append(msg)
      if itm.nation.show_info: sleep(loadsound('raiseundead1') / 2)
      itm.pos.update(itm.nation)
    else:
      msg = f'fallo.'
      logging.debug(msg)
      itm.log[-1].append(msg)
      if itm.show_info: 
        sp.speak(f'{self.name} fall�.')



class Reinvigoration(Spell):
  desc = 'sacrifica x población para regenerar poder.'



class SanguineHeritage(Spell):
  desc = 'sacrifices 44 slaves to raise 1 blood knight.'



class SecondSun(Spell):
  desc = 'crea un segundo sol negando la noche y dañando la agricultura de los lugares afectados.'



class SummonAwakenTree(Spell):
  name = 'summon awaken tree'
  cost = 1
  cast = 1
  type = 'spell'
  tags = ['summon']

  tile_forest = 1

  def ai_run(self, itm):
    self.init(itm)

  def run(self, itm):
    unit = itm.pos.add_unit(AwakenTree, itm.nation.name)
    msg = f'{unit} ({summoning_t})'
    logging.debug(msg)
    itm.log[-1] += [msg]



class SummonDevourerOfDemons(Spell):
  name = 'summon devourer of demons'
  cost = 1
  cast = 1
  type = 'spell'
  tags = ['summon']

  def ai_run(self, itm):
    if itm.pos.around_nations and itm.pos.around_snation == []:
      self.init(itm)

  def run(self, itm):
    unit = itm.pos.add_unit(DevourerOfDemons, wild_t)
    msg = f'{unit} ({summoning_t})'
    logging.debug(msg)
    itm.log[-1] += [msg]



class SummonDriads(Spell):
  name = 'summon driads'
  cost = 1
  cast = 1
  type = 'spell'
  tags = ['summon']

  def ai_run(self, itm):
    self.init(itm)

  def run(self, itm):
    unit = itm.pos.add_unit(Driads, itm.nation.name)
    msg = f'{unit} ({summoning_t})'
    logging.debug(msg)
    itm.log[-1] += [msg]



class SummonForestBears(Spell):
  name = 'summon forest bears'
  cost = 1
  cast = 1
  type = 'spell'
  tags = ['summon']

  def ai_run(self, itm):
    if itm.pos.surf and itm.pos.surf == forest_t: self.init(itm)

  def run(self, itm):
    unit = itm.pos.add_unit(ForestBears, itm.nation.name)
    msg = f'{unit} ({summoning_t})'
    logging.debug(msg)
    itm.log[-1] += [msg]



class SummonFalcons(Spell):
  name = 'summon forest falcons'
  cost = 1
  cast = 1
  type = 'spell'
  tags = ['summon']

  def ai_run(self, itm):
    self.init(itm)

  def run(self, itm):
    unit = itm.pos.add_unit(Falcons, itm.nation.name)
    msg = f'{unit} ({summoning_t})'
    logging.debug(msg)
    itm.log[-1] += [msg]



class SummonSpectralInfantry(Spell):
  name = 'summon spectral infantry'
  cost = 1
  cast = 1
  type = 'spell'
  tags = ['summon']

  def ai_run(self, itm):
    self.init(itm)

  def run(self, itm):
    unit = itm.pos.add_unit(SpectralInfantry, itm.nation.name)
    msg = f'{unit} ({summoning_t})'
    logging.debug(msg)
    itm.log[-1] += [msg]

