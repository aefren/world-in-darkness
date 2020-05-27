# -*- coding: utf-8 -*-
#!/usr/bin/env python
#from math import ceil, floor
#from pdb import Pdb
#from random import randint, shuffle, choice, uniform
#from time import sleep, process_time

#from numpy import mean

#from basics import *
from data.events import *
from data.lang.es import *
from data.names import *
from data.skills import *
#from log_module import *
#from screen_reader import *
#from sound import *

class Empty:
  pass


class LightArmor:

  def __init__(self):
    self.arm = 1
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
  around_coast = 0
  base = None
  citylevel = None
  food = 1
  resource = 1
  income = 0
  food_pre = 1
  free_terrain = 0
  gold = 0
  grouth = 1
  grouth_total = 0
  grouth_pre = 1
  income = 1
  income_pre = 1
  is_complete = 0
  name = None
  nation = None
  nick = None
  own_terrain = 1
  prod_progress = 0
  public_order = 1
  public_order_pre = 1
  res_pre = 1
  size = 5
  type = building_t
  tag = []
  unique = 0
  upkeep = 0
  upgrade = []

  def __init__(self, nation, pos):
    self.nation = nation
    self.pos = pos
    self.av_units = []
    self.av_units_pre = []
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
      self.res_pre = base.resource 
  
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
    upgrade.pos = self.pos
    upgrade.size = self.size
    if self.pos.city: msg = [f'se actualizará {self} en {self.pos.city}, {self.pos} {self.pos.cords}.']
    else: msg = [f'se actualizará {self} en {self.pos} {self.pos.cords}.']
    upgrade.nation.log[-1].append(msg)
    self.pos.buildings[self.pos.buildings.index(self)] = upgrade

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

  def check_tile_req(self, pos):
    go = 1
    if self.citylevel and self.pos.city.name != self.citylevel: go = 0
    if pos.soil.name not in self.soil: go = 0
    if pos.surf.name not in self.surf: go = 0
    if pos.hill not in self.hill: go = 0
    if self.around_coast > 0 and pos.around_coast < self.around_coast: go = 0
    if pos.nation and self.free_terrain: go = 0
    if pos.nation != self.nation and self.own_terrain: go = 0    
    return go

  def launch_event(self):
    pass

  def __str__(self):
    name = f'{self.name}.' 
    if self.nick:
      name += f' {self.nick}.'
    return name

  def update(self):
    self.is_complete = 1 if self.resource_cost[0] >= self.resource_cost[1] else 0


