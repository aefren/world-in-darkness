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
  gold = 0
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
  tile_pop = 0

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
    if self.gold and itm.nation.gold < self.gold: msg += f'{self.name} {needs_t} {self.gold} {gold_t}.'
    if self.target and target.type not in self.target: msg += f'not {self.target} selected.'
    if self.traits: pass
    if self.tile_forest and itm.pos.surf.name != forest_t: msg += f'{self.name} {needs_t} forest.'
    if self.corpses and itm.pos.corpses == []: msg += f'{self.name} {needs_t} corpses.'
    if self.tile_pop and itm.pos.pop < self.tile_pop: msg += f'{self.name} {needs_t} {self.tile_pop} population.'
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
  cost = 30
  type = spell_t
  tags = ['weather']

  def ai_run(self, itm):
    tiles = itm.pos.get_near_tiles(1)
    raining = 0
    for t in tiles:
      if self.name in [ev.name for ev in t.events]: raining = 1
    if raining == 0: self.init(itm)


  def run(self, itm):
    if itm.show_info: sleep(loadsound('spell27', channel=ch5, vol=0.7) / 2)
    msg = f'spell {self.name}'
    itm.log[-1] += [msg]
    logging.debug(msg)
    dist = 2
    roll = roll_dice(1)
    if roll >= 6: dist += 4
    elif roll >= 5: dist += 2
    pos = itm.pos
    sq = pos.get_near_tiles(dist)
    casting = BloodRaining
    casting.turns = randint(2,3)
    roll = basics.roll_dice(1)
    if roll >= 5: casting.turns += 1 
    if roll >= 6: casting.turns += 3
    for s in sq:
      if casting.name not in [ev.name for ev in s.events]:
        s.events += [casting(s)]
        s.events = [evt for evt in s.events if evt.name != Rain.name
                    and evt.name != Storm.name]


class CastMist(Spell):
  name = 'cast mist'
  cast = 1#10
  cost = 1#20
  type = spell_t
  tags = ['weather']

  def ai_run(self,itm):
    self.init(itm)

  def run(self, itm):
    if itm.show_info: sleep(loadsound('spell27', channel=ch5, vol=0.7) / 2)
    msg = f'spell {self.name}'
    itm.log[-1] += [msg]
    logging.debug(msg)
    pos = itm.pos
    casting = Rain
    casting.turns = randint(2,4)
    if casting.name not in [ev.name for ev in pos.name]:
        pos.events += [casting(pos)]


class CastRain(Spell):
  name = 'cast rain'
  cast = 1#10
  cost = 1#20
  type = spell_t
  tags = ['weather']

  def ai_run(self, itm):
    tiles = itm.pos.get_near_tiles(2)
    tiles = [t for t in tiles if t.sight]
    raining = 0
    for t in tiles:
      if BloodRaining.name in [ev.name for ev in t.events]: raining = 1
    if raining: self.init(itm)

  def run(self, itm):
    if itm.show_info: sleep(loadsound('spell27', channel=ch5, vol=0.7) / 2)
    msg = f'spell {self.name}'
    itm.log[-1] += [msg]
    logging.debug(msg)
    dist = 3
    roll = roll_dice(1)
    if roll >= 6: dist += 2
    elif roll >= 5: dist += 1
    pos = itm.pos
    sq = pos.get_near_tiles(dist)
    casting = Rain
    casting.turns = randint(2,4)
    roll = basics.roll_dice(1)
    if roll >= 5: casting.turns += 1 
    if roll >= 6: casting.turns += 2 
    for s in sq:
      if all(i not in [Storm.name, Rain.name] for i in [ev.name for ev in s.events]):
        s.events += [casting(s)]
        s.events = [evt for evt in s.events if evt.name != BloodRaining.name]


class CastStorm(Spell):
  name = 'storm'
  cast = 1#0
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
    if itm.show_info: sleep(loadsound('spell27', channel=ch5, vol=0.7) / 2)
    msg = f'spell {self.name}'
    itm.log[-1] += [msg]
    logging.debug(msg)
    dist = 1
    roll = roll_dice(1)
    if roll >= 6: dist += 2
    elif roll >= 5: dist += 1
    pos = itm.pos
    sq = pos.get_near_tiles(dist)
    casting = Storm
    casting.turns = randint(2,4)
    roll = basics.roll_dice(1)
    if roll >= 6: casting.turns += 2 
    for s in sq:
      if all(i not in [Storm.name] for i in [ev.name for ev in s.events]):
        s.events += [casting(s)]
        s.events = [evt for evt in s.events if evt.name != BloodRaining.name]
        s.events = [evt for evt in s.events if evt.name != Rain.name]


