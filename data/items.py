#!/usr/bin/env python
# from math import ceil, floor
# from pdb import Pdb
# from random import randint, shuffle, choice, uniform
# from time import sleep, process_time

import numpy as np

import basics
from data.events import *
from data.lang.es import *
from data.names import *
from data.skills import *
# from log_module import *
# from screen_reader import *
# from sound import *



class Empty:
  pass



class LightArmor:

  def __init__(self):
    self.arm = 2
    self.name = 'light armor'



class MediumArmor:

  def __init__(self):
    self.arm = 3
    self.name = 'medium armor'



class HeavyArmor:

  def __init__(self):
    self.arm = 4
    self.name = 'heavy armor'



class Shield:

  def __init__(self):
    self.name = 'shield'
    self.dfs = 4



class Building:
  name = None
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
  grouth_total = 0
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
    if self.base:
      base = self.base(self.nation, self.pos)
      self.food_pre = base.food
      self.grouth_pre = base.grouth_total
      self.income_pre = base.income
      self.public_order_pre = base.public_order
      self.resource_pre = base.resource 
  
  def __str__(self):
    name = f'{self.name}.' 
    if self.nick:
      name += f' {self.nick}.'
    return name
  
  def can_build(self):
    logging.debug(f'requicitos de {self}.')
    if self.check_tile_req(self.pos) == 0:
      return 0
    if self.gold and self.nation.gold < self.gold:
      return 0
    if   self.size > self.pos.size:
      return 0
    if self.local_unique and has_name(self.pos.buildings, self.name):
      return 0
    if self.city_unique and has_name(self.pos.city.buildings, self.name):
      return 0
    if self.global_unique and has_name(self.pos.nation.buildings, self.name):
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
    if self.own_terrain and pos.nation != self.nation : go = 0    
    return go

  def improve(self, upgrade):
    msg = f'{self} actualizará a {upgrade}. {cost_t} {upgrade.gold} en {self.pos} {self.pos.cords}.'
    logging.info(msg)
    if self.nation.show_info:
      sp.speak(msg)
      sleep(loadsound('gold1') * 0.5)
    
    self.nation.gold -= upgrade.gold
    upgrade.av_units_pre = []
    for i in self.av_units_pre + self.av_units:
      if i not in upgrade.av_units_pre: upgrade.av_units_pre.append(i)
    upgrade.nation = self.nation
    upgrade.nations = self.nations
    upgrade.pos = self.pos
    upgrade.resource_cost[0] = 1
    upgrade.size = self.size
    if self.pos.city: msg = [f'se actualizará {self} en {self.pos.city}, {self.pos} {self.pos.cords}.']
    else: msg = [f'se actualizará {self} en {self.pos} {self.pos.cords}.']
    upgrade.nation.log[-1].append(msg)
    self.pos.buildings[self.pos.buildings.index(self)] = upgrade

  def launch_event(self):
    pass

  def set_hidden(self, nation):
    if nation in self.nations: return
    visible = self.pos.pop // 50
    visible += sum([(i.units * i.sight) // 20 for i in self.pos.units if i.nation == nation])
    if visible < 1: return
    stealth = self.stealth
    if self.pos.day_night: stealth += 4
    roll = basics.roll_dice(3)
    # print(f'{visible= }, {stealth= }, {roll= }, {roll= }.')
    msg = f'stealth check for {self} in {self.pos} {self.pos.cords}. {visible= }, {stealth= }, {roll= }.'
    self.pos.world.log[-1] += [msg]
    if roll >= stealth - visible:
      msg = [f'{self} {in_t} {self.pos} {self.pos.cords}.']
      nation.log[-1] += [msg]
      self.pos.world.log[-1] += [msg]
      self.nations += [nation]
      if nation.show_info: 
        sp.speak(f'{msg}', 1)
        sleep(loadsound('notify23'))

  def update(self):
    self.is_complete = 1 if self.resource_cost[0] >= self.resource_cost[1] else 0



class City:
  around_coast = 0
  around_threat = 0
  base = None
  defense = 0
  defense_min = 0
  defense_total = 0
  food = 1
  food_need = 0
  food_pre = 1
  food_total = 0
  events = []
  grouth_total = 1
  grouth = 1
  grouth_pre = 1
  capital = 0
  cost = 0
  defense_total_percent = 0
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
  name = None
  nation = None
  nick = None
  pop = 0
  pop_back = 0
  popdef_base = 15
  popdef_change = 200
  popdef_min = 5
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
    self.units = []
    self.upgrade = []

  def __str__(self):
    name = f'{self.nick}'
    return name

  def add_building(self, itm, pos):
    itm.resource_cost[0] = 1
    pos.buildings.append(itm)
    self.nation.gold -= itm.gold
    if self.nation.show_info:
      sp.speak(f'{added_t} {itm}')
      if itm.gold > 0: 
        sleep(loadsound('gold1'))
        sp.speak(f'{cost_t} {itm.gold}.')
    itm.pos = pos
    logging.debug(f'pos {itm.pos} {itm.pos.cords}.')
    itm.city = self
    itm.nation = self.nation
    itm.nations += [self.nation]
    pos.update(itm.nation)
    if itm.pos.city: msg = f'se construirá {itm} en {itm.pos.city}, {itm.pos} {itm.pos.cords}.'
    else: msg = f'se construirá {itm} en {itm.pos} {itm.pos.cords}.'
    logging.info(msg)
    itm.nation.log[-1].append(msg)
    self.update()

  def add_pop(self, number, info=0):
    [i.update(self.nation) for i in self.tiles]

    tiles = [i for i in self.tiles if i.blocked == 0
             and i.soil.name in self.nation.all_terrains]
    shuffle(tiles)
    tiles.sort(key=lambda x: x.food, reverse=True)
    tiles.sort(key=lambda x: x.soil.name in self.nation.pop_pref_soil 
               and x.surf.name in self.nation.pop_pref_surf 
               and x.hill in self.nation.pop_pref_hill, reverse=True)
    tiles.sort(key=lambda x: x.public_order, reverse=True)
    grouth = ceil(number / (len(self.tiles) * 1.1))  # avoid 0with ceil. if not add pop stops.
    msg = f'{self} crecerá {number}. grouth_total {grouth}.'
    self.nation.devlog[-1] += [msg]
    if info: logging.info(f'crecerá {number}. grouth_total {grouth}.')
    for t in tiles: t.last_grouth = []
    tries = 10000
    while number > 1:
      tries -= 1
      if tries < 0: 
        sp.speak(f'add pop stoped!', 1)
        sleep(1)
        Pdb().set_trace()
      
      for t in tiles:
        if number < 1: break
        building_mod = 0
        overpopulated = 0
        _grouth = grouth
        if t.hill not in self.nation.pop_pref_hill: _grouth *= 0.1
        if t.soil.name not in self.nation.pop_pref_soil: _grouth *= 0.4
        if t.surf.name not in self.nation.pop_pref_surf: _grouth *= 0.2
        if t.is_city: _grouth *= 1.1
        buildings = [b for b in t.buildings if b.nation == self.nation
                     and b.resource_cost[0] == b.resource_cost[1]]
        if buildings: 
          _grouth *= 1 + (len(buildings) // 10)
          building_mod = 1 + (len(buildings) // 2)
        if t.pop / t.food * 100 >= 50: 
          _grouth *= 0.5
          overpopulated = 50
        if t.pop / t.food * 100 >= 80:
          _grouth *= 0.3
          overpopulated = 80
        if t.pop / t.food * 100 >= 90: 
          _grouth *= 0.1
          overpopulated = 90
        _grouth = ceil(_grouth)
        if _grouth < 1: _grouth = 1
        if _grouth > number: _grouth = number
        if info: logging.debug(f'{t}, {t.is_city= }, {len(t.buildings)= }, {_grouth= }.')
        t.last_grouth += [["turn", t.world.turn, "grouth", grouth, "overpopulated", overpopulated, "building_mod", building_mod, "_grouth", _grouth, "number", number]]
        
        t.pop += _grouth
        number -= _grouth

  def can_build(self):
    logging.debug(f'requicitos de {self}.')
    if self.check_tile_req(self.pos) == 0:
      return 0
    if self.gold and self.nation.gold < self.gold:
      return 0
    if   self.size > self.pos.size:
      return 0
    if self.unique and has_name(self.pos.city.buildings, self.name):
      return 0
    return 1

  def check_building(self):
    logging.debug(f'check building {self}.')
    for bu in self.buildings:
      if bu.nation != bu.nation:
        bu.cost[1] -= 20 * bu.cost[1] / 100
      if bu.resource_cost[0] < bu.resource_cost[1] and bu.nation == self.nation: 
        bu.resource_cost[0] += self.resource_total
        if bu.resource_cost[0] >= bu.resource_cost[1]:
          bu.resource_cost[0] = bu.resource_cost[1]
          if bu.pos.city: msg = f'{bu} {complete_t} en {bu.pos.city}, {bu.pos} {bu.pos.cords}.'
          else: msg = f'. ({bu}) {complete_t} en {bu.pos} {bu.pos.cords}.'
          self.nation.log[-1].append(msg)
          if self.nation.show_info: sleep(loadsound('notify6', channel=ch2) * 0.2)

  def check_events(self):
    [event.run() for event in self.events]

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
    logging.debug(f'check training {self}.')
    if self.production:
      self.prod_progress -= self.resource_total
      if self.prod_progress <= 0:
        self.production[0].pos = self.pos
        self.production[0].city = self
        self.production[0].show_info = self.nation.show_info
        self.production[0].update()
        self.production[0].set_hidden(self.production[0].pos)
        self.nation.gold -= self.production[0].gold
        msg = f'{self.production[0]} entrenado en {self}.'
        logging.debug(msg)
        self.nation.log[-1].append(msg)
        self.pos.units.append(self.production.pop(0))
        self.nation.unit_number += 1
        if self.nation.show_info: sleep(loadsound('notify24', channel=ch4) * 0.5)
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
      logging.warning(f'income menor que cero! {income}')

  def launch_event(self):
    pass

  def population_change(self):
    self.update()
    grouth = round(self.grouth_total * self.pop / 100)
    logging.debug(f'{self.grouth_total}. extra population {grouth}.')
    self.add_pop(grouth)
    
    if self.pop_back > 0: 
      pop_back = randint(20, 40) * self.pop_back / 100
      self.add_pop(pop_back)
      self.pop_back -= pop_back
      logging.debug(f'regresan {pop_back} civiles.')

  def reduce_pop(self, number, info=0):
    logging.debug(f'reduce {number} de {self} ({self.pop} pop).')
    tiles = [i for i in self.tiles if i.blocked == 0]
    reduce = number / 6
    shuffle(tiles)
    tiles.sort(key=lambda x: x.get_distance(x, self.pos))
    if info: logging.debug(f'reducirá {number}.')
    while number > 0:
      for t in tiles:
        if t.pop >= reduce and number > 0:
          if info: logging.debug(f'{t.pop} en {t} {t.cords}.')
          t.pop -= reduce
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

    # logging.debug(f'_av {len(_av)}.')
  def set_capital_bonus(self):
    self.food = 0
    self.grouth = 0
    self.income = 0
    self.public_order = 0

  def set_defense(self):
    self.defense_total = 0
    self.defense_min = 0
    self.hostile_ranking = 0
    units = [i for i in self.units if i.nation == self.nation and i.goal == None and i.leader == None]
    self.defense = sum(i.ranking for  i in self.pos.units if i.garrison)
    for i in self.units:
      if i.garrison and i.pos == self.pos: i.city = self 
    self.defense_total = sum(i.ranking for i in units 
                             if i.scout == 0 and i.settler == 0 and i.goal == None and i.leader == None)
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

  def set_military_limit(self):
    self.military_limit = (self.military_base + 
                           (self.pop / self.military_change)) 
    if self.military_limit > self.military_max: 
      self.military_limit = self.military_max
    if self.seen_threat > self.defense_total // 2 or self.defense < self.defense_min: 
      self.military_limit *= 2

  def set_name(self):
    if self.nation.city_names: 
      shuffle(self.nation.city_names)
      self.nick = self.nation.city_names.pop()

  def set_seen_units(self, new=0, info=0):
    # logging.debug(f'set seen units {self}.')
    tiles = [t for t in self.pos.get_near_tiles(4)
             if t.units]
    self.pos.pos_sight(self.nation, self.nation.map)
    tiles = [t for t in tiles if t in self.nation.map and t.sight and t.units]
    [t.update(self.nation) for t in tiles]
    if new or self.seen_units == []: 
      self.seen_units.append([])
      logging.debug(f'nuevo.')
    for t in tiles:
      for uni in t.units: 
        if (uni.nation != self.nation and uni not in self.seen_units[-1] 
            and uni.hidden == 0): 
          self.seen_units[-1].append(uni)
    
    self.seen_threat = 0
    self.seen_animal = []
    self.seen_fly = []
    self.seen_human = []
    self.seen_mounted = []
    self.seen_pn = []
    self.seen_ranged = []
    self.seen_sacred = []
    self.seen_undead = []
    for l in self.seen_units[-4:]:
      for uni in l:
        self.seen_threat += uni.ranking
        if animal_t in uni.traits: self.seen_animal += [uni]
        if uni.can_fly: self.seen_fly += [uni]
        if human_t in uni.traits: self.seen_human += [uni]
        if mounted_t in uni.traits: self.seen_mounted += [uni]
        if uni.pn + uni.pn_mod: self.seen_pn += [uni]
        if uni.rng + uni.rng_mod >= 6: self.seen_ranged += [uni]
        if sacred_t in uni.traits: self.seen_sacred += [uni] 
        if undead_t in uni.traits: self.seen_undead += [uni]
    
    self.seen_animal_rnk = sum(i.ranking for i in self.seen_animal)
    self.seen_fly_rnk = sum(i.ranking for i in self.seen_fly)
    self.seen_human_rnk = sum(i.ranking for i in self.seen_human)
    self.seen_mounted_rnk = sum(i.ranking for i in self.seen_mounted)
    self.seen_pn_rnk = sum(i.ranking for i in self.seen_pn)
    self.seen_ranged_rnk = sum(i.ranking for i in self.seen_ranged)
    self.seen_sacred_rnk = sum(i.ranking for i in self.seen_sacred)
    self.seen_undead_rnk = sum(i.ranking for i in self.seen_undead)
    
    if info:
      logging.debug(f'animal {len(self.seen_animal)}. ranking {self.seen_animal_rnk}.')
      logging.debug(f'fly {len(self.seen_fly)}. ranking {self.seen_fly_rnk}.')
      logging.debug(f'human {len(self.seen_human)}. ranking {self.seen_human_rnk}.')
      logging.debug(f'mounted {len(self.seen_mounted)}. ranking {self.seen_mounted_rnk}.')
      logging.debug(f'rng {len(self.seen_ranged)}. ranking {self.seen_ranged_rnk}.')
      logging.debug(f'undead {len(self.seen_undead)}. ranking {self.seen_undead_rnk}.')
  
  def set_train_type(self, units, info=1):
    self.set_seen_units(0, info=1)
    self.set_units_types()
    shuffle(units)
    if roll_dice(1) >= 3:
      if info: logging.debug(f'sort by nation traits.')
      units.sort(key=lambda x: any(i in x.traits for i in self.nation.traits), reverse=True)
    [i.update() for i in units]
    if info: logging.debug(f'recividos {len(units)}.')
    _animal = [i for i in units if animal_t in i.traits]
    _anticav = [i for i in units if i.anticav]
    _archers = [i for i in units if i.rng + i.rng_mod > 5]
    _fly = [i for i in units if i.can_fly]
    _mounted = [i for i in units if mounted_t in i.traits]
    _sacred = [i for i in units if sacred_t in i.traits]
    _undead = [i for i in units if undead_t in i.traits]
    if self.defense_total_percent < 100 and self.nation.defense_total_percent < 300 or self.defense_total == 0:
      logging.debug(f'defensivo.')
      if roll_dice(1) >= 3: units.sort(key=lambda x: x.rng + x.rng_mod, reverse=True)
      if self.around_threat >= self.defense / 2: units.sort(key=lambda x: x.resource_cost <= self.resource_total, reverse=True)
      return units
    
    if self.seen_ranged_rnk > (self.units_ranged_rnk + self.units_fly_rnk) * 0.5:
      if info: logging.debug(f'contra ranged.')
      _units = [i for i in units if i.rng + i.rng_mod >= 5
                or i.armor
                or i.shield
                and levy_t not in i.traits] 
      _units.sort(key=lambda x: x.rng + x.rng_mod and x.ranking, reverse=True)
      _units.sort(key=lambda x: x.ranking, reverse=True)
      if _units: return _units
    if self.seen_mounted_rnk > self.units_piercing_rnk + self.units_mounted_rnk:
      if info: logging.debug(f'pn.')
      _units = [i for i in units if i.pn + i.pn_mod
                or i.type == 'cavalry']
      if roll_dice(1) >= 3: _units.sort(key=lambda x: x.ranking, reverse=True)
      if _units: return _units
    if self.seen_undead_rnk > self.units_sacred_rnk // 2:
      if info: logging.debug(f'sacred.')
      _units = [i for i in units if sacred_t in i.traits]
      if roll_dice(1) >= 3: _units.sort(key=lambda x: x.ranking, reverse=True)
      if _units: return _units
    if self.seen_sacred_rnk * 1.5 > self.units_undead_rnk:
      if info: logging.debug(f'human')
      _units = [i for i in units if human_t in i.traits and levy_t not in i.traits]
      _units.sort(key=lambda x: x.ranking, reverse=True)
      if _units: return units
    if info: logging.debug(f'av anticav {len(_anticav)}.')
    if info: logging.debug(f'total rnk {self.units_piercing_rnk*100//self.defense_total}.')
    if info: logging.debug(f'limit {self.nation.units_piercing_limit}.')
    if (_anticav and roll_dice(1) >= 3 
        and self.units_piercing_rnk * 100 // self.defense_total < self.nation.units_piercing_limit):
      if info: logging.debug(f'piercing.')
      if roll_dice(1) >= 3: _anticav.sort(key=lambda x: x.ranking, reverse=True)
      if _anticav: return _anticav
    if info: logging.debug(f'av sacred {len(_sacred)}.')
    if info: logging.debug(f'total rnk {self.units_sacred_rnk*100//self.defense_total}.')
    if info: logging.debug(f'limit {self.nation.units_sacred_limit}.')
    if (_sacred and roll_dice(1) >= 3 
        and self.units_sacred_rnk * 100 // self.defense_total < self.nation.units_sacred_limit):
      if info: logging.debug(f'sacred.')
      if roll_dice(1) >= 3: _sacred.sort(key=lambda x: x.ranking, reverse=True)
      if _sacred: return _sacred
    
    if self.pos.around_forest + self.pos.around_hill >= 3 and roll_dice(1) >= 5:
      _units = [i for i in units if i.can_fly or i.forest_survival or i.mountain_survival]
      if info: logging.debug(f'forest and hills.')
      _units.sort(key=lambda x: x.rng >= 6, reverse=True)
      if _units: return _units
    if info: logging.debug(f'av archers {len(_archers)}.')
    if info: logging.debug(f'total rnk {self.units_ranged_rnk*100//self.defense_total}')
    if info: logging.debug(f'limit {self.nation.units_ranged_limit}.')
    if (_archers and roll_dice(1) >= 3 
        and self.units_ranged_rnk * 100 // self.defense_total < self.nation.units_ranged_limit):
      if info: logging.debug(f'ranged.')
      if roll_dice(1) >= 2: _archers.sort(key=lambda x: x.ranking, reverse=True)
      _archers.sort(key=lambda x: x.rng >= 6, reverse=True)
      if _archers: return _archers
    if info: logging.debug(f'av mounted {len(_mounted)}.')
    if info: logging.debug(f'total rnk {self.units_mounted_rnk*100/self.defense_total}.')
    if info: logging.debug(f'limit {self.nation.units_mounted_limit}.')
    if (_mounted and roll_dice(1) >= 4
        and self.units_mounted_rnk * 100 / self.defense_total < self.nation.units_mounted_limit):
      if info: logging.debug(f'mounted.')
      _units = [i for i in units if mounted_t in i.traits]
      if _units: return _units
    
    if self.defense_total_percent > 200:
      if info: logging.debug(f'expensive.')
      _units = [i for i in units if levy_t not in i.traits]
      if _units: units = _units
      units.sort(key=lambda x: x.ranking, reverse=True)
      units = [i for i in units[:2]]
      
      shuffle(units)
      return units    
    
    return units

  def set_units_types(self):
    units = [i for i in self.units if i.leader == None and i.group == [] 
             and i.comm == 0]
    self.units_animal = []
    self.units_fly = []
    self.units_human = []
    self.units_melee = []
    self.units_mounted = []
    self.units_piercing = []
    self.units_ranged = []
    self.units_sacred = []
    self.units_undead = []
    for i in units:
      if animal_t in i.traits: self.units_animal += [i]
      if i.can_fly: self.units_fly += [i]
      if human_t in i.traits: self.units_human += [i]
      if i.rng + i.rng_mod < 6: self.units_melee += [i]
      if mounted_t in i.traits: self.units_mounted += [i]
      if i.pn: self.units_piercing += [i] 
      if i.rng >= 6: self.units_ranged += [i]
      if sacred_t in i.traits: self.units_sacred += [i]
      if undead_t in i.traits: self.units_undead += [i]  
    
    self.units_animal_rnk = sum(i.ranking for i in self.units_animal)
    self.units_fly_rnk = sum(i.ranking for i in self.units_fly)
    self.units_human_rnk = sum(i.ranking for i in self.units_human)
    self.units_melee_rnk = sum(i.ranking for i in self.units_melee)
    self.units_mounted_rnk = sum(i.ranking for i in self.units_mounted)
    self.units_piercing_rnk = sum(i.ranking for i in self.units_piercing)
    self.units_ranged_rnk = sum(i.ranking for i in self.units_ranged)
    self.units_sacred_rnk = sum(i.ranking for i in self.units_sacred)
    self.units_undead_rnk = sum(i.ranking for i in self.units_undead)
  
  def start_turn(self):
    self.outcome_raided = 0

  def status(self, info=0):
    logging.info(f'city status {self}.')
    self.for_food_tiles = self.get_tiles_food(self.tiles)
    self.for_food_tiles = [i for i in self.for_food_tiles if i.size >= 4]
    self.for_food_tiles.sort(key=lambda x: x.food, reverse=True)
    self.for_res_tiles = self.get_tiles_res(self.tiles)
    self.for_res_tiles = [i for i in self.for_res_tiles if i.size >= 4]
    self.for_res_tiles.sort(key=lambda x: x.resource, reverse=True)
    
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
    
    self.food_val = round(self.food_total - self.food_need)
    self.food_probable = self.food_val
    for b in self.buildings:
      if b.is_complete == 0:
        self.food_probable += b.food * b.pos.food / 100 
    self.food_probable = round(self.food_probable)
    
    if info:
      logging.debug(f'información de {self}.')
      logging.debug(f'balance de comida {self.food_val}.')
      logging.debug(f'terrenos estratégicos {len(self.defensive_tiles)}')
      logging.debug(f'terrenos de comida {len(self.for_food_tiles)}.')
      logging.debug(f'terreno de recursos {len(self.for_res_tiles)}.')
      
      # revisar si está entrenando unidades.
      if self.production:
        progress = ceil(self.prod_progress / self.resource_total)
        logging.debug(f'entrenando {self.production[0]} en {progress} {turns_t}.')
      elif self.production == []: logging.debug(f'no está produciendo')
      
      logging.debug(f'amenazas internas {self.threat_inside}. ')
      logging.debug(f'nivel de defensa {self.defense} de {self.defense_min}, ({self.defense_percent}%).')
      logging.debug(f'necesita {round(self.defense_need, 2)} defensa.')
      logging.debug(f'defensa total posible {self.defense_total}.')
      logging.debug(f'civiles {self.pop}, {round(self.pop_percent)}%.')
      logging.debug(f'población militar {self.pop_military}, ({round(self.military_percent, 1)}%.')
      logging.debug(f'total {self.pop_total}.')
      logging.debug(f'ingresos {self.income_total}.')

  def train(self, itm):
    logging.info(f'entrena {itm} en {self}.')
    if self.production == []: self.prod_progress = itm.resource_cost
    self.production.append(itm)
    self.nation.gold -= itm.gold
    self.reduce_pop(itm.pop)
    if self.nation.show_info: 
      sleep(loadsound('set6'))
      sp.speak(f'{added_t} {itm} {cost_t} {itm.gold}')
      if itm.gold > 0: loadsound('gold1')

  def update(self):
    [i.update(self.nation) for i in self.tiles]
    self.food_total = sum(t.food for t in self.tiles if t.blocked == 0)
    self.pop = sum([i.pop for i in self.tiles])
    self.pop_military = sum(i.pop for i in self.production)
    self.pop_military += sum(i.pop for i in self.nation.units if i.city == self)
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
    # data buildings.
    self.grouth_total = self.nation.grouth_base
    # print(f'{self.grouth_total = }')
    self.grouth_total += (self.food_total * 100 / self.pop - 100) / self.nation.grouth_rate
    # print(f'{self.grouth_total = }')
    self.grouth_total += self.grouth
    # print(f'from city {self.grouth_total = }')
    tiles = [i for i in self.tiles if i.pop > 0]
    self.public_order_total /= len(tiles)
    self.grouth_total -= round(abs(self.public_order_total - 100) * self.grouth_total / 100)
    # print(f'{round(abs(self.public_order_total-100)*self.grouth_total/100)}, {self.grouth_total = }.')
    if self.grouth_total < 0: self.grouth_total = 0.1
    if self.grouth_total > self.nation.grouth_base * 2: self.grouth_total = self.nation.grouth_base * 2
    self.status()
    self.set_av_units()
    
    # expanding.
    self.expanding = 0
    if self.production and self.production[0].settler: self.expanding = 1

  def set_upgrade(self):
    pass



class Nation:
  name = 'unnamed'
  nick = ''
  gold = 1000
  food_limit_builds = 200
  food_limit_upgrades = 800
  grouth_rate = 1
  public_order = 0
  upkeep_base = 50
  upkeep_change = 100

  attack_factor = 300
  capture = 0
  commander_rate = 10
  scout_factor = 4
  stalk_rate = 50  # cuantos stalk se envian.

  upkeep_change = 100
  ai = 0
  anphibian = 0
  defense_total_percent = 0
  defense_mean = 0
  city_req_pop_base = 1000
  pop_limit = 50

  gold_rate = 0.5
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
  units_animal_limit = 100
  units_fly_limit = 100
  units_human_limit = 100
  units_melee_limit = 100
  units_mounted_limit = 100
  units_piercing_limit = 100
  units_ranged_limit = 100
  units_sacred_limit = 100
  units_undead_limit = 100

  def __init__(self):
    # Casilla inicial permitida.
    self.hill = [0, 1]
    self.soil = [waste_t, glacier_t, grassland_t, ocean_t, plains_t, tundra_t]
    self.surf = [none_t]
    # Terrenos adyacentes permitidos
    self.allow_around_desert = 0
    self.allow_around_forest = 0
    self.allow_around_glacier = 0
    self.allow_around_grassland = 0
    self.allow_around_hill = 0
    self.allow_around_montain = 0
    self.allow_around_ocean = 0
    self.allow_around_plains = 0
    self.allow_around_swamp = 0
    self.allow_around_tundra = 0
    self.allow_around_volcano = 0
    # terrenos adyacentes no permitidos.
    self.unallow_around_desert = 10
    self.unallow_around_forest = 10
    self.unallow_around_glacier = 10
    self.unallow_around_grassland = 10
    self.unallow_around_hill = 10
    self.unallow_around_montain = 10
    self.unallow_around_ocean = 10
    self.unallow_around_plains = 10
    self.unallow_around_swamp = 10
    self.unallow_around_tundra = 10
    self.unallow_around_volcano = 10
    
    self.av_buildings = [Farm, Quarry, SawMill]
    self.buildings = []
    self.cities = []
    self.city_names = []
    
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
    self.units_free = []
    self.units_rebels = []
    
  def __str__(self):
    return self.name

  def add_city(self, itm, unit):
    itm = itm(unit.nation, unit.pos)
    scenary = unit.pos.scenary
    pop = unit.units * 4
    pos = unit.pos
    itm.pop = pop
    pos.buildings.append(itm)
    if unit in unit.pos.units: unit.pos.units.remove(unit)
    itm.set_name()
    if len(self.cities) == 0: itm.capital = 1
    if itm.capital: itm.set_capital_bonus()
    tiles = pos.get_near_tiles(1)
    for t in tiles:
      if t.nation == None:
        itm.tiles.append(t)
        t.city = itm
        t.nation = self
    msg = f'{hamlet_t} {itm.nick} se establece en {itm.pos} {itm.pos.cords}.'
    logging.info(msg)
    self.log[-1].append(msg)
    itm.add_pop(itm.pop)
    [t.update(itm.nation) for t in itm.tiles]
    itm.update()
    itm.status()
    for t in itm.tiles: t.unrest += itm.initial_unrest * uniform(0.5, 1.5)
    self.update(scenary)
    logging.debug(f'{itm.nation} ahora tiene {len(itm.nation.cities)} ciudades.')
  
  def build(self, city):
    if self.income < self.upkeep:
      logging.debug(f'not enogh gold.')
      return
    city.status()
    military_buildings = [b for b in self.av_buildings if military_t in b.tags]
    go = 0
    for b in self.av_buildings:
      if self.gold > b.gold: go = 1
    if go == 0: return
    # Build food buildings.
    logging.debug(f'build food.')
    buildings = [b for b in self.av_buildings if food_t in b.tags and b.gold < self.gold]
    if buildings:
      shuffle(city.tiles)
      count = 1
      if city.buildings_food_complete == []: 
        count = randint(3, 5)
      for b in buildings:
        city.tiles.sort(key=lambda x: x.food)
        city.tiles.sort(key=lambda x: x.public_order)
        for t in city.tiles:
          if t.city.buildings_food == []: rate = 0
          elif t.city.capital: rate = 60 
          elif t.city.capital == 0: rate = 80
          if t.public_order >= 80: rate += 20
          t.food_rate = rate
          if rate <= t.pop / t.food * 100 or city.nation.gold >= b.gold * 10:
            t.update(self)
            if t.around_threat or t.threat: 
              logging.debug(f'threat')
              continue
            building = b(self, t)
            if building.can_build():
              city.add_building(building, t)
              logging.debug(f'{building} added at {t} {t.cords}.')
              count -= 1
              if count < 1: break
    
    # build military buildings.
    city.status()
    if city.buildings_food and [b for b in city.buildings_military if b.is_complete == 0] == []:
      logging.debug(f'build military.')
      military_buildings.sort(key=lambda x: x(self, self.pos).resource_cost[1])
      if roll_dice(1) >= 5: shuffle(military_buildings)
      
      count = 1
      if city.capital == 0 and city.defense_total < 200:
        logging.debug(f'not capital and needs more defense.')
        count = 0
      for b in military_buildings:
        if count == 0: break
        city.tiles.sort(key=lambda x: len(x.around_snations), reverse=True)
        for t in city.tiles:
          t.update(self)
          if t.around_threat or t.threat: continue
          building = b(self, t)
          if building.can_build():
            city.add_building(building, t)
            logging.debug(f'{building} added at {t} {t.cords}.')
            count = 0
            break
    
    # build misc buildings.
    city.status()
    if city.buildings_food and city.buildings_military:
      count = 0
      logging.debug(f'build misc.')
      buildings = [b for b in self.av_buildings if any(i in b.tags for i in [unrest_t, resource_t])]
      cost_mean = sum([b.gold for b in buildings])
      completed = len(city.buildings_res)
      if completed < len(city.buildings_military_complete) or completed == 0: count = 1
      if len(city.buildings_military_complete) == len(military_buildings) and city.nation.gold > cost_mean: count = 1
      shuffle(buildings)
      for b in buildings:
        if count == 0: break
        if unrest_t in b.tags: city.tiles.sort(key=lambda x: x.public_order)
        if resource_t in b.tags:
          if city.defense_total_percent < 200:
            logging.debug(f'needs more defense to construct res buildings') 
            continue
          city.tiles.sort(key=lambda x: x.hill, reverse=True)

        for t in city.tiles:
          t.update(self)
          if t.around_threat or t.threat: continue
          if unrest_t in b.tags and t.public_order > 20: continue
          building = b(self, t)
          if building.can_build():
            city.add_building(building, t)
            logging.debug(f'{building} added at {t} {t.cords}.')
            count = 0
            break
    
  def check_events(self):
    pass

  def get_free_units(self):
    units_free = [it for it in self.units if  it.scout == 0 and it.settler == 0
           and it.goto == [] and it.group == []
           and it.leader == None and it.goal == None
           and it.comm == 0 and it.mp[0] > 1]
    
    self.units_free = []
    for i in units_free:
      i.pos.update(i.nation)
      if i.pos.around_threat + i.pos.threat > i.pos.defense: continue
      self.units_free += [i]
    
    return self.units_free

  def get_groups(self):
    # self.update(self.map)
    self.groups = [i for i in self.units if i.goal and i.hp_total > 0]
    self.groups_free = [i for i in self.groups if i.mp[0] == i.mp[1]
                        and i.goto == []]

  def improve_food(self, city):
    logging.info(f'build_food_upgrade.')
    # food upgrades.
    buildings = [b for b in city.buildings_food_complete if b.upgrade]
    logging.debug(f'upgradables {len(buildings)=:}.')
    factor = city.nation.food_limit_upgrades
    if city.grouth_total >= 5: factor *= 4
    if city.grouth_total >= 4: factor *= 3
    if city.grouth_total >= 3: factor *= 2
    for b in buildings:
      if b.pos.around_threat + b.pos.threat > b.pos.defense: continue
      count = 1
      if b.pos.pop / b.pos.food * 100 < 70:
        logging.debug(f'food not need.')
        b.pos.log = f"turn {b.pos.world.turn}, food not need."
        continue
      if city.nation.gold - factor >= factor:
        logging.debug(f'factor True.')
        b.pos.log = f'turn {b.pos.world.turn}, factor True.'
        count = 1
      
      if count == 0: continue
      upg = choice(b.upgrade)(self, self.pos)
      
      if upg.gold < self.gold:
        b.improve(upg)

  def improve_military(self, city):
    logging.info(f'build_military_upgrade.')
    # military upgrades.
    buildings = [b for b in city.buildings_military_complete if b.upgrade]
    city.military_upgrades = []
    logging.debug(f'upgradables {len(buildings)=:}.')
    for b in buildings:
      city.military_upgrades += b.upgrade
    for b in buildings:
      logging.debug(f'{b.name}')
      upg = choice(b.upgrade)(self, self.pos)
      
      if upg.gold + self.military_limit_upgrades < self.gold:
        b.improve(upg)

  def improve_misc(self, city):
    logging.info(f'build_misc_upgrade.')
    # misc upgrades.
    buildings = [b for b in city.buildings if b.upgrade and b.is_complete
                 and any(i in b.tags for i in [resource_t, unrest_t])]
    logging.debug(f'upgradables {len(buildings)=:}.')
    for b in buildings:
      upg = choice(b.upgrade)(self, self.pos)
      
      if upg.gold < self.gold:
        b.improve(upg)

  def is_allowed_tiles(self, tile):
    info = 0
    go = 1
    if tile.around_desert < self.allow_around_desert: 
      go = 0
      if info: logging.debug(f'decert.')
    if tile.around_forest < self.allow_around_forest: 
      go = 0
      if info: logging.debug(f'forest.')
    if tile.around_glacier < self.allow_around_glacier: 
      go = 0
      if info: logging.debug(f'glacier.')
    if tile.around_grassland < self.allow_around_grassland: 
      go = 0
      if info: logging.debug(f'grass.')
    if tile.around_hill < self.allow_around_hill: 
      go = 0
      if info: logging.debug(f'hill.')
    if tile.around_mountain < self.allow_around_montain: 
      go = 0
      if info: logging.debug(f'mountain.')
    if tile.around_coast < self.allow_around_ocean: 
      go = 0
      if info: logging.debug(f'coast.')
    if tile.around_plains < self.allow_around_plains: 
      go = 0
      if info: logging.debug(f'plains.')
    if tile.around_swamp < self.allow_around_swamp: 
      go = 0
      if info: logging.debug(f'swamp.')
    if tile.around_tundra < self.allow_around_tundra: 
      go = 0
      if info: logging.debug(f'tundra.')
    if tile.around_volcano < self.allow_around_volcano: 
      go = 0
      if info: logging.debug(f'volcan.')
    return go
  
  def is_unallowed_tiles(self, tile):
    stop = 0
    if tile.around_desert > self.unallow_around_desert: stop = 1
    if tile.around_forest > self.unallow_around_forest: stop = 1
    if tile.around_glacier > self.unallow_around_glacier: stop = 1
    if tile.around_grassland > self.unallow_around_grassland: stop = 1
    if tile.around_hill > self.unallow_around_hill: stop = 1
    if tile.around_mountain > self.unallow_around_montain: stop = 1
    if tile.around_coast > self.unallow_around_ocean: stop = 1
    if tile.around_plains > self.unallow_around_plains: stop = 1
    if tile.around_swamp > self.unallow_around_swamp: stop = 1
    if tile.around_tundra > self.unallow_around_tundra: stop = 1
    if tile.around_volcano > self.unallow_around_volcano: stop = 1
    return stop
  
  def launch_event(self):
    pass
  
  def set_hidden_buildings(self):
    buildings = []
    for t in self.map:
      if t.sight == 0: continue
      buildings += [bu for bu in t.buildings 
                    if bu.type == building_t]
      # [print(f'{b.name} {b.type}.') for b in buildings]
      buildings = [b for b in buildings if self != b.nation or self not in b.nations]
    
    [bu.set_hidden(self) for bu in buildings]

  def set_income(self):
    self.last_income = 0
    self.last_outcome = 0
    [ct.income_change() for ct in self.cities]
    [ct.start_turn() for ct in self.cities]
    self.last_income += self.raid_income
    msg1 = f'{income_t} {self.last_income}.'
    msg2 = f'lost by raiders {self.last_outcome}.'
    msg3 = f'{total_t} {self.last_income-self.last_outcome}.'
    self.log[-1] += [msg1, msg2, msg3]
    self.gold += round(self.last_income - self.last_outcome)
    self.raid_income = 0
    self.devlog[-1] += [f'starts with {self.gold} gold.']

  def set_new_city_req(self):
    cities = len([i for i in self.cities])
    self.city_req_pop = self.city_req_pop_base * (cities)
  
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
        logging.debug(f'{nt} descubierta.')
        sleep(loadsound('notify1') / 2)
        
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
      logging.debug(f'naciones descubiertas {len(self.seen_nations)}.')
      for nt in self.seen_nations:
        logging.debug(f'{nt}')
        logging.debug(f'casillas {len(nt.nations_tiles)}.')
        logging.debug(f'unidades {len(nt.seen_units)}.')
        logging.debug(f'score {nt.mean_score}.')

  def set_tiles_defense(self):
    for t in self.tiles:
      t.defense_req = t.income * 0.025
      if t.corpses: t.defense_req += 40
      buildings = [b for b in t.buildings if b.nation != self and self in b.nations]
      if t.buildings: 
        t.defense_req += 30 * len(t.buildings)
      if t.surf.name in [forest_t, swamp_t]: 
        t.defense_req += 20
      if t.hill:
        t.defense_req += 20
      if t.around_nations: t.defense_req += 40
      if t.unrest >= 15 and t.pop >= 40: t.defense_req += t.unrest // 2

  def start_turn(self):
    if self.pos: world = self.pos.world
    else: world = self.world
    if world.turn == 0: msg = f'{turn_t} {world.turn+1}.' 
    else: msg = f'{turn_t} {world.turn}.'
    
    self.log += [[msg]]
    self.devlog += [[msg]]
    msg = f'{world.ambient.stime}, {world.ambient.sseason} \
    {world.ambient.smonth}, {world.ambient.syear}.'
    self.log[-1] += [msg]
    [ct.check_events() for ct in self.cities]

  def status(self, info=0):
    # self.defense_need = 0
    self.income = sum(i.income_total for i in self.cities)
    self.pop_military = 0
    self.pop = 0
    self.pop_total = 0
    for ct in self.cities:
      self.pop += ct.pop
      
      for uni in self.units: 
        self.pop_military += uni.pop
    
    self.pop_total = self.pop_military + self.pop
    self.military_percent = round(self.pop_military * 100 / self.pop_total)
    self.pop_percent = round(self.pop * 100 / self.pop_total)
    
    self.upkeep_limit_percent = self.upkeep_base
    self.upkeep_limit_percent = self.upkeep_limit_percent + (self.pop / self.upkeep_change)
    if self.upkeep_limit_percent > 100: self.upkeep_limit_percent = 100
    self. upkeep_limit = round(self.upkeep_limit_percent * self.income / 100)
    
    if info:
      logging.debug(f'estado de {self}.')
      logging.debug(f'necesita {self.defense_need} defensa.')
      logging.debug(f'civiles: {self.pop}, ({self.pop_percent}%).')
      logging.debug(f'militares: {self.pop_military} ({self.military_percent}%).')
      logging.debug(f'población total {self.pop_total}.')
      logging.debug(f'ingresos {self.income}.')
      logging.debug(f'gastos {self.upkeep}., ({self.upkeep_percent}%).')

  def update(self, scenary):
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
        if uni.nation == self and uni.hp_total >= 1:
          self.units.append(uni)
    for i in self.units: i.update()
    for uni in self.units:
      if animal_t in uni.traits: self.units_animal.append(uni)
      if uni.can_fly: self.units_fly.append(uni)
      if human_t in uni.traits: self.units_human.append(uni)
      if uni.rng + uni.rng_mod < 6: self.units_melee.append(uni)
      if mounted_t in uni.traits: self.units_mounted.append(uni)
      if uni.pn + uni.pn_mod: self.units_piercing.append(uni) 
      if uni.rng + uni.rng_mod >= 6: self.units_ranged.append(uni)
      if sacred_t in uni.traits: self.units_sacred.append(uni)
      if undead_t in uni.traits: self.units_undead.append(uni)
    
    self.production = []
    for c in self.cities: 
      for p in c.production:
        self.production.append(p) 
    self.units_comm = [it for it in self.units if it.comm]
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
    
    if self.cities: self.pos = self.cities[0].pos
    else: self.pos = None
    self.set_new_city_req()
    self.units.sort(key=lambda x: len(x.group))
    # expanding.
    self.expanding = 0
    if any(i for i in [ct.expanding for ct in self.cities]): self.expanding = 1
    # print(f'time {time()-init}.')



class Unit:
  name = str()
  nick = str()
  units = 0
  unique = 0
  sts = 0
  type = str()
  traits = []
  comm = 0
  unique = 0
  gold = 0
  upkeep = 0
  resource_cost = 0
  pop = 0
  food = 0
  sk = []
  terrain_skills = []

  hp = 0
  sight = 1
  mp = []
  moves = 0
  resolve = 0
  po = 0
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

  att = 0
  damage = 0
  javelins = 0
  rng = 1
  mrng = 0
  off = 0
  str = 0
  pn = 0
  offensive_skills = []
  other_skills = [] 
  
  armor_ign = 0
  damage_critical = 0
  damage_charge = 0
  damage_sacred = 0
  id = 0
  hit_rolls = 1
  rng = 1
  stealth = 0
  hp_res = 1
  hp_res_mod = 0
  other_skills = []

  ai = 1
  align = None
  anticav = 0
  attacking = 0
  auto_explore = 0
  blocked = 0
  can_burn = 0
  can_charge = 0
  charge = 1
  can_fly = 0
  can_hide = 1
  can_join = 1
  can_raid = 0
  can_recall = 1
  can_regroup = 0
  can_retreat = 1
  city = None
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
    self.history = Empty()
    self.history.kills_record = 0
    self.history.raids = 0
    self.history.turns = 1
    self.nation = nation
    self.defensive_skills = [i(self) for i in self.defensive_skills]
    self.global_skills = [i(self) for i in self.global_skills]
    self.offensive_skills = [i(self) for i in self.offensive_skills]
    self.other_skills = [i for i in self.other_skills]
    self.traits = [i for i in self.traits]
    self.terrain_skills = [i(self) for i in self.terrain_skills]
    self.mp = [i for i in self.mp]
    self.food_total = self.food * self.units
    self.upkeep_total = self.upkeep * self.units

    self.battle_log = []
    self.buildings = []
    self.corpses = [Skeleton]
    self.deads = []
    self.effects = []
    self.favhill = [0, 1]
    self.favsoil = [coast_t, glacier_t, grassland_t, plains_t, ocean_t, tundra_t, waste_t]
    self.favsurf = [none_t, forest_t, swamp_t]
    self.goto = []
    self.group = []
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
    if self.nick: name = f'{self.nick}. '
    else: name = ''
    if self.units > 1: name += f'{self.units}'
    name += f' {self.name}'
    
    # if self.show_info == 0: name += f' id {self.id}.'
    return name

  def add_corpses(self, pos):
    corpses = sum(self.deads)
    self.deads = []
    unit = self.__class__(self.nation)
    unit.deads = [corpses]
    unit.hp_total = 0
    unit.units = 0
    unit.pos = self.pos
    pos.units += [unit]

  def auto_attack(self):
    local_units = self.pos.get_units(self.nation)
    target = self.set_attack()
    if target:
      self.combat_menu(self.pos, target)
      self.update()
      msg = f'ataque invisible.'
      self.log[-1].append(msg)
      return 1

  def autokill(self):
    if self.pos.get_nearest_nation() >= 6 and self in self.pos.world.units:
      self.hp_total = 0
      loadsound('set9')

  def attrition(self):
    if self.pos.world.turn < 2 or self.hp_total < 1: return 
    self.pos.update(self.nation)
    food = self.pos.food_need - self.pos.food
    if food >= 80: food = 80
    resolve = self.resolve + self.resolve_mod - round(food / 10)
    roll = basics.roll_dice(1)
    logging.debug(f'{food =: }, {resolve =: } {roll =: }.')
    if food > 0 and self.food and roll >= resolve:
      if self.desert_survival and self.pos.name == waste_t and basics.roll_dice(1) >= 3:
        logging.debug(f'sobreviviente del desierto.')
        return
      try:
        self.hp_total -= randint(1, ceil(food * self.hp_total / 100))
      except:
        Pdb().set_trace()
      if self.hp_total < 1:
        msg = f'{self} se ha disuelto por atrición.'
        self.nation.log[-1].append(msg)
        sleep(loadsound('notify18') * 0.5)

  def basic_info(self):
    sp.speak(f'{self}', 1)
    if self.other_skills:
      loadsound('set9', channel=ch5)
      for sk in self.other_skills: sp.speak(f'{sk.name}')
    sp.speak(f'{self.nation}.')
    sp.speak(f'hp {self.hp_total}.')
    if self.hidden:
      loadsound('hidden1', vol=0.5)
      sp.speak(f'{hidden_t}.')
    if self.nation == self.pos.world.nations[self.pos.world.player_num]:
      sp.speak(f'mp {self.mp[0]} {of_t} {self.mp[1]}.')
    if self.goto and isinstance(self.goto[0], list):
      loadsound('walk_ft1')
      goto = self.goto[0][1]
      cord = ''
      if self.pos.y < goto.y: cord += f'{south_t}.' 
      if self.pos.y > goto.y: cord += f'{north_t}.'
      if self.pos.x < goto.x: cord += f' { east_t}.'  
      if self.pos.x > goto.x: cord += f' {west_t}.'
      sp.speak(f'{heading_to_t} {cord}')
      if self.goto[0][1] in self.pos.world.nations[self.pos.world.player_num].map:
        sp.speak(f'{self.goto[0][1]}.')
        sp.speak(self.goto[0][1].cords)
      else: sp.speak(f'...')

  def break_group(self):
    logging.debug(f'{self} rompe grupo.')
    loadsound('set1')
    # print(f'{self} breaks group in {self.pos} {self.pos.cords}.')
    self.group_base = 0
    self.group_score = 0
    for i in self.group: 
      i.leader = None
      i.goto = []
    self.goal = None
    self.goto = []
    self.group = []

  def burn(self, cost=0):
    buildings = [b for b in self.pos.buildings if b.type == building_t and b.nation != self.nation
                 and self.nation in b.nations and b.resource_cost[0] > 0]
    if buildings and self.mp[0] >= cost and self.can_burn:
      if [i for i in self.pos.units
          if i.nation != self.nation]:
        return
      self.pos.update(self.pos.nation)
      
      self.update()
      building = choice(buildings)
      damage = (self.damage + self.damage_mod) * self.att
      damage *= self.units
      if self.resolve + self.resolve_mod >= 7: damage *= 0.3
      if self.resolve + self.resolve_mod >= 5: damage *= 0.2
      else: damage *= 0.1
      building.resource_cost[0] -= damage
      self.pos.burned = 1
      msg = f'{self} {burn_t} {building}. {in_t} {self.pos.city} {self.pos.cords}'
      self.log[-1].append(msg)
      self.nation.log[-1].append(msg)
      if self.pos.nation and self.nation != self.pos.nation: self.pos.nation.log[-1].append(msg)
      logging.debug(msg)
      if building.resource_cost[0] < 1:
        msg = f'{building} {has_been_destroyed_t} {in_t} {self.pos.cords}.'
        self.log[-1].append(msg)
        self.nation.log[-1].append(msg)
        if self.pos.nation and self.nation != self.pos.nation: self.pos.nation.log[-1].append(msg)
        if building.nation in self.pos.world.random_nations: self.pos.world.log[-1] += [msg]
        logging.debug(msg)
        gold = building.gold // 2
        self.nation.gold += gold
        msg = [f'{gold} {gold_t}.']
        self.log[-1].append(msg)
        self.nation.log[-1].append(msg)
        if self.pos.nation and self.nation != self.pos.nation: self.pos.nation.log[-1].append(msg)
        logging.debug(msg)
      if self.pos.nation and any(i for i in [self.nation.show_info, self.pos.nation.show_info]): 
        sleep(loadsound('build_burn01', channel=ch3) * 0.5)

  def can_pass(self, pos):
    try:
      if pos.soil.name in self.soil and pos.surf.name in self.surf: return True
    except: Pdb().set_trace()

  def check_enemy(self, pos, is_city=0, info=0):
    if info: logging.debug(f'check enemy, {is_city=:}.')
    pos.update(self.nation)
    if is_city and self.nation != pos.nation:
      self.revealed = 1
      for i in pos.units:
        i.revealed = 1
        i.update()
    self.update()
    for uni in pos.units:
      if self.hidden == 0 and uni.nation != self.nation and uni.hidden == 0:
        logging.warning(f'enemigo {uni}.')
        return 1

  def check_position(self):
    logging.debug(f'checking position.')
    if self.pos.is_city and self.nation != self.pos.nation and self.hidden == 0:
      if self.check_enemy(self.pos, is_city=1) == None: 
        if self.nation in self.pos.world.nations and self.pos.defense >= 50 * self.pos.city.pop / 100: take_city(self)
        elif self.nation not in self.pos.world.nations and self.pos.defense >= 100 * self.pos.city.pop / 100: take_city(self) 

  def check_ready(self):
    go = 1
    if self.group_score > 0 or self.group:
      # logging.debug(f'grupo de {self}, {self.group_score} de {self.group_base}.')
      if self.group_score > 0: self.create_group(self.group_base)
      for i in self.group:
        logging.debug(f'{i} pos {i.pos.cords}. {self} pos {self.pos.cords}.')
        if i.pos != self.pos: go = 0
        if i.mp[0] < self.mp[0]: go = 0
      if self.group_score > 0: go = 0
      if self.going > 0: go = 1
    if self.group and go == 0: logging.debug(f'go {go}.')
    return go
  
  def combat_menu(self, pos, target=None, dist=0, info=0):
    self.update()
    if self not in  self.pos.units:
      logging.debug(f'self not in self.pos')
    _units = [it for it in pos.units if it.nation != self.nation]
    [it.update() for it in _units]
    _units.sort(key=lambda x: sum([x.off, x.off_mod, x.str, x.str_mod]), reverse=True)
    _units.sort(key=lambda x: x.units, reverse=True)
    _units.sort(key=lambda x: x.rng >= 6, reverse=True)
    _units.sort(key=lambda x: x.comm)
    _units.sort(key=lambda x: x.mp[0] > 0, reverse=True)
    if info: logging.debug(f'distancia inicial {dist}.')
    go = 1
    if target == None: target = _units[0]
    dist = max(self.rng + self.rng_mod, self.mrng, target.rng + target.rng_mod, target.mrng)
    if self.hidden: dist = self.rng + self.rng_mod
    dist += roll_dice(1)
    self.dist = dist
    self.pos.update()
    target.pos.update(target.nation)
    self.attacking = 1
    self.target = target
    self.won = 0
    target.attacking = 0
    target.can_retreat = 1
    target.target = self
    target.won = 0
    units = [self, target]
    if target.pos.city: msg1 = [f'ataque en {target.pos.city}, {target.pos}, {target.pos.cords}  de {self.pos}, {self.pos.cords}.']
    else: msg1 = [f'ataque en {target.pos}, {target.pos.cords}  de {self.pos}, {self.pos.cords}.']
    if info:logging.info(msg1[0])
    msg2 = f'{self} ({self.nation}) ataca a {target} ({target.nation}).'
    if info:logging.info(msg2)
    if info:logging.info(f'hp {self} {self.hp_total}, target {target} {target.hp_total}.')
    if info:logging.info(f'ranking {self.ranking} VS {target.ranking}.')
    info = 1 if any(i.show_info == 1 for i in units) else 0
    if info: sleep(loadsound('warn4') / 2)
    for i in units:
      if i.damage_charge: i.can_charge = 1
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
      i.strikes = []
      i.raised = []
      i.temp_log = None
      i.wounds = []
    gold_self = self.set_value()
    gold_target = target.set_value()
    _round = 1
    while self.hp_total > 0 or target.hp_total > 0:
      if go:
        # logging.debug(f'ronda {_round}.')
        shuffle(units)
        [i.update() for i in units]
        units.sort(key=lambda x: x.moves + x.moves_mod, reverse=True)
        units.sort(key=lambda x: x.hidden, reverse=True)
        for i in units:
          i.attack = 1
          i.attacks.append(0)
          i.aa_log = []
          i.ac_log = []
          i.ba_log = []
          i.bc_log = []
          i.damage_done.append(0)
          i.deads.append(0)
          i.fled.append(0)
          i.hits_armor_blocked += [0]
          i.hits_blocked += [0]
          i.hits_body += [0]
          i.hits_head += [0]
          i.hits_resisted += [0]
          i.hits_shield_blocked += [0]
          i.hits_failed += [0]
          i.raised += [0]
          i.strikes += {0} 
          i.target.c_units = i.target.units
          i.wounds.append(0)
        
        # log
        temp_log = [
          f'{round_t} {_round}.',
          f'{units[0]} {health_t} {units[0].hp_total}. ranking {units[0].ranking} \
          vs {units[1]} {health_t} {units[1].hp_total}. ranking {units[1].ranking}.',
           
          f'{resolve_t} {units[0].resolve+units[0].resolve_mod}. {units[1].resolve+units[1].resolve_mod}.',
          f'{moves_t} {units[0].moves+units[0].moves_mod}. {units[1].moves+units[1].moves_mod}.',
          f'{skills_t} {units[0].skill_names}. {units[1].skill_names}.',
          f'{effects_t} {units[0].effects}. {units[1].effects}.', ]
          
        for i in units:
          i.temp_log = temp_log
          i.combat_round = _round
        
        # before combat.
        [i.before_combat() for i in units]
        for uni in units:
          if (uni.attacking 
              or uni.rng + uni.rng_mod < uni.target.rng + uni.target.rng_mod 
              and dist > uni.rng + uni.rng_mod):
            dist = self.combat_moves(dist, uni)
            self.dist, target.dist = [dist, dist]
            uni.temp_log.insert(2, f'{distance_t} {units[0].dist}, {units[0].rng+units[0].rng_mod}. {units[1].dist}, {units[1].rng+units[1].rng_mod}.',)
        # combat.
        for uni in units:
          if uni.hp_total > 0 and uni.rng + uni.rng_mod >= dist:
            uni.before_attack()
            uni.combat_fight(dist, _round)
            uni.after_attack()
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
        self.combat_log(units)
        _round += 1
        for i in units:
          if dist == 1: i.charging = 0
        
        # end of combat.
        if any(i.hp_total < 1 for i in units):
          if self.nation in self.pos.world.nations: self.mp[0] -= 1
          [i.stats_battle() for i in [self, target] if i.hp_total >= 1]
          self.combat_post(target, info)
          for i in units:
            msg = [i for i in msg1]
            msg += i.battle_log
            i.log[-1] += [msg, msg2]
            i.nation.log[-1] += [msg, msg2]
            if i.nation in i.pos.world.random_nations: i.pos.world.log[-1] += [msg, msg2]
            i.add_corpses(target.pos)
          if self.hp_total < 1:
            if self.pos != target.pos and self in self.pos.units: self.pos.units.remove(self)
            msg = f'{target} ({target.nation}) a vencido.'
            if target.show_info: sp.speak(msg)
            logging.info(msg)
            target.log[-1].append(msg)
            target.nation.log[-1].append(msg)
            target.pos.world.log[-1] += [msg]
            self.nation.log[-1].append(msg)
            if gold_self:
              msg1 = f'gana {gold_self} {gold_t}.'
              target.nation.gold += gold_self
              target.nation.log[-1].append(msg1)
              logging.debug(msg1)
            if info:
              sp.speak(msg)
              sleep(loadsound('notify18') * 0.5)
            logging.info(msg)
            # check_position(target)
            return 0
          elif target.hp_total < 1:
            msg = f'{self} ({self.nation}) ha vencido.'
            self.log[-1].append(msg)
            self.nation.log[-1].append(msg)
            target.nation.log[-1].append(msg)
            target.pos.world.log[-1] += [msg]
            if gold_target:
              msg1 = f'gana {gold_target} {gold_t}.'
              self.nation.gold += gold_target
              self.nation.log[-1].append(msg1)
              logging.debug(msg1)
            if info:
              sp.speak(msg=msg)
              sleep(loadsound('win1') * 0.5)
            logging.info(msg)
            # check_position(self)
            return 1

  def combat_fight(self, _round, info=0):
    self.update()
    target = self.target
    target.update()
    target.c_units = target.units
    if info: logging.info(f'{self} total hp {self.hp_total} ataca.')
    if target.armor: armor = target.armor.name
    else: armor = 'none'
    if target.shield: shield = target.shield.name
    else: shield = 'none'
    log = self.temp_log
    log += [  
      f'{self} {attacking_t}.',
      f'att {self.att + self.att_mod} (+{self.att_mod}).'
      f'{damage_t} {self.damage + self.damage_mod} (+{self.damage_mod}). '
      f'sacred damage {self.damage_sacred_mod}.',
      f'off {self.off + self.off_mod} (+{self.off_mod}). '
      f'{target} dfs {target.dfs+ target.dfs_mod} (+{target.dfs_mod}).',
      f'str {self.str + self.str_mod} (+{self.str_mod}). '
      f'{target} res {target.res+ target.res_mod} (+{target.res_mod})',
      f'armor {armor}, shield {shield}.',
      ]
    for uni in range(self.units):
      if info: logging.debug(f'unidad {uni+1} de {self.units}.')
      attacks = self.att + self.att_mod
      for i in range(attacks):
        if target.hp_total < 1: break
        self.attacks[-1] += 1
        if info: logging.debug(f'ataque {i+1} de {attacks}.')
        target.c_units = target.units
        damage = self.damage + self.damage_mod
        
        # hit
        if self.combat_hits(target,info)== None: continue
        
        # shield.
        if self.combat_shield(target, info): continue
        
        #wounds:
        wounds = self.combat_wounds(target, info)
        if wounds == None: continue
        else: hit_to = wounds 
        
        # armor
        if self.combat_armors(hit_to, target, info) == 1: continue
        
        if hit_to == 'body': self.hits_body[-1] += 1
        elif hit_to == 'head': 
          self.hits_head[-1] += 1
          damage += round(damage*1.5)
        if info: logging.debug(f"{hit_to}")
        
        if undead_t in target.traits:
          damage += self.damage_sacred
          if info: logging.debug(f'damage holy {self.damage_sacred}.')
        # if damage > self.target.hp: damage = self.target.hp
        if self.can_charge and self.charge:
          damage += self.damage_charge
          if info: logging.debug(f'carga {self.damage_charge}.')
        target.hp_total -= (damage)
        if info: logging.info(f'{target} recibe {damage} de daño.')
        target.update()
        self.damage_done[-1] += damage
        target.deads[-1] += target.c_units - target.units
    
    self.hits_failed[-1] = self.attacks[-1] - self.strikes[-1]
    self.charge = 0
    if self.damage_done[-1] and self.target.hidden: 
      self.temp_log += [f'{self.target} revealed.']
      self.target.revealed = 1
    
    log += [  
      f'{attacks_t} {self.attacks[-1]}, {hits_failed_t} {self.hits_failed[-1]}, '
      f'{hits_t} {self.strikes[-1]}.',
      ]
    if self.hits_resisted[-1]: log += [f'resisted {self.hits_resisted[-1]}.']
    if self.hits_armor_blocked[-1]: log += [f'armor blocked {self.hits_armor_blocked[-1]}.']
    if self.hits_shield_blocked[-1]: log += [f'shield blocked {self.hits_shield_blocked[-1]}.']
    log += [f'to the head {self.hits_head[-1]}, to the body {self.hits_body[-1]}.',
      f'{wounds_t} {self.hits_body[-1]+self.hits_head[-1]}, {damage_t} {self.damage_done[-1]}, '
      f'{deads_t} {self.target.deads[-1]}.'
      ]

  def combat_armors(self,hit_to, target,info=0):
    if info:logging.info(f"armors.")
    if hit_to == 'body':
      roll = basics.roll_dice(1)
      armor = target.arm + target.arm_mod
      if target.armor: armor += target.armor.arm
      if target.armor_ign + target.armor_ign_mod == 0: armor -= self.pn + self.pn_mod
      else: 
        if info: logging.debug(f'{target} ignora pn.')
      armor = basics.get_armor_mod(armor)
      if info: logging.debug(f'roll{roll} necesita {armor}.')
      if roll >= armor and armor > 0:
        self.hits_armor_blocked[-1] += 1
        return 1
  def combat_hits(self, target, info=0):
    if info:logging.info(f"hits.")
    hit_rolls = self.hit_rolls + self.hit_rolls_mod
    for i in range(hit_rolls):
          if info: logging.debug(f'impactos {i} de {hit_rolls}')
          hit_roll = basics.roll_dice(1)
          if info: logging.debug(f'{hit_roll=:}.')
          off = self.off + self.off_mod
          if self.rng + self.rng_mod >= 6 and self.dist < self.rng + self.rng_mod: 
            off -= 1
          off_need = off
          if info: logging.debug(f'off_need1  {off_need}.')
          off_need -= target.dfs + target.dfs_mod
          if info: logging.debug(f'off_need2 {off_need}.')
          off_need = basics.get_hit_mod(off_need)
          if info: logging.debug(f'off_need3 {off_need}.')
          if hit_roll >= off_need:
            self.strikes[-1] += 1
            return 1
  
  
  def combat_shield(self, target, info=0):
    if info:logging.info(f"shield.")
    if target.shield:
      shield_need = basics.roll_dice(1)
      shield = basics.get_armor_mod(target.shield.dfs)
      if shield > shield_need : 
        self.hits_shield_blocked[-1] += 1
        return 1
  def combat_wounds(self,target,info=0):
    if info:logging.info(f"wounds.")
    hit_to = 'body'
    wound_roll = basics.roll_dice(1)
    if info:logging.debug(f'roll {wound_roll=}')
    wound_need = self.str + self.str_mod
    if info: logging.debug(f'wound_need1 {wound_need}.')
    res = target.res + target.res_mod
    roll = basics.roll_dice(1)
    if self.rng + self.rng_mod < 6:
      head_factor = 6
      size_factor = (self.size + self.size_mod) - (self.target.size + self.target.size_mod)
      head_factor -= size_factor
      head_factor -= (self.rng + self.rng_mod)
    elif self.rng + self.rng_mod >= 6 or self.can_fly: head_factor = 6
    if roll >= head_factor:
      hit_to = 'head'
      if info:logging.debug(f'hit to the head.')
      res = target.hres + target.hres_mod
    wound_need -= res
    if info: logging.debug(f'wound_need2 {wound_need}.')
    wound_need = basics.get_wound_mod(wound_need)
    if info: logging.debug(f'wound_need3 {wound_need}.')
    if wound_roll < wound_need:
      self.hits_resisted[-1] += 1
    else: return 1, hit_to
  def after_attack(self):
    self.update()
    for sk in self.skills:
      if sk.type == 'after attack': sk.run(self)
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
      if sk.type == 'before attack': sk.run(self)
      if self.ba_log: self.temp_log += self.ba_log

  def before_combat(self):
    self.update()
    for sk in self.skills:
      if sk.type == 'before combat':
        sk.run(self)
        if self. bc_log: self.temp_log += self.bc_log

  def combat_moves(self, dist, info=1):
      moves = self.moves + self.moves_mod
      if info:logging.debug(f'distancia de {self}  {dist}.')
      if dist > self.rng + self.rng_mod:
        move = roll_dice(2)
        if self.can_fly: move += 2
        if info: logging.debug(f'move {move}. moves {moves}.')
        if move > moves: move = moves
        if self.hidden: move += 2
        dist -= move
        if dist < 1: dist = 1
        if dist < self.rng + self.rng_mod: dist = self.rng + self.rng_mod
        if info: logging.debug(f'distancia final {dist}.')
      return dist

  def combat_log(self, units):
    log = units[0].temp_log
    # for i in units:
      # if i.aa_log: log += i.aa_log
      # if i.ac_log: log += i.ac_log 
      # if i.ba_log: log += i.ba_log
      # if i.bc_log: log += i.bc_log
    # if units[0].aa_log: log += units[0].aa_log
    # elif units[1].aa_log: log += units[1].aa_log
    # log += [
      # f'{raised_t} {units[0].raised[-1]}. {units[1].raised[-1]}.',
      # f'{fled_t} {units[0].fled[-1]}. {units[1].fled[-1]}',
      # ]
    for uni in units:
      uni.battle_log.append(log)

  def combat_post(self, target, info=0):
    logging.info(f'combat post.')
    for i in [self, target]:
      if i.hp_total > 0: i.pos.update(i.nation)
      if  i.hp_total < 1 and i.attacking: i.pos = i.target.pos
      i.attacking = 0
      i.target = None
      if i.hp_total > 0:
        skills = [sk for sk in i.skills if sk.type == 'pos combat']
        [sk(i) for sk in skills]
      if i.hp_total < 1 and sum(i.fled) >= 1 and i.can_retreat:
        if info: logging.debug(f'{i} pierde.')
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
        if info: logging.debug(f'{unit} huyen {sum(i.fled)}.')
        if unit.units < unit.min_units / 4: continue
        unit.pos.units.append(unit)
        if unit.can_retreat:
          if info:logging.debug(f'se retirará.')
          unit.mp[0] = unit.mp[1]
          tile = unit.get_retreat_pos(info=1)
          unit.move_set(tile)

  def combat_retreat(self, info=0):
    if info: logging.debug(f' combat retreat.')
    self.update()
    if info: logging.debug(f'{self} retreat units {self.units} hp {self.hp_total}.')
    if death_t in self.traits:
      logging.debug(f'{death_t}.')
      return
    dead = self.deads[-1]
    if info: logging.info(f'{self} loses {dead}.')
    
    roll = roll_dice(1)
    if info: logging.debug(f'dado {roll}.')
    roll += dead
    if info: logging.debug(f'dado {roll}.')
    resolve = self.resolve + self.resolve_mod
    if info: logging.debug(f'{self} resolve {resolve}.')
    if roll > resolve:
      retreat = roll - resolve
      if retreat > self.units: retreat = self.units
      self.hp_total -= retreat * self.hp 
      msg = f'{fleed_t} {retreat} {self}.'
      self.fled[-1] += retreat
      self.temp_log += [msg]
      if info: logging.debug(msg)
      self.update()
      if info: logging.debug(f'total huídos {self.fled}.')

  def create_group(self, score, same_mp=0):
    if score < 0: return
    logging.debug(f'{self} crea grupo de {score}')
    self.group_base = score
    self.group_score = self.group_base
    for i in self.group:
      if i.pos == self.pos or self.pos in i.goto_pos: 
        self.group_score -= i.ranking
    sq = [s for s in self.pos.get_near_tiles(3) if s.around_threat + s.threat == 0]
    units = [] 
    for s in sq:
      for u in s.units:
        if (u.comm == 0 and u.goto == [] and u.goal == None): units += [u]
    if same_mp: units = [i for i in units if i.mp[1] >= self.mp[1]] 
    shuffle(units)
    units.sort(key=lambda x: x.pos.get_distance(self.pos, x.pos))
    if self.rng + self.rng_mod <= 6:
      units.sort(key=lambda x: x.rng >= 6, reverse=True)
    elif self.rng >= 6:
      units.sort(key=lambda x: x.off + x.off_mod, reverse=True)
    if self.settler:
      units.sort(key=lambda x: x.mp[1] == self.mp[1], reverse=True)
      units.sort(key=lambda x: x.ranking, reverse=True)
    
    logging.debug(f'disponibles {len(units)}.')
    if len(units) == 0:
      logging.debug(f'no puede crear grupo')
      return
    self.log[-1] += [f'creates group of {self.group_base}. on {self.pos} {self.pos.cords}.']
    for i in units:
      if i == self or i.pos.around_threat + i.pos.threat or i.nation != self.nation: continue
      if i.scout or i.group or i.leader: continue
      logging.debug(f'score {self.group_score}.')
      logging.debug(f'encuentra a {i}')
      if self.group_score > 0 and i not in self.group:
        self.group.append(i)
        i.leader = self
        logging.debug(f'{i} se une con {i.ranking} ranking.')
        self.group_score -= i.ranking
        logging.debug(f'quedan {self.group_score}.')
        self.log[-1] += [f'{i} on {i.pos} {i.pos.cords} added.']
        i.log[-1] += [f'added to {self} group on {self.pos} {self.pos.cords}.']
        if self.group_score < 0:
          self.group_base = 0
          logging.debug(f'grupo creado.') 
          break

  def disband(self):
    if self.city and self.can_recall:
      self.city.pop_back += self.pop
      self.nation.units.remove(self)
      self.pos.units.remove(self)
      self.nation.update(self.pos.scenary)

  def get_favland(self, pos):
    go = 1
    if pos.soil.name not in self.favsoil: go = 0
    if pos.surf.name not in self.favsurf: go = 0
    if pos.hill not in self.favhill: go = 0
    return go

  def get_retreat_pos(self,info=0):
    if info: logging.info(f"retreat_pos")
    if info:logging.debug(f'pocición inicial {self.pos} {self.pos.cords}.')
    Pdb().set_trace()
    sq = self.pos.get_near_tiles(1)
    sq = [i for i in sq
          if i.soil.name in self.soil and i.surf.name in self.surf and i != self.pos
          and (self.can_fly == 0 and i.cost <= self.mp[0])
          or (self.can_fly and i.cost_fly <= self.mp[0])]
    [s.update(self.nation) for s in sq]
    if info:logging.debug(f'{len(sq)} casillas para retirada.')
    shuffle(sq)
    sq.sort(key=lambda x: x.nation == None, reverse=True)
    sq.sort(key=lambda x: x.nation == self.nation, reverse=True)
    sq.sort(key=lambda x: x.threat)
    sq.sort(key=lambda x: x.cost)
    for i in sq:
      if info: logging.debug(f'{i}, {i.cords}.')
    for s in sq:
      if s.cost <= self.mp[1]: return sq[0]



  def get_skills(self):
    self.skills = [i for i in self.global_skills + self.terrain_skills + 
                   self.defensive_skills + self.offensive_skills + self.other_skills]
    self.skills_tags = []
    for sk in self.skills:
      self.skills_tags += sk.tags
    return self.skills
  
  def info(self, nation, sound='in1'):
    sleep(loadsound(sound))
    say = 1
    x = 0
    self.update()
    while True:
      sleep(0.1)
      if say:
        effects = [e for e in self.effects]
        if self.armor: armor = self.armor.name
        else: armor = 'no'
        if self.defensive_skills: defensive_skills = [s.name for s in self.defensive_skills]
        else: defensive_skills = 'No'
        if self.global_skills: global_skills = [s.name for s in self.global_skills]
        else: global_skills = 'No'
        if self.nation == nation: mp = f'{self.mp[0]} {of_t} {self.mp[1]}.'
        else: mp = 'X'
        if self.offensive_skills: offensive_skills = [s.name for s in self.offensive_skills]
        else: offensive_skills = 'No'
        if self.power_max: power = f'{self.power} {of_t} {self.power_max}, restores {self.power_res}.'
        else: power = f'x'
        if self.shield: shield = self.shield.name
        else: shield = 'no'
        if self.spells: spells = [s.name for s in self.spells]
        else: spells = 'No'
        if self.terrain_skills: terrain_skills = [s.name for s in self.terrain_skills]
        else: terrain_skills = 'No'
        lista = [
          f'{self}. total hp {self.hp_total}.',
          f'{squads_t} {self.squads} {of_t} {self.max_squads}, {ranking_t} {self.ranking}.',
          f'level {self.level}.',
          f'{stealth_t} {self.stealth+self.stealth_mod} ({self.stealth_mod}).',
          f'{type_t} {self.type}.',
          f'{traits_t} {self.traits}.',
          f'{size_t} {self.size}.',
          f'{gold_t} {self.gold}, {upkeep_t} {self.upkeep} ({self.upkeep_total}).',
          f'{resources_t} {self.resource_cost}.',
          f'{food_t} {self.food}, {population_t} {self.pop}.',
          f'effects {effects}.',
          f'terrain skills {terrain_skills}.',
          f'{health_t} {self.hp}. '
          f'{restores_t} {self.hp_res+self.hp_res_mod} (+{self.hp_res_mod}).',
          ]
        
        if self.demon_souls: lista += [f'demon souls {self.demon_souls}.']
        
        lista += [
          f'{magic_t} {power}.',
          f'mp {mp}.',
          f'{moves_t} {self.moves+self.moves_mod} ({self.moves_mod}).',
          f'{resolve_t} {self.resolve+self.resolve_mod} ({self.resolve_mod}).',
          f'global skills {global_skills}.',
          f'{defense_t} {self.dfs+self.dfs_mod} ({self.dfs_mod}).',
          f'{resiliency_t} {self.res+self.res_mod} ({self.res_mod}).',
          f'h res {self.hres+self.hres_mod} ({self.hres_mod}).',
          f'{basearm_t} {self.arm+self.arm_mod} ({self.arm_mod}).',
          f'{armor_t} {armor}.',
          f'{shield_t} {shield}.',
          f'defensive skills {defensive_skills}.',
          f'{attacks_t} {self.att+self.att_mod} ({self.att_mod}).',
          f'{range_t} {self.rng+self.rng_mod} ({self.rng_mod}).',
          f'{damage_t} {self.damage+self.damage_mod} ({self.damage_mod}).',
          f'sacred damage {self.damage_sacred}',
          f'{offensive_t} {self.off+self.off_mod} ({self.off_mod}).',
          f'{strength_t} {self.str+self.str_mod} ({self.str_mod}).',
          f'{piercing_t} {self.pn+self.pn_mod} ({self.pn_mod}).',
          f'offensive skills {offensive_skills}.',
          f'spells {spells}.' 
          ]
        
        sp.speak(lista[x])
        say = 0
        
      for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_UP:
            x = selector(lista, x, go="up")
            say = 1
          if event.key == pygame.K_DOWN:
            say = 1
            x = selector(lista, x, go="down")
          if event.key == pygame.K_HOME:
            x = 0
            say = 1
            loadsound('s1')
          if event.key == pygame.K_END:
            x = len(lista) - 1
            say = 1
            loadsound('s1')
          if event.key == pygame.K_PAGEUP:
            x -= 10
            say = 1
            if x < 0: x = 0
            loadsound('s1')
          if event.key == pygame.K_PAGEDOWN:
            x += 10
            say = 1
            if x >= len(lista): x = len(lista) - 1
            loadsound('s1')
          if event.key == pygame.K_s:
            self.set_auto_explore()
          if event.key == pygame.K_F12:
            sp.speak(f'debug on.', 1)
            Pdb().set_trace()
            sp.speak(f'debug off.', 1)
          if event.key == pygame.K_ESCAPE:
            sleep(loadsound('back1') / 2)
            return

  def join_units(self, units, info=0):
    if info: logging.info(f'join_units.')
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
        # print(f'divided.')
      elif i.squads + unit.squads <= unit.max_squads: item = i
      if unit.squads + item.squads > unit.max_squads: return
      unit.demon_souls = item.demon_souls
      unit.history.kills_record += item.history.kills_record
      unit.history.raids += item.history.raids
      unit.hp_total += item.hp_total
      unit.mp[0] = min(unit.mp[0], item.mp[0])
      unit.pop += item.pop
      unit.other_skills += item.other_skills
      msg = f'{item} has joined.'
      unit.log[-1] += [msg]
      item.hp_total = 0
    unit.update()
    unit.pos.update()

  def join_group(self):
    if self.leader and self.pos != self.leader.pos:
      logging.debug(f'{self} en {self.pos} {self.pos.cords} busca unirse a su lider {self.leader}.')
      if self.goto == []: self.move_set(self.leader.pos)

  def launch_event(self):
    pass

  def unit_new_turn(self):
    logging.info(f'new turn {self.pos.world.turn=:} {to_t} {self} {in_t} {self.pos.cords}.')
    # print(f'new turn {world.turn=:} {to_t} {self} {in_t} {self.pos.cords}.')
    # init = time()
    if self.hp_total < 1: return
    self.start_turn()
    self.restoring()
    self.set_hidden(self.pos)
    if (self.goal and self.goal[0] == 'stalking'
        or (self.leader and self.leader.goal and self.leader.goal[0] == 'stalking') 
        or self.scout
        and self.ai == 1):
      if self.comm == 0: self.oportunist_attack(self)
    self.join_group()
    if self.goto: 
      self.move_unit(self)
    self.attrition()
    self.maintenanse()
    # print(f'{time()-init}')

  def maintenanse(self):
    # logging.debug(f'mantenimiento de {self} de {self.nation}.')
    if self.upkeep > 0 and self.nation.gold >= self.upkeep:
      self.nation.gold -= self.upkeep_total
      logging.debug(f'{self} cobra {self.upkeep_total}.')
    elif self.upkeep > 0 and self.nation.gold < self.upkeep:
      self.pos.units.remove(self)
      self.nation.units.remove(self)
      self.city.pop_back += self.pop
      logging.debug(f'se disuelve')

  def move_set(self, goto):
    logging.debug(f"move_set {self} on {self.pos} {self.pos.cords}.")
    self.garrison = 0
    if (goto.__class__ == self.pos.__class__
        and self.can_pass(goto)):
      if self.can_fly: cost = goto.cost_fly
      elif self.can_fly == 0:
        cost = goto.cost
        if self.forest_survival and goto.surf.name == forest_t: cost -= 1
        elif self.mountain_survival and (goto.surf.name in mountain_t or goto.hill): cost -= 1
        elif self.swamp_survival and goto.surf.name == swamp_t: cost -= 1
        elif ((goto.surf.name in [forest_t, swamp_t] or goto.hill) and mounted_t in self.traits):
          self.mp[0] -= 1
      if self.goto == []: self.goto.append([cost, goto])
      elif self.goto: self.goto.insert(0, [cost, goto])
      self.move_unit()
    elif isinstance(goto, str):
      self.goto.append(goto)
      self.move_unit()
  
  def move_far(self): 
    logging.debug(f'{self} mueve lejos')
    goto = self.goto[0][1]
    
    pos = self.pos
    
    sq = self.pos.get_near_tiles(1)
    # logging.debug(f'{len(sq)} terrenos iniciales.')
    if goto.x > pos.x:
      # logging.debug(f'al este.')
      sq = [ti for ti in sq if ti.x > pos.x]
    if goto.x < self.pos.x:
      # logging.debug(f'al oeste.')
      sq = [ti for ti in sq if ti.x < self.pos.x]
    
    if goto.y < pos.y:
      # logging.debug(f'al norte.')
      sq = [ti for ti in sq if ti.y < pos.y]
    if goto.y > pos.y:
      # logging.debug(f'al sur.')
      sq = [ti for ti in sq if ti.y > pos.y]
    
    sq = [ti for ti in sq if ti.soil.name in self.soil and ti.surf.name in self.surf
          and ti != self.pos]
    shuffle(sq)
    sq.sort(key=lambda x: x.cost <= self.mp[1], reverse=True)
    sq.sort(key=lambda x: x.nation == self.nation, reverse=True)
    # logging.debug(f'{len(sq)} terrenos finales.')
    self.set_favland(sq)
    
    if roll_dice(2) <= self.fear:
      # logging.debug(f'ordena por fear.')
      sq.sort(key=lambda x: x.threat)
      sq.sort(key=lambda x: x.around_threat)
    if sq:
      self.move_set(sq[0])
    else:
      logging.debug(f'{self} en {self.pos} {self.pos.cords}. no hay donde mover.')
      sq = self.goto[0][1].get_near_tiles(2)
      sq = [ti for ti in sq if ti.soil.name in self.soil and ti.surf.name in self.surf
          and ti != self.pos and ti in self.nation.map]
      self.move_set(choice(sq))

  def move_group(self, info=0):
      logging.info(f'move group turn {self.pos.world.turn}.')
      if info: logging.debug(f'{self} {self.id} at {self.pos} {self.pos.cords}..')
      if info: logging.debug(f'goal {self.goal[0]} to {self.goal[1]}.')
      if info: logging.debug(f'leads {len(self.group)} units.')
      group = [str(i) for i in self.group]
      if self.group: logging.debug(f'{group}.')
      goto = self.goto[0][1]
      goto.update(self.nation)
    
      self.pos.update(self.nation)
      ranking = sum([i.ranking for i in [self] + self.group])
      threat = goto.threat
      if goto.hill and mountain_survival_t not in self.traits: threat *= 1.10
      if goto.surf.name == forest_t and forest_survival_t not in self.traits: threat *= 1.10
      if goto.surf.name == swamp_t and swamp_survival_t not in self.traits: threat *= 1.10
      if info: logging.debug(f'ranking {round(ranking)} vs {round(threat)}.')
    
      alt = goto.get_near_tiles(1)
      alt = [i for i in alt
            if i.get_distance(i, self.pos) == 1]
      [s.update(self.nation) for s in alt]
      alt.sort(key=lambda x: x.income, reverse=True)
      alt.sort(key=lambda x: x.bu, reverse=True)
      alt.sort(key=lambda x: x.threat)
      if self.forest_survival: alt.sort(key=lambda x: x.surf.name == forest_t, reverse=True)
      if self.swamp_survival: alt.sort(key=lambda x: x.surf.name == swamp_t, reverse=True)
      if self.mountain_survival: alt.sort(key=lambda x: x.hill, reverse=True)
      defense_roll = 5
      if self.comm: defense_roll -= 2
      if basics.roll_dice(1) >= defense_roll: 
        alt.sort(key=lambda x: x.hill and x.threat < ranking, reverse=True)
    
      if self.goal[0] == base_t:
        self.break_group()
        return
      if self.goal[0] == capture_t:
        if goto.threat > ranking * uniform(0.8, 1.2):
          if info: logging.debug(f'mayor.')
          if basics.roll_dice(1) > 2:
            if info: logging.debug(f'wait next turn.') 
            return
          
          else:
            if info: logging.debug(f'switch goto.')
            for s in alt:
              if s.threat < self.group_ranking:
                if (self.day_night 
                    and (s.nation != self.nation and s.nation != None)
                    and basics.roll_dice(1) >= 3):
                  if info: logging.debug(f'will avoid hills by night.')
                  continue
                if info: logging.debug(f'changes to {s} {s.cords}.')
                self.move_set(s)
                return
          
          if basics.roll_dice(1) > 4:
            if info: logging.debug(f'{self} go home.')
            go_home(self)
            return
        [i.move_set(self.goal[1]) for i in self.group]
        goto.update(goto.nation)
        self.update()
        if self.comm and goto.threat <= self.ranking: self.moving_unit()
        else:
          if self.group == []:
            if info: logging.debug(f'lider se retira..') 
            self.break_group()
          return
      if self.goal[0] == stalk_t:
        if self.rng + self.rng_mod > 5 and self.pos.day_night: ranking *= 0.2
        if ranking * 1.5 < threat:
          if info: logging.debug(f'mayor.')
          if basics.roll_dice(2) >= 10:
            if info: logging.debug(f'ataca.')
            if basics.roll_dice(1) >= 3: self.group.sort(key=lambda x: x.rng + x.rng_mod > 5, reverse=True)
            for i in self.group:
              if i.goto == []: i.move_set(goto)
            goto.update(self.nation)
            self.update()
            if goto.threat <= self.ranking * 1.25:
              if info: logging.debug(f'lider mueve. threat {goto.threat} ranking {self.ranking*1,5}.') 
              self.moving_unit()
              return
            if self.group: 
              if info: logging.debug(f'espera grupo.')
              return
            else:
              if info: logging.debug(f'lider se retira.')
              self.break_group()
              self.goal = None
              self.goto = []
              return
          roll = 2
          if self.pos.hill: roll += 1
          if self.pos.surf.name == forest_t: roll += 1
          if self.pos.surf.name == swamp_t: roll += 1
          if info: logging.debug(f'switch chanse {roll}.')
          if basics.roll_dice(1) >= roll:
            if info: logging.debug(f'will move.')
            for s in alt:
              if info: logging.debug(f'{s.threat =: }. {s} {s.cords}.')
              if s.threat < self.group_ranking * 0.7:
                if (self.day_night 
                    and (s.nation != self.nation and s.nation != None)
                    and basics.roll_dice(1) >= 3):
                  if info: logging.debug(f'will avoid hills by night.')
                  continue
                if info: logging.debug(f'moves to {s} {s.cords}.')
                self.move_set(s)
                return
            if info: logging.debug(f'espera.')
            return 
          if basics.roll_dice(1) >= 4:
            if info: logging.debug(f'espera')
            return
          self.break_group()
          return
        else:
          if info: logging.debug(f'just moves.')
          for i in self.group:
            if i.goto == []: i.goto = [g for g in self.goto]
          for i in self.group:
            i.moving_unit()
          goto.update(self.nation)
          self.moving_unit()

  def move_unit(self, info=1):
    self.update()
    if info:logging.debug(f'move_unit on {self.pos}, {self.pos.cords}.')
    goto = self.goto[0][1]
    if goto == self.pos:
      self.goto = []
      self.stopped = 1
      msg = f'{self} {self.nation}  detenido.'
      self.log[-1].append(msg)
      if info: logging.debug(msg)
      if self.show_info:
        sp.speak(msg=msg)
      return 0
    if self.going == 0:
      if self.check_ready() == 0:
        if info: logging.debug(f'go = 0.')
        return
    if isinstance(self.goto[0], list):
      msg = f'{self} ({self.nation}) moves to {self.goto[0][1]}., {self.goto[0][1].cords}'
      self.log[-1].append(msg)
      if info: logging.debug(msg)
      if info: logging.debug(f'mp {self.mp[0]} de {self.mp[1]}, costo {self.goto[0][0]}.')
      if self.group: 
        if info: logging.debug(f'lider, grupo {len(self.group)}.')
      elif self.leader: 
        if info: logging.debug(f'following {self.leader} on {self.leader.pos} {self.leader.pos.cords}.')
      while (self.goto and self.mp[0] > 0 and self.hp_total > 0
             and isinstance(self.goto[0], list)):
        goto = self.goto[0][1]
        square = self.pos.get_near_tiles(1)
        if goto not in square:
          self.move_far()
        
        elif goto in square:
          if self.goal and goto == self.goal[1]:
            self.move_group()
            return
          self.going = 1
          if basics.roll_dice(1) >= 2: 
            self.group.sort(key=lambda x: x.rng, reverse=True)
          for i in self.group:
            if i.pos != self.goto[0][1] and i.goto == []:
              if info: logging.debug(f'seguidor {i} {i.mp} moves')
              i.move_set(goto)
          self.moving_unit(self)
        
    elif isinstance(self.goto[0], str):
      if self.goto[0] == 'attack':
        del(self.goto[0])
        self.auto_attack()
        if self.hp_total < 1: return
      elif self.goto[0] == 'gar':
        self.garrison = 1
        if info: logging.debug(f'{self} defiende {self.pos}.')
        del(self.goto[0])
      elif self.goto[0] == 'join':
        basics.ai_join_units(self)
        if info: logging.debug(f'{self} joins.')
        del(self.goto[0])
      elif self.goto[0] == 'set':
        placement = choice(self.buildings)
        if placement(self.nation, self.pos).check_tile_req(self.pos):
          self.nation.add_city(placement, self)
        else: logging.warning(f'{self} no puede fundar aldea en {self.pos}.')

  def moving_unit(self, info=0):
    if info: logging.debug(f'mueve cerca {self} {self.id}.')
    if self.goto == []: 
      if info: logging.debug(f'sin goto')
      return
    
    mp = self.mp[0]
    cost = self.goto[0][0]
    goto = self.goto[0][1]
    if info: logging.debug(f'mp {mp}, cost {cost}.')
    # menor.
    if mp < cost:
      if info: logging.debug(f'menor.')
      self.goto[0][0] -= self.mp[0]
      self.mp[0] = 0
      if self.ai == 0: loadsound('set4')
    # mayor
    elif mp >= cost:
      if info: logging.debug(f'mayor.')
      self.mp[0] -= cost
      self.garrison = 0
      self.set_hidden(goto)
      if info: logging.debug(f'hidden {self.hidden}.')
      if self not in self.pos.units: 
        if info: logging.debug(f'not in position.')
      # chekeo de enemigos.
      if self.check_enemy(goto, goto.is_city):
        if info: logging.debug(f'hay enemigos.')
        veredict = self.combat_menu(goto)
        self.update()
        if info: logging.debug(f'hidden {self.hidden}.')
        if veredict == 0:
          # self.pos.update(self.nation)
          if info: logging.debug(f'veredict {veredict}.')
          return
        
        if self.check_enemy(goto, goto.is_city):
          if info: logging.debug(f'still enemies.')
          del(self.goto[0])
          return
        
      self.unit_arrival(goto)

  def oportunist_attack(self, info=1):
    if self.hp_total < 1: return
    logging.info(f'ataque de oportunidad de {self}.')
    sq = self.pos.get_near_tiles(1)
    [i.update(self.nation) for i in sq]
    sq = [it for it in sq if it.soil.name in self.soil and it.surf.name in self.surf
              and it.threat > 0]
    if info: logging.debug(f'{len(sq)} casillas.')
    for s in sq:
      if roll_dice(2) >= 3 and self.get_favland(s) == 0:
        if info: logging.debug(f'not favland.')
        continue
      ranking = self.ranking
      if info: logging.debug(f'{ranking=:}.')
      if self.comm: ranking *= 0.6
      if s.surf.name == forest_t and self.forest_survival == 0: 
        ranking -= ranking * 0.2
        if info: logging.debug(f'reduce by forest.')
      if s.surf.name == swamp_t and self.swamp_survival == 0: 
        ranking -= ranking * 0.2
        if info: logging.debug(f'reduce by swamp.')
      if s.hill and self.mountain_survival == 0: 
        ranking -= ranking * 0.2
        if info: logging.debug(f'reduce by mountain.')
      rnd = randint(round(ranking * 0.9), round(ranking * 1.2))
      if self.nation not in self.pos.world.nations: 
        rnd *= 1.5
        if info: logging.debug(f'rnd increased by random unit.')
      if info: logging.debug(f'{rnd=:}, {s.threat=:}, {s.around_threat=:}')
      if self.fear in [5, 6]: fear = 1.5
      if self.fear in [4, 3]: fear = 2
      if self.fear <= 2: fear = 3
      if info: logging.debug(f'{rnd*fear=:}, {s.around_threat=:}.')
      if rnd * fear < s.around_threat:
        if info: logging.debug(f'afraid.')
        continue
      if rnd > s.threat and s.cost <= self.mp[0]:
        msg = f'{self} en {self.pos} aprobecha y ataqua a {s}.'
        if info: logging.debug(msg)
        self.log[-1].append(msg)
        self.move_set(s)
        self.move_set('attack')
        return 1



  def raid(self, cost=0):
    if (self.pos.city and self.pos.nation != self.nation and self.can_raid 
        and self.mp[0] >= cost):  
      self.mp[0] -= cost
      self.update()
      self.pos.update()
      if self.pos.raided < self.pos.income:
        logging.info(f'{self} saquea a {self.pos.city} {self.pos.nation} en {self.pos} {self.pos.cords}')
        self.set_hidden(self.pos)
        raided = self.hp_total * 2
        if mounted_t in self.traits: raided *= 2
        if raided > self.pos.income: raided = self.pos.income
        self.pos.raided = raided
        self.pos.city.raid_outcome += raided
        self.nation.raid_income += raided
        self.history.raids += raided
        msg = f'{self} {raids_t} {raided} {gold_t} {in_t} {self.pos} {self.pos.cords}, {self.pos.city}.'
        self.pos.nation.log[-1].append(msg)
        self.log[-1].append(msg)
        self.nation.log[-1].append(msg)
        if any(i for i in [self.pos.nation.show_info, self.show_info]) and raided: 
          sleep(loadsound('spell34', channel=ch3))
      if self.pos.pop:
        logging.debug(f'{self.pop=:}.')
        pop = self.pos.pop
        deads = (self.damage + self.damage_mod) * randint(1, self.units)
        logging.debug(f'initial dead {deads}.')
        deads *= randint(1, self.att + self.att_mod + 1)
        if mounted_t in self.traits: deads *= 2 
        logging.debug(f'second dead {deads}.')
        defense = sum([i.units for i in self.pos.units if i.nation == self.pos.nation])
        if defense: deads -= defense * 0.5
        logging.debug(f'end dead {deads}.')
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
          msg = f'masacre!.'
          self.log[-1].append(msg)
          self.nation.log[-1].append(msg)
          self.pos.nation.log[-1].append(msg)
          sq = self.pos.get_near_tiles(1)
          sq = [s for s in sq if s.nation == self.pos.nation]
          for s in sq: s.unrest += randint(15, 30)
          if any(i for i in [self.pos.nation.show_info, self.show_info]): 
            sleep(loadsound('spell33', channel=ch3) * 0.2)
        if deads:
          msg = f'{deads} población perdida.'
          self.pos.nation.log[-1].append(msg)
          self.log[-1].append(msg)
          self.nation.log[-1].append(msg)
          if any(i for i in [self.show_info, self.pos.nation.show_info]): 
            sleep(loadsound('spell36', channel=ch5) // 2)
      logging.info(f'raid_income {round(self.pos.nation.raid_income)}.')      
      self.pos.city.update()

  def random_move(self, sq=None, value=1, info=1):
    logging.debug(f'movimiento aleatoreo para {self} en {self.pos}, {self.pos.cords}.')
    done = 0
    if sq == None:
      sq = self.pos.get_near_tiles(value)
      sq = [it for it in sq if self.can_pass(it)]
      if info: logging.debug(f'{len(sq)} casillas iniciales.')
    if sq:
      if self.city and self.nation in self.pos.world.random_nations: sq = [it for it in sq if it.get_distance(it, self.city.pos) <= self.mp[1]]
      print(f'{len(sq)= }.')
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
        if info: logging.debug(f'sorted.')
        sort = 1
        [s.set_threat(self.nation) for s in sq]
        if self.populated_land:
          if info: logging.debug(f'casillas pobladas.')
          sq.sort(key=lambda x: x.pop, reverse=True)
        self.set_favland(sq)
      
      if info: logging.debug(f'{self.ranking=:}.')
      rnd = randint(round(self.ranking * 0.9), round(self.ranking * 1.3))
      if self.pos.surf.name == forest_t and self.forest_survival == 0: rnd -= rnd * 0.3
      if self.pos.hill and self.mountain_survival == 0: rnd -= rnd * 0.3
      if self.pos.surf.name == swamp_t and self.swamp_survival == 0: rnd -= rnd * 0.3
      if commander_t in self.traits: rnd -= rnd * 0.3
      if self.nation not in self.pos.world.nations: rnd *= 1.5
      if basics.roll_dice(1) <= self.fear:
        if info: logging.debug(f'ordena por miedo')
        fear = 1
        sq.sort(key=lambda x: x.city == None, reverse=True)
        sq.sort(key=lambda x: x.threat <= rnd, reverse=True)
        sq.sort(key=lambda x: x.around_threat <= rnd, reverse=True)
        if basics.roll_dice(1) >= 3: sq.sort(key=lambda x: x.food - x.food_need < self.food)
        sq.sort(key=lambda x: x.defense, reverse=True)
      if self.scout:
        if info:  logging.debug(f'ordena para exploración')
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
      movstatus = f'fear {fear}, sort {sort}.'
      self.log[-1].append(movstatus)
      if info: logging.debug(f'{len(sq)} casillas finales.')
      moved = 0
      for s in sq:
        if self.fear in [6, 5]: fear = 1.5
        if self.fear in [4, 3]: fear = 2
        if self.fear in [2, 1]: fear = 3
        if info: logging.debug(f'{rnd*fear=:} {s.around_threat=:}.')
        if rnd * fear < s.around_threat and self.fear >= 5: 
          if info: logging.debug(f'afraid.')
          continue
        if info: logging.debug(f'rnd {rnd} amenaza {round(s.threat)} in {s}, {s.cords}.')
        if rnd >= s.threat:
          moved = 1
          self.move_set(s)
          break
      if moved == 0:
        msg = f'no se mueve.!'
        if info: logging.debug(msg)
        self.log[-1].append(msg)
        self.stopped = 1
    return done



  def restoring(self, info=0):
    logging.debug(f'restaura {self} id {self.id}.')
    if self.hp_total < 1:
      logging.warning(f'sin salud.')
      return
    self.history.turns += 1
    self.stopped = 0
    self.revealed = 0
  
    # hp.
    if self.hp_total < self.hp * self.units:
      res = self.hp_res + self.hp_res_mod
      self.hp_total += res
      if self.hp_total > self.hp * self.units: self.hp_total = self.hp * self.hp * self.units
      if info: logging.debug(f'restaura {res} hp.')
      if self.hp_total > self.hp * self.units: self.hp_total = self.hp * self.units
  
    # Refit
    if self.pos.nation and self.sts + self.sts_mod:
      if self.units < self.min_units * self.squads:
        sts = self.hp * (self.sts + self.sts_mod)
        self.hp_total += sts
        msg = f'recovers {sts}.'
        self.log[-1] += {msg}
        if info: logging.debug(msg)
        reduction = round(self.pop / self.initial_units)
        self.pos.city.reduce_pop(reduction)
    
    # mp.
    self.mp[0] = self.mp[1]
    if info: logging.debug(f'mp {self.mp}.')
  
    # poder.
    power_res = self.power_res + self.power_res_mod
    self.power += power_res
    if self.power > self.power_max: self.power = self.power_max
  
    # skills.
    for sk in self.skills:
      if sk.type == "start turn":
        sk.run(self)
      if sk.turns > 0:sk.turns -= 1
    self.global_skills = [sk for sk in self.global_skills if sk.turns == -1 or sk.turns > 0]
    self.offensive_skills = [sk for sk in self.offensive_skills if sk.turns == -1 or sk.turns > 0]
    self.other_skills = [sk for sk in self.other_skills if sk.turns == -1 or sk.turns > 0]
    self.terrain_skills = [sk for sk in self.terrain_skills if sk.turns == -1 or sk.turns > 0]

  def set_attack(self):
    if self.mp[0] < 0: return
    logging.debug(f'ataque hidden.')
    enemies = [i for i in self.pos.units
               if i.nation != self.nation and i.hidden == 0]
    if enemies:
      weakest = roll_dice(1)
      if self.hidden: 
        weakest += 2
      if weakest >= 5: enemies.sort(key=lambda x: x.ranking)
      return enemies[0]

  def set_auto_explore(self):
      if self.scout == 0:
        self.scout = 1
        self.ai = 1
        msg = f'exploración automática activada.'
        sp.speak(msg)         
        logging.debug(msg)
        loadsound('s2')
      elif self.scout == 1:
        self.scout = 0
        self.ai = 0
        msg = f'exploración automática desactivada.'
        sp.speak(msg)         
        logging.debug(msg)
        loadsound('s2')

  def set_default_align(self):
    if self.pos:
      for nt in self.pos.world.random_nations: 
        if nt.name == self.align.name: self.nation = nt

  def set_favland(self, sq):
    shuffle(sq)
    sq.sort(key=lambda x: self.get_favland(x), reverse=True)
    if self.pref_corpses: sq.sort(key=lambda x: len(x.corpses), reverse=True)

  def set_hidden(self, pos, info=0):
    if info: logging.info(f'set hidden {self} a {pos} {pos.cords}.')
    visible = self.size * self.units
    if info: logging.debug(f'visible {visible}')
    if self.nation != pos.nation: 
      visible += pos.pop
      if info: logging.debug(f'visible {visible} pop')
    visible += sum([it.units * it.sight for it in pos.units if it.nation != self.nation])
    if info: logging.debug(f'visible {visible} units')
    visible = floor(visible / 200)
    if visible > 7: visible = 7
    if info: logging.debug(f'visible {visible} rond 20')
    stealth = self.stealth + self.stealth_mod
    if info: logging.debug(f'stealth {stealth}')
    stealth -= visible
    roll = roll_dice(2)
    if info: logging.debug(f'roll {roll}. stealth {stealth}.')
    if roll >= stealth or roll == 12: 
      self.revealed = 1
      self.update()
      if info: logging.debug(f'revelado.')
    self.revealed_val = stealth, visible 

  def set_id(self):
    num = self.id
    # logging.debug(f'id base {self} {num}.')
    self.nation.units.sort(key=lambda x: x.id)
    for i in self.nation.units:
      # logging.debug(f'{i} id {i.id}.')
      if i.id == num: num += 1
    self.id = num

    # logging.debug(f'id final {self.id}.')
  def set_level(self):
    level = self.level
    for i in self.exp_tree:
      if self.exp <= i:
        self.level = self.exp_tree.index(i)
        break
    
    if self.level > level: self.level_up()

  def set_ranking(self):
    self.ranking_off = 0
    self.ranking_off_l = []
    self.ranking_off += (self.damage + self.damage_mod)
    self.ranking_off_l += ['damage', self.ranking_off]
    self.ranking_off += (self.damage_sacred + self.damage_sacred_mod)
    self.ranking_off_l += ['sacred', self.ranking_off]
    self.ranking_off *= self.att + self.att_mod
    self.ranking_off_l += ['att', self.ranking_off]
    self.ranking_off *= self.units
    self.ranking_off_l += ['units', self.ranking_off]
    self.ranking_off += (self.damage_charge + self.damage_charge_mod) * 10
    self.ranking_off_l += ['charge', self.ranking_off]
    # if self.ranking > 1: self.ranking //= 2
    # self.ranking_off_l += ['divided', self.ranking_off]
    if self.off + self.off_mod >= 8: self.ranking_off *= 3 + (self.off + self.off_mod) / 10    
    elif self.off + self.off_mod >= 6: self.ranking_off *= 2 + (self.off + self.off_mod) / 10
    elif self.off + self.off_mod >= 4: self.ranking_off *= 1.3 + (self.off + self.off_mod) / 10
    else: self.ranking_off *= 1 + (self.off + self.off_mod) / 20
    self.ranking_off_l += ['off', self.ranking_off]
    if self.str + self.str_mod >= 8: self.ranking_off *= 2.5 + (self.str + self.str_mod) / 10
    elif self.str + self.str_mod >= 6: self.ranking_off *= 2 + (self.str + self.str_mod) / 10
    elif self.str + self.str_mod >= 4: self.ranking_off *= 1.5 + (self.str + self.str_mod) / 10
    else: self.ranking_off *= 1 + (self.str + self.str_mod) / 10
    self.ranking_off_l += ['str', self.ranking_off]
    self.ranking_off *= 1 + (self.pn + self.pn_mod) / 5
    self.ranking_off_l += ['pn', self.ranking_off]
    self.ranking_off *= 1 + (self.moves + self.moves_mod) / 20
    self.ranking_off_l += ['moves', self.ranking_off]
    self.ranking_off = round(self.ranking_off / 20)
  
    self.ranking_dfs = self.hp_total
    self.ranking_dfs_l = ['hp', self.ranking_dfs]
    if self.dfs + self.dfs_mod >= 8: self.ranking_dfs *= 3 + (self.dfs + self.dfs_mod) / 10
    elif self.dfs + self.dfs_mod >= 6: self.ranking_dfs *= 2 + (self.dfs + self.dfs_mod) / 10
    else: self.ranking_dfs *= 1 + (self.dfs + self.dfs_mod) / 10
    self.ranking_dfs_l += ['dfs', self.ranking_dfs]
    if self.res + self.res_mod >= 8: self.ranking_dfs *= 3 + (self.res + self.res_mod) / 10
    elif self.res + self.res_mod >= 6: self.ranking_dfs *= 2.5 + (self.res + self.res_mod) / 10
    elif self.res + self.res_mod >= 4: self.ranking_dfs *= 2 + (self.res + self.res_mod) / 10
    else: self.ranking_dfs *= 1 + (self.res + self.res_mod) / 10
    self.ranking_dfs_l += ['res', self.ranking_dfs]
    if self.hres + self.hres_mod >= 4: self.ranking_dfs *= 3 + (self.hres + self.hres_mod) / 10
    elif self.hres + self.hres_mod >= 2: self.ranking_dfs *= 2 + (self.hres + self.hres_mod) / 10
    else: self.ranking_dfs *= 1 + (self.hres + self.hres_mod) / 10
    self.ranking_dfs_l += ['h res', self.ranking_dfs]
    if self.arm + self.arm_mod >= 8: self.ranking_dfs *= 3 + (self.arm + self.arm_mod) / 10
    elif self.arm + self.arm_mod >= 6: self.ranking_dfs *= 2.5 + (self.arm + self.arm_mod) / 10
    elif self.arm + self.arm_mod >= 4: self.ranking_dfs *= 2 + (self.arm + self.arm_mod) / 10
    else: self.ranking_dfs *= 1 + (self.arm + self.arm_mod) / 10
    self.ranking_dfs_l += ['arm', self.ranking_dfs]
    if self.armor : 
      if self.armor.arm >= 4: self.ranking_dfs *= 1.5 + (self.armor.arm / 10)
      else: self.ranking_dfs *= 1 + (self.armor.arm / 10)
      self.ranking_dfs_l += ['armor', self.ranking_dfs]
    if self.shield: 
      self.ranking_dfs *= 1.5 + (self.shield.dfs) / 10
      self.ranking_dfs_l += ['shield', self.ranking_dfs]
    self.ranking_dfs = round(self.ranking_dfs / 20)

    self.ranking = self.ranking_dfs + self.ranking_off
    if self.rng + self.rng_mod >= 20: self.ranking *= 2
    elif self.rng + self.rng_mod >= 15: self.ranking *= 1.75
    elif self.rng + self.rng_mod >= 10: self.ranking *= 1.5
    elif self.rng + self.rng_mod >= 6: self.ranking *= 1.2
  
    if self.can_fly: self.ranking *= 1.3
    if self.resolve + self.resolve_mod >= 6: self.ranking *= 1.3
    if self.size >= 4: self.ranking *= 1.2
    elif self.size >= 5: self.ranking *= 1.3
    elif self.size >= 6: self.ranking *= 1.5
    for sk in self.skills:
      self.ranking *= sk.ranking
    self.ranking = round(self.ranking)

  def set_skills(self, info=0):
    if info: print(f'get skills {self}')
    self.arm_mod = 0
    self.armor_ign_mod = 0
    self.att_mod = 0
    self.damage_mod = 0
    self.damage_critical_mod = 0
    self.damage_charge_mod = 0
    self.damage_sacred_mod = 0
    self.dfs_mod = 0
    self.hit_rolls_mod = 0
    self.hp_res_mod = 0
    self.hres_mod = 0
    self.hp_mod = 0
    self.moves_mod = 0
    self.off_mod = 0
    self.pn_mod = 0
    self.power_mod = 0
    self.power_max_mod = 0
    self.power_res_mod = 0
    self.rng_mod = 0
    self.ranking_skills = 0
    self.res_mod = 0
    self.resolve_mod = 0
    self.size_mod = 0
    self.stealth_mod = 0
    self.str_mod = 0
    self.sts_mod = 0

    self.skill_names = []
    self.effects = []
    if self.hidden: self.effects += {hidden_t}
    if self.settler == 1: self.skill_names.append(f' {settler_t}.')
    if self.charge and self.can_charge: self.effects += {charge_t} 
    
    skills = [i for i in self.skills]
    [self.skill_names.append(i.name) for i in self.skills]
    if self.pos: self.pos.set_skills()
    tile_skills = []
    if self.pos:
      if self.attacking == 0: tile_skills += [sk for sk in self.pos.terrain_events + self.pos.skills + self.pos.events ]
      elif self.attacking: tile_skills += [sk for sk in self.target.pos.terrain_events + self.pos.skills + self.pos.events]
    if info: print(f'{len(tile_skills)} de casillas.')
    for i in tile_skills:
      if i.type == 'generic':
        if info: print(f'{i.name} added.')
        skills.append(i)
    
    if self.target: skills += [s for s in self.target.skills if s.effect == 'enemy']    
    if info: print(f'run')
    for sk in skills:
      if sk.type == 'generic':
        if info: print(sk.name)
        sk.run(self)
    
    self.skill_names.sort()

  def set_squads(self, value):
    self.hp_total = self.hp * (self.min_units * value)
    self.update()

  def set_tile_attr(self, info=0):
    tiles = self.pos.get_near_tiles(1)
    tiles = [t for t in tiles if t.nation 
           and t.nation != self.nation and t.pop]
    if info and tiles: print(f'set_tile_attr {self} en {self.pos} {self.pos.cords}')
    for t in tiles:
      unrest = self.pos.defense * 0.15
      if info: logging.debug(f'unrest {unrest= }.')
      unrest -= t.defense * 0.15
      if t.defense: unrest -= t.around_defense * 0.2
      if info: logging.debug(f'after defense {unrest= }.')
      if unrest < 0: unrest = 0
      if info: logging.debug(f'unrest {unrest}')
      if t == self.pos: unrest *= 2
      if info: logging.debug(f'same pos {unrest}')
      if info: logging.debug(f'unrest final {unrest}')
      if unrest < 0: unrest = 0
      t.unrest += unrest

  def set_value(self):
    value = self.upkeep * self.units
    value += randint(2, 10)
    if self.history.raids:
      value += self.history.raids
    if self.history.kills_record: 
      value += self.history.kills_record * 2
    value *= ceil(self.history.turns / 3)
    if mounted_t in self.traits: value *= 1.5
    return value

  def split(self, times=1):
    if self.squads <= 1 or self.goto: return self
    logging.info(f'divide {self}.')
    units = []
    for i in range(times):
      self.update()
      logging.debug(f'{self} hp {self.hp_total} units {self.units} mínimo {self.min_units}.')
      if self.units <= self.min_units:
        logging.debug(f'mínimo alcansado.')
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
      unit.log = [[f'{turn_t} {self.pos.world.turn}.']]
      msg = f'{unit} detached from {self}.'
      unit.log[-1] += [msg]
      self.log[-1] += [msg]
      self.pos.units.append(unit)
      if self.show_info: sp.speak(f'{self}.')
      units += [unit]
    if len(units) > 1: self.join_units(units)
    return units[0]

  def start_turn(self):
    self.update()
    self.log += [[f'{turn_t} {self.pos.world.turn}.']]
    self.burn()
    self.raid()

  def stats_battle(self):
    target = self.target.__class__(self.target.nation)
    kills_record = target.ranking / target.units
    kills_record *= sum(self.target.deads)
    self.history.kills_record += kills_record

  def unit_arrival(self, goto, info=0):
    if self.hp_total < 1:
      logging.warning(f'arrival. {self} no tiene salud.')
      return
    
    self.pos.units.remove(self)
    goto.units.append(self)
    self.pos = goto
    del(self.goto[0])
    self.can_retreat = 1
    self.going = 0
    msg = f'{self} llega a ({goto}, {goto.cords}.'
    if info: logging.debug(msg)
    self.log[-1].append(msg)
    if self.show_info and self.goto == [] and self.scout == 0: sleep(loadsound('walk_ft1') / 5)
    if self.show_info: goto.pos_sight(self.nation, self.nation.map)
    self.pos.update(self.nation)
    self.check_position()
    self.set_tile_attr()
    self.burn()
    self.raid()
    [b.set_hidden(self.nation) for b in self.pos.buildings if b.type == building_t]
    [i.set_hidden(self.pos) for i in self.pos.units 
     if i.nation != self.nation and i.hidden]




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
      if self.log == []: self.log.append([f'{turn_t} {self.pos.world.turn}.'])
      if self.pos.nation != self.nation and self.pos.nation != None and self.pos not in self.tiles_hostile:
        self.tiles_hostile.append(self.pos)
        # logging.debug(f'hostiles explorados {len(self.tiles_hostile)}.')
    
    # atributos.
    if commander_t in self.traits: self.comm = 1
    if settler_t in self.traits: self.settler = 1
    self.units = ceil(self.hp_total / self.hp)
    if self.units < 0: self.units = 0
    if self.power < 0: self.power = 0
    self.upkeep_total = self.upkeep * self.units
    if undead_t in self.traits: self.can_recall = 0
    if self.can_hide: self.hidden = 1
    if self.can_charge and self.target == None: self.charge = 1
    if self.revealed: self.hidden = 0
    if self.hp_total > 0: self.squads = ceil(self.units / self.min_units)
    self.food_total = self.food * self.units
    self.spells_tags = []
    for sp in self.spells: self.spells_tags += sp.tags
    if self.leader and self.leader.group == []: self.leader = None
    self.show_info = self.nation.show_info
    
    # ranking.
    self.get_skills()
    self.set_skills()
    self.effects += [s.name for s in self.other_skills]
    self.set_ranking()
    if self.leader and self.leader not in self.nation.units: 
      self.leader = None
      logging.warning(f'{self} sin lider.')
    self.group = [i for i in self.group if i.units > 0 and i in self.nation.units]
    self.group_ranking = self.ranking + sum(i.ranking for i in self.group)



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
    self.stealth = 4



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
    self.stealth = 2



class Ship(Unit):

  def __init__(self, nation):
    super().__init__(nation)
    self.type = 'ship'
    self.soil = [coast_t, ocean_t] 



class Undead(Unit):

  def __init__(self, nation):
    super().__init__(nation)
    Ground.__init__(self)
    self.stealth = 2



# Elfos.
# edificios.
class Hall(City):
  name = 'salón'
  events = [Starving, Unrest, Looting, Revolt]
  food = 200
  public_order = 20
  initial_unrest = 15
  resource = 1
  upkeep = 1500

  free_terrain = 1
  own_terrain = 0

  military_base = 45
  military_change = 100
  military_max = 70
  popdef_base = 35
  popdef_change = 300
  popdef_min = 5
  tags = [city_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.nation = nation
    self.pos = pos
    self.av_units = [ForestGuard, ElvesSettler]
    self.resource_cost = [100, 100]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t]
    self.hill = [0]

  def set_capital_bonus(self):
    self.food += 100
    self.income += 50
    self.public_order += 20
    self.upkeep = 0

  def set_downgrade(self):
    msg = ''
    if self.level == 1 and self.pop <= 1500:
      msg = f'{self} se degrada a {hamlet_t}.'
      self.level = 0
      self.name = hamlet_t
      self.food -= 100
      # self.grouth -= 1
      self.income -= 100
      # self.public_order -= 10
    if self.level == 2 and self.pop <= 5000:
      msg = f'{self} se degrada a {village_t}.'
      self.level = 1
      self.name = village_t
      self.food -= 100
      # self.grouth -= 1
      self.income -= 100
      # self.public_order -= 10
    if self.level == 3 and self.pop <= 14000:
      msg = f'{self} se degrada a {town_t}.'
      self.level = 1
      self.name = town_t
      self.food -= 100
      # self.grouth -= 1
      self.income -= 100
      # self.public_order -= 10
    if msg:
      self.nation.log[-1].append(msg)
      logging.debug(msg)
      if self.nation.show_info:
        sp.speak(msg, 1) 
        sleep(loadsound('notify18'))

  def set_upgrade(self):
    msg = ''
    if self.level == 0 and self.pop >= 2000:
      msg = f'{self} mejor a {village_t}.'
      self.level = 1
      self.name = village_t
      self.food += 100
      # self.grouth += 1
      self.income += 100
      # self.public_order += 10
    if self.level == 1 and self.pop >= 6000:
      msg = f'{self} mejor a {town_t}.'
      self.level = 2
      self.name = town_t
      self.food += 100
      # self.grouth += 1
      self.income += 100
      # self.public_order += 10
    if self.level == 2 and self.pop >= 15000:
      msg = f'{self} mejor a {city_t}.'
      self.level = 3
      self.name = city_t
      self.food += 100
      # self.grouth += 1
      self.income += 100
      # self.public_order += 10
    if msg:
      logging.debug(msg)
      if self.nation.show_info:
        sp.speak(msg, 1)
        sleep(loadsound('notify14'))



class GlisteningPastures(Building):
  name = 'Pasturas radiantes'
  level = 1
  city_unique = 1
  size = 6
  gold = 18000
  food = 100
  income = 20

  own_terrain = 1
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [WildHuntsman]
    self.resource_cost = [0, 160]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t]
    self.hill = [0, 1]
    self.upgrade = [WhisperingWoods]



class WhisperingWoods(GlisteningPastures, Building):
  name = 'Establos del viento'
  level = 2
  base = GlisteningPastures
  gold = 24000
  income = 50

  own_terrain = 1
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [DemonHunter, ForestRider, ForestGiant, ]
    self.resource_cost = [0, 120]
    self.size = 0



class FalconRefuge(Building):
  name = 'refugio del alcón'
  level = 1
  city_unique = 1
  size = 4
  gold = 8000
  food = 100
  own_terrain = 1
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Druid, Falcon, Huntress]
    self.resource_cost = [0, 80]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t]
    self.hill = [0, 1]
    self.upgrade = [ForestLookout]



class ForestLookout(FalconRefuge, Building):
  name = 'Observatorio forestal'
  level = 2
  base = FalconRefuge
  gold = 15000

  own_terrain = 1
  tags = [military_t]
  upkeep = 1000

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [ForestEagle, WoodArcher]
    self.resource_cost = [0, 80]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t]
    self.hill = [0, 1]
    self.upgrade = []



class Sanctuary(Building):
  name = 'santuario'
  level = 1
  city_unique = 1
  size = 6
  gold = 14000
  food = 100
  income = 100

  own_terrain = 1
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [BladeDancer]  # KeeperOfTheGrove
    self.resource_cost = [0, 80]
    self.surf = [forest_t]
    self.hill = [0]
    self.upgrade = [HauntedForest]



class HauntedForest(Sanctuary, Building):
  name = 'Bosque embrujado'
  level = 2
  base = Sanctuary
  gold = 18000
  income = 0
  own_terrain = 1
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [EternalGuard, ForestBear]
    self.resource_cost = [0, 120]
    self.size = 0
    self.surf = [forest_t]
    self.hill = [0]
    self.upgrade = [MoonsFountain]



class WailingWoods(HauntedForest, Building):
  name = 'wailing woods'
  level = 3
  base = Sanctuary
  gold = 25000
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [SisterFromTheDeepth]
    self.resource_cost = [0, 150]
    self.size = 0
    self.upgrade = []



class MoonsFountain(WailingWoods, Building):
  name = 'Fuentes de la luna'
  level = 4
  base = Sanctuary
  gold = 35000
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [AwakenTree, Driad, PriestessOfTheMoon]
    self.resource_cost = [0, 150]
    self.size = 0
    self.upgrade = []



class Grove(Building):
  name = 'Huerto'
  level = 1
  size = 6
  gold = 2000
  food = 150

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
  name = 'racimos de uva'
  level = 2
  base = Grove
  gold = 7500
  food = 250
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
  name = 'Viñedo'
  level = 3
  base = GrapeVines
  gold = 14000
  food = 400
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
  name = 'Artesanos de los árboles'
  level = 1
  local_unique = 1
  size = 4
  local_unique = 1
  gold = 5000
  food = 100
  income = 100
  resource = 2
  own_terrain = 1
  tags = [resource_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 70]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t]
    self.hill = [0, 1]
    self.upgrade = []



class stoneCarvers(Building):
  name = 'Talladores de la piedra'
  level = 1
  size = 5
  local_unique = 1
  gold = 10000
  food = 50
  income = 300
  resource = 2
  
  own_terrain = 1
  tags = [resource_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 120]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [1]
    self.upgrade = []



# Unidades.
class DemonHunter(Elf):
  name = 'demon hunter'
  units = 5
  min_units = 5
  max_squads = 5
  type = 'infantry'
  traits = [elf_t]
  size = 2
  gold = 500
  upkeep = 80
  resource_cost = 25
  food = 3
  pop = 25
  terrain_skills = [Burn, DarkVision, DesertSurvival, ForestSurvival, MountainSurvival, SwampSurvival]

  hp = 18
  mp = [2, 2]
  moves = 6
  resolve = 7
  global_skills = [DHLevels, ForestWalker, Furtive, ShadowHunter]

  dfs = 5
  res = 2
  hres = 0
  arm = 0
  armor = None

  att = 1
  damage = 4
  off = 4
  str = 3
  pn = 0
  offensive_skills = [Ambushment]

  def __init__(self, nation):
    super().__init__(nation)
    # self.spells = [HealingRoots, SummonFalcons]
    self.align = Wild



class Druid(Elf):
  name = 'druida'
  units = 5
  min_units = 5
  max_squads = 1
  comm = 1
  type = 'infantry'
  traits = [elf_t, commander_t, wizard_t, poisonres_t]
  size = 2
  gold = 800
  upkeep = 70
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

  dfs = 4
  res = 2
  hres = 0
  arm = 0
  armor = None

  att = 2
  damage = 3
  off = 4
  str = 3
  pn = 0
  offensive_skills = [Ambushment, ToxicArrows]

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [HealingRoots, SummonFalcons]
    self.align = Wild



class KeeperOfTheGrove (Elf):
  name = 'keeper of the grove '
  units = 10
  min_units = 10
  max_squads = 1
  comm = 1
  type = 'infantry'
  traits = [elf_t, commander_t, wizard_t, poisonres_t]
  size = 2
  gold = 1200
  upkeep = 70
  resource_cost = 30
  food = 3
  pop = 20
  terrain_skills = [DarkVision, ForestSurvival]

  hp = 10
  sight = 5
  mp = [2, 2]
  moves = 7
  resolve = 7
  power = 0
  power_max = 30
  power_res = 3
  global_skills = [ForestWalker, Furtive, PyreOfCorpses, Refit, Regroup]

  dfs = 5
  res = 2
  hres = 0
  arm = 0
  armor = MediumArmor()

  att = 2
  damage = 4
  off = 5
  str = 4
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [RecruitForestGuards]
    self.spells = []  # [Entangling Roots ]
    self.align = Wild



class PriestessOfTheMoon(Elf):
  name = 'priestess of the moon'
  units = 1
  min_units = 1
  max_squads = 1
  unique = 1
  comm = 1
  type = 'infantry'
  traits = [elf_t, commander_t, wizard_t]
  size = 3
  gold = 2400
  upkeep = 500
  resource_cost = 35
  food = 6
  pop = 30
  terrain_skills = [DarkVision, ForestSurvival]

  hp = 26
  sight = 30
  mp = [4, 4]
  moves = 8
  resolve = 8
  power = 0
  power_max = 60
  power_res = 5
  global_skills = [ForestWalker, Furtive, Inspiration, PyreOfCorpses]

  dfs = 7
  res = 4
  hres = 2
  arm = 2
  armor = None

  att = 3
  damage = 4
  rng = 20
  off = 7
  str = 5
  pn = 2

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = []  # [Entangling Roots ]
    self.align = Wild



class AwakenTree(Elf):
  name = 'árbol despertado'
  units = 1
  min_units = 1
  max_squads = 1
  type = 'infantry'
  traits = [elf_t, poisonres_t]
  size = 5
  gold = 1200
  upkeep = 140
  resource_cost = 30
  food = 4
  pop = 30
  terrain_skills = [ForestSurvival]

  hp = 50
  mp = [2, 2]
  moves = 4
  resolve = 10
  global_skills = [ForestWalker]

  dfs = 3
  res = 6
  hres = 0
  hlm = 0
  arm = 4
  armor = None

  att = 3
  damage = 7
  rng = 5
  mrng = 20
  off = 6
  str = 7
  pn = 2
  offensive_skills = [ImpalingRoots]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class BladeDancer(Elf):
  name = 'danzante de la espada'
  units = 20
  min_units = 10
  max_squads = 5
  type = 'infantry'
  traits = [elf_t]
  size = 2
  gold = 380
  upkeep = 25
  resource_cost = 24
  food = 3
  pop = 45
  terrain_skills = [Burn, DarkVision, ForestSurvival, Raid]

  hp = 10
  mp = [2, 2]
  moves = 7
  resolve = 8
  global_skills = [ForestWalker, PyreOfCorpses, Regroup]

  dfs = 4
  res = 2
  hres = 0
  arm = 0
  armor = None

  att = 3
  damage = 4
  rng = 1
  off = 5
  str = 3
  pn = 1
  offensive_skills = [Ambushment]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class Driad(Elf):
  name = 'driad'
  units = 5
  min_units = 5
  max_squads = 5
  type = 'infantry'
  traits = [elf_t, poisonres_t]
  size = 2
  gold = 580
  upkeep = 45
  resource_cost = 30
  food = 3
  pop = 10
  terrain_skills = [Burn, DarkVision, ForestSurvival]

  hp = 40
  sight = 3
  mp = [2, 2]
  moves = 7
  resolve = 8
  global_skills = [ForestWalker, Furtive]

  dfs = 4
  res = 3
  hres = 0
  arm = 2
  armor = None

  att = 2
  damage = 5
  rng = 1
  off = 5
  str = 4
  pn = 1
  
  stealth = 8
  offensive_skills = [Ambushment]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild



class EternalGuard(Elf):
  name = 'guardia eterna'
  units = 40
  min_units = 20
  max_squads = 4
  type = 'infantry'
  traits = [elf_t]
  size = 2
  gold = 850
  upkeep = 25
  resource_cost = 25
  food = 4
  pop = 60
  terrain_skills = [Burn, DarkVision, ForestSurvival, Raid]

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 8
  global_skills = [ForestWalker, PyreOfCorpses, Refit, Regroup]

  dfs = 4
  res = 2
  hres = 0
  arm = 0
  armor = HeavyArmor()

  att = 2
  damage = 3
  rng = 2
  off = 4
  str = 4
  pn = 1
  offensive_skills = [PikeSquare]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class Falcon(Elf):
  name = 'Alcón'
  units = 2
  min_units = 2
  max_squads = 10
  type = 'beast'
  traits = [animal_t]
  size = 1
  gold = 140
  upkeep = 28
  resource_cost = 18
  food = 3
  pop = 20
  terrain_skills = [Fly, ForestSurvival]

  hp = 3
  sight = 5
  mp = [4, 4]
  moves = 10
  resolve = 6
  global_skills = [ForestWalker]

  dfs = 4
  res = 1
  hres = 0
  arm = 0
  armor = None

  att = 2
  damage = 2
  rng = 1
  off = 4
  str = 3
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild



class ForestBear(Unit):
  name = 'Oso del bosque'
  units = 4
  min_units = 4
  max_squads = 10
  type = 'beast'
  traits = [animal_t]
  size = 3
  gold = 300
  upkeep = 25
  resource_cost = 22
  food = 5
  pop = 20
  terrain_skills = [ForestSurvival]

  hp = 16
  mp = [2, 2]
  moves = 6
  resolve = 6
  global_skills = [ForestWalker, Furtive]

  dfs = 3
  res = 3
  hres = 2
  arm = 1
  armor = None

  att = 3
  damage = 4
  rng = 1
  off = 4
  str = 5
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class ForestEagle(Elf):
  name = 'águila del bosque'
  units = 2
  min_units = 2
  max_squads = 10
  type = 'beast'
  traits = [animal_t]
  size = 2
  gold = 600
  upkeep = 40
  resource_cost = 25
  food = 4
  pop = 10
  terrain_skills = [Fly, ForestSurvival]

  hp = 7
  sight = 3
  mp = [3, 3]
  moves = 8
  resolve = 8
  global_skills = [ForestWalker]

  dfs = 4
  res = 2
  hres = 0
  arm = 0
  armor = None

  att = 2
  damage = 4
  rng = 1
  off = 5
  str = 3
  pn = 1

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild



class Earban(Elf):
  name = 'earban'
  units = 1
  min_units = 1
  max_squads = 1
  comm = 1
  type = 'beast'
  traits = [animal_t, commander_t]
  size = 3
  gold = 1200
  upkeep = 200
  resource_cost = 35
  food = 6
  pop = 30
  terrain_skills = [Fly, ForestSurvival, MountainSurvival]

  hp = 30
  sight = 3
  mp = [4, 4]
  moves = 8
  resolve = 10
  global_skills = [ForestWalker]

  dfs = 5
  res = 3
  hres = 1
  arm = 2
  armor = None

  att = 5
  damage = 5
  rng = 1
  off = 5
  str = 5
  pn = 1

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild



class ForestGiant(Unit):
  name = 'forest giant'
  units = 1
  min_units = 1
  max_squads = 10
  type = 'beast'
  traits = []
  size = 4
  gold = 400
  upkeep = 60
  resource_cost = 24
  food = 5
  pop = 15
  terrain_skills = [Burn, ForestSurvival, MountainSurvival, Raid]

  hp = 20
  mp = [2, 2]
  moves = 5
  resolve = 6
  global_skills = [ForestWalker, Trample]

  dfs = 4
  res = 5
  hres = 2
  arm = 2
  armor = None

  att = 2
  damage = 5
  rng = 1
  off = 4
  str = 5
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class ForestGuard(Elf):
  name = 'guardia forestal'
  units = 20
  min_units = 10
  max_squads = 10
  type = 'infantry'
  traits = [elf_t]
  size = 2
  gold = 180
  upkeep = 8
  resource_cost = 14
  food = 2
  pop = 20
  terrain_skills = [Burn, ForestSurvival, Raid]

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 6
  global_skills = [ForestWalker, PyreOfCorpses]

  dfs = 2
  res = 2
  hres = 0
  arm = 0
  armor = None

  att = 2
  damage = 2
  rng = 1
  off = 3
  str = 3
  pn = 0
  offensive_skills = [Ambushment]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class ForestRider(Elf):
  name = 'forest rider'
  units = 10
  min_units = 50
  max_squads = 8
  type = 'cavalry'
  traits = [elf_t, mounted_t]
  size = 3
  gold = 750
  upkeep = 40
  resource_cost = 30
  food = 5
  pop = 30
  terrain_skills = [Burn, ForestSurvival, Raid]

  hp = 14
  mp = [4, 4]
  moves = 8
  resolve = 8
  global_skills = [ForestWalker, PyreOfCorpses, Refit, Regroup]

  dfs = 4
  res = 3
  hres = 1
  arm = 1
  armor = HeavyArmor
  shield = Shield()

  att = 2
  damage = 5
  rng = 3
  off = 4
  str = 5
  pn = 1
  offensive_skills = [HeavyCharge]

  def __init__(self, nation):
    super().__init__(nation)
    self.traits += [mounted_t]
    self.align = Wild
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, none_t]



class ElvesSettler(Human):
  name = 'Silvan settler'
  units = 200
  min_units = 200
  max_squads = 1
  settler = 1
  type = 'civil'
  traits = [elf_t, settler_t]
  size = 2
  gold = 1500
  upkeep = 10
  resource_cost = 60
  food = 1
  pop = 300
  terrain_skills = [ForestSurvival]

  hp = 4
  mp = [2, 2]
  moves = 3
  resolve = 4

  dfs = 1
  res = 1
  hres = 0
  arm = 0
  armor = None

  att = 2
  damage = 1
  rng = 1
  off = 1
  str = 1
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.buildings = [Hall]
    self.corpses = [Zombie]



class Huntress(Elf):
  name = huntresse_t
  units = 10
  min_units = 5
  max_squads = 5
  type = 'infantry'
  traits = [elf_t]
  size = 2
  gold = 360
  upkeep = 12
  resource_cost = 14
  food = 2
  pop = 20
  terrain_skills = [Burn, ForestSurvival]

  hp = 10
  sight = 2
  mp = [2, 2]
  moves = 6
  resolve = 6
  global_skills = [ForestWalker, Furtive, PyreOfCorpses]

  dfs = 2
  res = 2
  hres = 0
  arm = 0
  armor = None

  att = 1
  damage = 3
  rng = 10
  off = 5
  str = 4
  pn = 0
  offensive_skills = [Ambushment, Skirmisher]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class WoodArcher(Elf):
  name = 'alto arquero silvano'
  units = 20
  min_units = 10
  max_squads = 5
  type = 'infantry'
  traits = [elf_t]
  size = 2
  gold = 520
  upkeep = 20
  resource_cost = 28
  food = 2
  pop = 30
  terrain_skills = [Burn, DarkVision, ForestSurvival, Raid]

  hp = 10
  mp = [2, 2]
  moves = 7
  resolve = 7
  global_skills = [ForestWalker, Furtive, PyreOfCorpses, Refit, Regroup]

  dfs = 2
  res = 2
  hres = 0
  arm = 0
  armor = None

  att = 2
  damage = 3
  rng = 20
  off = 4
  str = 3
  pn = 0
  offensive_skills = [Ambushment, Skirmisher]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class SisterFromTheDeepth(Elf):
  name = 'sister from the deppth'
  units = 10
  min_units = 5
  max_squads = 6
  type = 'infantry'
  traits = [elf_t, poisonres_t]
  size = 2
  gold = 350
  upkeep = 15
  resource_cost = 22
  food = 2
  pop = 30
  terrain_skills = [Burn, DarkVision, ForestSurvival]

  hp = 10
  sight = 2
  mp = [2, 2]
  moves = 7
  resolve = 6
  global_skills = [ForestWalker, Furtive, PyreOfCorpses, Regroup]

  dfs = 2
  res = 2
  hres = 0
  arm = 0
  armor = None

  att = 1
  damage = 2
  rng = 10
  off = 5
  str = 5
  pn = 0
  offensive_skills = [Ambushment, Skirmisher, ToxicArrows]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class WildHuntsman(Elf):
  name = 'wild huntsman'
  units = 5
  min_units = 5
  max_squads = 6
  type = 'cavalry'
  traits = [elf_t, mounted_t]
  size = 4
  gold = 550
  upkeep = 30
  resource_cost = 25
  food = 5
  pop = 20
  terrain_skills = [Burn, ForestSurvival, Raid]

  hp = 16
  mp = [3, 3]
  moves = 6
  resolve = 6
  global_skills = [ForestWalker, Furtive, Trample]

  dfs = 4
  res = 4
  hres = 1
  arm = 2
  armor = None

  att = 2
  damage = 4
  rng = 1
  off = 4
  str = 4
  pn = 0
  offensive_skills = [BattleFocus, HeavyCharge]

  def __init__(self, nation):
    super().__init__(nation)
    self.traits += [mounted_t]
    self.align = Wild
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, none_t]  



# Holy empire.
class Hamlet(City):
  name = hamlet_t
  events = [Starving, Unrest, Looting, Revolt]
  food = 100
  grouth = 0
  public_order = 10
  initial_unrest = 30
  resource = 1
  upkeep = 1000

  free_terrain = 1
  own_terrain = 0

  military_base = 40
  military_change = 100
  military_max = 60
  popdef_base = 20
  popdef_change = 200
  popdef_min = 5
  tags = [city_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.nation = nation
    self.pos = pos
    self.av_units = [Archer, PeasantLevy, Settler]
    self.resource_cost = [100, 100]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [none_t]
    self.hill = [0]
    # self.events = [i(self) for i in self.events]

  def set_capital_bonus(self):
    self.food += 100
    self.public_order += 10
    # self.initial_unrest //= 2
    self.upkeep = 0

  def set_downgrade(self):
    msg = ''
    if self.level == 1 and self.pop <= 2500:
      msg = f'{self} se degrada a {hamlet_t}.'
      self.level = 0
      self.name = hamlet_t
      self.food -= 1.5
      # self.grouth -= 1
      # self.income -= 10
      self.public_order -= 10
    if self.level == 2 and self.pop <= 8000:
      msg = f'{self} se degrada a {village_t}.'
      self.level = 1
      self.name = village_t
      self.food -= 1.5
      # self.grouth -= 1
      # self.income -= 10
      self.public_order -= 10
    if self.level == 3 and self.pop <= 18000:
      msg = f'{self} se degrada a {town_t}.'
      self.level = 2
      self.name = town_t
      self.food -= 1.5
      # self.grouth -= 1
      # self.income -= 10
      self.public_order -= 10
    if msg:
      self.nation.log[-1].append(msg)
      logging.debug(msg)
      if self.nation.show_info:
        sp.speak(msg, 1) 
        sleep(loadsound('notify18'))

  def set_upgrade(self):
    msg = ''
    if self.level == 0 and self.pop >= 3000:
      msg = f'{self} mejor a {village_t}.'
      self.level = 1
      self.name = village_t
      self.food += 1.5
      # self.grouth += 1
      self.public_order += 10
    if self.level == 1 and self.pop >= 10000:
      msg = f'{self} mejor a {town_t}.'
      self.level = 2
      self.name = town_t
      self.food += 1.5
      # self.grouth += 1
      # self.income += 10
      self.public_order += 10
    if self.level == 2 and self.pop >= 20000:
      msg = f'{self} mejor a {city_t}.'
      self.level = 3
      self.name = city_t
      self.food += 1.5
      # self.grouth += 1
      self.public_order += 10
    if msg:
      self.nation.log[-1] += [msg]
      logging.debug(msg)
      if self.nation.show_info:
        sp.speak(msg, 1)
        sleep(loadsound('notify14'))



# edificios.
class TrainingCamp(Building):
  name = 'campo de entrenamiento'
  level = 1
  city_unique = 1
  size = 4
  gold = 10000
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
  name = 'campo de entrenamiento mejorado'
  level = 2
  base = TrainingCamp
  gold = 14000
  public_order = 10
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Legatus, Hastati]  
    self.resource_cost = [0, 70]
    self.size = 0
    self.upgrade = [Barracks]



class Barracks(ImprovedTrainingCamp, Building):
  name = 'cuartel'
  level = 3
  base = TrainingCamp
  gold = 22000
  public_order = 10
  tags = [military_t, unrest_t]
  upkeep = 500

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Principes, ImperialGuard, Aquilifer]
    self.resource_cost = [0, 120]
    self.size = 0
    self.upgrade = [ImprovedBarracks]