class City:
  around_coast = 0
  around_threat = 0
  base = None
  defense = 0
  defense_pred = 0
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
    pos.update(itm.nation)
    if itm.pos.city: msg = f'se construirá {itm} en {itm.pos.city}, {itm.pos} {itm.pos.cords}.'
    else: msg = f'se construirá {itm} en {itm.pos} {itm.pos.cords}.'
    logging.info(msg)
    itm.nation.log[-1].append(msg)
    self.update()

  def add_pop(self, number, info = 0):
    [i.update(self.nation) for i in self.tiles]
    tiles = [i for i in self.tiles if i.blocked == 0
             and i.soil.name != coast_t]
    shuffle(tiles)
    tiles.sort(key = lambda x: x.food, reverse = True)
    grouth = ceil(number / 200)
    if info: logging.info(f'crecerá {number}. grouth_total {grouth}.')
    tries = 5000
    while number > 0:
      tries -= 1
      if tries < 0: 
        sp.speak(f'add pop stoped!', 1)
        sleep(2)
        
      for t in tiles:
        rnd = 3
        if t.surf and t.surf.name == swamp_t: rnd -= 2
        if t.surf and t.surf.name == forest_t: rnd -= 1
        if t.hill: rnd -= 1
        if t.is_city: rnd += 3
        rnd += ceil((t.food - t.pop) / 50)
        rnd -= t.unrest // 10
        if rnd < 1:
          rnd = 1
          if t.soil.name == grassland_t and t.surf.name == none_t and t.hill == 0: 
            rnd += 4 
            if t.buildings: rnd += 2
            if t.is_city: rnd += 2
            rnd -= t.unrest // 10
            if rnd < 1: rnd = 0
        roll = randint(1, 12)
        if info:  logging.debug(f'{t}. {rnd=:}, {roll=:}. {ceil((t.food-t.pop)/50)}.')
        
        try:
          if rnd >= roll:
              t.pop += grouth
              number -= grouth
        except:
          logging.debug(f'error')

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
      if bu.resource_cost[0] < bu.resource_cost[1]: 
        bu.resource_cost[0] += self.resource_total
        if bu.resource_cost[0] >= bu.resource_cost[1]:
          bu.resource_cost[0] = bu.resource_cost[1]
          if bu.pos.city: msg = f'{bu} {complete_t} en {bu.pos.city}, {bu.pos} {bu.pos.cords}.'
          else: msg = f'. ({bu}) {complete_t} en {bu.pos} {bu.pos.cords}.'
          self.nation.log[-1].append(msg)
          if self.nation.show_info: sleep(loadsound('notify6', channel = ch2) * 0.2)

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
        if self.nation.show_info: sleep(loadsound('notify24', channel = ch4) * 0.5)
        if self.production: self.prod_progress = self.production[0].resource_cost

  def get_defense_info(self):
    self.set_defense()
    self.defense_total = 0
    self.hostile_ranking = 0
    units = [i for i in self.units if i.nation == self.nation and i.goal == None and i.leader == None]
    self.defense = sum(i.ranking for  i in self.pos.units if i.garrison)
    for i in self.units:
      if i.garrison and i.pos == self.pos: i.city = self 
    self.defense_total = sum(i.ranking for i in units 
                             if i.scout == 0 and i.settler == 0)
    if self.defense: self.defense_total_percent = round(self.defense_total * 100 / self.defense)
    for t in self.tiles:
      t.update(self.nation)
      self.hostile_ranking += t.threat
    
    self.defense = round(self.defense)
    self.defense_need = round(self.defense_pred - self.defense)
    self.defense_total = round(self.defense_total)
    self.defense_percent = round(self.defense * 100 / self.defense_pred)

  def get_popdef(self):
    popdef = self.popdef_base
    popdef -= round(self.pop / self.popdef_change)
    if popdef < self.popdef_min:
      popdef = self.popdef_min
    
    self.defense_base = round(popdef * self.pop / 100)
    return popdef

  def get_threats(self):
    self.threat_inside = 0
    for ti in self.tiles:
      self.threat_inside += ti.threat

  def get_tiles_defense(self, items):
    tiles = []
    for i in items:
      if i.defense_terrain > 0: tiles.append(i)
    
    return tiles

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
    logging.debug(f'ingreso previo {income}.')
    income -= self.raid_outcome
    logging.debug(f'perdida por saqueo {self.raid_outcome}.')
    self.nation.gold += round(income)
    logging.info(f'recibe {income} oro de {self}.')
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

  def reduce_pop(self, number, info = 0):
    logging.debug(f'reduce {number} de {self} ({self.pop} pop).')
    tiles = [i for i in self.tiles if i.blocked == 0]
    reduce = number / 20
    shuffle(tiles)
    if info: logging.debug(f'reducirá {number}.')
    while number > 0:
      for t in tiles:
        if t.pop >= reduce and number > 0:
          if info: logging.debug(f'{t.pop} en {t} {t.cords}.')
          t.pop -= reduce
          number -= reduce

  def set_av_units(self):
    self.all_av_units = []
    for t in self.tiles:
      for b in t.buildings:
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
    self.popdef = self.get_popdef()
    self.defense_pred = round(self.popdef * self.pop / 100) // 2
    self.set_seen_units(info = 0)
    units = []
    for l in self.seen_units[-5:]:
      for uni in l: 
        if uni not in units and self.pos.get_distance(uni.pos, self.pos) <= 3: units.append(uni)
    self.seen_threat = sum([i.ranking for i in units])
    
    if self.pos.around_threat > self.defense: self.defense_pred = self.seen_threat // 2
    if self.defense_pred < self.defense_base / 2: self.defense_pred = self.defense_base / 2

  def set_downgrade(self):
    pass

  def set_military_limit(self):
    self.military_limit = (self.military_base + 
                           (self.pop / self.military_change)) 
    if self.military_limit > self.military_max: 
      self.military_limit = self.military_max
    if self.seen_threat > self.defense_total // 2 or self.defense < self.defense_pred: 
      self.military_limit *= 2

  def set_name(self):
    if self.nation.city_names: 
      shuffle(self.nation.city_names)
      self.nick = self.nation.city_names.pop()

  def set_seen_units(self, new = 0, info = 0):
    # logging.debug(f'set seen units {self}.')
    tiles = [t for t in self.pos.get_near_tiles(6)
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
    
    self.seen_animal = []
    self.seen_fly = []
    self.seen_human = []
    self.seen_mounted = []
    self.seen_ranged = []
    self.seen_sacred = []
    self.seen_undead = []
    for l in self.seen_units[-4:]:
      for uni in l:
        if animal_t in uni.traits: self.seen_animal.append(uni)
        if uni.can_fly: self.seen_fly.append(uni)
        if human_t in uni.traits: self.seen_human.append(uni)
        if mounted_t in uni.traits: self.seen_mounted.append(uni)
        if uni.rng >= 6: self.seen_ranged.append(uni)
        if sacred_t in uni.traits: self.seen_sacred.append(uni) 
        if undead_t in uni.traits: self.seen_undead.append(uni)
    
    self.seen_animal_rnk = sum(i.ranking for i in self.seen_animal)
    self.seen_fly_rnk = sum(i.ranking for i in self.seen_fly)
    self.seen_human_rnk = sum(i.ranking for i in self.seen_human)
    self.seen_mounted_rnk = sum(i.ranking for i in self.seen_mounted)
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

  def set_units_types(self):
    units = [i for i in self.units if i.leader == None and i.group == [] 
             and i.comm == 0]
    self.units_animal = []
    self.units_fly = []
    self.units_human = []
    self.units_mounted = []
    self.units_piercing = []
    self.units_ranged = []
    self.units_sacred = []
    self.units_undead = []
    for i in units:
      if animal_t in i.traits: self.units_animal.append(i)
      if i.can_fly: self.units_fly.append(i)
      if human_t in i.traits: self.units_human.append(i)
      if mounted_t in i.traits: self.units_mounted.append(i)
      if i.pn: self.units_piercing.append(i) 
      if i.rng >= 6: self.units_ranged.append(i)
      if i.damage_sacred + i.damage_sacred_mod: self.units_sacred.append(i)
      if undead_t in i.traits: self.units_undead.append(i)  
    
    self.units_animal_rnk = sum(i.ranking for i in self.units_animal)
    self.units_fly_rnk = sum(i.ranking for i in self.units_fly)
    self.units_human_rnk = sum(i.ranking for i in self.units_human)
    self.units_mounted_rnk = sum(i.ranking for i in self.units_mounted)
    self.units_piercing_rnk = sum(i.ranking for i in self.units_piercing)
    self.units_ranged_rnk = sum(i.ranking for i in self.units_ranged)
    self.units_sacred_rnk = sum(i.ranking for i in self.units_sacred)
    self.units_undead_rnk = sum(i.ranking for i in self.units_undead)
    
  def set_train_type(self, units):
    self.set_seen_units(0, info = 1)
    self.set_units_types()
    shuffle(units)
    if roll_dice(1) >= 3:
      logging.debug(f'sort by nation traits.')
      units.sort(key = lambda x: any(i in x.traits for i in self.nation.traits), reverse = True)
    [i.update() for i in units]
    logging.debug(f'recividos {len(units)}.')
    _animal = [i for i in units if animal_t in i.traits]
    _anticav = [i for i in units if i.anticav]
    _archers = [i for i in units if i.rng + i.rng_mod > 5]
    _fly = [i for i in units if i.can_fly]
    _mounted = [i for i in units if mounted_t in i.traits]
    _sacred = [i for i in units if sacred_t in i.traits]
    _undead = [i for i in units if undead_t in i.traits]
    if self.defense_total_percent < 200 and self.nation.score < self.nation.attack_factor * 3:
      logging.debug(f'defensivo.')
      units.sort(key = lambda x: x.ranking, reverse = True)
      if roll_dice(1) >= 3: units.sort(key = lambda x: x.rng + x.rng_mod, reverse = True)
      if self.around_threat >= self.defense / 2: units.sort(key = lambda x: x.resource_cost <= self.resource_total, reverse = True)
      return units
    
    if self.seen_ranged_rnk > (self.units_ranged_rnk + self.units_fly_rnk) * 0.5:
      logging.debug(f'contra ranged.')
      _units = [i for i in units if i.rng + i.rng_mod >= 5
                or i.armor
                or i.shield] 
      _units.sort(key = lambda x: x.rng + x.rng_mod, reverse = True)
      if roll_dice(1) >= 5: _units.sort(key = lambda x: x.ranking, reverse = True)
      if _units: return _units
    if self.seen_mounted_rnk > self.units_piercing_rnk + self.units_mounted_rnk:
      logging.debug(f'pn.')
      _units = [i for i in units if i.pn
                or mounted_t in i.traits]
      if roll_dice(1) >= 3: _units.sort(key = lambda x: x.ranking, reverse = True)
      if _units: return _units
    if self.seen_undead_rnk > self.units_sacred_rnk // 2:
      logging.debug(f'sacred.')
      _units = [i for i in units if i.damage_sacred + i.damage_sacred_mod]
      if roll_dice(1) >= 3: _units.sort(key = lambda x: x.ranking, reverse = True)
      if _units: return _units
    if self.seen_sacred_rnk * 1.5 > self.units_undead_rnk:
      logging.debug(f'human')
      units.sort(key = lambda x: any(i in x.traits for i in [human_t]), reverse = True)
      return units
    logging.debug(f'av anticav {len(_anticav)}.')
    logging.debug(f'total rnk {self.units_piercing_rnk*100//self.defense_total}.')
    logging.debug(f'limit {self.nation.units_piercing_limit}.')
    if (_anticav and roll_dice(1) >= 3 
        and self.units_piercing_rnk * 100 // self.defense_total < self.nation.units_piercing_limit):
      logging.debug(f'piercing.')
      if roll_dice(1) >= 3: _anticav.sort(key = lambda x: x.ranking, reverse = True)
      if _anticav: return _anticav
    logging.debug(f'av sacred {len(_sacred)}.')
    logging.debug(f'total rnk {self.units_sacred_rnk*100//self.defense_total}.')
    logging.debug(f'limit {self.nation.units_sacred_limit}.')
    if (_sacred and roll_dice(1) >= 3 
        and self.units_sacred_rnk * 100 // self.defense_total < self.nation.units_sacred_limit):
      logging.debug(f'sacred.')
      if roll_dice(1) >= 3: _sacred.sort(key = lambda x: x.ranking, reverse = True)
      if _sacred: return _sacred
    
    if self.pos.around_forest + self.pos.around_hill >= 3 and roll_dice(1) >= 5:
      _units = [i for i in units if i.can_fly or i.forest_survival or i.mountain_survival]
      logging.debug(f'forest and hills.')
      _units.sort(key = lambda x: x.rng >= 6, reverse = True)
      if _units: return _units
    logging.debug(f'av archers {len(_archers)}.')
    logging.debug(f'total rnk {self.units_ranged_rnk*100//self.defense_total}')
    logging.debug(f'limit {self.nation.units_ranged_limit}.')
    if (_archers and roll_dice(1) >= 3 
        and self.units_ranged_rnk * 100 // self.defense_total < self.nation.units_ranged_limit):
      logging.debug(f'ranged.')
      if roll_dice(1) >= 2: _archers.sort(key = lambda x: x.ranking, reverse = True)
      _archers.sort(key = lambda x: x.rng >= 6, reverse = True)
      if _archers: return _archers
    logging.debug(f'av mounted {len(_mounted)}.')
    logging.debug(f'total rnk {self.units_mounted_rnk*100/self.defense_total}.')
    logging.debug(f'limit {self.nation.units_mounted_limit}.')
    if (_mounted and roll_dice(1) >= 4
        and self.units_mounted_rnk * 100 / self.defense_total < self.nation.units_mounted_limit):
      logging.debug(f'mounted.')
      _units = [i for i in units if mounted_t in i.traits]
      if _units: return _units
    
    if self.defense_total_percent > 200:
      logging.debug(f'expensive.')
      _units = [i for i in units if levy_t not in i.traits]
      if _units: units = _units
      units.sort(key = lambda x: x.ranking, reverse = True)
      units = [i for i in units[:3]]
      
      shuffle(units)
      return units    
    
    return units

  def status(self, info = 0):
    logging.info(f'city status {self}.')
    self.defensive_tiles = self.get_tiles_defense(self.tiles)
    self.defensive_tiles.sort(key = lambda x: x.hill, reverse = True)
    self.for_food_tiles = self.get_tiles_food(self.tiles)
    self.for_food_tiles = [i for i in self.for_food_tiles if i.size >= 4]
    self.for_food_tiles.sort(key = lambda x: x.food, reverse = True)
    self.for_res_tiles = self.get_tiles_res(self.tiles)
    self.for_res_tiles = [i for i in self.for_res_tiles if i.size >= 4]
    self.for_res_tiles.sort(key = lambda x: x.resource, reverse = True)
    
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
    
    self.get_threats()
    self.food_val = round(self.food_total - self.food_need)
    self.food_probable = self.food_val
    for b in self.buildings:
      if b.is_complete == 0:
        self.food_probable += b.food * b.pos.food / 100 
    self.food_probable = round(self.food_probable)
    
    self.get_popdef()
    self.set_defense()
    self.get_defense_info()
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
      logging.debug(f'nivel de defensa {self.defense} de {self.defense_pred}, ({self.defense_percent}%).')
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
        if bu.type == building_t:bu.update()
        bu.poss = t
        self.buildings.append(bu)
      for uni in t.units: 
        if uni.nation == self.nation: self.units.append(uni)
    
    self.buildings.sort(key = lambda x: x.resource_cost[0])
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
      if t.blocked == 0: self.income_total += t.income
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
    pop = unit.units * 3
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
        t.city = itm
        t.nation = self
        itm.tiles.append(t)
    msg = f'{hamlet_t} {itm.nick} se establece en {itm.pos} {itm.pos.cords}.'
    logging.info(msg)
    self.log[-1].append(msg)
    itm.add_pop(itm.pop)
    [t.update(itm.nation) for t in itm.tiles]
    itm.update()
    itm.status()
    self.update(scenary)
    logging.debug(f'{itm.nation} ahora tiene {len(itm.nation.cities)} ciudades.')
  
  def build(self, city):
    if self.income < self.upkeep:
      logging.debug(f'not enogh gold.')
      return
    city.status()
    # Build food buildings.
    logging.debug(f'build food.')
    shuffle(city.tiles)
    city.tiles.sort(key = lambda x: x.is_city, reverse = True)
    buildings = [b for b in self.av_buildings if food_t in b.tags and b.gold < self.gold]
    count = 1
    po_factor = 50
    if city.buildings_food_complete == []: 
      count = randint(3, 6)
      po_factor = 100
    for b in buildings:
      city.tiles.sort(key = lambda x: x.po)
      for t in city.tiles:
        t.update(self)
        if t.around_threat or t.threat: continue
        if t.po > po_factor:
          logging.debug(f'tu much po. {t.po=:}, {po_factor=:}.') 
          continue
        building = b(self, t)
        if building.can_build():
          city.add_building(building, t)
          logging.debug(f'{building} added at {t} {t.cords}.')
          count -= 1
          if count < 1: break
    
    # build military buildings.
    city.status()
    if city.buildings_food:
      logging.debug(f'build military.')
      buildings = [b for b in self.av_buildings if military_t in b.tags and b.gold < self.gold]
      buildings.sort(key = lambda x: x(self, self.pos).resource_cost[1])
      if roll_dice(1) >= 5: shuffle(buildings)
      count = 1
      for b in buildings:
        if count == 0: break
        city.tiles.sort(key = lambda x: len(x.around_snations), reverse = True)
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
    if city.buildings_food:
      logging.debug(f'build misc.')
      buildings = [b for b in self.av_buildings if any(i in b.tags for i in [unrest_t, resource_t]) and b.gold < self.gold]
      cost_mean = sum([b.gold for b in buildings])
      completed = len(city.buildings_res_complete)
      if completed == 0: completed = 1
      shuffle(buildings)
      count = 1
      if len(city.buildings_res_complete) > len(city.tiles) // 5: count = 0
      if self.gold > cost_mean * completed: count = 1
      for b in buildings:
        if count == 0: break
        if unrest_t in b.tags: city.tiles.sort(key = lambda x: x.po)
        if resource_t in b.tags: 
          if roll_dice(1) >= 4:
            logging.debug(f'roll set to not build.')
            continue
          city.tiles.sort(key = lambda x: x.hill, reverse = True)

        for t in city.tiles:
          t.update(self)
          if t.around_threat or t.threat: continue
          if unrest_t in b.tags and t.po > 20: continue
          building = b(self, t)
          if building.can_build():
            city.add_building(building, t)
            logging.debug(f'{building} added at {t} {t.cords}.')
            count = 0
            break
    
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
      count = 1
      if b.pos.food < b.pos.pop or b.pos.po >= 10:
        logging.debug(f'food not need.')
        count = 0
      if city.nation.gold - factor >= factor:
        logging.debug(f'factor True.')
        count = 1
      
      if count == 0: continue
      upg = choice(b.upgrade)(self, self.pos)
      
      if upg.gold < self.gold:
        b.improve(upg)

  def improve_military(self, city):
    logging.info(f'build_military_upgrade.')
    # military upgrades.
    buildings = [b for b in city.buildings_military_complete if b.upgrade]
    logging.debug(f'upgradables {len(buildings)=:}.')
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
      upg = choice(b.upgrades)(self, self.pos)
      
      if upg.gold < self.gold:
        b.improve(upg)

  def check_events(self):
    pass

  def get_groups(self):
    self.update(self.map)
    self.groups = [i for i in self.units if i.goal and i.hp_total > 0]
    self.groups_free = [i for i in self.groups if i.mp[0] == i.mp[1]
                        and i.goto == []]

  def get_free_units(self):
    self.units_free = [it for it in self.units if it.garrison == 0 
           and it.scout == 0 and it.settler == 0 
           and it.goto == [] and it.group == []
           and it.leader == None and it.goal == None
           and it.comm == 0 and it.mp[0] > 0]
    
    return self.units_free

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

  def set_income(self):
    [ct.income_change() for ct in self.cities]
    self.gold += self.raid_income
    logging.debug(f'gana {self.raid_income} por saqueos.')
    self.raid_income = 0

  def set_seen_nations(self, info = 0):
    for nt in self.seen_nations:
      nt.seen_tiles = [t for t in nt.seen_tiles if str(t.nation) == str(nt)]
    self.seen_nations = [nt for nt in self.seen_nations if nt.seen_tiles]
    for t in self.map:
      if t.sight == 0: continue
      t.update(self)
      if (t.nation != None and str(t.nation) != str(self) 
          and str(t.nation) not in self.str_nations and t.sight):
        nt = t.nation.__class__()
        self.str_nations.append(str(t.nation))
        self.seen_nations.append(nt)
        logging.debug(f'{nt} descubierta.')
        sleep(loadsound('notify1') / 2)
        
    for nt in self.seen_nations:
      nt.seen_units = []
      seen_score = 0
      for t in self.map:
        if t.sight == 0: continue
        if str(t.nation) == str(nt): 
          if t not in nt.seen_tiles: nt.seen_tiles.append(t)
        for uni in t.units:
          if str(uni.nation) == str(nt) and uni.hidden == 0: 
            seen_score += uni.ranking
            nt.seen_units.append(uni)
      
      nt.seen_score.insert(0, seen_score)
      nt.max_score = max(nt.seen_score[:5])
      nt.mean_score = mean(nt.seen_score[:10])
      nt.last_score = seen_score
    
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

  def set_new_city_req(self):
    cities = len([i for i in self.cities])
    self.city_req_pop = self.city_req_pop_base * (cities)
  
  def status(self, info = 0):
    self.defense_need = 0
    self.income = sum(i.income_total for i in self.cities)
    self.pop_military = 0
    self.pop = 0
    self.pop_total = 0
    for ct in self.cities:
      ct.get_popdef()
      ct.set_defense()
      ct.get_defense_info()
      self.defense_need += ct.defense_need
      if ct.defense < ct.defense_total: self.defense_need -= ct.defense_total / 2
      self.pop += ct.pop
      
      for uni in self.units: 
        self.pop_military += uni.pop
    
      self.pop_total = self.pop_military + self.pop
      self.military_percent = round(self.pop_military * 100 / self.pop_total)
      self.pop_percent = round(self.pop * 100 / self.pop_total)
      self.upkeep_percent = round(self.upkeep * 100 / self.income, 1)
      
      if info:
        logging.debug(f'estado de {self}.')
        logging.debug(f'necesita {self.defense_need} defensa.')
        logging.debug(f'civiles: {self.pop}, ({self.pop_percent}%).')
        logging.debug(f'militares: {self.pop_military} ({self.military_percent}%).')
        logging.debug(f'población total {self.pop_total}.')
        logging.debug(f'ingresos {self.income}.')
        logging.debug(f'gastos {self.upkeep}., ({self.upkeep_percent}%).')
      
      if self.cities: 
        self.defense_mean = int(mean([i.defense_total_percent for i in self.cities]))

  def update(self, scenary):
    if self.cities: self.pos = self.cities[0].pos
    else: self.pos = None
    self.buildings = []
    self.cities = []
    self.score = 0
    self.tiles = [t for t in scenary if t.nation == self]
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
        if uni.nation == self: 
          self.units.append(uni)
          if animal_t in uni.traits: self.units_animal.append(uni)
          if uni.can_fly: self.units_fly.append(uni)
          if human_t in uni.traits: self.units_human.append(uni)
          if uni.rng < 6: self.units_melee.append(uni)
          if mounted_t in uni.traits: self.units_mounted.append(uni)
          if uni.pn: self.units_piercing.append(uni) 
          if uni.rng >= 6: self.units_ranged.append(uni)
          if sacred_t in uni.traits: self.units_sacred.append(uni)
          if undead_t in uni.traits: self.units_undead.append(uni)
    
    self.production = []
    for c in self.cities: 
      for p in c.production:
        self.production.append(p) 
    self.units_comm = [it for it in self.units if it.comm]
    self.units_scout = [i for i in self.units if i.scout]
    self.upkeep += sum(b.upkeep for b in self.buildings if b.is_complete)
    self.upkeep += sum(b.upkeep for b in self.cities)
    for i in self.units:
      i.update()
      self.score += i.ranking
      self.upkeep += i.upkeep_total
      i.show_info = self.show_info
    
    self.income = round(self.income)
    self.raid_outcome = sum(ct.raid_outcome for ct in self.cities)
    self.score = round(self.score)
    self.upkeep = round(self.upkeep)
    [it.update() for it in self.cities]
    self.defense_pred = sum(it.defense_pred for it in self.cities)
    self.defense_total = sum(it.defense_total for it in self.cities)
    self.upkeep_limit = self.upkeep_base
    self.status()
    self.upkeep_limit += round(self.pop / self.upkeep_change)
    if self.upkeep_limit > 100: self.upkeep_limit = 100
    self.upkeep_limit = round(self.upkeep_limit * self.income // 100)
    self.cities.sort(key = lambda x: x.capital, reverse = True)
    self.set_new_city_req()
    self.units.sort(key = lambda x: len(x.group))
    # expanding.
    self.expanding = 0
    if any(i for i in [ct.expanding for ct in self.cities]): self.expanding = 1


class Unit:
  name = str()
  nick = str()
  units = 0
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
  mp = []
  moves = 0
  resolve = 0
  po = 0
  global_skills = []

  dfs = 0
  res = 0
  arm = 0
  armor = None
  shield = None
  defensive_skills = []

  att = 0
  damage = 0
  rng = 1
  mrng = 0
  off = 0
  str = 0
  pn = 0
  offensive_skills = []
  spells = []
  other_skills = [] 
  
  power = 0
  power_max = 0
  power_res = 0
  unique = 0

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
  auto_attack = 0
  auto_explore = 0
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
  can_siege = 0
  city = None
  desert_survival = 0
  dist = 0
  fled = 0
  fear = 4
  food = 0
  forest_survival = 0
  garrison = 0
  goal = None
  going = 0
  gold = 0
  group_score = 0
  group_base = 0
  hidden = 0
  leader = None
  level = 0
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
  squads = 1
  stopped = 0
  swamp_survival = 0
  units_min = 0
  units_max = 50
  to_avoid = 0

  def __init__(self, nation):
    self.hp_total = self.hp * self.units
    self.history = Empty()
    self.history.turns = 1
    self.initial_units = self.units
    self.nation = nation
    self.defensive_skills = [i(self) for i in self.defensive_skills]
    self.global_skills = [i(self) for i in self.global_skills]
    self.offensive_skills = [i(self) for i in self.offensive_skills]
    self.other_skills = [i for i in self.other_skills]
    self.spells = [i(self) for i in self.spells]
    self.traits = [i for i in self.traits]
    self.terrain_skills = [i(self) for i in self.terrain_skills]
    self.mp = [i for i in self.mp]
    
    self.battle_log = []
    self.buildings = []
    self.corpses = [Skeletons]
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
    
  def __str__(self):
    if self.nick: name = f'{self.nick}. '
    else: name = ''
    if self.units > 1: name += f'{self.units}'
    name += f' {self.name}'
    
    # if self.show_info == 0: name += f' id {self.id}.'
    return name

  def autokill(self):
    if self.pos.get_nearest_nation() > 3 and self in self.pos.world.units:
      self.hp_total = 0
      loadsound('set9')

  def break_group(self):
    logging.debug(f'{self} rompe grupo.')
    self.group_base = 0
    self.group_score = 0
    for i in self.group: 
      i.leader = None
      i.goto = []
    self.goal = None
    self.goto = []
    self.group = []

  def burn(self, cost = 0):
    if (self.pos.buildings
        and self.mp[0] >= cost and self.can_burn and self.pos.nation != self.nation): 
      if [i for i in self.pos.units
          if i.nation == self.pos.nation]:
        return
      self.pos.update(self.pos.nation)
      
      building = choice(self.pos.buildings)
      self.update()
      damage = self.damage * self.att
      damage *= self.units
      building.resource_cost[0] -= damage
      self.pos.burned = 1
      msg = f'{self} {burn_t} {building}. {in_t} {self.pos.city} {self.pos.cords}'
      self.log[-1].append(msg)
      self.nation.log[-1].append(msg)
      self.pos.nation.log[-1].append(msg)
      logging.debug(msg)
      if building.resource_cost[0] < 1:
        msg = f'{building} {has_been_destroyed_t} {in_t} {self.pos.cords}.'
        self.log[-1].append(msg)
        self.nation.log[-1].append(msg)
        self.pos.nation.log[-1].append(msg)
        logging.debug(msg)
      if any(i for i in [self.nation.show_info, self.pos.nation.show_info]): 
        sleep(loadsound('build_burn01', channel = ch3) * 0.5)

  def can_pass(self, pos):
    if pos.soil.name in self.soil and pos.surf.name in self.surf: return True

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

  def combat_retreat(self, info = 0):
    if info: logging.debug(f' combat retreat.')
    self.update()
    if info: logging.debug(f'{self} retreat units {self.units} hp {self.hp_total}.')
    if death_t in self.traits:
      logging.debug(f'{death_t}.')
      return
    dead = sum(self.deads)
    if info: logging.info(f'{self} loses {dead}.')
    
    roll = roll_dice(1)
    if info: logging.debug(f'dado {roll}.')
    roll += dead
    if info: logging.debug(f'dado {roll}.')
    resolve = self.resolve + self.resolve_mod
    if info: logging.debug(f'{self} resolve {resolve}.')
    if dead and roll > resolve:
      retreat = roll - resolve
      if retreat > self.units: retreat = self.units
      self.hp_total -= retreat * self.hp 
      self.fled[-1] += retreat
      if info: logging.warning(f'{self} huyen {retreat} unidades.')
      self.update()
      if info: logging.debug(f'total huídos {self.fled}.')

  def create_group(self, score, same_mp = 0):
    if score < 0: return
    logging.debug(f'{self} crea grupo de {score}')
    self.group_base = score
    self.group_score = self.group_base
    for i in self.group:
      if i.pos == self.pos or self.pos in i.goto_pos: 
        self.group_score -= i.ranking
    units = self.nation.get_free_units()
    if same_mp: units = [i for i in units if i.mp[1] >= self.mp[1]] 
    shuffle(units)
    if self.rng <= 6:
      units.sort(key = lambda x: x.pos.get_distance(self.pos, x.pos))
      units.sort(key = lambda x: x.rng >= 6, reverse = True)
    elif self.rng >= 6:
      units.sort(key = lambda x: x.pos.get_distance(self.pos, x.pos))
      units.sort(key = lambda x: x.off, reverse = True)
    if self.settler:
      units.sort(key = lambda x: x.pos.get_distance(self.pos, x.pos))
      units.sort(key = lambda x: x.mp[1] == self.mp[1], reverse = True)
      units.sort(key = lambda x: x.ranking, reverse = True)
    
    logging.debug(f'disponibles {len(units)}.')
    if len(units) == 0:
      logging.debug(f'no puede crear grupo')
      return
    
    for i in units:
      if i == self: continue
      logging.debug(f'score {self.group_score}.')
      logging.debug(f'encuentra a {i}')
      if self.group_score > 0 and i not in self.group and i != self:
        self.group.append(i)
        i.leader = self
        logging.debug(f'{i} se une con {i.ranking} ranking.')
        self.group_score -= i.ranking
        logging.debug(f'quedan {self.group_score}.')
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

  def get_skills(self, info = 1):
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
    tile_skills = []
    if self.pos:
      if self.attacking == 0: tile_skills += [sk for sk in self.pos.terrain_events + self.pos.events + self.pos.skills]
      elif self.attacking: tile_skills += [sk for sk in self.target.pos.terrain_events + self.pos.events]
    if info: print(f'{len(tile_skills)} de casillas.')
    for i in tile_skills:
      if i.type == 'generic':
        if info: print(f'{i} added.')
        skills.append(i)
        if info: print(f'se agrega {i.name}')
    
    if self.target: skills += [s for s in self.target.skills if s.effect == 'enemy']    
    if info: print(f'run')
    for sk in skills:
      if sk.type == 'generic':
        if info: print(sk.name)
        sk.run(self)
    
    self.skill_names.sort()

  def launch_event(self):
    pass

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

  def raid(self, cost = 0):
    if (self.pos.city and self.pos.nation != self.nation and self.can_raid 
        and self.mp[0] >= cost):  
      self.mp[0] -= cost
      self.update()
      self.pos.update()
      if self.pos.raided < self.pos.income:
        logging.info(f'{self} saquea a {self.pos.city} {self.pos.nation} en {self.pos} {self.pos.cords}')
        raided = self.hp_total * 2
        if mounted_t in self.traits: raided *= 2
        raided *= (self.moves + self.moves_mod) / 2
        if raided > self.pos.income: raided = self.pos.income
        self.pos.raided = raided
        self.pos.city.raid_outcome += raided
        self.nation.raid_income += raided
        msg = f'{self} {raid_t} {raided} {gold_t} {in_t} {self.pos} {self.pos.cords}, {self.pos.city}.'
        self.pos.nation.log[-1].append(msg)
        self.log[-1].append(msg)
        self.nation.log[-1].append(msg)
        if any(i for i in [self.pos.nation.show_info, self.show_info]) and raided: 
          sleep(loadsound('gold2', channel = ch3))
      if self.pos.pop:
        logging.debug(f'{self.pop=:}.')
        pop = self.pos.pop
        dead = (self.damage + self.damage_mod) * randint(1, self.units)
        logging.debug(f'initial dead {dead}.')
        dead *= randint(1, self.att + self.att_mod + 1)
        if mounted_t in self.traits: dead *= 2 
        logging.debug(f'second dead {dead}.')
        defense = sum([i.units for i in self.pos.units if i.nation == self.pos.nation])
        if defense: dead -= randint(int(defense * 0.1), int(defense * 0.3))
        logging.debug(f'end dead {dead}.')
        if dead < 0: dead = 0
        if dead > pop: dead = pop
        self.pos.pop -= dead
        if self.pos.pop: self.pos.unrest += randint(dead, dead * 2)
        if dead >= 50 * pop / 100:
          msg = f'masacre!.'
          self.log[-1].append(msg)
          self.nation.log[-1].append(msg)
          self.pos.nation.log[-1].append(msg)
          sq = self.pos.get_near_tiles(1)
          sq = [s for s in sq if s.nation == self.pos.nation]
          for s in sq: s.unrest += randint(15, 30)
          if any(i for i in [self.pos.nation.show_info, self.show_info]): 
            sleep(loadsound('spell36', channel = ch3) * 0.2)
        if dead:
          msg = f'{dead} población perdida.'
          self.pos.nation.log[-1].append(msg)
          self.log[-1].append(msg)
          self.nation.log[-1].append(msg)
          if any(i for i in [self.show_info, self.pos.nation.show_info]): 
            sleep(loadsound('notify23') * 0.5)
      logging.info(f'raid_income {round(self.pos.nation.raid_income)}.')      
      self.pos.city.update()

  def set_attack(self, enemies):
    if self.mp[0] < 0: return
    logging.debug(f'ataque hidden.')
    enemies = [i for i in enemies
               if i.nation != self.nation and i.hidden == 0]
    if enemies:
      weakest = roll_dice(1)
      if self.hidden: 
        weakest += 2
      if weakest >= 5: enemies.sort(key = lambda x: x.ranking)
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

  def set_hidden(self, pos, info = 1):
    if info: logging.info(f'set hidden {self} a {pos} {pos.cords}.')
    visible = self.units
    if info: logging.debug(f'visible {visible}')
    if self.nation != pos.nation: 
      visible += pos.pop
      if info: logging.debug(f'visible {visible} pop')
    visible += sum([it.units for it in pos.units if it.nation != self.nation])
    if info: logging.debug(f'visible {visible} units')
    visible = floor(visible / 300)
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
    self.revealed_val = stealth 

  def set_id(self):
    num = self.id
    # logging.debug(f'id base {self} {num}.')
    self.nation.units.sort(key = lambda x: x.id)
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
    self.ranking_off += self.damage + self.damage_mod
    self.ranking_off_l += ['damage', self.ranking_off]
    self.ranking_off += self.damage_sacred + self.damage_sacred_mod
    self.ranking_off_l += ['sacred', self.ranking_off]
    self.ranking_off *= self.att + self.att_mod
    self.ranking_off_l += ['att', self.ranking_off]
    self.ranking_off *= self.units
    self.ranking_off_l += ['units', self.ranking_off]
    self.ranking_off += (self.damage_charge + self.damage_charge_mod) * 10
    self.ranking_off_l += ['charge', self.ranking_off]
    self.ranking_off *= 1 + (self.off + self.off_mod) / 10
    self.ranking_off_l += ['off', self.ranking_off]
    self.ranking_off *= 1 + (self.str + self.str_mod) / 10
    self.ranking_off_l += ['str', self.ranking_off]
    self.ranking_off += (self.pn + self.pn_mod) * 5
    self.ranking_off_l += ['pn', self.ranking_off]
    self.ranking_off *= 1 + ((self.moves + self.moves_mod) / 2) / 10
    self.ranking_off_l += ['moves', self.ranking_off]
  
    self.ranking_dfs = self.hp_total
    self.ranking_dfs_l = ['hp', self.ranking_dfs]
    self.ranking_dfs *= 1 + (self.dfs + self.dfs_mod) / 10
    self.ranking_dfs_l += ['dfs', self.ranking_dfs]
    self.ranking_dfs *= 1 + (self.res + self.res_mod) / 10
    self.ranking_dfs_l += ['res', self.ranking_dfs]
    self.ranking_dfs *= 1 + (self.arm + self.arm_mod) / 5
    self.ranking_dfs_l += ['arm', self.ranking_dfs]
    if self.armor: 
      self.ranking_dfs *= 1 + (self.armor.arm) / 10 * 5
      self.ranking_dfs_l += ['armor', self.ranking_dfs]
    if self.shield: 
      self.ranking_dfs += 1 + (self.shield.dfs) / 10
      self.ranking_dfs_l += ['shield', self.ranking_dfs]
    self.ranking = self.ranking_dfs + self.ranking_off
    self.ranking += (self.rng + self.rng_mod) * 5
  
    self.ranking = round(self.ranking / 4)
    if self.can_fly: self.ranking *= 1.2
    if self.resolve + self.resolve_mod >= 6: self.ranking *= 1.3
    if self.resolve + self.resolve_mod < 6: self.ranking *= 0.7
    self.ranking += sum(s.ranking for s in self.skills + self.spells)

  def set_tile_attr(self, info = 0):
    tiles = self.pos.get_near_tiles(1)
    tiles = [t for t in tiles if t.nation 
           and t.nation != self.nation and t.pop]
    if info and tiles: print(f'set_tile_attr {self} en {self.pos} {self.pos.cords}')
    for t in tiles:
      t.update(self.nation)
      unrest = self.ranking * 0.1
      if info: print(f'unrest {unrest}')
      if t == self.pos: unrest *= 2
      if info: print(f'diferente que. unrest {unrest}')
      if info: print(f'unrest final {unrest}')
      if unrest < 0: unrest = 0
      t.unrest += unrest

  def split(self, times = 1):
    if self.squads <= 1: return
    logging.info(f'divide {self}.')
    for i in range(times):
      self.update()
      logging.debug(f'{self} hp {self.hp_total} units {self.units} mínimo {self.initial_units}.')
      if self.units <= self.initial_units:
        logging.debug(f'mínimo alcansado.')
        return
  
      unit = self.__class__(self.nation)
      self.hp_total -= self.initial_units * self.hp
      self.pop -= unit.pop
      unit.city = self.city
      unit.day_night = self.day_night
      unit.garrison = self.garrison
      unit.pos = self.pos
      unit.revealed = self.revealed
      unit.global_skills = self.global_skills
      unit.offensive_skills = self.offensive_skills
      unit.other_skills = self.other_skills
      unit.log = [[f'{turn_t} {self.pos.world.turn}.']]
      msg = f'{unit} detached from {self}.'
      unit.log[-1] += [msg]
      self.log[-1] += [msg]
      self.update()
      self.pos.units.append(unit)
      if self.show_info: sp.speak(f'{self}.')

  def start_turn(self):
    self.burn()
    self.raid()

  def update(self):
    self.day_night = self.ambient.day_night
    self.month = self.ambient.month[0]
    self.season = self.ambient.season[0]
    self.time = self.ambient.time[0]
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
    self.squads = ceil(self.units / self.initial_units)
    
    # ranking.
    self.skills = [i for i in self.global_skills + self.terrain_skills + 
                   self.defensive_skills + self.offensive_skills + self.other_skills]
    self.get_skills()
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
  events = [Unrest]
  food = 2
  public_order = 20
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
    self.food += 1
    self.income += 1.5
    self.public_order += 50
    self.upkeep = 0

  def set_downgrade(self):
    msg = ''
    if self.level == 1 and self.pop <= 1500:
      msg = f'{self} se degrada a {hamlet_t}.'
      self.level = 0
      self.name = hamlet_t
      self.food -= 2
      self.grouth -= 1
      self.income -= 1.5
      self.public_order -= 50
    if self.level == 2 and self.pop <= 2400:
      msg = f'{self} se degrada a {village_t}.'
      self.level = 1
      self.name = village_t
      self.food -= 2
      self.grouth -= 1
      self.income -= 1.5
      self.public_order -= 50
    if self.level == 3 and self.pop <= 7000:
      msg = f'{self} se degrada a {town_t}.'
      self.level = 1
      self.name = town_t
      self.food -= 2
      self.grouth -= 1
      self.income -= 1.5
      self.public_order -= 50
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
      self.grouth += 1
      self.income += 1.5
      self.public_order += 50
    if self.level == 1 and self.pop >= 8000:
      msg = f'{self} mejor a {town_t}.'
      self.level = 2
      self.name = town_t
      self.food += 1.5
      self.grouth += 1
      self.income += 1.5
      self.public_order += 50
    if self.level == 2 and self.pop >= 20000:
      msg = f'{self} mejor a {city_t}.'
      self.level = 3
      self.name = city_t
      self.food += 2
      self.grouth += 1
      self.income += 1.5
      self.public_order += 50
    if msg:
      logging.debug(msg)
      if self.nation.show_info:
        sp.speak(msg, 1)
        sleep(loadsound('notify14'))


class GlisteningPastures(Building):
  name = 'Pasturas radiantes'
  gold = 20000
  food = 100
  income = 1.2

  own_terrain = 1
  size = 6
  tags = [military_t]
  unique = 1

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [WildHuntsmen]
    self.resource_cost = [0, 160]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t]
    self.hill = [0, 1]
    self.upgrade = [WindsStables]


class WindsStables(GlisteningPastures, Building):
  name = 'Establos del viento'
  base = GlisteningPastures
  gold = 30000
  income = 1.5

  own_terrain = 1
  tags = [military_t]
  unique = 1

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [ForestRider]
    self.resource_cost = [0, 120]
    self.size = 0


class FalconRefuge(Building):
  name = 'refugio del alcón'
  gold = 7000
  own_terrain = 1
  unique = 1
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Falcons, SilvanArcher]
    self.resource_cost = [0, 80]
    self.size = 0
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t]
    self.hill = [0, 1]
    self.upgrade = []


class ForestLookout(FalconRefuge, Building):
  name = 'Observatorio forestal'
  base = FalconRefuge
  unique = 1
  gold = 15000

  own_terrain = 1
  size = 4
  tags = [military_t]
  unique = 1

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [ForestEagle, HighSilvanArcher]
    self.resource_cost = [0, 80]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t]
    self.hill = [0, 1]
    self.upgrade = [FalconRefuge]


class Sanctuary(Building):
  name = 'santuario'
  gold = 15000
  food = 2
  income = 1.5
  unique = 1

  own_terrain = 1
  size = 6
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [BladeDancers]
    self.resource_cost = [0, 80]
    self.surf = [forest_t]
    self.hill = [0]
    self.upgrade = [HauntedForest]


class HauntedForest(Sanctuary, Building):
  name = 'Bosque embrujado'
  base = Sanctuary
  gold = 25000
  own_terrain = 1
  size = 5
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [EternalGuard, ForestBears]
    self.resource_cost = [0, 120]
    self.size = 0
    self.surf = [forest_t]
    self.hill = [0]
    self.upgrade = [MoonsFountain]


class MoonsFountain(HauntedForest, Building):
  name = 'Fuente de la luna'
  base = Sanctuary
  gold = 40000
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [AwakenTree, Driad]
    self.resource_cost = [0, 150]
    self.size = 0
    self.upgrade = []


class Grove(Building):
  name = 'Huerto'
  gold = 2000
  food = 1.5

  own_terrain = 1
  size = 6
  tags = [food_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 40]
    self.soil = [grassland_t, plains_t]
    self.surf = [forest_t, none_t]
    self.hill = [0]
    self.upgrade = [GrapeVines]


class GrapeVines(Grove, Building):
  name = 'racimos de uva'
  base = Grove
  gold = 7500
  food = 2.0
  income = 1.5
  own_terrain = 1
  tags = [food_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 80]
    self.size = 5
    self.soil = [grassland_t, plains_t]
    self.surf = [forest_t, none_t]
    self.hill = [0]
    self.upgrade = [Vineyard]


class Vineyard(GrapeVines, Building):
  name = 'Viñedo'
  base = GrapeVines
  gold = 14000
  food = 2.5
  income = 2
  own_terrain = 1
  tags = [food_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 150]
    self.size = 0
    self.soil = [grassland_t, plains_t]
    self.surf = [none_t]
    self.hill = [0]
    self.upgrade = []


class CraftmensTree(Building):
  name = 'Artesanos de los árboles'
  gold = 6000
  food = 1.2
  income = 2
  resource = 100
  own_terrain = 1
  size = 6
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
  gold = 10000
  food = 1.2
  income = 1.5
  resource = 2
  
  own_terrain = 1
  size = 6
  tags = [resource_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 120]
    self.soil = [grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [1]
    self.upgrade = []


# Unidades.
class AwakenTree(Elf):
  name = 'árbol despertado'
  units = 1
  type = 'infantry'
  traits = [elf_t, poisonres_t]
  gold = 1200
  upkeep = 140
  resource_cost = 40
  food = 4
  pop = 30
  terrain_skills = [ForestSurvival]

  hp = 10
  mp = [2, 2]
  moves = 5
  resolve = 8
  global_skills = [ForestWalker]

  dfs = 3
  res = 6
  arm = 4
  armor = None

  att = 3
  damage = 4
  rng = 5
  mrng = 20
  off = 6
  str = 7
  pn = 3
  offensive_skills = [ImpalingRoots]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Skeletons]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]


