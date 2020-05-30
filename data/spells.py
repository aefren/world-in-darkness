#!/usr/bin/env python
# -*- coding: utf-8 -*-
from data.lang.es import *
from data.items import *


class BloodHeal(Skill):
  desc = 'sacrifica un número aleatoreo de población para curarse.'


class BreathOfTheDesert(Skill):
  desc = 'Envía aires del desierto a una casilla elegida. esto subirá la temperatura y dañara la producción de alimentos.'


class CastBloodRain(Skill):
  name = 'blood rain'
  cost = 40
  cast = 10
  ranking = 5
  type = spell_t

  def ai_run(self, itm):
    self.init(itm)
  def run(self, itm):
    sleep(loadsound('spell27', channel = ch5, vol = 0.7) / 2)
    dist = randint(3, 6)
    pos = itm.pos
    sq = pos.get_near_tiles(itm.pos.scenary, dist)
    for s in sq:
      if self.name not in [ev.name for ev in s.events]:
        s.events += [BloodRaining(s)]


class HealingMists(Skill):
  desc = 'summons a mist in unit position. this mist heals all units into.'


class HealingRoots(Skill):
  name = 'raices curativas.'
  cost = 10
  cast = 4
  ranking = 5
  type = 'spell'
  tags = [health_t]

  def ai_run(self, itm):
    units = [i for i in itm.pos.units if i.nation == itm.nation
             and intoxicated_t in i.global_skills]
    
    if units: self.init(itm)

  def run(self, itm):
    if roll_dice(2) >= cast:
      units = [i for i in itm.pos.units if i.nation == itm.nation]
      unit = choice(units)
      unit.other_skills = [sk for sk in unit.other_skills if sk.name != intoxicated_t]
      msg = f'{itm} has removed {intoxicated_t} {from_t} {unit}.'
      logging.debug(msg)
      itm.log[-1] += [msg]
      unit.log[-1] += [msg]


class Eartquake(Skill):
  pass


class EnchantedForests(Skill):
  pass


class FeastOfFlesh(Skill):
  desc = 'sacrifica x población para invocar ogros a su servicio.'


class FireDarts(Skill):
  pass


class MagicDuel(Skill):
  pass



class Mist(Skill):
  pass


class PoisonCloud(Skill):
  pass


class RaiseDead(Skill):
  name = raise_dead_t
  cost = 20
  cast = 6
  ranking = 10
  type = 'spell34'
  tags = [raise_dead_t]

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


class Reinvigoration(Skill):
  desc = 'sacrifica x población para regenerar poder.'


class SanguineHeritage(Skill):
  desc = 'sacrifices 44 slaves to raise 1 blood knight.'


class SecondSun(Skill):
  desc = 'crea un segundo sol negando la noche y dañando la agricultura de los lugares afectados.'


class SummonAwakenTree(Skill):
  name = 'summon awaken tree'
  cost = 20
  cast = 8
  ranking = 5
  type = 'spell'
  tags = ['summon']

  def ai_run(self, itm):
    self.init(itm)

  def run(self, itm):
    itm.pos.add_unit(AwakenTree, itm.nation.name)
    msg = f'{AwakenTree} has been sommoned'
    logging.debug(msg)
    itm.log[-1] += [msg]


class SummonDevourerOfDemons(Skill):
  name = 'summon devourer of demons'
  cost = 1
  cast = 1
  ranking = 5
  type = 'spell'
  tags = ['summon']

  def ai_run(self, itm):
    if itm.pos.around_nations and itm.pos.around_snation == []:
      self.init(itm)

  def run(self, itm):
    itm.pos.add_unit(DevourerOfDemons, wild_t)
    msg = f'{DevourerOfDemons} has been sommoned'
    logging.debug(msg)
    itm.log[-1] += [msg]


class SummonDriads(Skill):
  name = 'summon driads'
  cost = 1
  cast = 1
  ranking = 5
  type = 'spell'
  tags = ['summon']

  def ai_run(self, itm):
    self.init(itm)

  def run(self, itm):
    itm.pos.add_unit(Driads, itm.nation.name)
    msg = f'{Driads} has been sommoned'
    logging.debug(msg)
    itm.log[-1] += [msg]



class SummonForestBears(Skill):
  name = 'summon forest bears'
  cost = 1
  cast = 1
  ranking = 5
  type = 'spell'
  tags = ['summon']

  def ai_run(self, itm):
    if itm.pos.surf and itm.pos.surf == forest_t: self.init(itm)

  def run(self, itm):
    itm.pos.add_unit(ForestBears, itm.nation.name)
    msg = f'{ForestBears} has been sommoned'
    logging.debug(msg)
    itm.log[-1] += [msg]



class SummonFalcons(Skill):
  name = 'summon forest falcons'
  cost = 1
  cast = 1
  ranking = 5
  type = 'spell'
  tags = ['summon']

  def ai_run(self, itm):
    if itm.pos.surf and itm.pos.surf == forest_t: self.init(itm)

  def run(self, itm):
    itm.pos.add_unit(Falcons, itm.nation.name)
    msg = f'{Falcons} has been sommoned'
    logging.debug(msg)
    itm.log[-1] += [msg]


class SummonSpectralInfantry(Skill):
  name = 'summon spectral infantry'
  cost = 1
  cast = 1
  ranking = 5
  type = 'spell'
  tags = ['summon']

  def ai_run(self, itm):
    self.init(itm)

  def run(self, itm):
    itm.pos.add_unit(SpectralInfantry, itm.nation.name)
    msg = f'{SpectralInfantry} has been sommoned'
    logging.debug(msg)
    itm.log[-1] += [msg]


class WailingWinds(Skill):
  desc = 'The necromancer releases a wind of horrible screams and sighs. All enemies hearing the wailing will feel their spirits sink and have their hearts gripped with fear.'