class ImprovedBarracks(Barracks, Building):
  name = 'cuartel mejorado'
  level = 4
  base = TrainingCamp
  gold = 30000
  public_order = 20
  tags = [military_t, unrest_t]
  upkeep = 1500

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Halberdier, CrossBowMan]
    self.resource_cost = [0, 200]
    self.size = 0



class Pastures(Building):
  name = 'pasturas'
  level = 1
  city_unique = 1
  size = 6
  gold = 14000
  food = 100
  income = 50

  own_terrain = 1
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Equites]
    self.resource_cost = [0, 80]
    self.soil = [grassland_t, plains_t]
    self.surf = [none_t]
    self.hill = [0]
    self.upgrade = [Stables]



class Stables(Pastures, Building):
  name = 'establos'
  level = 2
  base = Pastures
  gold = 22000
  food = 100
  income = 100

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Equites2]
    self.resource_cost = [0, 140]
    self.size = 0
    self.hill = [0]
    self.upgrade = []



class PlaceOfProphecy(Building):
  name = 'plaza de las profesías'
  level = 1
  city_unique = 1
  size = 4
  gold = 8000
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
  name = 'holy fountains'
  level = 2
  base = PlaceOfProphecy
  gold = 12500
  public_order = 15

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [RebornOne, Augur]
    self.resource_cost = [0, 50]
    self.size = 0
    self.upgrade = [TheMarbleTemple]