class BladeDancers(Elf):
  name = 'danzantes de la espada'
  units = 20
  type = 'infantry'
  traits = [elf_t]
  gold = 320
  upkeep = 20
  resource_cost = 24
  food = 3
  pop = 25
  terrain_skills = [Burn, ForestSurvival, Raid]

  hp = 2
  mp = [2, 2]
  moves = 7
  resolve = 8
  global_skills = [ForestWalker, Regroup]

  dfs = 5
  res = 2
  arm = 0
  armor = None

  att = 3
  damage = 2
  rng = 1
  off = 5
  str = 3
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Skeletons]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]


class Driad(Elf):
  name = 'driades'
  units = 5
  type = 'infantry'
  traits = [elf_t, poisonres_t]
  gold = 580
  upkeep = 45
  resource_cost = 30
  food = 3
  pop = 10
  terrain_skills = [Burn, ForestSurvival]

  hp = 2
  mp = [2, 2]
  moves = 7
  resolve = 8
  global_skills = [ForestWalker]

  dfs = 4
  res = 4
  arm = 1
  armor = HeavyArmor()

  att = 2
  damage = 2
  rng = 1
  off = 4
  str = 4
  pn = 1
  
  stealth = 8

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild


class EternalGuard(Elf):
  name = 'guardia eterna'
  units = 20
  type = 'infantry'
  traits = [elf_t]
  gold = 550
  upkeep = 25
  resource_cost = 25
  food = 4
  pop = 30
  terrain_skills = [Burn, ForestSurvival, Raid]

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 8
  global_skills = [ForestWalker, Refit, Regroup]

  dfs = 5
  res = 2
  arm = 0
  armor = HeavyArmor()

  att = 2
  damage = 2
  rng = 1
  off = 4
  str = 4
  pn = 1
  offensive_skills = [PikeSquare]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Skeletons]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]


