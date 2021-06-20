#!/usr/bin/env python
import copy

from data import weapons
from data.events import *
from language import *
from data.names import *
from data.skills import *

import basics
import numpy as np



# from math import ceil, floor
# from pdb import Pdb
# from random import randint, shuffle, choice, uniform
# from time import sleep, process_time
# from log_module import *
# from screen_reader import *
# from sound import *
class Empty:
  pass



class LightArmor:

  def __init__(self):
    self.arm = 2
    self.name = "light armor"



class MediumArmor:

  def __init__(self):
    self.arm = 3
    self.name = "medium armor"



class HeavyArmor:

  def __init__(self):
    self.arm = 4
    self.name = "heavy armor"



class Shield:

  def __init__(self):
    self.name = "shield"
    self.dfs = 5



class Building:
  name = None
  type = building_t
  nick = None
  level = 1
  size = 5
  stealth = 1
  gold = 0
  food = 0
  food_pre = 0
  grouth = 0
  grouth_pre = 0
  income = 0
  income_pre = 0
  public_order = 0
  public_order_pre = 0
  resource = 0
  resource_pre = 0
  upkeep = 0

  around_coast = 0
  base = None
  citylevel = None
  city_unique = 0
  global_unique = 0
  local_unique = 0
  free_terrain = 0
  grouth = 0
  is_complete = 0
  
  nation = None
  own_terrain = 1
  prod_progress = 0
  type = building_t
  tag = []
  
  upgrade = []

  def __init__(self, nation, pos):
    self.nation = nation
    self.pos = pos
    self.av_units = []
    self.av_units_pre = []
    self.nations = []
    self.production = []
    self.resource_cost = [0, 0]
    self.tiles = []
    self.soil = [coast_t, glacier_t, grassland_t, ocean_t, plains_t, tundra_t, waste_t]
    self.surf = [forest_t, none_t, river_t, swamp_t]    
    self.hill = [0, 1]
    self.upgrade = []
    self.units = []
    if self.base:
      base = self.base(self.nation, self.pos)
      self.food_pre = base.food
      self.grouth_pre = base.grouth
      self.income_pre = base.income
      self.public_order_pre = base.public_order
      self.resource_pre = base.resource 
  
  def __str__(self):
    name = f"{self.name}." 
    if self.nick:
      name += f" {self.nick}."
    return name
  
  def can_build(self):
    logging.debug(f"requicitos de {self}.")
    if self.check_tile_req(self.pos) == 0:
      return 0
    if self.gold and self.nation.gold < self.gold:
      return 0
    if   self.size > self.pos.size:
      return 0
    if self.local_unique and basics.has_name(self.pos.buildings, self.name):
      return 0
    if self.city_unique and basics.has_name(self.pos.city.buildings, self.name):
      return 0
    if self.global_unique and basics.has_name(self.pos.nation.buildings, self.name):
      return 0
    return 1

  def check_tile_req(self, pos):
    go = 1
    if self.citylevel and self.pos.city.name != self.citylevel: go = 0
    if pos.soil.name not in self.soil: go = 0
    if pos.surf.name not in self.surf: go = 0
    if pos.hill not in self.hill: go = 0
    if self.around_coast > 0 and pos.around_coast < self.around_coast: go = 0
    if self.free_terrain and pos.nation: go = 0
    if self.own_terrain and pos.nation != self.nation: go = 0    
    return go

  def improve(self, upgrade):
    msg = f"{self} actualizará a {upgrade}. {cost_t} {upgrade.gold} en {self.pos} {self.pos.cords}."
    logging.info(msg)
    if self.nation.show_info:
      sp.speak(msg)
      sleep(loadsound("gold1") * 0.5)
    
    self.nation.gold -= upgrade.gold
    upgrade.av_units_pre = []
    for i in self.av_units_pre + self.av_units:
      if i not in upgrade.av_units_pre: upgrade.av_units_pre.append(i)
    upgrade.nation = self.nation
    upgrade.nations = self.nations
    upgrade.pos = self.pos
    upgrade.resource_cost[0] = 1
    upgrade.size = self.size
    if self.pos.city: msg = [f"se actualizará {self} en {self.pos.city}, {self.pos} {self.pos.cords}."]
    else: msg = [f"se actualizará {self} en {self.pos} {self.pos.cords}."]
    upgrade.nation.log[-1].append(msg)
    self.pos.buildings[self.pos.buildings.index(self)] = upgrade

  def launch_event(self):
    pass

  def set_hidden(self, nation, info=0):
    logging.info(f"set_hidden for {self}.")
    if nation in self.nations: return
    visible = self.pos.pop // 50
    visible += sum([(i.units * i.sight) // 20 for i in self.pos.units if i.nation == nation])
    if visible < 1: return
    stealth = self.stealth
    if self.pos.day_night: stealth += 4
    roll = basics.roll_dice(3)
    if info: logging.debug(f"{visible= }, {stealth= }, {roll= }, {roll= }.")
    msg = f"stealth check for {self} in {self.pos} {self.pos.cords}. {visible= }, {stealth= }, {roll= }."
    self.pos.world.log[-1] += [msg]
    if roll >= stealth - visible:
      msg = [f"{self} {in_t} {self.pos} {self.pos.cords}."]
      nation.log[-1] += [msg]
      self.pos.world.log[-1] += [msg]
      self.nations += [nation]
      if nation.show_info: 
        sp.speak(f"{msg}", 1)
        sleep(loadsound("notify23"))

  def info(self, sound="in1"):
    sleep(loadsound(sound))
    say = 1
    x = 0
    while True:
      sleep(0.001)
      if say:
        av_units = [i.name for i in self.av_units]
        upgrades = [i.name for i in self.upgrade]
        lista = [
          f"{self},.",
          f"{size_t} {self.size}, {stealth_t} {self.stealth}.",
          f"{gold_t} {self.gold}. {upkeep_t} {self.upkeep}, {resources_t} {self.resource_cost[1]}.",
          f"{units_t} {av_units if self.av_units else str()}.",
          f"{upgrades_t} {upgrades if self.upgrade else str()}.",
          f"{income_t} {self.income}, {upkeep_t} {self.upkeep}.",
          f"{food_t} {self.food}. {resources_t} {self.resource}.",
          f"{public_order_t} {self.public_order}. {grouth_t} {self.grouth}.",
          ]
  
        sp.speak(lista[x])
        say = 0
  
      for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_UP:
            x = basics.selector(lista, x, go="up")
            say = 1
          if event.key == pygame.K_DOWN:
            x = basics.selector(lista, x, go="down")
            say = 1
          if event.key == pygame.K_HOME:
            x = 0
            say = 1
            loadsound("s1")
          if event.key == pygame.K_END:
            x = len(lista) - 1
            say = 1
            loadsound("s1")
          if event.key == pygame.K_F12:
            sp.speak(f"on.", 1)
            sp.speak(f"off.", 1)
          if event.key == pygame.K_ESCAPE:
            sleep(loadsound("back1") / 2)
            return

  def update(self):
    self.is_complete = 1 if self.resource_cost[0] >= self.resource_cost[1] else 0
    self.units = [uni for uni in self.units if uni.hp_total >= 1]



class City:
  name = None
  type = city_t
  around_coast = 0
  around_threat = 0
  base = None
  defense = 0
  defense_min = 0
  defense_total = 0
  events = []
  food = 1
  food_need = 0
  food_pre = 1
  food_total = 0
  grouth = 0
  grouth_base = 0.1
  grouth_factor = 50
  grouth_min_bu = 30
  grouth_min_upg = 30
  capital = 0
  commander_request = 0
  cost = 0
  free_terrain = 1
  gold = 0
  hp_total = [80, 80]
  income = 1
  income_pre = 1
  is_complete = 1
  level = 0
  military_limit = 30
  military_base = 30
  military_change = 2
  military_max = 40
  nation = None
  nick = None
  pop = 0
  pop_back = 0
  prod_progress = 0
  public_order = 1
  public_order_pre = 1
  raid_outcome = 0
  resource = 1
  res_pre = 1
  size = 6
  seen_threat = 0 
  type = city_t
  unique = 0
  upkeep = 0

  def __init__(self, nation, pos):
    self.nation = nation
    self.pos = pos
    
    self.av_units_pre = []
    self.buildings = []
    # self.buildings_food = []
    self.events = [i(self) for i in self.events]
    self.production = []
    self.resource_cost = [0, 0]
    self.soil = [waste_t, glacier_t, grassland_t, ocean_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t, river_t, swamp_t]
    self.seen_units = []
    self.hill = [0, 1]
    self.tiles = []
    self.traits = []
    self.units = []
    self.upgrade = []

  def __str__(self):
    name = f"{self.nick}"
    return name

  def add_building(self, itm, pos):
    itm.resource_cost[0] = 1
    pos.buildings.append(itm)
    self.nation.gold -= itm.gold
    if self.nation.show_info:
      sp.speak(f"{added_t} {itm}")
      if itm.gold > 0: 
        sleep(loadsound("gold1"))
        sp.speak(f"{cost_t} {itm.gold}.")
    itm.pos = pos
    logging.debug(f"pos {itm.pos} {itm.pos.cords}.")
    itm.city = self
    itm.nation = self.nation
    itm.nations += [self.nation]
    pos.update(itm.nation)
    if itm.pos.city: msg = f"se construirá {itm} en {itm.pos.city}, {itm.pos} {itm.pos.cords}."
    else: msg = f"se construirá {itm} en {itm.pos} {itm.pos.cords}."
    logging.info(msg)
    itm.nation.log[-1].append(msg)
    self.update()
  
  def add_pop(self, number, info=0):
    [i.update(self.nation) for i in self.tiles]
    
    tiles = [i for i in self.tiles if i.blocked == 0]
    shuffle(tiles)
    tiles.sort(key=lambda x: x.food, reverse=True)
    tiles.sort(key=lambda x: self.nation.check_ppt(x), reverse=True) 
    tiles.sort(key=lambda x: x.public_order, reverse=True)
    grouth = ceil(number / (len(self.tiles) * 1.1))  # avoid 0with ceil. if not add pop stops.
    msg = f"{self} crecerá {number}. grouth {grouth}."
    self.nation.devlog[-1] += [msg]
    if info: logging.info(f"crecerá {number}. grouth_total {grouth_total}.")
    for t in tiles: t.last_grouth = []
    tries = 10000
    while number > 1:
      tries -= 1
      if tries < 0: 
        sp.speak(f"add pop stoped!", 1)
        sleep(1)
        Pdb().set_trace()
      
      for t in tiles:
        if number < 1: break
        _grouth = grouth* uniform(0.8, 1.2)
        
        if t.is_city: _grouth *= 1.1
        if t.hill not in t.nation.main_pop_hill: _grouth *= 0.8
        if t.soil.name not in t.nation.main_pop_soil: _grouth *= 0.8
        if t.surf.name not in t.nation.main_pop_surf: _grouth *= 0.8
        if _grouth > number: _grouth = number
        if info: logging.debug(f"{t}, {t.is_city= }, {len(t.buildings)= }, {_grouth= }.")
        t.last_grouth += [["turn", t.world.turn, "grouth_total", grouth, _grouth, _grouth, "number", number]]
        
        t.pop += _grouth
        number -= _grouth

  def can_build(self):
    logging.debug(f"requicitos de {self}.")
    if self.check_tile_req(self.pos) == 0:
      return 0
    if self.gold and self.nation.gold < self.gold:
      return 0
    if   self.size > self.pos.size:
      return 0
    if self.unique and basics.has_name(self.pos.city.buildings, self.name):
      return 0
    return 1

  def check_building(self):
    logging.debug(f"check building {self}.")
    for bu in self.buildings:
      if bu.nation != bu.nation:
        bu.cost[1] -= 20 * bu.cost[1] / 100
      if bu.resource_cost[0] < bu.resource_cost[1] and bu.nation == self.nation: 
        bu.resource_cost[0] += self.resource_total
        if bu.resource_cost[0] >= bu.resource_cost[1]:
          bu.resource_cost[0] = bu.resource_cost[1]
          if military_t in bu.tags: self.nation.set_path()
          if bu.pos.city: msg = f"{bu} {complete_t} en {bu.pos.city}, {bu.pos} {bu.pos.cords}."
          else: msg = f". ({bu}) {complete_t} en {bu.pos} {bu.pos.cords}."
          self.nation.log[-1].append(msg)
          if self.nation.show_info: sleep(loadsound("notify6", channel=CHT3) * 0.2)

  def check_events(self, info=0):
    logging.info(f"check_event for {self}.")
    for ev in self.events:
      if info: logging.debug(f"{str(ev)}.")
      ev.run()

  def check_tile_req(self, pos):
    go = 1
    if pos.soil.name not in self.soil: go = 0
    if pos.surf.name not in self.surf: go = 0
    if pos.hill not in self.hill: go = 0
    if pos.around_coast < self.around_coast: go = 0
    if pos.nation and self.free_terrain: go = 0
    if pos.nation != self.nation and self.own_terrain: go = 0    
    return go

  def check_training(self):
    logging.debug(f"check training {self}.")
    if self.production:
      self.prod_progress -= self.resource_total
      if self.prod_progress <= 0:
        unit = self.production.pop(0)
        msg = f"{unit} entrenado en {self}."
        self.nation.gold -= unit.gold
        unit.pos = self.pos
        unit.city = self
        unit.show_info = self.nation.show_info
        unit.set_hidden(unit.pos)
        unit.update()
        logging.debug(msg)
        self.nation.log[-1] += [msg]
        self.pos.units += [unit]
        self.nation.unit_number += 1
        if self.nation.show_info: sleep(loadsound("notify24", channel=CHTE2) * 0.5)
        if self.production: self.prod_progress = self.production[0].resource_cost
  
  def get_threats(self):
    self.threat_inside = 0
    for ti in self.tiles:
      self.threat_inside += ti.threat

  def get_tiles_food(self, items):
    tiles = []
    buildings = [it(self.nation, self.pos) for it in self.nation.av_buildings]
    buildings = [it for it in buildings if it.food]
    for bu in buildings:
      for i in items:
        if (i.soil.name in bu.soil 
            and i.surf.name in bu.surf 
            and i.hill in bu.hill
            and i not in tiles):
          tiles.append(i)
    
    return tiles

  def get_tiles_res(self, items):
    tiles = []
    buildings = [it(self.nation, self.pos) for it in self.nation.av_buildings]
    buildings = [it for it in buildings if it.resource]
    for bu in buildings:
      for i in items:
        if (i.soil.name in bu.soil
              and i.surf.name in bu.surf
              and i.hill in bu.hill 
              and i not in tiles):
          tiles.append(i)
    
    return tiles

  def income_change(self):
    self.update()
    income = self.income_total - self.upkeep
    self.nation.last_income += income
    self.nation.last_outcome += self.raid_outcome
    
    if income < 0: 
      logging.warning(f"income menor que cero! {income}")
      Pdb().set_trace()

  def launch_event(self):
    pass

  def population_change(self):
    self.update()
    grouth = round(self.grouth_total * self.pop / 100, 1)
    msg = f"{self} grows {grouth}."
    logging.debug(msg)
    self.nation.devlog[-1] += [msg]
    self.population_grouth()
    
    if self.pop_back > 0: 
      pop_back = self.pop_back / 3
      self.add_pop(pop_back)
      self.pop_back -= pop_back
      logging.debug(f"regresan {pop_back} civiles.")

  def population_grouth(self):
    for tl in self.tiles:
      if tl.pop == 0: tl.pop = randint(1, 3)
      tl.pop += tl.grouth * tl.pop / 100

  def reduce_pop(self, number, info=0):
    logging.info(f"reduce {number} de {self} ({self.pop} pop).")
    tiles = [i for i in self.tiles if i.blocked == 0]
    shuffle(tiles)
    if info: logging.debug(f"reducirá {number}.")
    while number > 0:
      for it in tiles:
        if self.nation.check_ppt(it) == 0 and basics.roll_dice(1) >= 5:
          if info: logging.debug(f"skip by ppt.")
          continue
        reduce = it.pop * 0.1
        if reduce > number: reduce = number
        it.pop -= reduce
        number -= reduce
  
  def set_av_units(self):
    self.all_av_units = []
    for b in self.buildings:
      if b.pos.blocked == 0: 
        self.all_av_units += [i for i in b.av_units_pre if i.name not in [av.name for av in self.all_av_units]]
      if (b.is_complete and b.pos.blocked == 0): 
        self.all_av_units += [i for i in b.av_units if i.name not in [av.name for av in self.all_av_units]]
    _av = []
    for i in self.all_av_units:
      if i.name not in [av.name for av in _av]: _av += [i]

    # logging.debug(f"_av {len(_av)}.")
  def set_buildings_upgrades(self):
    self.food_upgrades = []
    self.military_upgrades = []
    self.resource_upgrades = []
    for bu in self.buildings:
      for upg in bu.upgrade:
        if food_t in upg.tags: self.food_upgrades += [upg]
        if military_t in upg.tags: self.military_upgrades += [upg]
        if resource_t in upg.tags: self.resource_upgrades += [upg] 

  def set_capital_bonus(self):
    self.food = 0
    self.grouth = 0
    self.income = 0
    self.public_order = 0

  def set_defense(self):
    logging.debug(f"set_defense.")
    self.defense_total = 0
    self.defense_min = 0
    self.hostile_ranking = 0
    units = [i for i in self.units 
             if self.nation in i.belongs and i.goal == None 
             and i.leader == None and i.scout == 0 and i.settler == 0]
    self.defense = sum(i.ranking for  i in self.pos.units if i.garrison)
    for i in units:
      if i.garrison and i.pos == self.pos: i.city = self 
    self.defense_total = sum(i.ranking for i in units) 
    for t in self.tiles:
      t.update(self.nation)
      self.hostile_ranking += t.threat
      self.defense_min += t.defense_req
    
    if len(self.nation.cities) > 1:
      for ct in self.nation.cities:
        if ct != self: self.defense_total += 10 * ct.defense_total / 100
    
    self.defense_min /= 2
    self.defense_total_percent = round(self.defense_total * 100 / self.defense_min)
    self.defense = round(self.defense)
    self.defense_total = round(self.defense_total)
    self.defense_total_percent = round(self.defense_total_percent)

  def set_downgrade(self):
    pass

  def set_grouth(self):
    # [tl.update(self.nation) for tl in self.tiles]
    self.grouth_total = sum([tl.grouth for tl in self.tiles]) / len(self.tiles)
    
  def set_military_limit(self):
    self.military_limit = (self.military_base + 
                           (self.pop / self.military_change)) 
    if self.military_limit > self.military_max: 
      self.military_limit = self.military_max
    if self.seen_threat > self.defense_total // 2 or self.defense < self.defense_min: 
      self.military_limit *= 2

  def set_name(self):
      self.nick = self.nation.city_names.pop()

  def set_seen_units(self, new=0, info=0):
    # logging.debug(f"set seen units {self}.")
    if len(self.tiles) < 12: tiles = [t for t in self.pos.get_near_tiles(3)]
    elif len(self.tiles) >= 12: tiles = [t for t in self.pos.get_near_tiles(4)]
    tiles = [t for t in tiles if t.units]
    self.pos.pos_sight(self.nation, self.nation.map)
    tiles = [t for t in tiles if t in self.nation.map and t.sight and t.units]
    [t.update(self.nation) for t in tiles]
    if new or self.seen_units == []: 
      self.seen_units.append([])
      logging.debug(f"nuevo.")
    for t in tiles:
      units = t.get_free_squads(self.nation) + t.get_comm_units(self.nation)
      for uni in units: 
        if (self.nation not in uni.belongs and uni not in self.seen_units[-1]): 
          self.seen_units[-1].append(uni)
    
    self.seen_threat = 0
    self.seen_wild = []
    self.seen_fly = []
    self.seen_human = []
    self.seen_mounted = []
    self.seen_pn = []
    self.seen_ranged = []
    self.seen_sacred = []
    self.seen_undead = []
    self.end_seen_units = []
    for l in self.seen_units[-7:]:
      for uni in l:
        if uni not in self.end_seen_units: 
          self.end_seen_units += [uni]
          # if uni in self.seen_units[-3:]: continue
          if uni in self.seen_units[-7:-3]: uni.ranking -= uni.ranking * 0.4
    for uni in self.end_seen_units:
      self.seen_threat += uni.ranking
      if uni.aligment == wild_t: self.seen_wild += [uni]
      if uni.can_fly: self.seen_fly += [uni]
      if human_t in uni.traits: self.seen_human += [uni]
      if uni.mounted: self.seen_mounted += [uni]
      if uni.pn: self.seen_pn += [uni]
      if uni.ranged >= 6: self.seen_ranged += [uni]
      if uni.aligment == sacred_t: self.seen_sacred += [uni] 
      if death_t in uni.traits: self.seen_undead += [uni]
    
    self.seen_fly_rnk = sum(i.ranking for i in self.seen_fly)
    self.seen_human_rnk = sum(i.ranking for i in self.seen_human)
    self.seen_mounted_rnk = sum(i.ranking for i in self.seen_mounted)
    self.seen_pn_rnk = sum(i.ranking for i in self.seen_pn)
    self.seen_ranged_rnk = sum(i.ranking for i in self.seen_ranged)
    self.seen_sacred_rnk = sum(i.ranking for i in self.seen_sacred)
    self.seen_death_rnk = sum(i.ranking for i in self.seen_undead)
    self.seen_wild_rnk = sum(i.ranking for i in self.seen_wild)
    
    if info:
      logging.debug(f"fly {len(self.seen_fly)}. ranking {self.seen_fly_rnk}.")
      logging.debug(f"human {len(self.seen_human)}. ranking {self.seen_human_rnk}.")
      logging.debug(f"mounted {len(self.seen_mounted)}. ranking {self.seen_mounted_rnk}.")
      logging.debug(f"rng {len(self.seen_ranged)}. ranking {self.seen_ranged_rnk}.")
      logging.debug(f"undead {len(self.seen_undead)}. ranking {self.seen_death_rnk}.")
      logging.debug(f"wild {len(self.seen_wild)}. ranking {self.seen_wild_rnk}.")
  
  def set_train_type(self, units, info=1):
    self.set_seen_units(0, info=1)
    self.set_units_types()
    shuffle(units)
    if basics.roll_dice(1) >= 3:
      if info: logging.debug(f"sort by nation traits.")
      units.sort(key=lambda x: any(i in x.traits for i in self.nation.traits), reverse=True)
    [i.update() for i in units]
    if info: logging.debug(f"recividos {len(units)}.")
    _wild = [i for i in units if wild_t in i.traits]
    _anticav = [i for i in units if i.anticav]
    _archers = [i for i in units if i.range[1] > 5]
    _fly = [i for i in units if i.can_fly]
    _mounted = [i for i in units if i.mounted]
    _sacred = [i for i in units if i.aligment == sacred_t]
    _death = [i for i in units if death_t in i.traits]
    if self.defense_total_percent < 100 and self.nation.defense_total_percent < 300 or self.defense_total == 0:
      logging.debug(f"defensivo.")
      if basics.roll_dice(1) >= 3: 
        units.sort(key=lambda x: x.ranged, reverse=True)
        if info: logging.debug(f"sort by ranged")
      if self.pos.around_threat and self.pos.around_threat >= self.defense / 2: 
        units.sort(key=lambda x: x.resource_cost <= self.resource_total, reverse=True)
        if info: logging.debug(f"sort by less resource.")
      return units
    
    # more ranged enemies.
    if self.seen_ranged_rnk > (self.units_ranged_rnk + self.units_fly_rnk) * 0.5:
      if info: logging.debug(f"contra ranged.")
      _units = [i for i in units if i.ranged
                or i.armor
                or i.shield
                and i.levy == 0] 
      _units.sort(key=lambda x: x.ranged and x.ranking, reverse=True)
      _units.sort(key=lambda x: x.ranking, reverse=True)
      if _units: return _units
    
    # More mounted enemies.
    if self.seen_mounted_rnk > self.units_piercing_rnk + self.units_mounted_rnk:
      if info: logging.debug(f"pn.")
      _units = [i for i in units if i.pn
                or i.type == "cavalry"]
      if basics.roll_dice(1) >= 3: _units.sort(key=lambda x: x.ranking, reverse=True)
      if _units: return _units
    
    # More undead enemies.
    if self.seen_death_rnk > self.units_sacred_rnk // 2:
      if info: logging.debug(f"sacred.")
      _units = [i for i in units if i.aligment == sacred_t]
      if basics.roll_dice(1) >= 3: _units.sort(key=lambda x: x.ranking, reverse=True)
      if _units: return _units
    # more sacred enemies.
    if self.seen_sacred_rnk * 1.5 > self.units_death_rnk:
      if info: logging.debug(f"human")
      _units = [i for i in units if i.aligment not in [hell_t, malignant_t] and i.levy == 0]
      _units.sort(key=lambda x: x.ranking, reverse=True)
      if _units: return units
    # Anticav.
    total_rnk = (self.units_piercing_rnk 
                 * 100 // self.defense_total)
    if info: logging.debug(f"av anticav {len(_anticav)}.")
    if info: logging.debug(f"total rnk {total_rnk}.")
    if info: logging.debug(f"limit {self.nation.units_piercing_limit}.")
    if (basics.roll_dice(1) >= 5 and _anticav 
        and total_rnk < self.nation.units_piercing_limit):
      if info: logging.debug(f"piercing.")
      if basics.roll_dice(1) >= 3: _anticav.sort(key=lambda x: x.ranking, reverse=True)
      if _anticav: return _anticav
    
    # Sacred.
    total_rnk = (self.units_sacred_rnk 
                 * 100 // self.defense_total)
    if info: logging.debug(f"av sacred {len(_sacred)}.")
    if info: logging.debug(f"total rnk {total_rnk}.")
    if info: logging.debug(f"limit {self.nation.units_sacred_limit}.")
    if (basics.roll_dice(1) >= 5 and _sacred 
        and total_rnk < self.nation.units_sacred_limit):
      if info: logging.debug(f"sacred.")
      if basics.roll_dice(1) >= 3: _sacred.sort(key=lambda x: x.ranking, reverse=True)
      if _sacred: return _sacred
    
    # Forest.
    if self.pos.around_forest + self.pos.around_hill >= 3 and basics.roll_dice(1) >= 5:
      _units = [i for i in units if i.can_fly or i.forest_survival or i.mountain_survival]
      if info: logging.debug(f"forest and hills.")
      _units.sort(key=lambda x: x.ranged, reverse=True)
      if _units: return _units
      
    # Archers.
    total_rnk = (self.units_ranged_rnk 
                 * 100 // self.defense_total)
    if info: logging.debug(f"av archers {len(_archers)}.")
    if info: logging.debug(f"total rnk {total_rnk}")
    if info: logging.debug(f"limit {self.nation.units_ranged_limit}.")
    if (basics.roll_dice(1) >= 5 and _archers  
        and total_rnk < self.nation.units_ranged_limit):
      if info: logging.debug(f"ranged.")
      if basics.roll_dice(1) >= 2: _archers.sort(key=lambda x: x.ranking, reverse=True)
      _archers.sort(key=lambda x: x.ranged, reverse=True)
      if _archers: return _archers
    
    # Mounted.
    total_rnk = (self.units_mounted_rnk * 
                 100 / self.defense_total)
    if info: logging.debug(f"av mounted {len(_mounted)}.")
    if info: logging.debug(f"total rnk {total_rnk}.")
    if info: logging.debug(f"limit {self.nation.units_mounted_limit}.")
    if (basics.roll_dice(1) >= 5 and _mounted and total_rnk < self.nation.units_mounted_limit):
      if info: logging.debug(f"mounted.")
      _units = [i for i in units if i.mounted]
      if _units: return _units
    
    if self.defense_total_percent > 200:
      if info: logging.debug(f"expensive.")
      _units = [i for i in units if i.levy == 0]
      if _units: units = _units
      units.sort(key=lambda x: x.ranking, reverse=True)
      
      shuffle(units)
      return units    

    if self.nation.units_comm:
      logging.debug(f"set priority to units for commanders.")
      for uni in units: uni._go = 1
      for uni in units:
        for tr in uni.traits:
          if tr not in self.comm_lead_traits: uni._go = 0
        if uni.aligment not in self.comm_lead_aligments: uni._go = 0
      units = [it for it in units if it._go]    
    return units

  def set_units_types(self):
    units = [i for i in self.units if i.leader == None or 
             (i.leader and i.leader.goal == None)] 
    self.comm_lead_traits = []
    self.comm_lead_aligments = []
    self.units_fly = []
    self.units_human = []
    self.units_melee = []
    self.units_mounted = []
    self.units_orc = []
    self.units_piercing = []
    self.units_ranged = []
    self.units_sacred = []
    self.units_death = []
    self.units_wild = []
    for i in units:
      if i.can_fly: self.units_fly += [i]
      if human_t in i.traits: self.units_human += [i]
      if i.range[1] < 6: self.units_melee += [i]
      if i.mounted: self.units_mounted += [i]
      if orc_t in i.traits: self.units_orc += [i] 
      if i.pn: self.units_piercing += [i]
      if i.range[1] >= 6: self.units_ranged += [i]
      if i.aligment == sacred_t: self.units_sacred += [i]
      if death_t in i.traits: self.units_death += [i]  
      if i.aligment == wild_t: self.units_wild += [i]
      if i.leadership:
        for tr in i.lead_traits:
          if tr not in self.comm_lead_traits: self.comm_lead_traits += [tr]
        for al in i.lead_aligments:
          if al not in self.comm_lead_aligments: 
            self.comm_lead_aligments += [al]
    
    self.units_fly_rnk = sum(i.ranking for i in self.units_fly)
    self.units_human_rnk = sum(i.ranking for i in self.units_human)
    self.units_melee_rnk = sum(i.ranking for i in self.units_melee)
    self.units_mounted_rnk = sum(i.ranking for i in self.units_mounted)
    self.units_orc_rnk = sum(i.ranking for i in self.units_orc)
    self.units_piercing_rnk = sum(i.ranking for i in self.units_piercing)
    self.units_ranged_rnk = sum(i.ranking for i in self.units_ranged)
    self.units_sacred_rnk = sum(i.ranking for i in self.units_sacred)
    self.units_death_rnk = sum(i.ranking for i in self.units_death)
    self.units_wild_rnk = sum(i.ranking for i in self.units_wild)
  
  def start_turn(self):
    self.outcome_raided = 0

  def status(self, info=0):
    logging.info(f"city status {self}.")
    # to delete.
    #===========================================================================
    # self.for_food_tiles = self.get_tiles_food(self.tiles)
    # self.for_food_tiles = [i for i in self.for_food_tiles if i.size >= 4]
    # self.for_food_tiles.sort(key=lambda x: x.food, reverse=True)
    # self.for_res_tiles = self.get_tiles_res(self.tiles)
    # self.for_res_tiles = [i for i in self.for_res_tiles if i.size >= 4]
    # self.for_res_tiles.sort(key=lambda x: x.resource, reverse=True)
    #===========================================================================
    
    self.buildings_food = [i for i in self.buildings if food_t in i.tags]
    self.buildings_food_complete = [i for i in self.buildings_food if i.is_complete]
    self.buildings_income = [i for i in self.buildings if income_t in i.tags]
    self.buildings_income_complete = [i for i in self.buildings_income if i.is_complete]
    self.buildings_military = [i for i in self.buildings if military_t in i.tags]
    self.buildings_military_complete = [i for i in self.buildings_military if i.is_complete]
    self.buildings_res = [i for i in self.buildings if resource_t in i.tags]
    self.buildings_res_complete = [i for i in self.buildings_res if i.is_complete]
    self.buildings_unrest = [i for i in self.buildings if unrest_t in i.tags]
    self.buildings_unrest_complete = [i for i in self.buildings_unrest if i.is_complete]
    
    # To delete.
    #===========================================================================
    # self.food_val = round(self.food_total - self.food_need)
    # self.food_probable = self.food_val
    # for b in self.buildings:
    #   if b.is_complete == 0:
    #     self.food_probable += b.food * b.pos.food / 100 
    # self.food_probable = round(self.food_probable)
    #===========================================================================
    
    if info:
      logging.debug(f"información de {self}.")
      logging.debug(f"balance de comida {self.food_val}.")
      logging.debug(f"terrenos estratégicos {len(self.defensive_tiles)}")
      logging.debug(f"terrenos de comida {len(self.for_food_tiles)}.")
      logging.debug(f"terreno de recursos {len(self.for_res_tiles)}.")
      
      # revisar si está entrenando unidades.
      if self.production:
        progress = ceil(self.prod_progress / self.resource_total)
        logging.debug(f"entrenando {self.production[0]} en {progress} {turns_t}.")
      elif self.production == []: logging.debug(f"no está produciendo")
      
      logging.debug(f"amenazas internas {self.threat_inside}. ")
      logging.debug(f"nivel de defensa {self.defense} de {self.defense_min}, ({self.defense_percent}%).")
      logging.debug(f"necesita {round(self.defense_need, 2)} defensa.")
      logging.debug(f"defensa total posible {self.defense_total}.")
      logging.debug(f"civiles {self.pop}, {round(self.pop_percent)}%.")
      logging.debug(f"población militar {self.pop_military}, ({round(self.military_percent, 1)}%.")
      logging.debug(f"total {self.pop_total}.")
      logging.debug(f"ingresos {self.income_total}.")

  def train(self, itm):
    logging.info(f"entrena {itm} en {self}.")
    if self.production == []: self.prod_progress = itm.resource_cost
    self.production.append(itm)
    self.nation.gold -= itm.gold
    self.reduce_pop(itm.pop * itm.units)
    if self.nation.show_info: 
      sleep(loadsound("set6"))
      sp.speak(f"{added_t} {itm} {cost_t} {itm.gold}")
      if itm.gold > 0: loadsound("gold1")

  def update(self):
    [i.update(self.nation) for i in self.tiles]
    self.food_total = sum(t.food for t in self.tiles if t.blocked == 0)
    self.pop = sum([i.pop for i in self.tiles])
    self.pop_military = sum(i.pop for i in self.production)
    self.pop_military += sum(i.total_pop for i in self.nation.units if i.city == self)
    self.resource_total = sum(t.resource for t in self.tiles if t.blocked == 0)
    self.food_need = round(self.pop)
    
    self.buildings = []
    self.units = []
    for t in self.tiles:
      for bu in t.buildings:
        if bu.nation != self.nation: continue
        if bu.type == building_t:bu.update()
        bu.poss = t
        self.buildings.append(bu)
      for uni in t.units: 
        if uni.nation == self.nation: self.units.append(uni)
    
    self.set_buildings_upgrades()
    self.buildings.sort(key=lambda x: x.resource_cost[0])
    self.food_total = round(self.food_total)
    self.pop_total = self.pop + self.pop_military
    self.pop_percent = round(self.pop * 100 / self.pop_total, 1)
    self.pop = round(self.pop, 1)
    
    self.set_military_limit() 
    self.military_percent = round(self.pop_military * 100 / self.pop_total, 1)
    
    # datos económicos.
    self.income_total = 0
    self.public_order_total = 0
    for t in self.tiles:
      if t.blocked == 0: 
        self.income_total += t.income
        self.raid_outcome += t.raided
      if t.pop > 0: self.public_order_total += t.public_order
    
    # mejorar ciudad.
    self.set_downgrade()
    self.set_upgrade()
    
    tiles = [i for i in self.tiles if i.pop > 0]
    self.public_order_total /= len(tiles)
    self.set_grouth()
    if self.grouth_total < 0: self.grouth = 0.1
    self.status()
    self.set_av_units()
    
    # expanding.
    self.expanding = 0
    if self.production and self.production[0].settler: self.expanding = 1

  def set_upgrade(self):
    pass



class Nation:
  name = "unnamed"
  nick = ""
  gold = 1000
  capital_pop_bonus = 0
  food_limit_builds = 200
  food_limit_upgrades = 800
  grouth_rate = 1
  public_order = 0
  upkeep_base = 50
  upkeep_change = 100
  upkeep_limit = 0
  
  attack_factor = 300
  capture = 0
  commander_rate = 10
  scout_factor = 4
  stalk_rate = 50  # cuantos stalk se envian.
  
  ai = 0
  anphibian = 0
  defense_total_percent = 0
  defense_mean = 0
  city_req_pop_base = 1000
  pop_limit = 50
  
  gold_rate = 1
  income = 0
  military_percent = 0
  military_pop = 0
  pos = None
  raid_income = 0
  raid_outcome = 0
  show_info = 0
  stalk = 0
  tile_cost = 1200
  tile_power = 1
  tile_area_limit = 3
  type = nation_t
  unit_number = 0 
  units_wild_limit = 100
  units_fly_limit = 100
  units_human_limit = 100
  units_melee_limit = 100
  units_mounted_limit = 100
  units_piercing_limit = 100
  units_ranged_limit = 100
  units_sacred_limit = 100
  units_undead_limit = 100

  def __init__(self):
    self.commander_request = 0
    self.path = Empty()
    self.path.build_military = "build"  # build, improve.
    self.path.build_food = "build"  # build, improve.
    # Allowed start tile.
    self.hill = [0, 1]
    self.soil = [waste_t, glacier_t, grassland_t, ocean_t, plains_t, tundra_t]
    self.surf = [none_t]
    # allowed near tiles. 
    self.min_around_desert = 0
    self.min_around_forest = 0
    self.min_around_glacier = 0
    self.min_around_grassland = 0
    self.min_around_hill = 0
    self.min_around_montain = 0
    self.min_around_ocean = 0
    self.min_around_plains = 0
    self.min_around_swamp = 0
    self.min_around_tundra = 0
    self.min_around_volcano = 0
    # not allowed near tiles.
    self.max_around_waste = 10
    self.max_around_forest = 10
    self.max_around_glacier = 10
    self.max_around_grassland = 10
    self.max_around_hill = 10
    self.max_around_montain = 10
    self.max_around_ocean = 10
    self.max_around_plains = 10
    self.max_around_swamp = 10
    self.max_around_tundra = 10
    self.max_around_volcano = 10
    # Non starting tiles.
    self.generic_soil = [grassland_t, plains_t, tundra_t, waste_t]
    self.generic_surf = [forest_t, none_t, swamp_t,]
    self.generic_hill = [0, 1]
    
    self.av_buildings = [Farm, Quarry, SawMill]
    self.buildings = []
    self.cities = []
    self.city_names = []
    self.leadernames1 = []
    self.leadernames2 = []
    self.leadernames3 = []
    
    # terrenos de comida.
    self.for_food = Empty()
    self.for_food.soil = [grassland_t, plains_t]
    self.for_food.surf = [none_t]
    self.for_food.hill = [0]
    # terrenos de recursos.
    self.for_res = Empty()
    self.for_res.soil = [waste_t, glacier_t, grassland_t, ocean_t, plains_t, tundra_t]
    self.for_res.surf = [forest_t]
    self.for_res.hill = [0, 1]
    
    self.devlog = []
    self.log = []
    self.map = []
    self.resources = []
    self.seen_nations = []
    self.seen_score = [0]
    self.nations_tiles = []
    self.seen_tiles = []
    self.seen_units = []
    self.str_nations = []
    self.start_units = []
    self.units = []
    self.units_comm = []
    self.units_free = []
    self.units_rebels = []
    self.units_scout = []
    
  def __str__(self):
    return self.name

  def add_unit(self, itm):
    itm.nation = self
    itm.belongs += [self]

  def add_city(self, itm, unit):
    logging.info:(f"add_city for {self}.")
    unit.update()
    itm = itm(unit.nation, unit.pos)
    scenary = unit.pos.scenary
    pop = unit.total_pop
    if self.cities == []: pop += self.capital_pop_bonus
    pos = unit.pos
    itm.pop = pop
    
    pos.buildings.append(itm)
    unit.hp_total = 0
    itm.set_name()
    if len(self.cities) == 0: itm.capital = 1
    if itm.capital: itm.set_capital_bonus()
    tiles = pos.get_near_tiles(1)
    for t in tiles:
      if t.nation == None:
        itm.tiles.append(t)
        t.city = itm
        t.nation = self
    msg = f"{hamlet_t} {itm.nick} se establece en {itm.pos} {itm.pos.cords}."
    logging.info(msg)
    self.log[-1].append(msg)
    itm.add_pop(itm.pop)
    [t.update(itm.nation) for t in itm.tiles]
    itm.update()
    itm.status()
    for t in itm.tiles: t.unrest += itm.initial_unrest * uniform(0.5, 1.5)
    self.update(scenary)
    logging.debug(f"{itm.nation} ahora tiene {len(itm.nation.cities)} ciudades.")
  
  def build_food(self, city, info=0):
    logging.info(f"build_food.")
    if city.seen_threat > city.defense_total * 0.3:
      if info: logging.debug(f"seen enemy.")
      return
    buildings = [bu for bu in self.av_buildings 
                 if food_t in bu.tags]
    shuffle(city.tiles)
    buildings.sort(key=lambda x: x.food, reverse=True)
    count = 1
    if city.buildings_food_complete == []: 
      count += 1
    city.tiles.sort(key=lambda x: x.public_order)
    city.tiles.sort(key=lambda x: x.populated)
    city.tiles.sort(key=lambda x: self.check_ppt(x), reverse=True)
    for it in city.tiles:
      if count < 1: return
      it.update(self)
      if info: logging.debug(f"checking {it} {it.cords}. {count=:}.")
      rate = it.grouth
      if info: logging.debug(f"{rate=:}.")
      if city.buildings_food_complete == []: rate *= 0.5
      if city.capital: rate *= 0.5 
      if self.check_ppt(it) == 0: rate *= 2
      if self.path.build_military == "improve": rate *= 22
      it.food_rate = f"{it.grouth=:}, {rate=:}, {city.grouth_min_bu=:}."
      if info: logging.debug(f"{rate=: }, {city.grouth_min_bu=: }.")
      if rate >= city.grouth_min_bu:
        logging.debug(f"{rate=:} higher than {city.grouth_min_bu=:}.")
        continue
      for bu in buildings:
        building = bu(self, it)
        if building.can_build():
          city.add_building(building, it)
          if info: logging.debug(f"{building} added.")
          count -= 1
          break

  def build_military(self, city, info=0):
    logging.info(f"build military.")
    if city.buildings_military == [] or city.military_upgrades == []: 
      self.path.build_military = "build" 
    if self.path.build_military == "improve":
      if info:
        msg = f"path set to upgrade."
        logging.debug(msg)
      return
    military_buildings = [b for b in self.av_buildings if military_t in b.tags]
    if military_buildings == []: return
    military_buildings.sort(key=lambda x: x(self, self.pos).resource_cost[1])
    if basics.roll_dice(1) >= 5:
      logging.debug(f"shuffle.") 
      shuffle(military_buildings)
    
    count = 1
    if city.capital == 0 and city.defense_total < 200:
      if info:logging.debug(f"not capital and needs more defense.")
      count = 0
    for b in military_buildings:
      if count == 0: break
      city.tiles.sort(key=lambda x: len(x.around_snations), reverse=True)
      for it in city.tiles:
        it.update(self)
        if info: logging.debug(f"checking {it} {it.cords}")
        if it.around_threat + it.threat:
          if info: logging.debug(f"threat.") 
          continue
        if it.blocked: continue
        building = b(self, it)
        if building.can_build():
          city.add_building(building, it)
          logging.debug(f"{building} added.")
          break

  def build_misc(self, city, info=0):
    logging.info(f"build misc.")
    city.status()
    # military_buildings = [bu for bu in self.av_buildings 
                          # if military_t in bu.tags]
    buildings = [b for b in self.av_buildings if any(i in b.tags for i in [unrest_t, resource_t])]
    if buildings == []: return
    shuffle(buildings)
    res = len(city.buildings_res)
    if len(city.buildings_food_complete) == 0:
      if info:logging.debug(f"first needs food building.")
      return 
    defense_min = 200
    if self.path.build_military == "improve": defense_min += defense_min
    for b in buildings:
      if unrest_t in b.tags: city.tiles.sort(key=lambda x: x.public_order)
      if resource_t in b.tags:
        if city.seen_threat > city.defense_total * 0.3:
          if info: logging.debug(f"threats on city.")
          continue
        if city.defense_total_percent < defense_min * res + 1:
          if info: logging.debug(f"needs more defense to construct {res+1} buildings") 
          continue
        city.tiles.sort(key=lambda x: x.hill, reverse=True)
      for it in city.tiles:
        if info: logging.debug(f"checking {it} {it.cords}.")
        it.update(self)
        if it.around_threat + it.threat:
          if info: logging.debug(f"threats.") 
          continue
        if unrest_t in b.tags and it.public_order > 30:
          if info: logging.debug(f"not enough unrest.") 
          continue
        
        building = b(self, it)
        if building.can_build():
          city.add_building(building, it)
          logging.debug(f"{building} added.")
          return

  def check_events(self):
    pass

  def check_ppt(self, tile, info=0):
    if info: logging.info(f"check prefered pop tile for {tile} {tile.cords}.")
    go = 1
    log = []
    if tile.soil.name not in self.main_pop_soil:
      log += [f"not in soil."]
      go = 0 
    if tile.surf.name not in self.main_pop_surf:
      log += [f"not in surf."]
      go = 0
    if tile.hill not in self.main_pop_hill:
      log += [f"not in hill."]
      go = 0
    return go

  def get_free_comms(self):
    return [uni for uni in self.units_comm 
            if uni.leadership - 5 > uni.leading and uni.goto == []]

  def get_free_squads(self):
    units_free = [it for it in self.units if  it.scout == 0 and it.settler == 0
           and it.goto == [] and it.goal == None
           and it.leadership == 0]
    
    self.units_free = []
    for i in units_free:
      i.pos.update(i.nation)
      if i.pos.around_threat + i.pos.threat > i.pos.defense: continue
      if i.leader and i.leader.pos == i.pos: continue
      self.units_free += [i]
    
    return self.units_free

  def get_groups(self):
    # self.update(self.map)
    self.groups = [i for i in self.units if i.goal and i.hp_total >= 1]
    self.groups_free = [i for i in self.groups
                         if i.goto == []]

  def improve_food(self, city, info=1):
    logging.info(f"build_food_upgrade.")
    # food upgrades.
    buildings = [b for b in city.buildings_food_complete if b.upgrade]
    if info:logging.debug(f"upgradables {len(buildings)=:}.")
    for bu in buildings:
      if city.seen_threat > city.defense_total * 0.3: continue
      if city.defense_total_percent < 100: continue
      grouth_min = city.grouth_min_upg
      if info: logging.debug(f"{grouth_min}.")
      if self.path.build_military == "improve":
        grouth_min *= 0.5
        if info: logging.debug(f"grouth_min decreased to {grouth_min}.") 
      if bu.pos.grouth > grouth_min:
        logging.debug(f"food not need.")
        bu.pos.log = f"turn {bu.pos.world.turn}, food not need."
        continue
      
      upg = choice(bu.upgrade)(self, bu.pos)
      if upg.gold < self.gold:
        bu.improve(upg)

  def improve_military(self, city, info=0):
    logging.info(f"build_military_upgrade.")
    if self.path.build_military == "build":
      if info:
        msg = f"set to build."
        logging.debug(msg)
      return
    # military upgrades.
    buildings = [bu for bu in city.buildings_military_complete if bu.upgrade]
    if info:logging.debug(f"upgradables {len(buildings)=:}.")
    for bu in buildings:
      if info:logging.debug(f"{bu.name}")
      upg = choice(bu.upgrade)(self, bu.pos)
      
      if upg.gold < self.gold:
        bu.improve(upg)

  def improve_misc(self, city, info=0):
    logging.info(f"build_misc_upgrade.")
    # misc upgrades.
    if self.path.build_military == "improve" and basics.roll_dice(1) >= 2:
      if info: logging.debug(f"skipping by upgrade military building path.")
      return
    buildings = [bu for bu in city.buildings_res_complete if bu.upgrade]
    logging.debug(f"upgradables {len(buildings)=:}.")
    for bu in buildings:
      upg = choice(bu.upgrade)(self, bu.pos)
      
      if upg.gold < self.gold and city.defense_total_percent >= 150:
        bu.improve(upg)

  def check_min_tiles(self, tile, info=1):
    go = 1
    if tile.around_coast < self.min_around_ocean: 
      go = 0
      if info: logging.debug(f"coast.")
    if tile.around_forest < self.min_around_forest: 
      go = 0
      if info: logging.debug(f"forest.")
    if tile.around_glacier < self.min_around_glacier: 
      go = 0
      if info: logging.debug(f"glacier.")
    if tile.around_grassland < self.min_around_grassland: 
      go = 0
      if info: logging.debug(f"grass.")
    if tile.around_hill < self.min_around_hill: 
      go = 0
      if info: logging.debug(f"hill.")
    if tile.around_mountain < self.min_around_montain: 
      go = 0
      if info: logging.debug(f"mountain.")
    if tile.around_plains < self.min_around_plains: 
      go = 0
      if info: logging.debug(f"plains.")
    if tile.around_swamp < self.min_around_swamp: 
      go = 0
      if info: logging.debug(f"swamp.")
    if tile.around_tundra < self.min_around_tundra: 
      go = 0
      if info: logging.debug(f"tundra.")
    if tile.around_volcano < self.min_around_volcano: 
      go = 0
      if info: logging.debug(f"volcan.")
    if tile.around_waste < self.min_around_desert: 
      go = 0
      if info: logging.debug(f"decert.")
    return go
  
  def check_max_tiles(self, tile, info=1):
    stop = 0
    if tile.around_coast > self.max_around_ocean: 
      stop = 1
      if info: logging.debug(f"Osean.")
    if tile.around_forest > self.max_around_forest: 
      stop = 1
      if info: logging.debug(f"Forest.")
    if tile.around_glacier > self.max_around_glacier: 
      stop = 1
      if info: logging.debug(f"Glacier.")
    if tile.around_grassland > self.max_around_grassland: 
      stop = 1
      if info: logging.debug(f"Grassland.")
    if tile.around_hill > self.max_around_hill: 
      stop = 1
      if info: logging.debug(f"Hill.")
    if tile.around_mountain > self.max_around_montain: 
      stop = 1
      if info: logging.debug(f"Mountain.")
    if tile.around_plains > self.max_around_plains: 
      stop = 1
      if info: logging.debug(f"Plains.")
    if tile.around_swamp > self.max_around_swamp: 
      stop = 1
      if info: logging.debug(f"swamp.")
    if tile.around_tundra > self.max_around_tundra: 
      stop = 1
      if info: logging.debug(f"Tundra.")
    if tile.around_volcano > self.max_around_volcano: 
      stop = 1
      if info: logging.debug(f"Volcano.")
    if tile.around_waste > self.max_around_waste: 
      stop = 1
      if info: logging.debug(f"Waste.")
    return stop
  
  def launch_event(self):
    pass
  
  def set_hidden_buildings(self):
    logging.info(f"set_hidden for {self} buildings.")
    buildings = []
    for t in self.map:
      if t.sight == 0: continue
      buildings += [bu for bu in t.buildings 
                    if bu.type == building_t]
      buildings = [b for b in buildings if self != b.nation or self not in b.nations]
    
    [bu.set_hidden(self) for bu in buildings]

  def set_income(self):
    self.last_income = 0
    self.last_outcome = 0
    [ct.income_change() for ct in self.cities]
    [ct.start_turn() for ct in self.cities]
    self.last_income += self.raid_income
    msg1 = f"{income_t} {self.last_income}."
    msg2 = f"lost by raiders {self.last_outcome}."
    msg3 = f"{total_t} {self.last_income-self.last_outcome}."
    self.log[-1] += [msg1, msg2, msg3]
    self.gold += round(self.last_income - self.last_outcome)
    self.raid_income = 0
    msg = f"starts with {self.gold} gold. {self.income:=}, {self.upkeep:=}."
    self.devlog[-1] += [msg]

  def set_new_city_req(self):
    cities = len([i for i in self.cities])
    self.city_req_pop = self.city_req_pop_base * (cities)
  
  def set_new_buildings(self, city, info=1):
    logging.info(f"new buildings for {self}.")
    if self.income < self.upkeep:
      logging.debug(f"not enogh gold for upkeep.")
      return
    
    city.status()
    go = 0
    for b in self.av_buildings:
      if self.gold > b.gold: go = 1
    if go == 0:
      if info: logging.debug(f"not enough gold for buildings.") 
      return
    
    build_action = [self.build_food, self.build_military, self.build_misc]
    shuffle(build_action)
    for act in build_action:
      act(city, info)
    
  def set_path(self):
    self.path.build_military = choice(["build", "improve"])

  def set_seen_nations(self, info=0):
    for nt in self.seen_nations:
      nt.seen_tiles = [t for t in nt.seen_tiles if str(t.nation) == str(nt)]
    self.seen_nations = [nt for nt in self.seen_nations if nt.seen_tiles]
    for t in self.map:
      if t.sight == 0 or t.nation == None: continue
      t.update(self)
      if (str(t.nation) != str(self) 
          and str(t.nation) not in self.str_nations):
        nt = t.nation.__class__()
        self.str_nations.append(str(t.nation))
        self.seen_nations.append(nt)
        logging.debug(f"{nt} descubierta.")
        sleep(loadsound("notify1") / 2)
        
    for nt in self.seen_nations:
      nt.seen_units = []
      for t in self.map:
        if t.sight == 0: continue
        if str(t.nation) == str(nt): 
          nt.score = t.nation.score
          if t not in nt.seen_tiles: nt.seen_tiles.append(t)
        for uni in t.units:
          if str(uni.nation) == str(nt) and uni.hidden == 0: 
            nt.seen_units.append(uni)
    
    self.nations_tiles = []
    for nt in self.seen_nations:
      self.nations_tiles += nt.seen_tiles
    if info:
      logging.debug(f"naciones descubiertas {len(self.seen_nations)}.")
      for nt in self.seen_nations:
        logging.debug(f"{nt}")
        logging.debug(f"casillas {len(nt.nations_tiles)}.")
        logging.debug(f"unidades {len(nt.seen_units)}.")
        logging.debug(f"score {nt.mean_score}.")

  def set_tiles_defense(self):
    for it in self.tiles:
      buildings = [bu for bu in it.buildings
                     if bu.nation == self and bu.type == building_t
                     and self in bu.nations]
      it.defense_req = it.income * 0.1
      if it.corpses: it.defense_req += 50
      if buildings:
        it.defense_req += 40 * len(buildings)
      if it.surf.name in [forest_t, swamp_t]: 
        it.defense_req += 20
      if it.hill:
        it.defense_req += 20
      if it.around_nations: it.defense_req += 40
      if it.unrest >= 15 and it.pop >= 40: it.defense_req += it.unrest
      for bu in buildings:
        if military_t in bu.tags: it.defense_req *= 1.5
      it.defense_req = it.defense_req if it.defense_req < 300 else 300 

  def set_threat(self):
    self.seen_threat = sum(ct.seen_threat for ct in self.cities)

  def setup_commanders(self, info=1):
    logging.info(f"setup_commanders for {self}.")
    comms = self.get_free_comms()
    comms.sort(key=lambda x: x.ranking)
    comms.sort(key=lambda x: x.pos.around_threat + x.pos.threat, reverse=True)
    if info: logging.debug(f"{comms=:}.")
    for com in comms:
      if info: logging.debug(f"{com}.")
      leadership = com.leadership
      threats = [com.pos.around_threat]
      if com.pos.city and com.pos.nation in com.belongs: 
        threats += [com.pos.city.seen_threat] 
      threat = max(threats)
      if info:
        msg = f"setup {threat=:}." 
        logging.debug(msg)
        com.log[-1] += [msg]
      if threat < com.pos.defense * 0.4: leadership *= 0.7
      if info: logging.debug(f"{leadership=:}.")
      # if com is random.
      if self in com.pos.world.random_nations:
        if info:
          msg = f"is random" 
          logging.debug(msg)
          com.log[-1] += [msg] 
        leadership = com.leadership
      com.create_group(leadership)
    
    comms = [com for com in self.units_comm if com.leads]
    [com.set_lead_disband() for com in comms]
    for com in comms:
      for uni in com.leads: 
        if uni.squads < uni.max_squads * 0.5: basics.ai_join_units(uni)
    [com.set_army_auto() for com in comms]

  def start_turn(self):
    if self.pos: world = self.pos.world
    else: world = self.world
    if world.turn == 0: msg = f"{turn_t} {world.turn+1}." 
    else: msg = f"{turn_t} {world.turn}."
    
    self.log += [[msg]]
    self.devlog += [[msg]]
    msg = f"{world.ambient.stime}, {world.ambient.sseason} \
    {world.ambient.smonth}, {world.ambient.syear}."
    self.log[-1] += [msg]

  def status(self, info=0):
    # self.defense_need = 0
    self.income = sum(i.income_total for i in self.cities)
    self.pop_military = 0
    self.pop = 0
    self.pop_total = 0
    for ct in self.cities:
      self.pop += ct.pop
      for uni in self.units: 
        self.pop_military += uni.total_pop
    
    self.pop_total = self.pop_military + self.pop
    self.military_percent = round(self.pop_military * 100 / self.pop_total)
    self.pop_percent = round(self.pop * 100 / self.pop_total)
    
    self.upkeep_limit_percent = self.upkeep_base
    self.upkeep_limit_percent = self.upkeep_limit_percent + (self.pop / self.upkeep_change)
    if self.upkeep_limit_percent > 100: self.upkeep_limit_percent = 100
    self. upkeep_limit = round(self.upkeep_limit_percent * self.income / 100)
    
    if info:
      logging.debug(f"estado de {self}.")
      logging.debug(f"necesita {self.defense_need} defensa.")
      logging.debug(f"civiles: {self.pop}, ({self.pop_percent}%).")
      logging.debug(f"militares: {self.pop_military} ({self.military_percent}%).")
      logging.debug(f"población total {self.pop_total}.")
      logging.debug(f"ingresos {self.income}.")
      logging.debug(f"gastos {self.upkeep}., ({self.upkeep_percent}%).")

  def update(self, scenary, info=0):
    init = time()
    self.buildings = []
    self.cities = []
    self.score = 0
    self.tiles = [t for t in scenary if t.nation == self]
    self.set_tiles_defense()
    self.units = []
    self.units_animal = []
    self.units_fly = []
    self.units_human = []
    self.units_melee = []
    self.units_mounted = []
    self.units_piercing = []
    self.units_ranged = []
    self.units_sacred = []
    self.units_undead = []
    self.upkeep = 0
    for t in scenary:
      for b in t.buildings:
        if b.nation == self:
          if b.type != city_t: self.buildings.append(b)
          if b.type == city_t: self.cities.append(b)
      for uni in t.units:
        if self in uni.belongs and uni.hp_total >= 1:
          self.units.append(uni)
    for i in self.units: i.update()
    for uni in self.units:
      if animal_t in uni.traits: self.units_animal.append(uni)
      if uni.can_fly: self.units_fly.append(uni)
      if human_t in uni.traits: self.units_human.append(uni)
      if uni.range[1] < 6: self.units_melee.append(uni)
      if uni.mounted: self.units_mounted.append(uni)
      if uni.pn: self.units_piercing.append(uni) 
      if uni.range[1] >= 6: self.units_ranged.append(uni)
      if sacred_t in uni.traits: self.units_sacred.append(uni)
      if undead_t in uni.traits: self.units_undead.append(uni)
    
    self.production = []
    for c in self.cities: 
      for p in c.production:
        self.production.append(p) 
    self.units_comm = [it for it in self.units if it.leadership]
    self.units_scout = [i for i in self.units if i.scout]
    self.units_settler = [i for i in self.units if i.settler]
    self.upkeep += sum(b.upkeep for b in self.buildings if b.is_complete)
    self.upkeep += sum(b.upkeep for b in self.cities)
    for i in self.units:
      self.upkeep += i.upkeep_total
    
    self.income = round(self.income)
    self.raid_outcome = sum(ct.raid_outcome for ct in self.cities)
    self.upkeep = round(self.upkeep)
    if self.cities:
      self.cities.sort(key=lambda x: x.capital, reverse=True)
      self.status()
      self.cities.sort(key=lambda x: x.pop)
      [ct.set_defense() for ct in self.cities]
      self.cities.sort(key=lambda x: x.pop, reverse=True)
      self.defense_min = sum(it.defense_min for it in self.cities)
      self.defense_total = sum(it.defense_total for it in self.cities) / len(self.cities)
      self.defense_total_percent = sum(it.defense_total_percent for it in self.cities) / len(self.cities)
      self.defense_mean = int(mean([i.defense_total_percent for i in self.cities]))
      self.score = round(sum(ct.defense_min for ct in self.cities))
      self.score += round(sum(ct.defense_total for ct in self.cities) / 20)
      self.set_threat()
    
    if self.cities: self.pos = self.cities[0].pos
    else: self.pos = None
    self.set_new_city_req()
    self.units.sort(key=lambda x: len(x.leads))
    # expanding.
    self.expanding = 0
    if any(i for i in [ct.expanding for ct in self.cities]): self.expanding = 1
    if info: logging.debug(f"time {time()-init}.")



class Unit:
  name = str()
  namelist = None
  nick = str()
  units = 0
  min_units = 0
  ln = 0
  unique = 0
  sts = 0
  ethereal = 0
  levy = 0
  mounted = 0
  leadership = 0
  is_leader = 0
  poisonres = 0
  type = str()
  will_less = 0
  wizard = 0
  xp = 0
  unique = 0
  traits = []
  train_rate = 1
  gold = 0
  hire_rate = 1
  upkeep = 0
  resource_cost = 0
  pop = 0
  total_pop = 0
  food = 0
  sk = []
  terrain_skills = []

  hp = 0
  sight = 1
  mp = []
  moves = 0
  resolve = 0
  luck = 0
  power = 0
  power_max = 0
  power_res = 0
  global_skills = []

  dfs = 0
  res = 0
  hres = 0
  hlm = 0
  arm = 0
  armor = None
  shield = None
  defensive_skills = []

  weapon1 = None
  att1 = 0
  weapon2 = None
  att2 = 0
  weapon3 = None
  att3 = 0
  javelins = 0
  mrng = 0
  off = 0
  strn = 1
  pn = 0
  offensive_skills = []
  
  armor_ign = 0
  common = 0
  id = 0
  hit_rolls = 1
  stealth = 0
  hp_res = 1
  hp_res_mod = 0

  ai = 1
  align = None
  anticav = 0
  attacking = 0
  auto_explore = 0
  blocked = 0
  can_burn = 0
  can_charge = 0
  charges = 0
  can_fly = 0
  can_hide = 1
  can_hire = 0
  can_join = 1
  can_raid = 0
  can_recall = 1
  can_regroup = 0
  can_retreat = 1
  city = None
  coldres = 0
  dark_vision = 0
  demon_souls = 0
  desert_survival = 0
  dist = 0
  fled = 0
  fear = 4
  forest_survival = 0
  garrison = 0
  goal = None
  going = 0
  gold = 0
  group_score = 0
  group_base = 0
  hidden = 0
  hired = 0
  lead_traits = []
  lead_alignment = []
  leader = None
  level = 1
  mountain_survival = 0
  nation = None
  night_survival = 0
  populated_land = 0
  pos = None
  pref_corpses = 0
  ranking = 0
  ranking_skills = 0 
  revealed = 0
  scout = 0
  settler = 0
  show_info = 0
  sight = 1
  sort_chance = 50
  spells = []
  squads = 1
  stopped = 0
  swamp_survival = 0
  units_min = 0
  units_max = 50
  to_avoid = 0

  def __init__(self, nation, dead=0, units=None):
    if units: self.units = units
    self.hp_total = self.hp * self.units
    if dead: self.hp_total = 0
    self.gold = self.upkeep * self.units * self.train_rate
    self.history = Empty()
    self.history.kills_record = 0
    self.history.raids = 0
    self.history.turns = 1
    self.nation = nation
    self.set_name()
    self.defensive_skills = [i(self) for i in self.defensive_skills]
    self.global_skills = [i(self) for i in self.global_skills]
    if self.ln == 0: self.ln = self.min_units
    self.offensive_skills = [i(self) for i in self.offensive_skills]
    self.other_skills = []
    self.squads_position = [self]
    self.traits = [i for i in self.traits]
    self.terrain_skills = [i(self) for i in self.terrain_skills]
    if self.weapon1: self.weapon1 = self.weapon1(self)
    if self.weapon2: self.weapon2 = self.weapon2(self)
    if self.weapon3: self.weapon3 = self.weapon3(self)
    
    self.mp = [i for i in self.mp]
    self.extra_leading = 0
    self.food_total = self.food * self.units
    self.leading = 0
    self.upkeep_total = self.upkeep * self.units

    self.battle_log = []
    self.belongs = [nation]
    self.buildings = []
    self.corpses = [Skeleton]
    self.deads = []
    self.effects = []
    self.favhill = [0, 1]
    self.favsoil = [coast_t, glacier_t, grassland_t, plains_t, ocean_t, tundra_t, waste_t]
    self.favsurf = [none_t, forest_t, swamp_t]
    self.goto = []
    self.leads = []
    self.skills = []
    self.log = []
    self.soil = [coast_t, glacier_t, grassland_t, plains_t, tundra_t, waste_t, ]
    self.surf = [forest_t, none_t, river_t, swamp_t]
    self.status = []
    self.tags = []
    self.target = None
    self.tiles_hostile = []
    self.get_skills()
    self.set_skills()
    
  def __str__(self):
    if self.nick: name = f"{self.nick}. "
    else: name = ""
    if self.units > 1: name += f"{self.units} "
    name += f" {self.name}."
    
    # if self.show_info == 0: name += f" id {self.id}."
    return name

  def add_corpses(self, pos):
    corpses = round(sum(self.deads))
    self.deads = []
    unit = self.__class__(self.nation)
    unit.deads = [corpses]
    unit.hp_total = 0
    unit.units = 0
    unit.pos = self.pos
    for it in pos.corpses:
      if it.name == unit.name:
        if len(it.deads):it.deads[0] += corpses
        else: it.deads = [corpses]
        return
    pos.units += [unit]

  def auto_attack(self):
    target = self.set_attack()
    if target:
      self.combat_pre(self.pos, target)
      self.update()
      msg = f"ataque invisible."
      self.log[-1].append(msg)
      return 1

  def autokill(self):
    if self.pos.get_nearest_nation() >= 6 and self in self.pos.world.units:
      self.hp_total = 0
      loadsound("set9")

  def attrition(self):
    if self.pos.world.turn < 2 or self.hp_total < 1: return
    if self.food_total == 0: return 
    self.pos.update(self.nation)
    food = self.pos.food_need - self.pos.food
    if food >= 80: food = 80
    food = self.pos.food_need * 100 / self.pos.food
    food -= 100
    food = round(food / 20)
    if food > 6: food = 6
    resolve = self.resolve + self.resolve_mod 
    roll = basics.roll_dice(1)
    logging.debug(f"{food =: }, {resolve =: } {roll =: }.")
    if roll < food:
      if self.desert_survival and self.pos.name == waste_t and basics.roll_dice(1) >= 3:
        logging.debug(f"sobreviviente del desierto.")
        return
      disband = 1
      if resolve <= 7: disband += randint(0, 1)
      elif resolve <= 6: disband += randint(1, 2)
      elif resolve <= 5: disband += randint(1, 3)
      elif resolve <= 4: disband += randint(2, 4)
      elif resolve <= 3: disband += randint(2, 5)
      elif resolve < 3: disband += randint(3, 6)
      
      self.hp_total -= disband * self.hp
      if self.hp_total < 1:
        msg = f"{self} se ha disuelto por atrición."
        self.nation.log[-1].append(msg)
        sleep(loadsound("notify18") * 0.5)

  def basic_info(self, nation=None):
    sp.speak(f"{self}", 1)
    if self.leads and nation in self.belongs: 
      sp.speak(f" leads {self.leading} ({len(self.leads)}) ")
    if self.extra_leading >= 1:
      loadsound("set7", vol=0.5)
      sp.speak(f"leadership exceeded {self.leading} {of_t} {self.leadership}.")
    if self.hidden:
      loadsound("hidden1", vol=0.25)
      sp.speak(f"{hidden_t}.")
    if self.other_skills:
      try:
        loadsound(choice(self.other_skills[0].sound), channel=CHUNE1, vol=0.25)
      except: loadsound("notify27", channel=CHUNE1, vol=0.25)
      for sk in self.other_skills: sp.speak(f"{sk.name}")
    belongs = [nt.name for nt in self.belongs]
    sp.speak(f"{belongs}.")
    sp.speak(f"hp {self.hp_total}.")
    if nation in self.belongs:
      sp.speak(f"mp {self.mp[0]} {of_t} {self.mp[1]}.")
      if self.check_ready() == 0 or self.mp[0] == 0:
        sleep(loadsound("no_moves") / 2)
    if self.goto and isinstance(self.goto[0], list):
      loadsound("walk_ft1")
      goto = self.goto[0][1]
      cord = ""
      if self.pos.y < goto.y: cord += f"{south_t}." 
      if self.pos.y > goto.y: cord += f"{north_t}."
      if self.pos.x < goto.x: cord += f" { east_t}."  
      if self.pos.x > goto.x: cord += f" {west_t}."
      sp.speak(f"{heading_to_t} {cord}")
      if self.goto[0][1] in self.pos.world.nations[self.pos.world.player_num].map:
        sp.speak(f"{self.goto[0][1]}.")
        sp.speak(self.goto[0][1].cords)
      else: sp.speak(f"...")

  def break_group(self):
    logging.debug(f"{self} rompe grupo.")
    if self.show_info: loadsound("set1")
    for i in self.leads: 
      i.leader = None
      i.goto = []
    self.leads = []
    self.update()

  def burn(self, cost=0):
    buildings = [b for b in self.pos.buildings if b.type == building_t and b.nation != self.nation
                 and self.nation in b.nations and b.resource_cost[0] > 0]
    if buildings and self.mp[0] >= cost and self.can_burn:
      if [i for i in self.pos.units
          if i.nation not in self.belongs]:
        return
      self.pos.update(self.pos.nation)
      
      self.update()
      building = choice(buildings)
      damage = self.damage 
      damage *= self.units
      if self.resolve + self.resolve_mod >= 7: damage *= 0.3
      if self.resolve + self.resolve_mod >= 5: damage *= 0.2
      else: damage *= 0.1
      building.resource_cost[0] -= damage
      self.pos.burned = 1
      msg = f"{self} {burn_t} {building}. {in_t} {self.pos.city} {self.pos.cords}"
      self.log[-1].append(msg)
      self.nation.log[-1].append(msg)
      if self.pos.nation and self.nation != self.pos.nation: self.pos.nation.log[-1].append(msg)
      logging.debug(msg)
      if building.resource_cost[0] < 1:
        msg = f"{building} {has_been_destroyed_t} {in_t} {self.pos.cords}."
        self.log[-1].append(msg)
        self.nation.log[-1].append(msg)
        if self.pos.nation and self.nation != self.pos.nation: self.pos.nation.log[-1].append(msg)
        if building.nation in self.pos.world.random_nations: self.pos.world.log[-1] += [msg]
        logging.debug(msg)
        gold = building.gold // 2
        self.nation.gold += gold
        msg = [f"{gold} {gold_t}."]
        self.log[-1].append(msg)
        self.nation.log[-1].append(msg)
        if self.pos.nation and self.nation != self.pos.nation: self.pos.nation.log[-1].append(msg)
        logging.debug(msg)
      if self.pos.nation and any(i for i in [self.nation.show_info, self.pos.nation.show_info]): 
        sleep(loadsound("build_burn01", channel=CHTE1) * 0.5)

  def can_pass(self, pos):
    try:
      if pos.soil.name in self.soil and pos.surf.name in self.surf: return True
    except: Pdb().set_trace()

  def check_enemy(self, pos, is_city=0, info=0):
    if info: logging.debug(f"check enemy, {is_city=:}.")
    pos.update(self.nation)
    if is_city and pos.nation not in self.belongs:
      self.revealed = 1
      for i in pos.units:
        i.revealed = 1
        i.update()
    self.update()
    for uni in pos.units:
      if self.hidden == 0 and self.nation not in uni.belongs and uni.hidden == 0:
        logging.warning(f"enemigo {uni}.")
        return 1

  def check_position(self):
    logging.debug(f"checking position.")
    if self.pos.is_city and self.pos.nation not in self.belongs and self.hidden == 0:
      if self.check_enemy(self.pos, is_city=1) == None: 
        if self.nation not in self.pos.world.random_nations:
          if self.pos.defense >= 50 * self.pos.city.pop / 100: self.take_city()

  def check_ready(self, info=0):
    if info: logging.info(f"check_ready for {self} {on_t} {self.pos} {self.pos.cords}.")
    go = 1
    for i in self.leads:
        if info: logging.debug(f"{i} pos {i.pos.cords}. {self} pos {self.pos.cords}.")
        if i.pos != self.pos: go = 0
        if i.mp[0] < i.mp[1]: go = 0
    if self.leads: 
      if info: logging.debug(f"go {go}.")
    return go
  
  def combat_armors(self, hit_to, pn, target, info=0):
    if info:logging.info(f"armors.")
    if hit_to == "body":
      roll = basics.roll_dice(1)
      armor = target.arm + target.arm_mod
      if target.armor: armor += target.armor.arm
      if target.armor_ign + target.armor_ign_mod == 0: armor -= pn
      else: 
        if info: logging.debug(f"{target} ignora pn.")
      armor = self.get_armor_mod(armor)
      if info: logging.debug(f"roll{roll} necesita {armor}.")
      if roll >= armor and armor > 0:
        self.hits_armor_blocked[-1] += 1
        return 1

  def combat_charge(self, damage, info=0):
    self.temp_log += [f"{self} {charges_t}"]
    if self.weapon1: damage += self.weapon1.damage
    if self.weapon2: damage += self.weapon2.damage
    if info: logging.debug(f"{self} {charges_t}.")
    self.charges = 0
    return damage
  
  def combat_critical(self, damage, weapon, hit_to, info=0):
    if hit_to == "body": self.hits_body[-1] += 1
    elif hit_to == "head": self.hits_head[-1] += 1
    luck = self.luck + self.luck_mod
    if basics.roll_dice(1) >= 6 - luck: 
      damage += weapon.critical
      self.critical_damage += 1
    
    return damage

  def combat_damage(self, damage, target, info=0):
    if damage > target.hp_total: damage = target.hp_total
    self.damage_done[-1] += damage
    target.hp_total -= (damage)
    if info: logging.info(f"{target} recibe {damage} de daño.")
    target.update()
    target.deads[-1] += target.c_units - target.units
    self.kills[-1] += target.c_units - target.units

  def combat_dex(self, weapon):
    target = self.target
    weapons = [self.weapon1, self.weapon2, self.weapon3]
    modifier = weapon.modifier 
    damage = weapon.damage
    damage += self.strn + self.strn_mod
    damage -= target.res + target.res_mod
    if damage < 1: damage = 1
    head_damage = weapon.damage
    head_damage += self.strn + self.strn_mod
    head_damage -= target.hres + target.hres_mod
    if head_damage < 1: head_damage = 1
    self.temp_log += [
    f"{self} {attacking_t}. dist {self.dist}"]
    if weapons.index(weapon) == 0: 
      self.temp_log += [f"att1 {self.att1+self.att1_mod} ({self.att1_mod})."]
    if weapons.index(weapon) == 1: 
      self.temp_log += [f"att2 {self.att2+self.att2_mod} ({self.att2_mod})."]
    if weapons.index(weapon) == 2: 
      self.temp_log += [f"att3 {self.att3+self.att3_mod} ({self.att3_mod})."]
    self.temp_log += [
      f"{weapon_t}: {weapon.name},"
      f"weapon damage: {weapon.damage},"
      f"weapon critical: {weapon.critical},", ]
    if modifier: self.temp_log += [modifier]
    self.temp_log += [
      f"{range_t}: {weapon.range_min, weapon.range_max},",
      f"{damage_t}: {damage},"
      f"head damage: {head_damage}."
      ]

  def combat_fight(self, weapon, info=0):
    target = self.target
    # Shield setting.
    if weapon.shield and self.combat_shield(target, info): return
    # Hits setting.
    if weapon.hits and self.combat_hits(self.off + self.off_mod, info) == None: return
    # Hit_to
    hit_res = self.combat_hit_to(target)
    hit_to = hit_res[0]
    res = hit_res[1]
    # Wound setting.
    if weapon.hit_to: 
      hit_to = weapon.hit_to
    # if weapon.wounds:
      # if self.combat_wounds(res, self.strn + self.strn_mod, info) == None: return
    # Damage setting.
    damage = weapon.damage
    strn = self.strn + self.strn_mod
    if hit_to == "body": res = self.target.res + self.target.res_mod
    elif hit_to == "head": res = self.target.hres + self.target.hres_mod
    damage += strn - res
    if damage < 1: damage = 1
    
    # Pn setting.
    pn = weapon.pn
    pn += floor((strn - res) / 3)
    if pn < 0: pn = 0
    
    # Armors setting.
    if weapon.armor and self.target.armor and self.combat_armors(hit_to, pn, target, info) == 1: return
    # Critical setting.
    damage = self.combat_critical(damage, weapon, hit_to)
    # Charge setting
    if self.charges: damage = self.combat_charge(damage, info=0) 
    self.combat_damage(damage, target, info=0)

  def combat_gold(self):
    value = self.upkeep * self.units
    value += sum(it.upkeep * it.units for it in self.leads)
    value *= self.train_rate
    raids = self.history.raids
    raids += sum(it.history.raids for it in self.leads)
    kills_record = self.history.kills_record
    kills_record += sum(it.history.kills_record for it in self.leads)
    value += raids
    if kills_record: value += kills_record * 2
    value = ceil(value / 2)
    value *= 1 + self.history.turns / 4
    if self.mounted: value *= 3
    value = round(value * uniform(0.8, 1.2))
    return value

  def combat_hits(self, off, info=0):
    if info:logging.info(f"hits.")
    target = self.target
    hit_rolls = self.hit_rolls + self.hit_rolls_mod
    for i in range(hit_rolls):
          if info: logging.debug(f"impactos {i} de {hit_rolls}")
          hit_roll = basics.roll_dice(1)
          if info: logging.debug(f"{hit_roll=:}.")
          off_need = off
          if info: logging.debug(f"off_need1  {off_need}.")
          off_need -= target.dfs + target.dfs_mod
          if info: logging.debug(f"off_need2 {off_need}.")
          off_need = self.get_hit_mod(off_need)
          if info: logging.debug(f"off_need3 {off_need}.")
          if hit_roll >= off_need:
            self.strikes[-1] += 1
            return 1
  
  def combat_hit_to(self, target, info=0):
    hit_to = "body"
    res = target.res + target.res_mod
    roll = basics.roll_dice(1)
    if self.dist < 6:
      head_factor = 6
      size_factor = (self.size + self.size_mod) - (self.target.size + self.target.size_mod)
      head_factor -= size_factor
      head_factor -= (self.range[1])
    elif self.dist >= 6 or self.can_fly: head_factor = 4
    if roll >= head_factor:
      hit_to = "head"
      if info:logging.debug(f"hit to the head.")
      res = target.hres + target.hres_mod
    return hit_to, res

  def combat_menu(self, target=None, attacker_log=[], defender_log=[], info=0):
    logging.info(f"combat_menu for {self}.")
    self.update()
    if self not in  self.pos.units:
      logging.warning(f"self not in self.pos")
      Pdb().set_trace()
    go = 1
    target.update()
    dist = max(self.range[1], target.range[1])
    dist += randint(4, 8)
    if self.hidden: dist = self.range[1]
    self.pos.update()
    target.pos.update(target.nation)
    end_of_combat = 0
    self.attacking = 1
    self.target = target
    self.won = 0
    target.attacking = 0
    target.can_retreat = 1
    target.target = self
    target.won = 0
    units = [self, target]
    msg1 = f"{self} ({self.nation}) ataca a {target} ({target.nation})."
    for it in [attacker_log, defender_log]:
      it[1][0] += [[msg1]]
    if info:logging.info(msg1)
    if info:logging.info(f"hp {self} {self.hp_total}, target {target} {target.hp_total}.")
    if info:logging.info(f"ranking {self.ranking} VS {target.ranking}.")
    for i in units:
      i.dist = dist
      if i.can_charge: i.charges = 1
      i.pre_melee = i.javelins 
      i.attacks = []
      i.battle_log = []
      i.damage_done = []
      i.deads = []
      i.enemy_fled = []
      i.fled = []
      i.hits_armor_blocked = []
      i.hits_body = []
      i.hits_blocked = []
      i.hits_head = []
      i.hits_resisted = []
      i.hits_shield_blocked = []
      i.hits_failed = []
      i.kills = []
      i.strikes = []
      i.raised = []
      i.temp_log = None
      i.wounds = []
      i.retreats = 0
    _round = 1
    while self.hp_total > 0 or target.hp_total > 0:
      if go:
        # logging.debug(f"ronda {_round}.")
        shuffle(units)
        [i.update() for i in units]
        units.sort(key=lambda x: x.range, reverse=True)
        units.sort(key=lambda x: x.moves + x.moves_mod, reverse=True)
        units.sort(key=lambda x: x.hidden, reverse=True)
        for i in units:
          i.attack = 1
          i.attacks += [0]
          i.aa_log = []
          i.ac_log = []
          i.ba_log = []
          i.bc_log = []
          i.damage_done += [0]
          i.deads += [0]
          i.fled += [0]
          i.hits_armor_blocked += [0]
          i.hits_blocked += [0]
          i.hits_body += [0]
          i.hits_head += [0]
          i.hits_resisted += [0]
          i.hits_shield_blocked += [0]
          i.hits_failed += [0]
          i.kills += [0]
          i.raised += [0]
          i.strikes += {0} 
          i.target.c_units = i.target.units
          i.wounds.append(0)
        
        # log
        shields = []
        if self.shield: shields += [self.shield.name]
        else: shields += [none_t]
        if target.shield: shields += [target.shield.name]
        else: shields += [none_t]
        
        armors = []
        if units[0].armor: armors += [units[0].armor.name]
        else: armors += [none_t]
        if units[1].armor: armors += [units[1].armor.name]
        else: armors += [none_t]
        temp_log = [
          f"{round_t} {_round}.",
          f"{units[0]} {health_t} {units[0].hp_total}. ranking {units[0].ranking} \
          vs {units[1]} {health_t} {units[1].hp_total}. ranking {units[1].ranking}.",
          f"{resolve_t}: {units[0].resolve+units[0].resolve_mod} ({units[0].resolve_mod}) VS "
          f"{units[1].resolve+units[1].resolve_mod} ({units[1].resolve_mod}).",
          
          f"{moves_t}: {units[0].moves+units[0].moves_mod} ({units[0].moves_mod}) VS "
          f"{units[1].moves+units[1].moves_mod} ({units[1].moves_mod}).",
          
          f"{skills_t} {units[0].skill_names}. VS {units[1].skill_names}.",
          f"{effects_t} {units[0].effects}. VS {units[1].effects}.",
          
          f"dfs: {units[0].dfs+units[0].dfs_mod} ({units[0].dfs_mod}) VS "
          f"{units[1].dfs+units[1].dfs_mod} ({units[1].dfs_mod})",
          
          f"res: {units[0].res+units[0].res_mod} ({units[0].res_mod}) VS "
          f"{units[1].res+units[1].res_mod} ({units[1].res_mod})",
          
          f"hres: {units[0].hres+units[0].hres_mod} ({units[0].hres_mod}) VS "
          f"{units[1].hres+units[1].hres_mod} ({units[1].hres_mod})",
          
          f"off: {units[0].off+units[0].off_mod} (+{units[0].off_mod}) " 
          f"VS {units[1].off+units[1].off_mod} (+{units[1].off_mod}).",
          f"strn: {units[0].strn+units[0].strn_mod} (+{units[0].strn_mod}) " 
          f"VS {units[1].strn+units[1].strn_mod} (+{units[1].strn_mod}).",
          f"shield: {shields[0]} VS {shields[1]}.",
          f"armor: {armors[0]} VS {armors[1]}." 
          ]
          
        for i in units:
          i.temp_log = temp_log
          i.combat_round = _round
        
        # before combat.
        [i.before_combat() for i in units]
        for uni in units:
          dist = uni.dist
          if uni.hp_total > 0: dist = uni.combat_moves(dist,)
          self.dist, target.dist = [dist, dist]
          [sk.run(uni) for sk in uni.skills if sk.type == "before attack"]
          if uni.dist in range(uni.range[0], uni.range[1] + 1): uni.combat_settings(_round)
          [sk.run(uni) for sk in uni.skills if sk.type == "after attack"]
          # before attack retreats
          if uni.target.hp_total > 0 and uni.target.deads[-1]: 
            if uni.target.resolve + uni.target.resolve_mod <= 5:
              uni.target.combat_retreat()
        # After attack retreats.
        [uni.combat_retreat() for uni in units if uni.resolve + uni.resolve_mod >= 6]
        
        # after combat.
        [i.after_combat() for i in units if i.hp_total > 0]
        dist = units[0].dist
        
        # fin del turno.
        self.set_combat_log(units)
        _round += 1
        for i in units:
          if dist == 1: i.charging = 0
        
        if _round == 50: Pdb().set_trace()
        # end of combat.
        if any(i.hp_total < 1 for i in units): end_of_combat = 1
        if any(i.retreats for i in units): end_of_combat = 1
        if end_of_combat:
          self.mp[0] -= 1
          [i.stats_battle() for i in [self, target] if i.hp_total >= 1]
          self.combat_post(target, info)
          msg2 = f"""
          {kills_t} {sum(self.kills)}, {deads_t} {sum(self.deads)}, 
          {fled_t} {sum(self.fled)}. VS 
          {kills_t} {sum(target.kills)}, {deads_t} {sum(target.deads)}, 
          {fled_t} {sum(target.fled)}.
          """
          for it in [attacker_log, defender_log]:
            it[1][0][-1] += [self.battle_log]
            it[1][0] += [msg2]
          for i in units:
            i.add_corpses(target.pos)
          if self.hp_total < 1 or self.retreats:
            msg = f"{target} ({target.nation}) a vencido."
            if target.show_info: sp.speak(msg)
            logging.info(msg)
            attacker_log[1][0] += [msg]
            defender_log[1][0] += [msg]
            # self.combat_log[-1][0] += [msg]
            # target.pos.world.log[-1][-1] += target.combat_log
            logging.debug(msg)
            # check_position(target)
            return 0
          elif target.hp_total < 1 or target.retreats:
            msg = f"{self} ({self.nation}) ha vencido."
            attacker_log[1][0] += [msg]
            defender_log[1][0] += [msg]
            # target.combat_log[-1][0] += [msg]
            # target.pos.world.log[-1][-1] += target.combat_log
            logging.info(msg)
            # check_position(self)
            return 1
  
  def combat_moves(self, dist, info=1):
      moves = self.moves + self.moves_mod
      c_dist = dist
      if self.weapon1: weapon = self.weapon1
      elif self.weapon2: weapon = self.weapon2
      else: weapon = self.weapon3
      if self.target.weapon1:target_weapon = self.target.weapon1
      elif self.target.weapon2:target_weapon = self.target.weapon2
      else: target_weapon = self.target.weapon3
      if info:logging.debug(f"distancia de {self}  {dist}.")
      
      if (self.attacking and dist > weapon.range_max
          or target_weapon.range_max > weapon.range_max):
        if (self.can_charge
            and self.dist > self.range[1] + 4): self.charges = 1
        if info: logging.debug(f"forwards.")
        move = basics.roll_dice(2)
        # if self.can_fly: move += 2
        if info: logging.debug(f"{move=:}. {moves=:}.")
        if move > moves: move = moves
        # if self.hidden: move += 2
        dist -= move
        if dist < weapon.range_max: dist = weapon.range_max
        if info: logging.debug(f"distancia final {dist}.")
        msg = f"{self} advances from {c_dist} to {dist}"
        self.temp_log += [msg]
      elif dist < weapon.range_min:
        if info: logging.debug(f"backs up.")
        move = randint(0, self.moves + self.moves_mod)
        move = ceil(move / 2)
        # if self.can_fly: move += 2
        if info: logging.debug(f"{move=:}. {moves=:}.")
        if move > moves: move = moves
        # if self.hidden: move += 2
        dist += move
        if dist > self.weapon1.range_max: dist = self.weapon1.range_max
        if info: logging.debug(f"distancia final {dist}.")
        msg = f"{self} back ups from {c_dist} to {dist}"
        self.temp_log += [msg]
        if info: logging.debug(msg)
      return dist

  def combat_settings(self, _round, info=0):
    if self.hp_total < 1: return
    self.update()
    target = self.target
    target.update()
    target.c_units = target.units
    self.critical_damage = 0
    if info: logging.info(f"{self} total hp {self.hp_total} ataca.")
    weapon = None
    weapons = [self.weapon1, self.weapon2, self.weapon3]
    
    for wp in weapons:
      if wp == None: continue
      if self. dist not in range(wp.range_min, wp.range_max + 1): continue
      wp.update()
      weapon = wp
      
      self.combat_dex(weapon)
      
      ln = self.ln + self.ln_mod
      if self.ranged: ln = self.units
      if ln > self.units: ln = self.units
      for uni in range(ln):
        if info: logging.debug(f"unidad {uni+1} de {self.units}.")
        attacks = self.att1 + self.att1_mod
        for i in range(attacks):
          if target.hp_total < 1: break
          self.attacks[-1] += 1
          if info: logging.debug(f"ataque {i+1} de {attacks}.")
          target.c_units = target.units
          weapon.run()
      weapon.after_melee()
      weapon.effects()
      
    if weapon == None: return
    self.hits_failed[-1] = self.attacks[-1] - self.strikes[-1]
    if self.damage_done[-1] and self.target.hidden: 
      self.temp_log += [f"{self.target} revealed."]
      self.target.revealed = 1
    
    self.temp_log += [  
      f"{attacks_t} {self.attacks[-1]}, {hits_failed_t} {self.hits_failed[-1]}, "
      f"{hits_t} {self.strikes[-1]}.",
      ]
    if self.hits_resisted[-1]: self.temp_log += [f"resisted {self.hits_resisted[-1]}."]
    if self.hits_armor_blocked[-1]: self.temp_log += [f"armor blocked {self.hits_armor_blocked[-1]}."]
    if self.hits_shield_blocked[-1]: self.temp_log += [f"shield blocked {self.hits_shield_blocked[-1]}."]
    self.temp_log += [
      f"to the head {self.hits_head[-1]}, to the body {self.hits_body[-1]}.",
      f"{wounds_t} {self.hits_body[-1]+self.hits_head[-1]}, " 
      f"{damage_t} {self.damage_done[-1]}, {critical_t} {self.critical_damage}.",
      f"{deads_t} {self.target.deads[-1]}."
      ]

  def combat_sacred_damage(self, damage, target, info=0):
    if self.damage_sacred + self.damage_sacred_mod and undead_t in target.traits:
      damage += self.damage_sacred
      if info: logging.debug(f"damage holy {self.damage_sacred}.")
      return damage

  def combat_shield(self, target, info=0):
    if info:logging.info(f"shield.")
    if target.shield:
      roll = basics.roll_dice(1)
      shield = target.shield.dfs
      shield -= self.off + self.off_mod 
      shield = self.get_hit_mod(shield)
      if shield < roll: 
        self.hits_shield_blocked[-1] += 1
        return 1

  def combat_wounds(self, res, strn, info=0):
    if info:logging.info(f"wounds.")
    wound_roll = basics.roll_dice(1)
    if info:logging.debug(f"roll {wound_roll=}")
    wound_need = strn
    if info: logging.debug(f"wound_need1 {wound_need}.")
    wound_need -= res
    if info: logging.debug(f"wound_need2 {wound_need}.")
    wound_need = self.get_wound_mod(wound_need)
    if info: logging.debug(f"wound_need3 {wound_need}.")
    if wound_roll < wound_need:
      self.hits_resisted[-1] += 1
    else: return 1

  def after_attack(self):
    self.update()
    for sk in self.skills:
      if sk.type == "after attack": sk.run(self)
      if self.aa_log: self.temp_log += self.aa_log

  def after_combat(self):
    self.update()
    self.skills.sort(key=lambda x: x.index)
    for sk in self.skills:
      sk.run_after_combat(self)
      if self.ac_log: self.temp_log += self.ac_log

  def before_attack(self):
    self.update()
    for sk in self.skills:
      if sk.type == "before attack": sk.run(self)
      if self.ba_log: self.temp_log += self.ba_log

  def before_combat(self):
    self.update()
    for sk in self.skills:
      if sk.type == "before combat":
        sk.run(self)
        if self. bc_log: self.temp_log += self.bc_log
  
  def set_cast(self):
    cast = self.get_cast()
    if cast:
      init = cast.init(self)
      if init != None: 
        self.log[-1] += [init]
        logging.debug(init)
      self.nation.update(self.nation.map)
      self.nation.pos.map_update(self.nation, self.nation.map)
  def set_combat_log(self, units):
    log = units[0].temp_log
    # for i in units:
      # if i.aa_log: log += i.aa_log
      # if i.ac_log: log += i.ac_log 
      # if i.ba_log: log += i.ba_log
      # if i.bc_log: log += i.bc_log
    # if units[0].aa_log: log += units[0].aa_log
    # elif units[1].aa_log: log += units[1].aa_log
    # log += [
      # f"{raised_t} {units[0].raised[-1]}. {units[1].raised[-1]}.",
      # f"{fled_t} {units[0].fled[-1]}. {units[1].fled[-1]}",
      # ]
    for uni in units:
      uni.battle_log.append(log)

  def combat_post(self, target, info=1):
    logging.info(f"combat post.")
    for i in [self, target]:
      if i.hp_total > 0: i.pos.update(i.nation)
      if  i.hp_total < 1 and i.attacking: i.pos = i.target.pos
      i.attacking = 0
      i.target = None
      if i.hp_total > 0:
        skills = [sk for sk in i.skills if sk.type == "pos combat"]
        [sk(i) for sk in skills]
      if (i.will_less == 0 and i.hp_total < 1 
          and sum(i.fled) >= 1 and i.can_retreat):
        if info: logging.debug(f"{i} pierde.")
        unit = i.__class__(i.nation)
        unit.can_retreat = i.can_retreat
        unit.hp_total = sum(i.fled) * unit.hp
        unit.log = i.log
        unit.pos = i.pos
        unit.city = i.city
        unit.mp[0] = 0
        unit.other_skills = i.other_skills
        unit.level = i.level
        unit.update()
        if info: logging.debug(f"{unit} huyen {sum(i.fled)}.")
        if unit.leadership == 0 and unit.units < unit.min_units / 4: continue
        unit.pos.units.append(unit)
        if unit.can_retreat:
          if info:logging.debug(f"se retirará.")
          unit.mp[0] = unit.mp[1]
          tile = unit.get_retreat_pos(info=1)
          unit.move_set(tile)

  def combat_pre(self, pos, target=None, info=1):
    logging.info(f"pre_combat for {self}.")
    self.update()
    _units = [it for it in pos.units 
              if it.nation not in self.belongs and it != self 
              and it.hidden == 0]
    _units = [it for it in _units 
              if it.leader == None or it.leader and it.leader.pos != it.pos]
    [it.update() for it in _units]
    _units.sort(key=lambda x: sum([x.off, x.off_mod, x.strn, x.strn_mod]), reverse=True)
    _units.sort(key=lambda x: x.units, reverse=True)
    _units.sort(key=lambda x: x.ranged, reverse=True)
    _units.sort(key=lambda x: x.mp[0] > 0, reverse=True)
    
    if target == None:
      if _units: target = _units[0]
      else: return
    
    if self.leadership:
      attackers = self.squads_position
      leader1 = self
    elif self.leader == None or self.leader and self.pos != self.leader.pos: 
      attackers = self.squads_position
      leader1 = self
    elif self.leader and self.pos == self.leader.pos:
      attackers = self.leader.squads_position
      leader1 = self.leader
    attacker_gold = leader1.combat_gold()
    squads1 = [str(i) for i in leader1.squads_position]
    
    if target.leadership:
      defenders = target.squads_position
      leader2 = target
    elif (target.leader == None or target.leader 
        and target.leader.pos != target.pos): 
      defenders = _units
      leader2 = defenders[0]
      defenders.sort(key=lambda x: x != leader2,reverse=True)
    elif target.leader and target.pos == target.leader.pos: 
      defenders = target.leader.squads_position
      leader2 = target.leader
    defender_gold = leader2.combat_gold()
    squads2 = [str(i) for i in leader2.squads_position]    
    
    if target.pos.city: 
      combat_location = f"""{combat_t} {in_t} {pos.city}, {pos}, {pos.cords}  
      {from_t} {self.pos}, {self.pos.cords}."""
    else: 
      combat_location = f"""{combat_t} {in_t} {pos}, {pos.cords} "  
      {from_t} {self.pos}, {self.pos.cords}."""    
    
    combat_desc = [f"{attacking_t} {leader1}, {ranking_t} {leader1.ranking}.",
            f"{squads1}.",
            f"{defending_t} {leader2}, {ranking_t} {leader2.ranking}.",
            f"{squads2}.",
            ] 
    attacker_log = copy.deepcopy([combat_location, [combat_desc]])
    defender_log = copy.deepcopy([combat_location, [combat_desc]])
    self.nation.log[-1] += [attacker_log]
    target.nation.log[-1] += [defender_log]
    self.pos.world.log[-1] += [attacker_log]
    for i in attackers:
      i.combat_log = []
      i.log[-1] += [attacker_log]
    for i in defenders:
      i.combat_log = []
      i.log[-1] += [defender_log]
    
    # Combatants list:
    if info:
      logging.debug(f"attackers:")
      for it in attackers: 
        logging.debug(f" {it} {it.nation}.")
      logging.debug(f" defenders:")
      for it in defenders:
        logging.debug(f" {it} {it.nation}.")
    
    # Start of combat
    info = 1 if any(it.show_info == 1 for it in [leader1, leader2]) else 0
    if info: sleep(loadsound("warn4", channel=CHTE3) / 2)
    while attackers and defenders:
      attackers[0].combat_menu(defenders[0],
                               attacker_log=attacker_log, defender_log=defender_log)
      attackers = [it for it in attackers if it. hp_total >= 1]
      defenders = [it for it in defenders if it. hp_total >= 1]
    
    # End of combat
    if attackers:
      msg = f"{leader1.nation} {gets_t} {defender_gold} {gold_t}"
      self.nation.gold += defender_gold
      attacker_log[1][0] += [msg]
      # XP.
      for i in attackers: i.xp += ceil(defender_gold * 0.02)
      if leader1.show_info:
        sleep(loadsound("win1")) 
      return 1
    elif defenders:
      msg = f"{leader2.nation} {gets_t} {defender_gold} {gold_t}"
      self.nation.gold += attacker_gold
      defender_log[1][0] += [msg]
      if leader2.show_info: sleep(loadsound("notify18"))
      # XP.
      for i in defenders: i.xp += ceil(attacker_gold * 0.02) 
      return 0
  
  def combat_retreat(self, info=0):
    if info: logging.debug(f" combat retreat.")
    self.update()
    if info: logging.debug(f"{self} retreat units {self.units} hp {self.hp_total}.")
    if death_t in self.traits:
      logging.debug(f"{death_t}.")
      return
    dead = self.deads[-1]
    if info: logging.info(f"{self} loses {dead}.")
    
    roll = basics.roll_dice(1)
    if info: logging.debug(f"dado {roll}.")
    roll += dead
    if info: logging.debug(f"dado {roll}.")
    resolve = self.resolve + self.resolve_mod
    if info: logging.debug(f"{self} resolve {resolve}.")
    if roll > resolve:
      retreat = roll - resolve
      if retreat > self.units: retreat = self.units
      self.hp_total -= retreat * self.hp 
      msg = f"{fleed_t} {retreat} {of_t} {self}."
      self.fled[-1] += retreat
      self.temp_log += [msg]
      if info: logging.debug(msg)
      self.update()
      if info: logging.debug(f"total huídos {self.fled}.")

  def create_group(self, leadership, chosen_units=None, info=1):
    logging.info(f"{self} leading {self.leading} creates  {leadership}")
    if self.leading + leadership > self.leadership: 
      leadership = self.leadership
      leadership -= self.leading
      if info:
        msg = f"leadership moved to {leadership}."
        logging.debug(msg)
        self.log[-1] += [msg]
    if leadership < 1: return
    self.group_base = leadership
    units = [] 
    distance = 1
    if self.pos.city and self.pos.city.capital: distance += 1
    sq = [s for s in self.pos.get_near_tiles(distance)]
    if self.pos.city and self.pos.city.capital == 0:
      sq = [it for it in sq if it.city == self.pos.city]
    for s in sq:
      for it in s.units:
        if it.leadership: continue
        if it.leader or it.nation not in self.belongs: continue
        if  it.goal or it.settler: continue
        it.pos.update(it.nation) 
        if it.pos != self.pos and it.will_less: continue
        if (it.pos.around_threat + it.pos.threat and it.pos != self.pos 
            and self.pos.around_threat + self.pos.threat < self.ranking * 0.5): 
          continue
        if it.scout and it.pos.get_distance(it.pos, self.pos) > 2: continue
        units += [it]
    if chosen_units: units = chosen_units
    shuffle(units)
    units.sort(key=lambda x: x.pos.get_distance(self.pos, x.pos))
    units.sort(key=lambda x: x.pos.around_threat + x.pos.threat)    
    
    if info:
      msg = f"available before to set_lead_traits {len(units)}." 
      logging.debug(msg)
      self.log[-1] += [msg]
    units = self.set_lead_traits(units)
    if info:
      msg = f"available after to set_lead_traits {len(units)}." 
      logging.debug(msg)
      self.log[-1] += [msg]
    if len(units) == 0:
      if info: logging.debug(f"not units available.")
      return
    self.log[-1] += [f"creates leads of {self.group_base}. on {self.pos} {self.pos.cords}."]
    leading = 0
    for i in units:
      if info: logging.debug(f"{self.leadership=: } {self.leading=: }.")
      if info: logging.debug(f"encuentra a {i}")
      if leading + i.units < leadership:
        self.leads += [i]
        i.leader = self
        i.scout = 0
        i.goto = []
        if info: logging.debug(f"{i} se une con {i.ranking} ranking.")
        leading += i.units
        if info: logging.debug(f"quedan {leadership - leading}.")
        self.log[-1] += [f"{i} on {i.pos} {i.pos.cords} added to group."]
        i.log[-1] += [f"added to {self} leads on {self.pos} {self.pos.cords}."]
        i.join_group()
        if leading >= leadership:
          if info: logging.debug(f"grupo creado.") 
          break
      else:
        logging.debug(f"full leading.")
        i.split()
        break        

  def disband(self, hired=0):
    if self.hired: 
      self.pos.units.remove(self)
      self.nation.update(self.pos.scenary) 
    elif self.city and self.can_recall:
      self.city.pop_back += self.total_pop
      if self in self.nation.units: self.nation.units.remove(self)
      self.pos.units.remove(self)
      self.nation.update(self.pos.scenary)

  def get_armor_mod(self, num):
    if num >= 5: return 2
    if num >= 4: return 3
    if num >= 3: return 4
    if num >= 2: return 5
    if num >= 1: return 6
    if num <= 0: return 0

  def get_cast(self):
    sleep(loadsound("in1") * 0.5)
    sp.speak(f"hechisos.")
    say = 1
    x = 0
    while True:
      sleep(0.001)
      if say and self.spells:
        sp.speak(f"{self.spells[x].name}. {cost_t} {self.spells[x].cost}.", 1)
        say = 0
  
      for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_F1:
            sp.speak(f"{power_t} {self.power} {of_t} {self.power_max}.")
          if event.key == pygame.K_HOME:
            x = 0
            loadsound("s2")
            say = 1
          if event.key == pygame.K_END:
            x = len(self.spells) - 1
            loadsound("s2")
            say = 1
          if event.key == pygame.K_UP:
            x = basics.selector(self.spells, x, go="up")
            say = 1
          if event.key == pygame.K_DOWN:
            x = basics.selector(self.spells, x, go="down")
            say = 1
          if event.key == pygame.K_i:
            pass
          if event.key == pygame.K_RETURN:
            if self.spells: return self.spells[x](self)
          if event.key == pygame.K_F12:
            sp.speak(f"on", 1)
            Pdb().set_trace()
            sp.speak(f"off", 1)
          if event.key == pygame.K_ESCAPE:
            loadsound("back3")
            return



  def get_favland(self, pos):
    go = 1
    if pos.soil.name not in self.favsoil: go = 0
    if pos.surf.name not in self.favsurf: go = 0
    if pos.hill not in self.favhill: go = 0
    return go

  def get_fear(self):
    fear = 1
    fear += self.fear / 2
    return fear

  def get_hire_units(self, sound="in1", auto=0):
    logging.info(f"get_hire_unitss for {self}.")
    if self.show_info: sleep(loadsound(sound) / 2)
    say = 1
    x = 0
    units = []
    for bu in self.pos.buildings: 
      if bu.nation in self.pos.world.random_nations: 
        units += [i for i in bu.av_units]
    for uni in units:
      uni._go = 1
      for t in uni.traits:
        if t not in self.lead_traits: uni._go = 0
      if uni.aligment not in self.lead_aligments: uni._go = 0
      
    units = [i(self.nation) for i in units if i._go == 1]
    if auto:
      if units == []: return
      shuffle(units)
      for i in units:
        cost = i.gold * 1.5
        cost *= self.hire_rate
        if self.nation.upkeep_limit > self.nation.upkeep + cost:
          self.set_hire(i)
          break
      return
    while True:
      sleep(0.001)
      if say:
        if units: 
          cost = units[x].gold * 1.5
          cost *= self.hire_rate
          sp.speak(f"{units[x]} {cost}.")
        else: sp.speak(f"{empty_t}.")
        say = 0
      
      for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_UP:
            x = basics.selector(units, x, go="up")
            say = 1
          if event.key == pygame.K_DOWN:
            x = basics.selector(units, x, go="down")
            say = 1
          if event.key == pygame.K_HOME:
            x = 0
            say = 1
            loadsound("s1")
          if event.key == pygame.K_END:
            x = len(units) - 1
            say = 1
            loadsound("s1")
          if event.key == pygame.K_i:
            units[x].info(self.nation)
          if event.key == pygame.K_RETURN:
            if units: 
              self.set_hire(units[x])
            else: sleep(loadsound("errn1") / 2)
            say = 1
          if event.key == pygame.K_F12:
            sp.speak(f"on.", 1)
            Pdb().set_trace()
            sp.speak(f"off.", 1)
          if event.key == pygame.K_ESCAPE:
            return sleep(loadsound("back1") / 2)

  def get_hit_mod(self, num):
    if num >= 4: return 2
    elif num >= 1: return 3
    elif num >= -2: return 4
    elif num >= -7: return 5 
    else: return 6

  def get_retreat_pos(self, info=0):
    if info: logging.info(f"retreat_pos")
    if info:logging.debug(f"pocición inicial {self.pos} {self.pos.cords}.")
    sq = self.pos.get_near_tiles(1)
    sq = [i for i in sq
          if i.soil.name in self.soil and i.surf.name in self.surf and i != self.pos
          and (self.can_fly == 0 and i.cost <= self.mp[0])
          or (self.can_fly and i.cost_fly <= self.mp[0])]
    [s.update(self.nation) for s in sq]
    if info:logging.debug(f"{len(sq)} casillas para retirada.")
    shuffle(sq)
    sq.sort(key=lambda x: x.nation == None, reverse=True)
    sq.sort(key=lambda x: x.nation == self.nation, reverse=True)
    sq.sort(key=lambda x: x.threat)
    sq.sort(key=lambda x: x.cost)
    for i in sq:
      if info: logging.debug(f"{i}, {i.cords}.")
    for s in sq:
      if s.cost <= self.mp[1]: return sq[0]

  def get_skills(self):
    if hasattr(self, "other_skills") == False:
      self.other_skills = []
    self.skills = [i for i in self.global_skills + self.terrain_skills  
                   +self.defensive_skills + self.offensive_skills   
                   +self.other_skills]
    self.skills_tags = []
    for sk in self.skills:
      self.skills_tags += sk.tags
    return self.skills
  
  def get_total_food(self):
    msg = f"{food_t} {self.food} total ({self.food*self.units}).\n"
    self.food_total = self.food*self.units
    if self.leads:
      leading = sum(it.food*it.units for it in self.leads+[self])
      self.food_total = leading
      msg += f"total leading {self.food_total}."
    return msg
  def get_wound_mod(self, num):
    if num >= 2: return 2
    elif num >= 1: return 3
    elif num >= 0: return 4
    elif num >= -1: return 5 
    else: return 6

  def go_home(self, info=0):
    tiles = self.nation.tiles
    tiles.sort(key=lambda x: x.around_threat + x.threat)
    tiles.sort(key=lambda x: x.get_distance(self.pos, x))
    tiles.sort(key=lambda x: x.cost)
    if info: logging.debug(f"{self} regresa.")
    self.goto = []
    self.goal = [base_t, tiles[0]]
    self.move_set(tiles[0])

  def info(self, nation, sound="in1"):
    sleep(loadsound(sound))
    say = 1
    x = 0
    self.update()
    while True:
      sleep(0.01)
      if say:
        effects = [e for e in self.effects]
        if self.armor: armor = self.armor.name
        else: armor = "no"
        if self.defensive_skills: defensive_skills = [s.name for s in self.defensive_skills]
        else: defensive_skills = "No"
        if self.global_skills: global_skills = [s.name for s in self.global_skills]
        else: global_skills = "No"
        if nation in self.belongs: mp = f"{self.mp[0]} {of_t} {self.mp[1]}."
        else: mp = "X"
        if self.offensive_skills: offensive_skills = [s.name for s in self.offensive_skills]
        else: offensive_skills = "No"
        if self.power_max: power = f"{self.power} {of_t} {self.power_max}, restores {self.power_res}."
        else: power = f"x"
        if self.shield: shield = self.shield.name
        else: shield = "no"
        if self.spells: spells = [s.name for s in self.spells]
        else: spells = "No"
        if self.terrain_skills: terrain_skills = [s.name for s in self.terrain_skills]
        else: terrain_skills = "No"
        weapons = []
        if self.weapon1:weapons = [self.weapon1.name]
        if self.weapon2:weapons = [self.weapon2.name]
        if self.weapon3:weapons = [self.weapon3.name]
        special_traits = []
        if self.mounted: special_traits += [mounted_t]
        if self.poisonres: special_traits += [poisonres_t]
        if self.settler: special_traits += [settler_t]
        if self.will_less: special_traits += [will_less_t]
        if self.wizard: special_traits += [wizard_t]
        
        lista = [
          f"{self}. total hp {self.hp_total}.",
          f"{squads_t} {self.squads} {of_t} {self.max_squads}, {ranking_t} {self.ranking}.",
          f"level {self.level}, XP {self.xp}.",
          f"{stealth_t} {self.stealth+self.stealth_mod} ({self.stealth_mod}).",
          ]
        if self.leadership: 
          lista += [
            f"{leadership_t} {self.leadership} {leading_t} {self.leading}.",
            f"lead traits {self.lead_traits}.",
            f"lead_aligments {self.lead_aligments}."] 
        if special_traits: lista += [f"{special_traits}."]
        lista += [
          # f"{type_t}: {self.type}.",
          f"effects {effects}.",
          f"{traits_t}: {self.traits}.",
          f"{aligment_t}: {self.aligment}.",
          f"{size_t} {self.size}.",
          f"{gold_t} {self.gold}, {upkeep_t} {self.upkeep} ({self.upkeep_total}).",
          f"{resources_t} {self.resource_cost}.",
          f"{population_t} {self.pop} ({self.total_pop})>",
          f"{food_t} {self.get_total_food()}.", 
          f"terrain skills {terrain_skills}.",
          f"{health_t} {self.hp}. "
          f"{restores_t} {self.hp_res+self.hp_res_mod} (+{self.hp_res_mod}).",
          ]
        
        if self.demon_souls: lista += [f"demon souls {self.demon_souls}."]
        
        lista += [
          f"{magic_t} {power}.",
          f"mp {mp}.",
          f"{moves_t} {self.moves+self.moves_mod} ({self.moves_mod}).",
          f"{resolve_t} {self.resolve+self.resolve_mod} ({self.resolve_mod}).",
          f"global skills {global_skills}.",
          f"{defense_t} {self.dfs+self.dfs_mod} ({self.dfs_mod}).",
          f"{resiliency_t} {self.res+self.res_mod} ({self.res_mod}).",
          f"h res {self.hres+self.hres_mod} ({self.hres_mod}).",
          f"{basearm_t} {self.arm+self.arm_mod} ({self.arm_mod}).",
          f"{armor_t} {armor}.",
          f"{shield_t} {shield}.",
          f"defensive skills {defensive_skills}.",
          ]
        if self.weapon1:
          lista += [
            f"{weapon_t} {self.weapon1}",
            f"{attacks_t} {self.att1+self.att1_mod} ({self.att1_mod}).",
            ]
        if self.weapon2:
          lista += [
            f"{weapon_t}2 {self.weapon2}",
            f"{attacks_t} {self.att2+self.att2_mod} ({self.att2_mod}).",
            ]
        if self.weapon3:
          lista += [
            f"{weapon_t} {self.weapon3}",
            f"{attacks_t} {self.att3+self.att3_mod} ({self.att3_mod}).",
            ]
        lista += [
          f"{offensive_t} {self.off+self.off_mod} ({self.off_mod}).",
          f"{strength_t} {self.strn+self.strn_mod} ({self.strn_mod}).",
          f"offensive skills {offensive_skills}.",
          f"spells {spells}." 
          ]
        
        sp.speak(lista[x])
        say = 0
        
      for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_UP:
            x = basics.selector(lista, x, go="up")
            say = 1
          if event.key == pygame.K_DOWN:
            x = basics.selector(lista, x, go="down")
            say = 1
          if event.key == pygame.K_HOME:
            x = 0
            say = 1
            loadsound("s1")
          if event.key == pygame.K_END:
            x = len(lista) - 1
            say = 1
            loadsound("s1")
          if event.key == pygame.K_PAGEUP:
            x -= 10
            say = 1
            if x < 0: x = 0
            loadsound("s1")
          if event.key == pygame.K_PAGEDOWN:
            x += 10
            say = 1
            if x >= len(lista): x = len(lista) - 1
            loadsound("s1")
          if event.key == pygame.K_c:
            self.set_cast()
          if event.key == pygame.K_l:
            basics.view_log(self.log, self.nation)
          if event.key == pygame.K_s:
            self.set_auto_explore()
          if event.key == pygame.K_F12:
            sp.speak(f"debug on.", 1)
            Pdb().set_trace()
            sp.speak(f"debug off.", 1)
          if event.key == pygame.K_ESCAPE:
            return sleep(loadsound("back1") / 2)

  def join_units(self, units, info=0):
    if info: logging.info(f"join_units.")
    units.sort(key=lambda x: x.history.turns, reverse=True)
    name = units[0].name
    for i in units:
      if i.name != name or i.can_join == 0: return
      if FeedingFrenzy.name in [s.name for s in i.skills]: return
    unit = units[0]
    if unit.squads == unit.max_squads: return
    for i in units[1:]:
      if i.squads + unit.squads > unit.max_squads: 
        item = i.split(unit.max_squads - unit.squads)
        # print(f"divided.")
      elif i.squads + unit.squads <= unit.max_squads: item = i
      if unit.squads + item.squads > unit.max_squads: return
      unit.demon_souls = item.demon_souls
      unit.history.kills_record += item.history.kills_record
      unit.history.raids += item.history.raids
      unit.hp_total += item.hp_total
      unit.mp[0] = min(unit.mp[0], item.mp[0])
      for sk in item.other_skills:
        if sk.name not in [it.name for it in unit.other_skills]:
          unit.other_skills += [sk]
      msg = f"{item} has joined."
      unit.log[-1] += [msg]
      item.hp_total = 0
    unit.update()
    unit.pos.update()

  def join_group(self):
    if self.leader and self.pos != self.leader.pos:
      logging.debug(f"{self} en {self.pos} {self.pos.cords} busca unirse a su lider {self.leader}.")
      if self.goto == []: self.move_set(self.leader.pos)

  def launch_event(self):
    pass
  def levelup(self):
    pass
  def maintenanse(self):
    # logging.debug(f"mantenimiento de {self} de {self.nation}.")
    if self.upkeep > 0 and self.nation.gold >= self.upkeep:
      self.nation.gold -= self.upkeep_total
      logging.debug(f"{self} cobra {self.upkeep_total}.")
    elif self.upkeep > 0 and self.nation.gold < self.upkeep:
      self.disband()

  def move_set(self, goto):
    logging.debug(f"move_set {self} on {self.pos} {self.pos.cords}.")
    if self.will_less:
      if self.show_info: 
        loadsound("errn1")
      return 
    self.garrison = 0
    can_fly = self.can_fly
    coldres = self.coldres
    desert_survival = self.desert_survival + 1
    forest_survival = self.forest_survival
    mountain_survival = self.mountain_survival
    mounted = self.mounted
    swamp_survival = self.swamp_survival
    if self.leads:
      for uni in self.leads: 
        if uni.can_fly == 0: can_fly = 0 
        if uni.coldres == 0: coldres = 0
        if uni.forest_survival == 0: forest_survival = 0
        if uni.mountain_survival == 0: mountain_survival = 0
        if uni.mounted == 0: mounted = 0
        if uni.swamp_survival == 0: swamp_survival = 0
    if (goto.__class__ == self.pos.__class__
        and self.can_pass(goto)):
      if can_fly: cost = goto.cost_fly
      elif can_fly == 0:
        cost = goto.cost
        if forest_survival and goto.surf.name == forest_t: cost -= 1
        elif mountain_survival and (goto.surf.name in mountain_t or goto.hill): cost -= 1
        elif swamp_survival and goto.surf.name == swamp_t: cost -= 1
        elif ((goto.surf.name in [forest_t, swamp_t] or goto.hill) and mounted):
          self.mp[0] -= 1
      if self.goto == []: self.goto.append([cost, goto])
      elif self.goto: self.goto.insert(0, [cost, goto])
      self.move_unit()
    elif isinstance(goto, str):
      self.goto += [goto]
      self.move_unit()
  
  def move_far(self): 
    logging.debug(f"{self} mueve lejos")
    goto = self.goto[0][1]
    
    pos = self.pos
    
    sq = self.pos.get_near_tiles(1)
    # logging.debug(f"{len(sq)} terrenos iniciales.")
    if goto.x > pos.x:
      # logging.debug(f"al este.")
      sq = [ti for ti in sq if ti.x > pos.x]
    if goto.x < self.pos.x:
      # logging.debug(f"al oeste.")
      sq = [ti for ti in sq if ti.x < self.pos.x]
    
    if goto.y < pos.y:
      # logging.debug(f"al norte.")
      sq = [ti for ti in sq if ti.y < pos.y]
    if goto.y > pos.y:
      # logging.debug(f"al sur.")
      sq = [ti for ti in sq if ti.y > pos.y]
    
    sq = [ti for ti in sq if ti.soil.name in self.soil and ti.surf.name in self.surf
          and ti != self.pos]
    shuffle(sq)
    sq.sort(key=lambda x: x.cost <= self.mp[1], reverse=True)
    sq.sort(key=lambda x: x.nation == self.nation, reverse=True)
    # logging.debug(f"{len(sq)} terrenos finales.")
    self.set_favland(sq)
    
    if basics.roll_dice(2) <= self.fear:
      # logging.debug(f"ordena por fear.")
      sq.sort(key=lambda x: x.threat)
      sq.sort(key=lambda x: x.around_threat)
    if sq:
      self.move_set(sq[0])
    else:
      logging.debug(f"{self} en {self.pos} {self.pos.cords}. no hay donde mover.")
      sq = self.goto[0][1].get_near_tiles(2)
      sq = [ti for ti in sq if ti.soil.name in self.soil and ti.surf.name in self.surf
          and ti != self.pos and ti in self.nation.map]
      self.move_set(choice(sq))

  def move_group(self, info=0):
    logging.info(f"move leads turn {self.pos.world.turn}.")
    if info: logging.debug(f"{self} {self.id} at {self.pos} {self.pos.cords}..")
    if info: logging.debug(f"goal {self.goal[0]} to {self.goal[1]}.")
    if info: logging.debug(f"leads {len(self.leads)} units.")
    leads = [str(i) for i in self.leads]
    if self.leads: logging.debug(f"{leads}.")
    goto = self.goto[0][1]
    goto.update(self.nation)
    
    self.pos.update(self.nation)
    ranking = self.ranking
    threat = goto.threat
    if goto.hill and mountain_survival_t not in self.traits: threat *= 1.2
    if goto.surf.name == forest_t and forest_survival_t not in self.traits: threat *= 1.2
    if goto.surf.name == swamp_t and swamp_survival_t not in self.traits: threat *= 1.2
    if info: logging.debug(f"ranking {round(ranking)} vs {round(threat)}.")
    
    alt = goto.get_near_tiles(1)
    alt = [it for it in alt
        if it.get_distance(it, self.pos) == 1]
    [it.update(self.nation) for it in alt]
    alt.sort(key=lambda x: x.income, reverse=True)
    alt.sort(key=lambda x: x.bu, reverse=True)
    alt.sort(key=lambda x: x.threat)
    if self.forest_survival: alt.sort(key=lambda x: x.surf.name == forest_t, reverse=True)
    if self.swamp_survival: alt.sort(key=lambda x: x.surf.name == swamp_t, reverse=True)
    if self.mountain_survival: alt.sort(key=lambda x: x.hill, reverse=True)
    defense_roll = 5
    if self.leadership: defense_roll -= 2
    if basics.roll_dice(1) >= defense_roll: 
      alt.sort(key=lambda x: x.hill and x.threat < ranking, reverse=True)
    
    if self.goal[0] == base_t:
      self.break_group()
      return
    if self.goal[0] == capture_t:
      if goto.threat > ranking:
        if info: logging.debug(f"mayor.")
        if basics.roll_dice(1) > 2:
          if info: logging.debug(f"wait next turn.") 
          return
        
        else:
          if info: logging.debug(f"switch goto.")
          for it in alt:
            if it.threat < ranking:
              if (self.day_night 
                  and (it.nation != self.nation and it.nation != None)
                  and basics.roll_dice(1) >= 3):
                if info: logging.debug(f"will avoid hills by night.")
                continue
              if info: logging.debug(f"changes to {it} {it.cords}.")
              self.move_set(it)
              return
        
        if basics.roll_dice(1) > 4:
          if info: logging.debug(f"{self} go home.")
          self.go_home()
          return
      self.move_set(self.goal[1])
      return
    if self.goal[0] == "settle":
      if goto.threat < self.ranking:
        self.moving_unit(goto)
        return
    if self.goal[0] == stalk_t:
      if self.ranged > 5 and self.pos.day_night and self.dark_vision == 0: 
        ranking *= 0.5
      if ranking < threat:
        if info: logging.debug(f"mayor.")
        if basics.roll_dice(2) >= 10:
          if info: logging.debug(f"ataca.")
          if goto.threat <= self.ranking * 1.25:
            if info: logging.debug(f" . {goto.threat=:} {self.ranking*1,5=:}.") 
            self.move_set_(goto)
            return
        roll = 2
        if self.pos.hill: roll += 1
        if self.pos.surf.name == forest_t: roll += 1
        if self.pos.surf.name == swamp_t: roll += 1
        if info: logging.debug(f"switch chanse {roll}.")
        if basics.roll_dice(1) >= roll:
          if info: logging.debug(f"will move.")
          for it in alt:
            if info: logging.debug(f"{it.threat=: }. {it} {it.cords}.")
            if it.threat < self.group_ranking * 0.8:
              if (self.day_night 
                  and (it.nation != self.nation and it.nation != None)
                  and basics.roll_dice(1) >= 3):
                if info: logging.debug(f"will avoid hills by night.")
                continue
              if info: logging.debug(f"moves to {it} {it.cords}.")
              self.move_set(it)
              return
          if info: logging.debug(f"espera.")
          return 
        if basics.roll_dice(1) >= 4:
          if info: logging.debug(f"espera")
          return
        self.go_home()
        return
      else:
        if info: logging.debug(f"just moves.")
        self.move_set(goto)

  def move_unit(self, info=0):
    self.update()
    if info:logging.debug(f"move_unit for {self} on {self.pos}, {self.pos.cords}.")
    goto = self.goto[0][1]
    if goto == self.pos:
      self.goto = []
      self.stopped = 1
      msg = f"{self} {self.nation}  detenido."
      # self.log[-1].append(msg)
      if info: logging.debug(msg)
      if self.show_info:
        sp.speak(msg)
      return 0
    if isinstance(self.goto[0], list):
      msg = f"{self} ({self.nation}) moves to {self.goto[0][1]}., {self.goto[0][1].cords}"
      self.log[-1].append(msg)
      if info: logging.debug(msg)
      if info: logging.debug(f"mp {self.mp[0]} de {self.mp[1]}, costo {self.goto[0][0]}.")
      if self.leads: 
        if info: logging.debug(f"lider, grupo {len(self.leads)}.")
      elif self.leader: 
        if info: logging.debug(f"following {self.leader} on {self.leader.pos} {self.leader.pos.cords}.")
      while (self.goto and self.mp[0] > 0 and self.hp_total >= 1
             and isinstance(self.goto[0], list)):
        goto = self.goto[0][1]
        if self.check_ready() == 0:
          if info: logging.debug(f"go = 0.")
          return
        square = self.pos.get_near_tiles(1)
        if goto not in square:
          self.move_far()
        
        elif goto in square:
          if self.goal and goto == self.goal[1]:
            self.move_group()
            return
          self.moving_unit(self)
    
    elif isinstance(self.goto[0], str):
      if self.goto[0] == "attack":
        del(self.goto[0])
        self.auto_attack()
        if self.hp_total < 1: return
      elif self.goto[0] == "gar":
        self.garrison = 1
        
        if info: logging.debug(f"{self} defiende {self.pos}.")
        del(self.goto[0])
      elif self.goto[0] == "join":
        basics.ai_join_units(self)
        if info: logging.debug(f"{self} joins.")
        del(self.goto[0])
      elif self.goto[0] == "set":
        self.set_settlemment()
        

  def moving_unit(self, info=0):
    if info: logging.debug(f"mueve cerca {self} {self.id}.")
    if self.goto == []: 
      if info: logging.debug(f"sin goto.")
      return
    if isinstance(self.goto[0][0], str):
      if info: logging.debug(f"goto es str.")
      self.goto = []
      return
    mp = min(i.mp[0] for i in self.leads + [self])
    cost = self.goto[0][0]
    goto = self.goto[0][1]
    if info: logging.debug(f"mp {mp}, cost {cost}.")
    # menor.
    if mp < cost:
      if info: logging.debug(f"menor.")
      self.goto[0][0] -= self.mp[0]
      self.mp[0] = 0
      for uni in self.leads: uni.mp[0] = 0
      if self.ai == 0: loadsound("set4")
    # mayor
    elif mp >= cost:
      if info: logging.debug(f"mayor.")
      self.mp[0] -= cost
      for uni in self.leads: uni.mp[0] -= cost
      self.garrison = 0
      [uni.set_hidden(goto) for uni in self.leads + [self]]
      if info: logging.debug(f"hidden {self.hidden}.")
      if self not in self.pos.units: 
        if info: logging.debug(f"not in position.")
      # chekeo de enemigos.
      if self.check_enemy(goto, goto.is_city):
        if info: logging.debug(f"hay enemigos.")
        veredict = self.combat_pre(goto)
        self.update()
        if info: logging.debug(f"hidden {self.hidden}.")
        if veredict == 0:
          # self.pos.update(self.nation)
          if info: logging.debug(f"veredict {veredict}.")
          return
        
        if self.check_enemy(goto, goto.is_city):
          if info: logging.debug(f"still enemies.")
          del(self.goto[0])
          return
      [uni.unit_arrival(goto) for uni in self.leads + [self]]

  def oportunist_attack(self, info=1):
    if self.hp_total < 1: return
    if self.check_ready() == 0: return
    logging.info(f"oportunist_attack for {self}.")
    sq = self.pos.get_near_tiles(1)
    [i.update(self.nation) for i in sq]
    sq = [it for it in sq if self.can_pass(it)
              and it.threat > 0]
    if info: logging.debug(f"{len(sq)} casillas.")
    for s in sq:
      if basics.roll_dice(2) >= 8 and self.get_favland(s) == 0:
        if info: logging.debug(f"not favland.")
        continue
      ranking = self.ranking
      if info: logging.debug(f"{ranking=:}.")
      if self.leadership and self.leading == 0: ranking *= 0.6
      if s.surf.name == forest_t and self.forest_survival == 0: 
        ranking -= ranking * 0.2
        if info: logging.debug(f"reduce by forest.")
      if s.surf.name == swamp_t and self.swamp_survival == 0: 
        ranking -= ranking * 0.2
        if info: logging.debug(f"reduce by swamp.")
      if s.hill and self.mountain_survival == 0: 
        ranking -= ranking * 0.2
        if info: logging.debug(f"reduce by mountain.")
      rnd = randint(round(ranking * 0.9), round(ranking * 1.2))
      if self.nation not in self.pos.world.nations: 
        rnd *= 1.5
        if info: logging.debug(f"rnd increased by random unit.")
      if info: logging.debug(f"{rnd=:}, {s.threat=:}, {s.around_threat=:}")
      fear = self.get_fear()
      if info: logging.debug(f"{rnd*fear=:}, {s.around_threat=:}.")
      if rnd * fear < s.around_threat:
        if info: logging.debug(f"afraid.")
        continue
      if rnd > s.threat and s.cost <= self.mp[0]:
        msg = f"{self} en {self.pos} aprobecha y ataqua a {s}."
        if info: logging.debug(msg)
        self.log[-1].append(msg)
        self.move_set(s)
        self.move_set("attack")
        return 1

  def raid(self, cost=0):
    if (self.pos.city and self.pos.nation != self.nation and self.can_raid 
        and self.mp[0] >= cost): 
      self.mp[0] -= cost
      self.update()
      self.pos.update()
      if self.pos.raided < self.pos.income:
        logging.info(f"{self} saquea a {self.pos.city} {self.pos.nation} en {self.pos} {self.pos.cords}")
        self.set_hidden(self.pos)
        raided = self.hp_total * 2
        if self.mounted: raided *= 2
        if raided > self.pos.income: raided = self.pos.income
        self.pos.raided = raided
        self.pos.city.raid_outcome += raided
        self.nation.raid_income += raided
        self.history.raids += raided
        msg = f"{self} {raids_t} {raided} {gold_t} {in_t} {self.pos} {self.pos.cords}, {self.pos.city}."
        self.pos.nation.log[-1].append(msg)
        self.log[-1].append(msg)
        self.nation.log[-1].append(msg)
        if any(i for i in [self.pos.nation.show_info, self.show_info]) and raided: 
          sleep(loadsound("spell34", channel=CHTE3))
      if self.pos.pop:
        logging.debug(f"{self.pop=:}.")
        pop = self.pos.pop
        deads = self.weapon1.damage
        if self.weapon2: deads += self.weapon2.damage
        if self.weapon3: deads += self.weapon3.damage
        logging.debug(f"initial dead {deads}.")
        deads *= randint(1, self.att1 + self.att1_mod + 1)
        if self.mounted: deads *= 2 
        logging.debug(f"second dead {deads}.")
        defense = sum([i.units for i in self.pos.units if i.nation == self.pos.nation])
        if defense: deads -= defense * 0.5
        logging.debug(f"end dead {deads}.")
        if deads < 0: deads = 0
        if deads > pop: deads = pop
        deads = int(deads)
        self.pos.pop -= deads
        self.pos.add_corpses(choice(self.pos.nation.population_type), deads)
        # corpses = choice(self.pos.nation.population_type)
        # corpses.deads = [deads]
        # corpses.units = 0
        # corpses.hp_total = 0
        # self.pos.units += [corpses]
        if self.pos.pop: self.pos.unrest += randint(deads, deads * 2)
        if deads >= 50 * pop / 100:
          msg = f"masacre!."
          self.log[-1].append(msg)
          self.nation.log[-1].append(msg)
          self.pos.nation.log[-1].append(msg)
          sq = self.pos.get_near_tiles(1)
          sq = [s for s in sq if s.nation == self.pos.nation]
          for s in sq: s.unrest += randint(15, 30)
          if any(i for i in [self.pos.nation.show_info, self.show_info]): 
            sleep(loadsound("spell33", channel=CHTE3) * 0.2)
        if deads:
          msg = f"{deads} población perdida."
          self.pos.nation.log[-1].append(msg)
          self.log[-1].append(msg)
          self.nation.log[-1].append(msg)
          if any(i for i in [self.show_info, self.pos.nation.show_info]): 
            sleep(loadsound("spell36", channel=CHTE3) // 2)
      logging.info(f"raid_income {round(self.pos.nation.raid_income)}.")      
      self.pos.city.update()

  def random_move(self, sq=None, value=1, info=1):
    logging.debug(f"movimiento aleatoreo para {self} en {self.pos}, {self.pos.cords}.")
    done = 0
    if sq == None:
      sq = self.pos.get_near_tiles(value)
      sq = [it for it in sq if self.can_pass(it)]
      if info: logging.debug(f"{len(sq)} casillas iniciales.")
    if sq:
      if self.city and self.nation in self.pos.world.random_nations: sq = [it for it in sq if it.get_distance(it, self.city.pos) <= self.mp[1]]
      if info: logging.debug(f"{len(sq)= }.")
      done = 1
      fear = 0
      move = 1
      sort = 0
      shuffle(sq)
      if sq == []: 
        self.move_set(self.city.pos)
        return
      self.pos.map_update(self.nation, sq)
      if randint(1, 100) < self.sort_chance:
        if info: logging.debug(f"sorted.")
        sort = 1
        [s.set_threat(self.nation) for s in sq]
        if self.populated_land:
          if info: logging.debug(f"casillas pobladas.")
          sq.sort(key=lambda x: x.pop, reverse=True)
        self.set_favland(sq)
      
      if info: logging.debug(f"{self.ranking=:}.")
      rnd = randint(round(self.ranking * 0.9), round(self.ranking * 1.3))
      if self.pos.surf.name == forest_t and self.forest_survival == 0: rnd -= rnd * 0.3
      if self.pos.hill and self.mountain_survival == 0: rnd -= rnd * 0.3
      if self.pos.surf.name == swamp_t and self.swamp_survival == 0: rnd -= rnd * 0.3
      if self.leadership: rnd -= rnd * 0.3
      if self.nation not in self.pos.world.nations: rnd *= 1.5
      if basics.roll_dice(1) <= self.fear:
        if info: logging.debug(f"ordena por miedo")
        fear = 1
        # sq.sort(key=lambda x: x.city == None, reverse=True)
        sq.sort(key=lambda x: x.threat <= rnd, reverse=True)
        sq.sort(key=lambda x: x.around_threat <= rnd, reverse=True)
        if basics.roll_dice(1) >= 3: sq.sort(key=lambda x: x.food - x.food_need < self.food)
        sq.sort(key=lambda x: x.defense, reverse=True)
      if self.scout:
        if info: logging.debug(f"ordena para exploración")
        fear = 1
        sq.sort(key=lambda x: x.has_city)
        if self.can_fly: sq.sort(key=lambda x: x.hill, reverse=True)
        if self.forest_survival: sq.sort(key=lambda x: x.surf.name == forest_t, reverse=True)
        elif self.swamp_survival: sq.sort(key=lambda x: x.surf.name == swamp_t, reverse=True)
        elif self.mountain_survival: sq.sort(key=lambda x: x.hill, reverse=True)
        if basics.roll_dice(1) >= 6: sq.sort(key=lambda x: x.hill, reverse=True)
        sq.sort(key=lambda x: x.get_distance(x, self.city.pos), reverse=True)
      
      # casillas finales.
      sq.sort(key=lambda x: x != self.pos, reverse=True)
      movstatus = f"fear {fear}, sort {sort}."
      self.log[-1].append(movstatus)
      if info: logging.debug(f"{len(sq)} casillas finales.")
      moved = 0
      for s in sq:
        if self.fear in [6, 5]: fear = 1.5
        if self.fear in [4, 3]: fear = 2
        if self.fear in [2, 1]: fear = 3
        if info: logging.debug(f"{rnd*fear=:} {s.around_threat=:}.")
        if rnd * fear < s.around_threat and self.fear >= 5: 
          if info: logging.debug(f"afraid.")
          continue
        if info: logging.debug(f"rnd {rnd} amenaza {round(s.threat)} in {s}, {s.cords}.")
        if rnd >= s.threat:
          moved = 1
          self.move_set(s)
          break
      if moved == 0:
        msg = f"no se mueve.!"
        if info: logging.debug(msg)
        self.log[-1].append(msg)
        self.stopped = 1
    return done

  def restoring(self, info=0):
    logging.debug(f"restaura {self} id {self.id}.")
    if self.hp_total < 1:
      logging.warning(f"sin salud.")
      return
    self.history.turns += 1
    self.stopped = 0
    self.revealed = 0
  
    # hp.
    if self.hp_total < self.hp * self.units:
      res = self.hp_res + self.hp_res_mod
      self.hp_total += res
      if self.hp_total > self.hp * self.units: self.hp_total = self.hp * self.hp * self.units
      if info: logging.debug(f"restaura {res} hp.")
      if self.hp_total > self.hp * self.units: self.hp_total = self.hp * self.units
  
    # Refit
    if self.pos.nation in self.belongs and self.sts + self.sts_mod:
        if self.pos.food_need <= self.pos.food:
          if self.units < self.min_units * self.squads:
            squads = self.squads
            units = self.units
            self.hp_total += self.hp * (self.sts + self.sts_mod)
            self.update()
            if self.squads > squads:
              self.hp_total = self.hp * (self.min_units*squads) 
            units = self.units - units
            msg = f"recovers {units}."
            self.log[-1] += {msg}
            if info: logging.debug(msg)
            reduction = round((self.sts + self.sts_mod) * self.pop)
            self.pos.city.reduce_pop(reduction)
    
    # mp.
    self.mp[0] = self.mp[1]
    if info: logging.debug(f"mp {self.mp}.")
  
    # poder.
    power_res = self.power_res + self.power_res_mod
    self.power += power_res
    if self.power > self.power_max: self.power = self.power_max
  
    # skills.
    for sk in self.skills:
      if sk.type == "start turn":
        try:
          sk.run(self)
        except: Pdb().set_trace()
      if sk.turns > 0:sk.turns -= 1
    self.global_skills = [sk for sk in self.global_skills if sk.turns == -1 or sk.turns > 0]
    self.offensive_skills = [sk for sk in self.offensive_skills if sk.turns == -1 or sk.turns > 0]
    self.other_skills = [sk for sk in self.other_skills if sk.turns == -1 or sk.turns > 0]
    self.terrain_skills = [sk for sk in self.terrain_skills if sk.turns == -1 or sk.turns > 0]

  def set_army(self, nation, view_mode=0, sound="in1"):
    logging.info(f"set_leads for {self}")
    if view_mode == 0:sp.speak(f"set army")
    elif view_mode:sp.speak(f"view army")
    sleep(loadsound(sound))
    self.update()
    items = self.squads_position
    items = [uni for uni in items 
             if nation in uni.belongs or uni.revealed]
    say = 1 
    x = 0
    while True:
      sleep(0.001)
      if say:
        sp.speak(f"{items[x]}.", 1)
        say = 0
      
      for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_UP:
            x = basics.selector(items, x, go="up")
            say = 1
          if event.key == pygame.K_DOWN:
            x = basics.selector(items, x, go="down")
            say = 1
          if event.key == pygame.K_HOME:
            x = 0
            say = 1
            loadsound("s1")
          if event.key == pygame.K_END:
            x = len(items[x]) - 1
            say = 1
            loadsound("s1")
          if event.key == pygame.K_i:
            items[x].info(self.nation)
          if event.key == pygame.K_PAGEUP:
            if nation not in self.belongs: 
              loadsound("errn1")
              continue
            unit = items[x]
            index = items.index(unit)
            say = 1  
            if index == 0: loadsound("errn1")
            else:
              sp.speak(f"{unit} moved up.")
              items.remove(unit)
              items.insert(index - 1, unit)
              x -= 1
          if event.key == pygame.K_PAGEDOWN:
            if nation not in self.belongs: 
              loadsound("errn1")
              continue
            unit = items[x]
            index = items.index(unit)
            say = 1  
            if index == len(items) - 1: loadsound("errn1")
            else:
              sp.speak(f"{unit} moved down.")
              items.remove(unit)
              items.insert(index + 1, unit)
              x += 1
          if event.key == pygame.K_ESCAPE:
            self.squads_position = items
            return sleep(loadsound("back1") / 2)

  def set_army_auto(self, layout="defensive1"):
    """layouts: defensive1, settle."""
    logging.info(f"set_army_auto for {self}.")
    self.squads_position = self.leads + [self]
    if layout == "defensive1":
      if self.info: logging.debug(f"layout {layout}.")
      self.squads_position.sort(key=lambda x: x.levy, reverse=True)
      self.squads_position.sort(key=lambda x: x.ranged, reverse=True)
      self.squads_position.sort(key=lambda x: x.leadership)
      self.squads_position.sort(key=lambda x: x.settler)
      
      

  def set_attack(self):
    if self.mp[0] < 0: return
    logging.debug(f"ataque hidden.")
    if self.pos == None: Pdb().set_trace()
    enemies = [i for i in self.pos.units
               if i.nation not in self.belongs and i.hidden == 0]
    if enemies:
      weakest = basics.roll_dice(1)
      if self.hidden: weakest += 2
      if weakest >= 5: enemies.sort(key=lambda x: x.ranking)
      return enemies[0]

  def set_auto_explore(self):
      if self.scout == 0:
        self.scout = 1
        self.ai = 1
        msg = f"exploración automática activada."
        sp.speak(msg)         
        logging.debug(msg)
        loadsound("s2")
      elif self.scout == 1:
        self.scout = 0
        self.ai = 0
        msg = f"exploración automática desactivada."
        sp.speak(msg)         
        logging.debug(msg)
        loadsound("s2")

  def set_auto_leads(self):
    pass

  def set_default_align(self):
    if self.pos:
      for nt in self.pos.world.random_nations: 
        if nt.name == self.aligment: self.nation = nt

  def set_favland(self, sq):
    shuffle(sq)
    sq.sort(key=lambda x: self.get_favland(x), reverse=True)
    if self.pref_corpses: sq.sort(key=lambda x: len(x.corpses), reverse=True)

  def set_hidden(self, pos, info=0):
    logging.info(f"set hidden {self} a {pos} {pos.cords}.")
    visible = self.size * self.units
    if info: logging.debug(f"visible {visible}")
    if self.nation != pos.nation: 
      visible += pos.pop
      if info: logging.debug(f"visible {visible} pop")
    visible += sum([it.units * it.sight for it in pos.units if it.nation not in self.belongs])
    if info: logging.debug(f"visible {visible} units")
    visible = floor(visible / 200)
    if visible > 7: visible = 7
    if info: logging.debug(f"visible {visible} rond 20")
    stealth = self.stealth + self.stealth_mod
    if info: logging.debug(f"stealth {stealth}")
    stealth -= visible
    roll = basics.roll_dice(2)
    if info: logging.debug(f"roll {roll}. stealth {stealth}.")
    if roll >= stealth or roll == 12: 
      self.revealed = 1
      self.update()
      if info: logging.debug(f"revelado.")
    self.revealed_val = stealth, visible 

  def set_hire(self, target):
    logging.info(f"{self} hire {self.pos.world.turn=:}.")
    cost = target.gold * self.hire_rate
    if self.nation.gold < cost:
      msg = f"not enought gold", 1
      logging.debug(msg)
      if self.show_info:
        sp.speak(msg)
        sleep(loadsound("errn1")) 
      return 
    if self.nation.gold >= cost:
      self.nation.gold -= cost
      target.belongs = [self.nation]
      target.pos = self.pos
      target.hired = 1
      msg = f"{self} has hired {target} by {cost}."
      if self.show_info: sp.speak(msg)
      self.log[-1] += [msg]
      logging.debug(msg)
      sleep(loadsound("gold1"))
      self.nation.update(self.nation.map)
      self.pos.units += [target]
      return 1

  def set_id(self):
    num = self.id
    # logging.debug(f"id base {self} {num}.")
    self.nation.units.sort(key=lambda x: x.id)
    for i in self.nation.units:
      # logging.debug(f"{i} id {i.id}.")
      if i.id == num: num += 1
    self.id = num

    # logging.debug(f"id final {self.id}.")
  def set_leads(self, sound="in1"):
    sleep(loadsound(sound))
    logging.info(f"set_leads for {self}")
    self.update()
    av_units = self.set_lead_traits(self.pos.units)
    t = 0
    say = 1
    x = 0
    while True:
      sleep(0.001)
      if say:
        items = [self.leads, av_units]
        if items[t] == []: sp.speak(f"{empty_t}.")
        else:
          sp.speak(items[t][x].basic_info())
        say = 0
      
      for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_UP:
            x = basics.selector(items[t], x, go="up")
            say = 1
          if event.key == pygame.K_DOWN:
            x = basics.selector(items[t], x, go="down")
            say = 1
          if event.key == pygame.K_HOME:
            x = 0
            say = 1
            loadsound("s1")
          if event.key == pygame.K_END:
            x = len(items[t]) - 1
            say = 1
            loadsound("s1")
          if event.key == pygame.K_PAGEUP:
            x -= 10
            say = 1
            if x < 0: x = 0
            loadsound("s1")
          if event.key == pygame.K_PAGEDOWN:
            x += 10
            say = 1
            if x >= len(items[t]): x = len(items[t]) - 1
            loadsound("s1")
          if event.key == pygame.K_F1:
            sp.speak(f"{self.leading} {of_t} {self.leadership}.", 1)
          if event.key == pygame.K_i:
            if items[t]: items[t][x].info(self.nation)
          if event.key == pygame.K_p:
            self.set_army(self.nation)
            say = 1
          if event.key == pygame.K_RETURN:
            if items[t] == []: 
              loadsound("errn1")
              continue
            unit = items[t][x]
            say = 1  
            if unit in av_units:
              if unit.units + self.leading > self.leadership:
                sp.speak(f"not enought leadership.",1)
                loadsound("errn2")
                continue
              sp.speak(f"{added_t}.", 1)
              sleep(loadsound("selected1") / 2)
              unit.leader = self
              self.leads += [unit]
              av_units.remove(unit)
              self.squads_position.insert(0, unit)
            elif unit in self.leads:
              sp.speak(f"{removed_t}.", 1)
              sleep(loadsound("set4") / 2)
              unit.leader = None
              av_units += [unit]
              self.leads.remove(unit)
              self.squads_position.remove(unit)
            if x >= len(items[t]): x -= 1
            self.update()
          if event.key == pygame.K_TAB:
            say = 1
            if t == 0:
              t = 1
              x = 0
              sp.speak(f"{units_t} {in_t} {self.pos}.")
            elif t == 1: 
              t = 0
              x = 0
              sp.speak(f"{units_t} {in_t} {self} leads.")
          if event.key == pygame.K_ESCAPE:
            return sleep(loadsound("back1") / 2)

  def set_lead_disband(self, info=1):
    logging.debug(f"set_lead_disband for {self}.")
    leadership = self.leadership
    threats = [self.pos.around_threat]
    if self.pos.city and self.pos.nation in self.belongs:
      threats += [self.pos.city.seen_threat] 
    threat = max(threats)
    if threat < self.pos.defense * 0.5 and self.goal == None: 
      leadership *= 0.8
    if info:
      msg = f"lead disband: {threat=:}, {self.pos.defense=:}."
      logging.debug(msg)
      self.log[-1] += [msg]
    if self.leading > leadership:
      units = [it for it in self.leads if it.squads > 1 
               and it.goto == [] and it.settler == 0]
      while units and self.leading - 10 > leadership:
        shuffle(self.leads)
        units.sort(key=lambda x: x.ranking)
        unit = units[0]
        msg = f"splits {unit}."
        unit.split()
        self.update()
        units = [it for it in self.leads if it.squads > 1 
               and it.goto == []]
        if info:
          msg2 = f"{self} {self.leadership=:}, {self.leading=:}."
          logging.debug(msg)
          logging.debug(msg2)
          self.log[-1] += [msg, msg2]

  def set_lead_traits(self, units):
    for it in units: it._go = 1
    for it in units:
      if it.leadership or it.leader: it._go = 0
      if it.nation not in self.belongs: it._go = 0
      for tr in it.traits:
        if tr not in self.lead_traits: it._go = 0
      if it.aligment not in self.lead_aligments: it._go = 0
    units = [it for it in units if it._go]
    return units 
  
  def set_level(self):
    level = self.level
    for i in self.exp_tree:
      if self.exp <= i:
        self.level = self.exp_tree.index(i)
        break
    
    if self.level > level: self.level_up()

  def set_name(self):
    if self.namelist == None: return
    while True:
      for i in self.namelist:
        if i != self.namelist[0]: self.nick += " "
        self.nick += choice(i)
      if basics.has_name(self.nation.units, self.nick) == None: return
      else: self.nick = str()

  def set_ranking(self):
    self.ranking_off = 0
    self.ranking_off_l = []
    
    # Offensive. 
    self.ranking_off = self.weapon1.damage
    self.ranking_off_l += [f"{self.weapon1}", self.weapon1.damage, self.ranking_off]
    self.ranking_off *= self.att1
    self.ranking_off_l += ["att1", self.att1, self.ranking_off]
    if self.weapon2:
      self.ranking_off += self.weapon2.damage
      self.ranking_off_l += [f"{self.weapon2}", self.weapon2.damage, self.ranking_off]
      self.ranking_off *= self.att2
      self.ranking_off_l += ["att2", self.att1, self.ranking_off]
    if self.weapon3:
      self.ranking_off = self.weapon3.damage
      self.ranking_off_l += [f"{self.weapon3}", self.weapon3.damage, self.ranking_off]
      self.ranking_off *= self.att3
      self.ranking_off_l += ["att3", self.att1, self.ranking_off]
    self.ranking_off *= self.units
    self.ranking_off_l += ["units", self.ranking_off]
    self.ranking_off *= 1 + (self.off + self.off_mod) / 10
    # if self.off + self.off_mod >= 14: self.ranking_off *= 2.5 + (self.off + self.off_mod) / 10    
    # elif self.off + self.off_mod >= 12: self.ranking_off *= 2 + (self.off + self.off_mod) / 10
    # elif self.off + self.off_mod >= 10: self.ranking_off *= 1.5 + (self.off + self.off_mod) / 10
    # else: self.ranking_off *= 1 + (self.off + self.off_mod) / 20
    self.ranking_off_l += ["off", self.ranking_off]
    self.ranking_off *= 1 + (self.strn + self.strn_mod) / 10
    # if self.strn + self.strn_mod >= 14: self.ranking_off *= 2.5 + (self.strn+ self.strn_mod) / 10    
    # elif self.strn+ self.strn_mod >= 12: self.ranking_off *= 2 + (self.strn+ self.strn_mod) / 10
    # elif self.strn+ self.strn_mod >= 10: self.ranking_off *= 1.5 + (self.strn+ self.strn_mod) / 10
    # else: self.ranking_off *= 1 + (self.strn+ self.strn_mod) / 20
    self.ranking_off_l += ["strn", self.ranking_off]
    self.ranking_off *= 1 + (self.moves + self.moves_mod) / 10
    self.ranking_off = round(self.ranking_off / 8)
    self.ranking_off_l += ["moves", self.ranking_off]
    
    # Defensive.
    self.ranking_dfs = self.hp_total // 2
    self.ranking_dfs_l = ["hp", self.ranking_dfs]
    if self.dfs + self.dfs_mod >= 14: self.ranking_dfs *= 2.5 + (self.dfs + self.dfs_mod) / 10
    elif self.dfs + self.dfs_mod >= 12: self.ranking_dfs *= 2 + (self.dfs + self.dfs_mod) / 10
    elif self.dfs + self.dfs_mod >= 10: self.ranking_dfs *= 1.5 + (self.dfs + self.dfs_mod) / 10
    else: self.ranking_dfs *= 1 + (self.dfs + self.dfs_mod) / 10
    self.ranking_dfs_l += ["dfs", self.ranking_dfs]
    if self.res + self.res_mod >= 10: self.ranking_dfs *= 1 + (self.res + self.res_mod) / 10
    elif self.res + self.res_mod < 10: self.ranking_dfs *= 1 + (self.res + self.res_mod) / 20
    self.ranking_dfs_l += ["res", self.ranking_dfs]
    self.ranking_dfs *= 1 + (self.hres + self.hres_mod) / 10
    self.ranking_dfs_l += ["h res", self.ranking_dfs]
    if self.arm + self.arm_mod >= 8: self.ranking_dfs *= 3 + (self.arm + self.arm_mod) / 10
    elif self.arm + self.arm_mod >= 6: self.ranking_dfs *= 2.5 + (self.arm + self.arm_mod) / 10
    elif self.arm + self.arm_mod >= 4: self.ranking_dfs *= 2 + (self.arm + self.arm_mod) / 10
    else: self.ranking_dfs *= 1 + (self.arm + self.arm_mod) / 10
    self.ranking_dfs_l += ["arm", self.ranking_dfs]
    if self.armor: 
      if self.armor.arm >= 4: self.ranking_dfs *= 1.5 + (self.armor.arm / 10)
      else: self.ranking_dfs *= 1 + (self.armor.arm / 10)
      self.ranking_dfs_l += ["armor", self.ranking_dfs]
    if self.shield: 
      self.ranking_dfs *= 1 + (self.shield.dfs) / 10
      self.ranking_dfs_l += ["shield", self.ranking_dfs]
    self.ranking_dfs = round(self.ranking_dfs / 150)

    self.ranking = self.ranking_dfs + self.ranking_off
  
    if self.can_fly: self.ranking *= 1.5
    if self.resolve + self.resolve_mod >= 6: self.ranking *= 1.3
    if self.size >= 3: self.ranking *= 1.25
    elif self.size >= 4: self.ranking *= 1.5
    elif self.size >= 5: self.ranking *= 2
    elif self.size >= 6: self.ranking *= 3
    if self.ranged: self.ranking *= 1 + (self.range[1]) / 20
    if self.ranged == 0: self.ranking += round(self.ln + self.ln_mod / 2)
    if self.hidden: self.ranking *= 1.4
    if self.hit_rolls + self.hit_rolls_mod >= 2: self.ranking *= 1.4 
    for sk in self.skills:
      self.ranking *= sk.passive_ranking
    self.ranking = round(self.ranking)
    
    # if self.lead.
    if self.leads: 
      self.ranking += sum(i.ranking for i in self.leads) * 0.8

  def set_settlemment(self):
    placement = choice(self.buildings)
    if placement(self.nation, self.pos).check_tile_req(self.pos):
      self.nation.add_city(placement, self)
      return 1
    else: 
      logging.debug(f"{self} no puede fundar aldea en {self.pos}.")
  def set_skills(self, info=0):
    if info: logging.debug(f"get skills {self}")
    self.arm_mod = 0
    self.armor_ign_mod = 0
    self.att1_mod = 0
    self.att2_mod = 0
    self.att3_mod = 0
    self.dfs_mod = 0
    self.hit_rolls_mod = 0
    self.hp_res_mod = 0
    self.hres_mod = 0
    self.hp_mod = 0
    self.ln_mod = 0
    self.luck_mod = 0
    self.moves_mod = 0
    self.off_mod = 0
    self.power_mod = 0
    self.power_max_mod = 0
    self.power_res_mod = 0
    self.ranking_skills = 0
    self.res_mod = 0
    self.resolve_mod = 0
    self.size_mod = 0
    self.stealth_mod = 0
    self.strn_mod = 0
    self.sts_mod = 0

    self.skill_names = []
    self.effects = []
    if self.hidden: self.effects += {hidden_t}
    if self.settler == 1: self.skill_names.append(f" {settler_t}.")
    if self.charges and self.can_charge: self.effects += {charge_t} 
    
    skills = [it for it in self.skills]
    [self.skill_names.append(i.name) for i in self.skills]
    if self.pos: self.pos.set_skills()
    tile_skills = []
    if self.pos:
      if self.attacking == 0: tile_skills += [sk for sk in self.pos.terrain_events + self.pos.skills + self.pos.events ]
      elif self.attacking: tile_skills += [sk for sk in self.target.pos.terrain_events + self.pos.skills + self.pos.events]
    if self.leader:
      skills += [sk for sk in self.leader.skills 
                       if sk.effect == "leading"]
      
    if info: logging.debug(f"{len(tile_skills)} de casillas.")
    for i in tile_skills:
      if i.type == "generic":
        if info: logging.debug(f"{i.name} added.")
        skills.append(i)
    
    if self.target: skills += [s for s in self.target.skills if s.effect == "enemy"]    
    if info: logging.debug(f"run")
    for sk in skills:
      if info: logging.debug(sk.name)
      if sk.type == "generic":
        sk.run(self)
    
    self.skill_names.sort()

  def set_squads(self, value):
    self.hp_total = self.hp * (self.min_units * value)
    self.update()

  def set_tags(self):
    self.tags = []
    if self.poisonres: self.tags += [poisonres_t]
    if self.wizard: self.tags += [wizard_t]
    if self.leadership: self.tags += [commander_t]

  def set_tile_attr(self, info=0):
    tiles = self.pos.get_near_tiles(1)
    tiles = [t for t in tiles if t.nation 
           and t.nation not in self.belongs and t.pop]
    if info and tiles: print(f"set_tile_attr {self} en {self.pos} {self.pos.cords}")
    for t in tiles:
      unrest = self.pos.defense * 0.15
      if info: logging.debug(f"unrest {unrest= }.")
      unrest -= t.defense * 0.15
      if t.defense: unrest -= t.around_defense * 0.2
      if info: logging.debug(f"after defense {unrest= }.")
      if unrest < 0: unrest = 0
      if info: logging.debug(f"unrest {unrest}")
      if t == self.pos: unrest *= 2
      if info: logging.debug(f"same pos {unrest}")
      if info: logging.debug(f"unrest final {unrest}")
      if unrest < 0: unrest = 0
      t.unrest += unrest
  
  def split(self, times=1):
    if self.squads <= 1 or self.goto: return self
    logging.info(f"divide {self}.")
    units = []
    for i in range(times):
      self.update()
      logging.debug(f"{self} hp {self.hp_total} units {self.units} mínimo {self.min_units}.")
      if self.units <= self.min_units:
        logging.debug(f"mínimo alcansado.")
        return
  
      unit = self.__class__(self.nation)
      unit.hp_total = unit.min_units * unit.hp
      unit.update()
      unit.pop = unit.units * 100 / self.units
      unit.pop = int(ceil(unit.pop * self.pop / 100))
      self.hp_total -= self.min_units * self.hp
      self.pop -= unit.pop
      unit.name = self.name
      unit.city = self.city
      unit.demon_souls = self.demon_souls
      unit.garrison = self.garrison
      unit.level = self.level
      unit.mp = [self.mp[0], self.mp[1]]
      unit.pos = self.pos
      unit.revealed = self.revealed
      unit.global_skills = self.global_skills
      unit.offensive_skills = self.offensive_skills
      unit.other_skills = self.other_skills
      self.update()
      unit.update()
      unit.log = [[f"{turn_t} {self.pos.world.turn}."]]
      msg = f"{unit} detached from {self}."
      unit.log[-1] += [msg]
      self.log[-1] += [msg]
      self.pos.units.append(unit)
      if self.show_info: sp.speak(f"{self}.")
      units += [unit]
    if len(units) > 1: self.join_units(units)
    return units[0]

  def start_turn(self):
    self.xp += randint(0,1)
    self.update()
    self.log += [[f"{turn_t} {self.pos.world.turn}."]]
    self.burn()
    self.raid()

  def stats_battle(self):
    target = self.target.__class__(self.target.nation)
    kills_record = target.ranking / target.units
    kills_record *= sum(self.target.deads)
    self.history.kills_record += kills_record

  def take_city(self):
    logging.debug(f"{self} takes city {self.pos}.")
    msg = f"{self} {self.nation} toma ciudad de {self.pos.city}."
    self.nation.log[-1].append(msg)
    self.pos.nation.log[-1].append(msg)
    logging.info(msg)
    city = self.nation.av_cities[0](self.nation, self.pos)
    # city.set_name()
    city.name = self.pos.city.name
    city.tiles = self.pos.city.tiles
    self.pos.city.nation.cities.remove(self.pos.city)
    self.pos.buildings.remove(self.pos.city)
    for tl in self.pos.city.tiles:
      tl.nation = self.nation
      tl.city = city
      tl.pop -= randint(20, 40) * t.pop // 100
      tl.unrest += randint(40, 80)
      for b in tl.buildings:
        if b.name in [bu.name for bu in self.nation.av_cities]: 
          b.nation = self.nation
    self.pos.city = city
    self.pos.buildings += [city]
    city.update()
    self.nation.cities.append(self.pos.city)
    self.nation.update(self.nation.map)
  
  def unit_arrival(self, goto, info=0):
    if info: logging.info(f"unit_arrival for {self}.")
    if self.hp_total < 1:
      logging.warning(f"arrival. {self} no tiene salud.")
      return
    
    try:
      self.pos.units.remove(self)
    except: 
      logging.warning(f"{self} not in {self.pos}, {self.pos.cords}.") 
    goto.units.append(self)
    self.pos = goto
    if self.goto:del(self.goto[0])
    self.can_retreat = 1
    self.going = 0
    msg = f"{self} llega a ({goto}, {goto.cords}."
    if info: logging.debug(msg)
    self.log[-1].append(msg)
    if self.show_info and self.goto == [] and self.scout == 0: sleep(loadsound("walk_ft1") / 5)
    if self.show_info: goto.pos_sight(self.nation, self.nation.map)
    self.pos.update(self.nation)
    self.check_position()
    self.set_tile_attr()
    self.burn()
    self.raid()
    self.xp += randint(0, 1)
    [b.set_hidden(self.nation) for b in self.pos.buildings if b.type == building_t]
    [i.set_hidden(self.pos) for i in self.pos.units 
     if self.nation not in i.belongs and i.hidden]

  def unit_new_turn(self):
    logging.info(f"new turn {self.pos.world.turn=:} {to_t} {self} {in_t} {self.pos.cords}.")
    # init = time()
    if self.hp_total < 1: return
    self.start_turn()
    self.restoring()
    self.set_hidden(self.pos)
    self.join_group()
    if self.goto: 
      self.move_unit(self)
    self.attrition()
    self.maintenanse()
    # print(f"{time()-init}")

  def update(self):
    if self.pos: self.day_night = self.pos.day_night
    self.month = self.ambient.smonth
    self.season = self.ambient.sseason[0]
    self.time = self.ambient.stime[0]
    self.week = self.ambient.week
    self.year = self.ambient.year
    
    self.goto_pos = []
    for i in self.goto: self.goto_pos.append(i[1])
    if self.id == 0: self.set_id()
    if self.city == None:
      if self.nation and self.nation.cities: self.city = choice(self.nation.cities)
      
    # si pos.
    if self.pos:
      if self.log == []: self.log.append([f"{turn_t} {self.pos.world.turn}."])
      if self.pos.nation != self.nation and self.pos.nation != None and self.pos not in self.tiles_hostile:
        self.tiles_hostile.append(self.pos)
        # logging.debug(f"hostiles explorados {len(self.tiles_hostile)}.")
    
    # atributos.
    self.ranged = 0
    try:
      self.units = ceil(self.hp_total / self.hp)
    except: Pdb().set_trace()
    if self.hp_total > self.units * self.hp: self.hp_total = self.units_self.hp
    if self.units < 0: self.units = 0
    if self.power < 0: self.power = 0
    if self.mp[0] < 0: self.mp[0] = 0
    self.total_pop = self.pop * self.units
    self.upkeep_total = self.upkeep * self.units
    if death_t in self.traits: 
      self.can_recall = 0
      self.pop = 0
    if self.can_hide: self.hidden = 1
    if self.can_charge and self.target == None: self.charges = 1
    if self.revealed: self.hidden = 0
    if self.hp_total > 0: self.squads = ceil(self.units / self.min_units)
    if self.squads > self.max_squads:
      self.hp_total = (self.min_units * self.max_squads) * self.hp
    self.food_total = self.food * self.units + sum(i.food * i.units for i in self.leads)
    self.spells_tags = []
    for sp in self.spells: self.spells_tags += sp.tags
    if self.leader and self.leader.hp_total < 1: self.leader = None
    self.show_info = self.nation.show_info
    self.weapons = [self.weapon1]
    if self.weapon2: self.weapons += [self.weapon2]
    if self.weapon3: self.weapons += [self.weapon3]
    self.damage1 = self.weapon1.damage if self.weapon1 else 0
    self.damage2 = self.weapon2.damage if self.weapon2 else 0
    self.damage3 = self.weapon3.damage if self.weapon3 else 0
    self.damage = self.damage1 + self.damage2 + self.damage3
    
    ranges = []
    if self.weapon1: ranges += [self.weapon1.range_min, self.weapon1.range_max]
    if self.weapon2: ranges += [self.weapon2.range_min, self.weapon2.range_max]
    if self.weapon3: ranges += [self.weapon3.range_min, self.weapon3.range_max]
    try:
      self.range = [min(ranges), max(ranges)]
    except: Pdb().set_trace()
    if self.range[1] >= 6: self.ranged = 1
    
    self.pn = [self.weapon1.pn]
    if self.weapon2: self.pn += [self.weapon2.pn]
    if self.weapon3: self.pn += [self.weapon3.pn]
    self.pn = max(self.pn)
    
    # Levelup.
    self.levelup()
    # ranking.
    self.get_skills()
    self.set_skills()
    self.effects += [s.name for s in self.other_skills]
    self.set_ranking()
    self.leads = [i for i in self.leads if i.hp_total >= 1 and self.nation in i.belongs]
    self.squads_position = [it for it in self.squads_position 
                            if it.hp_total >= 1 and it in self.leads or it == self]
    self.leading = sum(i.units for i in self.leads)
    if self.leadership: 
      self.extra_leading = self.leading * 100 / self.leadership - 100
    self.group_ranking = self.ranking + sum(i.ranking for i in self.leads)
    self.hp_total = round(self.hp_total)
    self.ranking = round(self.ranking)



class Amphibian:

  def __init__(self):
    self.soil = [coast_t, glacier_t, grassland_t, plains_t, ocean_t, tundra_t]
    self.surf = [forest_t, none_t, river_t, swamp_t]



class Elf(Unit):

  def __init__(self, nation):
    super().__init__(nation)
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, none_t]
    self.soil = [grassland_t, plains_t, tundra_t, waste_t]
    self.surf = [forest_t, none_t, river_t, swamp_t]



class Ground:

  def __init__(self):
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [forest_t, none_t, river_t, swamp_t]
    self.soil = [grassland_t, plains_t, tundra_t, waste_t]
    self.surf = [forest_t, none_t, river_t, swamp_t]



class Human(Unit):

  def __init__(self, nation):
    super().__init__(nation)
    Ground.__init__(self)



class Ship(Unit):

  def __init__(self, nation):
    super().__init__(nation)
    self.type = "ship"
    self.soil = [coast_t, ocean_t] 



class Undead(Unit):

  def __init__(self, nation):
    super().__init__(nation)
    Ground.__init__(self)



# Elfos.
# edificios.
class Hall(City):
  name = "salón"
  traits = [elf_t]
  events = [Starving, Unrest, Looting, Revolt]
  food = 50
  food_rate = 80
  grouth = 50
  grouth_base = 0
  grouth_min_bu = 12
  grouth_min_upg = 6
  income = 100
  public_order = 20
  initial_unrest = 5
  resource = 1
  upkeep = 1500

  free_terrain = 1
  own_terrain = 0

  military_base = 45
  military_change = 100
  military_max = 70
  tags = [city_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [ElvesSettler, ForestGuard, PathFinder]
    # self.events = [i(self) for i in self.events]
    self.hill = [0]
    self.nation = nation
    self.pos = pos
    self.resource_cost = [100, 100]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t]

  def set_capital_bonus(self):
    self.food += 50
    self.public_order += 20
    self.upkeep = 0

  def set_downgrade(self):
    msg = ""
    if self.level == 1 and self.pop <= 1500:
      msg = f"{self} se degrada a {hamlet_t}."
      self.level = 0
      self.name = hamlet_t
      self.food -= 100
      self.grouth_total -= 5
      self.income -= 100
      # self.public_order -= 10
    if self.level == 2 and self.pop <= 5000:
      msg = f"{self} se degrada a {village_t}."
      self.level = 1
      self.name = village_t
      self.food -= 100
      self.grouth_total -= 5
      self.income -= 100
      # self.public_order -= 10
    if self.level == 3 and self.pop <= 14000:
      msg = f"{self} se degrada a {town_t}."
      self.level = 1
      self.name = town_t
      self.food -= 100
      self.grouth_total -= 5
      self.income -= 100
      # self.public_order -= 10
    if msg:
      self.nation.log[-1].append(msg)
      logging.debug(msg)
      if self.nation.show_info:
        sp.speak(msg, 1) 
        sleep(loadsound("notify18"))

  def set_upgrade(self):
    msg = ""
    if self.level == 0 and self.pop >= 2000:
      msg = f"{self} mejor a {village_t}."
      self.level = 1
      self.name = village_t
      self.food += 100
      self.grouth_total += 5
      self.income += 100
      # self.public_order += 10
    if self.level == 1 and self.pop >= 6000:
      msg = f"{self} mejor a {town_t}."
      self.level = 2
      self.name = town_t
      self.food += 100
      self.grouth_total += 5
      self.income += 100
      # self.public_order += 10
    if self.level == 2 and self.pop >= 15000:
      msg = f"{self} mejor a {city_t}."
      self.level = 3
      self.name = city_t
      self.food += 100
      self.grouth_total += 5
      self.income += 100
      # self.public_order += 10
    if msg:
      logging.debug(msg)
      if self.nation.show_info:
        sp.speak(msg, 1)
        sleep(loadsound("notify14"))



class GlisteningPastures(Building):
  name = "Pasturas radiantes"
  level = 1
  city_unique = 1
  size = 6
  gold = 10000
  food = 100
  grouth = 30
  income = 20

  own_terrain = 1
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [ElkRider]
    self.resource_cost = [0, 120]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t]
    self.hill = [0, 1]
    self.upgrade = [WhisperingWoods]



class WhisperingWoods(GlisteningPastures, Building):
  name = "Establos del viento"
  level = 2
  base = GlisteningPastures
  gold = 14000

  own_terrain = 1
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [DemonHunter, ForestRider, ForestGiant, ]
    self.resource_cost = [0, 120]
    self.size = 0



class FalconRefuge(Building):
  name = "refugio del alcón"
  level = 1
  city_unique = 1
  size = 4
  gold = 5000
  own_terrain = 1
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Falcon, Huntress]
    self.resource_cost = [0, 50]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t]
    self.hill = [0, 1]
    self.upgrade = [ForestLookout]



class ForestLookout(FalconRefuge, Building):
  name = "Observatorio forestal"
  level = 2
  base = FalconRefuge
  gold = 10000

  own_terrain = 1
  tags = [military_t]
  upkeep = 1000

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Druid, ForestEagle, WoodArcher]
    self.resource_cost = [0, 70]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t]
    self.hill = [0, 1]
    self.upgrade = []



class Sanctuary(Building):
  name = "santuario"
  level = 1
  city_unique = 1
  size = 6
  gold = 7000
  food = 100
  grouth = 50
  income = 100

  own_terrain = 1
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [BladeDancer, KeeperOfTheGrove]
    self.resource_cost = [0, 80]
    self.surf = [forest_t]
    self.hill = [0]
    self.upgrade = [HauntedForest]



class HauntedForest(Sanctuary, Building):
  name = "Bosque embrujado"
  level = 2
  base = Sanctuary
  gold = 10000
  own_terrain = 1
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [EternalGuard, ForestBear]
    self.resource_cost = [0, 120]
    self.size = 0
    self.surf = [forest_t]
    self.hill = [0]
    self.upgrade = [WailingWoods]



class WailingWoods(HauntedForest, Building):
  name = "wailing woods"
  level = 3
  base = HauntedForest
  gold = 15000
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [SisterFromTheDeepth]
    self.resource_cost = [0, 150]
    self.size = 0
    self.upgrade = [MoonsFountain]



class MoonsFountain(WailingWoods, Building):
  name = "Fuentes de la luna"
  level = 4
  base = Sanctuary
  gold = 20000
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [AwakenTree, Driad, PriestessOfTheMoon]
    self.resource_cost = [0, 150]
    self.size = 0
    self.upgrade = []



class Grove(Building):
  name = "Huerto"
  level = 1
  size = 6
  gold = 1000
  food = 50
  grouth = 20

  own_terrain = 1
  tags = [food_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 30]
    self.soil = [grassland_t, plains_t]
    self.surf = [forest_t, none_t]
    self.hill = [0]
    self.upgrade = [GrapeVines]



class GrapeVines(Grove, Building):
  name = "racimos de uva"
  level = 2
  base = Grove
  gold = 2500
  food = 100
  grouth = 30
  income = 20
  own_terrain = 1
  tags = [food_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 80]
    self.soil = [grassland_t, plains_t]
    self.surf = [forest_t, none_t]
    self.hill = [0]
    self.upgrade = [Vineyard]



class Vineyard(GrapeVines, Building):
  name = "Viñedo"
  level = 3
  base = GrapeVines
  gold = 8000
  food = 200
  grouth = 50
  income = 60
  own_terrain = 1
  tags = [food_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 150]
    self.soil = [grassland_t, plains_t]
    self.surf = [none_t]
    self.hill = [0]
    self.upgrade = []



class CraftmensTree(Building):
  name = "craftment tree 1"
  level = 1
  local_unique = 1
  size = 4
  local_unique = 1
  gold = 1500
  grouth = 10
  income = 20
  resource = 50
  own_terrain = 1
  tags = [resource_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 70]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t]
    self.hill = [0, 1]
    self.upgrade = [CraftmensTree2]



class CraftmensTree2(CraftmensTree, Building):
  name = "craftment tree 2"
  base = CraftmensTree
  level = 2
  local_unique = 1
  size = 4
  local_unique = 1
  gold = 3500
  grouth = 20
  income = 24
  resource = 100
  own_terrain = 1
  tags = [resource_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 70]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t]
    self.hill = [0, 1]
    self.upgrade = []



class StoneCarvers(Building):
  name = "StoneCarvers 1"
  level = 1
  size = 5
  local_unique = 1
  gold = 3000
  grouth = 10
  income = 30
  resource = 75
  
  own_terrain = 1
  tags = [resource_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 100]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [1]
    self.upgrade = [StoneCarvers2]



class StoneCarvers2(StoneCarvers, Building):
  name = "StoneCarvers 2"
  base = StoneCarvers
  level = 2
  size = 5
  local_unique = 1
  gold = 5000
  grouth = 20
  income = 50
  resource = 150
  
  own_terrain = 1
  tags = [resource_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 100]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [1]
    self.upgrade = []



# Commanders.
class Druid(Elf):
  name = "druida"
  namelist = [elves_name1, elves_name2]
  units = 5
  ln = 5
  min_units = 5
  max_squads = 1
  can_hire = 1
  leadership = 40
  poisonres = 1
  type = "infantry"
  wizard = 1
  traits = [elf_t, ]
  aligment = wild_t
  size = 2
  train_rate = 3
  upkeep = 25
  resource_cost = 22
  food = 3
  pop = 20
  terrain_skills = [DarkVision, ForestSurvival]

  hp = 10
  sight = 2
  mp = [2, 2]
  moves = 7
  resolve = 7
  power = 30
  power_max = 30
  power_res = 5
  global_skills = [ForestWalker, Furtive]

  dfs = 8
  res = 8
  hres = 4
  arm = 0
  armor = None

  weapon1 = weapons.ShortPoisonBow
  att1 = 1
  weapon2 = weapons.ToxicDagger
  att2 = 1
  off = 8
  strn = 5
  offensive_skills = [Ambushment]

  common = 4

  lead_traits = [elf_t, human_t, bear_t]
  lead_aligments = [nature_t, order_t, wild_t]

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [HealingRoots, SummonClayGolem, SummonFalcons]
  def levelup(self):
    if self.xp >= 20 and self.level == 1:
      self.level = 2
      self.leadership += 5



class KeeperOfTheGrove (Elf):
  name = "keeper of the grove "
  namelist = [elves_name1, elves_name2]
  units = 10
  sts = 4
  ln = 10
  min_units = 10
  max_squads = 1
  can_hire = 1
  leadership = 60
  type = "infantry"
  wizard = 1
  traits = [elf_t]
  aligment = wild_t
  size = 2
  train_rate = 3
  upkeep = 25
  resource_cost = 30
  food = 3
  pop = 2
  terrain_skills = [DarkVision, ForestSurvival]

  hp = 10
  sight = 5
  mp = [2, 2]
  moves = 7
  resolve = 7
  power = 0
  power_max = 30
  power_res = 3
  global_skills = [ForestWalker, Furtive, PyreOfCorpses, Regroup]

  dfs = 11
  res = 12
  hres = 4
  arm = 0
  armor = MediumArmor()

  weapon1 = weapons.GreatSword
  att1 = 2
  off = 10
  strn = 10

  lead_traits = [elf_t, human_t]
  lead_aligments = [order_t, wild_t]

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [RecruitForestGuards]
    self.spells = []  # [Entangling Roots ]
  def levelup(self):
    if self.xp >= 20 and self.level == 1:
      self.level = 2
      self.leadership += 5



class PathFinder(Elf):
  name = "Path finder"
  namelist = [elves_name1, elves_name2]
  units = 5
  sts = 2
  min_units = 5
  ln = 10
  max_squads = 1
  can_hire = 1
  leadership = 60
  type = "infantry"
  wizard = 1
  traits = [elf_t]
  aligment = wild_t
  size = 3
  train_rate = 2
  upkeep = 25
  resource_cost = 20
  food = 6
  pop = 3
  terrain_skills = [DarkVision, ForestSurvival]

  hp = 12
  sight = 30
  mp = [2, 2]
  moves = 8
  resolve = 8
  power = 0
  power_max = 60
  power_res = 5
  global_skills = [ForestWalker, Furtive, Organization, PyreOfCorpses]

  dfs = 8
  res = 7
  hres = 4
  arm = 0
  armor = LightArmor()

  weapon1 = weapons.LongBow
  att1 = 1
  weapon2 = weapons.ShortSword
  att2 = 1
  off = 7
  strn = 7

  lead_traits = [elf_t, human_t]
  lead_aligments = [order_t, wild_t]

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = []  # [Entangling Roots ]
  def levelup(self):
    if self.xp >= 20 and self.level == 1:
      self.level = 2
      self.leadership += 5



class PriestessOfTheMoon(Elf):
  name = "priestess of the moon"
  namelist = [elves_name1, elves_name2]
  units = 1
  min_units = 1
  ln = 1
  max_squads = 1
  can_hire = 1
  unique = 1
  leadership = 60
  type = "infantry"
  wizard = 1
  traits = [elf_t]
  aligment = wild_t
  size = 3
  train_rate = 3
  upkeep = 400
  resource_cost = 35
  food = 6
  pop = 20
  terrain_skills = [DarkVision, ForestSurvival]

  hp = 26
  hp_res = 5
  sight = 30
  mp = [4, 4]
  moves = 8
  resolve = 8
  power = 0
  power_max = 60
  power_res = 5
  global_skills = [ForestWalker, Furtive, Inspiration, PyreOfCorpses]

  dfs = 12
  res = 11
  hres = 4
  arm = 2
  armor = None

  weapon1 = weapons.LongBow
  att1 = 1
  weapon2 = weapons.TigerFangs
  att2 = 1
  off = 18
  strn = 12

  lead_traits = [elf_t, human_t]
  lead_aligments = [order_t, wild_t]

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = []
  def levelup(self):
    if self.xp >= 20 and self.level == 1:
      self.level = 2
      self.leadership += 5



class AwakenTree(Elf):
  name = "árbol despertado"
  units = 1
  min_units = 1
  ln = 3
  max_squads = 6
  poisonres = 1
  type = "infantry"
  traits = [tree_t]
  aligment = wild_t
  size = 6
  train_rate = 3
  upkeep = 30
  resource_cost = 30
  food = 4
  pop = 4
  terrain_skills = [ForestSurvival]

  hp = 50
  hp_res = 5
  mp = [2, 2]
  moves = 4
  resolve = 10
  global_skills = [ForestWalker]

  dfs = 6
  res = 14
  hres = 14
  hlm = 0
  arm = 5
  armor = None

  weapon1 = weapons.Branch
  att1 = 4
  weapon2 = weapons.Crush
  att2 = 1
  off = 10
  strn = 20
  offensive_skills = [ImpalingRoots]

  common = 3

  def __init__(self, nation):
    super().__init__(nation)
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class BladeDancer(Elf):
  name = "danzante de la espada"
  units = 10
  min_units = 10
  ln = 10
  max_squads = 5
  type = "infantry"
  traits = [elf_t]
  aligment = wild_t
  size = 2
  train_rate = 1.5
  upkeep = 16
  resource_cost = 24
  food = 3
  pop = 2
  terrain_skills = [Burn, DarkVision, ForestSurvival, Raid]

  hp = 10
  mp = [2, 2]
  moves = 7
  resolve = 8
  global_skills = [ForestWalker, PyreOfCorpses, Regroup]

  dfs = 9
  res = 8
  hres = 4
  arm = 0
  armor = None

  weapon1 = weapons.Sword
  att1 = 1
  weapon2 = weapons.Dagger
  att2 = 1
  off = 9
  strn = 12
  pn = 1
  offensive_skills = [Ambushment]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class DemonHunter(Elf):
  name = "demon hunter"
  units = 1
  ln = 1
  min_units = 1
  max_squads = 1
  type = "infantry"
  traits = [elf_t]
  aligment = wild_t
  size = 2
  train_rate = 3
  upkeep = 90
  resource_cost = 25
  food = 3
  pop = 25
  terrain_skills = [Burn, DarkVision, DesertSurvival, ForestSurvival, MountainSurvival, SwampSurvival]

  hp = 24
  hp_res = 4
  mp = [2, 2]
  moves = 6
  resolve = 7
  global_skills = [DHLevels, ForestWalker, Furtive, ShadowHunter]

  dfs = 10
  res = 12
  hres = 6
  arm = 0
  armor = None

  weapon1 = weapons.SoulDrain
  att1 = 1
  off = 10
  strn = 16
  offensive_skills = [Ambushment]

  def __init__(self, nation):
    super().__init__(nation)



class Driad(Elf):
  name = "driad"
  units = 5
  min_units = 5
  ln = 15
  max_squads = 5
  poisonres = 1
  type = "infantry"
  traits = [elf_t]
  aligment = wild_t
  size = 2
  train_rate = 3
  upkeep = 25
  resource_cost = 30
  food = 3
  pop = 3
  terrain_skills = [Burn, DarkVision, ForestSurvival]

  hp = 30
  hp_res = 5
  sight = 3
  mp = [2, 2]
  moves = 7
  resolve = 8
  global_skills = [ForestWalker, ElusiveShadow]

  dfs = 11
  res = 8
  hres = 4
  arm = 0
  armor = None

  weapon1 = weapons.ShortBow
  att1 = 2
  off = 9
  strn = 10
  
  offensive_skills = [Ambushment]

  common = 6

  def __init__(self, nation):
    super().__init__(nation)



class EternalGuard(Elf):
  name = "guardia eterna"
  units = 20
  sts = 4
  min_units = 20
  ln = 10
  max_squads = 3
  type = "infantry"
  traits = [elf_t]
  aligment = wild_t
  size = 2
  train_rate = 2
  upkeep = 35
  resource_cost = 25
  food = 4
  pop = 2
  terrain_skills = [Burn, DarkVision, ForestSurvival, Raid]

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 8
  global_skills = [ForestWalker, PyreOfCorpses, Regroup]

  dfs = 10
  res = 9
  hres = 4
  arm = 0
  armor = HeavyArmor()

  weapon1 = weapons.Spear
  att1 = 1
  weapon2 = weapons.Dagger
  att2 = 1
  off = 9
  strn = 12
  offensive_skills = [PikeSquare]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class Falcon(Elf):
  name = "Alcón"
  units = 2
  min_units = 2
  ln = 20
  max_squads = 10
  type = "beast"
  traits = [falcon_t]
  aligment = nature_t
  size = 1
  train_rate = 3
  upkeep = 30
  resource_cost = 18
  food = 3
  pop = 3
  terrain_skills = [Fly, ForestSurvival]

  hp = 3
  sight = 5
  mp = [4, 4]
  moves = 10
  resolve = 6
  global_skills = [ForestWalker]

  dfs = 8
  res = 5
  hres = 1
  arm = 0
  armor = None

  weapon1 = weapons.Claw
  att1 = 2
  weapon2 = weapons.Bite
  att2 = 2
  off = 11
  strn = 5
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)



class ForestBear(Unit):
  name = "Oso del bosque"
  units = 4
  min_units = 4
  ln = 7
  max_squads = 10
  type = "beast"
  traits = [bear_t]
  aligment = nature_t
  size = 3
  train_rate = 2
  upkeep = 20
  resource_cost = 22
  food = 5
  pop = 3
  terrain_skills = [ForestSurvival]

  hp = 16
  mp = [2, 2]
  moves = 6
  resolve = 6
  global_skills = [ForestWalker, Furtive]

  dfs = 8
  res = 12
  hres = 6
  arm = 1
  armor = None

  weapon1 = weapons.Claw
  att1 = 2
  weapon2 = weapons.Bite
  att2 = 1
  off = 9
  strn = 10

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [DeadBear]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class ForestEagle(Elf):
  name = "águila del bosque"
  units = 2
  min_units = 2
  ln = 20
  max_squads = 10
  type = "beast"
  traits = [eagle_t]
  aligment = nature_t
  size = 2
  train_rate = 3
  upkeep = 30
  resource_cost = 25
  food = 4
  pop = 4
  terrain_skills = [Fly, ForestSurvival]

  hp = 7
  sight = 3
  mp = [3, 3]
  moves = 8
  resolve = 8
  global_skills = [ForestWalker]

  dfs = 8
  res = 7
  hres = 1
  arm = 0
  armor = None

  weapon1 = weapons.Claw
  att1 = 2
  weapon2 = weapons.Bite
  att2 = 1
  off = 10
  strn = 7

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Harpy]



class GreatEagle(Elf):
  name = "great eagle "
  units = 1
  min_units = 1
  max_squads = 1
  type = "beast"
  traits = [eagle_t]
  aligment = nature_t
  size = 3
  train_rate = 4
  upkeep = 50
  resource_cost = 35
  food = 6
  pop = 5
  terrain_skills = [Fly, ForestSurvival, MountainSurvival]

  hp = 30
  sight = 3
  mp = [4, 4]
  moves = 8
  resolve = 10
  global_skills = [ForestWalker]

  dfs = 8
  res = 8
  hres = 2
  arm = 2
  armor = None

  weapon1 = weapons.Talon
  att1 = 2
  weapon2 = weapons.Beak
  att2 = 1
  off = 11
  strn = 9

  def __init__(self, nation):
    super().__init__(nation)



class ForestGiant(Unit):
  name = "forest giant"
  units = 5
  min_units = 5
  ln = 5
  max_squads = 6
  type = "beast"
  traits = [beast_t]
  aligment = wild_t
  size = 4
  train_rate = 2
  upkeep = 30
  resource_cost = 24
  food = 5
  pop = 5
  terrain_skills = [Burn, ForestSurvival, MountainSurvival, Raid]

  hp = 16
  mp = [2, 2]
  moves = 5
  resolve = 6
  global_skills = [ForestWalker]

  dfs = 8
  res = 12
  hres = 8
  arm = 2
  armor = None

  weapon1 = weapons.GreatClub
  att1 = 1
  weapon2 = weapons.Crush
  att2 = 1
  off = 9
  strn = 11

  common = 4

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Abomination]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class ForestGuard(Elf):
  name = "guardia forestal"
  units = 20
  min_units = 10
  ln = 10
  max_squads = 10
  type = "infantry"
  traits = [elf_t]
  aligment = wild_t
  size = 2
  train_rate = 1.5
  upkeep = 6
  resource_cost = 14
  food = 2
  pop = 1.3
  terrain_skills = [Burn, ForestSurvival, Raid]

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 6
  global_skills = [ForestWalker, PyreOfCorpses]

  dfs = 9
  res = 8
  hres = 2
  arm = 0
  armor = None

  weapon1 = weapons.ShortSword
  att1 = 1
  off = 8
  strn = 8
  offensive_skills = [Ambushment]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class ForestRider(Elf):
  name = "forest rider"
  units = 5
  sts = 2
  min_units = 5
  ln = 7
  max_squads = 6
  type = "cavalry"
  mounted = 1
  traits = [elf_t]
  aligment = wild_t
  size = 3
  train_rate = 3
  upkeep = 40
  resource_cost = 30
  food = 5
  pop = 4
  terrain_skills = [Burn, ForestSurvival, Raid]

  hp = 18
  mp = [4, 4]
  moves = 6
  resolve = 8
  global_skills = [ForestWalker, PyreOfCorpses, Regroup]

  dfs = 10
  res = 10
  hres = 4
  arm = 1
  armor = HeavyArmor
  shield = Shield()

  weapon1 = weapons.Lance 
  att1 = 1
  weapon2 = weapons.Hoof
  att2 = 2
  off = 9
  strn = 11
  offensive_skills = [HeavyCharge]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, none_t]



class ElvesSettler(Human):
  name = elf_settler_t
  units = 15
  min_units = 10
  ln = 10
  max_squads = 1
  settler = 1
  type = "civil"
  traits = [elf_t]
  aligment = wild_t
  size = 2
  train_rate = 3
  upkeep = 20
  resource_cost = 40
  food = 6
  pop = 10
  terrain_skills = [ForestSurvival]

  hp = 4
  mp = [2, 2]
  moves = 3
  resolve = 4

  dfs = 5
  res = 5
  hres = 1
  arm = 0
  armor = None

  weapon1 = weapons.Fist
  att1 = 1
  off = 4
  strn = 5

  def __init__(self, nation):
    super().__init__(nation)
    self.buildings = [Hall]
    self.corpses = [Zombie]



class Huntress(Elf):
  name = huntresse_t
  units = 5
  min_units = 5
  max_squads = 5
  type = "infantry"
  traits = [elf_t]
  aligment = wild_t
  size = 2
  train_rate = 1.5
  upkeep = 12
  resource_cost = 14
  food = 2
  pop = 2
  terrain_skills = [Burn, ForestSurvival]

  hp = 10
  sight = 2
  mp = [2, 2]
  moves = 6
  resolve = 6
  global_skills = [ForestWalker, Furtive, PyreOfCorpses]

  dfs = 8
  res = 7
  hres = 1
  arm = 0
  armor = None

  weapon1 = weapons.CrossBow
  att1 = 1
  weapon2 = weapons.Dagger
  att2 = 1
  off = 6
  strn = 8
  offensive_skills = [Ambushment, Skirmisher]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class WoodArcher(Elf):
  name = "alto arquero silvano"
  units = 10
  sts = 2
  min_units = 10
  max_squads = 5
  type = "infantry"
  traits = [elf_t]
  aligment = wild_t
  size = 2
  train_rate = 2
  upkeep = 15
  resource_cost = 28
  food = 2
  pop = 2
  terrain_skills = [Burn, DarkVision, ForestSurvival, Raid]

  hp = 10
  mp = [2, 2]
  moves = 7
  resolve = 7
  global_skills = [ForestWalker, Furtive, PyreOfCorpses, Regroup]

  dfs = 8
  res = 8
  hres = 1
  arm = 0
  armor = None

  weapon1 = weapons.Bow
  att1 = 1
  weapon2 = weapons.Dagger
  att1 = 1
  off = 6
  strn = 9
  offensive_skills = [Ambushment, Skirmisher, Withdrawall]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class SisterFromTheDeepth(Elf):
  name = "sister from the deppth"
  units = 10
  min_units = 5
  max_squads = 6
  poisonres = 1
  type = "infantry"
  traits = [elf_t]
  aligment = wild_t
  size = 2
  train_rate = 3
  upkeep = 15
  resource_cost = 22
  food = 2
  pop = 3
  terrain_skills = [Burn, DarkVision, ForestSurvival]

  hp = 10
  sight = 2
  mp = [2, 2]
  moves = 7
  resolve = 6
  global_skills = [ForestWalker, Furtive, PyreOfCorpses, Regroup]

  dfs = 7
  res = 8
  hres = 1
  arm = 0
  armor = None

  weapon1 = weapons.ShortPoisonBow
  att1 = 1
  weapon2 = weapons.ToxicDagger
  att2 = 1
  off = 5
  strn = 3
  offensive_skills = [Ambushment, Skirmisher]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class ElkRider(Elf):
  name = "wild huntsman"
  units = 5
  min_units = 5
  ln = 5
  max_squads = 6
  type = "cavalry"
  mounted = 1
  traits = [elf_t]
  aligment = wild_t
  size = 4
  train_rate = 3
  upkeep = 50
  resource_cost = 25
  food = 5
  pop = 4.5
  terrain_skills = [Burn, ForestSurvival, Raid]

  hp = 16
  mp = [3, 3]
  moves = 6
  resolve = 6
  global_skills = [ForestWalker, Furtive]

  dfs = 8
  res = 12
  hres = 6
  arm = 2
  armor = None

  weapon1 = weapons.LongBow
  att1 = 1
  weapon2 = weapons.HeavyHoof
  att2 = 2
  off = 5
  strn = 10
  offensive_skills = [BattleFocus]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, none_t]  



# Holy empire.
class Hamlet(City):
  name = hamlet_t
  traits = [human_t]
  events = [Starving, Unrest, Looting, Revolt]
  food = 50
  food_rate = 80
  grouth = 100
  grouth_factor = 40
  grouth_min_bu = 10
  grouth_min_upg = 6
  income = 100
  initial_unrest = 5
  public_order = 10
  resource = 1
  upkeep = 1000

  free_terrain = 1
  own_terrain = 0

  military_base = 40
  military_change = 100
  military_max = 60
  tags = [city_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Decarion, PeasantLevy, Settler]
    # self.events = [i(self) for i in self.events]
    self.nation = nation
    self.pos = pos
    self.resource_cost = [100, 100]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [none_t]
    self.hill = [0]

  def set_capital_bonus(self):
    self.food += 50
    self.public_order += 10
    self.upkeep = 0

  def set_downgrade(self):
    msg = ""
    if self.level == 1 and self.pop <= 2500:
      msg = f"{self} se degrada a {hamlet_t}."
      self.level = 0
      self.name = hamlet_t
      self.food -= 1.5
      self.grouth_total -= 5
      # self.income -= 10
      self.public_order -= 10
    if self.level == 2 and self.pop <= 8000:
      msg = f"{self} se degrada a {village_t}."
      self.level = 1
      self.name = village_t
      self.food -= 1.5
      self.grouth_total -= 5
      # self.income -= 10
      self.public_order -= 10
    if self.level == 3 and self.pop <= 18000:
      msg = f"{self} se degrada a {town_t}."
      self.level = 2
      self.name = town_t
      self.food -= 1.5
      self.grouth_total -= 5
      # self.income -= 10
      self.public_order -= 10
    if msg:
      self.nation.log[-1].append(msg)
      logging.debug(msg)
      if self.nation.show_info:
        sp.speak(msg, 1) 
        sleep(loadsound("notify18"))

  def set_upgrade(self):
    msg = ""
    if self.level == 0 and self.pop >= 3000:
      msg = f"{self} mejor a {village_t}."
      self.level = 1
      self.name = village_t
      self.food += 1.5
      self.grouth_total += 5
      self.public_order += 10
    if self.level == 1 and self.pop >= 10000:
      msg = f"{self} mejor a {town_t}."
      self.level = 2
      self.name = town_t
      self.food += 1.5
      self.grouth_total += 5
      # self.income += 10
      self.public_order += 10
    if self.level == 2 and self.pop >= 20000:
      msg = f"{self} mejor a {city_t}."
      self.level = 3
      self.name = city_t
      self.food += 1.5
      self.grouth_total += 5
      self.public_order += 10
    if msg:
      self.nation.log[-1] += [msg]
      logging.debug(msg)
      if self.nation.show_info:
        sp.speak(msg, 1)
        sleep(loadsound("notify14"))



# edificios.
class TrainingCamp(Building):
  name = "campo de entrenamiento"
  level = 1
  city_unique = 1
  size = 4
  gold = 5000
  own_terrain = 1
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Velites, Sagittarii]
    self.resource_cost = [0, 40]
    self.soil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [0]
    self.upgrade = [ImprovedTrainingCamp]



class ImprovedTrainingCamp(TrainingCamp, Building):
  name = "campo de entrenamiento mejorado"
  level = 2
  base = TrainingCamp
  gold = 8000
  public_order = 10
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Centurion, Hastati, Principes, ]  
    self.resource_cost = [0, 70]
    self.size = 0
    self.upgrade = [Barracks]



class Barracks(ImprovedTrainingCamp, Building):
  name = "cuartel"
  level = 3
  base = TrainingCamp
  gold = 12000
  public_order = 10
  tags = [military_t, unrest_t]
  upkeep = 500

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [ImperialGuard, Aquilifer]
    self.resource_cost = [0, 120]
    self.size = 0
    self.upgrade = [ImprovedBarracks]



class ImprovedBarracks(Barracks, Building):
  name = "cuartel mejorado"
  level = 4
  base = TrainingCamp
  gold = 16000
  public_order = 20
  tags = [military_t, unrest_t]
  upkeep = 1500

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [CrossBowMan, Halberdier, Legatus]
    self.resource_cost = [0, 200]
    self.size = 0



class Pastures(Building):
  name = "pasturas"
  level = 1
  city_unique = 1
  size = 6
  gold = 8000
  food = 100
  income = 50

  own_terrain = 1
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Decurion, Equite]
    self.resource_cost = [0, 80]
    self.soil = [grassland_t, plains_t]
    self.surf = [none_t]
    self.hill = [0]
    self.upgrade = [Stables]



class Stables(Pastures, Building):
  name = "establos"
  level = 2
  base = Pastures
  gold = 12000
  food = 100
  income = 100

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Equites2, Legatus]
    self.resource_cost = [0, 140]
    self.size = 0
    self.hill = [0]
    self.upgrade = []



class PlaceOfProphecy(Building):
  name = "place of prophecy"
  level = 1
  city_unique = 1
  size = 4
  gold = 4000
  own_terrain = 1
  public_order = 10
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Flagellant]
    self.resource_cost = [0, 40]
    self.soil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [0]
    self.upgrade = [HolyFountains]



class HolyFountains(PlaceOfProphecy, Building):
  name = "holy fountains"
  level = 2
  base = PlaceOfProphecy
  gold = 8000
  public_order = 15

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [RebornOne, Augur]
    self.resource_cost = [0, 50]
    self.size = 0
    self.upgrade = [TheMarbleTemple]



class TheMarbleTemple(PlaceOfProphecy, Building):
  name = "the marble temple"
  level = 3
  base = PlaceOfProphecy
  gold = 13500
  public_order = 30
  upkeep = 1000

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [KnightsTemplar , Flamen, SacredWarrior]
    self.resource_cost = [0, 100]
    self.size = 0
    self.upgrade = [FieldsOfJupiter]


class FieldsOfJupiter(TheMarbleTemple, Building):
  name = "templo de la luz"
  level = 4
  base = PlaceOfProphecy
  gold = 18000
  public_order = 50
  upkeep = 2500

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [PontifexMaximus, Gryphon, GryphonRiders]
    self.resource_cost = [0, 160]
    self.size = 0
    self.upgrade = []



# Commanders
class Augur(Unit):
  name = "augur"
  namelist = [praenomen, nomen, cognomen]
  units = 10
  sts = 2
  min_units = 5
  ln = 10
  max_squads = 1
  can_hire = 1
  leadership = 30
  type = "infantry"
  wizard = 1
  traits = [human_t]
  aligment = sacred_t
  size = 2
  train_rate = 3
  upkeep = 20
  resource_cost = 30
  food = 3
  pop = 3

  hp = 10
  sight = 2
  mp = [2, 2]
  moves = 5
  resolve = 7
  power = 20
  power_max = 30
  power_res = 3
  global_skills = [Regroup, SermonOfCourage]  # cure

  dfs = 7
  res = 6
  hres = 1
  arm = 0
  armor = None

  weapon1 = weapons.Staff
  att1 = 1
  att1 = 1
  off = 7
  strn = 5

  lead_traits = [human_t, sacred_t]
  lead_aligments = [order_t, sacred_t]

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [HealingRoots, SightFromFuture]
  def levelup(self):
    if self.xp >= 30 and self.level == 1:
      self.level = 2
      self.leadership += 5



class Aquilifer(Human):
  name = "aquilifer"
  namelist = [praenomen, nomen, cognomen]
  units = 20
  sts = 5
  ln = 10
  min_units = 10
  max_squads = 1
  can_hire = 1
  is_leader = 1
  leadership = 80
  unique = 1
  type = "infantry"
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 3
  upkeep = 30
  resource_cost = 35
  food = 5
  pop = 4
  unique = 1
  tags = ["commander"]

  hp = 15
  power = 2
  power_max = 6
  power_res = 4
  mp = [4, 4]
  moves = 7
  resolve = 8
  global_skills = [Inspiration, Regroup]

  dfs = 11
  res = 9
  hres = 2
  arm = 0
  armor = HeavyArmor()
  shield = Shield()

  weapon1 = weapons.GreatSword
  att1 = 2
  weapon2 = weapons.Pugio
  att2 = 1
  off = 11
  strn = 12

  lead_traits = [human_t]
  lead_aligments = [order_t, sacred_t]

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [RecruitLevy]
  def levelup(self):
    if self.xp >= 30 and self.level == 1:
      self.level = 2
      self.leadership += 5



class Ballistarius(Human):
  name = "Ballistarius"
  namelist = [praenomen, nomen]
  units = 10
  sts = 2
  ln = 10
  min_units = 10
  max_squads = 1
  can_hire = 1
  leadership = 40
  type = "infantry"
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 2
  upkeep = 25
  resource_cost = 25
  food = 5
  pop = 2.5
  terrain_skills = []
  tags = ["commander"]

  hp = 10
  power = 2
  power_max = 6
  power_res = 2
  mp = [2, 2]
  moves = 6
  resolve = 8
  global_skills = [Organization, Regroup]

  dfs = 8
  res = 8
  hres = 1
  arm = 0
  armor = MediumArmor()
  shield = Shield()
  defensive_skills = []

  weapon1 = weapons.GreatSword
  att1 = 2
  weapon2 = weapons.Pugio
  att2 = 1
  off = 8
  strn = 12
  offensive_skills = []

  can_hire = 1
  lead_traits = [human_t]
  lead_alignment = [order_t]

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = []
    self.mp = [2, 2]



class Centurion(Human):
  name = "centurion"
  namelist = [praenomen, nomen]
  units = 20
  sts = 4
  ln = 10
  min_units = 10
  max_squads = 1
  can_hire = 1
  leadership = 100
  type = "infantry"
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 2.5
  upkeep = 15
  resource_cost = 25
  food = 5
  pop = 2.2
  terrain_skills = []
  tags = ["commander"]

  hp = 10
  power = 2
  power_max = 6
  power_res = 2
  mp = [2, 2]
  moves = 6
  resolve = 8
  global_skills = [HoldPositions, Organization, Regroup]

  dfs = 10
  res = 9
  hres = 4
  arm = 0
  armor = MediumArmor()
  shield = Shield()
  defensive_skills = []

  weapon1 = weapons.GreatSword
  att1 = 2
  weapon2 = weapons.Pugio
  att2 = 1
  off = 10
  strn = 12
  offensive_skills = []

  can_hire = 1
  lead_traits = [human_t]
  lead_alignment = [order_t]

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [RecruitLevy]
    self.mp = [2, 2]
  def levelup(self):
    if self.xp >= 30 and self.level == 1:
      self.level = 2
      self.leadership += 5



class Decarion(Human):
  name = "decarion"
  namelist = [praenomen, nomen]
  units = 10
  sts = 2
  min_units = 10
  ln = 10
  max_squads = 1
  can_hire = 1
  leadership = 60
  type = "infantry"
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 2
  upkeep = 25
  resource_cost = 15
  food = 5
  pop = 2
  terrain_skills = []
  tags = ["commander"]

  hp = 10
  power = 2
  power_max = 6
  power_res = 2
  mp = [2, 2]
  moves = 6
  resolve = 8
  global_skills = [Organization, Regroup]

  dfs = 9
  res = 8
  hres = 4
  arm = 0
  armor = MediumArmor()
  shield = Shield()
  defensive_skills = []

  weapon1 = weapons.GreatSword
  att1 = 2
  weapon2 = weapons.Pugio
  att2 = 1
  off = 9
  strn = 9
  offensive_skills = []

  can_hire = 1
  lead_traits = [human_t]
  lead_aligments = [order_t]

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = []
    self.mp = [2, 2]
  def levelup(self):
    if self.xp >= 30 and self.level == 1:
      self.level = 2
      self.leadership += 5



class Decurion(Human):
  name = "Decurion"
  namelist = [praenomen, nomen]
  units = 10
  sts = 2
  min_units = 10
  max_squads = 1
  can_hire = 1
  leadership = 70
  type = "infantry"
  mounted = 1
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 2.5
  upkeep = 30
  resource_cost = 20
  food = 5
  pop = 3
  terrain_skills = []
  tags = ["commander"]

  hp = 10
  power = 2
  power_max = 6
  power_res = 2
  mp = [4, 4]
  moves = 6
  resolve = 8
  global_skills = [Organization, Regroup]

  dfs = 9
  res = 9
  hres = 4
  arm = 0
  armor = MediumArmor()
  shield = Shield()
  defensive_skills = []

  weapon1 = weapons.GreatSword
  att1 = 2
  weapon2 = weapons.Pugio
  att2 = 1
  off = 9
  strn = 12
  offensive_skills = []

  can_hire = 1
  lead_traits = [human_t]
  lead_alignment = [order_t]

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = []
    self.mp = [2, 2]
  def levelup(self):
    if self.xp >= 30 and self.level == 1:
      self.level = 2
      self.leadership += 5



class Flamen(Human):
  name = "flamen"
  namelist = [praenomen, nomen, cognomen]
  units = 10
  sts = 2
  min_units = 10
  ln = 10
  max_squads = 1
  can_hire = 1
  leadership = 30
  type = "infantry"
  wizard = 1
  traits = [human_t]
  aligment = sacred_t
  size = 2
  train_rate = 3
  upkeep = 40
  resource_cost = 30
  food = 3
  pop = 4

  hp = 15
  mp = [2, 2]
  moves = 5
  resolve = 8
  power = 20
  power_max = 20
  global_skills = [Regroup, SermonOfCourage]

  dfs = 7
  res = 6
  hres = 1
  arm = 0
  armor = LightArmor()

  weapon1 = weapons.Staff
  att1 = 1
  off = 8
  strn = 5

  lead_traits = [human_t]
  lead_aligments = [order_t, sacred_t]

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [BlessingWeapons]  # Cleanship
  def levelup(self):
    if self.xp >= 30 and self.level == 1:
      self.level = 2
      self.leadership += 5



class Legatus(Human):
  name = "legatus"
  namelist = [praenomen, nomen, cognomen]
  units = 10
  sts = 2
  ln = 10
  min_units = 10
  max_squads = 1
  can_hire = 1
  leadership = 140
  type = "infantry"
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 2.5
  upkeep = 50
  resource_cost = 40
  food = 5
  pop = 4
  terrain_skills = []
  tags = ["commander"]

  hp = 10
  power = 4
  power_max = 6
  power_res = 4
  mp = [4, 4]
  moves = 6
  resolve = 8
  global_skills = [HoldPositions, Organization, Regroup]

  dfs = 10
  res = 10
  hres = 4
  arm = 0
  armor = MediumArmor()
  shield = Shield()
  defensive_skills = []

  weapon1 = weapons.GreatSword
  att1 = 2
  weapon2 = weapons.Pugio
  att2 = 1
  off = 10
  strn = 12
  offensive_skills = []

  lead_traits = [human_t]
  lead_aligments = [order_t]

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [RecruitLevy]
    self.mp = [2, 2]
  def levelup(self):
    if self.xp >= 30 and self.level == 1:
      self.level = 2
      self.leadership += 5



class PontifexMaximus(Unit):
  name = "pontifex maximus"
  namelist = [praenomen, nomen, cognomen]
  units = 5
  sts = 5
  min_units = 5
  ln = 10
  max_squads = 1
  leadership = 40
  unique = 1
  type = "infantry"
  wizard = 1
  traits = [human_t]
  aligment = sacred_t
  size = 2
  train_rate = 3
  upkeep = 60
  resource_cost = 30
  food = 5
  pop = 80

  hp = 10
  mp = [2, 2]
  moves = 5
  resolve = 8
  power = 40
  power_max = 40
  global_skills = [Regroup, SermonOfCourage]

  dfs = 7
  res = 6
  hres = 1
  arm = 0
  armor = LightArmor()
  shield = Shield()

  weapon1 = weapons.Staff
  att1 = 1
  off = 7
  strn = 5

  lead_traits = [human_t, sacred_t]
  lead_aligments = [sacred_t]

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [SummonSecondSun, SummonDevourerOfDemons]
  def levelup(self):
    if self.xp >= 30 and self.level == 1:
      self.level = 2
      self.leadership += 5



# unidades
class Settler(Human):
  name = settler_t
  units = 20
  min_units = 20
  ln = 10
  max_squads = 1
  settler = 1
  type = "civil"
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 4
  upkeep = 10
  resource_cost = 30
  food = 5
  pop = 12

  hp = 3
  mp = [2, 2]
  moves = 3
  resolve = 2

  dfs = 6
  res = 1
  hres = 0
  arm = 0
  armor = None

  weapon1 = weapons.Fist
  att1 = 1
  off = 5
  strn = 4
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.buildings = [Hamlet]
    self.corpses = [Zombie]



class Flagellant(Human):
  name = flagellant_t
  units = 20
  min_units = 10
  ln = 10
  max_squads = 10
  type = "infantry"
  traits = [human_t]
  aligment = sacred_t
  size = 2
  train_rate = 1.5
  upkeep = 6
  resource_cost = 11
  food = 2
  pop = 1.5
  terrain_skills = [Burn]

  hp = 10
  mp = [2, 2]
  moves = 5
  resolve = 5
  global_skills = [PyreOfCorpses]

  dfs = 8
  res = 8
  hres = 2
  arm = 0
  armor = None

  weapon1 = weapons.Flail
  att1 = 1
  weapon2 = weapons.Fist
  att2 = 1
  off = 8
  strn = 8
  offensive_skills = [Fanatism]

  common = 8

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]



class RebornOne(Human):
  name = "renacido"
  units = 20
  min_units = 10
  ln = 10
  max_squads = 10
  type = "infantry"
  traits = [human_t]
  aligment = sacred_t
  size = 2
  train_rate = 2
  upkeep = 14
  resource_cost = 14
  food = 3
  pop = 1.7
  terrain_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 5
  resolve = 5
  global_skills = [PyreOfCorpses, Regroup]

  dfs = 9
  res = 9
  hres = 4
  arm = 0
  armor = None
  Shield = Shield()

  weapon1 = weapons.Sword
  att1 = 1
  weapon2 = weapons.Fist
  att2 = 1
  off = 9
  strn = 9
  offensive_skills = [Fanatism]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]



class Velites(Human):
  name = "velites "
  units = 20
  min_units = 10
  ln = 10
  max_squads = 6
  type = "infantry"
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 1.5
  upkeep = 20
  resource_cost = 12
  food = 3
  pop = 2.5
  terrain_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 5
  global_skills = [PyreOfCorpses, Undisciplined]

  dfs = 8
  res = 8
  hres = 2
  arm = 0
  armor = None
  shield = Shield()

  weapon1 = weapons.Sword
  att1 = 1
  weapon2 = weapons.Fist
  att2 = 1 
  off = 8
  strn = 9

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]



class ImperialGuard(Human):
  name = "guardia imperial"
  units = 10
  sts = 4
  min_units = 10
  ln = 10
  max_squads = 3
  type = "infantry"
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 2
  upkeep = 40
  resource_cost = 18
  food = 4
  pop = 3
  terrain_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 7
  resolve = 7
  global_skills = [BattleBrothers, PyreOfCorpses, Regroup]

  dfs = 9
  res = 9
  hres = 4
  arm = 0
  armor = HeavyArmor()

  weapon1 = weapons.GreatSword
  att1 = 2
  weapon2 = weapons.Pugio
  att2 = 1
  off = 9
  strn = 10

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]



class Hastati(Human):
  name = "hastati"
  units = 10
  sts = 1
  min_units = 10
  sts = 1
  ln = 10
  max_squads = 3
  type = "infantry"
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 2
  upkeep = 25
  resource_cost = 15
  food = 3
  pop = 2
  terrain_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 5
  resolve = 5
  global_skills = [BattleBrothers, PyreOfCorpses, Regroup]

  dfs = 9
  res = 10
  hres = 4
  arm = 0
  armor = None

  weapon1 = weapons.BronzeSpear
  att1 = 1
  weapon2 = weapons.Dagger
  att2 = 1
  off = 9
  strn = 11
  offensive_skills = [PikeSquare]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]



class Principes(Human):
  name = "principes"
  units = 10
  sts = 2
  min_units = 10
  ln = 10
  max_squads = 6
  type = "infantry"
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 2.5
  upkeep = 40
  resource_cost = 24
  food = 3
  pop = 2.5
  terrain_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 5
  resolve = 6
  global_skills = [BattleBrothers, PyreOfCorpses, Regroup]

  dfs = 9
  res = 10
  hres = 4
  arm = 0
  armor = HeavyArmor()

  weapon1 = weapons.Spear
  att1 = 1
  weapon2 = weapons.Pugio
  att2 = 1
  off = 9
  strn = 11
  offensive_skills = [PikeSquare]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]



class Halberdier(Human):
  name = "halberdier"
  units = 10
  sts = 2
  min_units = 10
  ln = 10
  max_squads = 6
  type = "infantry"
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 2.5
  upkeep = 40
  resource_cost = 18
  food = 4
  pop = 3
  terrain_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 7
  resolve = 6
  global_skills = [BattleBrothers, PyreOfCorpses]

  dfs = 9
  res = 10
  hres = 4
  arm = 0
  armor = MediumArmor()

  weapon1 = weapons.Halberd
  att1 = 1
  weapon2 = weapons.Pugio
  att2 = 1
  off = 9
  strn = 11
  offensive_skills = [MassSpears, PikeSquare]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]



class SacredWarrior(Human):
  name = sacred_warrior_t
  units = 10
  min_units = 10
  ln = 10
  max_squads = 6
  type = "infantry"
  traits = [human_t]
  aligment = sacred_t
  size = 2
  train_rate = 2.5
  upkeep = 30
  resource_cost = 16
  food = 3
  pop = 3
  terrain_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 7
  global_skills = [BattleBrothers, PyreOfCorpses, Regroup]

  dfs = 9
  res = 10
  hres = 4
  arm = 0
  armor = None
  shield = Shield()

  weapon1 = weapons.BlessedSword
  att1 = 1
  weapon2 = weapons.Pugio
  att2 = 1
  off = 9
  strn = 10
  offensive_skills = [ShadowHunter]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]



class KnightsTemplar (Human):
  name = knights_templar_t
  units = 5
  min_units = 5
  ln = 5
  max_squads = 6
  type = "infantry"
  traits = [human_t]
  aligment = sacred_t
  size = 2
  train_rate = 2
  upkeep = 60
  resource_cost = 22
  food = 4
  pop = 5
  terrain_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 7
  global_skills = [BattleBrothers, PyreOfCorpses, Regroup]

  dfs = 10
  res = 11
  hres = 4
  arm = 0
  armor = HeavyArmor()

  weapon1 = weapons.LongSpear
  att1 = 1
  weapon2 = weapons.Pugio
  att2 = 1
  off = 10
  strn = 12
  offensive_skills = [PikeSquare]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]  



class Sagittarii(Human):
  name = "sagittarii"
  units = 10
  sts = 2
  min_units = 10
  max_squads = 4
  type = "infantry"
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 1.5
  upkeep = 14
  resource_cost = 12
  food = 3
  pop = 2
  terrain_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 6
  global_skills = [PyreOfCorpses]

  dfs = 8
  res = 9
  hres = 2
  arm = 0
  armor = None

  weapon1 = weapons.Bow
  att1 = 1
  weapon2 = weapons.Dagger
  att2 = 1
  off = 5
  strn = 8
  offensive_skills = [Ambushment, ReadyAndWaiting, Skirmisher, Withdrawall]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]



class CrossBowMan(Human):
  name = "CrossBowMan"
  units = 10
  sts = 2
  min_units = 10
  max_squads = 3
  type = "infantry"
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 2
  upkeep = 20
  resource_cost = 18
  food = 3
  pop = 2.5

  hp = 10
  mp = [2, 2]
  moves = 5
  resolve = 6
  global_skills = [PyreOfCorpses]

  dfs = 8
  res = 9
  hres = 2
  arm = 0
  armor = None

  weapon1 = weapons.CrossBow
  att1 = 1
  weapon2 = weapons.Dagger
  att2 = 1
  off = 8
  strn = 10
  offensive_skills = [Ambushment, ReadyAndWaiting]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]



class Arquebusier(Human):
  name = "Arquebusier"
  units = 10
  sts = 2
  min_units = 10
  max_squads = 5
  type = "infantry"
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 2
  upkeep = 40
  resource_cost = 25
  food = 3
  pop = 2.5

  hp = 10
  mp = [2, 2]
  moves = 5
  resolve = 6
  global_skills = [PyreOfCorpses]

  dfs = 8
  res = 9
  hres = 2
  arm = 0
  armor = None

  att1 = 1
  off = 7
  strn = 10
  offensive_skills = [Ambushment, ReadyAndWaiting, Skirmisher]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]



class Musket(Human):
  name = "musquet"
  units = 10
  sts = 2
  min_units = 10
  max_squads = 5
  type = "infantry"
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 2
  upkeep = 50
  resource_cost = 30
  food = 3
  pop = 2.5

  hp = 10
  mp = [2, 2]
  moves = 5
  resolve = 6
  global_skills = [PyreOfCorpses]

  dfs = 8
  res = 9
  hres = 2
  arm = 0
  armor = None

  att1 = 2
  off = 9
  strn = 10
  offensive_skills = [Ambushment, ReadyAndWaiting, Skirmisher]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]



class Equite(Human):
  name = equites_t
  units = 5
  min_units = 5
  ln = 7
  max_squads = 6
  type = "cavalry"
  mounted = 1
  traits = [human_t]
  aligment = order_t
  size = 3
  train_rate = 2
  upkeep = 25
  resource_cost = 14
  food = 5
  pop = 3
  terrain_skills = [Burn, Raid]

  hp = 14
  mp = [4, 4]
  moves = 8
  resolve = 6
  global_skills = [BattleBrothers, PyreOfCorpses]

  dfs = 10
  res = 9
  hres = 4
  arm = 1
  armor = None
  shield = None

  weapon1 = weapons.LightLance
  att1 = 1
  weapon2 = weapons.Hoof
  att2 = 2
  off = 8
  strn = 12
  offensive_skills = [Charge]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favhill = [0]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t]



class Equites2(Human):
  name = feudal_knight_t
  units = 5
  sts = 2
  min_units = 5
  ln = 7
  max_squads = 6
  type = "cavalry"
  mounted = 1
  traits = [human_t]
  aligment = order_t
  size = 3
  train_rate = 2.5
  upkeep = 40
  resource_cost = 22
  food = 6
  pop = 4
  terrain_skills = [Burn, Raid]

  hp = 16
  mp = [3, 3]
  moves = 7
  resolve = 8
  global_skills = [BattleBrothers, Regroup]

  dfs = 8
  res = 10
  hres = 6
  arm = 2
  armor = HeavyArmor()

  weapon1 = weapons.Lance
  att1 = 1
  weapon2 = weapons.Sword
  att2 = 1
  off = 9
  strn = 11
  offensive_skills = [Charge]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t]



class Gryphon(Unit):
  name = "gryphon"
  units = 4
  min_units = 2
  ln = 5
  max_squads = 5
  type = "beast"
  traits = [gryphon_t]
  aligment = wild_t
  size = 4
  train_rate = 2.5
  upkeep = 50
  resource_cost = 20
  food = 4
  pop = 5
  terrain_skills = [DarkVision, Fly]

  hp = 14
  sight = 4
  mp = [4, 4]
  moves = 8
  resolve = 8
  global_skills = []

  dfs = 10
  res = 10
  hres = 3
  arm = 1
  armor = None

  weapon1 = weapons.Beak
  att1 = 1
  weapon2 = weapons.Talon
  att2 = 2
  off = 10
  strn = 12
  offensive_skills = [HeavyCharge]

  def __init__(self, nation):
    super().__init__(nation)



class GryphonRiders(Unit):
  name = "gryphon rider"
  units = 2
  min_units = 2
  ln = 5
  max_squads = 5
  type = "beast"
  mounted = 1
  traits = [human_t]
  aligment = sacred_t
  size = 4
  train_rate = 3
  upkeep = 80
  resource_cost = 22
  food = 6
  pop = 6
  terrain_skills = [Burn, DarkVision, Fly, Raid]

  hp = 24
  sight = 5
  mp = [2, 2]
  moves = 6
  resolve = 7
  global_skills = [ShadowHunter]

  dfs = 8
  res = 10
  hres = 5
  arm = 2
  armor = None

  weapon1 = weapons.Talon
  att1 = 1
  weapon2 = weapons.GreatSword
  att2 = 1
  off = 9
  strn = 12
  offensive_skills = [Charge]

  def __init__(self, nation):
    super().__init__(nation)



# Vampiros.
class CursedHamlet(City):
  name = cursed_hamlet_t
  traits = [death_t, malignant_t]
  events = [Starving, Looting, Reanimation, Revolt]
  food = 200
  food_rate = 60
  grouth = 50
  grouth_base = 0
  grouth_factor = 20
  grouth_min_bu = 12
  grouth_min_upg = 8
  income = 100
  public_order = 20
  initial_unrest = 5
  resource = 1
  upkeep = 600

  free_terrain = 1
  own_terrain = 0

  military_base = 40
  military_change = 50
  military_max = 70
  tags = [city_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [BoierLord, Levy, Settler2]
    # self.events = [i(self) for i in self.events]
    self.nation = nation
    self.pos = pos
    self.resource_cost = [100, 100]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [0, 1]

  def set_capital_bonus(self):
    self.food += 200
    # self.grouth += 100
    self.public_order += 10
    self.upkeep = 0

  def set_downgrade(self):
    msg = ""
    if self.level == 1 and self.pop <= 1700:
      logging.debug(f"{self} se degrada a {cursed_hamlet_t}.")
      self.level = 0
      self.name = cursed_hamlet_t
      self.food -= 0.5
      self.grouth_base -= 2.5
      # self.public_order -= 10
    if self.level == 2 and self.pop <= 6000:
      logging.debug(f"{self} se degrada a {village_t}.")
      self.level = 1
      self.name = village_t
      self.food -= 0.5
      self.grouth_base -= 2.5
      # self.public_order -= 10
    if self.level == 3 and self.pop <= 16000:
      logging.debug(f"{self} se degrada a {town_t}.")
      self.level = 2
      self.name = town_t
      self.food -= 0.5
      self.grouth_base -= 2.5
      # self.public_order -= 10
    if msg:
      logging.debug(msg)
      if self.nation.show_info:
        sp.speak(msg, 1)
        sleep(loadsound("notify18"))

  def set_upgrade(self):
    msg = ""
    if self.level == 0 and self.pop >= 2000:
      msg = f"{self} mejor a {village_t}."
      self.level = 1
      self.name = cursed_village_t
      self.food += 1
      self.grouth_base += 2.5
      # self.public_order += 10
    if self.level == 1 and self.pop >= 7000:
      msg = f"{self} mejor a {village_t}."
      self.level = 1
      self.name = town_t
      self.food += 1
      self.grouth_base += 2.5
      # self.public_order += 10
    if self.level == 2 and self.pop >= 18000:
      msg = f"{self} mejor a {city_t}."
      self.level = 3
      self.name = city_t
      self.food += 0.5
      self.grouth_base += 2.5
      # self.public_order += 10
    if msg:
      logging.debug(msg)
      if self.nation.show_info:
        sp.speak(msg, 1)
        sleep(loadsound("notify14"))



class Necropolis(Building):
  name = "necropolis"
  level = 1
  city_unique = 1
  size = 6
  gold = 5000
  own_terrain = 1
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Skeleton, Ghoul]
    self.resource_cost = [0, 30]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [none_t]
    self.hill = [0]
    self.upgrade = [Crypts]



class Crypts(Necropolis, Building):
  name = "campo de sangre"
  level = 2
  base = Necropolis
  gold = 10000
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [CryptHorror, Vampire, VarGhul]
    self.resource_cost = [0, 56]
    self.size = 0
    self.upgrade = [Mausoleum]



class Mausoleum(Crypts, Building):
  name = "mausoleo"
  level = 3
  base = Necropolis
  gold = 15000
  public_order = 20
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [GraveGuard, VampireCount]
    self.resource_cost = [0, 90]
    self.size = 0
    self.upgrade = [CourtOfBlood]



class CourtOfBlood(Mausoleum, Building):
  name = "corte oscura"
  level = 4
  base = Necropolis
  gold = 25000
  public_order = 50

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [BloodKnight, VladDracul]
    self.resource_cost = [0, 129]
    self.size = 0
    self.upgrade = []



class HallsOfTheDead (Building):
  name = "sala de los muertos"
  level = 1
  city_unique = 1
  size = 4
  gold = 7000
  own_terrain = 1
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Adjule, Paznic, Zombie]
    self.resource_cost = [0, 40]
    self.hill = [0, 1]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.upgrade = [SummoningCircle]



class SummoningCircle(HallsOfTheDead, Building):
  name = summoning_field_t
  level = 2
  base = HallsOfTheDead
  gold = 12000

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [FellBat, BloodSkeleton]
    self.resource_cost = [0, 60]
    self.size = 0
    self.upgrade = [DarkMonolit]



class DarkMonolit(SummoningCircle, Building):
  name = "monolito oscuro"
  level = 3
  base = HallsOfTheDead
  gold = 20000
  own_terrain = 1
  public_order = 50

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [BlackKnight, ForgeMaster]
    self.resource_cost = [0, 120]
    self.size = 0
    self.upgrade = []



class HuntingGround(Building):
  name = hunting_ground_t
  level = 1
  city_unique = 1
  size = 6
  gold = 8000
  food = 50
  income = 50
  own_terrain = 1
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Bat, Wolf]
    self.resource_cost = [0, 60]
    self.surf = [forest_t]
    self.hill = [0]
    self.upgrade = [SinisterForest]



class SinisterForest(HuntingGround, Building):
  name = "bosque abyssal"
  level = 1
  base = HuntingGround
  gold = 14000
  income = 50

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [DireWolf, Vargheist, ]
    self.resource_cost = [0, 80]
    self.size = 0
    self.upgrade = []



class Gallows(Building):
  name = "Gallows"
  level = 1
  local_unique = 1
  size = 2
  gold = 3200
  public_order = 30
  own_terrain = 1
  tags = [unrest_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 30]
    self.soil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t, swamp_t]
    self.hill = [0, 1]
    self.upgrade = [ImpaledField]



class ImpaledField(Gallows, Building):
  name = "campo de empalados"
  level = 2
  base = Gallows
  gold = 5500
  public_order = 50
  tags = [unrest_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 40]
    self.size = 0
    self.upgrade = []



class Pit(Building):
  name = "fosa"
  level = 1
  local_unique = 1
  size = 5
  gold = 1200
  food = 50
  grouth = 100
  public_order = 30
  own_terrain = 1
  tags = [food_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 30]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [none_t]
    self.hill = [0]
    self.upgrade = [FuneraryDungeon]



class FuneraryDungeon(Pit, Building):
  name = "mazmorra funeraria"
  level = 2
  base = Pit
  gold = 3000
  food = 50
  grouth = 400
  income = 100
  public_order = 20
  resource = 2
  tags = [food_t, resource_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 50]
    self.size = 0
    self.upgrade = []



# Commanders.
class BoierLord(Unit):
  name = "boier lord"
  namelist = [romanian_name1, romanian_name2]
  units = 10
  sts = 2
  min_units = 10
  ln = 10
  max_squads = 1
  can_hire = 1
  leadership = 60
  type = "infantry"
  wizard = 1
  traits = [human_t]
  aligment = malignant_t
  size = 2
  train_rate = 2
  upkeep = 18
  resource_cost = 15
  food = 4
  pop = 4
  terrain_skills = [Burn, Raid]

  hp = 10
  sight = 5
  mp = [2, 2]
  moves = 6
  resolve = 8
  power = 3
  power_max = 3
  power_res = 2
  global_skills = [BloodLord, Furtive, Organization]

  dfs = 9
  res = 9
  hres = 2
  arm = 0
  armor = MediumArmor()
  shield = Shield()

  weapon1 = weapons.BroadSword
  att1 = 1
  off = 9
  strn = 9
  
  fear = 6
  lead_traits = [human_t, blood_drinker_t, ]
  lead_aligments = [malignant_t, wild_t, order_t]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [BloodSkeleton]
    self.spells = [RecruitLevy]
  def levelup(self):
    if self.xp >= 30 and self.level == 1:
      self.level = 2
      self.leadership += 5



class Paznic(Unit):
  name = "paznic"
  namelist = [romanian_name1, romanian_name2]
  units = 10
  sts = 2
  min_units = 10
  ln = 10
  max_squads = 1
  can_hire = 1
  leadership = 50
  poisonres = 1
  type = "infantry"
  wizard = 1
  traits = [human_t]
  aligment = malignant_t
  size = 2
  train_rate = 2
  upkeep = 28
  resource_cost = 15
  food = 4
  pop = 4
  terrain_skills = [Burn, Raid]

  hp = 10
  sight = 5
  mp = [2, 2]
  moves = 6
  resolve = 8
  power = 10
  power_max = 10
  power_res = 4
  global_skills = [Furtive, LordOfBones]

  dfs = 8
  res = 7
  hres = 2
  arm = 0
  armor = MediumArmor()
  shield = Shield()

  weapon1 = weapons.Staff
  att1 = 1
  off = 8
  strn = 8
  
  fear = 6
  lead_traits = [death_t, human_t, wolf_t]
  lead_aligments = [malignant_t, wild_t]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [BloodSkeleton]
  def levelup(self):
    if self.xp >= 30 and self.level == 1:
      self.level = 2
      self.leadership += 5



class ForgeMaster(Unit):
  name = "forge master"
  units = 10
  min_units = 1
  max_squads = 1
  can_hire = 1
  leadership = 120
  unique = 1
  type = "infantry"
  wizard = 1
  traits = [human_t]
  aligment = malignant_t
  size = 2
  unique = 1
  train_rate = 3
  upkeep = 33
  resource_cost = 25
  food = 4
  pop = 8
  terrain_skills = [DarkVision]

  hp = 30
  sight = 20
  mp = [2, 2]
  moves = 7
  resolve = 8
  power = 20
  power_max = 50
  power_res = 5
  global_skills = [Furtive, LordOfBones]

  dfs = 11
  res = 14
  hres = 4
  arm = 0
  armor = MediumArmor()
  shield = Shield()

  weapon = weapons.BroadSword
  att1 = 2
  off = 5
  strn = 112
  
  fear = 1
  lead_traits = [death_t, human_t]
  lead_aligment = [hell_t, malignant_t]
  pref_corpses = 1

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [RaiseBloodSkeleton, RaiseFellBat]
  def levelup(self):
    if self.xp >= 30 and self.level == 1:
      self.level = 2
      self.leadership += 5



class Necromancer(Human):
  name = necromancer_t
  namelist = [necromancer_name1]
  units = 10
  ln = 10
  min_units = 1
  max_squads = 1
  can_hire = 1
  leadership = 40
  type = "infantry"
  wizard = 1
  traits = [human_t]
  aligment = malignant_t
  size = 2
  train_rate = 2
  upkeep = 25
  resource_cost = 20
  food = 4
  pop = 6
  terrain_skills = []

  hp = 10
  mp = [2, 2]
  moves = 5
  resolve = 5
  power = 10
  power_max = 20
  power_res = 5
  global_skills = [ElusiveShadow, LordOfBones]

  dfs = 7
  res = 6
  hres = 1
  arm = 0
  armor = None
  shield = Shield()

  weapon1 = weapons.Staff
  att1 = 1
  off = 6
  strn = 4
  
  comon = 5
  fear = 6
  lead_traits = [human_t, death_t, blood_drinker_t]
  lead_aligments = [hell_t, malignant_t, wild_t]
  sort_chance = 100
  pref_corpses = 1

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [CryptHorror]
    self.spells = [CastWailingWinds, RaiseDead]
    self.favhill = [1]
    self.favsurf = [forest_t, swamp_t] 



class VampireCount(Undead):
  name = vampire_count_t
  namelist = [romanian_name1, romanian_name2]
  units = 1
  min_units = 1
  max_squads = 1
  can_hire = 1
  leadership = 80
  type = "beast"
  traits = [blood_drinker_t, vampire_t]
  aligment = malignant_t
  size = 2
  train_rate = 2.5
  upkeep = 300
  resource_cost = 25
  food = 0
  pop = 50
  terrain_skills = [DarkVision, ForestSurvival, MountainSurvival, NightSurvival]

  hp = 40
  hp_res = 5
  sight = 5
  power = 10
  power_max = 20
  power_res = 3
  mp = [2, 2]
  moves = 9
  resolve = 10
  global_skills = [DarkPresence, ElusiveShadow, FearAura, Helophobia, BloodLord, ChaliceOfBlood]

  dfs = 12
  res = 14
  hres = 6
  arm = 0
  armor = MediumArmor()

  weapon1 = weapons.GreatSword
  att1 = 2
  weapon2 = weapons.VampireBite
  att2 = 1
  off = 10
  strn = 14

  common = 5
  lead_traits = [human_t, blood_drinker_t, bat_t, vampire_t, wolf_t]
  lead_aligments = [hell_t, malignant_t, nature_t, wild_t]

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [BloodHeal, RecruitLevy]
    self.favhill = [0, 1]
    self.favsurf = [forest_t, none_t, swamp_t]
  def levelup(self):
    if self.xp >= 20 and self.level == 1:
      self.level = 2
      self.leadership += 5



class VarGhul(Undead):
  name = varghul_t
  namelist = [ghoul_name1]
  units = 1
  min_units = 1
  max_squads = 1
  ln = 1
  leadership = 40
  type = "beast"
  traits = [death_t, blood_drinker_t]
  aligment = malignant_t
  size = 3
  train_rate = 3
  upkeep = 30
  resource_cost = 18
  food = 5
  pop = 6
  terrain_skills = [DarkVision, NightSurvival]

  hp = 35
  mp = [2, 2]
  moves = 5
  resolve = 5
  global_skills = [BloodLord, NightFerocity, Scavenger, ]

  dfs = 8
  res = 11
  hres = 8
  arm = 2

  weapon1 = weapons.ImmenseClaws
  att1 = 2
  off = 8
  strn = 11

  common = 6
  fear = 2
  lead_traits = [human_t, blood_drinker_t]
  lead_aligments = [malignant_t, wild_t]
  populated = 1

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [CryptHorror]
    self.favhill = [0, 1]
    self.favsoil = [waste_t]
    self.favsurf = [forest_t, none_t, swamp_t]
    self.spells = [EatCorpses]
  def levelup(self):
    if self.xp >= 40 and self.level == 1:
      self.level = 2
      self.leadership += 5



class VladDracul(Undead):
  name = "Vlad Dracul"
  units = 1
  min_units = 1
  max_squads = 1
  can_hire = 1
  leadership = 160
  is_leader = 1
  unique = 1
  type = "beast"
  wizard = 1
  traits = [death_t, blood_drinker_t, vampire_t]
  aligment = malignant_t
  size = 2
  train_rate = 3
  upkeep = 666
  resource_cost = 50
  food = 0
  pop = 300
  terrain_skills = [DarkVision, Fly, ForestSurvival, MountainSurvival, NightSurvival]

  hp = 60
  hp_res = 9
  sight = 40
  power = 20
  power_max = 70
  power_res = 10
  mp = [2, 2]
  moves = 12
  resolve = 10
  global_skills = [DarkPresence, ElusiveShadow, FearAura, Helophobia, BloodLord, MastersEye]

  dfs = 15
  res = 16
  hres = 10
  arm = 3
  armor = None

  weapon1 = weapons.PosesedBlade
  att1 = 4
  weapon2 = weapons.VampireBite
  att2 = 2
  off = 14
  strn = 16

  lead_traits = [bat_t, blood_drinker_t, death_t, human_t, vampire_t, wolf_t]
  lead_aligments = [malignant_t, nature_t, order_t, wild_t]
  pref_corpses = 1

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [CastBloodRain, CastRainOfToads, Returning, SummonBloodKnight]  # , BloodStorm
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [forest_t, none_t]
    self.favhill = 0, 1
  def levelup(self):
    if self.xp >= 20 and self.level == 1:
      self.level = 2
      self.leadership += 5



# unidades.
class Adjule(Unit):
  name = "adjule"
  units = 10
  min_units = 5
  ln = 20
  max_squads = 5
  type = beast_t
  traits = [death_t]
  aligment = malignant_t
  size = 2
  train_rate = 2
  upkeep = 8
  resource_cost = 14
  food = 0
  pop = 0
  terrain_skills = [DarkVision, DesertSurvival, NightSurvival]

  hp = 16
  mp = [2, 2]
  moves = 5
  resolve = 10
  global_skills = [NightFerocity, Furtive, Regroup]

  dfs = 7
  res = 8
  hres = 5
  arm = 0
  armor = None

  weapon1 = weapons.Bite
  att1 = 1
  off = 8
  strn = 8

  fear = 0

  def __init__(self, nation):
    super().__init__(nation)
    Ground.__init__(self)
    self.favhill = [0]
    self.favsoil = [waste_t]
    self.favsurf = [none_t]



class WailingLady(Undead):
  # Pendiente: resolver el tema etéreo.
  name = wailinglady_t
  units = 1
  min_units = 1
  max_squads = 1
  ethereal = 1
  type = "infantry"
  traits = [death_t]
  aligment = hell_t
  size = 2
  train_rate = 2
  upkeep = 100
  resource_cost = 30
  food = 0
  pop = 0
  terrain_skills = [DarkVision, Fly, ]

  hp = 15
  mp = [2, 2]
  moves = 8
  resolve = 10
  global_skills = [ElusiveShadow, Ethereal, FearAura, NightFerocity]

  dfs = 7
  res = 14
  hres = 10
  arm = 0
  armor = None

  weapon1 = weapons.ScreenOfSorrow
  att1 = 1
  weapon2 = weapons.Skythe
  att2 = 1
  off = 9
  strn = 16

  common = 3

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Ghost]



class Bat(Unit):
  name = bat_t
  units = 40
  sts = 2
  min_units = 20
  ln = 40
  max_squads = 10
  poisonres = 1
  type = "beast"
  traits = [bat_t]
  aligment = nature_t
  size = 1
  train_rate = 1.5
  upkeep = 1
  resource_cost = 15
  food = 2
  pop = 0.5
  terrain_skills = [DarkVision, Fly, ForestSurvival, MountainSurvival, SwampSurvival]

  hp = 4
  sight = 2
  mp = [4, 4]
  moves = 4
  resolve = 3
  global_skills = [NightSurvival]

  dfs = 7
  res = 4
  hres = 1
  arm = 0
  armor = None

  weapon1 = weapons.Bite
  att1 = 2
  off = 6
  strn = 3

  common = 8
  fear = 6

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [FellBat]
    self.favhill = [1]
    self.favsurf = [forest_t]



class BlackKnight(Undead):
  name = black_knight_t
  units = 5
  min_units = 5
  ln = 7
  max_squads = 6
  type = "cavalry"
  mounted = 1
  traits = [death_t]
  aligment = malignant_t
  size = 3
  train_rate = 2
  upkeep = 30
  resource_cost = 18
  food = 0
  pop = 6.6
  terrain_skills = [DarkVision, Burn, NightSurvival]

  hp = 18
  mp = [4, 4]
  moves = 7
  resolve = 10
  global_skills = [FearAura, NightFerocity, NightSurvival]

  dfs = 10
  res = 11
  hres = 6
  arm = 1
  armor = HeavyArmor()

  weapon1 = weapons.Lance
  att1 = 1
  weapon2 = weapons.BroadSword
  att2 = 1
  off = 9
  strn = 12
  offensive_skills = [Charge]

  common = 6
  fear = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [BloodKnight]
    self.favhill = [0]
    self.favsoil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t]



class BloodKnight(Undead):
  name = blood_knight_t
  units = 2
  min_units = 2
  ln = 10
  max_squads = 20
  type = "infantry"
  traits = [death_t, blood_drinker_t]
  aligment = malignant_t
  size = 2
  train_rate = 2.5
  upkeep = 40
  resource_cost = 25
  food = 0
  pop = 8
  terrain_skills = [DarkVision, NightSurvival]

  hp = 20
  mp = [2, 2]
  moves = 7
  resolve = 10
  global_skills = [FearAura, NightFerocity]

  dfs = 10
  res = 12
  hres = 7
  arm = 1
  armor = HeavyArmor()
  shield = Shield()

  weapon1 = weapons.GreatSword
  att1 = 2
  weapon2 = weapons.BloodDrinker
  att2 = 1
  off = 11
  strn = 12

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Ghost]
    self.favhill = [0]
    self.favsoil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t]



class CryptHorror(Undead):
  name = crypt_horror_t
  units = 4
  min_units = 2
  ln = 5
  max_squads = 20
  type = "beast"
  traits = [death_t]
  aligment = malignant_t
  size = 4
  train_rate = 3
  upkeep = 20
  resource_cost = 18
  food = 0
  pop = 4
  terrain_skills = [DarkVision, Fly, NightSurvival]

  hp = 15
  mp = [2, 2]
  moves = 5
  resolve = 10
  global_skills = [FearAura, NightFerocity]

  dfs = 8
  res = 10
  hres = 6
  arm = 2
  armor = None

  weapon1 = weapons.ToxicClaw
  att1 = 2
  weapon2 = weapons.ToxicFangs
  att2 = 1
  off = 9
  strn = 10

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.other_skills = [Pestilence(self)]



class DireWolf(Undead):
  name = dire_wolf_t
  units = 4
  min_units = 2
  ln = 7
  max_squads = 20
  type = "beast"
  traits = [death_t, wolf_t]
  aligment = malignant_t
  size = 3
  train_rate = 2
  upkeep = 30
  resource_cost = 22
  food = 0
  pop = 5
  terrain_skills = [DarkVision, ForestSurvival, MountainSurvival, NightSurvival]

  hp = 24
  mp = [2, 2]
  moves = 6
  resolve = 10
  global_skills = [BloodyBeast, FearAura, NightFerocity]

  dfs = 8
  res = 11
  hres = 5
  arm = 2
  armor = None

  weapon1 = weapons.Claw
  att1 = 2
  weapon2 = weapons.Bite
  att2 = 1
  off = 8
  strn = 12

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [glacier_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class Draugr(Unit):
  name = "Draugr"
  units = 5
  min_units = 5
  ln = 5
  max_squads = 20
  type = "infantry"
  traits = [death_t, blood_drinker_t]
  aligment = malignant_t
  size = 4
  train_rate = 2
  upkeep = 20
  resource_cost = 18
  food = 2
  pop = 5
  terrain_skills = [DarkVision, Burn, ForestSurvival, MountainSurvival, Raid]

  hp = 22
  mp = [2, 2]
  power = 1
  power_max = 1
  power_res = 1
  moves = 6
  resolve = 7
  global_skills = [Scavenger, NightFerocity, Regroup]

  dfs = 8
  res = 10
  hres = 4
  arm = 2

  weapon1 = weapons.ToxicClaw
  att1 = 2
  weapon2 = weapons.Crush
  att2 = 1
  off = 7
  strn = 14

  pref_corpses = 1

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Ghost]
    Ground.__init__(self)
    self.spells = [EatCorpses]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, waste_t, tundra_t]
    self.favsurf = [none_t, forest_t, swamp_t]
    self.other_skills = [Pestilence(self)]



class FellBat(Undead):
  name = fell_bat_t
  units = 5
  min_units = 5
  ln = 15
  max_squads = 10
  type = beast_t
  traits = [death_t, bat_t, blood_drinker_t]
  aligment = malignant_t
  size = 2
  train_rate = 2
  upkeep = 20
  resource_cost = 16
  food = 0
  pop = 4
  terrain_skills = [DarkVision, Fly, ForestSurvival, MountainSurvival, SwampSurvival]

  hp = 8
  sight = 2
  mp = [4, 4]
  moves = 7
  resolve = 10
  global_skills = [ElusiveShadow, Fly, Helophobia, NightSurvival]

  dfs = 9
  res = 8
  hres = 4
  arm = 0

  weapon1 = weapons.Claw
  att1 = 2
  weapon2 = weapons.Bite
  att2 = 1
  off = 9
  strn = 9

  common = 5

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Ghost]
    self.favsurf = [forest_t]
    self.other_skills = [Pestilence(self)]



class Ghoul(Human):
  name = ghoul_t
  units = 20
  min_units = 10
  ln = 10
  max_squads = 5
  poisonres = 1
  type = "infantry"
  traits = [human_t, blood_drinker_t]
  aligment = malignant_t
  size = 2
  train_rate = 1.5
  upkeep = 6
  resource_cost = 11
  food = 2
  pop = 1.5
  terrain_skills = [Burn, DarkVision, ForestSurvival, MountainSurvival, Raid]

  hp = 11
  mp = [2, 2]
  power = 1
  power_max = 1
  power_res = 1
  moves = 6
  resolve = 5
  global_skills = [Furtive]

  dfs = 8
  res = 8
  hres = 4
  arm = 0
  armor = None

  weapon1 = weapons.ToxicClaw
  att1 = 2
  weapon2 = weapons.Bite
  att2 = 1
  off = 7
  strn = 8

  common = 10
  populated_land = 1
  pref_corpses = 1

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [EatCorpses]
    self.corpses = [Draugr]



class GraveGuard(Undead):
  name = grave_guard_t
  units = 5
  min_units = 5
  ln = 10
  max_squads = 8
  type = "infantry"
  traits = [death_t, ]
  aligment = malignant_t 
  size = 2
  train_rate = 2.5
  upkeep = 50
  resource_cost = 18
  food = 0
  pop = 6
  terrain_skills = [Burn, DarkVision, NightSurvival]

  hp = 25
  mp = [2, 2]
  moves = 5
  resolve = 10
  global_skills = [FearAura, NightFerocity]

  dfs = 8
  res = 10
  hres = 4
  arm = 2
  armor = HeavyArmor()
  shield = Shield()

  weapon1 = weapons.Spear
  att1 = 1
  off = 9
  strn = 12

  common = 5

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favsoil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t]



class Settler2(Human):
  name = "wallachian settler"
  units = 20
  min_units = 10
  ln = 10
  max_squads = 1
  settler = 1 
  type = "civil"
  traits = [human_t]
  size = 2
  aligment = order_t
  train_rate = 3.5
  upkeep = 20
  resource_cost = 30
  food = 5
  pop = 8
  terrain_skills = [DesertSurvival]

  hp = 3
  mp = [2, 2]
  moves = 3
  resolve = 2

  dfs = 5
  res = 4
  hres = 1
  arm = 0
  armor = None

  weapon1 = weapons.Fist
  att1 = 1
  off = 5
  strn = 4

  def __init__(self, nation):
    super().__init__(nation)
    self.buildings = [CursedHamlet]
    self.corpses = [Zombie]



class Skeleton(Undead):
  name = skeleton_t
  units = 10
  min_units = 10
  ln = 10
  max_squads = 10
  type = "infantry"
  will_less = 1
  traits = [death_t]
  aligment = malignant_t
  size = 2
  train_rate = 1.5
  upkeep = 1
  resource_cost = 10
  food = 0
  pop = 1.2
  terrain_skills = []

  hp = 13
  mp = [2, 2]
  moves = 4
  resolve = 10
  global_skills = [SkeletonLegion]

  dfs = 7
  res = 8
  hres = 4
  arm = 0

  weapon1 = weapons.Claw
  att1 = 1
  off = 7
  strn = 7

  common = 8
  fear = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Ghost]
    self.other_skills = [Pestilence(self)]



class BloodSkeleton(Undead):
  name = "blood skeleton"
  units = 10
  min_units = 10
  ln = 10
  max_squads = 10
  type = "infantry"
  will_less = 1
  traits = [death_t]
  aligment = malignant_t
  size = 2
  train_rate = 2
  upkeep = 8
  resource_cost = 14
  food = 0
  pop = 2
  terrain_skills = []

  hp = 18
  mp = [2, 2]
  moves = 5
  resolve = 10
  global_skills = [SkeletonLegion]

  dfs = 9
  res = 10
  hres = 8
  arm = 1

  weapon1 = weapons.RustSword
  att1 = 1
  off = 10
  strn = 9

  common = 8
  fear = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Ghost]
    self.other_skills = [Pestilence(self)]



class SpectralInfantry(Unit):
  name = "infantería espectral"
  units = 10
  min_units = 10
  ln = 15
  max_squads = 10
  type = "infantry"
  will_less = 1
  traits = [death_t]
  aligment = wild_t
  size = 2
  train_rate = 2.5
  upkeep = 15
  resource_cost = 15
  food = 0
  pop = 3.5
  terrain_skills = [Burn, DarkVision, Raid]

  hp = 13
  mp = [2, 2]
  moves = 6
  resolve = 10
  global_skills = []

  dfs = 8
  res = 11
  hres = 6
  arm = 0
  armor = MediumArmor()

  weapon1 = weapons.BronzeSpear
  att1 = 1
  off = 8
  strn = 12

  fear = 0

  common = 3

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Ghost]



class Vampire(Undead):
  name = vampire_t
  units = 5
  min_units = 1
  ln = 10
  max_squads = 20
  type = "beast"
  traits = [blood_drinker_t, vampire_t]
  aligment = malignant_t
  size = 2
  train_rate = 2
  upkeep = 30
  resource_cost = 25
  food = 0
  pop = 4
  terrain_skills = [DarkVision, ForestSurvival, MountainSurvival, NightSurvival]

  hp = 15
  sight = 5
  hp_res = 2
  mp = [2, 2]
  moves = 8
  resolve = 10
  global_skills = [ElusiveShadow, Helophobia, Fly, NightFerocity]

  dfs = 10
  res = 12
  hres = 8
  arm = 0
  armor = None

  weapon1 = weapons.Claw
  att1 = 2
  weapon2 = weapons.VampireBite
  att2 = 1
  off = 10
  strn = 10

  common = 5
  populated_land = 1

  def __init__(self, nation):
    super().__init__(nation)
    self.favhill = [0, 1]
    self.favsurf = [forest_t, none_t, swamp_t]
    self.corpses = [Ghost]



class Vargheist(Undead):
  name = "vargheist"
  units = 1
  min_units = 1
  ln = 7
  max_squads = 3
  type = "beast"
  traits = [blood_drinker_t, vampire_t]
  aligment = malignant_t
  size = 3
  train_rate = 2.5
  upkeep = 25
  resource_cost = 20
  food = 0
  pop = 15
  terrain_skills = [DarkVision, ForestSurvival, MountainSurvival]

  hp = 25
  hp_res = 4
  sight = 5
  mp = [2, 2]
  moves = 9
  resolve = 10
  global_skills = [ElusiveShadow, FearAura, Fly, Helophobia, NightSurvival, TheBeast]

  dfs = 8
  res = 12
  hres = 8
  arm = 2

  weapon1 = weapons.VampireBite
  att1 = 1
  weapon2 = weapons.Claw
  att2 = 2
  off = 12
  strn = 15

  fear = 6
  populated_land = 1

  common = 4

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Ghost] 
    self.favsurf = [forest_t, swamp_t]



class Zombie(Undead, Ground):
  name = zombie_t
  units = 20
  min_units = 10
  ln = 30
  max_squads = 20
  type = "infantry"
  will_less = 1
  traits = [death_t]
  aligment = malignant_t
  size = 2
  train_rate = 1.5
  upkeep = 1
  resource_cost = 10
  food = 0
  pop = 1.5

  hp = 13
  mp = [2, 2]
  moves = 3
  resolve = 10
  global_skills = [Spread]

  dfs = 5
  res = 8
  hres = 4
  arm = 0

  weapon1 = weapons.ZombieBite
  att1 = 1
  off = 7
  strn = 7
  offensive_skills = [Surrounded]

  fear = 0
  populated_land = 1
  sort_chance = 70

  common = 11

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Zombie]
  def levelup(self):
    if self.xp >= 10 and self.level == 1:
      self.level = 2
      self.name = "rotten zombie"
      self.res += 2
      self.other_skills += [Pestilence(self)]



# otros.
class Dock(Building):
  name = "dock"
  level = 1
  city_unique = 1
  size = 6
  gold = 4000
  grouth = 30
  income = 50
  food = 50
  own_terrain = 1
  tags = ["dock"]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Galley]
    self.resource_cost = [0, 50]
    self.citylevel = village_t
    self.soil = [grassland_t, plains_t, tundra_t, waste_t]
    self.surf = [none_t]
    self.hill = [0]
    self.around_coast = 1
    self.upgrade = []  



class Fields(Building):
  name = fields_t
  level = 1
  local_unique = 1
  size = 6
  gold = 1300
  food = 50
  grouth = 50
  income = 0
  # public_order = 20
  own_terrain = 1
  tags = [food_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 25]
    self.soil = [grassland_t, plains_t]
    self.surf = [none_t]
    self.hill = [0]
    self.upgrade = [SmallFarm]



class SmallFarm(Fields, Building):
  name = small_farm_t
  level = 2
  base = Fields
  gold = 3000
  food = 100
  grouth = 100
  income = 20
  # public_order = 10

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 80]
    self.size = 0
    self.upgrade = [Farm]



class Farm(SmallFarm, Building):
  name = farm_t
  base = SmallFarm
  gold = 7000
  food = 200
  grouth = 200
  # income = 100
  # public_order = 30

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 150]
    self.size = 0
    self.upgrade = []



class Fort(City):
  defense_terrain = 1
  food = 100
  free_terrain = 1
  income = 0
  military_base = 30
  military_change = 50
  military_max = 50
  name = fort_t
  own_terrain = 0
  resource_cost = 100
  size = 8
  tags = [city_t]
  public_order = 50

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [250, 250]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [none_t]
    self.hill = [0, 1]



class Market(Building):
  name = "market"
  level = 1
  gold = 200
  food = 25
  income = 20
  resource_cost = 50
  tags = [food_t, income_t, rest_t]



class Quarry(Building):
  name = "quarry 1"
  level = 1
  local_unique = 1
  size = 6
  gold = 3500
  food = 30
  grouth = 20
  income = 50
  resource = 100
  own_terrain = 1
  tags = [resource_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 80]
    self.soil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [1]
    self.upgrade = [Quarry2]



class Quarry2(Quarry, Building):
  name = "quarry 2"
  base = Quarry
  level = 2
  local_unique = 1
  size = 6
  gold = 7000
  food = 75
  grouth = 40
  income = 100
  resource = 200
  own_terrain = 1
  tags = [resource_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 80]
    self.soil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [1]
    self.upgrade = []



class SawMill(Building):
  name = "sawmill 1"
  level = 1
  local_unique = 1
  size = 4
  gold = 2000
  food = 30
  grouth = 20
  income = 30
  resource = 50
  own_terrain = 1
  tags = [resource_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 50]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t]
    self.hill = [0, 1]
    self.upgrade = [SawMill2]



class SawMill2(SawMill, Building):
  name = "sawmill 2"
  base = SawMill
  level = 1
  local_unique = 1
  size = 4
  gold = 4300
  food = 65
  grouth = 50
  income = 100
  resource = 100
  own_terrain = 1
  tags = [resource_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 60]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t]
    self.hill = [0, 1]
    self.upgrade = []



class SlaveMarket(Building):
  name = "mercado de esclavos"
  level = 1
  city_unique = 1
  size = 4
  gold = 8000
  income = 50
  resource = 1
  own_terrain = 1
  tags = [market_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 30]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, swamp_t]
    self.hill = [0]



# Naciones.
class HolyEmpire(Nation):
  name = holy_empire_t
  nick = nation_phrase1_t
  traits = [human_t, sacred_t]
  capital_pop_bonus = 100
  expansion = 1000
  gold = 10000
  grouth_base = 4
  grouth_rate = 1
  main_pop_hill = [0]
  main_pop_soil = [grassland_t, plains_t]
  main_pop_surf = [none_t]
  military_limit_upgrades = 3000
  public_order = 0
  tile_cost = 600
  upkeep_base = 70
  upkeep_change = 200

  attack_factor = 200
  capture_rate = 150
  commander_rate = 7
  explore_range = 3
  scout_factor = 8
  stalk_rate = 100

  city_req_pop_base = 800
  # commander_rate = 10
  pop_limit = 60
  units_wild_limit = 20
  units_fly_limit = 20
  units_human_limit = 100
  units_melee_limit = 100
  units_mounted_limit = 20
  units_piercing_limit = 50
  units_ranged_limit = 30
  units_sacred_limit = 20
  units_undead_limit = 30

  def __init__(self):
    super().__init__()
    # City names.
    self.city_names = holy_empire_citynames
    # Casilla inicial permitida.
    self.hill = [0]
    self.soil = [plains_t, grassland_t]
    self.surf = [none_t]
    # Terrenos adyacentes permitidos
    self.min_around_grassland = 4
    self.min_around_plains = 0
    # terrenos adyacentes no permitidos.
    self.max_around_forest = 2
    self.max_around_ocean = 2 
    self.max_around_swamp = 1
    self.max_around_tundra = 0
    self.max_around_glacier = 0
    # All terrains.
    self.all_terrains = [waste_t, grassland_t, plains_t, tundra_t]
    # Non starting tiles.
    self.generic_soil = [grassland_t, plains_t, tundra_t, waste_t]
    self.generic_surf = [None]
    self.generic_hill = [0]

    # edificios iniciales disponibles.
    self.av_buildings = [Fields, PlaceOfProphecy, Pastures, TrainingCamp, SawMill, Quarry]
    # Cities.
    self.av_cities = [Hamlet]
  
    # terrenos de comida.
    self.for_food.soil = [grassland_t, plains_t]
    self.for_food.surf = [none_t]
    self.for_food.hill = [0]
    # terrenos de recursos.
    self.for_res.soil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.for_res.surf = [2]
    self.for_res.hill = [0, 1]
  
    # Population types.
    self.population_type = [Peasant(self)]
    # Rebels.
    self.units_rebels = [Archer, Hunter, Raider, Rider, Warrior]
    # initial placement.
    self.initial_placement = Hamlet
    # initial settler.
    self.initial_settler = Settler 
    # Unidades iniciales.
    self.start_units = [Decarion, PeasantLevy, PeasantLevy, PeasantLevy]



class WoodElves(Nation):
  name = wood_elves_t
  nick = ""
  traits = [elf_t, wild_t]
  capital_pop_bonus = 140
  expansion = 2500
  gold = 10000
  food_limit_builds = 3000
  food_limit_upgrades = 5000
  grouth_base = 2
  grouth_rate = 1
  main_pop_hill = [0]
  main_pop_soil = [grassland_t, plains_t, tundra_t]
  main_pop_surf = [forest_t]
  military_limit_upgrades = 1000
  public_order = 0
  upkeep_base = 70
  upkeep_change = 500

  attack_factor = 200
  capture_rate = 150
  commander_rate = 8
  explore_range = 3
  scout_factor = 5
  stalk_rate = 150

  city_req_pop_base = 1000
  # commander_rate = 7
  pop_limit = 30
  units_wild_limit = 100
  units_fly_limit = 40
  units_human_limit = 100
  units_melee_limit = 100
  units_mounted_limit = 20
  units_piercing_limit = 50
  units_ranged_limit = 60
  units_sacred_limit = 50
  units_undead_limit = 20

  def __init__(self):
    super().__init__()
    # City names.
    self.city_names = elven_citynames
    # Casilla inicial permitida.
    self.hill = [0]
    self.soil = [plains_t, grassland_t]
    self.surf = [forest_t]
    # Terrenos adyacentes permitidos
    self.min_around_forest = 5
    # terrenos adyacentes no permitidos.
    self.max_around_ocean = 0 
    self.max_around_swamp = 0
    # All terrains.
    self.all_terrains = [grassland_t, plains_t, tundra_t]
    # Non starting tiles.
    self.generic_soil = [grassland_t, plains_t, tundra_t]
    self.generic_surf = [forest_t, none_t]
    self.generic_hill = [0]

    # edificios iniciales disponibles.
    self.av_buildings = [CraftmensTree, FalconRefuge, GlisteningPastures, Grove, Sanctuary, StoneCarvers]
    # Cities.
    self.av_cities = [Hall]
  
    # terrenos de comida.
    self.for_food_soil = [grassland_t, plains_t]
    self.for_food.surf = [none_t]
    self.for_food.hill = [0]
    # terrenos de recursos.
    self.for_res.soil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.for_res.surf = [2]
    self.for_res.hill = [0, 1]
    
    # Population types.
    self.population_type = [ForestGuard(self), Huntress(self)]
    # rebeldes.
    self.units_rebels = [Huntress, Hunter, ForestGuard, Warrior]
    # initial placement.
    self.initial_placement = Hall
    # initial settler.
    self.initial_settler = ElvesSettler
    # initial units.
    self.start_units = [ForestGuard, ForestGuard, ForestGuard, PathFinder]



class Valahia(Nation):
  name = valahia_t
  nick = nation_phrase2_t
  traits = [blood_drinker_t, death_t, vampire_t]
  capital_pop_bonus = 120
  expansion = 1500
  gold = 10000
  food_limit_builds = 3000
  food_limit_upgrades = 4000
  grouth_base = 4
  grouth_rate = 1
  main_pop_hill = [0, 1]
  main_pop_soil = [grassland_t, plains_t, tundra_t]
  main_pop_surf = [none_t, forest_t]
  military_limit_upgrades = 3000
  public_order = 0
  upkeep_base = 70
  upkeep_change = 200

  attack_factor = 150
  capture_rate = 200
  # commander_rate = 6
  explore_range = 5
  scout_factor = 15
  stalk_rate = 80
  
  city_req_pop_base = 600
  # commander_rate = 10
  pop_limit = 50
  units_wild_limit = 100
  units_fly_limit = 40
  units_human_limit = 20
  units_melee_limit = 100
  units_mounted_limit = 30
  units_piercing_limit = 100
  units_ranged_limit = 20
  units_sacred_limit = 20
  units_undead_limit = 100

  def __init__(self):
    super().__init__()
    # Start tile
    self.hill = [1]
    self.soil = [grassland_t, plains_t, waste_t]
    self.surf = [forest_t, none_t]
    # Minimum terrain request. 
    self.min_around_plains = 2
    self.min_around_forest = 1
    # self.min_around_hill = 1
    # Maximum aroundterrain request.
    self.max_around_ocean = 0
    # self.max_around_waste = 2
    self.max_around_hill = 2
    # All terrains.
    self.all_terrains = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    # Non starting tiles.
    self.generic_soil = [grassland_t, plains_t, tundra_t, waste_t]
    self.generic_surf = [forest_t, none_t]
    self.generic_hill = [0, 1]

    # edificios iniciales disponibles.
    self.av_buildings = [Necropolis, Fields, HallsOfTheDead, HuntingGround, Gallows, Pit, Quarry, SawMill]
    # Cities.
    self.av_cities = [CursedHamlet]
    # City names.
    self.city_names = death_citynames

    # terrenos de comida.
    self.for_food.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.for_food.surf = [none_t]
    self.for_food.hill = [0]
    # terrenos de recursos.
    self.for_res.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.for_res.surf = [none_t, forest_t]
    self.for_res.hill = [0, 1]
    # Population types.
    self.population_type = [Slave(self)]
    
    # rebeldes.
    self.units_rebels = [Archer, Raider, Rider, Ghoul, VarGhul]
    # initial placement.
    self.initial_placement = CursedHamlet
    # initial settler.
    self.initial_settler = Settler2
    # Unidades iniciales.
    self.start_units = [BoierLord, Levy, Levy, Levy, ]



# Buildings.
class BrigandLair(Building):
  name = "brigand lair"
  nation = wild_t
  level = 1
  city_unique = 1
  size = 3
  stealth = 14
  common = 10
  gold = 4000
  unrest = 4
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Raider, WarlockApprentice]
    self.resource_cost = [0, 20]
    self.soil = [grassland_t, plains_t, tundra_t, waste_t, ]
    self.surf = [forest_t, none_t, swamp_t]
    self.hill = [0, 1]
    self.upgrade = []



class Campment(Building):
  name = "campment"
  nation = order_t
  level = 1
  city_unique = 1
  size = 4
  stealth = 15
  common = 8
  gold = 7000
  unrest = 2
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Archer, Rider, Warrior, Warlord]
    self.resource_cost = [0, 40]
    self.soil = [grassland_t, plains_t]
    self.surf = [forest_t , none_t]
    self.hill = [0]
    self.upgrade = []



class CaveOfDarkRites(Building):
  name = "cave of dark rites"
  nation = hell_t
  level = 1
  city_unique = 1
  size = 4
  stealth = 20
  common = 5
  gold = 7000
  unrest = 1
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Harpy, Satyr, Witch]
    self.resource_cost = [0, 40]
    self.soil = [grassland_t, plains_t, tundra_t, waste_t, ]
    self.surf = [forest_t]
    self.hill = [1]
    self.upgrade = []



class CaveOfGhouls(Building):
  name = "cave of ghouls"
  nation = malignant_t
  level = 1
  city_unique = 1
  size = 4
  stealth = 19
  common = 10 
  gold = 6000
  unrest = 2
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Ghoul, VarGhul]
    self.resource_cost = [0, 50]
    self.soil = [grassland_t, plains_t, waste_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [1]
    self.upgrade = []



class DececratedCemetery(Building):
  name = "dececrated cemetery"
  nation = malignant_t
  level = 1
  city_unique = 1
  size = 6
  stealth = 18
  common = 8
  gold = 8000
  unrest = 2
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Skeleton, Ghoul, Necromancer]
    self.resource_cost = [0, 60]
    self.soil = [plains_t, tundra_t, waste_t]
    self.surf = [forest_t, none_t]
    self.hill = [0]
    self.upgrade = []



class FightingPit(Building):
  name = "fighting pit"
  nation = orcs_t
  level = 1
  city_unique = 1
  size = 4
  stealth = 14
  common = 12
  gold = 6000
  unrest = 2
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [OrcWarrior, OrcArcher, OrcCaptain]
    self.resource_cost = [0, 50]
    self.soil = [plains_t, tundra_t, waste_t, ]
    self.surf = [forest_t, none_t]
    self.hill = [0]
    self.upgrade = []



class GoblinLair(Building):
  name = "goblin lair"
  nation = orcs_t
  level = 1
  city_unique = 1
  size = 3
  stealth = 19
  common = 12
  gold = 4000
  unrest = 2
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Goblin, GoblinShaman, WolfRider]
    self.resource_cost = [0, 30]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, swamp_t]
    self.hill = [0, 1]
    self.upgrade = []



class HiddenForest(Building):
  name = "hidden forest"
  nation = wild_t
  level = 1
  city_unique = 1
  size = 5
  stealth = 20
  common = 5
  gold = 12000
  unrest = 0
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Akhlut, Warlock]
    self.resource_cost = [0, 60]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t]
    self.hill = [0, 1]
    self.upgrade = []



class HiddenTemple(Building):
  name = "hidden temple"
  nation = order_t
  level = 1
  city_unique = 1
  size = 5
  stealth = 18
  common = 8
  gold = 16000
  unrest = 5
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Flagellant, Inquisitor, Warrior]
    self.resource_cost = [0, 60]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [0, 1]
    self.upgrade = []



class HyenasLair(Building):
  name = "hyenas lair"
  nation = wild_t
  level = 1
  city_unique = 1
  size = 2
  stealth = 16
  common = 8
  gold = 2000
  unrest = 1
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Hyena]
    self.resource_cost = [0, 20]
    self.soil = [plains_t, waste_t, ]
    self.surf = [forest_t, none_t]
    self.hill = [0, 1]
    self.upgrade = []



class LizardsBog(Building):
  name = "lizards bog"
  nation = wild_t
  level = 1
  city_unique = 1
  size = 4
  stealth = 20
  common = 5
  gold = 5000
  unrest = 1
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [LizardMan, LizardManInfantry, ShamanOfTheLostTribe]
    self.resource_cost = [0, 60]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [swamp_t]
    self.hill = [0]
    self.upgrade = []



class MammotsCave(Building):
  name = "mammot's cave"
  nation = wild_t
  level = 1
  city_unique = 1
  size = 6
  stealth = 19
  common = 6 
  gold = 12000
  unrest = 2
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [BlizzardWarrior, GiantOfTheLostTribe, Mammot, ShamanOfTheWind]
    self.resource_cost = [0, 50]
    self.soil = [tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [0, 1]
    self.upgrade = []



class NecromancersLair(Building):
  name = "Necromancers Lair"
  nation = malignant_t
  level = 1
  city_unique = 1
  size = 4
  stealth = 20
  common = 5
  gold = 6000
  unrest = 3
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Abomination, Necromancer, Skeleton]
    self.resource_cost = [0, 40]
    self.soil = [plains_t, tundra_t, waste_t, ]
    self.surf = [forest_t, swamp_t]
    self.hill = [0, 1]
    self.upgrade = []



class OathStone(Building):
  name = "oath stone"
  nation = hell_t
  level = 1
  city_unique = 1
  size = 4
  stealth = 15
  common = 6
  gold = 8000
  unrest = 1
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [CannibalWarlord, Ogre, Troglodyte]
    self.resource_cost = [0, 35]
    self.soil = [grassland_t, plains_t, tundra_t, waste_t, ]
    self.surf = [none_t]
    self.hill = [1]
    self.upgrade = []



class OpulentCrypt(Building):
  name = "opulent crypt"
  nation = malignant_t
  level = 1
  city_unique = 1
  size = 4
  stealth = 22
  common = 3
  gold = 20000
  unrest = 2
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Vampire, VampireLord]
    self.resource_cost = [0, 50]
    self.soil = [plains_t, tundra_t, waste_t, ]
    self.surf = [forest_t , none_t]
    self.hill = [0, 1]
    self.upgrade = []



class StalagmiteCavern(Building):
  name = "Stalagmite Cavern"
  nation = order_t
  level = 1
  city_unique = 1
  size = 4
  stealth = 22
  common = 5
  gold = 10000
  unrest = 2
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [PaleOne, WetOne]
    self.resource_cost = [0, 50]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t , none_t]
    self.hill = [0]
    self.upgrade = []



class TroglodyteCave(Building):
  name = "troglodyte cave"
  nation = wild_t
  level = 1
  city_unique = 1
  size = 4
  stealth = 20
  common = 8
  gold = 12000
  unrest = 2
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Satyr, Witch]
    self.resource_cost = [0, 50]
    self.soil = [grassland_t, plains_t, tundra_t, waste_t]
    self.surf = [forest_t , none_t]
    self.hill = [0]
    self.upgrade = []



class TrollCave(Building):
  name = "troll cave"
  nation = orcs_t
  level = 1
  city_unique = 1
  size = 4
  stealth = 20
  common = 6
  gold = 12000
  unrest = 1
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Troll]
    self.resource_cost = [0, 60]
    self.soil = [grassland_t, plains_t, tundra_t, waste_t]
    self.surf = [none_t]
    self.hill = [1]
    self.upgrade = []



class UnderworldEntrance(Building):
  name = "underworld entrance"
  nation = hell_t
  level = 1
  city_unique = 1
  size = 6
  stealth = 24
  common = 3
  gold = 24000
  unrest = 5
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Ghost, HellHound, DevoutOfChaos, AncientWitch]
    self.resource_cost = [0, 80]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, swamp_t, none_t]
    self.hill = [0, 1]
    self.upgrade = []



class WisperingWoods(Building):
  name = "wispering woods"
  nation = wild_t
  level = 1
  city_unique = 1
  size = 5
  stealth = 22
  common = 4
  gold = 12000
  unrest = 1
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Driad, Druid, ForestBear, ForestGiant]
    self.resource_cost = [0, 60]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t]
    self.hill = [0]
    self.upgrade = []



class WargsCave(Building):
  name = "Warg cave"
  nation = wild_t
  level = 1
  city_unique = 1
  size = 3
  stealth = 18
  common = 8
  gold = 7000
  unrest = 3
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Warg]
    self.resource_cost = [0, 70]
    self.soil = [tundra_t]
    self.surf = [forest_t, none_t, swamp_t]
    self.hill = [0, 1]
    self.upgrade = []



class WolfLair(Building):
  name = "wolf lair"
  nation = nature_t
  level = 1
  city_unique = 1
  size = 2
  stealth = 18
  common = 10
  gold = 2000
  unrest = 2
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Wolf]
    self.resource_cost = [0, 20]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t]
    self.hill = [0]
    self.upgrade = []



# Commanders.
class AncientWitch(Unit):
  name = "ancient witch"
  namelist = [female_name1, surfname1]
  units = 5
  min_units = 5
  ln = 5
  max_squads = 1
  leadership = 50
  type = "infantry"
  wizard = 1
  traits = [human_t]
  aligment = wild_t
  size = 2
  train_rate = 3
  upkeep = 25
  resource_cost = 26
  food = 3
  pop = 20
  terrain_skills = [ForestSurvival, SwampSurvival]

  hp = 8
  mp = [2, 2]
  moves = 6
  power = 20
  power_max = 50
  power_res = 10
  resolve = 5
  global_skills = [Furtive]

  dfs = 7
  res = 5
  hres = 1
  arm = 0
  armor = None

  weapon1 = weapons.Staff
  att1 = 1
  off = 7
  strn = 5

  common = 6
  fear = 6
  lead_traits = [beast_t, human_t, blood_drinker_t, death_t]
  lead_aligments = [malignant_t, wild_t, nature_t]
  populated_land = 1
  sort_chance = 80

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [WailingLady]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, none_t]



class CannibalWarlord(Human):
  name = "canibal warlord"
  namelist = [male_name1 + romanian_name1, ]
  units = 10
  sts = 2
  min_units = 1
  ln = 10
  max_squads = 1
  can_hire = 1
  leadership = 60
  type = "infantry"
  traits = [human_t]
  aligment = hell_t
  size = 2
  train_rate = 2
  upkeep = 18
  resource_cost = 15
  food = 5
  pop = 3
  terrain_skills = []

  hp = 10
  power = 2
  power_max = 6
  power_res = 2
  mp = [2, 2]
  moves = 6
  resolve = 8
  global_skills = [LeadershipExceeded, Organization]

  dfs = 9
  res = 9
  hres = 4
  arm = 0
  armor = MediumArmor()
  shield = Shield()
  defensive_skills = []

  weapon1 = weapons.Sword
  att1 = 1
  off = 8
  strn = 19
  offensive_skills = []

  can_hire = 1
  common = 8
  lead_traits = [human_t]
  lead_aligments = [order_t, wild_t]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.spells = []
  def levelup(self):
    if self.xp >= 30 and self.level == 1:
      self.level = 2
      self.leadership += 5



class GoblinShaman(Human):
  name = "goblin shaman"
  namelist = [goblin_name1]
  units = 10
  sts = 4
  min_units = 10
  ln = 10
  max_squads = 1
  can_hire = 1
  leadership = 40
  type = "infantry"
  traits = [goblin_t]
  aligment = orcs_t
  size = 2
  train_rate = 2
  upkeep = 12
  resource_cost = 18
  food = 4
  pop = 3

  hp = 7
  mp = [2, 2]
  moves = 6
  resolve = 6
  global_skills = []  # grant night vision.

  dfs = 6
  res = 6
  hres = 1
  arm = 0
  armor = None
  shield = Shield()

  weapon1 = weapons.ShortBow
  att1 = 2
  weapon2 = weapons.Fist
  att2 = 1
  off = 5
  strn = 6
  offensive_skills = []

  common = 9
  lead_traits = [goblin_t]
  lead_aligments = [malignant_t, wild_t]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
  def levelup(self):
    if self.xp >= 40 and self.level == 1:
      self.level = 2
      self.leadership += 5



class Inquisitor(Human):
  name = inquisitors_t
  namelist = [praenomen, nomen]
  units = 10
  sts = 2
  min_units = 10
  ln = 10
  max_squads = 1
  can_hire = 1
  leadership = 40
  type = "infantry"
  traits = [human_t]
  aligment = sacred_t
  size = 2
  train_rate = 2
  upkeep = 20
  resource_cost = 22
  food = 4
  pop = 4

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 7
  global_skills = [Exaltation, Furtive]

  dfs = 8
  res = 7
  hres = 2
  arm = 0
  armor = LightArmor()
  shield = Shield()

  weapon1 = weapons.Sword
  att1 = 1
  off = 8
  strn = 6
  offensive_skills = [ShadowHunter]

  common = 8
  lead_traits = [human_t]
  lead_aligments = [order_t, sacred_t]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
  def levelup(self):
    if self.xp >= 30 and self.level == 1:
      self.level = 2
      self.leadership += 5



class OrcCaptain(Human):
  name = "orc captain"
  namelist = [orc_name1, orc_name2]
  units = 10
  sts = 2
  min_units = 10
  ln = 10
  max_squads = 1
  can_hire = 1
  leadership = 90
  type = "infantry"
  traits = [orc_t]
  aligment = malignant_t
  size = 2
  train_rate = 2
  upkeep = 14
  resource_cost = 15
  food = 5
  pop = 4
  terrain_skills = []

  hp = 10
  power = 2
  power_max = 6
  power_res = 2
  mp = [2, 2]
  moves = 6
  resolve = 8
  global_skills = [Organization]

  dfs = 9
  res = 10
  hres = 6
  arm = 0
  armor = MediumArmor()
  shield = Shield()
  defensive_skills = []

  weapon1 = weapons.GreatSword
  att1 = 1
  off = 9
  strn = 10
  offensive_skills = []

  can_hire = 1
  common = 9
  lead_traits = [orc_t]
  lead_aligments = [malignant_t]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.spells = []
  def levelup(self):
    if self.xp >= 30 and self.level == 1:
      self.level = 2
      self.leadership += 5



class ShamanOfTheLostTribe(Human):
  name = "shaman of the lost tribe"
  namelist = [aztec_name1]
  units = 10
  sts = 4
  min_units = 1
  ln = 10
  max_squads = 10
  leadership = 50
  type = "infantry"
  traits = [human_t]
  aligment = wild_t
  size = 2
  train_rate = 2
  upkeep = 15
  resource_cost = 18
  food = 3
  pop = 2
  terrain_skills = [ForestSurvival, MountainSurvival]

  hp = 10
  mp = [2, 2]
  moves = 5
  power = 10
  power_max = 20
  power_res = 10
  resolve = 7
  global_skills = [Furtive]

  dfs = 8
  res = 5
  hres = 1
  arm = 0

  weapon1 = weapons.Staff
  att1 = 1
  off = 7
  strn = 7

  fear = 6

  common = 7
  lead_traits = [bear_t, falcon_t, human_t, lizard_t, wolf_t]
  lead_aligments = [order_t, wild_t]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    Ground.__init__(self)
    self.favhill = [0, 1]
    self.favsoil = [tundra_t]
    self.favsurf = [forest_t, none_t, swamp_t]
    self.spells += [CastStorm, SummonGiantBears]
  def levelup(self):
    if self.xp >= 30 and self.level == 1:
      self.level = 2
      self.leadership += 5



class ShamanOfTheWind(Human):
  name = "shaman of the wind"
  namelist = [cold_name1]
  units = 10
  sts = 4
  min_units = 1
  ln = 10
  max_squads = 10
  leadership = 60
  type = "infantry"
  traits = [human_t]
  aligment = wild_t
  size = 2
  train_rate = 2
  upkeep = 15
  resource_cost = 18
  food = 3
  pop = 3
  terrain_skills = [ForestSurvival, MountainSurvival]

  hp = 10
  mp = [2, 2]
  moves = 5
  power = 10
  power_max = 20
  power_res = 10
  resolve = 7
  global_skills = [Furtive]

  dfs = 8
  res = 5
  hres = 1
  arm = 0

  weapon1 = weapons.Staff
  att1 = 1
  off = 7
  strn = 7

  common = 5
  fear = 6

  lead_traits = [bear_t, human_t, mammot_t, wolf_t]
  lead_aligments = [order_t, wild_t]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    Ground.__init__(self)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [tundra_t]
    self.favsurf = [forest_t, none_t, swamp_t]
    self.spells += [CastStorm, SummonGiantBears]
  def levelup(self):
    if self.xp >= 30 and self.level == 1:
      self.level = 2
      self.leadership += 5



class VampireLord(Undead):
  name = "vampire lord"
  namelist = [male_name1 + romanian_name1, surfname1 + romanian_name2]
  units = 1
  min_units = 1
  max_squads = 1
  can_hire = 1
  leadership = 50
  type = "beast"
  traits = [death_t, blood_drinker_t, vampire_t]
  aligment = malignant_t
  size = 2
  train_rate = 2
  upkeep = 300
  resource_cost = 20
  food = 0
  pop = 25
  terrain_skills = [DarkVision, ForestSurvival, MountainSurvival, NightSurvival]

  hp = 30
  hp_res = 5
  sight = 5
  power = 5
  power_max = 5
  power_res = 2
  mp = [2, 2]
  moves = 9
  resolve = 10
  global_skills = [ElusiveShadow, Helophobia, BloodLord]

  dfs = 11
  res = 12
  hres = 6
  arm = 0
  armor = MediumArmor()

  weapon1 = weapons.GreatSword
  att1 = 2
  weapon2 = weapons.VampireBite
  att2 = 1
  off = 11
  strn = 12

  common = 2
  lead_traits = [bat_t, blood_drinker_t, human_t, vampire_t, wolf_t]
  lead_aligments = [malignant_t, nature_t, wild_t]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.spells = [BloodHeal, RecruitLevy]
    self.favhill = [0, 1]
    self.favsurf = [forest_t, none_t]
  def levelup(self):
    if self.xp >= 20 and self.level == 1:
      self.level = 2
      self.leadership += 5



class WarlockApprentice(Unit):
  name = "warlock aprentice"
  namelist = [male_name1, surfname1]
  units = 5
  min_units = 10
  ln = 5
  max_squads = 1
  leadership = 20
  type = "infantry"
  traits = [human_t]
  aligment = wild_t
  size = 2
  train_rate = 1.5
  upkeep = 20
  resource_cost = 16
  food = 3
  pop = 4
  terrain_skills = []

  hp = 10
  mp = [2, 2]
  moves = 6
  power = 5
  power_max = 15
  power_res = 3
  resolve = 6
  global_skills = []

  dfs = 8
  res = 5
  hres = 1
  arm = 0
  armor = None

  weapon1 = weapons.Staff
  att1 = 1
  off = 8
  strn = 4

  common = 7
  fear = 5
  lead_traits = [beast_t, human_t, blood_drinker_t, death_t, wolf_t]
  lead_aligments = [malignant_t, death_t, wild_t, nature_t]
  populated_land = 1
  sort_chance = 80

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, none_t]
    self.spells += [Curse]
  def levelup(self):
    if self.xp >= 30 and self.level == 1:
      self.level = 2
      self.leadership += 5



class Warlock(Unit):
  name = "warlock"
  namelist = [barbarian_name1, surfname1]
  units = 5
  sts = 2
  min_units = 1
  ln = 5
  max_squads = 1
  can_hire = 1
  leadership = 40
  type = "infantry"
  wizard = 1
  traits = [human_t]
  aligment = wild_t
  size = 2
  train_rate = 2
  upkeep = 30
  resource_cost = 22
  food = 3
  pop = 6
  terrain_skills = [ForestSurvival, SwampSurvival, MountainSurvival]

  hp = 10
  mp = [2, 2]
  moves = 6
  power = 10
  power_max = 30
  power_res = 5
  resolve = 6
  global_skills = [Furtive]

  dfs = 9
  res = 6
  hres = 1
  arm = 0
  armor = None

  weapon1 = weapons.Staff
  att1 = 1
  off = 9
  strn = 6

  common = 4
  fear = 5
  lead_traits = [human_t, blood_drinker_t]
  lead_aligments = [death_t, wild_t, nature_t]
  populated_land = 1
  sort_chance = 80

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, none_t]
    self.spells = [Curse, SummonClayGolem, SummonWoodlandSpirit]
  def levelup(self):
    if self.xp >= 30 and self.level == 1:
      self.level = 2
      self.leadership += 5



class Warlord(Human):
  name = "warlord"
  namelist = [barbarian_name1, barbarian_name1 + surfname1]
  units = 10
  sts = 2
  min_units = 10
  ln = 10
  max_squads = 1
  can_hire = 1
  leadership = 60
  type = "infantry"
  traits = [human_t]
  aligment = wild_t
  size = 2
  train_rate = 2
  upkeep = 15
  resource_cost = 15
  food = 5
  pop = 4
  terrain_skills = []
  tags = ["commander"]

  hp = 10
  power = 2
  power_max = 6
  power_res = 2
  mp = [2, 2]
  moves = 6
  resolve = 8
  global_skills = [LeadershipExceeded, Organization]

  dfs = 9
  res = 9
  hres = 4
  arm = 0
  armor = MediumArmor()
  shield = Shield()
  defensive_skills = []

  weapon1 = weapons.GreatSword
  att1 = 1
  off = 9
  strn = 9
  offensive_skills = []

  can_hire = 1
  common = 8
  lead_traits = [human_t]
  lead_aligments = [order_t, wild_t]

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.mp = [2, 2]
    self.spells = [RecruitPeasants]
  def levelup(self):
    if self.xp >= 30 and self.level == 1:
      self.level = 2
      self.leadership += 5



class WarMonger(Human):
  name = "warmonger"
  units = 10
  sts = 2
  min_units = 1
  ln = 10
  max_squads = 1
  can_hire = 1
  leadership = 120
  type = "infantry"
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 2.5
  upkeep = 200
  resource_cost = 25
  food = 4
  pop = 4

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 7
  global_skills = [Furtive, Organization, Regroup]

  dfs = 8
  res = 8
  hres = 4
  arm = 0
  armor = LightArmor()

  weapon = weapons.Sword
  att1 = 1
  damage = 3
  off = 8
  pn = 0
  offensive_skills = [ShadowHunter]
  strn = 9

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
  def levelup(self):
    if self.xp >= 30 and self.level == 1:
      self.level = 2
      self.leadership += 5



class Witch(Unit):
  name = "witch"
  namelist = [female_name1, surfname1]
  units = 5
  min_units = 5
  ln = 5
  max_squads = 1
  leadership = 30
  type = "infantry"
  wizard = 1
  traits = [human_t]
  aligment = wild_t
  size = 2
  train_rate = 2
  upkeep = 25
  resource_cost = 22
  food = 3
  pop = 10
  terrain_skills = [ForestSurvival, SwampSurvival]

  hp = 8
  mp = [2, 2]
  moves = 6
  power = 10
  power_max = 30
  power_res = 5
  resolve = 5
  global_skills = [Furtive]

  dfs = 7
  res = 5
  hres = 1
  arm = 0
  armor = None

  weapon1 = weapons.Staff
  att1 = 1
  off = 7
  strn = 5

  common = 6
  fear = 6
  lead_traits = [beast_t, human_t, blood_drinker_t, death_t]
  lead_aligments = [malignant_t, death_t, wild_t, nature_t]
  populated_land = 1
  sort_chance = 80

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Harpy]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, none_t]
  def levelup(self):
    if self.xp >= 30 and self.level == 1:
      self.level = 2
      self.leadership += 5



# Units.
class Abomination(Unit):
  name = "abomination"
  units = 4
  min_units = 4
  ln = 5
  max_squads = 5
  poisonres = 1
  type = "beast"
  traits = [death_t]
  aligment = malignant_t
  size = 4
  train_rate = 3
  upkeep = 20
  resource_cost = 20
  food = 0
  pop = 5
  terrain_skills = []

  hp = 30
  mp = [2, 2]
  moves = 4
  resolve = 10

  dfs = 8
  res = 12
  hres = 8
  arm = 2
  armor = None

  weapon1 = weapons.ToxicClaw
  att1 = 1
  weapon2 = weapons.Crush
  att2 = 1
  off = 9
  strn = 15

  common = 4

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]
    self.other_skills = [Pestilence(self)]



class Archer(Human):
  name = archer_t
  units = 20
  min_units = 10
  max_squads = 5
  type = "infantry"
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 1.5
  upkeep = 6
  resource_cost = 11
  food = 3
  pop = 1.5
  terrain_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 5
  resolve = 4

  dfs = 6
  res = 7
  hres = 1
  arm = 0
  armor = None

  weapon1 = weapons.Bow
  att1 = 1
  weapon2 = weapons.Fist
  att2 = 1
  off = 4
  strn = 6
  offensive_skills = [Withdrawall]
  
  fear = 5
  populated_land = 1
  sort_chance = 70

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favhill = [1]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t, forest_t]



class Akhlut(Unit):
  name = "akhlut"
  units = 1
  min_units = 1
  ln = 5
  max_squads = 5
  type = "beast"
  traits = [beast_t]
  aligment = wild_t
  size = 3
  train_rate = 2.5
  upkeep = 60
  resource_cost = 28
  food = 12
  pop = 0
  terrain_skills = [DarkVision, ForestSurvival, MountainSurvival]

  hp = 20
  mp = [2, 2]
  moves = 7
  resolve = 8
  global_skills = [Furtive]

  dfs = 10
  res = 12
  hres = 8
  arm = 2
  armor = None

  weapon1 = weapons.Bite
  att1 = 1
  off = 10
  strn = 14

  fear = 2

  common = 3

  def __init__(self, nation):
    super().__init__(nation)
    Amphibian.__init__(self)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [tundra_t]
    self.favsurf = [forest_t, none_t, swamp_t]



class BlackOrc(Unit):
  name = "orco negro"
  units = 10
  min_units = 10
  ln = 7
  max_squads = 16
  type = "infantry"
  traits = [orc_t]
  aligment = malignant_t
  size = 3
  train_rate = 2.3
  upkeep = 25
  resource_cost = 20
  food = 6
  pop = 4
  terrain_skills = [Burn, DarkVision, Raid]

  hp = 18
  mp = [2, 2]
  moves = 6
  resolve = 8
  global_skills = [BloodyBeast]

  dfs = 8
  res = 12
  hres = 6
  arm = 2
  armor = HeavyArmor

  weapon1 = weapons.GreatSword
  att1 = 2
  off = 10
  strn = 10

  fear = 2
  populated_land = 1
  sort_chance = 70

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    Ground.__init__(self)
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t, forest_t]



class BlizzardWarrior(Human):
  name = "blizzard warrior"
  units = 20
  min_units = 10
  ln = 10
  max_squads = 10
  type = "infantry"
  traits = [human_t]
  aligment = wild_t
  size = 2
  train_rate = 1.5
  upkeep = 10
  resource_cost = 11
  food = 3
  pop = 2.5
  terrain_skills = [ColdResist, Burn, Raid]

  hp = 11
  mp = [2, 2]
  moves = 6
  resolve = 6
  global_skills = [PyreOfCorpses]

  dfs = 8
  res = 8
  hres = 2
  arm = 0
  armor = None

  weapon1 = weapons.BronzeAxe
  att1 = 2
  off = 8
  strn = 9

  common = 10
  fear = 5
  populated_land = 1
  sort_chance = 70

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, none_t]



class CannibalWarrior(Human):
  name = "cannibal warrior"
  units = 20
  min_units = 10
  ln = 10
  max_squads = 10
  type = "infantry"
  traits = [human_t]
  aligment = hell_t
  size = 2
  train_rate = 1.5
  upkeep = 5
  resource_cost = 10
  food = 2
  pop = 1.5
  terrain_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 6
  global_skills = [PyreOfCorpses]

  dfs = 8
  res = 9
  hres = 2
  arm = 0
  armor = None

  weapon1 = weapons.Sword
  att1 = 1
  off = 8
  strn = 9

  common = 10
  fear = 5
  populated_land = 1
  sort_chance = 70

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, none_t]



class Crocodile(Unit):
  name = crocodile_t
  units = 1
  min_units = 1
  ln = 7
  max_squads = 20
  type = "beast"
  traits = [crocodile_t]
  aligment = nature_t
  size = 2
  train_rate = 2
  upkeep = 15
  resource_cost = 20
  food = 2
  pop = 4
  terrain_skills = [DarkVision, SwampSurvival]

  hp = 15
  mp = [2, 2]
  moves = 6
  resolve = 4
  global_skills = [Ambushment, Furtive]

  dfs = 8
  res = 12
  hres = 5
  arm = 3
  armor = None

  weapon1 = weapons.Bite
  att1 = 1
  off = 8
  strn = 14

  fear = 2
  sort_chance = 100

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    Amphibian.__init__(self)
    self.favhill = [0]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [swamp_t]



class DeadBear(Unit):
  name = "dead bear"
  units = 4
  min_units = 4
  ln = 7
  max_squads = 5
  type = "beast"
  traits = [death_t, bear_t]
  aligment = malignant_t
  size = 3
  train_rate = 2
  upkeep = 5
  resource_cost = 15
  food = 0
  pop = 3
  terrain_skills = []

  hp = 24
  mp = [2, 2]
  moves = 4
  resolve = 10
  global_skills = []

  dfs = 5
  res = 14
  hres = 6
  arm = 1
  armor = None

  weapon1 = weapons.Claw
  att1 = 1
  weapon2 = weapons.Bite
  att2 = 1
  off = 8
  strn = 12

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class DesertNomad(Human):
  name = "ginete a camello"
  units = 20
  sts = 2
  min_units = 10
  ln = 10
  max_squads = 5
  mounted = 1
  type = "cavalry"
  traits = [human_t]
  aligment = wild_t
  size = 3
  train_rate = 1.5
  upkeep = 20
  resource_cost = 18
  food = 4
  pop = 1.5
  terrain_skills = [Burn, DesertSurvival, Raid]

  hp = 14
  sight = 2
  mp = [3, 3]
  moves = 6
  resolve = 5
  global_skills = [Undisciplined]

  dfs = 8
  res = 9
  hres = 3
  arm = 1
  armor = None
  shield = None

  weapon1 = weapons.ShortBow
  att1 = 1
  weapon2 = weapons.Hoof
  att2 = 2
  off = 4
  strn = 8
  offensive_skills = []
  
  fear = 3
  populated_land = 1
  sort_chance = 80

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favhill = [0]
    self.favsoil = [waste_t]
    self.favsurf = [none_t]



class DevourerOfDemons(Unit):
  name = "devorador de demonios"
  units = 1
  min_units = 1
  max_squads = 1
  type = "beast"
  traits = [spirit_t]
  aligment = wild_t
  size = 5
  train_rate = 2.5
  upkeep = 500
  resource_cost = 50
  food = 0
  pop = 0
  terrain_skills = [DarkVision, Fly, ForestSurvival, MountainSurvival, SwampSurvival]

  hp = 120
  hp_res = 5
  sight = 30
  mp = [2, 2]
  moves = 10
  resolve = 10
  global_skills = [Furtive, Ethereal, FearAura]

  dfs = 9
  res = 14
  hres = 8
  arm = 0
  armor = None

  weapon1 = weapons.SoulDrain
  att1 = 1
  off = 10
  strn = 15

  fear = 2
  populated_land = 1
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [forest_t, none_t, swamp_t]
    self.favhill = 0, 1



class DevoutOfChaos(Human):
  name = "devout of chaos"
  units = 10
  sts = 2
  min_units = 10
  ln = 15
  max_squads = 3
  type = "infantry"
  traits = [human_t]
  aligment = hell_t
  size = 2
  train_rate = 1.5
  upkeep = 30
  resource_cost = 20
  food = 3
  pop = 1.5
  terrain_skills = [Burn, ]

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 7
  global_skills = [ElusiveShadow]

  dfs = 9
  res = 8
  hres = 3
  arm = 0
  armor = None
  shield = Shield()

  weapon1 = weapons.Sword
  att1 = 1
  off = 9
  strn = 10
  
  fear = 6
  sort_chance = 100
  pref_corpses = 0

  common = 5

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [BlackKnight]
    self.spells = []
    self.favhill = [0, 1]
    self.favsurf = [forest_t] 



class Galley(Ship):
  name = "galera"
  units = 1
  min_units = 1
  max_squads = 5
  type = "veicle"
  gold = 130
  upkeep = 30
  resource_cost = 35
  food = 10
  pop = 30

  hp = 35
  mp = [2, 2]
  moves = 6
  resolve = 6

  dfs = 3
  res = 4
  arm = 0

  att1 = 1
  damage = 10
  off = 3
  strn = 3
  pn = 0
  
  cap = 60

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = []
    self.favhill = [0]
    self.favsoil = [coast_t]
    self.favsurf = [none_t]
    self.traits += ["ship", ]



class GiantBear(Unit):
  name = "oso gigante"
  units = 1
  min_units = 1
  ln = 5
  max_squads = 10
  type = "beast"
  traits = [bear_t]
  aligment = nature_t
  size = 4
  train_rate = 2.5
  upkeep = 30
  resource_cost = 26
  food = 8
  pop = 5
  terrain_skills = [ForestSurvival, MountainSurvival]

  hp = 30
  mp = [3, 3]
  moves = 5
  resolve = 8
  global_skills = [Undisciplined]

  dfs = 7
  res = 12
  hres = 6
  arm = 2
  armor = None

  weapon1 = weapons.Claw
  att1 = 1
  weapon2 = weapons.Bite
  att2 = 1
  off = 9
  strn = 14

  common = 6
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [GiantDeadBear]
    self.favhill = [0, 1]
    self.favsoil = [tundra_t]
    self.favsurf = [forest_t, none_t]



class GiantDeadBear(Unit):
  name = "giant dead bear"
  units = 1
  min_units = 1
  ln = 5
  max_squads = 10
  type = "beast"
  traits = [death_t, bear_t]
  aligment = malignant_t
  size = 4
  train_rate = 3
  upkeep = 15
  resource_cost = 30
  food = 0
  pop = 7
  terrain_skills = []

  hp = 40
  mp = [2, 2]
  moves = 3
  resolve = 10
  global_skills = [Pestilence]

  dfs = 5
  res = 12
  hres = 10
  arm = 2
  armor = None

  weapon1 = weapons.Claw
  att1 = 1
  weapon2 = weapons.Bite
  att2 = 1
  off = 9
  strn = 14

  common = 6
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [tundra_t]
    self.favsurf = [forest_t, none_t]



class GiantCrocodile(Unit):
  name = "giant crocodile"
  units = 1
  min_units = 1
  ln = 7
  max_squads = 10
  type = "beast"
  traits = [crocodile_t]
  aligment = nature_t
  size = 3
  train_rate = 2.5
  upkeep = 25
  resource_cost = 20
  food = 6
  pop = 6
  terrain_skills = [DarkVision, SwampSurvival]

  hp = 30
  mp = [2, 2]
  moves = 5
  resolve = 4
  global_skills = [Ambushment, Furtive]

  dfs = 7
  res = 13
  hres = 6
  arm = 5
  armor = None

  weapon1 = weapons.Bite
  att1 = 1
  off = 8
  strn = 15

  fear = 2
  sort_chance = 100

  def __init__(self, nation):
    super().__init__(nation)
    Amphibian.__init__(self)
    self.corpses = [Skeleton]
    self.favhill = [0]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [swamp_t]



class GiantOfTheLostTribe(Unit):
  name = "giant of the lost tribe"
  units = 4
  min_units = 4
  ln = 7
  max_squads = 10
  type = "beast"
  traits = [beast_t]
  aligment = wild_t
  size = 3
  train_rate = 3
  upkeep = 30
  resource_cost = 24
  food = 6
  pop = 4
  terrain_skills = [ColdResist, DarkVision, ForestSurvival, MountainSurvival]

  hp = 15
  sight = 2
  mp = [2, 2]
  moves = 5
  resolve = 7
  global_skills = []

  dfs = 8
  res = 12
  hres = 6
  arm = 2
  armor = None

  weapon1 = weapons.GreatClub
  att1 = 1
  att2 = weapons.Crush
  att2 = 1
  off = 9
  strn = 11
  
  common = 4
  fear = 4
  populated_land = 1
  sort_chance = 70

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Abomination]
    Ground.__init__(self)
    self.favhill = [0, 1]
    self.favsoil = [tundra_t]
    self.favsurf = [none_t, forest_t]



class GiantWolf(Unit):
  name = giant_wolf_t
  units = 5
  min_units = 5
  ln = 10
  max_squads = 6
  type = "beast"
  traits = [wolf_t]
  aligment = nature_t
  size = 3
  train_rate = 2.5
  upkeep = 30
  resource_cost = 18
  food = 6
  pop = 3
  terrain_skills = [DarkVision, ForestSurvival, MountainSurvival]

  hp = 13
  sight = 3
  mp = [2, 2]
  moves = 6
  resolve = 4
  global_skills = [BloodyBeast, Furtive, NightFerocity]

  dfs = 8
  res = 9
  hres = 4
  arm = 1
  armor = None

  weapon1 = weapons.Bite
  att1 = 1
  att2 = weapons.Claw
  att2 = 1
  off = 9
  strn = 10
  
  common = 6
  fear = 4
  populated_land = 1
  sort_chance = 70

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [DireWolf]
    Ground.__init__(self)
    self.favhill = [0, 1]
    self.favsoil = [tundra_t]
    self.favsurf = [none_t, forest_t]



class Ghost(Undead):
  name = "ghost"
  units = 5
  min_units = 5
  ln = 20
  max_squads = 6
  ethereal = 1
  type = "infantry"
  will_less = 1
  traits = [death_t]
  aligment = hell_t
  size = 2
  train_rate = 3
  upkeep = 10
  resource_cost = 20
  food = 0
  pop = 3
  terrain_skills = [DarkVision, Fly, MountainSurvival, ForestSurvival,
                    SwampSurvival]

  hp = 15
  mp = [2, 2]
  moves = 5
  resolve = 10
  global_skills = [ElusiveShadow, Ethereal, FearAura]

  dfs = 12
  res = 6
  hres = 6
  arm = 0
  armor = None

  weapon1 = weapons.Skythe
  att1 = 1
  off = 8
  strn = 12

  common = 7

  def __init__(self, nation):
    super().__init__(nation)



class Goblin(Unit):
  name = goblin_t
  units = 20
  sts = 4
  min_units = 20
  ln = 20
  max_squads = 10
  type = "infantry"
  traits = [goblin_t]
  aligment = orcs_t
  size = 1
  train_rate = 1.5
  upkeep = 4
  resource_cost = 12
  food = 2
  pop = 1.2
  terrain_skills = [Burn, ForestSurvival, MountainSurvival, SwampSurvival, Raid]

  hp = 6
  mp = [3, 3]
  moves = 8
  resolve = 4
  global_skills = [BloodyBeast, Furtive, Undisciplined]

  dfs = 10
  res = 6
  hres = 1
  arm = 0
  armor = None

  weapon1 = weapons.ShortBow
  att1 = 1
  weapon2 = weapons.Claw
  att2 = 1
  off = 4
  strn = 6
  offensive_skills = [Ambushment, Skirmisher] 
  
  fear = 3
  populated_land = 1
  sort_chance = 90

  common = 12

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    Ground.__init__(self)
    self.favsoil = [waste_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, swamp_t]
    self.favhill = [0, 1]



class ClayGolem(Unit):
  name = "clay golem"
  units = 5
  min_units = 1
  ln = 5
  max_squads = 5
  type = "beast"
  will_less = 1
  traits = [golem_t, ]
  aligment = wild_t
  size = 4
  train_rate = 3
  upkeep = 10
  resource_cost = 30
  food = 0
  pop = 0
  terrain_skills = []

  hp = 60
  mp = [2, 2]
  moves = 4
  resolve = 10
  global_skills = []

  dfs = 7
  res = 12
  hres = 12
  arm = 2
  armor = None

  weapon1 = weapons.Fist
  att1 = 1
  weapon2 = weapons.Crush
  att2 = 1
  off = 7
  strn = 10
  offensive_skills = [] 
  
  fear = 3
  populated_land = 0
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    Ground.__init__(self)
    self.favsoil = [waste_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, swamp_t]
    self.favhill = [0, 1]



class Harpy(Unit):
  name = harpy_t
  units = 20
  sts = 2
  ln = 20
  min_units = 10
  max_squads = 6
  poisonres = 1
  type = beast_t
  traits = [beast_t]
  aligment = malignant_t
  size = 2
  train_rate = 2.5
  upkeep = 6
  resource_cost = 16
  food = 0
  pop = 2
  terrain_skills = [Fly, ForestSurvival, MountainSurvival, Raid]

  hp = 13
  sight = 3
  mp = [4, 4]
  moves = 8
  resolve = 4
  global_skills = [Furtive]

  dfs = 10
  res = 7
  hres = 2
  arm = 1
  armor = None

  weapon1 = weapons.Talon
  att1 = 2
  off = 8
  strn = 8
  
  common = 7
  fear = 1
  populated_land = 1
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]    
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [forest_t, swamp_t]
    self.soil += [coast_t]



class HellHound(Undead):
  name = hellhound_t
  units = 2
  ln = 7
  min_units = 1
  max_squads = 5
  type = "beast"
  traits = [death_t]
  aligment = hell_t
  size = 3
  train_rate = 3
  upkeep = 30
  resource_cost = 30
  food = 0
  pop = 5
  terrain_skills = [DarkVision, DesertSurvival, ForestSurvival, MountainSurvival, NightSurvival]

  hp = 35
  hp_res = 4
  sight = 10
  mp = [2, 2]
  moves = 6
  resolve = 10
  global_skills = [BloodyBeast, ElusiveShadow, NightFerocity, Regroup]

  dfs = 8
  res = 12
  hres = 7
  arm = 2
  armor = None

  weapon1 = weapons.Bite
  att1 = 1
  weapon2 = weapons.Claw
  att2 = 1
  off = 9
  strn = 15
  
  fear = 2

  common = 4

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [plains_t, tundra_t, waste_t]



class Hyena(Unit):
  name = "hyena"
  units = 20
  sts = 4
  ln = 15
  min_units = 5
  max_squads = 12
  type = "beast"
  traits = [hyena_t]
  aligment = nature_t
  size = 2
  train_rate = 1.5
  upkeep = 15
  resource_cost = 15
  food = 4
  pop = 2
  terrain_skills = [DarkVision, NightSurvival]

  hp = 12
  sight = 2
  mp = [4, 4]
  moves = 6
  resolve = 4
  global_skills = [BloodyBeast, Furtive]

  dfs = 8
  res = 8
  hres = 2
  arm = 1
  armor = None

  weapon1 = weapons.Bite
  att1 = 1
  off = 8
  strn = 12
  
  common = 8
  fear = 5
  populated_land = 1
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [HellHound]
    Ground.__init__(self)
    self.favhill = [0]
    self.favsoil = [plains_t, waste_t]
    self.favsurf = [forest_t, none_t]



class Hunter(Human):
  name = hunter_t
  units = 10
  min_units = 10
  max_squads = 4
  type = "infantry"
  traits = [human_t]
  aligment = wild_t
  size = 2
  train_rate = 1.5
  upkeep = 6
  resource_cost = 12
  food = 3
  pop = 1.5
  terrain_skills = [ForestSurvival, MountainSurvival, Raid]

  hp = 10
  sight = 2
  mp = [2, 2]
  moves = 5
  resolve = 4
  global_skills = [Furtive, Undisciplined]

  dfs = 7
  res = 7
  hres = 1
  arm = 0
  armor = None

  weapon1 = weapons.ShortBow
  att1 = 1
  weapon2 = weapons.Fist
  att2 = 1
  off = 8
  strn = 9
  offensive_skills = [Ambushment, Skirmisher]

  common = 8
  fear = 6
  populated_land = 1
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class KillerMantis(Human):
  name = "killer mantis"
  units = 5
  min_units = 5
  ln = 7
  max_squads = 4
  type = "Beast"
  will_less = 1
  traits = [mantis_t]
  aligment = nature_t
  size = 3
  train_rate = 2
  upkeep = 20
  resource_cost = 15
  food = 5
  pop = 3
  terrain_skills = [ForestSurvival, MountainSurvival, SwampSurvival]

  hp = 16
  sight = 2
  mp = [2, 2]
  moves = 8
  resolve = 4
  global_skills = [Furtive, Undisciplined]

  dfs = 10
  res = 8
  hres = 2
  arm = 0
  armor = None

  weapon1 = weapons.MantisClaw
  att1 = 2
  off = 10
  strn = 9

  common = 5
  fear = 6
  populated_land = 1
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class NomadsRider(Human):
  name = nomads_rider_t
  units = 20
  min_units = 10
  ln = 7
  max_squads = 6
  mounted = 1
  type = "cavalry"
  traits = [human_t]
  aligment = order_t
  size = 3
  train_rate = 2.5
  upkeep = 25
  resource_cost = 25
  food = 5
  pop = 3
  terrain_skills = [Burn, Raid]

  hp = 14
  mp = [4, 4]
  moves = 6
  resolve = 4
  global_skill = [Undisciplined]

  dfs = 8
  res = 9
  hres = 2
  arm = 1
  armor = None

  weapon1 = weapons.Bow
  att1 = 1
  weapon2 = weapons.Hoof
  att2 = 2
  off = 4
  offensive_skills = [Skirmisher, Withdrawall]
  strn = 11

  common = 7
  fear = 3
  populated_land = 1
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favhill = [0]
    self.favsoil = [plains_t, grassland_t, tundra_t]
    self.favsurf = [none_t]



class OrcArcher(Unit):
  name = orc_archer_t
  units = 30
  sts = 2
  min_units = 10
  max_squads = 10
  type = "infantry"
  traits = [orc_t]
  aligment = malignant_t
  size = 2
  train_rate = 1.3
  upkeep = 10
  resource_cost = 12
  food = 3
  pop = 2
  terrain_skills = [Burn, DarkVision, ForestSurvival, MountainSurvival, Raid]

  hp = 12
  mp = [2, 2]
  moves = 5
  resolve = 4
  global_skills = [BloodyBeast, Undisciplined]

  dfs = 7
  res = 9
  hres = 4
  arm = 1
  armor = None

  weapon1 = weapons.Bow
  att1 = 1
  att2 = weapons.Fist
  att2 = 1
  off = 3
  strn = 8
  offensive_skills = [Ambushment, Skirmisher, Withdrawall]
  
  common = 10
  fear = 4
  populated_land = 1
  sort_chance = 80

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    Ground.__init__(self)
    self.favhill = [1]    
    self.favsoil = [waste_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t, forest_t]



class OrcWarrior(Unit):
  name = "orc warriors"
  units = 20
  sts = 4
  min_units = 10
  ln = 15
  max_squads = 10
  type = "infantry"
  traits = [orc_t]
  aligment = malignant_t
  size = 2
  train_rate = 1.3
  upkeep = 7
  resource_cost = 10
  food = 3
  pop = 1.5
  terrain_skills = [Burn, DarkVision, ForestSurvival, MountainSurvival, Raid]

  hp = 12
  mp = [2, 2]
  moves = 6
  resolve = 4
  global_skills = [BloodyBeast, Undisciplined]

  dfs = 8
  res = 10
  hres = 5
  arm = 1
  armor = None

  weapon1 = weapons.Sword
  att1 = 1
  off = 7
  strn = 10
  
  common = 12
  fear = 4
  populated_land = 1
  sort_chance = 80

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    Ground.__init__(self)
    self.favsoil = [waste_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t, forest_t]
    self.traits += [orc_t]



class Levy(Human):
  name = levy_t
  units = 20
  sts = 2
  min_units = 10
  ln = 15
  max_squads = 10
  levy = 1
  type = "infantry"
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 1.3
  upkeep = 4
  resource_cost = 11
  food = 2
  pop = 1.3
  terrain_skills = [Burn, PyreOfCorpses, Raid]

  hp = 10
  mp = [2, 2]
  moves = 5
  resolve = 5
  global_skills = [Undisciplined]

  dfs = 7
  res = 9
  hres = 3
  arm = 0
  armor = None
  shield = Shield()

  weapon1 = weapons.BronzeSpear
  att1 = 1
  off = 7
  strn = 8

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t]
    self.favhill = [0]



class LizardMan(Human):
  name = "lizardman"
  units = 20
  min_units = 10
  ln = 10
  max_squads = 10
  poisonres = 1
  type = "infantry"
  traits = [lizard_t]
  aligment = order_t
  size = 2
  train_rate = 1.5
  upkeep = 10
  resource_cost = 8
  food = 2
  pop = 2
  terrain_skills = [Burn, DarkVision, Raid, SwampSurvival]

  hp = 12
  mp = [2, 2]
  moves = 7
  resolve = 4
  global_skills = []

  dfs = 9
  res = 8
  hres = 2
  arm = 2
  armor = None
  shield = None

  weapon1 = weapons.Bite
  att1 = 1
  weapon2 = weapons.Claw
  att2 = 4
  off = 8
  strn = 10

  common = 8
  fear = 5
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.other_skills = [Miasma(self)]
    self.favhill = [0]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [swamp_t]



class LizardManInfantry(Human):
  name = "lizardman heavy infantry"
  units = 20
  sts = 2
  min_units = 10
  ln = 10
  max_squads = 6
  poisonres = 1
  type = "infantry"
  traits = [lizard_t]
  aligment = order_t
  size = 2
  train_rate = 2
  upkeep = 18
  resource_cost = 18
  food = 2
  pop = 3
  terrain_skills = [Burn, DarkVision, Raid, SwampSurvival]

  hp = 12
  mp = [2, 2]
  moves = 6
  resolve = 6
  global_skills = []

  dfs = 10
  res = 9
  hres = 2
  arm = 2
  armor = HeavyArmor()
  shield = Shield()

  weapon1 = weapons.Trident
  att1 = 2
  off = 10
  strn = 11

  common = 6
  fear = 5
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.favhill = [0]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [swamp_t]
    self.other_skills = [Miasma(self)]



class Mandeha(Unit):
  name = "mandeha"
  units = 1
  min_units = 1
  ln = 2
  max_squads = 1
  type = "beast"
  traits = [beast_t]
  aligment = hell_t
  size = 5
  train_rate = 2
  upkeep = 540
  resource_cost = 40
  food = 7
  pop = 0
  terrain_skills = [DarkVision, ForestSurvival, MountainSurvival]

  hp = 80
  hp_res = 12
  sight = 100
  mp = [2, 2]
  moves = 6
  resolve = 10
  global_skills = [DeepestDarkness, FearAura]

  dfs = 7
  res = 20
  hres = 14
  arm = 2
  armor = None

  weapon1 = weapons.FleshEater
  att1 = 2
  off = 16
  offensive_skills = []
  strn = 122

  fear = 2

  def __init__(self, nation):
    super().__init__(nation)
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class Mammot(Unit):
  name = "mammot"
  units = 2
  min_units = 2
  ln = 5
  max_squads = 10
  type = "beast"
  traits = [mammot_t]
  aligment = nature_t
  size = 4
  train_rate = 3
  upkeep = 15
  resource_cost = 25
  food = 10
  pop = 5
  terrain_skills = []

  hp = 30
  mp = [2, 2]
  moves = 5
  resolve = 5

  dfs = 6
  res = 14
  hres = 4
  arm = 4
  armor = None

  weapon1 = weapons.Tusk
  att1 = 1
  weapon2 = weapons.Crush
  att2 = 1
  off = 8
  strn = 16

  common = 8
  fear = 5
  populated_land = 1
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [DeadMammot]
    Ground.__init__(self)
    self.favhill = [0]
    self.favsoil = [tundra_t]
    self.favsurf = [none_t]



class DeadMammot(Unit):
  name = "dead mammot"
  units = 1
  min_units = 1
  ln = 5
  max_squads = 10
  type = "beast"
  traits = [death_t, mammot_t]
  aligment = malignant_t
  size = 4
  train_rate = 4
  upkeep = 7
  resource_cost = 30
  food = 0
  pop = 3
  terrain_skills = []

  hp = 50
  mp = [2, 2]
  moves = 3
  resolve = 10

  dfs = 4
  res = 14
  hres = 8
  arm = 4
  armor = None

  weapon1 = weapons.Tusk
  att1 = 1
  weapon2 = weapons.Crush
  att2 = 1
  off = 6
  strn = 16

  common = 8
  fear = 1
  populated_land = 1
  sort_chance = 50

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    Ground.__init__(self)
    self.favhill = [0]
    self.favsoil = [tundra_t]
    self.favsurf = [none_t]



class MASTER(Unit):
  name = "MASTER"
  units = 1
  min_units = 1
  max_squads = 1
  unique = 1
  type = "DEBUG ONLY"
  traits = [human_t, death_t, malignant_t, leader_t, vampire_t, wizard_t, commander_t]
  size = 10
  gold = 0
  upkeep = 0
  resource_cost = 0
  food = 0
  pop = 0
  terrain_skills = [DesertSurvival, ForestSurvival, MountainSurvival, SwampSurvival]

  hp = 1000
  mp = [2000, 2000]
  moves = 12
  resolve = 10
  global_skills = [DarkPresence, ElusiveShadow, FearAura, Fly, BloodLord, MastersEye, NightFerocity, NightSurvival]
  power = 2000000
  power_max = 2000000
  power_res = 5

  dfs = 8
  res = 7
  arm = 0
  armor = LightArmor()

  att1 = 6
  damage = 6
  off = 8
  strn = 8
  pn = 3

  stealth = 5

  pref_corpses = 1

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [CastBloodRain, RaiseDead]  # , BloodStorm, DarkMantle, SummonBloodKnight]
    self.corpses = []
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [forest_t, none_t]
    self.favhill = 0, 1



class Ogre(Unit):
  name = "ogro"
  units = 10
  min_units = 5
  ln = 7
  max_squads = 20
  type = "beast"
  traits = [ogre_t]
  aligment = wild_t
  size = 3
  train_rate = 2.5
  upkeep = 15
  resource_cost = 15
  food = 6
  pop = 3
  terrain_skills = [Burn, Raid]

  hp = 22
  mp = [2, 2]
  moves = 5
  resolve = 5
  global_skills = [BloodyBeast]

  dfs = 7
  res = 10
  hres = 4
  arm = 2
  armor = None

  weapon1 = weapons.GreatClub
  att1 = 1
  off = 8
  strn = 11

  common = 6
  fear = 2
  populated_land = 1
  sort_chance = 80

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    Ground.__init__(self)
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t, forest_t]



class PaleOne(Unit):
  name = "pale one"
  units = 20
  min_units = 10
  ln = 10
  max_squads = 6
  type = "beast"
  traits = [beast_t]
  aligment = order_t
  size = 2
  train_rate = 2
  upkeep = 15
  resource_cost = 12
  food = 1
  pop = 2
  terrain_skills = [DarkVision, Burn, MountainSurvival, Raid]

  hp = 10
  hp_res = 2
  mp = [2, 2]
  moves = 6
  resolve = 5
  global_skills = []

  dfs = 8
  res = 9
  hres = 4
  arm = 0
  armor = None

  weapon1 = weapons.BronzeSpear
  att1 = 1
  off = 8
  strn = 9

  fear = 5
  populated_land = 0
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    Ground.__init__(self)
    self.favhill = [1]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t]



class Peasant(Human):
  name = peasant_t
  units = 40
  min_units = 10
  ln = 20
  max_squads = 20
  levy = 1
  type = "civil"
  will_less = 1
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 1
  upkeep = 1
  resource_cost = 7
  food = 2
  pop = 1
  terrain_skills = [Burn]

  hp = 6
  mp = [2, 2]
  moves = 5
  resolve = 3
  global_skills = [PyreOfCorpses, Undisciplined]

  dfs = 6
  res = 6
  hres = 2
  arm = 0
  armor = None

  weapon1 = weapons.Pitchfork
  att1 = 1
  off = 6
  strn = 6

  fear = 5

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Zombie]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t]
    self.favhill = [0]



class PeasantLevy(Human):
  name = peasant_levie_t
  units = 30
  min_units = 10
  ln = 15
  max_squads = 12
  levy = 1
  type = "infantry"
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 1.3
  upkeep = 3
  resource_cost = 9
  food = 2
  pop = 1.2
  terrain_skills = [Burn, Raid]

  hp = 8
  mp = [2, 2]
  moves = 5
  resolve = 4
  global_skills = [PyreOfCorpses, Undisciplined]

  dfs = 7
  res = 8
  hres = 2
  arm = 0
  armor = None
  shield = Shield()

  weapon1 = weapons.BronzeSpear
  att1 = 1
  off = 7
  strn = 8

  common = 6
  fear = 5

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Zombie]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t]
    self.favhill = [0]



class Population(Human):
  name = "population"
  units = 50
  min_units = 10
  max_squads = 5
  type = "civil"
  traits = [human_t]
  size = 2
  gold = 60
  upkeep = 2
  resource_cost = 8
  food = 2
  pop = 1
  terrain_skills = [Burn, Raid]

  hp = 3
  mp = [2, 2]
  moves = 5
  resolve = 4

  dfs = 1
  res = 2
  hres = 0
  arm = 0
  armor = None

  att1 = 1
  off = 1
  strn = 1
  pn = 0
  
  fear = 5
  populated_land = 1
  sort_chance = 70

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Zombie]
    self.favhill = [1]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t, forest_t]



class Raider(Human):
  name = raider_t
  units = 20
  sts = 1
  min_units = 10
  ln = 15
  max_squads = 5
  type = "infantry"
  traits = [human_t]
  aligment = wild_t
  size = 2
  train_rate = 1.5
  upkeep = 10
  resource_cost = 14
  food = 3
  pop = 1.5
  terrain_skills = [Burn, DarkVision, ForestSurvival, MountainSurvival, SwampSurvival, Raid]

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 4
  global_skills = [Furtive, Undisciplined]

  dfs = 7
  res = 7
  hres = 2
  arm = 0
  armor = None

  weapon1 = weapons.ShortSword
  att1 = 1
  off = 7
  strn = 7
  
  common = 10
  fear = 4
  populated_land = 1
  sort_chance = 80

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [forest_t, none_t, swamp_t]



class Rider(Human):
  name = rider_t
  units = 10
  min_units = 10
  ln = 7
  max_squads = 4
  type = "cavalry"
  mounted = 1
  traits = [human_t]
  aligment = order_t
  size = 3
  train_rate = 2
  upkeep = 25
  resource_cost = 16
  food = 6
  pop = 3
  terrain_skills = [Burn, Raid]

  hp = 14
  mp = [4, 4]
  moves = 8
  resolve = 5
  global_skills = [Undisciplined]

  dfs = 8
  res = 9
  hres = 4
  arm = 1
  armor = None

  weapon1 = weapons.Sword
  att1 = 1
  weapon2 = weapons.Hoof
  att2 = 1
  off = 9
  strn = 10
  offensive_skills = [Charge]

  common = 6
  fear = 4
  populated_land = 1
  sort_chance = 80

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favhill = [0]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t]



class Satyr(Human):
  name = "satyr"
  units = 10
  min_units = 10
  ln = 10
  max_squads = 4
  type = "infantry"
  traits = [beast_t]
  aligment = wild_t
  size = 2
  train_rate = 1.5
  upkeep = 15
  resource_cost = 12
  food = 2
  pop = 2
  terrain_skills = [Burn, ForestSurvival, MountainSurvival, Raid]

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 5
  global_skills = [Undisciplined]

  dfs = 8
  res = 9
  hres = 4
  arm = 0
  armor = None

  weapon1 = weapons.ShortSword
  att1 = 1
  off = 7
  strn = 8
  offensive_skills = [Charge]

  common = 6
  fear = 4
  populated_land = 1
  sort_chance = 80

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favhill = [1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class Slave(Human):
  name = "slave"
  units = 30
  min_units = 10
  ln = 20
  max_squads = 60
  type = "civil"
  will_less = 1
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 4
  upkeep = 1
  resource_cost = 7
  food = 3
  pop = 1
  terrain_skills = [Burn]

  hp = 6
  mp = [2, 2]
  moves = 5
  resolve = 3
  global_skills = [PyreOfCorpses, Undisciplined]

  dfs = 6
  res = 6
  hres = 1
  arm = 0
  armor = None

  weapon1 = weapons.Sword
  att1 = 2
  weapon2 = weapons.Fist
  att2 = 1
  off = 5
  strn = 5

  fear = 5

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Zombie]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t]
    self.favhill = [0]



class SlaveHunter(Human):
  name = "cazador esclavo"
  units = 20
  min_units = 5
  max_squads = 5
  type = "infantry"
  will_less = 1
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 5
  upkeep = 3
  resource_cost = 1
  food = 2
  pop = 2
  terrain_skills = [ForestSurvival, MountainSurvival, Raid]

  hp = 8
  sight = 2
  mp = [2, 2]
  moves = 5
  resolve = 2
  global_skills = [Undisciplined]

  dfs = 6
  res = 8
  hres = 1
  arm = 0
  armor = None

  weapon1 = weapons.ShortBow
  att1 = 1
  weapon2 = weapons.Fist
  att2 = 1
  off = 6
  offensive_skills = [Ambushment, Skirmisher]
  strn = 8

  fear = 6
  populated_land = 1
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Zombie]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class SlaveWarrior(Human):
  name = "guerrero esclavo"
  units = 20
  min_units = 10
  ln = 10
  max_squads = 8
  type = "infantry"
  will_less = 1
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 8
  upkeep = 4
  resource_cost = 10
  food = 3
  pop = 1.5
  terrain_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 3
  global_skills = [PyreOfCorpses, Undisciplined]

  dfs = 7
  res = 8
  hres = 2
  arm = 0
  armor = None
  shield = Shield()

  weapon1 = weapons.Sword
  att1 = 1
  off = 8
  pn = 0
  strn = 8

  fear = 5
  populated_land = 1
  sort_chance = 70

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, none_t]



class SonOfWind(Human):
  name = "hijo del viento"
  units = 10
  min_units = 10
  ln = 10
  max_squads = 4
  type = "infantry"
  traits = [human_t]
  aligment = wild_t
  size = 2
  train_rate = 1.5
  upkeep = 15
  resource_cost = 16
  food = 3
  pop = 2
  terrain_skills = [Burn, DarkVision, DesertSurvival, Raid, MountainSurvival]

  hp = 10
  mp = [2, 2]
  moves = 7
  resolve = 6
  global_skills = [Furtive]

  dfs = 9
  res = 8
  hres = 2
  arm = 0
  armor = LightArmor()
  shield = Shield()

  weapon1 = weapons.Scimitar
  att1 = 2
  off = 8
  strn = 10

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]



class Troglodyte(Unit):
  name = "troglodyte"
  units = 6
  min_units = 6
  ln = 10
  max_squads = 10
  type = "beast"
  traits = [human_t]
  aligment = wild_t
  size = 2
  train_rate = 2
  upkeep = 5
  resource_cost = 18
  food = 3
  pop = 1.5
  terrain_skills = [DarkVision, Burn, MountainSurvival, Raid]

  hp = 30
  mp = [2, 2]
  moves = 5
  resolve = 6

  dfs = 7
  res = 9
  hres = 4
  arm = 0
  armor = None

  weapon1 = weapons.Claw
  att1 = 1
  off = 8
  strn = 9

  common = 8
  fear = 1
  populated_land = 1
  sort_chance = 98

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    Ground.__init__(self)
    self.favhill = [1]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t]



class Troll(Unit):
  name = "troll"
  units = 2
  min_units = 1
  ln = 5
  max_squads = 8
  poisonres = 1
  type = "beast"
  traits = [troll_t]
  aligment = wild_t
  size = 5
  train_rate = 3
  upkeep = 40
  resource_cost = 22
  food = 6
  pop = 5
  terrain_skills = [Burn, ForestSurvival, MountainSurvival, Raid]

  hp = 40
  mp = [2, 2]
  moves = 5
  resolve = 5

  dfs = 8
  res = 12
  hres = 8
  arm = 5
  armor = None

  weapon1 = weapons.GreatClub
  att1 = 2
  off = 8
  strn = 11

  common = 5
  fear = 2
  populated_land = 1
  sort_chance = 70

  def __init__(self, nation):
    super().__init__(nation)
    Ground.__init__(self)
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t, forest_t]



class Warg(Unit):
  name = "huargo"
  units = 10
  sts = 1
  min_units = 5
  ln = 10
  max_squads = 12
  type = "beast"
  traits = [wolf_t]
  aligment = malignant_t
  size = 2
  train_rate = 3
  upkeep = 35
  resource_cost = 18
  food = 6
  pop = 3
  terrain_skills = [DarkVision, ForestSurvival, MountainSurvival]

  hp = 16
  sight = 3
  mp = [4, 4]
  moves = 7
  resolve = 5
  global_skills = [BloodyBeast, Furtive, Undisciplined]

  dfs = 8
  res = 10
  hres = 4
  arm = 1
  armor = None

  weapon1 = weapons.Bite
  att1 = 1
  weapon2 = weapons.Claw
  att2 = 1
  off = 9
  strn = 10
  
  common = 6
  fear = 4
  populated_land = 1
  sort_chance = 70

  def __init__(self, nation):
    super().__init__(nation)
    Ground.__init__(self)
    self.corpses = [DireWolf]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class WargRider(Unit):
  name = "warg rider"
  units = 5
  min_units = 5
  ln = 7
  max_squads = 6
  mounted = 1
  type = "beast"
  traits = [orc_t]
  aligment = malignant_t
  size = 3
  train_rate = 2.5
  upkeep = 60
  resource_cost = 22
  food = 8
  pop = 4
  terrain_skills = [DarkVision, ForestSurvival, MountainSurvival]

  hp = 25
  sight = 3
  mp = [2, 2]
  moves = 6
  resolve = 5
  global_skills = [BloodyBeast, Furtive, Undisciplined]

  dfs = 8
  res = 11
  hres = 6
  arm = 1
  armor = None

  weapon1 = weapons.Sword
  att1 = 1
  weapon2 = weapons.Claw
  att2 = 1
  weapon3 = weapons.Bite
  att3 = 1  
  off = 9
  strn = 19
  
  common = 4
  fear = 3
  populated_land = 1
  sort_chance = 80

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    Ground.__init__(self)
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class Warrior(Human):
  name = warrior_t
  units = 20
  sts = 2
  min_units = 10
  ln = 5
  max_squads = 10
  type = "infantry"
  traits = [human_t]
  aligment = order_t
  size = 2
  train_rate = 1.5
  upkeep = 10
  resource_cost = 10
  food = 3
  pop = 1.5
  terrain_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 6
  global_skills = [PyreOfCorpses]

  dfs = 8
  res = 9
  hres = 2
  arm = 0
  armor = None

  weapon1 = weapons.Sword
  att1 = 1
  off = 8
  strn = 9

  common = 10
  fear = 5
  populated_land = 1
  sort_chance = 70

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, none_t]



class WetOne(Unit):
  name = "weet one"
  units = 20
  min_units = 10
  ln = 5
  max_squads = 6
  type = "beast"
  traits = [beast_t]
  aligment = order_t
  size = 2
  train_rate = 1.5
  upkeep = 10
  resource_cost = 14
  food = 1
  pop = 1.5
  terrain_skills = [DarkVision, Burn, SwampSurvival, Raid]

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 5
  global_skills = []

  dfs = 8
  res = 8
  hres = 1
  arm = 0
  armor = None

  weapon1 = weapons.StoneSpear
  att1 = 1
  off = 8
  strn = 7

  fear = 7
  populated_land = 0
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    Ground.__init__(self)
    self.soil += [coast_t]
    self.favhill = [0]
    self.favsoil = [coast_t, swamp_t]
    self.favsurf = [none_t]



class WoodlandSpirit(Unit):
  name = "woodland spirit"
  units = 1
  min_units = 1
  ln = 5
  max_squads = 5
  ethereal = 1
  type = "beast"
  traits = [spirit_t]
  aligment = wild_t
  size = 4
  train_rate = 2
  upkeep = 10
  resource_cost = 18
  food = 1
  pop = 3
  terrain_skills = [ForestSurvival, DarkVision]

  hp = 40
  hp_res = 2
  mp = [0, 0]
  moves = 5
  resolve = 10
  global_skills = []

  dfs = 9
  res = 11
  hres = 8
  arm = 0
  armor = None

  weapon1 = weapons.Branch
  att1 = 3
  off = 9
  strn = 11

  common = 4
  fear = 1

  def __init__(self, nation):
    super().__init__(nation)
    Ground.__init__(self)



class Wolf(Unit):
  name = wolf_t
  units = 20
  min_units = 10
  ln = 15
  max_squads = 6
  type = "beast"
  traits = [wolf_t]
  aligment = nature_t
  size = 2
  train_rate = 2
  upkeep = 15
  resource_cost = 14
  food = 3
  pop = 2
  terrain_skills = [DarkVision, ForestSurvival]

  hp = 10
  sight = 3
  mp = [4, 4]
  moves = 7
  resolve = 4
  global_skills = [Furtive, NightFerocity]

  dfs = 8
  res = 7
  hres = 3
  arm = 0
  armor = None

  weapon1 = weapons.Bite
  att1 = 1
  off = 9
  strn = 9  
  offensive_skills = [Ambushment]
  
  common = 8
  fear = 4
  populated_land = 1
  sort_chance = 70

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [DireWolf]
    Ground.__init__(self)
    self.favhill = [0]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t, forest_t]



class WolfRider(Unit):
  name = "wolf rider"
  units = 10
  min_units = 10
  ln = 10
  max_squads = 6
  mounted = 1
  type = "infantry"
  traits = [goblin_t]
  aligment = orcs_t
  size = 2
  train_rate = 2
  upkeep = 25
  resource_cost = 16
  food = 4
  pop = 2.5
  terrain_skills = [Burn, ForestSurvival, MountainSurvival, Raid]

  hp = 12
  mp = [3, 3]
  moves = 6
  resolve = 5
  global_skills = [BloodyBeast, Furtive, Undisciplined]

  dfs = 8
  res = 10
  hres = 5
  arm = 0
  armor = None

  weapon1 = weapons.ShortBow
  att1 = 1
  weapon2 = weapons.Bite
  att2 = 1
  off = 5
  strn = 10
  offensive_skills = [Ambushment] 
  
  common = 8
  fear = 3
  populated_land = 1
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeleton]
    Ground.__init__(self)
    self.favsoil = [waste_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, swamp_t]
    self.favhill = [0, 1]
    self.traits += [goblin_t]



# Random nations.
class Hell(Nation):
  name = hell_t
  info = 0

  def __init__(self):
    super().__init__()
    self.log = [[hell_t]]
    self.av_units = []



class Malignant(Nation):
  name = malignant_t
  info = 0

  def __init__(self):
    super().__init__()
    self.log = [[malignant_t]]
    self.av_units = []



class Nature(Nation):
  name = nature_t
  info = 0

  def __init__(self):
    super().__init__()
    self.log = [[nature_t]]
    self.av_units = []



class Order(Nation):
  name = order_t
  info = 0
  gold = 3000

  def __init__(self):
    super().__init__()
    self.log = [[order_t]]
    self.av_units = []



class Orcs(Nation):
  name = orcs_t
  info = 0

  def __init__(self):
    super().__init__()
    self.log = [[orcs_t]]
    self.av_units = []



class Sacred(Nation):
  name = sacred_t
  info = 0
  gold = 3000

  def __init__(self):
    super().__init__()
    self.log = [[sacred_t]]
    self.av_units = []



class Wild(Nation):
  name = wild_t
  info = 0
  gold = 3000

  def __init__(self):
    super().__init__()
    self.log = [[wild_t]]
    self.av_units = []



random_buildings = [
  BrigandLair, Campment, CaveOfDarkRites, CaveOfGhouls,
  DececratedCemetery, FightingPit, GoblinLair, HiddenForest, HyenasLair,
  LizardsBog, NecromancersLair, MammotsCave, OathStone, OpulentCrypt,
  TroglodyteCave, TrollCave, UnderworldEntrance, WisperingWoods, WolfLair,
  WargsCave]


nations = [HolyEmpire, Valahia, WoodElves]

nations_buildings = []
for it in nations: nations_buildings += it().av_buildings

nations_units = []
for it in nations_buildings: nations_units += it(None, None).av_units

random_units = []
for it in random_buildings: random_units += it(it.nation, None).av_units 
from data.spells import *