class TheMarbleTemple(PlaceOfProphecy, Building):
  name = 'the marble temple'
  level = 3
  base = PlaceOfProphecy
  gold = 17500
  public_order = 30
  upkeep = 1000

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [KnightsTemplar , Flamen, SacredWarrior]
    self.resource_cost = [0, 100]
    self.size = 0
    self.upgrade = [FieldsOfJupiter]

  name = 'templo de la luz'
  level = 4
  base = PlaceOfProphecy



class FieldsOfJupiter(TheMarbleTemple, Building):
  gold = 25000
  public_order = 50
  upkeep = 2500

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [PontifexMaximus, Gryphon, GryphonRiders]
    self.resource_cost = [0, 160]
    self.size = 0
    self.upgrade = []



# unidades.
# comandantes.
class Legatus(Human):
  name = 'legatus'
  units = 10
  min_units = 10
  max_squads = 1
  comm = 1
  type = 'infantry'
  traits = [human_t, commander_t]
  size = 2
  gold = 1000
  upkeep = 120
  resource_cost = 25
  food = 5
  pop = 40
  terrain_skills = []
  tags = ['commander']

  hp = 10
  power = 2
  power_max = 6
  power_res = 2
  mp = [4, 4]
  moves = 6
  resolve = 8
  global_skills = [Organization, WarCry]

  dfs = 4
  res = 2
  hres = 0
  arm = 0
  armor = MediumArmor()
  shield = Shield()
  defensive_skills = []

  att = 2
  damage = 3
  off = 4
  str = 4
  pn = 0
  offensive_skills = []

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [RecruitPeasants]
    self.align = Wild
    self.mp = [2, 2]