class Falcons(Elf):
  name = 'Alcón'
  units = 2
  type = 'beast'
  traits = [animal_t]
  gold = 140
  upkeep = 20
  resource_cost = 18
  food = 3
  pop = 20
  terrain_skills = [ForestSurvival]

  hp = 1
  mp = [4, 4]
  moves = 10
  resolve = 6
  global_skills = [Fly, ForestWalker]

  dfs = 4
  res = 1
  arm = 0
  armor = None

  att = 3
  damage = 1
  rng = 1
  off = 4
  str = 4
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild


class ForestBears(Elf):
  name = 'Osos del bosque'
  units = 5
  type = 'beast'
  traits = [animal_t]
  gold = 400
  upkeep = 30
  resource_cost = 26
  food = 6
  pop = 20
  terrain_skills = [Burn, ForestSurvival]

  hp = 4
  mp = [2, 2]
  moves = 6
  resolve = 8
  global_skills = [ForestWalker]

  dfs = 5
  res = 6
  arm = 2
  armor = None

  att = 3
  damage = 2
  rng = 1
  off = 4
  str = 5
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Skeletons]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]


class ForestEagle(Elf):
  name = 'águila del bosque'
  units = 1
  type = 'beast'
  traits = [animal_t]
  gold = 300
  upkeep = 50
  resource_cost = 25
  food = 6
  pop = 10
  terrain_skills = [ForestSurvival]

  hp = 2
  mp = [3, 3]
  moves = 8
  resolve = 8
  global_skills = [Fly, ForestWalker]

  dfs = 5
  res = 2
  arm = 0
  armor = None

  att = 2
  damage = 2
  rng = 1
  off = 5
  str = 5
  pn = 1

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild


class ForestGuard(Elf):
  name = 'guardia forestal'
  units = 20
  type = 'infantry'
  traits = [elf_t]
  gold = 150
  upkeep = 8
  resource_cost = 14
  food = 2
  pop = 20
  terrain_skills = [Burn, ForestSurvival, Raid]

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 5
  global_skills = [ForestWalker]

  dfs = 3
  res = 2
  arm = 0
  armor = LightArmor()

  att = 2
  damage = 1
  rng = 1
  off = 3
  str = 3
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Skeletons]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]


class ForestRider(Elf):
  name = 'arquero silvano'
  units = 10
  type = 'cavalry'
  traits = [elf_t]
  gold = 850
  upkeep = 40
  resource_cost = 30
  food = 5
  pop = 30
  terrain_skills = [Burn, ForestSurvival, Raid]

  hp = 3
  mp = [4, 4]
  moves = 8
  resolve = 8
  global_skills = [ForestWalker, Refit, Regroup]

  dfs = 4
  res = 3
  arm = 1
  armor = HeavyArmor
  shield = Shield()

  att = 2
  damage = 2
  rng = 3
  off = 5
  str = 5
  pn = 1
  offensive_skills = [HeavyCharge]

  def __init__(self, nation):
    super().__init__(nation)
    self.traits += [mounted_t]
    self.align = Wild
    self.corpses = [Skeletons]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, none_t]


class ElvesSettler(Human):
  name = 'Silvan settler'
  units = 200
  type = 'civil'
  traits = [elf_t, settler_t]
  gold = 1500
  upkeep = 10
  resource_cost = 60
  food = 1
  pop = 700
  terrain_skills = [ForestSurvival]

  hp = 1
  mp = [2, 2]
  moves = 3
  resolve = 3

  dfs = 1
  res = 1
  arm = 0
  armor = None

  att = 1
  damage = 1
  rng = 1
  off = 1
  str = 1
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.buildings = [Hall]
    self.corpses = [Zombies]


class SilvanArcher(Elf):
  name = 'arquero silvano'
  units = 20
  type = 'infantry'
  traits = [elf_t]
  gold = 250
  upkeep = 12
  resource_cost = 20
  food = 2
  pop = 20
  terrain_skills = [Burn, ForestSurvival]

  hp = 2
  mp = [2, 2]
  moves = 7
  resolve = 6
  global_skills = [ForestWalker]

  dfs = 4
  res = 2
  arm = 0
  armor = None

  att = 2
  damage = 1
  rng = 15
  off = 4
  str = 3
  pn = 0
  offensive_skills = [Ambushment, Skirmisher]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Skeletons]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]


class HighSilvanArcher(Elf):
  name = 'alto arquero silvano'
  units = 15
  type = 'infantry'
  traits = [elf_t]
  gold = 450
  upkeep = 20
  resource_cost = 28
  food = 2
  pop = 30
  terrain_skills = [Burn, ForestSurvival, Raid]

  hp = 2
  mp = [2, 2]
  moves = 7
  resolve = 6
  global_skills = [ForestWalker, LongBow, Refit, Regroup]

  dfs = 4
  res = 2
  arm = 0
  armor = None

  att = 2
  damage = 2
  rng = 15
  off = 5
  str = 4
  pn = 1
  offensive_skills = [Ambushment, Skirmisher]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Skeletons]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]


class WildHuntsmen(Elf):
  name = 'Cazadores salvajes'
  units = 10
  type = 'cavalry'
  traits = [elf_t]
  gold = 650
  upkeep = 30
  resource_cost = 18
  food = 5
  pop = 30
  terrain_skills = [Burn, ForestSurvival, Raid]

  hp = 3
  mp = [3, 3]
  moves = 6
  resolve = 6
  global_skills = [ForestWalker]

  dfs = 4
  res = 4
  arm = 2
  armor = None

  att = 3
  damage = 1
  rng = 1
  off = 4
  str = 4
  pn = 0
  offensive_skills = [BattleFocus, HeavyCharge]

  def __init__(self, nation):
    super().__init__(nation)
    self.traits += [mounted_t]
    self.align = Wild
    self.corpses = [Skeletons]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, none_t]  