class CastWailingWinds(Spell):
  name = 'wailing winds'
  desc = '-1 resolve for all units. ignores (death, malignant.'
  cast = 8
  cost = 10
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
    if itm.show_info: sleep(loadsound('spell38', channel=ch5, vol=0.7))
    msg = f'spell {self.name}'
    itm.log[-1] += [msg]
    logging.debug(msg)
    dist = 1
    roll = roll_dice(1)
    if roll >= 6: dist += 2
    elif roll >= 5: dist += 1
    pos = itm.pos
    sq = pos.get_near_tiles(dist)
    casting = WailingWinds
    casting.turns = randint(2,3)
    roll = basics.roll_dice(1)
    if roll >= 5: casting.turns += 1 
    if roll >= 6: casting.turns += 2 
    for s in sq:
      if casting.name not in [ev.name for ev in s.events]:
        s.events += [casting(s)]


class HealingMists(Spell):
  desc = 'summons a mist in unit position. this mist heals all units into.'
  cost = 15
  cast = 8



class HealingRoots(Spell):
  name = 'raices curativas.'
  cost = 15
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
  desc = 'sacrifica 200 población para invocar ogros a su servicio. +50 unrest.'
  cast = 4
  cost = 20

  tile_pop = 200


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
  cast = 6
  cost = 20
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
  desc = 'sacrifica 50 población para regenerar 10 poder.'
  cast = 4
  cost = 10


class SanguineHeritage(Spell):
  desc = 'sacrifices 44 slaves to raise 1 blood knight.'



class CastSecondSun(Spell):
  name = 'cast second sun.'
  desc = 'crea un segundo sol negando la noche.'
  cost = 3#
  cast = 1#
  type = spell_t
  tags = ['weather']

  def ai_run(self, itm):
    tiles = itm.pos.get_near_tiles(5)
    tiles = [t for t in tiles if t.sight]
    go = 0
    for t in tiles:
      if malignant_t in t.units_effects or Eclipse.name in [ev.name for ev in t.events]: 
        go= 1
    if go: self.init(itm)

  def run(self, itm):
    if itm.show_info: sleep(loadsound('spell27', channel=ch5, vol=0.7) / 2)
    msg = f'spell {self.name}'
    itm.log[-1] += [msg]
    logging.debug(msg)
    dist = 5
    pos = itm.pos
    sq = pos.get_near_tiles(dist)
    casting = SecondSun
    casting.turns = randint(2,5)
    for s in sq:
      if casting.name  not in [ev.name for ev in s.events]:
        s.events += [casting(s)]
        s.events[-1].tile_run(s)



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
  cast = 10
  cost = 20
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
  cast = 10
  cost = 25
  type = 'spell'
  tags = ['summon']

  def ai_run(self, itm):
    self.init(itm)

  def run(self, itm):
    unit = itm.pos.add_unit(Driads, itm.nation.name)
    msg = f'{unit} ({summoning_t})'
    logging.debug(msg)
    itm.log[-1] += [msg]


class SummonEclipse(Spell):
  name = 'summon eclipse.'
  desc = 'summon eclipse negating the day.'
  cost = 3#
  cast = 1#
  type = spell_t
  tags = ['weather']

  def ai_run(self, itm):
    tiles = itm.pos.get_near_tiles(8)
    tiles = [t for t in tiles if t.sight]
    go = 0
    for t in tiles:
      if malignant_t in t.units_effects or SecondSun.name in [ev.name for ev in t.events]: 
        go= 1
    if go: self.init(itm)

  def run(self, itm):
    if itm.show_info: sleep(loadsound('spell27', channel=ch5, vol=0.7) / 2)
    msg = f'spell {self.name}'
    itm.log[-1] += [msg]
    logging.debug(msg)
    dist = 8
    pos = itm.pos
    sq = pos.get_near_tiles(dist)
    casting = Eclipse
    casting.turns = randint(5,8)
    for s in sq:
      if casting.name  not in [ev.name for ev in s.events]:
        s.events += [casting(s)]


class SummonForestBears(Spell):
  name = 'summon forest bears'
  cost = 15
  cast = 8
  tags = ['summon']
  type = 'spell'

  def ai_run(self, itm):
    if itm.pos.surf and itm.pos.surf == forest_t: self.init(itm)

  def run(self, itm):
    unit = itm.pos.add_unit(ForestBears, itm.nation.name)
    msg = f'{unit} ({summoning_t})'
    logging.debug(msg)
    itm.log[-1] += [msg]



class SummonFalcons(Spell):
  name = 'summon forest falcons'
  cast = 5
  cost = 10
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
  cast = 8
  cost = 30
  type = 'spell'
  tags = ['summon']

  def ai_run(self, itm):
    self.init(itm)

  def run(self, itm):
    unit = itm.pos.add_unit(SpectralInfantry, itm.nation.name)
    msg = f'{unit} ({summoning_t})'
    logging.debug(msg)
    itm.log[-1] += [msg]