class Augur(Unit):
  name = 'augur'
  units = 5
  min_units = 5
  max_squads = 1
  comm = 1
  type = 'infantry'
  traits = [human_t, commander_t, sacred_t, wizard_t]
  size = 2
  gold = 1500
  upkeep = 150
  resource_cost = 30
  food = 3
  pop = 40

  hp = 10
  sight = 2
  mp = [2, 2]
  moves = 5
  resolve = 7
  power = 20
  power_max = 30
  power_res = 3
  global_skills = [DarkVision, PyreOfCorpses, SermonOfCourage]  # cure, BurnCorpses.

  dfs = 2
  res = 2
  hres = 0
  arm = 0
  armor = None

  att = 1
  damage = 2
  off = 3
  str = 3
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [HealingRoots, SightFromFuture]
    self.align = Wild



class Aquilifer(Human):
  name = 'aquilifer'
  units = 10
  min_units = 10
  max_squads = 1
  comm = 1
  type = 'infantry'
  traits = [human_t, leader_t]
  size = 2
  gold = 3000
  upkeep = 200
  resource_cost = 30
  food = 5
  pop = 100
  unique = 1
  tags = ['commander']

  hp = 15
  power = 2
  power_max = 6
  power_res = 4
  mp = [2, 2]
  moves = 7
  resolve = 8
  global_skills = [Inspiration, Regroup]

  dfs = 4
  res = 2
  hres = 0
  arm = 0
  armor = HeavyArmor()
  shield = Shield()

  att = 3
  damage = 3
  off = 5
  str = 4
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [RecruitPeasants]
    self.align = Wild