# Holy empire.
class Hamlet(City):
  name = hamlet_t
  events = [Unrest]
  food = 1.5
  grouth = 0
  public_order = 0
  resource = 1
  upkeep = 3000

  free_terrain = 1
  own_terrain = 0

  military_base = 40
  military_change = 100
  military_max = 60
  popdef_base = 25
  popdef_change = 200
  popdef_min = 5
  tags = [city_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.nation = nation
    self.pos = pos
    self.av_units = [Archers, PeasantLevies, Settler]
    self.resource_cost = [100, 100]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [none_t]
    self.hill = [0]
    self.events = [Unrest(self)]

  def set_capital_bonus(self):
    self.food += 0.5
    self.public_order += 30
    self.upkeep = 0

  def set_downgrade(self):
    msg = ''
    if self.level == 1 and self.pop <= 2500:
      msg = f'{self} se degrada a {hamlet_t}.'
      self.level = 0
      self.name = hamlet_t
      self.food -= 1.5
      self.grouth -= 1
      # self.income -= 10
      self.public_order -= 30
    if self.level == 2 and self.pop <= 8000:
      msg = f'{self} se degrada a {village_t}.'
      self.level = 1
      self.name = village_t
      self.food -= 1.5
      self.grouth -= 1
      # self.income -= 10
      self.public_order -= 30
    if self.level == 3 and self.pop <= 20000:
      msg = f'{self} se degrada a {town_t}.'
      self.level = 2
      self.name = town_t
      self.food -= 1.5
      self.grouth -= 1
      # self.income -= 10
      self.public_order -= 30
    if msg:
      self.nation.log[-1].append(msg)
      logging.debug(msg)
      if self.nation.show_info:
        sp.speak(msg, 1) 
        sleep(loadsound('notify18'))

  def set_upgrade(self):
    msg = ''
    if self.level == 0 and self.pop >= 4000:
      msg = f'{self} mejor a {village_t}.'
      self.level = 1
      self.name = village_t
      self.food += 1.5
      self.grouth += 1
      self.public_order += 30
    if self.level == 1 and self.pop >= 10000:
      msg = f'{self} mejor a {town_t}.'
      self.level = 2
      self.name = town_t
      self.food += 1.5
      self.grouth += 1
      # self.income += 10
      self.public_order += 30
    if self.level == 2 and self.pop >= 30000:
      msg = f'{self} mejor a {city_t}.'
      self.level = 3
      self.name = city_t
      self.food += 1.5
      self.grouth += 1
      self.public_order += 30
    if msg:
      logging.debug(msg)
      if self.nation.show_info:
        sp.speak(msg, 1)
        sleep(loadsound('notify14'))


# edificios.
class TrainingCamp(Building):
  name = 'campo de entrenamiento'
  gold = 10000
  own_terrain = 1
  size = 4
  tags = [military_t]
  unique = 1

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [SwordsMen, Sagittarii]
    self.resource_cost = [0, 40]
    self.soil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [0]
    self.upgrade = [ImprovedTrainingCamp]


class ImprovedTrainingCamp(TrainingCamp, Building):
  base = TrainingCamp
  gold = 20000
  name = 'campo de entrenamiento mejorado'
  public_order = 10
  size = 4
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Commander, SpearMen]  
    self.resource_cost = [0, 70]
    self.size = 0
    self.upgrade = [Barracks]


class Barracks(ImprovedTrainingCamp, Building):
  base = TrainingCamp
  gold = 30000
  name = 'cuartel'
  public_order = 10
  tags = [military_t, unrest_t]
  unique = 1
  upkeep = 100

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [SpearMen, GreatSwordsMen, Aquilifer]
    self.resource_cost = [0, 120]
    self.size = 0
    self.upgrade = [ImprovedBarracks]


class ImprovedBarracks(Barracks, Building):
  base = TrainingCamp
  gold = 40000
  name = 'cuartel mejorado'
  public_order = 15
  tags = [military_t, unrest_t]
  unique = 1
  upkeep = 150

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Halberdier, CrossBowMen]
    self.resource_cost = [0, 200]
    self.size = 0


class Pastures(Building):
  name = 'pasturas'
  gold = 14000
  food = 1.5
  income = 1.5

  own_terrain = 1
  size = 6
  tags = [military_t]
  unique = 1

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
  base = Pastures
  gold = 25000
  food = 2
  income = 3
  unique = 1

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Equites2]
    self.resource_cost = [0, 140]
    self.size = 0
    self.hill = [0]
    self.upgrade = []


class MeetingCamp(Building):
  name = 'campo de reunión'
  gold = 7000
  own_terrain = 1
  public_order = 10
  size = 4
  tags = [military_t]
  unique = 1

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Flagellants, SwordsMen]
    self.resource_cost = [0, 50]
    self.soil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [0]
    self.upgrade = [CultOfLight]


class CultOfLight(MeetingCamp, Building):
  base = MeetingCamp
  gold = 15500
  name = 'culto de la luz'
  public_order = 25
  upkeep = 1000
  unique = 1

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Inquisitors, SacredWarriors, Priest]
    self.resource_cost = [0, 100]
    self.size = 0
    self.upgrade = [TempleOfLight]


class TempleOfLight(CultOfLight, Building):
  base = MeetingCamp
  gold = 25000
  name = 'templo de la luz'
  public_order = 50
  upkeep = 2500
  unique = 1

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [KnightsTemplar ]
    self.resource_cost = [0, 160]
    self.size = 0
    self.upgrade = []


# unidades.
# comandantes.
class Commander(Human):
  name = 'commander'
  units = 10
  type = 'infantry'
  comm = 1
  gold = 1500
  upkeep = 50
  resource_cost = 25
  food = 5
  pop = 40
  terrain_skills = []
  tags = ['commander']

  hp = 2
  mp = [4, 4]
  moves = 6
  resolve = 8
  global_skills = [Organization]

  dfs = 4
  res = 2
  arm = 0
  armor = MediumArmor()
  shield = Shield()
  defensive_skills = []

  att = 2
  damage = 2
  off = 4
  str = 4
  pn = 0
  offensive_skills = []

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.mp = [2, 2]


class Aquilifer(Human):
  name = 'aquilifer'
  units = 30
  type = 'infantry'
  traits = [human_t, leader_t]
  gold = 4000
  upkeep = 70
  resource_cost = 30
  food = 5
  pop = 100
  unique = 1
  tags = ['commander']

  hp = 2
  mp = [2, 2]
  moves = 7
  resolve = 8
  global_skills = [Inspiration, Regroup]

  dfs = 5
  res = 2
  arm = 0
  armor = HeavyArmor()
  shield = Shield()

  att = 3
  damage = 2
  off = 5
  str = 4
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild


class Priest(Human):
  name = 'sacerdote'
  units = 10
  type = 'infantry'
  traits = [human_t, commander_t, sacred_t]
  gold = 1000
  upkeep = 40
  resource_cost = 30
  food = 3
  pop = 40
  tags = ['commander']

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 7
  global_skills = [SermonOfCourage]

  dfs = 3
  res = 2
  arm = 0
  armor = LightArmor()

  att = 1
  damage = 2
  off = 4
  str = 4
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild


# unidades
class Settler(Human):
  name = settler_t
  units = 300
  type = 'civil'
  traits = [human_t, settler_t]
  gold = 2000
  upkeep = 1
  resource_cost = 50
  food = 1
  pop = 1000

  hp = 1
  mp = [2, 2]
  moves = 3
  resolve = 3

  dfs = 1
  res = 1
  arm = 0
  armor = None

  att = 1
  damage = 1
  off = 1
  str = 1
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.buildings = [Hamlet]
    self.corpses = [Zombies]


class Flagellants(Human):
  name = flagellants_t
  units = 20
  type = 'infantry'
  traits = [human_t, sacred_t]
  gold = 140
  upkeep = 10
  resource_cost = 11
  food = 2
  pop = 40
  terrain_skills = [Burn]

  hp = 2
  mp = [2, 2]
  moves = 5
  resolve = 6

  dfs = 3
  res = 2
  arm = 0
  armor = None

  att = 2
  damage = 1
  off = 4
  str = 4
  pn = 0
  offensive_skills = [Fanatism]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild


class SwordsMen(Human):
  name = swordsmen_t
  units = 20
  type = 'infantry'
  traits = [human_t]
  gold = 250
  upkeep = 18
  resource_cost = 12
  food = 3
  pop = 30
  terrain_skills = [Burn, Raid]

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 6
  global_skills = [Regroup]

  dfs = 4
  res = 2
  arm = 0
  armor = LightArmor()
  shield = Shield()

  att = 1
  damage = 2
  off = 4
  str = 3
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild


class GreatSwordsMen(Human):
  name = 'grandes espaderos'
  units = 10
  type = 'infantry'
  traits = [human_t]
  gold = 720
  upkeep = 32
  resource_cost = 16
  food = 4
  pop = 30
  terrain_skills = [Burn, Raid]

  hp = 2
  mp = [2, 2]
  moves = 7
  resolve = 7
  global_skills = [BattleBrothers, Regroup, Refit]

  dfs = 5
  res = 2
  arm = 0
  armor = None

  att = 2
  damage = 2
  off = 6
  str = 4
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild


class SpearMen(Human):
  name = spearmen_t
  units = 10
  type = 'infantry'
  traits = [human_t]
  gold = 620
  upkeep = 30
  resource_cost = 15
  food = 3
  pop = 50
  terrain_skills = [Burn, Raid]

  hp = 2
  mp = [2, 2]
  moves = 5
  resolve = 6
  global_skills = [BattleBrothers, Regroup]

  dfs = 4
  res = 2
  arm = 0
  armor = HeavyArmor()

  att = 1
  rng = 3
  damage = 3
  off = 4
  str = 5
  pn = 1
  offensive_skills = [HoldPositions, PikeSquare]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild


class Halberdier(Human):
  name = 'halberdier'
  units = 10
  type = 'infantry'
  traits = [human_t]
  gold = 450
  upkeep = 50
  resource_cost = 18
  food = 4
  pop = 23
  terrain_skills = [Burn, Raid]

  hp = 2
  mp = [2, 2]
  moves = 7
  resolve = 6
  global_skills = [BattleBrothers, Regroup, Refit, ]

  dfs = 4
  res = 2
  arm = 0
  armor = MediumArmor()

  att = 2
  damage = 3
  off = 4
  str = 4
  pn = 2
  offensive_skills = [MassSpears, PikeSquare]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild


class Inquisitors(Human):
  name = inquisitors_t
  units = 10
  type = 'infantry'
  traits = [human_t, sacred_t]
  gold = 600
  upkeep = 60
  resource_cost = 25
  food = 4
  pop = 40

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 8
  global_skills = [Exaltation, Furtive, Regroup]

  dfs = 3
  res = 2
  arm = 0
  armor = LightArmor()

  att = 2
  damage = 1
  off = 3
  str = 3
  pn = 0
  offensive_skills = [ShadowHunter]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Zombies]


class SacredWarriors(Human):
  name = sacred_warriors_t
  units = 10
  type = 'infantry'
  traits = [human_t, sacred_t]
  gold = 400
  upkeep = 40
  resource_cost = 16
  food = 4
  pop = 25
  global_skills = [Burn, Raid]

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 8
  global_skills = [Regroup, Refit]

  dfs = 5
  res = 2
  arm = 0
  armor = None
  shield = Shield()

  att = 1
  damage = 2
  off = 5
  str = 4
  pn = 0
  offensive_skills = [ShadowHunter]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Zombies]


class KnightsTemplar (Human):
  name = knights_templar_t
  units = 10
  type = 'infantry'
  traits = [human_t, sacred_t]
  gold = 550
  upkeep = 60
  resource_cost = 20
  food = 4
  pop = 35
  global_skills = [Burn, Raid]

  hp = 2
  mp = [2, 2]
  moves = 7
  resolve = 9
  global_skills = [Regroup, Refit]

  dfs = 5
  res = 2
  arm = 0
  armor = HeavyArmor()
  shield = Shield

  att = 2
  damage = 3
  off = 6
  str = 4
  pn = 0
  offensive_skills = [ShadowHunter]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Zombies]  


class Sagittarii(Human):
  name = 'sagittarii'
  units = 20
  type = 'infantry'
  traits = [human_t]
  gold = 320
  upkeep = 15
  resource_cost = 15
  food = 3
  pop = 40
  terrain_skills = [Burn, Raid]

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 6

  dfs = 3
  res = 2
  arm = 0
  armor = None

  att = 1
  damage = 1
  rng = 15
  off = 5
  str = 3
  pn = 0
  offensive_skills = [Ambushment, ReadyAndWaiting, Skirmisher]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild


class CrossBowMen(Human):
  name = 'CrossBowMen'
  units = 10
  type = 'infantry'
  traits = [human_t]
  gold = 420
  upkeep = 30
  resource_cost = 18
  food = 3
  pop = 30

  hp = 2
  mp = [2, 2]
  moves = 5
  resolve = 6

  dfs = 3
  res = 2
  arm = 0
  armor = None

  att = 1
  damage = 3
  rng = 10
  off = 5
  str = 5
  pn = 1
  offensive_skills = [Ambushment, ReadyAndWaiting, Skirmisher]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild


class Arquebusier(Human):
  name = 'Arquebusier'
  units = 10
  type = 'infantry'
  traits = [human_t]
  gold = 520
  upkeep = 40
  resource_cost = 25
  food = 3
  pop = 30

  hp = 2
  mp = [2, 2]
  moves = 5
  resolve = 6

  dfs = 3
  res = 2
  arm = 0
  armor = None

  att = 1
  damage = 3
  rng = 10
  off = 5
  str = 5
  pn = 1
  offensive_skills = [Ambushment, ReadyAndWaiting, Skirmisher]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild


class Musket(Human):
  name = 'musquet'
  units = 10
  type = 'infantry'
  traits = [human_t]
  gold = 550
  upkeep = 50
  resource_cost = 25
  food = 3
  pop = 30

  hp = 2
  mp = [2, 2]
  moves = 5
  resolve = 6

  dfs = 3
  res = 2
  arm = 0
  armor = None

  att = 2
  damage = 2
  rng = 20
  off = 6
  str = 5
  pn = 2
  offensive_skills = [Ambushment, ReadyAndWaiting, Skirmisher]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild


