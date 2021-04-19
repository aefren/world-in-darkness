#!/usr/bin/env python
# -*- coding: utf-8 -*-
import basics
from data.lang.es import *
from data.items import *



class Spell:
  name = "skill"
  type = "spell"
  sound = "success1" 
  desc = str()
  cast = 6
  cost = 1
  tags = []

  tile_area = -1
  target = None
  traits = None

  ambient_day = 0
  ambient_night = 0
  corpses = 0
  gold = 0
  own_tile = 0
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
  unit = None
  squads = None
  units = None

  mod_pop = 0  
  mod_unrest = 0

  ranking = 0

  def __init__(self, itm):
    self.itm = itm

  def __str__(self):
    return self.name
  
  def check_cast(self, itm):
    if basics.roll_dice(2) >= self.cast: return 1
    else: 
      msg = f"{self} {failed_t}."
      if itm.show_info: 
        sp.speak(msg, 1)
        sleep(loadsound("spell11", channel=ch5) // 2)
      return msg

  def check_conditions(self, itm, target):
    msg = ""
    if self.gold and itm.nation.gold < self.gold: 
      msg += f"{self.name} {needs_t} {self.gold} {gold_t}."
    if self.target and target.type not in self.target: 
      msg += f"not {self.target} selected."
    if self.traits: pass
    if self.tile_forest and itm.pos.surf.name != forest_t: 
      msg += f"{self.name} {needs_t} {forest_t}."
    if self.tile_waste and itm.pos.soil.name != waste_t: 
      msg += f"{self.name} {needs_t} {waste_t}."
    if self.corpses and itm.pos.corpses == []: 
      msg += f"{self.name} {needs_t} corpses."
    if self.own_tile and itm.pos.nation not in itm.belongs: 
      msg += f"not own nation."
    if self.tile_pop and itm.pos.pop < self.tile_pop: msg += f"{self.name} {needs_t} {self.tile_pop} population."
    if msg: 
      if itm.nation.show_info: sleep(loadsound("errn1") * 0.5)
      return msg
    else: return None

  def check_cost(self, itm):
    if itm.power < self.cost:
      msg = f"{self}. {needs_t} {power_t}."
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
      if (any(i in self.target for i in ["beast", "cavalry", "infantry", "civil"]) 
          and target == None):
        units = [i for i in itm.pos.units 
                 if i.nation == itm.nation and i != itm]
        target = basics.get_unit(units, itm.nation)
        if target == None: return
    conditions = self.check_conditions(itm, target)
    if conditions != None: return conditions
    check = self.check_cost(itm)
    if check != 1: return check
    cast = self.check_cast(itm)
    if cast != 1: return cast
    if itm.show_info: sleep(loadsound("self.sound")/2)
    if target:self.run(itm, target)
    else: 
      if self.type == "recruit": self.recruit(itm)
      elif self.type == summoning_t: self.recruit(itm)
      else: self.run(itm)
    
  def msg_upkeep_limit(self, itm):
    return f"{itm} can't summon {self} by upkeep_limit."

  def recruit(self, itm, nation=None, info=1):
    if nation: nation = nation
    else: nation = itm.nation.name
    if self.squads: itm.pos.add_unit(self.unit, nation, squads=self.squads)
    elif self.unit: itm.pos.add_unit(self.unit, nation, units=self.units)
    self.set_msg1(itm, self.unit)
    itm.pos.pop += self.mod_pop
    itm.pos.unrest += self.mod_unrest

    msg = f"{itm} {recruits_t} {self.unit} {on_t} {itm.pos} {itm.pos.cords}."
    if info: logging.debug(msg)
    itm.log[-1] += [msg]
    itm.pos.world.log[-1] += [msg]  
  def run(self):
    pass

  def set_msg0(self, itm):
    msg = f"{itm} spell {self.name} in {itm.pos} {itm.pos.cords}."
    itm.log[-1] += [msg]
    logging.debug(msg)
    if itm.pos.world:itm.pos.world.log[-1] += [msg]

  def set_msg1(self, itm, unit):
    msg = f"{unit} ({summoning_t}) on {itm.pos} {itm.pos.cords}."
    logging.debug(msg)
    itm.log[-1] += [msg]
    itm.pos.world.log[-1] += [msg]
  def summon(self, itm, nation=None, info=1):
    if nation: nation = nation
    else: nation = itm.nation.name
    if self.squads: itm.pos.add_unit(self.unit, nation, squads=self.squads)
    elif self.unit: itm.pos.add_unit(self.unit, nation, units=self.units)
    self.set_msg1(itm, self.unit)
    itm.pos.pop += self.mod_pop
    itm.pos.unrest += self.mod_unrest
    
    msg = f"{itm} {summons_t} {self.unit} {on_t} {itm.pos} {itm.pos.cords}."
    if info: logging.debug(msg)
    itm.log[-1] += [msg]
    itm.pos.world.log[-1] += [msg]


class FeastForBaal(Spell):
  name = "feast for baal"
  cast = 1
  cost = 0
  type = spell_t
  tags = ["feeding", "cannibalize"]

  def ai_run(self, itm):
    if FeedingFrenzy.name not in [s.__class__.name for s in itm.skills] and itm.pos.corpses: self.run(itm) 

  def run(self, itm):
    itm.update()
    if (FeedingFrenzy.name not in [s.__class__.name for s in itm.skills] 
        and itm.pos.corpses):
      corpses = sum(sum(i.deads) for i in itm.pos.corpses)
      sk = FeedingFrenzy(itm)
      if corpses >= itm.units: 
        sk.turns = 5
        sk.name += f" full" 
        times = itm.units
        for cr in itm.pos.corpses:
          if times <= 0: break
          for r in range(times):
            if cr.deads[0] < 1: break
            cr.deads[0] -= 1
            times -= 1
            if times < 1: break
      elif corpses >= 50 * itm.units / 100: 
        sk.turns = 3
        sk.name += f" half"
        itm.pos.corpses = []
      else: 
        sk.turns = 1
        sk.name += f" low"
        itm.pos.corpses = [] 
      itm.other_skills += [sk]
      msg = f"{itm} cannivalizes {corpses} {corpses_t}"
      itm.log[-1] += [msg]
      if itm.show_info: sleep(loadsound("spell37") // 2)
    else:
      itm.log[-1] += [f"can not cannivalize"] 
      if itm.show_info: loadsound("errn1")



class BlessingWeapons(Spell):
  name = "bendecir armas"
  cost = 1  # 0
  cast = 4
  type = "spell"
  tags = [health_t]

  target = ["infantry"]
  tags = ["blessing"]

  def ai_run(self, itm):
    if itm.pos.around_threat: 
      units = [uni for uni in itm.pos.units if uni != itm
               and self.name not in [ev.name for ev in uni.other_skills]]
      if units: self.init(itm, units[0])
  
  def run(self, itm, target):
    msg = f"{itm} has removed {intoxicated_t} {from_t} {target}."
    logging.debug(msg)
    itm.log[-1] += [msg]
    target.log[-1] += [msg]
    skill = BlessedWeapons
    skill.turns = randint(2, 5)
    target.other_skills += [skill(target)]



class BloodHeal(Spell):
  name = "blood heal"
  desc = "sacrifica un número aleatoreo de población para curarse."
  cast = 6
  cost = 10
  type = "spell"

  tile_pop = 20
  tags = ["restoration"]

  def ai_run(self, itm):
    if itm.hp_total < itm.hp * itm.units: self.init(itm)
    
  def run(self, itm):
    if itm.nation.show_info: sleep(loadsound("spell42", channel=ch3))
    itm.pos.pop -= 20
    itm.hp_total += 5
    itm.update()
    msg = f"{itm} recovers 5 hp."
    logging.debug(msg)
    itm.log[-1] += [msg]
    itm.pos.world.log[-1] += [msg]



class BreathOfTheDesert(Spell):
  desc = "Envía aires del desierto a una casilla elegida. esto subirá la temperatura y dañara la producción de alimentos."



class CastBloodRain(Spell):
  name = "blood rain"
  cast = 8
  cost = 20
  type = spell_t
  tags = ["weather"]

  def ai_run(self, itm):
    tiles = itm.pos.get_near_tiles(1)
    raining = 0
    for t in tiles:
      if self.name in [ev.name for ev in t.events]: raining = 1
    if (raining == 0 and (itm.pos.around_threat > itm.pos.defense 
                          or itm.pos.city and itm.pos.city.seen_threat > itm.pos.city.defense)): self.init(itm)

  def run(self, itm):
    if itm.show_info: sleep(loadsound("spell27", channel=ch5, vol=0.7) / 2)
    self.set_msg0(itm)
    dist = 2
    roll = basics.roll_dice(1)
    if roll >= 6: dist += 4
    elif roll >= 5: dist += 2
    pos = itm.pos
    sq = pos.get_near_tiles(dist)
    casting = BloodRaining
    casting.turns = randint(2, 3)
    roll = basics.roll_dice(1)
    if roll >= 5: casting.turns += 1 
    if roll >= 6: casting.turns += 3
    for s in sq:
      if casting.name not in [ev.name for ev in s.events]:
        s.events += [casting(s)]
        s.events = [evt for evt in s.events if evt.name != Rain.name
                    and evt.name != Storm.name]



class EatCorpses(Spell):
  name = "eat corpse"
  cast = 1
  cost = 0
  type = spell_t
  tags = ["feeding", "cannibalize"]

  def ai_run(self, itm):
    if FeedingFrenzy.name not in [s.__class__.name for s in itm.skills] and itm.pos.corpses: self.run(itm) 

  def run(self, itm):
    itm.update()
    if (FeedingFrenzy.name not in [s.__class__.name for s in itm.skills] 
        and itm.pos.corpses):
      corpses = sum(sum(i.deads) for i in itm.pos.corpses)
      sk = FeedingFrenzy(itm)
      if corpses >= itm.units: 
        sk.turns = 5
        sk.name += f" full" 
        times = itm.units
        for cr in itm.pos.corpses:
          if times <= 0: break
          for r in range(times):
            if cr.deads[0] < 1: break
            cr.deads[0] -= 1
            times -= 1
            if times < 1: break
      elif corpses >= 50 * itm.units / 100: 
        sk.turns = 3
        sk.name += f" half"
        itm.pos.corpses = []
      else: 
        sk.turns = 1
        sk.name += f" low"
        itm.pos.corpses = [] 
      itm.other_skills += [sk]
      msg = f"{itm} cannivalizes {corpses} {corpses_t}"
      itm.log[-1] += [msg]
      if itm.show_info: sleep(loadsound("spell37") // 2)
    else:
      itm.log[-1] += [f"can not cannivalize"] 
      if itm.show_info: loadsound("errn1")



class CastLocustSwarm(Spell):
  name = "cast locust swarm"
  cast = 10
  cost = 15
  tile_waste = 1
  type = spell_t
  tags = ["plague"]

  def ai_run(self, itm):
    self.init(itm)

  def run(self, itm):
    if itm.show_info: sleep(loadsound("spell27", channel=ch5, vol=0.7) / 2)
    self.set_msg0(itm)
    pos = itm.pos
    casting = LocustSwarm
    pos.events += [casting(pos)]



class CastMist(Spell):
  name = "cast mist"
  cast = 10
  cost = 10
  type = spell_t
  tags = ["weather"]

  def ai_run(self, itm):
    self.init(itm)

  def run(self, itm):
    if itm.show_info: sleep(loadsound("spell27", channel=ch5, vol=0.7) / 2)
    self.set_msg0(itm)
    pos = itm.pos
    casting = Rain
    casting.turns = randint(2, 4)
    if casting.name not in [ev.name for ev in pos.name]:
        pos.events += [casting(pos)]



class CastRain(Spell):
  name = "cast rain"
  cast = 9
  cost = 20
  type = spell_t
  tags = ["weather"]

  def ai_run(self, itm):
    tiles = itm.pos.get_near_tiles(2)
    tiles = [t for t in tiles if t.sight]
    raining = 0
    for t in tiles:
      if BloodRaining.name in [ev.name for ev in t.events]: raining = 1
    if raining: self.init(itm)

  def run(self, itm):
    if itm.show_info: sleep(loadsound("spell27", channel=ch5, vol=0.7) / 2)
    self.set_msg0(itm)
    dist = 3
    roll = basics.roll_dice(1)
    if roll >= 6: dist += 2
    elif roll >= 5: dist += 1
    pos = itm.pos
    sq = pos.get_near_tiles(dist)
    casting = Rain
    casting.turns = randint(2, 3)
    if itm.pos.ambient.sseason == winter_t: casting.turns += randint(2, 4)
    if basics.roll_dice(1) == 6: casting.turns += 2
    if itm.pos.soil.name == waste_t: casting.turns = randint(1, 2)
    for s in sq:
      if all(i not in [Storm.name, Rain.name] for i in [ev.name for ev in s.events]):
        s.events += [casting(s)]
        s.events = [evt for evt in s.events if evt.name != BloodRaining.name]



class CastRainOfToads(Spell):
  name = "lluvia de sapos"
  desc = "cast toads raining"
  cast = 8
  cost = 20
  type = spell_t
  tags = ["disease", "unrest", "miasma"]

  def ai_run(self, itm):
    tiles = itm.pos.get_near_tiles(1)
    raining = 0
    nations = 0
    hostiles = 0
    for t in tiles:
      if self.name in [ev.name for ev in t.events]: raining += 1
      if t.around_nations: nations += len(t.around_nations)
      if t .units: hostiles += len([u.units for u in t.units if u.nation not in itm.belongs])
    if ((raining <= 6 and nations >= 2) 
        or itm.pos.city and itm.pos.city.seen_threat >= itm.pos.city.defense
        or hostiles and raining <= 6): 
      self.init(itm)

  def run(self, itm):
    if itm.show_info: sleep(loadsound("spell27", channel=ch5, vol=0.7) / 2)
    self.set_msg0(itm)
    dist = 1
    roll = basic.roll_dice(1)
    if roll >= 5: dist += 1
    pos = itm.pos
    sq = pos.get_near_tiles(dist)
    casting = RainOfToads
    casting.turns = randint(3, 7)
    roll = basics.roll_dice(1)
    if roll >= 5: casting.turns += 1 
    if roll >= 6: casting.turns += 3
    for s in sq:
      if casting.name not in [ev.name for ev in s.events]:
        s.events += [casting(s)]



class CastStorm(Spell):
  name = "storm"
  cast = 10
  cost = 20
  type = spell_t
  tags = ["weather"]

  def ai_run(self, itm):
    tiles = itm.pos.get_near_tiles(1)
    raining = 0
    for t in tiles:
      if self.name in [ev.name for ev in t.events]: raining = 1
    if raining == 0: self.init(itm)

  def run(self, itm):
    if itm.show_info: sleep(loadsound("spell27", channel=ch5, vol=0.7) / 2)
    self.set_msg0(itm)
    dist = 1
    roll = basics.roll_dice(1)
    if roll >= 6: dist += 2
    elif roll >= 5: dist += 1
    pos = itm.pos
    sq = pos.get_near_tiles(dist)
    casting = Storm
    casting.turns = randint(2, 3)
    if itm.pos.ambient.sseason == winter_t: casting.turns += randint(1, 2)
    if roll >= 6: casting.turns += 2
    if itm.pos.soil.name == waste_t: casting.turns = 1 
    for s in sq:
      if all(i not in [Storm.name] for i in [ev.name for ev in s.events]):
        s.events += [casting(s)]
        s.events = [evt for evt in s.events if evt.name != BloodRaining.name]
        s.events = [evt for evt in s.events if evt.name != Rain.name]



class CastWailingWinds(Spell):
  name = "wailing winds"
  desc = "-1 resolve for all units. ignores (death, malignant."
  cast = 8
  cost = 10
  ranking = 0
  tags = ["morale"]
  type = "spell"

  def ai_run(self, itm):
    tiles = itm.pos.get_near_tiles(1)
    wailing = 0
    for t in tiles:
      if self.name in [ev.name for ev in t.events]: wailing = 1
    if wailing == 0: self.init(itm)

  def run(self, itm):
    if itm.show_info: sleep(loadsound("spell38", channel=ch5, vol=0.7))
    self.set_msg0(itm)
    dist = 1
    roll = basics.roll_dice(1)
    if roll >= 6: dist += 2
    elif roll >= 5: dist += 1
    pos = itm.pos
    sq = pos.get_near_tiles(dist)
    casting = WailingWinds
    casting.turns = randint(2, 3)
    roll = basics.roll_dice(1)
    if roll >= 5: casting.turns += 1 
    if roll >= 6: casting.turns += 2 
    for s in sq:
      if casting.name not in [ev.name for ev in s.events]:
        s.events += [casting(s)]



class Curse(Spell):
  name = "curse"
  desc = "if success target gets diseased."
  cast = 6
  cost = 9
  type = "spell"

  target = ["beast", "cavalry", "civil", "infantry"]
  tags = ["healer"]

  def ai_run(self, itm):
    units = [i for i in itm.pos.units if itm.nation not in i.belongs
             and self.name not in i.global_skills]
    
    if units:
      units.sort(key=lambda x: x.ranking, reverse=True) 
      self.init(itm, units[0])

  def run(self, itm, target):
    if itm.nation.show_info: sleep(loadsound("spell42", channel=ch3))
    sk = Diseased(itm)
    sk.turns = randint(1, 4)
    if sk.name not in [s.name for s in target.global_skills]:
      target.global_skills += [sk]
    msg = f"{itm} has cursed {to_t} {target}."
    logging.debug(msg)
    itm.log[-1] += [msg]
    itm.pos.world.log[-1] += [msg]
    target.log[-1] += [msg]



class HealingMists(Spell):
  desc = "summons a mist in unit position. this mist heals all units into."
  cast = 8
  cost = 15



class HealingRoots(Spell):
  name = "raices curativas."
  desc = "removes target poison effects."
  cast = 4
  cost = 15
  type = "spell"

  target = ["beast", "cavalry", "civil", "infantry"]
  tags = ["healer"]
  ranking = 1.2

  def ai_run(self, itm):
    units = [i for i in itm.pos.units if i.nation == itm.nation
             and intoxicated_t in i.global_skills]
    
    if units: self.init(itm, units[0])

  def run(self, itm, target):
    if itm.nation.show_info: sleep(loadsound("spell42", channel=ch3))
    target.other_skills = [sk for sk in target.other_skills if sk.name != intoxicated_t]
    msg = f"{itm} has removed {intoxicated_t} {from_t} {target}."
    logging.debug(msg)
    itm.log[-1] += [msg]
    target.log[-1] += [msg]



class Eartquake(Spell):
  pass



class EnchantedForests(Spell):
  pass



class FeastOfFlesh(Spell):
  name = "feast of flesh"
  desc = "sacrifica 200 población para invocar ogros a su servicio. +50 unrest."
  cast = 4
  cost = 20

  tile_pop = 200



class FireDarts(Spell):
  pass



class GiftForTheNight(Spell):
  name = "gift for the night"
  cast = 10
  cost = 12
  type = "spell"
  tags = ["summon"]

  def ai_run(self, itm):
    if itm.nation.upkeep_limit and itm.nation.upkeep > itm.nation.upkeep_limit: return self.msg_upkeep_limit(itm) 
    self.init(itm)

  def run(self, itm):
    unit = itm.pos.add_unit(WoodlandSpirit, itm.nation.name)
    unit.hp_total = randint(unit.hp, unit.hp * 5)
    self.set_msg1(itm, unit)



class MagicDuel(Spell):
  pass



class Mist(Spell):
  pass



class PoisonCloud(Spell):
  pass



class RaiseDead(Spell):
  name = raise_dead_t
  cast = 6
  cost = 5
  ranking = 10
  type = "spell34"
  tags = ["reanimating"]

  corpses = 1
  ranking = 1.2

  def ai_run(self, itm):
    if itm.pos.corpses: self.run(itm)

  def run(self, itm):
    logging.info(f"{self.name}. ({itm}).")
    tile = itm.pos
    
    total_hp = randint(30,90)
    dead = choice(tile.corpses)
    raised = choice(dead.corpses)(itm.nation)
    if sum(dead.deads)*total_hp >= total_hp: 
      raised.hp_total = total_hp
      dead.deads[0] -= total_hp/5
    else: 
      raised.hp_total = sum(dead.deads) * raised.hp
      tile.corpses.remove(dead)
    raised.update()
    logging.debug(f"unidades totales de {dead} {sum(dead.deads)}.")
    logging.debug(f"{raised} unidades {raised.units}. hp {raised.hp}.")
    
    msg = f"{itm} lanza {self.name}."
    logging.info(msg)
    raised.auto_attack()
    raised.pos = tile
    raised.pos.units.append(raised)
    msg = f"reanimados {raised}."
    itm.log[-1].append(msg)
    if itm.nation.show_info: sleep(loadsound("raiseundead1") / 2)
    itm.pos.update(itm.nation)



class RecruitForestGuards(Spell):
  name = "recruit forest guards"
  type = "recruit"
  desc = "recruit 1 forest guard squad.."
  cost = 1
  cast = 1
  unit = ForestGuard
  squads = 1

  mod_pop = -15
  mod_unrest = 2  
  own_tile = 1
  tile_pop = 15

  type = "recruit"
  tags = ["recruit"]
  ranking = 1.15

  def ai_run(self, itm):
    buildings = [b for b in itm.pos.buildings if b.nation == itm.nation]
    if itm.pos.public_order < 0 and itm.pos.unrest < 20: self.init(itm)
    if (itm.pos.around_threat + itm.pos.threat > itm.pos.defense * 2
        and buildings): self.init(itm)


class RecruitPeasants(Spell):
  name = "recruit peasants"
  type = "recruit"
  desc = "recruit 1 peasant squad.."
  cost = 1
  cast = 1
  unit = PeasantLevy
  squads = 1

  mod_pop = -20
  mod_unrest = 4  
  own_tile = 1
  tile_pop = 20

  tags = ["recruit"]
  ranking = 1.1

  def ai_run(self, itm):
    buildings = [b for b in itm.pos.buildings if b.nation == itm.nation]
    if itm.pos.public_order < 0 and itm.pos.unrest < 20: self.init(itm)
    if (itm.pos.around_threat + itm.pos.threat > itm.pos.defense * 2
        and buildings): self.init(itm)


class RecruitLevy(Spell):
  name = "recruit Levy"
  type = "recruit"
  desc = "recruit 1 levy squad.."
  cost = 2
  cast = 1
  unit = Levy
  squads = 1

  mod_pop = -20
  mod_unrest = 4  
  own_tile = 1
  tile_pop = 20

  tags = ["recruit"]
  ranking = 1.15

  def ai_run(self, itm):
    buildings = [b for b in itm.pos.buildings if b.nation == itm.nation]
    if itm.pos.public_order < 0 and itm.pos.unrest < 20: self.init(itm)
    if (itm.pos.around_threat + itm.pos.threat > itm.pos.defense * 2
        and buildings): self.init(itm)


class RecruitSlaveWarriors(Spell):
  name = "recruit slave warriors"
  type = "recruit"
  desc = "recruit 1 slave warrior squad.."
  cost = 2
  cast = 1
  units = SlaveWarrior
  squads = 1

  mod_pop = -30
  mod_unrest = 10
  own_tile = 1
  tile_pop = 30

  tags = ["recruit"]
  ranking = 1.2

  def ai_run(self, itm):
    buildings = [b for b in itm.pos.buildings if b.nation == itm.nation]
    if itm.pos.public_order < 0 and itm.pos.unrest < 20: self.init(itm)
    if (itm.pos.around_threat + itm.pos.threat > itm.pos.defense * 2
        and buildings): self.init(itm)


class Reinvigoration(Spell):
  desc = "sacrifica 50 población para regenerar 20 poder."
  cost = 10
  cast = 4



class Returning(Spell):
  name = "retorno"
  desc = "caster can teleport fastly to nation city capital. chance to be lost in time and return later or insane."
  cast = 8
  cost = 30 
  type = spell_t
  tags = ["teleport"]

  def ai_run(self, itm):
    go = 0
    if (itm.pos.around_threat > itm.pos.defense * 1.5 
        or itm.nation.cities[0].seen_threat > itm.nation.cities[0].defense_total):
      go = 1
    if itm.pos == itm.pos.nation.cities[0].pos: go = 0
    if go: self.init(itm)

  def run(self, itm):
    msg = f"spell {self.name}"
    itm.log[-1] += [msg]
    logging.debug(msg)
    if itm.nation.show_info: sleep(loadsound("spell41", channel=ch5) * 0.5)
    itm.mp[0] = 0
    pos = itm.pos
    itm.nation.cities[0].pos.units += [itm]
    pos.units.remove(itm)
    itm.pos = itm.nation.cities[0].pos
    if basics.roll_dice(1) >= 5:
      blocked = randint(1, 4)
      roll = basics.roll_dice(1)
      if roll >= 6: blocked += 6
      elif roll >= 5: blocked += 3
      itm.blocked = blocked
      itm.pos.units_blocked += [itm]
      msg = f"{itm} is lost on time."
      itm.log[-1] += [msg]
      itm.nation.log[-1] += [msg]



class SanguineHeritage(Spell):
  desc = "sacrifices 44 slaves to raise 1 blood knight."



class SightFromFuture(Spell):
  name = "vista desde el futuro"
  desc = "shows all near hidden units."
  cast = 6
  cost = 15
  type = spell_t
  tags = ["rebelation"]

  def ai_run(self, itm):
    if itm.pos.around_threat > itm.pos.defense: self.init(self, itm)

  def run(self, itm):
    self.set_msg0(itm)
    logging.debug(msg)
    if itm.nation.show_info: sleep(loadsound("spell41", channel=ch5) * 0.5)
    tiles = itm.pos.get_near_tiles(1)
    for t in tiles:
      for uni in t.units:
        if uni.nation not in itm.belongs: uni.revealed = 1


class SummonBloodKnight(Spell):
  name = "summon blood knight"
  type = summoning_t
  cast = 1
  cost = 20
  unit = BloodKnight
  tags = ["summon"]

  def ai_run(self, itm):
    if itm.nation.upkeep_limit and itm.nation.upkeep > itm.nation.upkeep_limit: return self.msg_upkeep_limit(itm) 
    self.init(itm)

  def run(self, itm):
    unit = itm.pos.add_unit(self.unit, itm.nation.name)
    self.set_msg1(itm, unit)



class SummonClayGolem(Spell):
  name = "summon clay golem"
  type = summoning_t
  cast = 9
  cost = 18
  unit = ClayGolem
  squads = 1
  tags = ["summon"]

  def ai_run(self, itm):
    if itm.nation.upkeep_limit and itm.nation.upkeep >= itm.nation.upkeep_limit: return self.msg_upkeep_limit(itm) 
    self.init(itm)

  def run(self, itm):
    unit = itm.pos.add_unit(ClayGolem, itm.nation.name, squads=self.squads)
    self.set_msg1(itm, unit)



class SummonSecondSun(Spell):
  name = "cast second sun."
  desc = "crea un segundo sol negando la noche."
  cast = 9
  cost = 40
  type = spell_t
  tags = ["weather"]

  def ai_run(self, itm):
    tiles = itm.pos.get_near_tiles(5)
    tiles = [t for t in tiles if t.sight]
    go = 0
    for t in tiles:
      if malignant_t in t.units_effects or Eclipse.name in [ev.name for ev in t.events]: 
        go = 1
    if go: self.init(itm)

  def run(self, itm):
    if itm.show_info: sleep(loadsound("spell27", channel=ch5, vol=0.7) / 2)
    self.set_msg0(itm)
    dist = 5
    pos = itm.pos
    sq = pos.get_near_tiles(dist)
    casting = SecondSun
    casting.turns = randint(2, 5)
    for s in sq:
      if casting.name  not in [ev.name for ev in s.events]:
        s.events += [casting(s)]
        s.events[-1].tile_run(s)



class SummonAwakenTree(Spell):
  name = "summon awaken tree"
  type = summoning_t
  cast = 4
  cost = 15
  unit = AwakenTree
  Squads = 1
  tags = ["summon"]

  tile_forest = 1

  def ai_run(self, itm):
    if itm.nation.upkeep_limit and itm.nation.upkeep > itm.nation.upkeep_limit: return self.msg_upkeep_limit(itm)
    self.init(itm)

  def run(self, itm):
    unit = itm.pos.add_unit(self.unit, itm.nation.name, squads=self.squads)
    self.set_msg1(itm, unit)



class SummonDevourerOfDemons(Spell):
  name = "summon devourer of demons"
  type = summoning_t
  cast = 10
  cost = 20
  unit = DevourerOfDemons
  squads = 1
  tags = ["summon"]

  def ai_run(self, itm):
    if itm.pos.around_nations and itm.pos.around_snation == []:
      self.init(itm)

  def run(self, itm):
    unit = itm.pos.add_unit(self.unit, wild_t, squads=self.squads)
    self.set_msg1(itm, unit)



class SummonDraugr(Spell):
  name = "summon draugr"
  type = summoning_t
  cast = 4
  cost = 10
  unit = Draugr
  tags = ["summon"]

  tile_forest = 1

  def ai_run(self, itm):
    if itm.nation.upkeep_limit and itm.nation.upkeep > itm.nation.upkeep_limit: return self.msg_upkeep_limit(itm)
    self.init(itm)

  def run(self, itm):
    unit = itm.pos.add_unit(self.unit, itm.nation.name, squads=self.squads)
    self.set_msg1(itm, unit)



class SummonDriads(Spell):
  name = "summon driads"
  type = summoning_t
  cast = 10
  cost = 25
  tile_forest = 1
  unit = Driad
  squads = 1
  tags = ["summon"]

  def ai_run(self, itm):
    if itm.nation.upkeep_limit and itm.nation.upkeep > itm.nation.upkeep_limit: return self.msg_upkeep_limit(itm)
    self.init(itm)

  def run(self, itm):
    unit = itm.pos.add_unit(self.unit, itm.nation.name, squads=self.squads)
    self.set_msg1(itm, unit)



class SummonEclipse(Spell):
  name = "summon eclipse."
  type = spell_t
  desc = "summon eclipse negating the day."
  cast = 10
  cost = 50
  tags = ["weather"]

  def ai_run(self, itm):
    tiles = itm.pos.get_near_tiles(8)
    tiles = [t for t in tiles if t.sight]
    go = 0
    for t in tiles:
      if malignant_t in t.units_effects or SecondSun.name in [ev.name for ev in t.events]: 
        go = 1
    if go: self.init(itm)

  def run(self, itm):
    if itm.show_info: sleep(loadsound("spell27", channel=ch5, vol=0.7) / 2)
    self.set_msg0(itm)
    dist = 8
    pos = itm.pos
    sq = pos.get_near_tiles(dist)
    casting = Eclipse
    casting.turns = randint(5, 8)
    for s in sq:
      if casting.name  not in [ev.name for ev in s.events]:
        s.events += [casting(s)]



class SummonForestBears(Spell):
  name = "summon forest bears"
  type = summoning_t
  cast = 8
  cost = 15
  tile_forest = 1
  unit = ForestBear
  squads = 1
  tags = ["summon"]

  def ai_run(self, itm):
    if (itm.pos.surf.name == forest_t 
        and itm.nation.upkeep_limit and itm.nation.upkeep > itm.nation.upkeep_limit): return self.msg_upkeep_limit(itm)
    self.init(itm)

  def run(self, itm):
    unit = itm.pos.add_unit(self.unit, itm.nation.name, squads=self.squads)
    self.set_msg1(itm, unit)



class SummonGiantBears(Spell):
  name = "summon giant bears"
  type = summoning_t
  cast = 6
  cost = 10
  tile_forest = 1
  unit = GiantBear
  squads = 1
  tags = ["summon"]

  def ai_run(self, itm):
    if (itm.pos.threat + itm.pos.around_threat > itm.pos.defense 
        and itm.nation.upkeep_limit and itm.nation.upkeep > itm.nation.upkeep_limit): return self.msg_upkeep_limit(itm) 
    self.init(itm)

  def run(self, itm):
    unit = itm.pos.add_unit(self.unit, itm.nation.name)
    unit.hp_total = randint(unit.hp, unit.hp * 2)
    self.set_msg1(itm, unit)



class SummonFalcons(Spell):
  name = "summon forest falcons"
  type = summoning_t
  cast = 5
  cost = 10
  unit = Falcon
  tags = ["summon"]

  def ai_run(self, itm):
    if itm.nation.upkeep_limit and itm.nation.upkeep > itm.nation.upkeep_limit: return self.msg_upkeep_limit(itm) 
    self.init(itm)

  def run(self, itm):
    unit = itm.pos.add_unit(self.unit, itm.nation.name)
    self.set_msg1(itm, unit)



class SummonMandeha(Spell):
  name = "summon mandeha"
  type = summoning_t
  cast = 8
  cost = 35
  unit = Mandeha
  tags = ["summon"]

  def ai_run(self, itm):
    self.init(itm)

  def run(self, itm):
    unit = itm.pos.add_unit(self.unit, itm.nation.name)
    self.set_msg1(itm, unit) 



class SummonSkeletonWarriors(Spell):
  name = "summon skeleton warriors"
  type = summoning_t
  cast = 6
  cost = 20
  unit = SkeletonWarrior
  tags = ["summon"]

  def ai_run(self, itm):
    if itm.nation.upkeep_limit and itm.nation.upkeep > itm.nation.upkeep_limit: return self.msg_upkeep_limit(itm) 
    self.init(itm)

  def run(self, itm):
    unit = itm.pos.add_unit(self.unit, itm.nation.name)
    self.set_msg1(itm, unit)



class SummonSpectralInfantry(Spell):
  name = "summon spectral infantry"
  type = summoning_t
  cast = 8
  cost = 20
  unit = SpectralInfantry
  tags = ["summon"]

  def ai_run(self, itm):
    if itm.nation.upkeep_limit and itm.nation.upkeep > itm.nation.upkeep_limit: return self.msg_upkeep_limit(itm) 
    self.init(itm)

  def run(self, itm):
    unit = itm.pos.add_unit(self.unit, itm.nation.name)
    self.set_msg1(itm, unit)



class SummonWoodlandSpirit(Spell):
  name = "summon woodland spirit"
  type = summoning_t
  cast = 10
  cost = 20
  tile_forest = 1
  unit = WoodlandSpirit
  tags = ["summon"]

  def ai_run(self, itm):
    if itm.nation.upkeep_limit and itm.nation.upkeep > itm.nation.upkeep_limit: return self.msg_upkeep_limit(itm)
    self.init(itm)

  def run(self, itm):
    unit = itm.pos.add_unit(self.unit, itm.nation.name)
    self.set_msg1(itm, unit)