class Flamen(Human):
  name = 'flamen'
  units = 5
  min_units = 5
  max_squads = 1
  comm = 1
  type = 'infantry'
  traits = [human_t, commander_t, sacred_t, wizard_t]
  size = 2
  gold = 1300
  upkeep = 200
  resource_cost = 30
  food = 3
  pop = 40

  hp = 15
  mp = [2, 2]
  moves = 5
  resolve = 8
  power = 20
  power_max = 20
  global_skills = [SermonOfCourage]

  dfs = 1
  res = 2
  hres = 0
  arm = 0
  armor = LightArmor()

  att = 1
  damage = 2
  off = 4
  str = 3
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [BlessingWeapons]  # Cleanship
    self.align = Wild



class PontifexMaximus(Unit):
  name = 'pontifex maximus'
  units = 5
  min_units = 5
  max_squads = 1
  unique = 1
  comm = 1
  type = 'infantry'
  traits = [human_t, commander_t, sacred_t, wizard_t]
  size = 2
  gold = 4000
  upkeep = 400
  resource_cost = 30
  food = 5
  pop = 80

  hp = 10
  mp = [2, 2]
  moves = 5
  resolve = 8
  power = 40
  power_max = 40
  global_skills = [SermonOfCourage]

  dfs = 2
  res = 2
  hres = 0
  arm = 0
  armor = LightArmor()
  shield = Shield()

  att = 2
  damage = 2
  off = 4
  str = 3
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [SummonSecondSun, SummonDevourerOfDemons]
    self.align = Wild