class Equites(Human):
  name = equites_t
  units = 10
  type = 'cavalry'
  traits = [human_t]
  gold = 1500
  upkeep = 50
  resource_cost = 18
  food = 5
  pop = 60
  terrain_skills = [Burn, Raid]

  hp = 3
  mp = [4, 4]
  moves = 8
  resolve = 6
  global_skills = [BattleBrothers]

  dfs = 3
  res = 3
  arm = 1
  armor = None
  shield = Shield()

  att = 2
  damage = 1
  off = 4
  str = 4
  pn = 0
  offensive_skills = [Charge]

  def __init__(self, nation):
    super().__init__(nation)
    self.traits += [mounted_t]
    self.align = Wild
    self.corpses = [Skeletons]
    self.favhill = [0]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t]


class Equites2(Human):
  name = feudal_knights_t
  units = 10
  type = 'cavalry'
  traits = [human_t]
  gold = 1700
  upkeep = 80
  resource_cost = 22
  food = 6
  pop = 70
  terrain_skills = [Burn, Raid]

  hp = 3
  mp = [3, 3]
  moves = 7
  resolve = 8
  global_skills = [BattleBrothers, Regroup, Refit]

  dfs = 5
  res = 3
  arm = 2
  armor = HeavyArmor()

  att = 1
  damage = 3
  off = 5
  str = 5
  pn = 2
  offensive_skills = [HeavyCharge]

  def __init__(self, nation):
    super().__init__(nation)
    self.traits += [mounted_t]
    self.align = Wild
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t]


# Vampiros.
class CursedHamlet(City):
  name = cursed_hamlet_t
  events = [Unrest]
  food = 1.5
  grouth = 0
  public_order = 30
  resource = 1
  upkeep = 1000

  free_terrain = 1
  own_terrain = 0

  military_base = 40
  military_change = 50
  military_max = 70
  popdef_base = 30
  popdef_change = 250
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
    self.food += 2
    self.public_order += 50
    self.upkeep = 0

  def set_downgrade(self):
    msg = ''
    if self.level == 1 and self.pop <= 1500:
      logging.debug(f'{self} se degrada a {cursed_hamlet_t}.')
      self.level = 0
      self.name = cursed_hamlet_t
      self.food -= 0.5
      self.grouth -= 0.5
      self.public_order -= 50
    if self.level == 2 and self.pop <= 6000:
      logging.debug(f'{self} se degrada a {village_t}.')
      self.level = 1
      self.name = village_t
      self.food -= 0.5
      self.grouth -= 0.5
      self.public_order -= 50
    if self.level == 3 and self.pop <= 6000:
      logging.debug(f'{self} se degrada a {town_t}.')
      self.level = 2
      self.name = town_t
      self.food -= 0.5
      self.grouth -= 0.5
      self.public_order -= 50
    if msg:
      logging.debug(msg)
      if self.nation.show_info:
        sp.speak(msg, 1)
        sleep(loadsound('notify18'))

  def set_upgrade(self):
    msg = ''
    if self.level == 0 and self.pop >= 3000:
      msg = f'{self} mejor a {village_t}.'
      self.level = 1
      self.name = cursed_village_t
      self.food += 1
      self.grouth += 0.5
      self.public_order += 50
    if self.level == 1 and self.pop >= 8000:
      msg = f'{self} mejor a {village_t}.'
      self.level = 1
      self.name = town_t
      self.food += 1
      self.grouth += 0.5
      self.public_order += 50
    if self.level == 2 and self.pop >= 18000:
      msg = f'{self} mejor a {city_t}.'
      self.level = 3
      self.name = city_t
      self.food += 0.5
      self.grouth += 0.5
      self.public_order += 50
    if msg:
      logging.debug(msg)
      if self.nation.show_info:
        sp.speak(msg, 1)
        sleep(loadsound('notify14'))


class Barrow(Building):
  name = barrow_t
  gold = 12000
  own_terrain = 1
  size = 4
  tags = [military_t]
  unique = 1

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Ghouls, Zombies]
    self.resource_cost = [0, 30]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [none_t]
    self.hill = [0]
    self.upgrade = [Cemetery]


class Cemetery(Barrow, Building):
  name = cemetery_t
  base = Barrow
  gold = 18000
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Draugr, VarGhul, Vampire]
    self.resource_cost = [0, 70]
    self.size = 0
    self.upgrade = [Mausoleum]


class Mausoleum(Cemetery, Building):
  name = 'mausoleo'
  base = Barrow
  gold = 25000
  public_order = 20
  upkeep = 100
  tags = [military_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [GraveGuards, VampireLord]
    self.resource_cost = [0, 120]
    self.size = 0
    self.upgrade = [CourtOfBlood]


class CourtOfBlood(Mausoleum, Building):
  name = 'corte oscura'
  base = Barrow
  gold = 45000
  public_order = 50

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [black_knights_t, blood_knights_t, VladDracul]
    self.resource_cost = [0, 159]
    self.size = 0
    self.upgrade = []


class DesecratedRuins (Building):
  name = 'ruinas profanadas'
  gold = 9000
  own_terrain = 1
  size = 4
  tags = [military_t]
  unique = 1

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Ghouls, FellBats]
    self.resource_cost = [0, 50]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [0, 1]
    self.upgrade = [SummoningField]


class SummoningField(DesecratedRuins, Building):
  name = summoning_field_t
  base = DesecratedRuins
  gold = 14000

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [CryptHorrors, Necromancer, Skeletons]
    self.resource_cost = [0, 100]
    self.size = 0
    self.upgrade = [DarkMonolit]


class DarkMonolit(SummoningField, Building):
  name = 'monolito oscuro'
  base = DesecratedRuins
  gold = 25000
  own_terrain = 1
  size = 4
  public_order = 50
  upkeep = 200

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Banshee, Vargheist]
    self.resource_cost = [0, 250]
    self.size = 0
    self.upgrade = []


class HuntingGround(Building):
  name = hunting_ground_t
  gold = 10000
  own_terrain = 1
  size = 4
  tags = [military_t]
  unique = 1

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Bats, Wolves]
    self.resource_cost = [0, 60]
    self.surf = [forest_t]
    self.hill = [0]
    self.upgrade = [SinisterForest]


class SinisterForest(HuntingGround, Building):
  name = 'bosque abyssal'
  base = HuntingGround
  gold = 20000

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [DireWolves]
    self.resource_cost = [0, 100]
    self.size = 0
    self.upgrade = []


class Gallows(Building):
  name = 'Gallows'
  gold = 5200
  public_order = 30
  own_terrain = 1
  size = 6
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
  base = Gallows
  gold = 8500
  public_order = 66
  tags = [unrest_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 60]
    self.size = 0
    self.upgrade = []


class Pit(Building):
  name = 'fosa'
  gold = 1500
  food = 1.5
  own_terrain = 1
  size = 6
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
  base = Pit
  gold = 6000
  food = 2
  resource = 2
  tags = [food_t, resource_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 80]
    self.size = 0
    self.upgrade = []


# unidades.
class Adjule(Unit):
  name = 'adjule'
  units = 10
  type = 'beast'
  traits = [death_t]
  gold = 330
  upkeep = 32
  resource_cost = 18
  food = 0
  pop = 25

  hp = 3
  mp = [3, 3]
  moves = 7
  resolve = 10
  global_skills = [DesertSurvival, NightFerocity, NightSurvival, Regroup]

  dfs = 3
  res = 4
  arm = 0
  armor = None

  att = 2
  damage = 1
  off = 4
  str = 4
  pn = 0
  
  stealth = 6

  fear = 3

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    Ground.__init__(self)
    self.corpses = [HellHounds]
    self.favhill = [0]
    self.favsoil = [waste_t]
    self.favsurf = [none_t]
    self.traits += [animal_t]


class Banshee(Undead):
  # Pendiente: resolver el tema etéreo.
  name = 'banshee'
  units = 1
  type = 'infantry'
  traits = [death_t, malignant_t, ethereal_t]
  gold = 666
  upkeep = 333
  resource_cost = 30
  food = 0
  pop = 30
  terrain_skills = []

  hp = 4
  mp = [2, 2]
  moves = 8
  resolve = 10
  global_skills = [Ethereal, FearAura, Fly, NightFerocity]

  dfs = 5
  res = 6
  arm = 0
  armor = None

  att = 2
  rng = 1
  mrng = 10
  damage = 3
  off = 5
  str = 6
  pn = 3
  offensive_skills = [Scream]
  
  stealth = 8

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell


class Bats(Unit):
  name = bats_t
  units = 20
  type = 'beast'
  traits = [animal_t, poisonres_t]
  gold = 135
  upkeep = 5
  resource_cost = 12
  food = 2
  pop = 30
  terrain_skills = [ForestSurvival]

  hp = 1
  mp = [4, 4]
  moves = 7
  resolve = 3
  global_skills = [Fly, NightSurvival]

  dfs = 4
  res = 1
  arm = 0
  armor = None

  att = 1
  damage = 1
  off = 4
  str = 2
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    self.favhill = [1]
    self.favsurf = [forest_t]
    self.traits += [animal_t]


class BlackKnights(Undead):
  name = black_knights_t
  units = 5
  type = 'cavalry'
  traits = [death_t, malignant_t]
  gold = 800
  upkeep = 70
  resource_cost = 26
  food = 0
  pop = 25
  terrain_skills = [Burn]

  hp = 3
  mp = [3, 3]
  moves = 7
  resolve = 10
  global_skills = [FearAura, NightFerocity, NightSurvival]

  dfs = 5
  res = 5
  arm = 1
  armor = HeavyArmor()

  att = 2
  damage = 3
  off = 6
  str = 5
  pn = 2
  offensive_skills = [HeavyCharge]

  def __init__(self, nation):
    super().__init__(nation)
    self.traits += [mounted_t]
    self.align = Hell
    self.corpses = [BloodKnights]
    self.favhill = [0]
    self.favsoil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t]


class BloodKnights(Undead):
  name = blood_knights_t
  units = 1
  type = 'infantry'
  traits = [death_t, malignant_t]
  gold = 1200
  upkeep = 150
  resource_cost = 22
  food = 0
  pop = 40

  hp = 4
  mp = [2, 2]
  moves = 7
  resolve = 10
  global_skills = [FearAura, NightFerocity, NightSurvival]

  dfs = 7
  res = 5
  arm = 1
  armor = HeavyArmor()
  shield = Shield()

  att = 3
  damage = 4
  off = 7
  str = 6
  pn = 2

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    self.favhill = [0]
    self.favsoil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t]


class CryptHorrors (Undead):
  name = crypt_horror_t
  units = 10
  type = 'infantry'
  traits = [death_t, malignant_t]
  gold = 460
  upkeep = 40
  resource_cost = 16
  food = 0
  pop = 0

  hp = 3
  mp = [2, 2]
  moves = 5
  resolve = 10
  global_skills = [FearAura, Fly, NightFerocity, NightSurvival]

  dfs = 5
  res = 5
  arm = 2
  armor = None

  att = 3
  damage = 3
  off = 5
  str = 4
  pn = 1
  offensive_skills = [ToxicClaws]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    self.corpses = [Skeletons]


class DireWolves(Undead):
  name = dire_wolves_t
  units = 5
  type = 'beast'
  traits = [death_t, malignant_t]
  gold = 350
  upkeep = 60
  resource_cost = 22
  food = 0
  pop = 15
  terrain_skills = [ForestSurvival, MountainSurvival]

  hp = 3
  mp = [3, 3]
  moves = 6
  resolve = 10
  global_skills = [NightFerocity, NightSurvival]

  dfs = 3
  res = 4
  arm = 2

  att = 2
  damage = 3
  off = 5
  str = 5
  pn = 1

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    self.corpses = [Skeletons]
    self.favhill = [0, 1]
    self.favsoil = [glacier_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]


class Draugr(Unit):
  name = 'Draugr'
  units = 5
  type = 'infantry'
  traits = [death_t, malignant_t]
  gold = 220
  upkeep = 40
  resource_cost = 18
  food = 2
  pop = 30
  terrain_skills = [Burn, ForestSurvival, MountainSurvival, Raid]

  hp = 3
  mp = [2, 2]
  moves = 6
  resolve = 7
  global_skills = [Scavenger, NightFerocity, Regroup]

  dfs = 5
  res = 4
  arm = 2

  att = 2
  damage = 1
  off = 5
  str = 4
  pn = 0
  offensive_skills = [ToxicClaws]
  
  stealth = 4

  fear = 4
  pref_corpses = 1

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    Ground.__init__(self)
    self.corpses = [Skeletons]
    self.favhill = [0, 1]
    self.favsoil = [tundra_t]
    self.favsurf = [none_t, forest_t, swamp_t]


class FellBats(Undead):
  name = fell_bats_t
  units = 5
  type = 'beast'
  traits = [death_t, malignant_t]
  gold = 320
  upkeep = 20
  resource_cost = 18
  food = 0
  pop = 15
  terrain_skills = [ForestSurvival, MountainSurvival]

  hp = 2
  mp = [4, 4]
  moves = 8
  resolve = 10
  global_skills = [ElusiveShadow, Fly, NightFerocity, NightSurvival]

  dfs = 5
  res = 3
  arm = 0

  att = 2
  damage = 1
  off = 3
  str = 4
  pn = 0
  offensive_skills = [ToxicClaws]

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    self.favsurf = [forest_t]


class Ghouls(Human):
  name = ghouls_t
  units = 15
  type = 'infantry'
  traits = [human_t, malignant_t, poisonres_t]
  gold = 200
  upkeep = 15
  resource_cost = 13
  food = 2
  pop = 20
  terrain_skills = [Burn, ForestSurvival, MountainSurvival, Raid]

  hp = 2
  mp = [2, 2]
  moves = 5
  resolve = 5
  global_skills = [Scavenger]

  dfs = 4
  res = 2
  arm = 0
  armor = None

  att = 2
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
    self.corpses = [Draugr]


class Necromancer(Human):
  name = necromancer_t
  units = 1
  type = 'infantry'
  traits = [human_t, malignant_t, commander_t, wizard_t]
  gold = 800
  upkeep = 400
  resource_cost = 20
  food = 4
  pop = 30
  terrain_skills = []

  hp = 2
  mp = [2, 2]
  moves = 5
  resolve = 5
  power = 0
  power_max = 20
  power_res = 2
  global_skills = [LordOfBones]
  spells = [RaiseDead]

  dfs = 3
  res = 2
  arm = 0
  armor = None
  shield = Shield()

  att = 1
  damage = 1
  off = 3
  str = 3
  pn = 0
  
  fear = 6
  pref_corpses = 1
  stealth = 6

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    self.corpses = [Zombies]


class GraveGuards(Undead):
  name = grave_guards_t
  units = 10
  type = 'infantry'
  traits = [death_t, malignant_t]
  gold = 550
  upkeep = 50
  resource_cost = 18
  food = 0
  pop = 30
  terrain_skills = [Burn]

  hp = 3
  mp = [2, 2]
  moves = 6
  resolve = 10
  global_skills = [FearAura, NightFerocity, NightSurvival]

  dfs = 5
  res = 5
  arm = 2
  armor = HeavyArmor()
  shield = Shield()

  att = 2
  damage = 4
  off = 4
  str = 5
  pn = 1

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    self.corpses = [Skeletons]
    self.favsoil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t]


class Settler2(Human):
  name = settler_t
  units = 200
  type = 'civil'
  traits = [human_t, settler_t]
  gold = 1000
  upkeep = 0
  resource_cost = 50
  food = 1
  pop = 800

  hp = 1
  mp = [2, 2]
  moves = 3
  resolve = 4

  dfs = 1
  res = 1
  arm = 0
  armor = None

  att = 1
  damage = 1
  off = 1
  str = 1
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.buildings = [CursedHamlet]
    self.corpses = [Zombies]


class Skeletons(Undead):
  name = skeletons_t
  units = 10
  type = 'infantry'
  traits = [death_t]
  traits = [death_t]
  gold = 200
  upkeep = 0
  resource_cost = 10
  food = 0
  pop = 0
  terrain_skills = [Burn, Raid]

  hp = 2
  mp = [2, 2]
  moves = 5
  resolve = 10
  global_skills = [SkeletonLegion]

  dfs = 3
  res = 4
  arm = 2

  att = 2
  damage = 1
  off = 3
  str = 3
  pn = 0

  fear = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    self.corpses = []


class Vampire(Undead):
  name = vampire_t
  units = 1
  type = 'beast'
  traits = [death_t, malignant_t, vampire_t]
  gold = 500
  upkeep = 80
  resource_cost = 25
  food = 0
  pop = 15
  terrain_skills = [ForestSurvival, MountainSurvival]

  hp = 12
  mp = [2, 2]
  moves = 8
  resolve = 10
  global_skills = [DarkPresence, ElusiveShadow, FearAura, Fly, NightFerocity, NightSurvival]

  dfs = 6
  res = 5
  arm = 0
  armor = LightArmor()

  att = 4
  damage = 3
  off = 5
  str = 5
  pn = 2

  populated_land = 1

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = []
    self.favhill = [0, 1]
    self.favsurf = [forest_t, none_t, swamp_t]


class VampireLord(Undead):
  name = vampirelord_t
  units = 1
  type = 'beast'
  traits = [death_t, commander_t, malignant_t, vampire_t]
  gold = 700
  upkeep = 200
  resource_cost = 25
  food = 0
  pop = 35
  terrain_skills = [ForestSurvival, MountainSurvival]

  hp = 14
  mp = [2, 2]
  moves = 9
  resolve = 10
  global_skills = [DarkPresence, ElusiveShadow, FearAura, Fly, LordOfBlodd, NightFerocity, NightSurvival]

  dfs = 7
  res = 5
  arm = 0
  armor = MediumArmor()

  att = 5
  damage = 4
  off = 6
  str = 6
  pn = 2

  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = []
    self.favhill = [0, 1]
    self.favsurf = [forest_t, none_t, swamp_t]


class Vargheist(Undead):
  name = 'vargheist'
  units = 1
  type = 'beast'
  traits = [death_t, malignant_t, vampire_t]
  gold = 420
  upkeep = 120
  resource_cost = 20
  food = 0
  pop = 60
  terrain_skills = [ForestSurvival, MountainSurvival]

  hp = 10
  mp = [2, 2]
  moves = 9
  resolve = 10
  global_skills = [ElusiveShadow, FearAura, Fly, NightFerocity, NightSurvival, TheBeast]

  dfs = 4
  res = 5
  arm = 0

  att = 4
  damage = 4
  off = 7
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
  unique = 1
  type = 'beast'
  traits = [death_t, malignant_t, leader_t, vampire_t, wizard_t]
  gold = 3200
  upkeep = 1620
  resource_cost = 50
  food = 0
  pop = 100
  terrain_skills = [ForestSurvival, MountainSurvival]

  hp = 18
  mp = [2, 2]
  moves = 12
  resolve = 10
  global_skills = [DarkPresence, ElusiveShadow, FearAura, Fly, LordOfBlodd, MastersEye, NightFerocity, NightSurvival]
  spells = [CastBloodRain, RaiseDead]  # , BloodStorm, DarkMantle, SummonBloodKnight]
  power = 0
  power_max = 60
  power_res = 4

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
    self.corpses = []
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, none_t, swamp_t]
    self.favhill = 0, 1


class VarGhul(Undead):
  name = varghul_t
  units = 1
  type = 'beast'
  traits = [death_t, malignant_t, commander_t, vampire_t]
  gold = 370
  upkeep = 80
  resource_cost = 20
  food = 5
  pop = 25

  hp = 5
  mp = [2, 2]
  moves = 6
  resolve = 6
  global_skills = [Scavenger, LordOfBlodd, NightFerocity, NightSurvival]

  dfs = 4
  res = 5
  arm = 2

  att = 3
  damage = 2
  off = 4
  str = 5
  offensive_skills = [ToxicClaws]

  fear = 2
  populated_land = 1

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    self.corpses = [CryptHorrors]
    self.favhill = [0, 1]
    self.favsoil = [waste_t]
    self.favsurf = [forest_t, none_t, swamp_t]


class Zombies(Undead, Ground):
  name = zombies_t
  units = 20
  type = 'infantry'
  traits = [death_t]
  gold = 220
  upkeep = 0
  resource_cost = 10
  food = 0
  pop = 20

  hp = 2
  mp = [2, 2]
  moves = 3
  resolve = 10
  global_skills = [Spread]

  dfs = 2
  res = 3
  arm = 0

  att = 1
  damage = 1
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
  gold = 4000
  grouth = 30
  income = 50
  food = 50
  own_terrain = 1
  size = 6
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
  gold = 2000
  food = 1.5
  own_terrain = 1
  size = 6
  tags = [food_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 40]
    self.soil = [grassland_t, plains_t]
    self.surf = [none_t]
    self.hill = [0]
    self.upgrade = [SmallFarm]


class SmallFarm(Fields, Building):
  name = small_farm_t
  base = Fields
  gold = 6000
  food = 3

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 80]
    self.size = 0
    self.upgrade = [Farm]


class Farm(SmallFarm, Building):
  name = farm_t
  base = SmallFarm
  gold = 15000
  food = 5
  # grouth = 50
  # income = 50

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
    food = 25
    gold = 200
    income = 20
    resource_cost = 50
    tags = [food_t, income_t, rest_t]


class Quarry(Building):
  name = 'cantera'
  gold = 10000
  food = 1.4
  income = 1.2
  resource = 2
  own_terrain = 1
  size = 6
  tags = [resource_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 70]
    self.soil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [1]


class SawMill(Building):
  name = 'aserradero'
  gold = 8000
  food = 1.3
  income = 2
  resource = 1.5
  own_terrain = 1
  size = 6
  tags = [resource_t]

  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 60]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t]
    self.hill = [0, 1]


# Naciones.
class HolyEmpire(Nation):
  name = holy_empire_t
  nick = nation_phrase1_t
  traits = [human_t, order_t]
  gold = 30000
  food_limit_builds = 3000
  food_limit_upgrades = 5000
  military_limit_upgrades = 3000
  grouth_base = 5
  grouth_rate = 60
  expansion = 5000
  public_order = 0
  upkeep_base = 60
  upkeep_change = 200

  attack_factor = 500
  capture_rate = 400
  commander_rate = 7
  explore_range = 3
  scout_factor = 8
  stalk_rate = 200

  city_req_pop_base = 4500
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
    self.unallow_around_ocean = 2 
    self.unallow_around_swamp = 1
    self.unallow_around_tundra = 0
    self.unallow_around_glacier = 0

    # edificios iniciales disponibles.
    self.av_buildings = [Fields, MeetingCamp, Pastures, TrainingCamp, SawMill, Quarry]
    self.av_cities = [Hamlet]
    self.city_names = roman_citynames
    
    # terrenos de comida.
    self.for_food.soil = [grassland_t, plains_t]
    self.for_food.surf = [none_t]
    self.for_food.hill = [0]
    # terrenos de recursos.
    self.for_res.soil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.for_res.surf = [2]
    self.for_res.hill = [0, 1]
    
    # rebeldes.
    self.units_rebels = [Archers, Hunters, Raiders, Riders, Warriors]
    # initial placement.
    self.initial_placement = Hamlet
    # initial settler.
    self.initial_settler = Settler 
    # Unidades iniciales.
    self.start_units = [PeasantLevies, PeasantLevies]


class WoodElves(Nation):
  name = wood_elves_t
  nick = ''
  traits = [elf_t, animal_t]
  gold = 30000
  food_limit_builds = 3000
  food_limit_upgrades = 5000
  military_limit_upgrades = 3000
  grouth_base = 2
  grouth_rate = 100
  public_order = 0
  expansion = 6000
  upkeep_base = 70
  upkeep_change = 200

  attack_factor = 600
  capture_rate = 600
  commander_rate = 8
  explore_range = 3
  scout_factor = 5
  stalk_rate = 400

  city_req_pop_base = 3000
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
    self.allow_around_forest = 4
    # terrenos adyacentes no permitidos.
    self.unallow_around_ocean = 2 
    self.unallow_around_swamp = 2

    # edificios iniciales disponibles.
    self.av_buildings = [CraftmensTree, FalconRefuge, GlisteningPastures, Grove, Sanctuary, stoneCarvers]
    self.av_cities = [Hall]
    self.city_names = elven_citynames
    
    # terrenos de comida.
    self.for_food_soil = [grassland_t, plains_t]
    self.for_food.surf = [none_t]
    self.for_food.hill = [0]
    # terrenos de recursos.
    self.for_res.soil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.for_res.surf = [2]
    self.for_res.hill = [0, 1]
    
    # rebeldes.
    self.units_rebels = [Archers, Hunters, Raiders, Riders, Warriors]
    # initial placement.
    self.initial_placement = Hall
    # initial settler.
    self.initial_settler = ElvesSettler
    # initial units.
    self.start_units = [ForestGuard, ForestGuard]


class Walachia(Nation):
  name = wallachia_t
  nick = nation_phrase2_t
  traits = [death_t, malignant_t, vampire_t]
  gold = 30000
  food_limit_builds = 3000
  food_limit_upgrades = 4000
  military_limit_upgrades = 3000
  grouth_base = 4
  grouth_rate = 80
  expansion = 5000
  public_order = 0
  upkeep_base = 70
  upkeep_change = 200

  attack_factor = 360
  capture_rate = 300
  commander_rate = 6
  explore_range = 5
  scout_factor = 15
  stalk_rate = 160

  city_req_pop_base = 2000
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
    self.soil = [plains_t, waste_t]
    self.surf = [forest_t, none_t]
    # Terrenos adyacentes permitidos
    self.allow_around_desert = 5
    self.allow_around_hill = 4
    # terrenos adyacentes no permitidos.
    self.unallow_around_ocean = 1
  
    # edificios iniciales disponibles.
    self.av_buildings = [Barrow, DesecratedRuins, HuntingGround, Gallows, Pit, Quarry, SawMill]
    self.av_cities = [CursedHamlet]
    self.city_names = death_citynames
    # terrenos de comida.
    self.for_food.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.for_food.surf = [none_t]
    self.for_food.hill = [0]
    # terrenos de recursos.
    self.for_res.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.for_res.surf = [none_t, forest_t]
    self.for_res.hill = [0, 1]
    
    # rebeldes.
    self.units_rebels = [Archers, Raiders, Riders, Ghouls, VarGhul]
    # initial placement.
    self.initial_placement = CursedHamlet
    # initial settler.
    self.initial_settler = Settler2
    # Unidades iniciales.
    self.start_units = [Zombies, Zombies, Zombies, VampireLord]


# unidades random.
class Archers(Human):
  name = archers_t
  units = 15
  type = 'infantry'
  traits = [human_t]
  gold = 160
  upkeep = 10
  resource_cost = 12
  food = 3
  pop = 25
  terrain_skills = [Burn, Raid]

  hp = 2
  mp = [2, 2]
  moves = 5
  resolve = 4

  dfs = 2
  res = 2
  arm = 0
  armor = None

  att = 1
  damage = 1
  rng = 15
  off = 3
  str = 3
  pn = 0
  offensive_skills = [Skirmisher]
  
  fear = 5
  populated_land = 1
  sort_chance = 70

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Zombies]
    self.favhill = [1]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t, forest_t]


class Akhlut(Unit):
  name = 'akhlut'
  units = 1
  type = 'beast'
  gold = 320
  upkeep = 60
  resource_cost = 28
  food = 12
  pop = 25
  terrain_skills = [ForestSurvival, MountainSurvival]

  hp = 6
  mp = [2, 2]
  moves = 7
  resolve = 6
  global_skills = [Regroup]

  dfs = 3
  res = 5
  arm = 2
  armor = None

  att = 3
  damage = 3
  off = 5
  str = 5
  pn = 0

  stealth = 6

  fear = 2

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    Amphibian.__init__(self)
    self.corpses = [Skeletons]
    self.favhill = [0, 1]
    self.favsoil = [tundra_t]
    self.favsurf = [forest_t, none_t, swamp_t]
    self.traits += [animal_t, ]


class BlackOrcs(Unit):
  name = 'orcos negros'
  units = 10
  type = 'infantry'
  traits = [orc_t, malignant_t]
  gold = 360
  upkeep = 35
  resource_cost = 20
  food = 6
  pop = 30
  terrain_skills = [Burn, Raid]

  hp = 6
  mp = [2, 2]
  moves = 7
  resolve = 8
  global_skills = [BloodyBeast]

  dfs = 4
  res = 4
  arm = 2
  armor = HeavyArmor

  att = 3
  damage = 2
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
    self.corpses = [Skeletons]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t, forest_t]
    self.traits += [orc_t]