# unidades
class Settler(Human):
  name = settler_t
  units = 250
  min_units = 250
  max_squads = 1
  settler = 1
  type = 'civil'
  traits = [human_t, settler_t]
  size = 2
  gold = 2000
  upkeep = 1
  resource_cost = 50
  food = 1
  pop = 400

  hp = 3
  mp = [2, 2]
  moves = 3
  resolve = 2

  dfs = 1
  res = 1
  hres = 0
  arm = 0
  armor = None

  att = 2
  damage = 1
  off = 1
  str = 1
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.buildings = [Hamlet]
    self.corpses = [Zombie]



class Flagellant(Human):
  name = flagellant_t
  units = 20
  min_units = 10
  max_squads = 10
  type = 'infantry'
  traits = [human_t, sacred_t]
  size = 2
  gold = 140
  upkeep = 6
  resource_cost = 11
  food = 2
  pop = 30
  terrain_skills = [Burn]

  hp = 10
  mp = [2, 2]
  moves = 5
  resolve = 5
  global_skills = [PyreOfCorpses]

  dfs = 2
  res = 2
  hres = 0
  arm = 0
  armor = None

  att = 2
  damage = 1
  off = 3
  str = 3
  pn = 0
  offensive_skills = [Fanatism]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild



class RebornOne(Human):
  name = 'renacido'
  units = 20
  min_units = 10
  max_squads = 10
  type = 'infantry'
  traits = [human_t, sacred_t]
  size = 2
  gold = 180
  upkeep = 14
  resource_cost = 14
  food = 3
  pop = 40
  terrain_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 5
  resolve = 5
  global_skills = [PyreOfCorpses]

  dfs = 3
  res = 2
  hres = 0
  arm = 0
  armor = None
  Shield = Shield()

  att = 1
  damage = 2
  off = 4
  str = 3
  pn = 0
  offensive_skills = [Fanatism]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild



class Velites(Human):
  name = 'velites '
  units = 30
  min_units = 10
  max_squads = 6
  type = 'infantry'
  traits = [human_t]
  size = 2
  gold = 350
  upkeep = 15
  resource_cost = 12
  food = 3
  pop = 50
  terrain_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 5
  global_skills = [PyreOfCorpses, Regroup]

  dfs = 3
  res = 2
  hres = 0
  hres = 1
  arm = 0
  armor = None
  shield = Shield()

  att = 2
  damage = 3
  off = 2
  str = 3
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild



class ImperialGuard(Human):
  name = 'guardia imperial'
  units = 20
  min_units = 20
  max_squads = 3
  type = 'infantry'
  traits = [human_t]
  size = 2
  gold = 820
  upkeep = 30
  resource_cost = 18
  food = 4
  pop = 60
  terrain_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 7
  resolve = 7
  global_skills = [BattleBrothers, PyreOfCorpses, Regroup, Refit]

  dfs = 4
  res = 2
  hres = 0
  arm = 0
  armor = HeavyArmor()

  att = 2
  damage = 4
  off = 5
  str = 4
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild



class Hastati(Human):
  name = 'hastati'
  units = 20
  min_units = 20
  max_squads = 3
  type = 'infantry'
  traits = [human_t]
  size = 2
  gold = 420
  upkeep = 25
  resource_cost = 15
  food = 3
  pop = 60
  terrain_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 5
  resolve = 5
  global_skills = [BattleBrothers, PyreOfCorpses, Regroup]

  dfs = 3
  res = 2
  hres = 0
  arm = 0
  armor = None

  att = 1
  rng = 2
  damage = 4
  off = 4
  str = 4
  pn = 1
  offensive_skills = [PikeSquare]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild



class Principes(Human):
  name = 'principes'
  units = 20
  min_units = 10
  max_squads = 6
  type = 'infantry'
  traits = [human_t]
  size = 2
  gold = 600
  upkeep = 40
  resource_cost = 24
  food = 3
  pop = 40
  terrain_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 5
  resolve = 6
  global_skills = [BattleBrothers, PyreOfCorpses, Regroup]

  dfs = 4
  res = 2
  hres = 0
  arm = 0
  armor = HeavyArmor()

  att = 1
  rng = 3
  damage = 5
  off = 5
  str = 4
  pn = 2
  offensive_skills = [PikeSquare]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild



class Halberdier(Human):
  name = 'halberdier'
  units = 10
  min_units = 10
  max_squads = 6
  type = 'infantry'
  traits = [human_t]
  size = 2
  gold = 550
  upkeep = 40
  resource_cost = 18
  food = 4
  pop = 30
  terrain_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 7
  resolve = 6
  global_skills = [BattleBrothers, PyreOfCorpses, Regroup, Refit, ]

  dfs = 3
  res = 2
  hres = 0
  arm = 0
  armor = MediumArmor()

  att = 2
  damage = 5
  off = 4
  str = 4
  pn = 2
  offensive_skills = [MassSpears, PikeSquare]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild



class SacredWarrior(Human):
  name = sacred_warrior_t
  units = 20
  min_units = 10
  max_squads = 6
  type = 'infantry'
  traits = [human_t, sacred_t]
  size = 2
  gold = 600
  upkeep = 30
  resource_cost = 16
  food = 3
  pop = 50
  global_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 7
  global_skills = [BattleBrothers, PyreOfCorpses, Regroup, Refit]

  dfs = 3
  res = 2
  hres = 0
  arm = 0
  armor = None
  shield = Shield()

  att = 2
  damage = 3
  off = 4
  str = 4
  pn = 0
  offensive_skills = [ShadowHunter]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Zombie]



class KnightsTemplar (Human):
  name = knights_templar_t
  units = 20
  min_units = 10
  max_squads = 6
  type = 'infantry'
  traits = [human_t, sacred_t]
  size = 2
  gold = 1250
  upkeep = 60
  resource_cost = 22
  food = 4
  pop = 55
  global_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 7
  global_skills = [BattleBrothers, PyreOfCorpses, Regroup, Refit]

  dfs = 4
  res = 2
  hres = 0
  arm = 0
  armor = MediumArmor()

  att = 1
  damage = 5
  rng = 2
  off = 4
  str = 4
  pn = 1
  offensive_skills = [PikeSquare, ShadowHunter]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Zombie]  



class Sagittarii(Human):
  name = 'sagittarii'
  units = 10
  min_units = 10
  max_squads = 4
  type = 'infantry'
  traits = [human_t]
  size = 2
  gold = 320
  upkeep = 14
  resource_cost = 14
  food = 3
  pop = 40
  terrain_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 6
  global_skills = [PyreOfCorpses]

  dfs = 1
  res = 2
  hres = 0
  arm = 0
  armor = None

  att = 2
  damage = 2
  rng = 15
  off = 3
  str = 2
  pn = 0
  offensive_skills = [Ambushment, ReadyAndWaiting, Skirmisher]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild



class CrossBowMan(Human):
  name = 'CrossBowMan'
  units = 10
  min_units = 10
  max_squads = 3
  type = 'infantry'
  traits = [human_t]
  size = 2
  gold = 420
  upkeep = 20
  resource_cost = 18
  food = 3
  pop = 30

  hp = 10
  mp = [2, 2]
  moves = 5
  resolve = 6
  global_skills = [PyreOfCorpses]

  dfs = 1
  res = 2
  hres = 0
  arm = 0
  armor = None

  att = 1
  damage = 6
  rng = 10
  off = 5
  str = 5
  pn = 1
  offensive_skills = [Ambushment, ReadyAndWaiting]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild



class Arquebusier(Human):
  name = 'Arquebusier'
  units = 20
  min_units = 10
  max_squads = 5
  type = 'infantry'
  traits = [human_t]
  size = 2
  gold = 1020
  upkeep = 40
  resource_cost = 25
  food = 3
  pop = 30

  hp = 10
  mp = [2, 2]
  moves = 5
  resolve = 6
  global_skills = [PyreOfCorpses]

  dfs = 1
  res = 2
  hres = 0
  arm = 0
  armor = None

  att = 1
  damage = 5
  rng = 15
  off = 5
  str = 5
  pn = 1
  offensive_skills = [Ambushment, ReadyAndWaiting, Skirmisher]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild



class Musket(Human):
  name = 'musquet'
  units = 20
  min_units = 10
  max_squads = 5
  type = 'infantry'
  traits = [human_t]
  size = 2
  gold = 1100
  upkeep = 50
  resource_cost = 30
  food = 3
  pop = 30

  hp = 10
  mp = [2, 2]
  moves = 5
  resolve = 6
  global_skills = [PyreOfCorpses]

  dfs = 2
  res = 2
  hres = 0
  arm = 0
  armor = None

  att = 2
  damage = 3
  rng = 20
  off = 5
  str = 5
  pn = 2
  offensive_skills = [Ambushment, ReadyAndWaiting, Skirmisher]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild



class Equites(Human):
  name = equites_t
  units = 20
  min_units = 10
  max_squads = 6
  type = 'cavalry'
  traits = [human_t, mounted_t]
  size = 3
  gold = 1800
  upkeep = 50
  resource_cost = 20
  food = 5
  pop = 60
  terrain_skills = [Burn, Raid]

  hp = 14
  mp = [4, 4]
  moves = 8
  resolve = 6
  global_skills = [BattleBrothers, PyreOfCorpses]

  dfs = 3
  res = 3
  hres = 1
  arm = 1
  armor = None
  shield = None

  att = 2
  damage = 4
  off = 4
  str = 4
  pn = 0
  offensive_skills = [Charge]

  def __init__(self, nation):
    super().__init__(nation)
    self.traits += [mounted_t]
    self.align = Wild
    self.corpses = [Skeleton]
    self.favhill = [0]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t]



class Equites2(Human):
  name = feudal_knight_t
  units = 10
  min_units = 10
  max_squads = 6
  type = 'cavalry'
  traits = [human_t, mounted_t]
  size = 3
  gold = 1500
  upkeep = 70
  resource_cost = 22
  food = 6
  pop = 70
  terrain_skills = [Burn, Raid]

  hp = 16
  mp = [3, 3]
  moves = 7
  resolve = 8
  global_skills = [BattleBrothers, Regroup, Refit, Trample]

  dfs = 4
  res = 3
  hres = 1
  arm = 2
  armor = HeavyArmor()

  att = 1
  damage = 5
  off = 5
  str = 5
  pn = 1
  offensive_skills = [HeavyCharge]

  def __init__(self, nation):
    super().__init__(nation)
    self.traits += [mounted_t]
    self.align = Wild
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t]



class Gryphon(Unit):
  name = 'gryphon'
  units = 4
  min_units = 2
  max_squads = 10
  type = 'beast'
  traits = [animal_t]
  size = 5
  gold = 800
  upkeep = 90
  resource_cost = 20
  food = 4
  pop = 20
  terrain_skills = [DarkVision, Fly]

  hp = 14
  sight = 4
  mp = [4, 4]
  moves = 8
  resolve = 8
  global_skills = []

  dfs = 4
  res = 4
  hres = 3
  arm = 1
  armor = None

  att = 2
  damage = 5
  rng = 1
  off = 5
  str = 5
  pn = 1
  offensive_skills = [Charge]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild  



class GryphonRiders(Unit):
  name = 'gryphon rider'
  units = 2
  min_units = 2
  max_squads = 10
  type = 'beast'
  traits = [animal_t, human_t, mounted_t]
  size = 5
  gold = 1200
  upkeep = 120
  resource_cost = 22
  food = 6
  pop = 30
  terrain_skills = [Burn, DarkVision, Fly, Raid]

  hp = 24
  sight = 5
  mp = [2, 2]
  moves = 7
  resolve = 7
  global_skills = [ShadowHunter]

  dfs = 5
  res = 4
  hres = 3
  arm = 2
  armor = None

  att = 3
  damage = 5
  rng = 1
  off = 5
  str = 5
  pn = 1
  offensive_skills = [HeavyCharge]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild  



# Vampiros.
class CursedHamlet(City):
  name = cursed_hamlet_t
  events = [Starving, Looting, Revolt]
  food = 100
  grouth = 0
  income = 50
  public_order = 20
  initial_unrest = 10
  resource = 1
  upkeep = 600

  free_terrain = 1
  own_terrain = 0

  military_base = 40
  military_change = 50
  military_max = 70
  popdef_base = 30
  popdef_change = 200
  popdef_min = 5
  tags = [city_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.nation = nation
    self.pos = pos
    self.resource_cost = [100, 100]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [0, 1]
    self.av_units = [Levy, Settler2]

  def set_capital_bonus(self):
    self.food += 100
    self.income += 100
    self.public_order += 10
    self.upkeep = 0

  def set_downgrade(self):
    msg = ''
    if self.level == 1 and self.pop <= 1700:
      logging.debug(f'{self} se degrada a {cursed_hamlet_t}.')
      self.level = 0
      self.name = cursed_hamlet_t
      self.food -= 0.5
      self.grouth -= 0.5
      # self.public_order -= 10
    if self.level == 2 and self.pop <= 6000:
      logging.debug(f'{self} se degrada a {village_t}.')
      self.level = 1
      self.name = village_t
      self.food -= 0.5
      self.grouth -= 0.5
      # self.public_order -= 10
    if self.level == 3 and self.pop <= 16000:
      logging.debug(f'{self} se degrada a {town_t}.')
      self.level = 2
      self.name = town_t
      self.food -= 0.5
      self.grouth -= 0.5
      # self.public_order -= 10
    if msg:
      logging.debug(msg)
      if self.nation.show_info:
        sp.speak(msg, 1)
        sleep(loadsound('notify18'))

  def set_upgrade(self):
    msg = ''
    if self.level == 0 and self.pop >= 2000:
      msg = f'{self} mejor a {village_t}.'
      self.level = 1
      self.name = cursed_village_t
      self.food += 1
      self.grouth += 0.5
      # self.public_order += 10
    if self.level == 1 and self.pop >= 7000:
      msg = f'{self} mejor a {village_t}.'
      self.level = 1
      self.name = town_t
      self.food += 1
      self.grouth += 0.5
      # self.public_order += 10
    if self.level == 2 and self.pop >= 18000:
      msg = f'{self} mejor a {city_t}.'
      self.level = 3
      self.name = city_t
      self.food += 0.5
      self.grouth += 0.5
      # self.public_order += 10
    if msg:
      logging.debug(msg)
      if self.nation.show_info:
        sp.speak(msg, 1)
        sleep(loadsound('notify14'))



class Cemetery(Building):
  name = cemetery_t
  level = 1
  city_unique = 1
  size = 6
  gold = 8000
  own_terrain = 1
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Ghoul, Zombie]
    self.resource_cost = [0, 30]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [none_t]
    self.hill = [0]
    self.upgrade = [FieldOfBlood]



class FieldOfBlood(Cemetery, Building):
  name = 'campo de sangre'
  level = 2
  base = Cemetery
  gold = 18000
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [VarGhul, Vampire]
    self.resource_cost = [0, 70]
    self.size = 0
    self.upgrade = [Mausoleum]



class Mausoleum(FieldOfBlood, Building):
  name = 'mausoleo'
  level = 3
  base = Cemetery
  gold = 25000
  public_order = 20
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [GraveGuard, VampireLord]
    self.resource_cost = [0, 120]
    self.size = 0
    self.upgrade = [CourtOfBlood]



class CourtOfBlood(Mausoleum, Building):
  name = 'corte oscura'
  level = 4
  base = Cemetery
  gold = 45000
  public_order = 50

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [BlackKnight, BloodKnight, VladDracul]
    self.resource_cost = [0, 159]
    self.size = 0
    self.upgrade = []



class HallsOfTheDead (Building):
  name = 'sala de los muertos'
  level = 1
  city_unique = 1
  size = 4
  gold = 8000
  own_terrain = 1
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Ghoul, FellBat]
    self.resource_cost = [0, 50]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [0, 1]
    self.upgrade = [SummoningCircle]



class SummoningCircle(HallsOfTheDead, Building):
  name = summoning_field_t
  level = 2
  base = HallsOfTheDead
  gold = 14000

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [CryptHorror, Necromancer, Skeleton]
    self.resource_cost = [0, 100]
    self.size = 0
    self.upgrade = [DarkMonolit]



class DarkMonolit(SummoningCircle, Building):
  name = 'monolito oscuro'
  level = 3
  base = HallsOfTheDead
  gold = 25000
  own_terrain = 1
  public_order = 50

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Isaac, WailingLady]
    self.resource_cost = [0, 250]
    self.size = 0
    self.upgrade = []



class HuntingGround(Building):
  name = hunting_ground_t
  level = 1
  city_unique = 1
  size = 6
  gold = 9000
  food = 50
  income = 50
  own_terrain = 1
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Bat, GiantWolf]
    self.resource_cost = [0, 70]
    self.surf = [forest_t]
    self.hill = [0]
    self.upgrade = [SinisterForest]



class SinisterForest(HuntingGround, Building):
  name = 'bosque abyssal'
  level = 1
  base = HuntingGround
  gold = 20000
  income = 50

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [DireWolf, Vargheist, ]
    self.resource_cost = [0, 100]
    self.size = 0
    self.upgrade = []



class Gallows(Building):
  name = 'Gallows'
  level = 1
  local_unique = 1
  size = 2
  gold = 5200
  public_order = 30
  own_terrain = 1
  tags = [unrest_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 40]
    self.soil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t, swamp_t]
    self.hill = [0, 1]
    self.upgrade = [ImpaledField]



class ImpaledField(Gallows, Building):
  name = 'campo de empalados'
  level = 2
  base = Gallows
  gold = 8500
  public_order = 50
  tags = [unrest_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 60]
    self.size = 0
    self.upgrade = []



class Pit(Building):
  name = 'fosa'
  level = 1
  local_unique = 1
  size = 5
  gold = 1500
  food = 150
  # public_order = 30
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
  name = 'mazmorra funeraria'
  level = 2
  base = Pit
  gold = 5000
  food = 250
  income = 30
  # public_order = 20
  resource = 2
  tags = [food_t, resource_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 90]
    self.size = 0
    self.upgrade = []



# unidades.
class Adjule(Unit):
  name = 'adjule'
  units = 10
  min_units = 5
  max_squads = 20
  type = 'beast'
  traits = [death_t]
  size = 2
  gold = 330
  upkeep = 32
  resource_cost = 18
  food = 0
  pop = 25
  terrain_skills = [DarkVision, DesertSurvival, NightSurvival]

  hp = 14
  mp = [3, 3]
  moves = 7
  resolve = 10
  global_skills = [NightFerocity, Regroup]

  dfs = 2
  res = 4
  hres = 1
  arm = 0
  armor = None

  att = 2
  damage = 2
  off = 4
  str = 4
  pn = 0
  
  stealth = 6

  fear = 3

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    Ground.__init__(self)
    self.corpses = [HellHound]
    self.favhill = [0]
    self.favsoil = [waste_t]
    self.favsurf = [none_t]
    self.traits += [animal_t]



class WailingLady(Undead):
  # Pendiente: resolver el tema etéreo.
  name = wailinglady_t
  units = 1
  min_units = 1
  max_squads = 1
  type = 'infantry'
  traits = [death_t, malignant_t, ethereal_t]
  size = 2
  gold = 666
  upkeep = 100
  resource_cost = 30
  food = 0
  pop = 30
  terrain_skills = [DarkVision, Fly, ]

  hp = 15
  mp = [2, 2]
  moves = 8
  resolve = 10
  global_skills = [Ethereal, FearAura, NightFerocity]

  dfs = 3
  res = 6
  hres = 4
  arm = 0
  armor = None

  att = 2
  rng = 1
  mrng = 10
  damage = 4
  off = 5
  str = 6
  pn = 3
  offensive_skills = [Scream]
  
  stealth = 8

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell



class Bat(Unit):
  name = bat_t
  units = 30
  min_units = 10
  max_squads = 20
  type = 'beast'
  traits = [animal_t, poisonres_t]
  size = 1
  gold = 435
  upkeep = 2
  resource_cost = 15
  food = 2
  pop = 20
  terrain_skills = [DarkVision, ForestSurvival, Fly]

  hp = 4
  sight = 2
  mp = [4, 4]
  moves = 4
  resolve = 3
  global_skills = [NightSurvival]

  dfs = 2
  res = 1
  hres = 0
  arm = 0
  armor = None

  att = 1
  damage = 1
  off = 2
  str = 1
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    self.favhill = [1]
    self.favsurf = [forest_t]
    self.traits += [animal_t]



class BlackKnight(Undead):
  name = black_knight_t
  units = 10
  min_units = 5
  max_squads = 6
  type = 'cavalry'
  traits = [death_t, mounted_t, malignant_t]
  size = 3
  gold = 1400
  upkeep = 80
  resource_cost = 22
  food = 0
  pop = 35
  terrain_skills = [DarkVision, Burn, NightSurvival]

  hp = 18
  mp = [4, 4]
  moves = 7
  resolve = 10
  global_skills = [FearAura, NightFerocity, NightSurvival]

  dfs = 4
  res = 5
  hres = 2
  arm = 1
  armor = HeavyArmor()

  att = 3
  damage = 3
  off = 5
  str = 4
  pn = 2
  offensive_skills = [HeavyCharge]

  def __init__(self, nation):
    super().__init__(nation)
    self.traits += [mounted_t]
    self.align = Hell
    self.corpses = [BloodKnight]
    self.favhill = [0]
    self.favsoil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t]



class BloodKnight(Undead):
  name = blood_knight_t
  units = 1
  min_units = 1
  max_squads = 40
  type = 'infantry'
  traits = [death_t, malignant_t]
  size = 2
  gold = 1200
  upkeep = 120
  resource_cost = 25
  food = 0
  pop = 20
  terrain_skills = [DarkVision, NightSurvival]

  hp = 20
  mp = [2, 2]
  moves = 7
  resolve = 10
  global_skills = [FearAura, NightFerocity]

  dfs = 6
  res = 5
  hres = 2
  arm = 1
  armor = HeavyArmor()
  shield = Shield()

  att = 2
  damage = 5
  off = 7
  str = 6
  pn = 2

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    self.favhill = [0]
    self.favsoil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t]



class CryptHorror(Undead):
  name = crypt_horror_t
  units = 8
  min_units = 4
  max_squads = 20
  type = 'beast'
  traits = [death_t, malignant_t]
  size = 4
  gold = 560
  upkeep = 25
  resource_cost = 18
  food = 0
  pop = 20
  terrain_skills = [DarkVision, Fly, NightSurvival]

  hp = 15
  mp = [2, 2]
  moves = 5
  resolve = 10
  global_skills = [FearAura, NightFerocity]

  dfs = 4
  res = 5
  hres = 1
  arm = 2
  armor = None

  att = 3
  damage = 4
  off = 4
  str = 4
  pn = 0
  offensive_skills = [ToxicClaws]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    self.corpses = [Skeleton]



class DireWolf(Undead):
  name = dire_wolf_t
  units = 6
  min_units = 3
  max_squads = 20
  type = 'beast'
  traits = [death_t, malignant_t]
  size = 3
  gold = 850
  upkeep = 30
  resource_cost = 22
  food = 0
  pop = 25
  terrain_skills = [DarkVision, ForestSurvival, MountainSurvival, NightSurvival]

  hp = 24
  mp = [3, 3]
  moves = 6
  resolve = 10
  global_skills = [BloodyBeast, FearAura, NightFerocity]

  dfs = 3
  res = 5
  hres = 1
  arm = 2
  armor = None

  att = 2
  damage = 3
  off = 5
  str = 5
  pn = 1

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [glacier_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class Draugr(Unit):
  name = 'Draugr'
  units = 10
  min_units = 5
  max_squads = 20
  type = 'infantry'
  traits = [death_t, malignant_t, blood_drinker_t]
  size = 4
  gold = 520
  upkeep = 20
  resource_cost = 18
  food = 2
  pop = 30
  terrain_skills = [DarkVision, Burn, ForestSurvival, MountainSurvival, Raid]

  hp = 16
  mp = [2, 2]
  power = 1
  power_max = 1
  power_res = 1
  moves = 6
  resolve = 7
  global_skills = [Scavenger, NightFerocity, Regroup, Trample]

  dfs = 4
  res = 4
  hres = 1
  arm = 2

  att = 2
  damage = 3
  off = 4
  str = 4
  pn = 0
  offensive_skills = [ToxicClaws]
  
  stealth = 4

  fear = 4
  pref_corpses = 1

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [Cannibalize]
    self.align = Hell
    Ground.__init__(self)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, waste_t, tundra_t]
    self.favsurf = [none_t, forest_t, swamp_t]



class FellBat(Undead):
  name = fell_bat_t
  units = 10
  min_units = 5
  max_squads = 10
  type = 'beast'
  traits = [death_t, malignant_t, blood_drinker_t]
  size = 2
  gold = 520
  upkeep = 22
  resource_cost = 16
  food = 0
  pop = 20
  terrain_skills = [DarkVision, ForestSurvival, MountainSurvival]

  hp = 13
  sight = 2
  mp = [4, 4]
  moves = 7
  resolve = 10
  global_skills = [ElusiveShadow, Fly, Helophobia, NightSurvival]

  dfs = 4
  res = 3
  hres = 1
  arm = 0

  att = 3
  damage = 3
  off = 4
  str = 3
  pn = 0
  offensive_skills = [ToxicClaws]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    self.favsurf = [forest_t]



class Ghoul(Human):
  name = ghoul_t
  units = 20
  min_units = 10
  max_squads = 10
  type = 'infantry'
  traits = [human_t, malignant_t, poisonres_t, blood_drinker_t]
  size = 2
  gold = 180
  upkeep = 6
  resource_cost = 11
  food = 2
  pop = 25
  terrain_skills = [Burn, DarkVision, ForestSurvival, MountainSurvival, Raid]

  hp = 12
  mp = [2, 2]
  power = 1
  power_max = 1
  power_res = 1
  moves = 5
  resolve = 5
  global_skills = [Furtive]

  dfs = 3
  res = 3
  hres = 0
  arm = 0
  armor = None

  att = 3
  damage = 1
  off = 4
  str = 3
  pn = 0
  offensive_skills = [ToxicClaws]

  populated_land = 1
  pref_corpses = 1

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    self.spells = [Cannibalize]
    self.corpses = [Draugr]



class Isaac(Unit):
  name = 'isaac'
  units = 10
  min_units = 10
  max_squads = 1
  comm = 1
  type = 'infantry'
  traits = [human_t, malignant_t, commander_t, wizard_t]
  size = 2
  unique = 1
  gold = 3800
  upkeep = 90
  resource_cost = 25
  food = 4
  pop = 30
  terrain_skills = [Burn, DarkVision, Raid]

  hp = 30
  sight = 20
  mp = [2, 2]
  moves = 7
  resolve = 8
  power = 20
  power_max = 40
  power_res = 5
  global_skills = [LordOfBones]

  dfs = 4
  res = 2
  hres = 0
  arm = 0
  armor = MediumArmor()
  shield = Shield()

  att = 2
  damage = 4
  off = 5
  str = 4
  pn = 0
  
  fear = 6
  pref_corpses = 1
  stealth = 6

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [RaiseDead, SummonDraugr, SummonSpectralInfantry]
    self.align = Hell
    self.corpses = [Zombie]