class Children_Of_The_Wind(Human):
  name = 'hijos del viento'
  units = 10
  type = 'infantry'
  traits = [human_t]
  gold = 50
  upkeep = 20
  resource_cost = 16
  food = 3
  pop = 30
  terrain_skills = {Burn, DesertSurvival, Raid}

  hp = 2
  mp = [2, 2]
  moves = 7
  resolve = 6
  global_skills = [DesertSurvival, MountainSurvival]

  dfs = 3
  res = 2
  arm = 0
  armor = LightArmor()
  shield = Shield()

  att = 2
  damage = 2
  off = 5
  str = 3
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Zombies]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]


class Crocodile(Unit):
  name = crocodile_t
  units = 1
  type = animal_t
  gold = 220
  upkeep = 30
  resource_cost = 20
  food = 2
  pop = 10
  terrain_skills = [SwampSurvival]

  hp = 4
  mp = [2, 2]
  moves = 6
  resolve = 3
  global_skills = []

  dfs = 3
  res = 5
  arm = 3
  armor = None

  att = 2
  damage = 3
  off = 5
  str = 5
  pn = 1

  stealth = 8

  fear = 2

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    Amphibian.__init__(self)
    self.corpses = [Skeletons]
    self.favhill = [0, 1]
    self.favsoil = [tundra_t]
    self.favsurf = [forest_t, none_t, swamp_t]
    self.traits += [animal_t, ]


class DesertNomads(Human):
  name = 'ginetes a camello'
  units = 10
  type = 'cavalry'
  traits = [human_t]
  gold = 240
  upkeep = 20
  resource_cost = 18
  food = 4
  pop = 20
  terrain_skills = [Burn, DesertSurvival, Raid]

  hp = 3
  mp = [3, 3]
  moves = 8
  resolve = 5

  dfs = 3
  res = 3
  arm = 1
  armor = None
  shield = None

  att = 2
  damage = 1
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
    self.corpses = [Skeletons]
    self.favhill = [0]
    self.favsoil = [waste_t]
    self.favsurf = [none_t]


class Galley(Ship):
  name = 'galera'
  units = 1
  type = 'veicle'
  gold = 130
  upkeep = 30
  resource_cost = 35
  food = 10
  pop = 30

  hp = 25
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


class GiantWolves(Unit):
  name = giant_wolves_t
  units = 10
  type = 'beast'
  traits = [animal_t]
  gold = 60
  upkeep = 15
  resource_cost = 18
  food = 8
  pop = 15
  terrain_skills = [ForestSurvival, MountainSurvival]

  hp = 3
  mp = [2, 2]
  moves = 7
  resolve = 4
  global_skills = [BloodyBeast, Regroup]

  dfs = 4
  res = 4
  arm = 2
  armor = None

  att = 2
  damage = 2
  off = 5
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
    self.corpses = [DireWolves]
    self.favhill = [0, 1]
    self.favsoil = [tundra_t]
    self.favsurf = [none_t, forest_t]
    self.traits += [animal_t, ]


class Goblins(Unit):
  name = goblins_t
  units = 30
  type = 'infantry'
  traits = [goblin_t, malignant_t]
  gold = 50
  upkeep = 3
  resource_cost = 8
  food = 2
  pop = 14
  terrain_skills = [Burn, ForestSurvival, MountainSurvival, SwampSurvival, Raid]

  hp = 1
  mp = [3, 3]
  moves = 7
  resolve = 4
  global_skills = [BloodyBeast]

  dfs = 4
  res = 2
  arm = 0
  armor = None

  att = 2
  damage = 1
  rng = 10
  off = 3
  str = 2
  pn = 0
  offensive_skills = [Ambushment, Skirmisher] 
  
  fear = 3
  populated_land = 1
  sort_chance = 90
  stealth = 6

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    Ground.__init__(self)
    self.corpses = [Skeletons]
    self.favsoil = [waste_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, swamp_t]
    self.favhill = [0, 1]
    self.traits += [goblin_t]


class Harpy(Unit):
  name = harpy_t
  units = 10
  type = 'beast'
  traits = [malignant_t, poisonres_t]
  gold = 40
  upkeep = 10
  resource_cost = 16
  food = 0
  pop = 15
  terrain_skills = [ForestSurvival, MountainSurvival, Raid]

  hp = 3
  mp = [4, 4]
  moves = 6
  resolve = 4
  global_skills = [Fly]

  dfs = 5
  res = 3
  arm = 0
  armor = None

  att = 1
  damage = 2
  off = 3
  str = 3
  pn = 0
  
  fear = 1
  populated_land = 1
  sort_chance = 90
  stealth = 7

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    self.favhill = [0, 1]    
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [forest_t, swamp_t]
    self.soil += [coast_t]
    self.traits += [mounster_t]


class HellHounds(Undead):
  name = hellhounds_t
  units = 4
  type = 'beast'
  traits = [death_t, malignant_t]
  gold = 160
  upkeep = 20
  resource_cost = 30
  food = 0
  pop = 25
  terrain_skills = [DesertSurvival, ForestSurvival, MountainSurvival]

  hp = 4
  mp = [2, 2]
  moves = 6
  resolve = 10
  global_skills = [BloodyBeast, NightFerocity, NightSurvival, Regroup]

  dfs = 4
  res = 5
  arm = 2
  armor = None

  att = 1
  damage = 4
  off = 4
  str = 5
  pn = 0
  
  fear = 2
  stealth = 8

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    self.corpses = [Skeletons]
    self.favhill = [0, 1]
    self.favsoil = [plains_t, tundra_t, waste_t]


class Hyaenas(Unit):
  name = 'hyaenas'
  units = 10
  type = 'beast'
  traits = [animal_t]
  gold = 50
  upkeep = 8
  resource_cost = 15
  food = 4
  pop = 25

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 4
  global_skills = [BloodyBeast, NightSurvival, Regroup]

  dfs = 3
  res = 3
  arm = 0
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
    self.corpses = [HellHounds]
    self.favhill = [0]
    self.favsoil = [plains_t, waste_t]
    self.favsurf = [forest_t, none_t]
    self.traits += [animal_t]


class Hunters(Human):
  name = hunters_t
  units = 10
  type = 'infantry'
  traits = [human_t]
  gold = 90
  upkeep = 6
  resource_cost = 12
  food = 3
  pop = 12
  terrain_skills = [ForestSurvival, MountainSurvival, Raid]

  hp = 2
  mp = [2, 2]
  moves = 5
  resolve = 4

  dfs = 3
  res = 2
  arm = 0
  armor = None

  att = 1
  rng = 10
  damage = 2
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
    self.corpses = [Zombies]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]


class NomadsRiders(Human):
  name = nomads_riders_t
  units = 20
  type = 'cavalry'
  traits = [human_t]
  gold = 60
  upkeep = 15
  resource_cost = 18
  food = 5
  pop = 20
  terrain_skills = [Burn, Raid]

  hp = 3
  mp = [4, 4]
  moves = 7
  resolve = 4

  dfs = 3
  res = 3
  arm = 1
  armor = None

  att = 1
  rng = 15
  damage = 1
  off = 4
  str = 4
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
    self.corpses = [Skeletons]
    self.favhill = [0]
    self.favsoil = [plains_t, grassland_t, tundra_t]
    self.favsurf = [none_t]
    self.traits += [mounted_t]


class Orc_Archers(Unit):
  name = orc_archers_t
  units = 20
  type = 'infantry'
  traits = [orc_t, malignant_t]
  gold = 140
  upkeep = 12
  resource_cost = 12
  food = 3
  pop = 20
  terrain_skills = [Burn, ForestSurvival, MountainSurvival, Raid]

  hp = 3
  mp = [2, 2]
  moves = 5
  resolve = 4
  global_skills = [BloodyBeast]

  dfs = 3
  res = 2
  arm = 1
  armor = None

  att = 1
  damage = 1
  rng = 12
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
    self.corpses = [Skeletons]
    self.favhill = [1]    
    self.favsoil = [waste_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t, forest_t]
    self.traits += [orc_t]


class Orcs(Unit):
  name = 'orcos'
  units = 20
  type = 'infantry'
  traits = [orc_t, malignant_t]
  gold = 30
  upkeep = 5
  resource_cost = 10
  food = 3
  pop = 20
  terrain_skills = [Burn, ForestSurvival, MountainSurvival, Raid]

  hp = 3
  mp = [2, 2]
  moves = 6
  resolve = 4
  global_skills = [BloodyBeast]

  dfs = 3
  res = 3
  arm = 1
  armor = None

  att = 2
  damage = 1
  off = 3
  str = 4
  pn = 0
  
  fear = 4
  populated_land = 1
  sort_chance = 80
  stealth = 4

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Hell
    Ground.__init__(self)
    self.corpses = [Skeletons]
    self.favsoil = [waste_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t, forest_t]
    self.traits += [orc_t]


class Levy(Human):
  name = levy_t
  units = 20
  type = 'infantry'
  traits = [human_t, levy_t]
  gold = 50
  upkeep = 9
  resource_cost = 10
  food = 3
  pop = 20
  terrain_skills = [Burn, Raid]

  hp = 2
  mp = [2, 2]
  moves = 5
  resolve = 5

  dfs = 3
  res = 2
  arm = 0
  armor = None
  shield = Shield()

  att = 1
  damage = 2
  off = 3
  str = 2
  pn = 0

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t]
    self.favhill = [0]


class PeasantLevies(Human):
  name = peasant_levies_t
  units = 20
  type = 'infantry'
  traits = [human_t, levy_t]
  gold = 90
  upkeep = 6
  resource_cost = 8
  food = 3
  pop = 40
  terrain_skills = [DesertSurvival]

  hp = 2
  mp = [2, 2]
  moves = 5
  resolve = 4

  dfs = 2
  res = 2
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
    self.corpses = [Zombies]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t]
    self.favhill = [0]


class Raiders(Human):
  name = raiders_t
  units = 10
  type = 'infantry'
  traits = [human_t]
  gold = 50
  upkeep = 15
  resource_cost = 14
  food = 3
  pop = 20
  terrain_skills = [Burn, ForestSurvival, MountainSurvival, SwampSurvival, Raid]

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 4

  dfs = 3
  res = 2
  arm = 0
  armor = LightArmor()

  att = 1
  damage = 2
  off = 4
  str = 3
  pn = 0
  
  fear = 4
  populated_land = 1
  sort_chance = 80

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Zombies]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [forest_t, none_t, swamp_t]


class Riders(Human):
  name = riders_t
  units = 20
  type = 'cavalry'
  traits = [human_t]
  gold = 80
  upkeep = 20
  resource_cost = 15
  food = 6
  pop = 12
  terrain_skills = [Burn, Raid]

  hp = 3
  mp = [4, 4]
  moves = 8
  resolve = 6
  global_skills = []

  dfs = 3
  res = 2
  arm = 1
  armor = None

  att = 1
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
    self.corpses = [Skeletons]
    self.favhill = [0]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t]


class TheKnightsTemplar(Human):
  name = the_knights_templar_t
  units = 20
  type = 'cavalry'
  traits = [human_t]
  gold = 550
  upkeep = 40
  resource_cost = 30
  food = 8
  pop = 30
  terrain_skills = [Burn, Raid]

  hp = 3
  mp = [3, 3]
  moves = 8
  resolve = 8
  global_skills = [BattleBrothers, Regroup, Refit]

  dfs = 5
  res = 3
  arm = 2
  armor = HeavyArmor()

  att = 2
  damage = 2
  damage_charge_mod = 1
  off = 6
  str = 5
  pn = 2
  offensive_skills = [HeavyCharge]

  def __init__(self, nation):
    super().__init__(nation)
    self.traits += [mounted_t]
    self.align = Wild
    self.corpses = [BloodKnights]
    self.favhill = [0]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t]


class Wargs(Unit):
  name = 'huargos'
  units = 20
  type = 'beast'
  traits = [malignant_t]
  gold = 60
  upkeep = 20
  resource_cost = 18
  food = 6
  pop = 30
  terrain_skills = [ForestSurvival, MountainSurvival]

  hp = 3
  mp = [2, 2]
  moves = 7
  resolve = 5
  global_skills = [BloodyBeast, Regroup]

  dfs = 4
  res = 3
  arm = 0
  armor = None

  att = 1
  damage = 3
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
    self.corpses = [Skeletons]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]
    self.traits += [mounster_t]


class Warriors(Human):
  name = warriors_t
  units = 20
  type = 'infantry'
  traits = [human_t]
  gold = 30
  upkeep = 6
  resource_cost = 10
  food = 3
  pop = 15
  terrain_skills = [Burn, Raid]

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 6

  dfs = 3
  res = 2
  arm = 0
  armor = None

  att = 2
  damage = 1
  off = 4
  str = 3
  pn = 0

  fear = 5
  populated_land = 1
  sort_chance = 70

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    self.corpses = [Zombies]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, none_t]


class Wolves(Unit):
  name = wolves_t
  units = 10
  type = 'beast'
  traits = [animal_t]
  gold = 50
  upkeep = 6
  resource_cost = 14
  food = 4
  pop = 20
  terrain_skills = [ForestSurvival]

  hp = 2
  mp = [2, 2]
  moves = 7
  resolve = 4
  global_skills = [NightFerocity, Regroup]

  dfs = 4
  res = 3
  arm = 0
  armor = None

  att = 1
  damage = 1
  off = 3
  str = 4
  pn = 0
  
  fear = 4
  populated_land = 1
  sort_chance = 70
  stealth = 4

  def __init__(self, nation):
    super().__init__(nation)
    self.align = Wild
    Ground.__init__(self)
    self.corpses = [DireWolves]
    self.favhill = [0]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t, forest_t]


class Hell(Nation):
  name = hell_t
  show_info = 0

  def __init__(self):
    super().__init__()
    self.log = [[hell_t]]
    self.av_units = [Ghouls, Goblins, Harpy, HellHounds, Hyaenas, Orcs,
                     Orc_Archers, Skeletons, Vargheist, VarGhul, Wargs,
                     Zombies, Necromancer]


class Wild(Nation):
  name = wild_t
  show_info = 0

  def __init__(self):
    super().__init__()
    self.log = [[wild_t]]
    self.av_units = [Akhlut, Crocodile, DesertNomads, Hunters, NomadsRiders,
                     Raiders, Warriors, Wolves]