class Necromancer(Human):
  name = necromancer_t
  units = 1
  min_units = 1
  max_squads = 1
  comm = 1
  type = 'infantry'
  traits = [human_t, malignant_t, commander_t, wizard_t]
  size = 2
  gold = 800
  upkeep = 400
  resource_cost = 20
  food = 4
  pop = 30
  terrain_skills = []

  hp = 10
  mp = [2, 2]
  moves = 5
  resolve = 5
  power = 10
  power_max = 20
  power_res = 5
  global_skills = [LordOfBones]

  dfs = 2
  res = 2
  hres = 0
  arm = 0
  armor = None
  shield = Shield()

  att = 1
  damage = 2
  off = 3
  str = 3
  pn = 0
  
  fear = 6
  sort_chance = 100
  pref_corpses = 1
  stealth = 8

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [CastWailingWinds, RaiseDead]
    self.align = Hell
    self.corpses = [CryptHorror]
    self.favhill = [1]
    self.favsurf = [forest_t, swamp_t] 



class GraveGuard(Undead):
  name = grave_guard_t
  units = 10
  min_units = 5
  max_squads = 8
  type = 'infantry'
  traits = [death_t, malignant_t]
  size = 3
  gold = 850
  upkeep = 50
  resource_cost = 18
  food = 0
  pop = 40
  terrain_skills = [Burn, DarkVision, NightSurvival]

  hp = 25
  mp = [2, 2]
  moves = 6
  resolve = 10
  global_skills = [FearAura, NightFerocity]

  dfs = 4
  res = 5
  hres = 1
  arm = 2
  armor = HeavyArmor()
  shield = Shield()

  att = 2
  damage = 4
  off = 5
  str = 5
  pn = 1

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    self.corpses = [Skeleton]
    self.favsoil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t]



class Settler2(Human):
  name = settler_t
  units = 150
  min_units = 150
  max_squads = 1
  settler = 1 
  type = 'civil'
  traits = [human_t, settler_t]
  size = 2
  gold = 1000
  upkeep = 0
  resource_cost = 50
  food = 1
  pop = 250
  terrain_skills = [DesertSurvival]

  hp = 3
  mp = [2, 2]
  moves = 3
  resolve = 2

  dfs = 1
  res = 1
  hres = 0
  arm = 0
  armor = None

  att = 2
  damage = 1
  off = 1
  str = 1
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.buildings = [CursedHamlet]
    self.corpses = [Zombie]



class Skeleton(Undead):
  name = skeleton_t
  units = 20
  min_units = 10
  max_squads = 10
  type = 'infantry'
  traits = [death_t, mindless_t]
  size = 2
  gold = 400
  upkeep = 0
  resource_cost = 10
  food = 0
  pop = 30
  terrain_skills = [Burn]

  hp = 13
  mp = [2, 2]
  moves = 5
  resolve = 10
  global_skills = [SkeletonLegion]

  dfs = 2
  res = 3
  hres = 1
  arm = 1

  att = 2
  damage = 3
  off = 3
  str = 3
  pn = 0

  fear = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    self.corpses = []



class SpectralInfantry(Unit):
  name = 'infantería espectral'
  units = 20
  min_units = 10
  max_squads = 10
  type = 'infantry'
  traits = [death_t]
  size = 2
  gold = 500
  upkeep = 10
  resource_cost = 15
  food = 0
  pop = 45
  terrain_skills = [Burn, DarkVision, Raid]

  hp = 13
  mp = [2, 2]
  moves = 6
  resolve = 10
  global_skills = []

  dfs = 3
  res = 4
  hres = 1
  arm = 0
  armor = MediumArmor()

  att = 1
  damage = 4
  off = 4
  str = 4
  pn = 0

  fear = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    self.corpses = []



class Vampire(Undead):
  name = vampire_t
  units = 1
  min_units = 1
  max_squads = 10
  type = 'beast'
  traits = [death_t, malignant_t, vampire_t]
  size = 2
  gold = 900
  upkeep = 70
  resource_cost = 25
  food = 0
  pop = 20
  terrain_skills = [DarkVision, ForestSurvival, MountainSurvival, NightSurvival]

  hp = 20
  sight = 5
  hp_res = 1
  mp = [2, 2]
  moves = 8
  resolve = 10
  global_skills = [ElusiveShadow, FearAura, Fly, NightFerocity]

  dfs = 5
  res = 4
  hres = 3
  arm = 0
  armor = None

  att = 4
  damage = 7
  off = 5
  str = 5
  pn = 0

  populated_land = 1

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = []
    self.favhill = [0, 1]
    self.favsurf = [forest_t, none_t, swamp_t]



class VampireLord(Undead):
  name = vampirelord_t
  units = 1
  min_units = 1
  max_squads = 1
  comm = 1
  type = 'beast'
  traits = [death_t, commander_t, malignant_t, vampire_t]
  size = 2
  gold = 1200
  upkeep = 200
  resource_cost = 25
  food = 0
  pop = 35
  terrain_skills = [DarkVision, Fly, ForestSurvival, MountainSurvival, NightSurvival]

  hp = 40
  sight = 5
  hp_res = 5
  power = 10
  power_max = 20
  power_res = 3
  mp = [2, 2]
  moves = 9
  resolve = 10
  global_skills = [DarkPresence, ElusiveShadow, FearAura, Helophobia, LordOfBlodd]

  dfs = 6
  res = 5
  hres = 4
  arm = 1
  armor = MediumArmor()

  att = 5
  damage = 9
  off = 6
  str = 5
  pn = 2

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [BloodHeal, RecruitLevy]
    self.corpses = []
    self.favhill = [0, 1]
    self.favsurf = [forest_t, none_t, swamp_t]



class Vargheist(Undead):
  name = 'vargheist'
  units = 1
  min_units = 1
  max_squads = 5
  type = 'beast'
  traits = [death_t, malignant_t, vampire_t]
  size = 2
  gold = 620
  upkeep = 120
  resource_cost = 20
  food = 0
  pop = 50
  terrain_skills = [DarkVision, ForestSurvival, MountainSurvival]

  hp = 27
  sight = 5
  hp_res = 6
  mp = [2, 2]
  moves = 9
  resolve = 10
  global_skills = [ElusiveShadow, FearAura, Fly, Helophobia, NightSurvival, TheBeast]

  dfs = 4
  res = 5
  hres = 5
  arm = 2

  att = 6
  damage = 6
  off = 5
  str = 7
  pn = 2

  fear = 6
  populated_land = 1

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    self.corpses = []
    self.favsurf = [forest_t, swamp_t]



class VladDracul(Undead):
  name = 'Vlad Dracul'
  units = 1
  min_units = 1
  max_squads = 1
  unique = 1
  comm = 1
  type = 'beast'
  traits = [death_t, malignant_t, leader_t, vampire_t, wizard_t]
  size = 2
  gold = 3200
  upkeep = 2620
  resource_cost = 50
  food = 0
  pop = 150
  terrain_skills = [DarkVision, ForestSurvival, MountainSurvival, NightSurvival]

  hp = 60
  sight = 40
  hp_res = 7
  power = 20
  power_max = 60
  power_res = 10
  mp = [2, 2]
  moves = 12
  resolve = 10
  global_skills = [DarkPresence, ElusiveShadow, FearAura, Helophobia, LordOfBlodd, MastersEye]

  dfs = 8
  res = 7
  hres = 5
  arm = 3
  armor = LightArmor()

  att = 6
  damage = 12
  off = 8
  str = 8
  pn = 3

  stealth = 5

  pref_corpses = 1

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [CastBloodRain, CastRainOfToads, Returning]  # , BloodStorm, DarkMantle, SummonBloodKnight]
    self.corpses = []
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [forest_t, none_t]
    self.favhill = 0, 1



class VarGhul(Undead):
  name = varghul_t
  units = 1
  min_units = 1
  max_squads = 5
  comm = 1
  type = 'beast'
  traits = [death_t, malignant_t, commander_t, vampire_t]
  size = 3
  gold = 470
  upkeep = 50
  resource_cost = 20
  food = 5
  pop = 25
  terrain_skills = [DarkVision, NightSurvival]

  hp = 25
  mp = [2, 2]
  power = 1
  power_max = 1
  power_res = 1
  moves = 6
  resolve = 6
  global_skills = [LordOfBlodd, NightFerocity, Scavenger, Trample]

  dfs = 3
  res = 4
  hres = 1
  arm = 2

  att = 4
  damage = 5
  off = 4
  str = 5
  offensive_skills = [ToxicClaws]

  fear = 2
  populated_land = 1

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = [Cannibalize]
    self.align = Hell
    self.corpses = [CryptHorror]
    self.favhill = [0, 1]
    self.favsoil = [waste_t]
    self.favsurf = [forest_t, none_t, swamp_t]



class Zombie(Undead, Ground):
  name = zombie_t
  units = 20
  min_units = 10
  max_squads = 20
  type = 'infantry'
  traits = [death_t, mindless_t]
  size = 2
  gold = 150
  upkeep = 0
  resource_cost = 10
  food = 0
  pop = 20

  hp = 13
  mp = [2, 2]
  moves = 3
  resolve = 10
  global_skills = [Spread]

  dfs = 1
  res = 3
  hres = 0
  arm = 0

  att = 1
  damage = 2
  off = 2
  str = 2
  pn = 0
  offensive_skills = [Surrounded]

  fear = 0
  populated_land = 1
  sort_chance = 70

  def __init__(self, nation):
    super().__init__(nation)



# otros.
class Dock(Building):
  name = 'dock'
  level = 1
  city_unique = 1
  size = 6
  gold = 4000
  grouth = 30
  income = 50
  food = 50
  own_terrain = 1
  tags = ['dock']

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
  gold = 1500
  food = 150
  income = 0
  # public_order = 20
  own_terrain = 1
  tags = [food_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 30]
    self.soil = [grassland_t, plains_t]
    self.surf = [none_t]
    self.hill = [0]
    self.upgrade = [SmallFarm]



class SmallFarm(Fields, Building):
  name = small_farm_t
  level = 2
  base = Fields
  gold = 6000
  food = 300
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
  gold = 15000
  food = 500
  # income = 50
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
  popdef_base = 20 
  popdef_min = 5
  popdef_change = 100
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
  name = 'market'
  level = 1
  gold = 200
  food = 25
  income = 20
  resource_cost = 50
  tags = [food_t, income_t, rest_t]



class Quarry(Building):
  name = 'cantera'
  level = 1
  local_unique = 1
  size = 6
  gold = 10000
  food = 100
  income = 500
  resource = 2
  own_terrain = 1
  tags = [resource_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 100]
    self.soil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [1]



class SawMill(Building):
  name = 'aserradero'
  level = 1
  local_unique = 1
  size = 4
  gold = 8000
  food = 50
  income = 200
  resource = 1.5
  own_terrain = 1
  tags = [resource_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 80]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t]
    self.hill = [0, 1]



class SlaveMarket(Building):
  name = 'mercado de esclavos'
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
  traits = [human_t, order_t]
  pop_pref_hill = [0]
  pop_pref_soil = [grassland_t, plains_t]
  pop_pref_surf = [none_t]
  gold = 30000
  food_limit_builds = 3000
  food_limit_upgrades = 5000
  military_limit_upgrades = 3000
  grouth_base = 4
  grouth_rate = 50
  expansion = 1000
  public_order = 0
  tile_cost = 600
  upkeep_base = 60
  upkeep_change = 200

  attack_factor = 500
  capture_rate = 400
  commander_rate = 7
  explore_range = 3
  scout_factor = 8
  stalk_rate = 200

  city_req_pop_base = 2200
  commander_rate = 10
  pop_limit = 60
  units_animal_limit = 20
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
    # Casilla inicial permitida.
    self.hill = [0]
    self.soil = [plains_t, grassland_t]
    self.surf = [none_t]
    # Terrenos adyacentes permitidos
    self.allow_around_grassland = 4
    self.allow_around_plains = 0
    # terrenos adyacentes no permitidos.
    self.unallow_around_forest = 2
    self.unallow_around_ocean = 2 
    self.unallow_around_swamp = 1
    self.unallow_around_tundra = 0
    self.unallow_around_glacier = 0
    # All terrains.
    self.all_terrains = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]

    # edificios iniciales disponibles.
    self.av_buildings = [Fields, PlaceOfProphecy, Pastures, TrainingCamp, SawMill, Quarry]
    # Cities.
    self.av_cities = [Hamlet]
    # city names.
    self.city_names = roman_citynames
  
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
    self.start_units = [PeasantLevy, PeasantLevy]



class WoodElves(Nation):
  name = wood_elves_t
  nick = ''
  traits = [elf_t, animal_t]
  pop_pref_hill = [0]
  pop_pref_soil = [grassland_t, plains_t, tundra_t]
  pop_pref_surf = [forest_t]
  gold = 30000
  food_limit_builds = 3000
  food_limit_upgrades = 5000
  military_limit_upgrades = 1000
  grouth_base = 2
  grouth_rate = 50
  public_order = 0
  expansion = 2500
  upkeep_base = 60
  upkeep_change = 500

  attack_factor = 600
  capture_rate = 600
  commander_rate = 8
  explore_range = 3
  scout_factor = 5
  stalk_rate = 400

  city_req_pop_base = 2500
  commander_rate = 7
  pop_limit = 30
  units_animal_limit = 100
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
    # Casilla inicial permitida.
    self.hill = [0]
    self.soil = [plains_t, grassland_t]
    self.surf = [forest_t]
    # Terrenos adyacentes permitidos
    self.allow_around_forest = 5
    # terrenos adyacentes no permitidos.
    self.unallow_around_ocean = 2 
    self.unallow_around_swamp = 0
    # All terrains.
    self.all_terrains = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]

    # edificios iniciales disponibles.
    self.av_buildings = [CraftmensTree, FalconRefuge, GlisteningPastures, Grove, Sanctuary, stoneCarvers]
    # Cities.
    self.av_cities = [Hall]
    # City names.
    self.city_names = elven_citynames
  
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
    self.start_units = [ForestGuard, ForestGuard]



class Wallachia(Nation):
  name = wallachia_t
  nick = nation_phrase2_t
  traits = [death_t, malignant_t, vampire_t]
  pop_pref_hill = [0]
  pop_pref_soil = [grassland_t, plains_t, tundra_t]
  pop_pref_surf = [none_t]
  gold = 30000
  food_limit_builds = 3000
  military_limit_upgrades = 3000
  food_limit_upgrades = 4000
  grouth_base = 4
  grouth_rate = 50
  expansion = 1500
  public_order = 0
  upkeep_base = 60
  upkeep_change = 200

  attack_factor = 360
  capture_rate = 300
  commander_rate = 6
  explore_range = 5
  scout_factor = 15
  stalk_rate = 160

  city_req_pop_base = 1600
  commander_rate = 10
  pop_limit = 50
  units_animal_limit = 100
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
    # Casilla inicial permitida.
    self.hill = [0, 1]
    self.soil = [grassland_t, plains_t, waste_t]
    self.surf = [forest_t, none_t]
    # Terrenos adyacentes permitidos
    # self.allow_around_desert = 5
    self.allow_around_hill = 3
    # terrenos adyacentes no permitidos.
    self.unallow_around_ocean = 0
    # All terrains.
    self.all_terrains = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]

    # edificios iniciales disponibles.
    self.av_buildings = [Cemetery, Fields, HallsOfTheDead, HuntingGround, Gallows, Pit, Quarry, SawMill]
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
    self.start_units = [Zombie, Zombie, VampireLord]



# Buildings.
class BrigandLair(Building):
  name = 'brigand lair'
  nation = wild_t
  level = 1
  city_unique = 1
  size = 3
  stealth = 14
  gold = 4000
  unrest = 4
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Raider]
    self.resource_cost = [0, 20]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t, swamp_t]
    self.hill = [0, 1]
    self.upgrade = []



class Campment(Building):
  name = 'campment'
  nation = wild_t
  level = 1
  city_unique = 1
  size = 4
  stealth = 15
  gold = 7000
  unrest = 2
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Rider, Warrior]
    self.resource_cost = [0, 40]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t , swamp_t, none_t]
    self.hill = [0, 1]
    self.upgrade = []



class CaveOfDarkRites(Building):
  name = 'cave of dark rites'
  nation = hell_t
  level = 1
  city_unique = 1
  size = 4
  stealth = 20
  gold = 7000
  unrest = 1
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Harpy, DevoutOfChaos]
    self.resource_cost = [0, 40]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, swamp_t]
    self.hill = [0, 1]
    self.upgrade = []



class CaveOfGhouls(Building):
  name = 'cave of ghouls'
  nation = hell_t
  level = 1
  city_unique = 1
  size = 4
  stealth = 19 
  gold = 6000
  unrest = 2
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Ghoul, VarGhul]
    self.resource_cost = [0, 50]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [0, 1]
    self.upgrade = []



class FightingPit(Building):
  name = 'fighting pit'
  nation = orcs_t
  level = 1
  city_unique = 1
  size = 4
  stealth = 14
  gold = 6000
  unrest = 2
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [OrcWarrior, Orc_Archer]
    self.resource_cost = [0, 50]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, swamp_t, none_t]
    self.hill = [0, 1]
    self.upgrade = []



class GoblinLair(Building):
  name = 'goblin lair'
  nation = orcs_t
  level = 1
  city_unique = 1
  size = 3
  stealth = 19
  gold = 4000
  unrest = 2
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Goblin]
    self.resource_cost = [0, 30]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, swamp_t]
    self.hill = [0, 1]
    self.upgrade = []



class HiddenForest(Building):
  name = 'hidden forest'
  nation = wild_t
  level = 1
  city_unique = 1
  size = 5
  stealth = 20
  gold = 12000
  unrest = 0
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Akhlut]
    self.resource_cost = [0, 60]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [0, 1]
    self.upgrade = []



class HiddenTemple(Building):
  name = 'hidden temple'
  nation = wild_t
  level = 1
  city_unique = 1
  size = 5
  stealth = 18
  gold = 16000
  unrest = 5
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Flagellant, Inquisitor]
    self.resource_cost = [0, 60]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [0, 1]
    self.upgrade = []



class HyenasLair(Building):
  name = 'hyenas lair'
  nation = wild_t
  level = 1
  city_unique = 1
  size = 2
  stealth = 16
  gold = 2000
  unrest = 1
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Hyena]
    self.resource_cost = [0, 20]
    self.soil = [waste_t, grassland_t]
    self.surf = [forest_t, none_t]
    self.hill = [0, 1]
    self.upgrade = []



class NecromancersLair(Building):
  name = 'Necromancers Lair'
  nation = hell_t
  level = 1
  city_unique = 1
  size = 4
  stealth = 20
  gold = 6000
  unrest = 3
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Necromancer, Skeleton, Zombie]
    self.resource_cost = [0, 40]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, swamp_t]
    self.hill = [0, 1]
    self.upgrade = []



class OathStone(Building):
  name = 'oath stone'
  nation = wild_t
  level = 1
  city_unique = 1
  size = 4
  stealth = 15
  gold = 8000
  unrest = 1
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Ogre]
    self.resource_cost = [0, 35]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [none_t]
    self.hill = [1]
    self.upgrade = []



class OpulentTomb(Building):
  name = 'opulent tomb'
  nation = wild_t
  level = 1
  city_unique = 1
  size = 4
  stealth = 22
  gold = 10000
  unrest = 2
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [VampireLord]
    self.resource_cost = [0, 50]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t , swamp_t, none_t]
    self.hill = [0, 1]
    self.upgrade = []



class TroglodyteCave(Building):
  name = 'troglodyte cave'
  nation = wild_t
  level = 1
  city_unique = 1
  size = 4
  stealth = 20
  gold = 12000
  unrest = 2
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Troglodyte]
    self.resource_cost = [0, 50]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t , swamp_t, none_t]
    self.hill = [0, 1]
    self.upgrade = []



class TrollCave(Building):
  name = 'troll cave'
  nation = orcs_t
  level = 1
  city_unique = 1
  size = 4
  stealth = 20
  gold = 12000
  unrest = 1
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Troll]
    self.resource_cost = [0, 60]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [1]
    self.upgrade = []



class UnderworldEntrance(Building):
  name = 'underworld entrance'
  nation = hell_t
  level = 1
  city_unique = 1
  size = 6
  stealth = 24
  gold = 24000
  unrest = 5
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Vargheist, HellHound]
    self.resource_cost = [0, 80]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, swamp_t, none_t]
    self.hill = [0, 1]
    self.upgrade = []



class WisperingWoods(Building):
  name = 'wispering woods'
  nation = wild_t
  level = 1
  city_unique = 1
  size = 5
  stealth = 22
  gold = 12000
  unrest = 1
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Driad]
    self.resource_cost = [0, 60]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t]
    self.hill = [0, 1]
    self.upgrade = []



class WargsCave(Building):
  name = 'Warg cave'
  nation = wild_t
  level = 1
  city_unique = 1
  size = 3
  stealth = 18
  gold = 4000
  unrest = 3
  own_terrain = 0
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Warg]
    self.resource_cost = [0, 40]
    self.soil = [tundra_t]
    self.surf = [forest_t, none_t, swamp_t]
    self.hill = [0, 1]
    self.upgrade = []



class WolfLair(Building):
  name = 'wolf lair'
  nation = nature_t
  level = 1
  city_unique = 1
  size = 2
  stealth = 18
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
class AntleredShaman(Human):
  name = "Antlered Shaman"
  units = 1
  min_units = 1
  max_squads = 1
  comm = 1
  type = 'infantry'
  traits = [beast_t, commander_t, wizard_t]
  size = 2
  gold = 1000
  upkeep = 500
  resource_cost = 20
  food = 4
  pop = 10
  terrain_skills = [ForestSurvival, MountainSurvival]

  hp = 14
  mp = [2, 2]
  moves = 6
  resolve = 6
  power = 6
  power_max = 6
  power_res = 2
  global_skills = []

  dfs = 2
  res = 4
  hres = 0
  arm = 0
  armor = None
  shield = Shield()

  att = 2
  damage = 3
  off = 3
  str = 4
  pn = 0
  
  fear = 6
  sort_chance = 100
  pref_corpses = 0
  stealth = 8

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = []
    self.align = Wild
    self.corpses = []
    self.favhill = [1]
    self.favsurf = [forest_t] 



class DevoutOfChaos(Human):
  name = "devout of chaos"
  units = 1
  min_units = 1
  max_squads = 1
  comm = 1
  type = 'infantry'
  traits = [human_t, malignant_t, commander_t, wizard_t]
  size = 2
  gold = 1200
  upkeep = 600
  resource_cost = 20
  food = 3
  pop = 15
  terrain_skills = []

  hp = 10
  mp = [2, 2]
  moves = 5
  resolve = 5
  power = 10
  power_max = 30
  power_res = 5
  global_skills = []

  dfs = 2
  res = 2
  hres = 0
  arm = 0
  armor = None
  shield = Shield()

  att = 1
  damage = 2
  off = 3
  str = 3
  pn = 0
  
  fear = 6
  sort_chance = 100
  pref_corpses = 0
  stealth = 8

  def __init__(self, nation):
    super().__init__(nation)
    self.spells = []
    self.align = Hell
    self.corpses = [BlackKnight]
    self.favhill = [0, 1]
    self.favsurf = [forest_t] 



class Inquisitor(Human):
  name = inquisitors_t
  units = 10
  min_units = 10
  max_squads = 1
  type = 'infantry'
  traits = [human_t, commander_t]
  size = 2
  gold = 600
  upkeep = 200
  resource_cost = 22
  food = 4
  pop = 20

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 7
  global_skills = [Exaltation, Furtive, Regroup]

  dfs = 2
  res = 2
  hres = 0
  arm = 0
  armor = LightArmor()

  att = 2
  damage = 3
  off = 3
  str = 3
  pn = 0
  offensive_skills = [ShadowHunter]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Zombie]



class WarMonger(Human):
  name = "warmonger"
  units = 1
  min_units = 1
  max_squads = 1
  type = 'infantry'
  traits = [human_t, commander_t]
  size = 2
  gold = 600
  upkeep = 200
  resource_cost = 22
  food = 4
  pop = 20

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 7
  global_skills = [Exaltation, Furtive, Regroup]

  dfs = 2
  res = 2
  hres = 0
  arm = 0
  armor = LightArmor()

  att = 2
  damage = 3
  off = 3
  str = 3
  pn = 0
  offensive_skills = [ShadowHunter]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Zombie]



# Units.
class Archer(Human):
  name = archer_t
  units = 20
  min_units = 10
  max_squads = 5
  type = 'infantry'
  traits = [human_t]
  size = 2
  gold = 460
  upkeep = 6
  resource_cost = 11
  food = 3
  pop = 45
  terrain_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 5
  resolve = 4

  dfs = 1
  res = 2
  hres = 0
  arm = 0
  armor = None

  att = 2
  damage = 1
  rng = 15
  off = 2
  str = 2
  pn = 0
  offensive_skills = [Skirmisher]
  
  fear = 5
  populated_land = 1
  sort_chance = 70

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Zombie]
    self.favhill = [1]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t, forest_t]



class Akhlut(Unit):
  name = 'akhlut'
  units = 1
  min_units = 1
  max_squads = 5
  type = 'beast'
  size = 3
  gold = 320
  upkeep = 60
  resource_cost = 28
  food = 12
  pop = 25
  terrain_skills = [DarkVision, ForestSurvival, MountainSurvival]

  hp = 30
  mp = [2, 2]
  moves = 7
  resolve = 6
  global_skills = [Regroup]

  dfs = 3
  res = 5
  hres = 2
  arm = 2
  armor = None

  att = 4
  damage = 5
  off = 5
  str = 5
  pn = 0

  stealth = 6

  fear = 2

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    Amphibian.__init__(self)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [tundra_t]
    self.favsurf = [forest_t, none_t, swamp_t]
    self.traits += [animal_t, ]



class BlackOrc(Unit):
  name = 'orco negro'
  units = 20
  min_units = 10
  max_squads = 16
  type = 'infantry'
  traits = [orc_t]
  size = 3
  gold = 960
  upkeep = 35
  resource_cost = 20
  food = 6
  pop = 40
  terrain_skills = [Burn, DarkVision, Raid]

  hp = 24
  mp = [2, 2]
  moves = 7
  resolve = 8
  global_skills = [BloodyBeast]

  dfs = 3
  res = 4
  hres = 0
  arm = 2
  armor = HeavyArmor

  att = 3
  damage = 5
  off = 5
  str = 5
  pn = 1

  fear = 2
  populated_land = 1
  sort_chance = 70

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    Ground.__init__(self)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t, forest_t]



class SonOfWind(Human):
  name = 'hijo del viento'
  units = 10
  min_units = 10
  max_squads = 4
  type = 'infantry'
  traits = [human_t]
  size = 2
  gold = 50
  upkeep = 20
  resource_cost = 16
  food = 3
  pop = 30
  terrain_skills = [Burn, DarkVision, DesertSurvival, Raid, MountainSurvival]

  hp = 10
  mp = [2, 2]
  moves = 7
  resolve = 6
  global_skills = [Furtive]

  dfs = 3
  res = 2
  hres = 0
  arm = 0
  armor = LightArmor()
  shield = Shield()

  att = 2
  damage = 4
  off = 5
  str = 3
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Zombie]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]



class Population(Human):
  name = 'population'
  units = 50
  min_units = 10
  max_squads = 5
  type = 'civil'
  traits = [human_t]
  size = 2
  gold = 60
  upkeep = 2
  resource_cost = 8
  food = 4
  pop = 20
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

  att = 1
  damage = 1
  rng = 1
  off = 1
  str = 1
  pn = 0
  
  fear = 5
  populated_land = 1
  sort_chance = 70

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Zombie]
    self.favhill = [1]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t, forest_t]



class Crocodile(Unit):
  name = crocodile_t
  units = 1
  min_units = 1
  max_squads = 20
  type = 'beast'
  size = 3
  gold = 220
  upkeep = 20
  resource_cost = 20
  food = 2
  pop = 10
  terrain_skills = [DarkVision, SwampSurvival]

  hp = 25
  mp = [2, 2]
  moves = 6
  resolve = 4
  global_skills = [Ambushment, Furtive]

  dfs = 3
  res = 4
  hres = 2
  arm = 3
  armor = None

  att = 3
  damage = 5
  off = 5
  str = 5
  pn = 2

  fear = 2
  sort_chance = 100

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    Amphibian.__init__(self)
    self.corpses = [Skeleton]
    self.favhill = [0]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [swamp_t]
    self.traits += [animal_t, ]



class DesertNomad(Human):
  name = 'ginete a camello'
  units = 20
  min_units = 10
  max_squads = 5
  type = 'cavalry'
  traits = [human_t, mounted_t]
  size = 3
  gold = 240
  upkeep = 30
  resource_cost = 18
  food = 4
  pop = 30
  terrain_skills = [Burn, DesertSurvival, Raid]

  hp = 14
  sight = 2
  mp = [3, 3]
  moves = 8
  resolve = 5

  dfs = 2
  res = 3
  hres = 0
  arm = 1
  armor = None
  shield = None

  att = 2
  damage = 2
  off = 4
  str = 3
  pn = 0
  offensive_skills = []
  
  fear = 3
  populated_land = 1
  sort_chance = 80

  def __init__(self, nation):
    super().__init__(nation)
    self.traits += [mounted_t]
    self.align = Wild
    self.corpses = [Skeleton]
    self.favhill = [0]
    self.favsoil = [waste_t]
    self.favsurf = [none_t]



class DevourerOfDemons(Unit):
  name = 'devorador de demonios'
  units = 1
  min_units = 1
  max_squads = 1
  type = 'beast'
  traits = [spirit_t]
  size = 5
  gold = 2200
  upkeep = 1200
  resource_cost = 50
  food = 0
  pop = 0
  terrain_skills = [DarkVision, Fly, ForestSurvival, MountainSurvival, SwampSurvival]

  hp = 150
  sight = 30
  mp = [2, 2]
  moves = 10
  resolve = 10
  global_skills = [ElusiveShadow, Ethereal, FearAura]

  dfs = 4
  res = 6
  hres = 2
  arm = 0
  armor = None

  att = 2
  damage = 10
  off = 8
  str = 8
  pn = 2

  stealth = 5

  fear = 2
  populated_land = 1
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = []
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [forest_t, none_t, swamp_t]
    self.favhill = 0, 1



class Galley(Ship):
  name = 'galera'
  units = 1
  min_units = 1
  max_squads = 5
  type = 'veicle'
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

  att = 1
  damage = 10
  off = 3
  str = 3
  pn = 0
  
  cap = 60

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = []
    self.favhill = [0]
    self.favsoil = [coast_t]
    self.favsurf = [none_t]
    self.traits += ['ship', ]



class GiantBear(Unit):
  name = 'oso gigante'
  units = 1
  min_units = 1
  max_squads = 10
  type = 'beast'
  traits = [animal_t]
  size = 5
  gold = 800
  upkeep = 48
  resource_cost = 26
  food = 8
  pop = 20
  terrain_skills = [ForestSurvival, MountainSurvival]

  hp = 30
  mp = [2, 2]
  moves = 5
  resolve = 6
  global_skills = []

  dfs = 3
  res = 4
  hres = 3
  arm = 4
  armor = None

  att = 3
  damage = 6
  rng = 1
  off = 5
  str = 5
  pn = 0

  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [tundra_t]
    self.favsurf = [forest_t, none_t]



class GiantWolf(Unit):
  name = giant_wolf_t
  units = 5
  min_units = 5
  max_squads = 6
  type = 'beast'
  traits = [animal_t]
  size = 3
  gold = 320
  upkeep = 25
  resource_cost = 18
  food = 6
  pop = 20
  terrain_skills = [DarkVision, ForestSurvival, MountainSurvival]

  hp = 13
  sight = 2
  mp = [2, 2]
  moves = 6
  resolve = 4
  global_skills = [BloodyBeast, NightFerocity, Regroup]

  dfs = 3
  res = 4
  hres = 1
  arm = 1
  armor = None

  att = 1
  damage = 4
  off = 4
  str = 5
  pn = 0
  
  fear = 4
  populated_land = 1
  sort_chance = 70
  stealth = 4

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    Ground.__init__(self)
    self.corpses = [DireWolf]
    self.favhill = [0, 1]
    self.favsoil = [tundra_t]
    self.favsurf = [none_t, forest_t]



class Goblin(Unit):
  name = goblin_t
  units = 40
  min_units = 10
  max_squads = 10
  type = 'infantry'
  traits = [goblin_t]
  size = 1
  gold = 230
  upkeep = 5
  resource_cost = 12
  food = 2
  pop = 50
  terrain_skills = [Burn, ForestSurvival, MountainSurvival, SwampSurvival, Raid]

  hp = 4
  mp = [3, 3]
  moves = 6
  resolve = 4
  global_skills = [BloodyBeast, Furtive, Undisciplined]

  dfs = 4
  res = 1
  hres = 0
  arm = 0
  armor = None

  att = 3
  damage = 2
  rng = 10
  off = 3
  str = 2
  pn = 0
  offensive_skills = [Ambushment, Skirmisher] 
  
  fear = 3
  populated_land = 1
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    Ground.__init__(self)
    self.corpses = [Skeleton]
    self.favsoil = [waste_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, swamp_t]
    self.favhill = [0, 1]
    self.traits += [goblin_t]



class Harpy(Unit):
  name = harpy_t
  units = 20
  min_units = 10
  max_squads = 6
  type = 'beast'
  traits = [malignant_t, poisonres_t]
  size = 2
  gold = 90
  upkeep = 10
  resource_cost = 16
  food = 0
  pop = 45
  terrain_skills = [Fly, ForestSurvival, MountainSurvival, Raid]

  hp = 13
  sight = 3
  mp = [4, 4]
  moves = 7
  resolve = 4
  global_skills = [Furtive]

  dfs = 4
  res = 3
  hres = 0
  arm = 1
  armor = None

  att = 2
  damage = 2
  off = 3
  str = 3
  pn = 0
  
  fear = 1
  populated_land = 1
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    self.favhill = [0, 1]    
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [forest_t, swamp_t]
    self.soil += [coast_t]
    self.traits += [mounster_t]



class HellHound(Undead):
  name = hellhound_t
  units = 2
  min_units = 1
  max_squads = 5
  type = 'beast'
  traits = [death_t, malignant_t]
  size = 3
  gold = 160
  upkeep = 20
  resource_cost = 30
  food = 0
  pop = 25
  terrain_skills = [DarkVision, DesertSurvival, ForestSurvival, MountainSurvival, NightSurvival]

  hp = 28
  sight = 10
  mp = [2, 2]
  moves = 6
  resolve = 10
  global_skills = [BloodyBeast, NightFerocity, Regroup]

  dfs = 3
  res = 5
  hres = 2
  arm = 2
  armor = None

  att = 2
  damage = 5
  off = 4
  str = 5
  pn = 0
  
  fear = 2
  stealth = 8

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [plains_t, tundra_t, waste_t]



class Hyena(Unit):
  name = 'hyaena'
  units = 30
  min_units = 5
  max_squads = 12
  type = 'beast'
  traits = [animal_t]
  size = 2
  gold = 210
  upkeep = 14
  resource_cost = 15
  food = 4
  pop = 65
  terrain_skills = [DarkVision, NightSurvival]

  hp = 12
  sight = 2
  mp = [2, 2]
  moves = 6
  resolve = 4
  global_skills = [BloodyBeast, Regroup]

  dfs = 3
  res = 3
  hres = 1
  arm = 1
  armor = None

  att = 1
  damage = 3
  off = 4
  str = 4
  pn = 1
  
  fear = 5
  populated_land = 1
  sort_chance = 90
  stealth = 5

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    Ground.__init__(self)
    self.corpses = [HellHound]
    self.favhill = [0]
    self.favsoil = [plains_t, waste_t]
    self.favsurf = [forest_t, none_t]
    self.traits += [animal_t]



class Hunter(Human):
  name = hunter_t
  units = 10
  min_units = 10
  max_squads = 4
  type = 'infantry'
  traits = [human_t]
  size = 2
  gold = 90
  upkeep = 6
  resource_cost = 12
  food = 3
  pop = 12
  terrain_skills = [ForestSurvival, MountainSurvival, Raid]

  hp = 10
  sight = 2
  mp = [2, 2]
  moves = 5
  resolve = 4
  global_skills = [Furtive]

  dfs = 2
  res = 2
  hres = 0
  arm = 0
  armor = None

  att = 1
  rng = 10
  damage = 4
  off = 3
  str = 3
  pn = 0
  offensive_skills = [Ambushment, Skirmisher]

  fear = 6
  populated_land = 1
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Zombie]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class NomadsRider(Human):
  name = nomads_rider_t
  units = 20
  min_units = 10
  max_squads = 6
  type = 'cavalry'
  traits = [human_t, mounted_t]
  size = 3
  gold = 240
  upkeep = 25
  resource_cost = 18
  food = 5
  pop = 40
  terrain_skills = [Burn, Raid]

  hp = 14
  mp = [4, 4]
  moves = 6
  resolve = 4

  dfs = 3
  res = 3
  hres = 1
  arm = 1
  armor = None

  att = 2
  rng = 15
  damage = 2
  off = 4
  str = 3
  pn = 0
  offensive_skills = [Skirmisher]

  fear = 3
  populated_land = 1
  sort_chance = 90
  stealth = 4

  def __init__(self, nation):
    super().__init__(nation)
    self.traits += [mounted_t]
    self.align = Wild
    self.corpses = [Skeleton]
    self.favhill = [0]
    self.favsoil = [plains_t, grassland_t, tundra_t]
    self.favsurf = [none_t]
    self.traits += [mounted_t]



class Orc_Archer(Unit):
  name = orc_archer_t
  units = 30
  min_units = 10
  max_squads = 10
  type = 'infantry'
  traits = [orc_t]
  size = 2
  gold = 240
  upkeep = 10
  resource_cost = 12
  food = 3
  pop = 50
  terrain_skills = [Burn, DarkVision, ForestSurvival, MountainSurvival, Raid]

  hp = 12
  mp = [2, 2]
  moves = 5
  resolve = 4
  global_skills = [BloodyBeast, Undisciplined]

  dfs = 3
  res = 2
  hres = 0
  arm = 1
  armor = None

  att = 2
  damage = 2
  rng = 15
  off = 3
  str = 4
  pn = 0
  offensive_skills = [Ambushment, Skirmisher]
  
  fear = 4
  populated_land = 1
  sort_chance = 80
  stealth = 4

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    Ground.__init__(self)
    self.corpses = [Skeleton]
    self.favhill = [1]    
    self.favsoil = [waste_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t, forest_t]
    self.traits += [orc_t]



class OrcWarrior(Unit):
  name = 'orc warriors'
  units = 40
  min_units = 10
  max_squads = 10
  type = 'infantry'
  traits = [orc_t]
  size = 2
  gold = 320
  upkeep = 13
  resource_cost = 10
  food = 3
  pop = 60
  terrain_skills = [Burn, DarkVision, ForestSurvival, MountainSurvival, Raid]

  hp = 14
  mp = [2, 2]
  moves = 6
  resolve = 4
  global_skills = [BloodyBeast, Undisciplined]

  dfs = 3
  res = 3
  hres = 1
  arm = 1
  armor = None

  att = 2
  damage = 3
  off = 3
  str = 3
  pn = 0
  
  fear = 4
  populated_land = 1
  sort_chance = 80
  stealth = 4

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    Ground.__init__(self)
    self.corpses = [Skeleton]
    self.favsoil = [waste_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t, forest_t]
    self.traits += [orc_t]



class Levy(Human):
  name = levy_t
  units = 30
  min_units = 10
  max_squads = 10
  type = 'infantry'
  traits = [human_t, levy_t]
  size = 2
  gold = 140
  upkeep = 4
  resource_cost = 11
  food = 3
  pop = 30
  terrain_skills = [Burn, Raid]

  hp = 9
  mp = [2, 2]
  moves = 5
  resolve = 5
  global_skills = [PyreOfCorpses, Undisciplined]

  dfs = 2
  res = 2
  hres = 0
  arm = 0
  armor = None
  shield = Shield()

  att = 1
  damage = 3
  off = 2
  str = 2
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t]
    self.favhill = [0]



class LizardMan(Human):
  name = 'lizardman'
  units = 20
  min_units = 10
  max_squads = 10
  type = 'infantry'
  traits = [lizard_t, poisonres_t]
  size = 2
  gold = 260
  upkeep = 14
  resource_cost = 8
  food = 2
  pop = 30
  terrain_skills = [Burn, DarkVision, Raid, SwampSurvival]

  hp = 12
  mp = [2, 2]
  moves = 7
  resolve = 4
  global_skills = []

  dfs = 4
  res = 3
  hres = 2
  arm = 2
  armor = None
  shield = None

  att = 2
  damage = 3
  off = 4
  str = 3
  pn = 0

  fear = 5
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.other_skills = [Miasma(self)]
    self.align = Wild
    self.favhill = [0]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [swamp_t]



class LizardManHeavyInfantry(Human):
  name = 'lizardman heavy infantry'
  units = 20
  min_units = 10
  max_squads = 6
  type = 'infantry'
  traits = [lizard_t, poisonres_t]
  size = 2
  gold = 420
  upkeep = 160
  resource_cost = 18
  food = 2
  pop = 30
  terrain_skills = [Burn, DarkVision, Raid, SwampSurvival]

  hp = 12
  mp = [2, 2]
  moves = 6
  resolve = 6
  global_skills = []

  dfs = 4
  res = 3
  hres = 2
  arm = 2
  armor = HeavyArmor()
  shield = Shield()

  att = 2
  damage = 3
  off = 4
  str = 4
  pn = 0

  fear = 5
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.favhill = [0]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [swamp_t]



class Mandeha(Unit):
  name = 'mandeha'
  units = 1
  min_units = 1
  max_squads = 1
  type = 'beast'
  traits = []
  size = 5
  gold = 3200
  upkeep = 540
  resource_cost = 40
  food = 7
  pop = 30
  terrain_skills = [DarkVision, ForestSurvival, MountainSurvival]

  hp = 80
  hp_res = 12
  sight = 100
  mp = [2, 2]
  moves = 6
  resolve = 10
  global_skills = [DeepestDarkness, FearAura]

  dfs = 5
  res = 8
  hres = 4
  arm = 2
  armor = None

  att = 3
  damage = 15
  rng = 2
  off = 6
  str = 6
  pn = 2
  offensive_skills = []

  fear = 2

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class Mammot(Unit):
  name = 'mammot'
  units = 2
  min_units = 2
  max_squads = 10
  type = 'beast'
  traits = [animal_t]
  size = 6
  gold = 1260
  upkeep = 185
  resource_cost = 28
  food = 10
  pop = 20
  terrain_skills = [Burn]

  hp = 40
  mp = [2, 2]
  moves = 5
  resolve = 5
  global_skills = [Trample]

  dfs = 4
  res = 5
  hres = 3
  arm = 4
  armor = None

  att = 2
  damage = 5
  off = 4
  str = 5
  pn = 0

  fear = 5
  populated_land = 1
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    Ground.__init__(self)
    self.corpses = [Skeleton]
    self.favhill = [0]
    self.favsoil = [tundra_t]
    self.favsurf = [none_t]



class MASTER(Unit):
  name = 'MASTER'
  units = 1
  min_units = 1
  max_squads = 1
  unique = 1
  type = 'DEBUG ONLY'
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
  global_skills = [DarkPresence, ElusiveShadow, FearAura, Fly, LordOfBlodd, MastersEye, NightFerocity, NightSurvival]
  power = 2000000
  power_max = 2000000
  power_res = 5

  dfs = 8
  res = 7
  arm = 0
  armor = LightArmor()

  att = 6
  damage = 6
  off = 8
  str = 8
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
  name = 'ogro'
  units = 10
  min_units = 5
  max_squads = 20
  type = 'beast'
  traits = [ogre_t]
  size = 3
  gold = 560
  upkeep = 18
  resource_cost = 18
  food = 6
  pop = 20
  terrain_skills = [Burn, Raid]

  hp = 22
  mp = [2, 2]
  moves = 5
  resolve = 6
  global_skills = [BloodyBeast]

  dfs = 3
  res = 5
  hres = 2
  arm = 2
  armor = None

  att = 1
  rng = 2
  damage = 4
  off = 3
  str = 4
  pn = 0

  fear = 2
  populated_land = 1
  sort_chance = 80

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    Ground.__init__(self)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t, forest_t]



class PaleOne(Unit):
  name = 'pale one'
  units = 20
  min_units = 10
  max_squads = 6
  type = 'beast'
  traits = []
  size = 2
  gold = 340
  upkeep = 14
  resource_cost = 12
  food = 1
  pop = 25
  terrain_skills = [DarkVision, Burn, MountainSurvival, Raid]

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 5
  global_skills = []

  dfs = 3
  res = 3
  hres = 1
  arm = 0
  armor = LightArmor

  att = 2
  damage = 3
  off = 3
  str = 3
  pn = 0

  fear = 5
  populated_land = 0
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    Ground.__init__(self)
    self.corpses = [Skeleton]
    self.favhill = [1]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t]



class Peasant(Human):
  name = "peasant"
  units = 40
  min_units = 10
  max_squads = 20
  type = "civil"
  traits = [human_t]
  size = 2
  gold = 80
  upkeep = 2
  resource_cost = 7
  food = 3
  pop = 40
  terrain_skills = [Burn]

  hp = 6
  mp = [2, 2]
  moves = 5
  resolve = 3
  global_skills = [PyreOfCorpses, Undisciplined]

  dfs = 1
  res = 2
  hres = 0
  arm = 0
  armor = None

  att = 2
  damage = 1
  off = 2
  str = 2
  pn = 0

  fear = 5

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Zombie]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t]
    self.favhill = [0]



class PeasantLevy(Human):
  name = peasant_levie_t
  units = 40
  min_units = 10
  max_squads = 12
  type = 'infantry'
  traits = [human_t, levy_t]
  size = 2
  gold = 100
  upkeep = 3
  resource_cost = 9
  food = 3
  pop = 50
  terrain_skills = [Burn]

  hp = 8
  mp = [2, 2]
  moves = 5
  resolve = 4
  global_skills = [PyreOfCorpses, Undisciplined]

  dfs = 1
  res = 2
  hres = 0
  arm = 0
  armor = None

  att = 2
  damage = 1
  off = 2
  str = 2
  pn = 0

  fear = 5

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Zombie]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t]
    self.favhill = [0]



class Raider(Human):
  name = raider_t
  units = 20
  min_units = 10
  max_squads = 5
  type = 'infantry'
  traits = [human_t]
  size = 2
  gold = 150
  upkeep = 10
  resource_cost = 14
  food = 3
  pop = 25
  terrain_skills = [Burn, DarkVision, ForestSurvival, MountainSurvival, SwampSurvival, Raid]

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 4
  global_skills = [Furtive, Undisciplined]

  dfs = 2
  res = 2
  hres = 0
  arm = 0
  armor = LightArmor()

  att = 1
  damage = 2
  off = 3
  str = 3
  pn = 0
  
  fear = 4
  populated_land = 1
  sort_chance = 80

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Zombie]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [forest_t, none_t, swamp_t]



class Rider(Human):
  name = rider_t
  units = 20
  min_units = 10
  max_squads = 4
  type = 'cavalry'
  traits = [human_t, mounted_t]
  size = 3
  gold = 380
  upkeep = 20
  resource_cost = 16
  food = 6
  pop = 32
  terrain_skills = [Burn, Raid]

  hp = 14
  mp = [4, 4]
  moves = 8
  resolve = 6
  global_skills = [Undisciplined]

  dfs = 3
  res = 3
  hres = 0
  arm = 1
  armor = None

  att = 2
  damage = 3
  off = 4
  str = 4
  pn = 0
  offensive_skills = [Charge]

  fear = 4
  populated_land = 1
  sort_chance = 80

  def __init__(self, nation):
    super().__init__(nation)
    self.traits += [mounted_t]
    self.align = Wild
    self.corpses = [Skeleton]
    self.favhill = [0]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t]



class Satyr(Human):
  name = 'satyr'
  units = 10
  min_units = 10
  max_squads = 4
  type = 'infantry'
  traits = []
  size = 2
  gold = 200
  upkeep = 10
  resource_cost = 12
  food = 2
  pop = 12
  terrain_skills = [Burn, ForestSurvival, MountainSurvival, Raid]

  hp = 15
  mp = [2, 2]
  moves = 6
  resolve = 6
  global_skills = []

  dfs = 2
  res = 2
  hres = 0
  arm = 0
  armor = None

  att = 3
  damage = 2
  off = 3
  str = 3
  pn = 0
  offensive_skills = [Charge]

  fear = 4
  populated_land = 1
  sort_chance = 80

  def __init__(self, nation):
    super().__init__(nation)
    self.traits += [mounted_t]
    self.align = Wild
    self.corpses = [Skeleton]
    self.favhill = [0]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t]



class Slave(Human):
  name = "slave"
  units = 20
  min_units = 10
  max_squads = 60
  type = "civil"
  traits = [human_t]
  size = 2
  gold = 220
  upkeep = 2
  resource_cost = 7
  food = 3
  pop = 20
  terrain_skills = [Burn]

  hp = 6
  mp = [2, 2]
  moves = 5
  resolve = 3
  global_skills = [PyreOfCorpses, Undisciplined]

  dfs = 1
  res = 2
  hres = 0
  arm = 0
  armor = None

  att = 2
  damage = 1
  off = 2
  str = 2
  pn = 0

  fear = 5

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Zombie]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t]
    self.favhill = [0]



class SlaveHunter(Human):
  name = 'cazador esclavo'
  units = 10
  min_units = 5
  max_squads = 5
  type = 'infantry'
  traits = [human_t, slaves_t]
  size = 2
  gold = 350
  upkeep = 2
  resource_cost = 1
  food = 3
  pop = 0
  terrain_skills = [ForestSurvival, MountainSurvival, Raid]

  hp = 10
  sight = 2
  mp = [2, 2]
  moves = 5
  resolve = 2
  global_skills = [Undisciplined]

  dfs = 2
  res = 2
  hres = 0
  arm = 0
  armor = None

  att = 1
  rng = 10
  damage = 3
  off = 3
  str = 3
  pn = 0
  offensive_skills = [Ambushment, Skirmisher]

  fear = 6
  populated_land = 1
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Zombie]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]



class SlaveWarrior(Human):
  name = 'guerrero esclavo'
  units = 20
  min_units = 10
  max_squads = 8
  type = 'infantry'
  traits = [human_t, slaves_t]
  size = 2
  gold = 360
  upkeep = 3
  resource_cost = 10
  food = 3
  pop = 0
  terrain_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 4
  global_skills = [PyreOfCorpses, Undisciplined]

  dfs = 2
  res = 2
  hres = 0
  arm = 0
  armor = None
  shield = Shield()

  att = 1
  damage = 2
  off = 4
  str = 3
  pn = 0

  fear = 5
  populated_land = 1
  sort_chance = 70

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Zombie]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, none_t]



class TheKnightsTemplar(Human):
  name = the_knights_templar_t
  units = 20
  min_units = 10
  max_squads = 6
  type = 'cavalry'
  traits = [human_t, mounted_t]
  size = 3
  gold = 850
  upkeep = 60
  resource_cost = 30
  food = 8
  pop = 70
  terrain_skills = [Burn, Raid]

  hp = 15
  mp = [3, 3]
  moves = 8
  resolve = 8
  global_skills = [BattleBrothers, Regroup, Refit, Trample]

  dfs = 4
  res = 3
  hres = 0
  arm = 2
  armor = HeavyArmor()

  att = 2
  damage = 4
  damage_charge_mod = 1
  off = 6
  str = 5
  pn = 2
  offensive_skills = [HeavyCharge]

  def __init__(self, nation):
    super().__init__(nation)
    self.traits += [mounted_t]
    self.align = Wild
    self.corpses = [BloodKnight]
    self.favhill = [0]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t]



class Troglodyte(Unit):
  name = 'troglodyte'
  units = 6
  min_units = 6
  max_squads = 10
  type = 'beast'
  traits = [troglodyte_t]
  size = 3
  gold = 540
  upkeep = 22
  resource_cost = 18
  food = 3
  pop = 10
  terrain_skills = [DarkVision, Burn, MountainSurvival, Raid]

  hp = 30
  mp = [2, 2]
  moves = 5
  resolve = 6
  global_skills = [Trample]

  dfs = 2
  res = 3
  hres = 2
  arm = 0
  armor = None

  att = 2
  damage = 5
  off = 3
  str = 5
  pn = 0

  fear = 1
  populated_land = 1
  sort_chance = 98

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    Ground.__init__(self)
    self.corpses = [Skeleton]
    self.favhill = [1]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t]



class Troll(Unit):
  name = 'troll'
  units = 2
  min_units = 1
  max_squads = 8
  type = 'beast'
  traits = [troll_t]
  size = 5
  gold = 1200
  upkeep = 60
  resource_cost = 22
  food = 6
  pop = 10
  terrain_skills = [Burn, ForestSurvival, MountainSurvival, Raid]

  hp = 30
  mp = [2, 2]
  moves = 5
  resolve = 5
  global_skills = [Trample]

  dfs = 4
  res = 5
  hres = 5
  arm = 5
  armor = None

  att = 2
  damage = 4
  off = 4
  str = 5
  pn = 0

  fear = 2
  populated_land = 1
  sort_chance = 70

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    Ground.__init__(self)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t, forest_t]



class Warg(Unit):
  name = 'huargo'
  units = 20
  min_units = 5
  max_squads = 12
  type = 'beast'
  traits = [malignant_t]
  size = 2
  gold = 240
  upkeep = 35
  resource_cost = 18
  food = 6
  pop = 30
  terrain_skills = [DarkVision, ForestSurvival, MountainSurvival]

  hp = 16
  sight = 3
  mp = [2, 2]
  moves = 7
  resolve = 5
  global_skills = [BloodyBeast, Furtive, Regroup, Undisciplined]

  dfs = 3
  res = 3
  hres = 1
  arm = 1
  armor = None

  att = 2
  damage = 4
  off = 4
  str = 4
  pn = 0
  
  fear = 4
  populated_land = 1
  sort_chance = 70
  stealth = 5

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    Ground.__init__(self)
    self.corpses = [Skeleton]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]
    self.traits += [mounster_t]



class Warrior(Human):
  name = warrior_t
  units = 20
  min_units = 10
  max_squads = 10
  type = 'infantry'
  traits = [human_t]
  size = 2
  gold = 70
  upkeep = 8
  resource_cost = 10
  food = 3
  pop = 25
  terrain_skills = [Burn, Raid]

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 6
  global_skills = [PyreOfCorpses]

  dfs = 2
  res = 2
  hres = 0
  arm = 0
  armor = None

  att = 2
  damage = 2
  off = 4
  str = 3
  pn = 0

  fear = 5
  populated_land = 1
  sort_chance = 70

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Zombie]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, none_t]



class WeetOne(Unit):
  name = 'weet one'
  units = 20
  min_units = 10
  max_squads = 6
  type = 'beast'
  traits = []
  size = 3
  gold = 380
  upkeep = 14
  resource_cost = 14
  food = 1
  pop = 30
  terrain_skills = [DarkVision, Burn, SwampSurvival, Raid]

  hp = 10
  mp = [2, 2]
  moves = 6
  resolve = 5
  global_skills = []

  dfs = 3
  res = 3
  hres = 1
  arm = 0
  armor = None

  att = 2
  damage = 3
  off = 3
  str = 3
  pn = 0

  fear = 7
  populated_land = 0
  sort_chance = 90

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Nature
    Ground.__init__(self)
    self.soil += [coast_t]
    self.corpses = [Skeleton]
    self.favhill = [0]
    self.favsoil = [coast_t, swamp_t]
    self.favsurf = [none_t]



class Wolf(Unit):
  name = wolf_t
  units = 20
  min_units = 10
  max_squads = 6
  type = 'beast'
  traits = [animal_t]
  size = 2
  gold = 120
  upkeep = 10
  resource_cost = 14
  food = 3
  pop = 30
  terrain_skills = [DarkVision, ForestSurvival]

  hp = 10
  sight = 3
  mp = [2, 2]
  moves = 7
  resolve = 4
  global_skills = [Furtive, NightFerocity, Regroup]

  dfs = 3
  res = 3
  hres = 0
  arm = 0
  armor = None

  att = 1
  damage = 2
  off = 3
  str = 3
  pn = 0
  offensive_skills = [Ambushment]
  
  fear = 4
  populated_land = 1
  sort_chance = 70

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    Ground.__init__(self)
    self.corpses = [DireWolf]
    self.favhill = [0]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t, forest_t]



class Hell(Nation):
  name = hell_t
  show_info = 0

  def __init__(self):
    super().__init__()
    self.log = [[hell_t]]
    self.av_units = [Ghoul, Harpy, HellHound, Necromancer, Ogre,
                     Skeleton, Troglodyte, Vargheist, VarGhul, Zombie]
                     


class Nature(Nation):
  name = nature_t
  show_info = 0

  def __init__(self):
    super().__init__()
    self.log = [[nature_t]]
    self.av_units = [Akhlut, Crocodile, Hyena, GiantBear, GiantWolf, Mammot, Wolf]



class Orcs(Nation):
  name = orcs_t
  show_info = 0

  def __init__(self):
    super().__init__()
    self.log = [[orcs_t]]
    self.av_units = [Orc_Archer, OrcWarrior, Goblin, Ogre, Troll, Troglodyte, Warg]



class Wild(Nation):
  name = wild_t
  show_info = 0
  gold = 3000

  def __init__(self):
    super().__init__()
    self.log = [[wild_t]]
    self.av_units = [DesertNomad, Hunter, Mammot, NomadsRider, LizardMan,
                     Raider, Troglodyte,
                       
                     Warrior, Wolf]



# Spells.
from data.spells import *
