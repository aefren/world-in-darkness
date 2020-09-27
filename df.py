# -*- coding: utf-8 -*-
#!/usr/bin/env python
import gc
from glob import glob
from math import ceil, floor
import pdb
import pickle
from random import choice, randint, uniform, shuffle
import sys
from time import sleep, time

import natsort
import numpy as np
import pygame
from pygame.time import get_ticks as ticks

dev_mode = 1
if dev_mode == 0:
  exec('import basics')
  exec('from data.lang.es import *')
  exec('import log_module')
  exec('from data.skills import *')
  exec('import screen_reader')
  exec('from sound import *')
if dev_mode:
  import basics
  from data.lang.es import *
  from data.skills import *
  import log_module
  from screen_reader import *
  from sound import *

# Some colors.
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
pygame.init()
# Set the width and height of the screen [width, height]
size = (700, 500)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Dark Fantasy")



class Ambient:

  def __init__(self):
    self.day_night = [0, [day_t, night_t]]
    self.month = [0, [january_t, february_t, march_t, april_t, may_t, june_t,
                      july_t, august_t, september_t, october_t, november_t, december_t]]
    self.season = [2, [winter_t, spring_t, summer_t, autum_t]]
    self.time = [0, [morning_t, noon_t , afternoon_t, evening_t, night_t, midnight_t, dawn_t]]
    self.week = 1
    self.year = 1
    self.update()

  def update(self):
    self.sseason = f'{self.season[1][self.season[0]]}'
    self.stime = f'{self.time[1][self.time[0]]}'
    self.smonth = f' {self.month[1][self.month[0]]}'
    self.syear = f'{year_t} {self.year}'
    self.sday_night = f'{self.day_night[1][self.day_night[0]]}'



ambient = Ambient()



class Empty:
  pass



class Terrain:
  ambient = ambient
  around_defense = 0
  around_threat = 0
  bu = 0
  building = None
  city = None
  blocked = 0
  cost = 0
  cost_fly = 2
  defense = 0
  defense_req = 0
  flood = 0
  has_city = 0
  income = 0
  is_city = 0
  land = 0
  name = None
  nation = None
  location = None
  pop = 0
  public_order = 0
  raid_gain = 0
  raided = 0
  raining = 0
  size = 0
  size_total = 10
  skills = []
  threat = 0

  soil = None
  surf = None
  hill = 0
  cost = 0
  food = 1
  grouth_total = 0
  resource = 1
  temp = 0
  daytemp = [0, 0, 0, 0]
  nighttemp = [0, 0, 0, 0]
  sight = 0
  type = 'tile'
  unrest = 0
  world = None

  def __init__(self):
    self.buildings = []
    self.corpses = []
    self.effects = []
    self.events = []
    self.items = []
    self.skills = []
    self.skill_names = []
    self.terrain_events = []
    self.units = []
    self.units_blocked = []
    if self.soil: self.update()

  def __str__(self):
    name = ''
    if self.name: name += f' {self.name}.'
    if self.hill: name += f' {hill_t},'
    if self.surf.name != none_t:
      name += f' {self.surf.name}, {self.soil.name}'
    elif self.surf.name == none_t:
      name += f' {self.soil.name}.'
    return name

  
  def add_corpses(self,corpse, number):
    corpse.deads = [number]
    corpse.units = 0
    corpse.hp_total = 0
    self.units += [corpse]
  def add_ghouls(self):
    roll = basics.roll_dice(2)
    if self.units: roll -= 1
    if roll >= 11:
      unit = self.add_unit(Ghouls, hell_t)
      unit.hp_total = randint(3, 8) * unit.hp
      unit.update()
      # rint(f'{roll=} {unit} added in  {self.cords}.')

  def add_miasma(self):
    roll = basics.roll_dice(2)
    corpses = 0
    for cr in self.corpses:
      corpses += sum(cr.deads)
    corpses = ceil(corpses / 10)
    sk = Miasma(self)
    if roll + corpses >= 11 and sk.name not in [ev.name for ev in self.events]:
      sk.turns = randint(2, 5)
      self.events += [sk]
    elif sk.name in [ev.name for ev in self.events] and roll >= 10:
      for ev in self.events:
        if ev.name == sk.name: ev.turns += 1

  def add_unit(self, unit, nation, revealed=0, units=None):   
    global sayland
    done = 0
    for nt in world.nations + world.random_nations:
      if nt.name == nation: 
        unit = unit(nt)
        done = 1
    if done == 0:
      for nt in world.nations + world.random_nations:
        if nt.name == unit(nation).align.name: 
          unit = unit(nt)
    unit.log += [[f'{turn_t} {world.turn}.']]
    unit.pos = self
    self.units.append(unit)
    unit.update()
    unit.set_hidden(unit.pos)
    unit.revealed = revealed
    unit.set_tile_attr()
    sayland = 1
    return unit

  def get_distance(self, pos, trg):
    v = 1
    while True:
      sq = pos.get_near_tiles(v)
      if pos == trg: return 0
      if trg in sq:
        return v
      
      v += 1

  def get_near_tiles(self, value):
    tiles = []
    x = [self.x - value, self.x + value]
    y = [self.y - value, self.y + value]
    for t1 in self.scenary:
      if (t1.x >= x[0] and t1.x <= x[1]) and (t1.y >= y[0] and t1.y <= y[1]):
        tiles.append(t1)
    return tiles

  def get_nearest_nation(self):
    distance = 1
    tries = 500
    while tries > 0:
      tiles = self.get_near_tiles(distance)
      for tl in tiles:
        if tl.nation: return distance
      
      distance += 1
      tries -= 1
      
  def get_tile_value(self, nation, scenary):
    self.food_value = self.food
    self.res_value = self.resource
    sq = self.get_near_tiles(1)
    for s in sq:
      if s != self and s in nation.map:
        self.food_value += s.food
        self.res_value += s.resource
        self.mean = mean([self.food_value, self.res_value])
  
  def is_blocked(self):
    self.blocked = 0
    for uni in self.units:
      if (uni.hidden == 0 and uni.nation != self.nation  
          and self.blocked == 0 and self.is_city == 0):
        self.blocked = 1

  def play_ambient(self):
    if self.hill: loadsound('terra_hill5', vol=(0.5, 0.5))
    if self.surf.name == forest_t: loadsound('terra_forest1', channel=ch1)
    elif self.surf.name == swamp_t: loadsound('terra_swamp1', channel=ch1, vol=(0.5, 0.5))
    elif self.soil.name == waste_t: loadsound('terra_waste1', channel=ch2)
    elif self.soil.name == grassland_t: loadsound('terra_grass1', channel=ch2)
    elif self.soil.name == plains_t: loadsound('terra_plains1', channel=ch2)
    elif self.soil.name == ocean_t: loadsound('terra_ocean1', channel=ch2, vol=0.2)
    elif self.soil.name == coast_t: loadsound('terra_ocean1', channel=ch2, vol=0.2)
    elif self.soil.name == tundra_t: loadsound('terra_tundra1', channel=ch2, vol=0.2)

  def pos_sight(self, nation, scenary):
    for t in scenary: t.sight = 0
    for t in scenary:
      t.update(nation)
      if t.city and t.city.nation == nation:
          t.sight = 1
          if t not in nation.map: nation.map.append(t)
          sq = t.get_near_tiles(1)
          for s in sq:
            if s not in nation.map: nation.map.append(s)
            if s.surf.name not in [forest_t] and s.hill not in [1]:
              s.sight = 1
        
      for uni in t.units:
        if uni.nation == nation:
          uni.update()
          sq = t.get_near_tiles(1)
          for s in sq:
            s.sight = 1
            if s not in nation.map: nation.map.append(s)
          if ((uni.pos.hill or uni.can_fly) 
              and (uni.day_night == 0 or uni.dark_vision)): 
          
            for s in sq:
              sq1 = s.get_near_tiles(1)
              for s1 in sq1:
                if s1 not in nation.map: 
                  nation.map.append(s1)
                  # print(f'se agrega {s1}.')
                if s1.surf.name not in [forest_t] and s1.hill not in [1]:
                  s1.sight = 1
  
  def set_around(self, nation):
    # logging.info(f'{self}.')
    score = 0
    if self.city:
      for i in self.city.units: score += i.ranking
    self.around_coast = 0
    self.around_corpses = 0
    self.around_defense = 0
    self.around_desert = 0
    self.around_forest = 0
    self.around_glacier = 0
    self.around_grassland = 0
    self.around_hill = 0
    self.around_mountain = 0
    self.around_nations = []
    self.around_snations = []
    self.around_plains = 0
    self.around_swamp = 0
    self.around_threat = 0
    self.around_tundra = 0
    self.around_volcano = 0
    self.buildings_tags = []
    self.coast = 0
    self.units_effects = []
    self.units_traits = []
    self.units_tags = []
    sq = self.get_near_tiles(1)
    for s in sq:
      if s != self:
        if s.hill: self.around_hill += 1
        if s.surf.name != none_t:
          if s.surf.name == swamp_t: self.around_swamp += 1
          if s.surf.name == forest_t: self.around_forest += 1
          if s.surf.name == mountain_t: self.around_mountain += 1
          if s.surf.name == volcano_t: self.around_volcano += 1
        elif s.surf.name == none_t:
          if s.soil.name == coast_t: self.around_coast += 1
          if s.soil.name == plains_t: self.around_plains += 1
          if s.soil.name == grassland_t: self.around_grassland += 1
          if s.soil.name == waste_t: self.around_desert += 1
          if s.soil.name == tundra_t: self.around_tundra += 1
          if s.soil.name == glacier_t: self.around_glacier += 1

      if s.sight and s != self:
        self.around_corpses += len(s.corpses)
        if nation:
          if s.nation != nation and s.nation != None: self.around_nations += [s.nation]
          if s.nation == nation: self.around_snations += [s.nation]
          for uni in s.units:
            uni.update()
            if uni.nation != nation and uni.hidden == 0:
              self.around_threat += uni.ranking
            if uni.nation == nation:
              self.around_defense += uni.ranking

    # datos finales.
    for uni in self.units:
      self.units_effects += uni.effects
      self.units_tags += uni.tags
      self.units_traits += uni.traits
      for bu in self.buildings:
        self.buildings_tags += bu.tags
    if self.soil.name == ocean_t and any(i for i in [self.around_plains,
                                                     self.around_grassland, self.around_desert, self.around_tundra, self.around_glacier, self.around_forest, self.around_swamp]):
      self.coast = 1
      self.soil.name = coast_t
    elif self.soil.name != ocean_t and self.around_coast:
      self.coast = 1

  def set_defense(self, nation, info=0):
    if info: print(f'set_defense.')
    self.defense = 0
    for u in self.units:
      u.update()
      if nation and u.nation == nation: 
        self.defense += u.ranking
        if info:print(f'{u.id}  {u.hidden}, {u.ranking}.')

  def set_income(self):
    if self.nation == None: return
    self.income = self.pop * self.nation.gold_rate
    self.incomes = [self.income]
    self.income += self.public_order * self.income / 100
    self.incomes += [self.income]
    # de edificios.
    for b in self.buildings:
      self.income *= b.income_pre
      if b.is_complete or b.type == city_t:
        self.income *= b.income
        self.incomes += [str(f'{b}'), self.income]
  
  def set_public_order(self, info=0):
    if info: print(f'set_public_order.') 
    if self.pop < 0: self.pop = 0
    if self.nation == None: return

    self.public_order = self.pop * 100 / self.food
    if info: print(f'after food {self.public_order= }.')
    self.public_order = 100 - self.public_order
    if info: print(f'after 100 reduction {self.public_order= }.')
    if self.is_city == 0: self.public_order += self.city.public_order * 0.5
    if info: print(f'after if is city {self.public_order= }.')
    # From buildings.
    self.public_order_buildings = 0
    for b in self.buildings:
      self.public_order_buildings += b.public_order_pre
      if b.is_complete or b.type == city_t:
        self.public_order_buildings += b.public_order

    self.public_order += self.public_order_buildings
    if info: print(f'after buildings {self.public_order= }.')
    # From units.
    self.po = self.public_order
    if self.public_order: 
      self.public_order_unrest = self.unrest * 100 // abs(self.public_order)
      self.public_order -= self.public_order_unrest
      if info: print(f'after unrest {self.public_order= }.')
    
    if self.defense: self.public_order += (self.defense //10)/self.pop*100
    if info: print(f'after units defense {self.public_order= }.')
    
    self.public_order_reduction = self.public_order_buildings * abs(self.public_order) / 100
    self.public_order += self.public_order_reduction
    if info: print(f'after reduction {self.public_order= }.')
    if self.public_order > 100: self.public_order = 100
    if self.po > 100: self.po = 100
    if self.public_order < -100: self.public_order = -100
    if self.pop == 0: 
      self.public_order = 0
      self.unrest = 0
    # if self.unrest > 100: self.unrest = 100
    self.unrest = round(self.unrest)

  def set_skills(self, info=0):
    if info: print(f'set_skills')
    self.skills = []
    self.skill_names = []
    self.units.sort(key=lambda x: x.ranking, reverse=True)
    for uni in self.units:
      if uni.hp_total > 0:
        unit_skills = uni.get_skills()
        for sk in unit_skills:
          if sk.effect in ['all', 'friend'] and sk.name not in self.skill_names:
            # print(f'terreno agrega {sk.name}.')
            self.skills += [sk]
            self.skill_names += [sk.name]
            
      self.skill_names.sort()
      [sk.tile_run(self) for sk in self.skills]

  def set_starving(self):
    if self.pop >= 120 * self.food / 100:
      self.unrest += randint(10, 35)
    elif self.pop >= 80 * self.food / 100:
      self.unrest += randint(5, 15)
    if self.pop >= 100 * self.food / 100 and basics.roll_dice(2) >= 11:
      deads = randint(10, 50)
      if deads > self.pop: deads = self.pop
      self.unrest += deads * self.pop / 100
      msg = f'starving in {self} {self.cords} deads {deads}.'
      self.nation.log[-1] += [msg]
      if self.nation.show_info: sleep(loadsound('spell36', channel=ch5) // 1.3)

  def set_tile_skills(self):
    if self.hill == 0:
      self.terrain_events = [e for e in self.terrain_events
                             if e.name != HillTerrain.name]
    if self.surf.name == none_t:
      self.terrain_events = [e for e in self.terrain_events
                             if e.name != ForestTerrain.name 
                             and e.name != SwampTerrain.name]
    if self.surf.name == forest_t:
      self.terrain_events = [e for e in self.terrain_events
                             if e.name != SwampTerrain.name]
      if ForestTerrain.name not in [e.name for e in self.terrain_events]:
        self.terrain_events += [ForestTerrain(self)]
    if self.surf.name == swamp_t:
      self.terrain_events = [e for e in self.terrain_events
                             if e.name != ForestTerrain.name
                             and e.name != HillTerrain.name]
      if SwampTerrain.name not in [e.name for e in self.terrain_events]:
        self.terrain_events += [SwampTerrain(self)]
    if self.hill:
      self.terrain_events = [e for e in self.terrain_events
                             if e.name != SwampTerrain.name]
      if HillTerrain.name not in [e.name for e in self.terrain_events]:
        self.terrain_events += [HillTerrain(self)]
    # day.
    if world.ambient.day_night[0] == 0:
      self.terrain_events = [e for e in self.terrain_events
                             if e.name != night_t]
    # night.
    if world.ambient.day_night[0]:
      if Night.name not in [e.name for e in self.terrain_events]:
        self.terrain_events += [Night(self)]
  
  def set_threat(self, nation):
    self.threat = 0
    if self.sight:
      for uni in self.units:
        if uni.nation.name != nation.name and uni.hidden == 0:
          uni.update()
          self.threat += uni.ranking

  def start_turn(self):
    self.raining = 0
    self.set_starving()
    for ev in self.events:
      ev.tile_run(self)
    self.events = [ev for ev in self.events if ev.turns > 0]
    self.burned = 0
    self.corpses = [i for i in self.corpses + self.units if i.hp_total < 1 and sum(i.deads) > 0
                    and i.corpses]
    if self.city: self.city.raid_outcome = 0
    if self.flood > 0: self.flood -= 1
    self.raided = 0
    if self.unrest > 0: self.unrest -= randint(2, 10)
    if self.unrest > 0: self.unrest -= self.defense * 0.1
    self.unrest = round(self.unrest)
    if self.unrest < 0: self.unrest = 0
    self.units_blocked + [u for u in self.units if u.blocked > 0]
    for u in self.units_blocked: u.blocked -= 1
    self.units += [u for u in self.units_blocked if u.blocked < 1]
    self.units_blocked = [u for u in self.units_blocked if u.blocked > 0]
    if self.corpses:
      self.add_miasma()
      self.add_ghouls()
      for cr in self.corpses:
        reducing = randint(5, 20) // cr.hp
        #Pdb().set_trace()
        cr.deads[0] -= reducing

  def stats_buildings(self):
    for b in self.buildings:
      if b.type == building_t: b.update()
      if b.is_complete == 0:
        self.food *= b.food_pre
        self.grouth_total += b.grouth_pre
        self.resource *= b.res_pre
      if b.is_complete or b.type == city_t:
        self.food *= b.food
        self.grouth_total *= b.grouth_total
        self.resource *= b.resource

  def stats_events(self):
    for ev in self.events:
      self.food *= ev.food
      self.income *= ev.income
      self.resource *= ev.res
      self.unrest *= ev.unrest

  def stats_tiles(self):
    self.cost = self.soil.cost
    self.cost += self.surf.cost
    self.food = self.soil.food
    self.food *= self.surf.food
    self.grouth_total = 0
    self.resource = self.soil.resource
    self.resource *= self.surf.resource
    if self.hill:
      self.cost += 1
      self.food *= 0.6
      self.resource *= 2
    
  def update(self, nation=None, info=0):
    if info: print(f'update {self} {self.cords}.')
    self.effects = []
    if mapeditor == 0: 
      self.ambient = world.ambient
      self.set_skills()
      self.set_tile_skills()
    self.has_city = 1 if self.city else 1
    self.is_city = 1 if [i for i in self.buildings if i.type == city_t] else 0
    self.set_around(nation)
    
    if nation:
      self.get_tile_value(nation, nation.map)
      self.set_threat(nation)
      
    # eliminando unidades, generando corpses.
    self.corpses = [i for i in self.corpses + self.units if i.hp_total < 1 and sum(i.deads) > 0
                    and i.corpses]
    self.units = [it for it in self.units 
                  if it.hp_total >= 1]
    self.is_blocked()
    
    # calculando defensa.
    self.set_defense(nation)
    
    # destruyendo edificios.
    for b in self.buildings:
      if b.resource_cost[0] < 1:
        msg = f'{b} {destroyed_t} {in_t} {self} {self.cords}.'
        if self.nation: self.nation.log[-1].append(msg)
        logging.debug(msg)
        sleep(loadsound('set8') / 2)

    self.buildings = [b for b in self.buildings if b.resource_cost[0] >= 1]
    self.bu = len(self.buildings)
    self.in_progress = 1 if [i for i in self.buildings
                             if i.resource_cost[0] < i.resource_cost[1]] else 0

    # Stats.
    self.stats_tiles()
    self.stats_buildings()
    self.stats_events()
    self.set_public_order()
    self.set_income()
    self.size = self.size_total
    self.size -= sum([b.size for b in self.buildings])
    
    # unidades.
    self.food_need = 0
    for i in self.units: 
      if nation and i.nation == nation: self.food_need += i.food * i.units
    self.food_available = self.food - self.food_need
    # rounding.
    self.around_threat = round(self.around_threat)
    self.defense = round(self.defense)
    self.food_available = round(self.food_available)
    self.food = round(self.food)
    self.income = round(self.income)
    self.pop = round(self.pop)
    self.public_order = round(self.public_order)
    self.resource = round(self.resource)
    self.threat = round(self.threat)
    
    self.day_night = self.ambient.day_night[0]
    self.month = self.ambient.smonth
    self.season = self.ambient.sseason
    self.time = self.ambient.stime
    self.week = self.ambient.week
    self.year = self.ambient.year



class Desert(Terrain):
  cost = 2
  cost_fly = 2
  food = 120
  name = waste_t
  resource = 1



class EmptySurf(Terrain):

  def __init__(self):
    self.name = none_t
    self.test = 10



class Glacier(Terrain):
  cost = 2
  cost_fly = 2
  food = 30
  name = glacier_t
  resource = 0



class Grassland(Terrain):
  cost = 2
  cost_fly = 2
  food = 300
  name = grassland_t
  resource = 1



class Forest(Terrain):
  cost = 1
  food = 0.7
  name = forest_t
  resource = 2

  def __init__(self):
    Terrain.__init__(self)
    self.tile_effects = [ForestTerrain]



class Mountain(Terrain):
  cost = 2
  cost_fly = 1
  food = -0.1
  name = mountain_t
  resource = 0



class Swamp(Terrain):
  cost = 1
  food = 0.5
  name = swamp_t
  resource = 1

  def __init__(self):
    Terrain.__init__(self)
    self.tile_effects = [SwampTerrain]



class Ocean(Terrain):
  cost = 1
  cost_fly = 2
  food = 75
  name = ocean_t
  resource = 0



class Plains(Terrain):
  cost = 2
  cost_fly = 2
  food = 200
  name = plains_t
  resource = 1



class River(Terrain):
  cost = 1
  food = 0
  name = river_t
  resource = 0



class Tundra(Terrain):
  cost = 2
  cost_fly = 2
  food = 100
  name = tundra_t
  resource = 0



class Volcano(Terrain):
  pass
  cost_fly = 2
  food = 0
  name = volcano_t
  resource = 0



class World:
  buildings = []
  difficulty = 100
  difficulty_type = 'simple'  # simple, dynamic.
  difficulty_change = 100
  east = 0
  events = []
  ext = None
  height  = 0
  log = []
  name = 'Unnamed'
  nations = []
  nations_score = 0
  map = []
  player_num = 0
  random_score = 0
  random_units = []
  turn = 0
  units = []
  west = 0
  width = 0

  def add_random_unit(self, num, info=1):
    logging.info(f'score aleatóreo a agregar. {num}.')
    tries = 100
    while tries > 0 and num > 0:
      tries -= 1
      building = choice(self.buildings)
      #print(f'adding unit from {building}.')
      item = choice(building.av_units)
      #print(f'adding {item}.')
      item = item(building.nation)
      item.city = building
      if info: 
        logging.debug(f'agregará {item}.')
      tile = building.pos
      go = 1
      
      # si listo.
      item.update()
      if go:
        if item.units > 1: item.hp_total = randint(20, 80) * item.hp_total / 100
        item.update()
        item.pos = tile
        item.nation.update(item.nation.map)
        loadsound('set10')
        tile.units.append(item)
        self.units.append(item)
        num -= item.ranking
        self.log[-1] += [f'{item} {added_t} {in_t} {tile} {tile.cords}.']
        if info: logging.info(f'{item}. ranking {item.ranking}.')

  def add_random_buildings(self, value):
    while value:
      tile = choice([t for t in self.map if t.get_nearest_nation() <= 6])
                      
      building = choice(self.random_buildings)
      for nt in self.random_nations:
        if nt.name == building.nation: building = building(nt, tile)
      tile.update()
      if City.check_tile_req(building, tile) and len(tile.buildings) < 3:
        msg = f'{building} added in {tile} {tile.cords}.'
        print(msg)
        self.log[-1] += [msg]
        building.size = 0
        building.resource_cost[0] = building.resource_cost[1]
        tile.buildings += [building]
        self.buildings += [building]
        value -= 1
        #print(f'{building} added in {tile} {tile.cords}.')
        #print(f'{self.buildings_value= }, {len(self.buildings)= }.')
  def clean_nations(self):
    global PLAYING
    [nt.update(nt.map) for nt in self.nations]
    self.nations = [nt for nt in self.nations if nt.cities 
                    or [u for u in nt.units if u.settler]
    or nt.units]

  def end_game(self):
    ai = [nt for nt in self.nations if nt.ai]
    hu = [nt for nt in self.nations if nt.ai == 0]
    if ai and hu == []:
      sp.speak(f'Defeat.', 1)
      PLAYING = False 
    elif hu and ai == []:
      sp.speak(f'Victory!')
      PLAYING = False

  def building_restoration(self):
    for b in self.buildings: b.resource_cost[0] += b.resource_cost[1]*0.2
  def season_events(self):
    self.set_master()
    self.events_num = int((self.height + self.width) * 0.1)
    self.generic_events()
    if self.ambient.sseason == autum_t: self.autum_events()
    if self.ambient.sseason == summer_t: self.summer_events()
    if self.ambient.sseason == spring_t: self.spring_events()
    if self.ambient.sseason == winter_t: self.winter_events()

  def set_master(self):
    self.super_unit = MASTER(Wild)
    self.super_unit.log = [[]]
    self.super_unit.pos = self.map[0]

  def generic_events(self):
    pass

  def autum_events(self):
    for r in range (len(self.map) // 50):
      events = [CastRain]
      ev = choice(events)
      go = 1
      pos = choice(self.map)
      roll = basics.roll_dice(2)
      if pos.soil.name == waste_t: roll -= 2
      if roll >= ev.cast:
        tiles = pos.get_near_tiles(2)
        for t in tiles:
          if ev.name in [e.name for e in t.events]: go = 0
      
      if go: 
        self.super_unit.pos = pos
        ev(self.super_unit).init(self.super_unit)

  def summer_events(self):
    for r in range (len(self.map) // 50):
      events = [CastLocustSwarm, CastRain]
      ev = choice(events)
      go = 1
      pos = choice(self.map)
      roll = basics.roll_dice(2)
      if roll >= ev.cast:
        tiles = pos.get_near_tiles(2)
        for t in tiles:
          if ev.name in [e.name for e in t.events]: go = 0
      
      if go: 
        self.super_unit.pos = pos
        ev(self.super_unit).init(self.super_unit)

  def spring_events(self):
    for r in range (len(self.map) // 50):
      events = [CastLocustSwarm, CastRain]
      ev = choice(events)
      go = 1
      pos = choice(self.map)
      roll = basics.roll_dice(2)
      if pos.soil.name == waste_t: roll -= 2
      if roll >= ev.cast:
        tiles = pos.get_near_tiles(2)
        for t in tiles:
          if ev.name in [e.name for e in t.events]: go = 0
      
      if go: 
        self.super_unit.pos = pos
        ev(self.super_unit).init(self.super_unit)

  def winter_events(self):
    for r in range (len(self.map) // 50):
      events = [CastRain, CastStorm]
      ev = choice(events)
      go = 1
      pos = choice(self.map)
      roll = basics.roll_dice(2)
      if pos.soil.name == waste_t: roll -= 2
      if roll >= ev.cast:
        tiles = pos.get_near_tiles(2)
        for t in tiles:
          if ev.name in [e.name for e in t.events]: go = 0
      
      if go: 
        self.super_unit.pos = pos
        ev(self.super_unit).init(self.super_unit)

  def update(self, scenary):
    self.clean_nations()
    # self.end_game()
    self.cnation = self.nations[self.player_num]
    [it.autokill() for it in self.units]
    self.season_events()
    
    self.buildings = []
    self.units = []
    for t in scenary:
      for b in t.buildings:
        if b.nation in self.random_nations: self.buildings += [b]
      for uni in t.units:
        if uni.nation in self.random_nations: self.units.append(uni)
    self.nations_score = sum(n.score for n in self.nations)
    self.units = [i for i in self.units if i.hp_total > 0]
    
    self.random_score = sum(u.ranking for u in self.units)



# funciones.
def ai_action_random(itm, info=0):
  itm.update()
  itm.pos.update(itm.nation)
  logging.debug(f'acción aleatórea para {itm} en {itm.pos} {itm.pos.cords}.')
  if info: logging.debug(f'salud {itm.hp_total}. mp {itm.mp}')
  tries = 3
  while (itm.mp[0] > 0 and itm.hp_total > 0 and itm.goto == []
           and tries > 0 and itm.stopped == 0):
    # si está en movimiento.
    if itm.goto:
      if info: logging.debug(f'se dirije a {itm.goto[0][1]} en {itm.goto[0][0]}.')
      return
    # si no descansa y no se mueve.
    elif itm.goto == []:
      # cast spells.
      if itm.spells: ai_unit_cast(itm.nation)
      # ataque hidden.
      itm.pos.update(itm.nation)
      rnd = itm.ranking * uniform(0.6, 1.2)
      if itm.pos.surf.name == forest_t and itm.forest_survival == 0: rnd -= rnd * 0.2
      if itm.pos.hill and itm.mountain_survival == 0: rnd -= rnd * 0.2
      if itm.pos.surf.name == swamp_t and itm.swamp_survival == 0: rnd -= rnd * 0.2
      if commander_t in itm.traits: rnd -= rnd * 0.2
      if info: logging.debug(f'{rnd=:}, {itm.pos.threat=:}.')
      if rnd > itm.pos.threat:
        auto_attack(itm)
        if any(i <= 0 for i in [itm.mp[0], itm.hp_total]): return
      
      # moves. 
      if itm.mp[0] > 0:
        if itm.pos.around_threat + itm.pos.threat < itm.ranking and basics.roll_dice(1) >= 5:
          if info: logging.debug(f'no moves by randomness.')
          return 
        random_move(itm, scenary)
        # cast spells.
        if itm.spells: ai_unit_cast(itm.nation)
    if tries < 2:
      logging.debug(f'tries < 7.')



def ai_add_settler(nation):
  '''buscará entrenar colonos para fundar nueva ciudad.'''
  logging.info(f'ai_add_settler. gold {nation.gold}.')
  logging.debug(f'pop_req  {nation.pop} de {nation.city_req_pop}.')
  if nation.pop < nation.city_req_pop or min(c.defense_total_percent for c in nation.cities) < 300: return
  settlers = [i for i in nation.units if i.settler]
  for ct in nation.cities:
    if ct.production and ct.production[0].settler: settlers += [ct.production]
  logging.debug(f'settlers {len(settlers)}, tiles far {len(nation.tiles_far)}.')
  if len(nation.tiles_far) and settlers == []:
    for ct in nation.cities:
      if ct.nation.defense_total_percent < 200:
        logging.debug(f'not enough defense total percent.')
        continue
      if len(ct.tiles_far) < 1:
        logging.debug(f'not land to set.')
        continue
      logging.debug(f'pop {in_t} {ct} {ct.pop}.')
      logging.debug(f'defense_total_percent {ct.defense_total_percent}. de ')
      logging.debug(f'seen threat {ct.seen_threat}.')
      if ct.seen_threat > 60 * ct.defense_total // 100: 
        logging.debug(f'high threat.')
        continue
      if ct.production == []:
        ct.update()
        logging.debug(f'gold {ct.nation.gold}.')
        units = [it(nation) for it in ct.all_av_units]
        [i.update() for i in units]
        units = [it for it in units if it.settler]
        shuffle(units)
        if units: unit = units[0]
        if req_unit(unit, nation, ct):
          ct.train(unit)
        break



def ai_add_explorer(nation):
  logging.info(f'ai_add_explorer {nation}. {world.turn= }.')
  for uni in nation.units_scout:
    distanse_limit = uni.mp[1] + uni.nation.explore_range
    if uni.pos.get_distance(uni.pos, uni.city.pos) >= distanse_limit - 1 and basics.roll_dice(2) >= 10: 
      uni.scout = 0
      uni.log[-1] += [f'randomly stops exploring.']
  nation.update(nation.map)
  if nation.units_free == []: return
  if nation.units_scout:
    logging.debug(f'{len(nation.units_scout)} exploradores. {len(nation.get_free_units())} unidades libres.')
    logging.debug(f'factor {len(nation.units_free)//nation.scout_factor}.')
  scout_factor = ceil(nation.scout_factor * nation.score / 100)
  scout_ranking = sum(i.ranking for i in nation.units_scout)
  add = 0
  if nation.units_scout == [] and len(nation.units_free) > 1: add = 1
  elif scout_ranking < scout_factor and len(nation.units_free) > 0: add = 1
  logging.debug(f'{add =: }, {len(nation.units_scout) =: }, {scout_factor =: } {scout_ranking =: }, {len(nation.units_free) =: }.')
  if add == 0: return
  nation.cities.sort(key=lambda x: x.defense_total_percent, reverse=True)
  for ct in nation.cities:
    logging.debug(f'{ct}.')
    logging.debug(f'defense_total_percent {ct.defense_total_percent}. defense_total_percent {ct.defense_total_percent}.')
    logging.debug(f'initial units {len(ct.units)}.')
    if ct.defense_total_percent > 200:
      units = [i for i in ct.nation.get_free_units()
               if i.city == ct]
      logging.debug(f'final units {len(units)}.')
      units.sort(key=lambda x: x.units)
      units.sort(key=lambda x: x.ranking)
      units.sort(key=lambda x: x.mp[1] >= 2 or (x.can_fly or x.forest_survival or x.mountain_survival or x.swamp_survival), reverse=True)
      if units: 
        units[0].scout = 1
        msg = f'{units[0]} es explorador.'
        logging.debug(msg)
        units [0].log[-1] += [msg]
        
        return



def ai_attack(nation, info=0):
  logging.info(f'ai_attack')
  if nation.expanding or nation.seen_nations == []: return
  if info: sp.speak(f' atacando.', 1)
  [i.update(nation) for i in nation.map]
  nation.set_seen_nations()
  nation.status()
  logging.debug(f'defense mean {nation.defense_mean}. attack factor {nation.attack_factor}.')
  if nation.defense_mean < nation.attack_factor: return
  nation.get_groups()
  nation.status()
  
  nation.capture = 0
  nation.stalk = 0
  for i in nation.groups:
    if i.goal[0] == capture_t: nation.capture += 1
    if i.goal[0] == stalk_t: nation.stalk += 1
  can_stalk = nation.defense_mean // nation.stalk_rate - nation.stalk
  can_capture = nation.defense_mean // nation.capture_rate - nation.capture
  
  logging.debug(f'capture {nation.capture}, stalk {nation.stalk}.')
  nation.seen_nations.sort(key=lambda x: x.score)
  for nt in nation.seen_nations:
    logging.debug(f'stalk a {nt}.')
    logging.debug(f'seen tiles {len(nt.seen_tiles)}.')
    logging.debug(f'seen units {len(nt.seen_units)}.')
    logging.debug(f'seen cities {len([c for c in nt.seen_tiles if c.is_city])}.')
    logging.debug(f'score {nt.score}.')
    shuffle(nt.seen_tiles)
    nt.seen_tiles.sort(key=lambda x: x.around_forest, reverse=1)
    nt.seen_tiles.sort(key=lambda x: x.around_hill, reverse=1)
    if basics.roll_dice(1) >= 5:
      nt.seen_tiles.sort(key=lambda x: x.hill, reverse=True)
    # stalk.
    for t in nt.seen_tiles:
      logging.debug(f'can_stalk {can_stalk}.')
      if can_stalk < 1: break
      units = nation.get_free_units()
      units = [i for i in units if i.comm == 0
               and i.pos.get_distance(i.pos, t) <= 3]
      logging.debug(f'{len(nation.units_free)} unidades disponibles.')
      if len(units) == 0: break
      units.sort(key=lambda x: x.ranking)
      if t.surf.name == forest_t: units.sort(key=lambda x: x.forest_survival, reverse=True) 
      if t.surf.name == swamp_t: units.sort(key=lambda x: x.swamp_survival, reverse=True)
      if t.hill: 
        units.sort(key=lambda x: x.mountain_survival, reverse=True)
        units.sort(key=lambda x: x.rng + x.rng_mod > 5, reverse=True)
      units.sort(key=lambda x: x.mp[1] >= 2)
      itm = units[0]
      if any(i for i in [itm.can_burn, itm.can_raid]):
        itm.create_group(itm.ranking)
      itm.goal = [stalk_t, t]
      if itm.group: itm = set_group(itm) 
      move_set(itm, t)
      can_stalk -= 1
  
    # capture.
    tiles = [i for i in nt.seen_tiles]
    [i.update(nation) for i in tiles]
    tiles = [i for i in tiles 
             if i.sight and (i.bu or i.is_city)]
    tiles.sort(key=lambda x: len(x.buildings), reverse=True) 
    tiles.sort(key=lambda x: mean([x.threat, x.around_threat]))
    for t in tiles:
      logging.debug(f'can_capture {can_capture}.')
      if can_capture < 1: break
      units = nation.get_free_units()
      units = [i for i in units if i.pos.city 
               and i.pos.get_distance(i.pos.city.pos, t) <= 3
               and i.pos.around_threat == 0]
      comms = [i for i in units if i.comm] 
      logging.debug(f'unidades {len(nation.units_free)} comandantes {len(comms)}.')
      if len(units + comms) < 1: break 
      logging.debug(f'ranking de {t} {t.threat}')
      units.sort(key=lambda x: x.ranking, reverse=True)
      if comms:
        shuffle(comms) 
        itm = comms[0]
      else:
        units.sort(key=lambda x: x.pos.get_distance(x.pos, t)) 
        itm = units[0]
      threat = t.threat * 1.5
      if itm.comm: threat = threat * 3
      itm.create_group(threat)
      if itm.group_score > 30:
        itm.break_group() 
        continue
      itm.goal = [capture_t, t]
      if itm.comm == 0: itm = set_group(itm)
      move_set(itm, t)



def ai_building_upgrade(nation):
  logging.debug(f'ai_building_upgrade. gold {nation.gold}')
  init = time()
  upgradable = [bu for bu in nation.buildings if bu.is_complete and bu.upgrade]
  logging.debug(f'upgradable {len(upgradable)}.')
  upgrades = []
  for bu in upgradable: upgrades += bu.upgrade
  for ct in nation.cities:
    shuffle(ct.buildings)
    ct.status()
    flup = nation.food_limit_upgrades - ceil(10 * ct.pop / 100)
    logging.debug(f'{flup=:} {ct.food_probable=:}.')
    ct.buildings.sort(key=lambda x: military_t in x.tags, reverse=True)
    if ct.food_probable < flup:
      ct.buildings.sort(key=lambda x: x.food, reverse=True)
      logging.debug(f'sort by food.')
    [bu.update() for bu in ct.buildings]
    for bu in ct.buildings:
      gold_limit = ct.nation.upkeep
      if ct.food_probable < flup:
        gold_limit //= 2
        logging.debug(f'gold limit reduced to {gold_limit} by food needs.')
      if bu.pos.blocked == 0 and bu.upgrade and bu.is_complete:
        upgrade = choice(bu.upgrade)(nation, nation.cities[0].pos)
        logging.debug(f'{upgrade} gold {upgrade.gold}.')
        if ct.food_probable > flup and food_t in bu.tags:
          logging.debug(f'no nesecita actualizar comida.')
          continue
        if ct.nation.gold - upgrade.gold < gold_limit:
          logging.debug(f'limite de gasto. {gold_limit}.')
          continue
        if public_order_t in bu.tags and bu.pos.public_order > 50:
          logging.debug(f'unrest not need.')
          continue
        if bu.check_tile_req(bu.pos):
          set_upgrade(bu, upgrade)
        
  logging.debug(f'time elapses. {time()-init}.')
  return sum(up.gold for up in upgrades if military_t in up.tags) * 0.1



def ai_construct(nation):
  logging.info(f'construir edificios {nation} turno {world.turn}.. gold {nation.gold}')
  nation.cities.sort(key=lambda x: x.capital, reverse=True)
  nation.gold_upgrade_limit = ai_building_upgrade(nation)
  logging.debug(f'{nation.gold_upgrade_limit} limite de gastos.')
  for ct in nation.cities:
    init = time() 
    logging.debug(f'{ct}.')
    flbp = nation.food_limit_builds - ceil(10 * ct.pop / 100)  # food limit build + 20% pop.
    logging.debug(f'valance de food {ct.food_val}.')
    logging.debug(f'probable food {ct.food_probable}. {flbp =: }.')
    ct.update()
    buildings = [i(nation, None) for i in nation.av_buildings]
    buildings.sort(key=lambda x: x.resource_cost[0])
    if ct.food_probable < flbp or ct.buildings_food == []:
      logging.debug(f'necesita food.')
      buildings.sort(key=lambda x: x.food, reverse=True)
      buildings.sort(key=lambda x: x.resource_cost[1])
      ct.tiles.sort(key=lambda x: x.food, reverse=True)
    for bu in buildings:
      if bu.gold > nation.gold: continue
      logging.debug(f'{bu}, gold {bu.gold}.')
      gold_limit = nation.gold_upgrade_limit
      count = 1
      if len(ct.buildings_food) <= 3:count = 3
      if food_t in bu.tags:
        if ct.food_probable < flbp:
          gold_limit = 0
          logging.debug(f'food_limit_build lowered to 0 by food need.')
        if len(ct.buildings_food) < 3 and ct.capital:
          gold_limit = nation.upkeep * 2
          logging.debug(f'food_limit_build lowered to {nation.upkeep*2} by capital.')
        if ct.food_probable > flbp and nation.gold < bu.gold * 8: 
          logging.debug(f'no necesita comida.')
          continue
      
      ct.update()
      military = 0
      resource = 0
      
      # permitir o no la construcción de edificios militares.
      if military_t in bu.tags:
        if ct.food_probable * 1.5 > flbp and roll_dice(1) >= 6:
          military = 1
        if len(ct.buildings_military) == 0:
          logging.debug(f'sin edificio militar.')
          military = 1 
          gold_limit = nation.upkeep
      
      # permitir o no la construcción de edificios de recursos.
      if resource_t in bu.tags:
        gold_limit_res = nation.income - nation.upkeep
        gold_limit_res += nation.gold * 0.1
        res_factor = len(ct.buildings_res) * 600
        logging.debug(f'gold_limit_res {gold_limit_res}, res factor {res_factor}.')
        if (nation.income > 400
            and ct.defense_total_percent > 200 and len(ct.buildings_military_complete) > 1
            and gold_limit_res > res_factor): 
          resource = 1
        if ct.resource_total >= 18 and ct.food_probable < flbp:
          resource = 0
      
      # edificios de órden.
      if public_order_t in bu.tags and  any(i < 0 for i in [ct.public_order_total]): gold_limit = nation.upkeep * 2 
      if nation.gold - bu.gold <= gold_limit:
        logging.debug(f'limite de gold {gold_limit}.')
        continue
      if military_t in bu.tags and military == 0:
        logging.debug(f'militar no permitido.')
        continue
      if resource_t in bu.tags and resource == 0:
        logging.debug(f'no necesita recursos.')
        continue
      for t in ct.tiles:
        if t.size < 1 or bu.size > t.size: continue
        if any(i > 0 for i in [t.threat, t.around_threat]): continue
        t.update(nation)
        ct.update()
        if public_order_t in bu.tags and (t.public_order > 50 or t.pop == 0):
          logging.debug(f'no necesita orden.')
          continue

        bu.pos = t
        if bu.can_build():
          if (nation.gold - bu.gold <= gold_limit
              or bu.upkeep and bu.upkeep + nation.upkeep > nation.upkeep_limit):
            logging.debug(f'toca el mantenimiento.')
            continue
          for b in nation.av_buildings:
            if b.name == bu.name: building = b(t, nation) 
          ct.add_building(building, t)
          count -= 1
          gold_limit = nation.gold_upgrade_limit
          if count == 0 or military_t in bu.tag: break
  
    logging.debug(f'time elapses. {time()-init}.')



def ai_divide_units(nation):
  units = [i for i in nation.units 
           if i.can_join and i.goto == []
           and i.leader == None and i.group == []]
  for i in units:
    i.pos.update(i.nation)
    if i.pos.around_threat > i.ranking * 0.5: continue
    city = i.pos.city
    if city: city.set_defense()
    roll = basics.roll_dice(1)
    needs = 6 - i.squads
    if i.scout: needs -= 2
    if i.pos.hill or i.rng + i.rng_mod > 5: needs += 2
    if i.pos.food_need >= i.pos.food: needs = 2
    if city and city.around_threat > city.defense: needs += 3 
    if roll >= needs:
      i.split()



def ai_expand_city(city):
  '''buscará expandir la ciudad.'''
  logging.info(f'ai_expand_city {city}. gold {city.nation.gold}')
  city.nation.devlog[-1] += [f'expanding {city}']
  if city.buildings_military_complete == []: return 'not military buildings.'
  if len(city.tiles) >= 11 and len(city.buildings_military_complete) < 2: return 'lack of military buildings.'
  if len(city.tiles) >= 13 and len([b for b in city.buildings_military_complete if b.level == 2]) < 2: return 'lack of military buildings.'
  if city.seen_threat > 50 * city.defense_total / 100:
    msg = f'seen threat {city.seen_threat}. total defense {city.defense_total} hight threatss. to expand' 
    city.nation.devlog[-1] += [msg]
    return msg
  
  rnd = basics.roll_dice(1)
  if rnd >= 5: request = 'res'
  else: request = 'food'
  logging.debug(f'{request=:}, {rnd=:}.')
  
  # revisara requisitos extras.
  factor = 1000
  if len(city.tiles) >= 10: factor = (len(city.tiles) - 9) * city.nation.expansion
  
  defense_percent_need = 200
  if len(city.tiles) >= 11: defense_percent_need = 400
  if len(city.tiles) >= 13: defense_percent_need = 600
  if len(city.tiles) >= 15: defense_percent_need = 1000

  if request == 'food':
    logging.debug(f'request food.')
    tiles = city.get_tiles_food(city.tiles_near)
    shuffle(tiles)
    tiles.sort(key=lambda x: x.food, reverse=True)
    tiles.sort(key=lambda x: x.get_distance(city.pos, x))
  elif request == 'res':
    logging.debug(f'request res.')
    tiles = city.get_tiles_res(city.tiles_near)
    shuffle(tiles)
    tiles.sort(key=lambda x: x.resource, reverse=True)
    tiles.sort(key=lambda x: x.get_distance(city.pos, x))
  tiles.sort(key=lambda x: len(x.around_snations), reverse=True)

  tiles = [t for t in tiles if t.blocked == 0]
  if tiles:
    msg = f'{tiles[0]}. {len(tiles)} tiles to expand.'
    logging.debug(msg)
    cost = city.nation.tile_cost
    distance = city.pos.get_distance(tiles[0], city.pos)
    cost = cost ** (city.nation.tile_power + distance / 10)
    cost = int(cost)
    logging.debug(f'costo {cost}')
    logging.debug(f'gold limit {factor}.')
    city.nation.devlog[-1] += [f'cost {cost} factor {factor}.']
    city.nation.devlog[-1] += [f'need defense {defense_percent_need}. total defense percent {city.defense_total_percent}']
    if tiles[0].threat + tiles[0].around_threat:
      msg = f'threat seen.'
      logging.debug(msg)
      city.nation.devlog[-1] += [msg]
      return
    if city.nation.gold - cost > factor and city.defense_total_percent >= defense_percent_need and tiles[0].threat + tiles[0].around_threat == 0:
      city.nation.gold -= cost
      city.tiles.append(tiles[0])
      tiles[0].city = city
      tiles[0].nation = city.nation
      msg = f'{city} se expandió a {tiles[0]}, {tiles[0].cords}. costo {cost}.'
      if city.nation.show_info: sp.speak(msg)
      nation.log[-1].append(msg)
      loadsound('warn3')
      return msg



def ai_explore(nation, scenary, info=0):
  logging.info('ai_explore {nation}. {world.turn= }..')
  if info:sp.speak(f' explorando.', 1)
  units = [it for it in nation.units if it.goto == [] and it.mp[0] > 0
           and it.ai and (it.scout or it.auto_explore)]
  if units: logging.debug(f'{len(units)} exploradores.')
  for uni in units:
    tries = 10
    while ((uni.mp[0] > 0 and uni.hp_total > 0 and uni.goto == [] and uni.city)
           and tries > 0):
      tries -= 1
      distanse = uni.mp[1] + uni.nation.explore_range
      sq1 = uni.city.pos.get_near_tiles(distanse)
      sq = uni.pos.get_near_tiles(1)
      sq = [it for it in sq if it.soil.name in uni.soil and it.surf.name in uni.surf
            and it in sq1 and it != uni.pos]
      [it.update(nation) for it in sq]
      if sq: random_move(uni, scenary, sq=sq)
      else:
        msg = f'sin lugar donde explorar'
        logging.debug(msg)
        sleep(1)



def ai_free_groups(nation, scenary):
  logging.info(f'ajuste de grupos')
  nation.get_groups()
  if nation.groups: logging.debug(f'grupos {len(nation.groups)}.')
  if nation.groups_free: logging.debug(f'grupos libres {len(nation.groups_free)}.')
  
  for itm in nation.groups_free:
    logging.debug(f'{itm} misión {itm.goal[0]} en {itm.goal[1]}.')
    itm.pos.update(itm.nation)
    # capture.
    if itm.goal[0] == capture_t:
      units = itm.group
      units.sort(key=lambda x: x.ranking)
      units.sort(key=lambda x: x.comm)
      if itm.group == []:
        logging.debug(f'{itm} sin grupo no mantiene casilla en {itm.pos} {itm.pos.cords}.')
        itm.break_group()
        return
      itm.pos.update(itm.pos.nation)      
      if  itm.goal[1] == itm.pos: itm.break_group()
      
    # stalk.
    if itm.goal[0] == stalk_t:
      roll = roll_dice(1)
      finish = 4
      if itm.pos.hill: finish -= 1
      if itm.pos.surf.name == forest_t: finish -= 1
      if (itm.pos.bu and itm.pos.nation != itm.nation
          and any(i for i in [itm.can_burn, itm.can_raid])):
        logging.debug(f'{itm} está en edificio enemigo ({itm.pos.building}. skip {finish}.')
        continue
      if itm.pos.around_threat > (itm.pos.defense + itm.pos.around_defense) * 1.5: finish += 3
      logging.debug(f'roll {roll}. finish {finish}.')
      if  roll < finish:
        logging.debug(f'{itm} se retira.')
        itm.break_group()



def ai_free_units(nation, scenary, info=1):
  logging.info(f'unidades libres.')
  nation.get_free_units()
  for uni in nation.units_free:
    if uni.squads > 4 and uni.pos.around_threat + uni.pos.threat < uni.ranking * 0.3: 
      uni.split(1)
      logging.debug(f'splits.')
  nation.get_free_units()
  if nation.units_free and info: logging.debug(f'{len(nation.units_free)} unidades libres.')
  nation.units.sort(key=lambda x: x.ranking, reverse=True)
  banned_tiles = []
  for uni in nation.units_free:
    if info: logging.debug(f'{uni}. ranking {uni.ranking} en {uni.pos} {uni.pos.cords}.')
    msg = f'free moves in {uni.pos} {uni.pos.cords}.'
    uni.log[-1] += [msg]
    move = 1
    num = 1
    while uni.goto == [] and move and uni.mp[0] > 1:
      uni.pos.update(uni.nation)
      if uni.auto_attack:
        auto_attack(uni)
        uni.auto_attack = 0
        if uni.mp[0] < 1 or uni.hp_total < 1: continue
      if uni.pos.nation == uni.nation:
        oportunist_attack(uni)
        if any(i < 1 for i in [uni.mp[0], uni.hp_total]): break
      
      if uni.pos.nation != uni.nation:
        skip = 0
        msg = f'out of nation.'
        if info: logging.debug(msg)
        uni.log[-1] += [msg]
      elif uni.pos.food_need > uni.pos.food:
        skip = 1
        msg = f'lack of food ({uni.pos.food_need}, {uni.pos.food}).'
        if info: logging.debug(msg)
        uni.log[-1] += [msg]
      elif uni.pos.public_order < 60:
        skip = 6
        msg = f'low public order {uni.pos.public_order}.'
        if info: logging.debug(msg)
        uni.log[-1] += [msg]
      elif uni.pos.is_city:
        skip = 1
        msg = f'own city.'
        if info: logging.debug(msg)
        uni.log[-1] += [msg]
      elif uni.pos.nation == uni.nation and uni.pos.buildings:
        skip = 6
        msg = f'have buildings.'
        if info: logging.debug(msg)
        uni.log[-1] += [msg]
      elif uni.pos.nation == nation and uni.pos.bu == 0:
        skip = 2
        msg = f'not buildings.'
        if info: logging.debug(msg)
        uni.log[-1] += [msg]
        if ((uni.forest_survival or uni.rng > 5) 
            and uni.pos.surf.name == forest_t):
          skip += 3
          msg = f'forest survival.'
          if info: logging.debug(msg)
          uni.log[-1] += [msg]
        if uni.pos.hill: 
          skip += 3
          msg = f'with hills.'
          if info: logging.debug(msg)
          uni.log[-1] += [msg]
        if uni.pos.around_hill or uni.pos.around_forest:
          skip += 3
          msg = f'around hills or forests..'
          if info: logging.debug(msg)
          uni.log[-1] += [msg]
      
      roll = basics.roll_dice(1)
      if info: logging.debug(f'roll {roll}, skip {skip}.')
      if skip >= roll:
        msg = f'salta.'
        if info: logging.debug(msg)
        uni.log[-1] += [msg]
        break
      sq = uni.pos.get_near_tiles(num)
      sq = [it for it in sq if it.soil.name in uni.soil and it.surf.name in uni.surf
            and it != uni.pos and it.nation == uni.nation and it not in banned_tiles]
      msg = f'num {num} tiles {len(sq)}.'
      if info: logging.debug(msg)
      uni.log[-1] += [msg]
      num += 1
      if num == 5:
        msg = f'no tiles found.'
        if info: logging.debug(msg)
        uni.log[-1] += [msg]
        move_set(uni, uni.city.pos)
        return
      [it.set_around(nation) for it in sq]
      shuffle(sq)
      sq.sort(key=lambda x: x.around_forest, reverse=True)
      sq.sort(key=lambda x: x.around_hill, reverse=True)
      sq.sort(key=lambda x: x.hill and x.defense == 0, reverse=True)
      sq.sort(key=lambda x: len(x.buildings) and x.defense == 0, reverse=True)
      sq.sort(key=lambda x: x.public_order, reverse=True,)
      if uni.rng + uni.rng_mod > 5: 
        sq.sort(key=lambda x: x.hill or (x.surf and x.surf.name == forest_t) and x.defense == 0, reverse=True)
      sq.sort(key=lambda x: x.defense_req - x.defense, reverse=True)
      sq.sort(key=lambda x: uni.get_favland(x), reverse=True)
      sq.sort(key=lambda x: x.food - x.food_need > uni.food * uni.units, reverse=True,)
      for s in sq:
        rnd = uni.ranking * uniform(0.75, 1.25)
        if s.food_need + (uni.food * uni.units) > s.food:
          if info: logging.debug(f'food needs')
          continue
        if s.bu: rnd += rnd * 0.3
        if s.cost > uni.mp[0]: move = 0
        elif s.cost <= uni.mp[0]: move = 1
        if info: logging.debug(f'defense {s.defense} rnd {rnd} threat {s.threat}. {s} {s.cords}.')
        if rnd > s.threat:
          if info: logging.debug(f'se moverá.')
          move_set(uni, s)
          num -= 1
          banned_tiles += [s]
          break



def ai_garrison(nation, info=0):
  logging.info(f'acciones de unidades en guarnición.')
  nation.devlog[-1] += [f'acciones de unidades en guarnición.']
  nation.update(nation.map)
  banned = []
  # unidades ranged.
  if info: logging.debug(f'unidades iniciales {len([i for i in nation.units if i.garrison])}.')
  nation.devlog[-1] += [f'unidades iniciales {len([i for i in nation.units if i.garrison and i.pos.around_threat+i.pos.threat])}.']
  # joining forces.
  for uni in [i for i in nation.units if i.garrison and i.pos.around_threat + i.pos.threat]:
    if uni.hp_total < 1: continue
    nation.devlog[-1] += [f'{uni} in {uni.pos} {uni.pos.cords}.']
    sq = uni.pos.get_near_tiles(1)
    [s.update(uni.nation) for s in sq]
    sq = [s for s in sq if s.threat]
    for s in sq:
      rnd = uni.ranking
      msg = f'ranking {rnd}.'
      nation.devlog[-1] += [msg]
      if info: logging.debug(msg)
      moves = max(i.moves + i.moves_mod for i in s.units if i.hidden == 0 and i.nation != uni.nation)
      rng = max(i.rng + i.rng_mod for i in s.units if i.hidden == 0 and i.nation != uni.nation)
      if info: logging.debug(f'rnd inicial {rnd}.')
      if s.around_threat: 
        rnd *= 0.8
        msg = f'reduced by around_threat to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if uni.comm: 
        rnd *= 0.6
        msg = f'reduced by comm to {rnd}.'
        nation.devlog[-1] += {msg} 
        if info: logging.debug(msg) 
      if uni.dark_vision == 0 and uni.pos.day_night:
        rnd *= 0.6
        msg = f'reduced by dark vision.'
        nation.devlog[-1] += {msg} 
        if info: logging.debug(msg)
      if uni.forest_survival and s.surf.name != forest_t: 
        rnd *= 0.8 
        msg = f'reduced by not forest tile to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if uni.swamp_survival and s.surf.name != swamp_t: 
        rnd *= 0.8
        msg = f'reduced by not swamp tile to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if uni.mountain_survival and s.hill == 0: 
        rnd *= 0.8
        msg = f'reduced by not mountaint tile to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if mounted_t in uni.traits and s.surf.name in [forest_t, swamp_t] or s.hill: 
        rnd *= 0.5
        msg = f'reduced by forest or hill or swamp to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if uni.forest_survival == 0 and s.surf.name in [forest_t]:
        rnd *= 0.5
        msg = f'reduced by forest to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if uni.swamp_survival == 0 and s.surf.name in [swamp_t]:
        rnd *= 0.5
        msg = f'reduced by swamp to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if uni.mountain_survival == 0 and s.hill:
        rnd *= 0.5
        msg = f'reduced by hill to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if moves > uni.moves + uni.moves_mod:
        rnd *= 0.7
        msg = f'reduced by hight moves to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if (rng >= 6 and uni.rng + uni.rng_mod < rng 
          and uni.shield == None and uni.armor == None):
        rnd *= 0.6
        msg = f'reduced by rng{rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if s.nation != nation: 
        rnd *= 0.8
        msg = f'reduced by not nation tile.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if s.nation != nation and s.nation:
        rnd *= 0.8
        msg = f'reduced by other nation tile to {rnd} and nation.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      max_ranking = max(i.ranking for i in s.units if i.revealed)
      nation.devlog[-1] += [f'rnd {rnd} max_ranking {max_ranking}.']
      if rnd * 0.8 < max_ranking: 
        msg = f'joining forces.'
        nation.devlog[-1] += [msg]
        if info: logging.debug(msg)
        if rnd * 0.8 < max_ranking: basics.ai_join_units(uni, count=1)
        elif max_ranking > rnd * 1.5: basics.ai_join_units(uni, count=2)
        elif max_ranking > rnd * 2: basics.ai_join_units(uni, count=4)
        elif max_ranking > rnd * 3: basics.ai_join_units(uni, count=20)
  
  units = [it for it in nation.units if it.garrison and it.rng + it.rng_mod >= 6
           and it.comm == 0 and it.pos.around_threat + it.pos.threat and it.mp[0] >= 2]
  if info: logging.debug(f'unidades ranged. {len(units)}.')
  nation.devlog[-1] += [f'unidades ranged. {len(units)}.']
  units.sort(key=lambda x: x.ranking)
  units.sort(key=lambda x: x.mp[0], reverse=True)
  units.sort(key=lambda x: x.rng + x.rng_mod, reverse=True)
  
  for uni in units:
    rnd = uni.ranking * uniform(1.3, 0.7)
    if rnd >= uni.pos.threat: auto_attack(uni)
    if uni.hp_total < 1: continue
    sq = uni.pos.get_near_tiles(1)
    sq = [s for s in sq if s.soil.name in uni.soil and s.surf.name in uni.surf
            and s != uni.pos and s.threat > 0]
    sq.sort(key=lambda x: x.threat)
    for s in sq:
      s.update(uni.nation)
      if s.threat < 1 or s in banned: continue
      if uni.pos.is_city:
        uni.pos.city.set_defense()
        if uni.pos.defense < uni.pos.around_threat * 2:
          if info: logging.debug(f'pocas unidades..')
          continue
      rnd = uni.ranking * uniform(1.1, 0.9)
      msg = f'initial rnd {rnd}.'
      nation.devlog[-1] += [msg]
      if info: logging.debug(msg)
      local_defense = sum(i.ranking for i in uni.pos.units if uni.garrison)
      if s.nation == uni.nation: local_defense *= 0.5
      moves = max([i.moves + i.moves_mod for i in s.units if i.hidden == 0])
      rng = max(i.rng + i.rng_mod for i in s.units if i.hidden == 0 and i.nation != uni.nation)
      if info: logging.debug(f'rnd inicial {rnd}.')
      if s.around_threat: 
        rnd *= 0.8
        msg = f'reduced by around_threat to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if uni.comm: 
        rnd *= 0.6
        msg = f'reduced by comm to {rnd}.'
        nation.devlog[-1] += {msg} 
        if info: logging.debug(msg) 
      if uni.dark_vision == 0 and uni.pos.day_night:
        rnd *= 0.6
        msg = f'reduced by dark vision.'
        nation.devlog[-1] += {msg} 
        if info: logging.debug(msg)
      if uni.forest_survival and s.surf.name != forest_t: 
        rnd *= 0.8 
        msg = f'reduced by not forest tile to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if uni.swamp_survival and s.surf.name != swamp_t: 
        rnd *= 0.8
        msg = f'reduced by not swamp tile to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if uni.mountain_survival and s.hill == 0: 
        rnd *= 0.8
        msg = f'reduced by not mountaint tile to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if mounted_t in uni.traits and s.surf.name in [forest_t, swamp_t] or s.hill: 
        rnd *= 0.5
        msg = f'reduced by forest or hill or swamp to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if uni.forest_survival == 0 and s.surf.name in [forest_t]:
        rnd *= 0.5
        msg = f'reduced by forest to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if uni.swamp_survival == 0 and s.surf.name in [swamp_t]:
        rnd *= 0.5
        msg = f'reduced by swamp to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if uni.mountain_survival == 0 and s.hill:
        rnd *= 0.5
        msg = f'reduced by hill to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if moves > uni.moves + uni.moves_mod:
        rnd *= 0.7
        msg = f'reduced by hight moves to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if s.nation != nation: 
        rnd *= 0.8
        msg = f'reduced by not nation tile.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if s.nation != nation and s.nation:
        rnd *= 0.8
        msg = f'reduced by other nation tile to {rnd} and nation.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      max_ranking = max(i.ranking for i in s.units if i.revealed)
      if info: logging.debug(f'{uni} rnd {round(rnd)}, trheat {s.threat}.')
      if info: logging.debug(f'max ranking {max_ranking}.')
      nation.devlog[-1] += [f'{uni} rnd {round(rnd)} max ranking {round(max_ranking)}.']
      nation.devlog[-1] += [f'local_defense{local_defense} a threat {s.around_threat}.']
      if (rnd > max_ranking and local_defense > s.around_threat):
        msg = f'garrison attack to {s} {s.cords}. '
        msg += f'rnd {rnd}, threat {s.threat}, around threat {s.around_threat}.'
        nation.devlog[-1] += [msg]
        move_set(uni, s)
        move_set(uni, 'attack')
        if uni.ranking > (s.threat + s.around_threat) * 3: banned += [s]
        break
  
  units = [it for it in nation.units if it.garrison == 1
           and it.scout == 0 and it.settler == 0 and it.comm == 0
           and it.rng + it.rng_mod <= 6 and it.mp[0] >= 2
           and it.pos.around_threat + it.pos.threat]
  if info: logging.debug(f'unidades melee. {len(units)}.')
  nation.devlog[-1] += [f'unidades melee. {len(units)}.']
  # unidades mele.
  shuffle(units)
  units.sort(key=lambda x: x.ranking, reverse=True)
  if basics.roll_dice(1) >= 4: units.sort(key=lambda x: x.pos.is_city)
  for uni in units:
    rnd = uni.ranking * uniform(1.3, 0.7)
    if rnd >= uni.pos.threat: auto_attack(uni)
    if uni.hp_total < 1: continue
    sq = uni.pos.get_near_tiles(1)
    sq = [s for s in sq if s.soil.name in uni.soil and s.surf.name in uni.surf
            and s != uni.pos and s.threat > 0]
    sq.sort(key=lambda x: x.threat)
    for s in sq:
      s.update(nation)
      if s.threat < 1 or s in banned: continue
      if uni.pos.is_city:
        uni.pos.city.set_defense()
        if uni.pos.defense < uni.pos.around_threat * 1.5:
          if info: logging.debug(f'pocas unidades..')
          continue
      nation.devlog[-1] += [f'{uni} in {uni.pos} {uni.pos.cords}.']
      defense = uni.ranking
      rnd = uni.ranking * uniform(1.1, 0.9)
      msg = f'initial rnd {rnd}.'
      nation.devlog[-1] += [msg]
      if info: logging.debug(msg)
      local_defense = sum(i.ranking for i in uni.pos.units if uni.garrison)
      if s.nation == uni.nation: local_defense *= 0.5
      moves = max(i.moves + i.moves_mod for i in s.units if i.hidden == 0 and i.nation != uni.nation)
      rng = max(i.rng + i.rng_mod for i in s.units if i.hidden == 0 and i.nation != uni.nation)
      if info: logging.debug(f'rnd inicial {rnd}.')
      if s.around_threat: 
        rnd *= 0.8
        msg = f'reduced by around_threat to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if uni.comm: 
        rnd *= 0.6
        msg = f'reduced by comm to {rnd}.'
        nation.devlog[-1] += {msg} 
        if info: logging.debug(msg) 
      if uni.dark_vision == 0 and uni.pos.day_night:
        rnd *= 0.6
        msg = f'reduced by dark vision.'
        nation.devlog[-1] += {msg} 
        if info: logging.debug(msg)
      if uni.forest_survival and s.surf.name != forest_t: 
        rnd *= 0.8 
        msg = f'reduced by not forest tile to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if uni.swamp_survival and s.surf.name != swamp_t: 
        rnd *= 0.8
        msg = f'reduced by not swamp tile to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if uni.mountain_survival and s.hill == 0: 
        rnd *= 0.8
        msg = f'reduced by not mountaint tile to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if mounted_t in uni.traits and s.surf.name in [forest_t, swamp_t] or s.hill: 
        rnd *= 0.5
        msg = f'reduced by forest or hill or swamp to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if uni.forest_survival == 0 and s.surf.name in [forest_t]:
        rnd *= 0.5
        msg = f'reduced by forest to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if uni.swamp_survival == 0 and s.surf.name in [swamp_t]:
        rnd *= 0.5
        msg = f'reduced by swamp to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if uni.mountain_survival == 0 and s.hill:
        rnd *= 0.5
        msg = f'reduced by hill to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if moves > uni.moves + uni.moves_mod:
        rnd *= 0.75
        msg = f'reduced by hight moves to {rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if (rng >= 6 and uni.rng + uni.rng_mod < rng 
          and uni.shield == None and uni.armor == None):
        rnd *= 0.6
        msg = f'reduced by rng{rnd}.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if s.nation != nation: 
        rnd *= 0.8
        msg = f'reduced by not nation tile.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      if s.nation != nation and s.nation:
        rnd *= 0.8
        msg = f'reduced by other nation tile to {rnd} and nation.'
        nation.devlog[-1] += {msg}
        if info: logging.debug(msg)
      max_ranking = max(i.ranking for i in s.units if i.hidden == 0)
      if info: logging.debug(f'{uni} rnd {round(rnd)}, trheat {s.threat}.')
      if info: logging.debug(f'max ranking {max_ranking}.')
      nation.devlog[-1] += [f'{uni} rnd {round(rnd)} max ranking {round(max_ranking)}.']
      if (rnd > max_ranking and local_defense > s.around_threat 
          and uni.mp[0] >= 2):
        if uni.ranking > (max_ranking + s.around_threat) * 2.5: uni.split(1)
        elif uni.ranking > (max_ranking + s.around_threat) * 4: uni.split(1)
        msg = f'garrison attack to {s} {s.cords}. '
        msg += f'rnd {rnd}, threat {s.threat}, around threat {s.around_threat}.'
        nation.devlog[-1] += [msg]
        move_set(uni, s)
        move_set(uni, 'attack')
        if uni.ranking > (s.threat + s.around_threat) * 3: banned += [s]
        break



def ai_get_extra_units(defense_req, nation):
  logging.info(f'extra unidades. requiere {defense_req}.')
  for ct in nation.cities:
    defense = ct.pos.defense
    logging.debug(f'defensa en {ct} {defense.defense} amenaza {ct.pos.around_threat}.')
    for uni in ct.pos.units:
      if ct.pos.defense - uni.ranking > ct.pos.around_threat and defense_req > 0:
        uni.garrison = 0
        defense_req -= uni.ranking
        logging.debug(f'{uni} ya no es guarnición en {ct}. requiere {defense_req}.')



def ai_hero_move(nation):
  logging.info(f'commander move.')
  units = [i for i in nation.units if i.comm and i.mp[0] > 0 and i.hp_total >= 1]
  for uni in units:
    goto = None
    if uni.goto: 
      for r in range(len(uni.goto) - 1, 0, -1):
        if isinstance(uni.goto[r][1], str) == False: goto = uni.goto[r][1]
      if goto and goto.threat + goto.threat == 0:
        msg = f'stops moving to {goto} {goto.cords}.'
        logging.debug(msg)
        uni.log[-1] += [msg]
        uni.goto = []

  for uni in units:
    # combat.
    ranking = uni.ranking * 0.8
    if uni.pos.threat < ranking:
      auto_attack(uni)
    
    # moves.
    if uni.pos.nation == uni.nation:
      oportunist_attack(uni)
      if any(v < 1 for v in [uni.mp[0], uni.hp_total]): continue
      sq = uni.pos.city.tiles
      sq = [s for s in sq if uni.can_pass(s) and s.nation == uni.nation]
      sq.sort(key=lambda x: len(x.buildings), reverse=True)
      sq.sort(key=lambda x: uni.pos.get_distance(x, uni.pos))
      if 'healer' in uni.spells_tags: sq.sort(key=lambda x: intoxicated_t in x.units_effects)
      if 'leader' in uni.skills_tags: sq.sort(key=lambda x: x.around_threat + x.threat and x.defense, reverse=True)
      logging.debug(f'casillas {len(sq)}.')
      for t in sq:
        if uni.ranking + t.defense > t.around_threat:
          msg = f'heading to {t} {t.cords}. defense {t.defense}, around threat {t.around_threat}.'
          logging.debug(msg)
          uni.log[-1] += [msg]
          move_set(uni, t)
          move_set(uni, 'attack')
          break
      
    # return to home.
    elif uni.pos.nation != uni.nation and uni.goal == None:
      num = 1
      while True:
        sq = uni.pos.get_near_tiles(num)
        set_favland(uni, sq)
        logging.debug(f'tiles {len(sq)} num {num}.')
        num += 1
        for t in sq:
          logging.debug(f'{uni} ranking {uni.ranking}, threat {t.around_threat+t.threat}.')
          if uni.ranking + t.defense > t.around_threat + t.threat and t.nation == uni.nation:
            move_set(uni, t)
            return



def ai_move_group(itm, info=0):
  logging.info(f'move group turn {world.turn}.')
  if info: logging.debug(f'{itm} {itm.id} at {itm.pos} {itm.pos.cords}..')
  if info: logging.debug(f'goal {itm.goal[0]} to {itm.goal[1]}.')
  if info: logging.debug(f'leads {len(itm.group)} units.')
  group = [str(i) for i in itm.group]
  if itm.group: logging.debug(f'{group}.')
  goto = itm.goto[0][1]
  goto.update(itm.nation)

  itm.pos.update(nation)
  ranking = sum([i.ranking for i in [itm] + itm.group])
  threat = goto.threat
  if goto.hill and mountain_survival_t not in itm.traits: threat *= 1.10
  if goto.surf.name == forest_t and forest_survival_t not in itm.traits: threat *= 1.10
  if goto.surf.name == swamp_t and swamp_survival_t not in itm.traits: threat *= 1.10
  if info: logging.debug(f'ranking {round(ranking)} vs {round(threat)}.')

  alt = goto.get_near_tiles(1)
  alt = [i for i in alt
        if i.get_distance(i, itm.pos) == 1]
  [s.update(itm.nation) for s in alt]
  alt.sort(key=lambda x: x.income, reverse=True)
  alt.sort(key=lambda x: x.bu, reverse=True)
  alt.sort(key=lambda x: x.threat)
  if itm.forest_survival: alt.sort(key=lambda x: x.surf.name == forest_t, reverse=True)
  if itm.swamp_survival: alt.sort(key=lambda x: x.surf.name == swamp_t, reverse=True)
  if itm.mountain_survival: alt.sort(key=lambda x: x.hill, reverse=True)
  defense_roll = 5
  if itm.comm: defense_roll -= 2
  if basics.roll_dice(1) >= defense_roll: 
    alt.sort(key=lambda x: x.hill and x.threat < ranking, reverse=True)

  if itm.goal[0] == base_t:
    itm.break_group()
    return
  if itm.goal[0] == capture_t:
    if goto.threat > ranking * uniform(0.8, 1.2):
      if info: logging.debug(f'mayor.')
      if basics.roll_dice(1) > 2:
        if info: logging.debug(f'wait next turn.') 
        return
      
      else:
        if info: logging.debug(f'switch goto.')
        for s in alt:
          if s.threat < itm.group_ranking:
            if (itm.day_night 
                and (s.nation != itm.nation and s.nation != None)
                and basics.roll_dice(1) >= 3):
              if info: logging.debug(f'will avoid hills by night.')
              continue
            if info: logging.debug(f'changes to {s} {s.cords}.')
            move_set(itm, s)
            return
      
      if basics.roll_dice(1) > 4:
        if info: logging.debug(f'{itm} go home.')
        go_home(itm)
        return
    [move_set(i, itm.goal[1]) for i in itm.group]
    goto.update(goto.nation)
    itm.update()
    if itm.comm and goto.threat <= itm.ranking: moving_unit(itm)
    else:
      if itm.group == []:
        if info: logging.debug(f'lider se retira..') 
        itm.break_group()
      return
  if itm.goal[0] == stalk_t:
    if itm.rng + itm.rng_mod > 5 and itm.pos.day_night: ranking *= 0.2
    if ranking * 1.5 < threat:
      if info: logging.debug(f'mayor.')
      if basics.roll_dice(2) >= 10:
        if info: logging.debug(f'ataca.')
        if basics.roll_dice(1) >= 3: itm.group.sort(key=lambda x: x.rng + x.rng_mod > 5, reverse=True)
        for i in itm.group:
          if i.goto == []: move_set(i, goto)
        goto.update(itm.nation)
        itm.update()
        if goto.threat <= itm.ranking * 1.25:
          if info: logging.debug(f'lider mueve. threat {goto.threat} ranking {itm.ranking*1,5}.') 
          moving_unit(itm)
          return
        if itm.group: 
          if info: logging.debug(f'espera grupo.')
          return
        else:
          if info: logging.debug(f'lider se retira.')
          itm.break_group()
          itm.goal = None
          itm.goto = []
          return
      roll = 2
      if itm.pos.hill: roll += 1
      if itm.pos.surf.name == forest_t: roll += 1
      if itm.pos.surf.name == swamp_t: roll += 1
      if info: logging.debug(f'switch chanse {roll}.')
      if basics.roll_dice(1) >= roll:
        if info: logging.debug(f'will move.')
        for s in alt:
          if info: logging.debug(f'{s.threat =: }. {s} {s.cords}.')
          if s.threat < itm.group_ranking * 0.7:
            if (itm.day_night 
                and (s.nation != itm.nation and s.nation != None)
                and boasics.roll_dice(1) >= 3):
              if info: logging.debug(f'will avoid hills by night.')
              continue
            if info: logging.debug(f'moves to {s} {s.cords}.')
            move_set(itm, s)
            return
        if info: logging.debug(f'espera.')
        return 
      if basics.roll_dice(1) >= 4:
        if info: logging.debug(f'espera')
        return
      itm.break_group()
      return
    else:
      if info: logging.debug(f'just moves.')
      for i in itm.group:
        if i.goto == []: i.goto = [g for g in itm.goto]
      for i in itm.group:
        moving_unit(i)
      goto.update(itm.nation)
      moving_unit(itm)



def ai_play(nation):
  logging.info(f'{turn_t} {of_t} {nation}. ai = {nation.ai}, info = {nation.show_info}.')
  init = time()
  sp.speak(f'{nation}.')
  # ingresos.
  nation.set_income()
  print(f'{nation} nation.set_income {time()-init}.')
  nation.set_hidden_buildings()
  
  # ciudades.
  for ct in nation.cities:
    ct.population_change()
    ct.set_downgrade()
    ct.set_upgrade()
    ct.check_training()
    ct.check_building()
    ct.status()
    ct.set_seen_units(new=1)
    ct.set_av_units()
  print(f'cities {time()-init}.')  
  
  # units.
  logging.debug(f'movimiento de unidades.')
  nation.update(scenary)
  for uni in nation.units:
    unit_new_turn(uni)
  print(f'units {time()-init}.')
  
  # actualizar vista.
  if nation.map == []:
    map_update(nation, scenary)
  else: 
    map_update(nation, nation.map)
  print(f'nation updates {time()-init}.')
  nation.set_seen_nations()
  print(f'seen nations {time()-init}.')
  # parametros de casillas cercanas.
  set_near_tiles(nation, scenary)
  # initial placement.
  #if nation.cities == [] and world.turn == 1: 
    #nation_start_placement(nation)
  #nation.update(nation.map)
  # colonos.
  logging.debug(f'colonos {len([i for i in nation.units if i.settler])}.')
  [set_settler(it, scenary) for it in nation.units if it.settler and it.goto == []]
  # liberar unidades de edificios que no son amenazados.
  ai_set_free_units(nation)
  print(f'ai_set_free units {time()-init}.')
  # entrenar colonos.
  ai_add_settler(nation)
  print(f'ai_add_settler {time()-init}.')
  # train commanders
  ai_train_comm(nation)
  print(f'ai_train_comm {time()-init}.')
  # entrenar unidades.
  ai_train(nation)
  print(f'ai_train {time()-init}.')
  # edificios.
  [nation.improve_military(ct) for ct in nation.cities]
  print(f'improve_military {time()-init}.')
  [nation.build(ct) for ct in nation.cities]
  print(f'nation.build {time()-init}.')
  [nation.improve_misc(ct) for ct in nation.cities]
  print(f'nation.improve_misc {time()-init}.')
  [nation.improve_food(ct) for ct in nation.cities]
  print(f'nation.improve_food {time()-init}.')
  # expandir ciudad.
  for ct in nation.cities: ai_expand_city(ct)
  print(f'expand city {time()-init}.')
  # asignar unidades a proteger casillas.
  ai_protect_tiles(nation)
  print(f'ai_protect_tiles {time()-init}.')
  # acciones de unidades en guarnición.
  ai_garrison(nation)
  print(f'ai_garrison {time()-init}.')
  # commander.
  ai_hero_move(nation)
  print(f'ai_hero_moves {time()-init}.')
  ai_unit_cast(nation)
  print(f'ai_unit_cast {time()-init}.')
  # liberar unidades de edificios que no son amenazados.
  # ai_set_free_units(nation)
  print(f'ai_set_free {time()-init}.')
  # agregar exploradores.
  ai_add_explorer(nation)
  print(f'ai_add_explorer {time()-init}.')
  # explorar
  ai_explore(nation, scenary)
  print(f'ai_explore {time()-init}.')
  # atacar.
  ai_attack(nation)
  print(f'ai_attack {time()-init}.')
  # grupos.
  ai_free_groups(nation, scenary)
  print(f'ai_free_group {time()-init}.')
  # unidades libres.
  ai_free_units(nation, scenary)
  print(f'ai_free_units {time()-init}.')
  # commander move again.
  ai_hero_move(nation)
  print(f'ai_hero_moves {time()-init}.')
  ai_unit_cast(nation)
  print(f'ai_unit_cast {time()-init}.')
  # desbandando unidades.
  ai_unit_disband(nation)
  print(f'ai_disband {time()-init}.')



def ai_protect_cities(nation):
  logging.info(f'proteger aldeas {nation} turno {world.turn}..')
  init = time()
  for ct in nation.cities:
    garrison = [i for i in ct.pos.units if i.garrison]
    logging.debug(f'quedan {len(garrison)}')
    nation.devlog[-1] += [f'quedan {len(garrison)}']
    if len(garrison) == 1:
      logging.debug(f'splited.')
      nation.devlog[-1] += [f'splited.']
      ct.pos.units[0].split()
    ct.set_seen_units()
    ct.set_defense()
    defense_need = ct.defense_need
    logging.debug(f'defense_min {ct.defense_min}, defense {ct.defense}.')
    nation.devlog[-1] += [f'defense_min {ct.defense_min}, defense {ct.defense}.']
    logging.debug(f'{ct} defense_need {defense_need}')
    nation.devlog[-1] += [f'{ct} defense_need {defense_need}']
    if defense_need < 0 and roll_dice(1) >= 6 and ct.around_threat == 0: 
      ct.units.sort(key=lambda x: x.squads, reverse=True)
      if ct.pos.units[0].squads >= 5: 
        ct.pos.units[0].split()
        ct.pos.units[-1].garrison = 0 
        ct.set_defense()
        defense_need = ct.defense_need
    if ct.defense_need < -30:
      logging.debug(f'sobra defensa {defense_need}. {ct.defense}, {ct.defense_min}.')
      nation.devlog[-1] += [f'sobra defensa {defense_need}. {ct.defense}, {ct.defense_min}.']
      units = [i for i in ct.pos.units if i.garrison]
      times = round(abs(ct.defense_need) / 20)
      for r in range(times):
        logging.debug(f'divide {r} de {times}.')
        units.sort(key=lambda x: x.units, reverse=True)
        units[0].split(6)
      for i in units:
        i.garrison = 0
      nation.update(scenary)
      ct.set_defense()
    
    logging.debug(f'defending {ct.defense}. defense_min {ct.defense_min}.')
    defense_need = ct.defense_need
    if defense_need > 10:
      logging.debug(f'necesita {defense_need}.')
      units = [it for it in ct.units if it.garrison == 0
               and it.scout == 0 and it.settler == 0
               and it.group == [] and it.leader == None
               and it.goal == None and it.goto == []]
               
      logging.debug(f'{len(units)} unidades disponibles.')
      nation.devlog[-1] += [f'{len(units)} unidades disponibles.']
      if units:
        logging.debug(f'busca en sus propias unidades.')
        nation.devlog[-1] += [f'busca en sus propias unidades.']
        units.sort(key=lambda x: x.pos.po, reverse=True)
        units.sort(key=lambda x: x.pos.income)
        units.sort(key=lambda x: levy_t not in x.traits, reverse=True)
        if ct.around_threat < ct.defense: 
          units.sort(key=lambda x: x.mp[1] < 3, reverse=True)
          units.sort(key=lambda x: x.comm == 0, reverse=True)
        units.sort(key=lambda x: x.rng + x.rng_mod >= 6 and x.units, reverse=True)
        units.sort(key=lambda x: x.comm)
        units.sort(key=lambda x: x.pos.get_distance(x.pos, ct.pos))
        units.sort(key=lambda x: x.pos.around_threat)
        logging.debug(f'unit list {[str(i) for i in units]}.')
        nation.devlog[-1] += [f'unit list {[str(i) for i in units]}.']
        for uni in units:
            defense_need = set_defend_pos(defense_need, uni, ct.pos)
            if defense_need == None:
              pass
            if defense_need <= 0: break
      
      if units == [] or defense_need > 0:
        logging.debug(f'buscará entre todas las unidades.')
        nation.devlog[-1] += [f'buscará entre todas las unidades.']
        units = [it for it in nation.units  if it.garrison == 0
                 and it.settler == 0 and it.scout == 0
                 and it.group == [] and it.leader == None
                 and it.goal == None and it.comm == 0 and it.goto == []]
        logging.debug(f'{len(units)} unidades disponibles.')
        nation.devlog[-1] += [f'{len(units)} unidades disponibles.']
        if units == []:
          logging.debug(f'no hay unidades.')
          nation.devlog[-1] += [f'no hay unidades.']
        units.sort(key=lambda x: x.rng >= 6, reverse=True)
        units.sort(key=lambda x: x.units, reverse=True)
        units.sort(key=lambda x: x.mp[0], reverse=True)
        units.sort(key=lambda x: x.comm)
        units.sort(key=lambda x: x.pos.around_threat)
        if ct.defense_total > ct.seen_threat: units.sort(key=lambda x: mounted_t in x.traits)
        units.sort(key=lambda x: x.pos.get_distance(x.pos, ct.pos))
        logging.debug(f'unit list {[str(i) for i in units]}.')
        nation.devlog[-1] += [f'unit list {[str(i) for i in units]}.']
        for uni in units:
          defense_need = set_defend_pos(defense_need, uni, ct.pos)
          if defense_need < 1: break

    garrison = [i for i in ct.pos.units if i.garrison]
    logging.debug(f'quedan {len(garrison)}')
    if len(garrison) == 1:
      logging.debug(f'splited.')
      ct.pos.units[0].split()
    logging.debug(f'time elapses. {time()-init}.')



def ai_protect_tiles(nation, info=0):
  logging.info(f'proteger casillas {nation} turno {world.turn}..')
  nation.devlog[-1] += [f'protect tiles.']
  init = time()
  shuffle(nation.tiles)
  [i.set_around(nation) for i in nation.tiles]
  nation.tiles.sort(key=lambda x: x.hill, reverse=True)
  nation.tiles.sort(key=lambda x: len(x.around_nations) > 0, reverse=True)
  nation.tiles.sort(key=lambda x: x.defense_req, reverse=True)
  nation.tiles.sort(key=lambda x: x.city.capital, reverse=True)
  nation.tiles.sort(key=lambda x: x.around_threat + x.threat, reverse=True)
  nation.tiles.sort(key=lambda x: x.is_city and x.around_threat + x.threat, reverse=True)
  nation.tiles.sort(key=lambda x: x.city.capital and x.is_city and x.around_threat + x.threat, reverse=True)
  for t in nation.tiles:
    if t.blocked: continue
    defense_needs = t.around_threat * 1.3
    if t.defense_req > defense_needs: defense_needs = t.defense_req
      
    defense = sum(u.ranking for u in t.units
                    if u.garrison == 1 and u.nation == nation)
    if defense < 80 * defense_needs / 100:
      msg = f'{t}. {t.cords} needs {defense_needs-defense} defense.'
      if info: logging.debug(msg)
      nation.devlog[-1] += [msg]
      if info: logging.debug(f'defensa {defense}, amenaza {t.around_threat}.')
      units = []
      ranking = 0
      if t.is_city == 0:sq = t.get_near_tiles(2)
      elif t.is_city: sq = t.get_near_tiles(3)
      sq = [s for s in sq if s != t and s.units]
      [i.set_around(nation) for i in sq]
      sq.sort(key=lambda x: x.get_distance(x, t))
      sq.sort(key=lambda x: x.hill)
      sq.sort(key=lambda x: x.surf.name in [forest_t, swamp_t])
      sq.sort(key=lambda x: x.around_threat + x.threat)
      for s in sq:
        if ranking >= 80 * defense_needs / 100:
          nation.devlog[-1] += [f'breaks tile checking by 80% defense.'] 
          break
        if s.units:nation.devlog[-1] += [f'check unit in {s.cords} a threat {s.around_threat}, threat {s.threat}']
        for u in s.units:
          if u.nation != nation or u.type == 'civil': continue
          if ranking >= 80 * defense_needs / 100:
            nation.devlog[-1] += [f'breaks unit checking by 80% defense.'] 
            break
          nation.devlog[-1] += [f'{u}, garrison {u.garrison}']
          if u.comm and t.is_city == 0:
            nation.devlog[-1] += [f'continues by unit comm and tile is not city.']
            continue
          if u.comm and t.is_city and t.around_threat + t.threat < 1:
            nation.devlog[-1] += [f'continues by unit comm and tile is city but no threats.']
            continue
          if s.is_city and s.city.capital and s.around_threat + s.threat:
            nation.devlog[-1] += [f'breaks by threat in capital.']
            continue
          if t.is_city and t.around_threat + t.threat == 0 and u.pos.around_threat + u.pos.threat and u.garrison: 
            nation.devlog[-1] += [f'breaks by threat.']
            continue
          if u.pos.is_city and u.garrison and len(u.pos.units) < 3:
            nation.devlog[-1] += [f'breaks by city less than 3 garrison..'] 
            continue
          if t.is_city == 0 and u.pos.around_threat + u.pos.threat and u.garrison:
            nation.devlog[-1] += [f'breakcs by unit defending.']
            continue
          if t.is_city == 0 and t.around_threat + t.threat == 0 and u.garrison:
            nation.devlog[-1] += [f'breakcs by not need defense'] 
            continue
          if t.is_city == 0 and u.pos.city != t.city and u.garrison:
            nation.devlog[-1] += [f'breakcs by unit not same city.'] 
            continue
          if (u.mp[0] >= 2 and u.group == [] 
              and u.leader == None and u.scout == 0 and u.settler == 0): 
              
            units += {u}
            ranking += u.ranking
            nation.devlog[-1] += [f'added.']
      if info: logging.debug(f'{len(units)} unidades disponibles iniciales.')
      if info: logging.debug(f'ranking total {ranking}')
      units.sort(key=lambda x: x.pos.around_threat + x.pos.threat)
      if t.surf.name == forest_t:
        units.sort(key=lambda x: x.forest_survival or x.rng + x.rng_mod >= 6, reverse=True)
        if info: logging.debug(f'sort to forest.')
      if t.surf.name == swamp_t:
        units.sort(key=lambda x: x.swamp_survival or x.rng + x.rng_mod >= 6, reverse=True)
        if info: logging.debug(f'sort to swamp.')
      if t.hill:
        units.sort(key=lambda x: x.mountain_survival or x.rng + x.rng_mod >= 6, reverse=True)
        if info: logging.debug(f'sort to swamp.')
      if t.surf.name in [forest_t, swamp_t] or t.hill: 
        units.sort(key=lambda x: mounted_t not in x.traits, reverse=True)
        units.sort(key=lambda x: x.can_fly, reverse=True)
        if info: logging.debug(f'sort by not mounted.')
      units.sort(key=lambda x: x.pos.get_distance(x.pos, t))
      units = [i for i in units if i.type != 'civil']
      nation.devlog[-1] += [f'defense {defense} needs {defense_needs}, ranking {ranking}.']
      for uni in units:
        if  uni.pos == t and uni.garrison or uni.type == 'civil': continue
        if defense > defense_needs: 
          nation.devlog[-1] += [f'defense > defense_need.']
          break
        if defense + uni.ranking > defense_needs * 1.2 and t.around_threat + t.threat == 0:
          uni.split((1))
          msg = f'splited.'
          if info: logging.debug(msg)
          nation.devlog[-1] += [msg]
        defense += uni.ranking
        if uni.garrison:
          uni.garrison = 0
          uni.scout = 0
          msg = f'{uni} leaves garrison on {uni.pos} {uni.pos.cords}.'
          uni.log[-1] += [msg]
          nation.devlog[-1] += [msg]
          if info:  logging.debug(msg)
        msg = f'{uni} de {uni.pos.cords} defenderá {t} {t.cords}.'
        if info: logging.debug(msg)
        nation.devlog[-1] += [msg]
        uni.log[-1] += [msg]
        msg = f'defensa {defense} needs {defense_needs}.'
        if info: logging.debug(msg)
        nation.devlog[-1] += [msg]
        uni.log[-1] += [msg]
        if uni.pos != t:
          move_set(uni, t)
          move_set(uni, 'gar')
        elif uni.pos == t: 
          move_set(uni, 'gar')
  
  if info: logging.debug(f'time elapses. {time()-init}.')



def ai_random():
  global world
  logging.debug('ai_random')
  sp.speak(f'randoms.')
  world.update(scenary)
  world.add_random_buildings(world.buildings_value - len(world.buildings))
  world.building_restoration()
  
  if world.difficulty_type == 'dynamic': 
    difficulty = world.difficulty * sum(i.score for i in world.nations) / 100 
  else: difficulty = world.difficulty
  if world.random_score < difficulty:
    # init = time()
    world.add_random_unit(world.difficulty_change)
    # print(f'add_random_unit. {time()-init}.')
    world.update(scenary)
    
  # ai units joins.
  for uni in world.units:
    if (uni.pos.around_threat + uni.pos.threat) > uni.ranking: basics.ai_join_units(uni)
    elif uni.pos.food_need > uni.pos.food: 
      uni.split(randint(1, 2))
  for uni in world.units:
    if uni.hp_total > 0:
      uni.log.append([f'{turn_t} {world.turn}.'])
      unit_restoring(uni)
      uni.set_hidden(uni.pos)
      if uni.goto: moving_unit(uni)
      if uni.goto == []:
        oportunist_attack(uni)
      unit_attrition(uni)
      ai_action_random(uni)


def ai_set_free_units(nation, req=0):
  logging.info(f'ai_set_free_units.')
  nation.devlog[-1] += [f'ai set free units.']
  init = time()
  
  for t in nation.tiles:
    # if t.is_city: continue
    units = [u for u in t.units if u.nation == nation and u.garrison]
    defense = sum(u.ranking for u in units if u.garrison)
    defense_need = max(t.defense_req , t.around_threat + t.threat)
    if defense > defense_need: continue
    if t.surf.name in [forest_t, swamp_t] or t.hill: 
      units.sort(key=lambda x: x.rng + x.rng_mod)
    for uni in units:
      if defense > defense_need * 4: uni.split(3)
      elif defense > defense_need * 3: uni.split(2)
      elif defense > defense_need * 1.5: uni.split(1)
      if defense - uni.ranking >= defense_need:
        uni.garrison = 0
        defense -= uni.ranking
        msg = f'{uni} es ahora libre de {t} {t.cords}.'
        logging.debug(msg)
        nation.devlog[-1] += [msg]
        uni.log[-1] += [msg]
  
  logging.debug(f'time elapses. {time()-init}.')



def ai_train(nation):
  logging.info(f'entrenamiento {nation}. turno {world.turn}.')
  init = time()
  nation.update(nation.map)
  for ct in nation.cities:
    logging.debug(f'{ct}.')
    if ct.production: continue
    ct.set_seen_units()
    # ct.update()
    upkeep_limit = nation.upkeep_limit
    logging.debug(f'upkeep_limit ={upkeep_limit}.')
    units = [it(nation) for it in ct.all_av_units if it.settler == 0 and it.comm == 0]
    ct.set_defense()
    if ct.defense_total < ct.defense_min:
      logging.debug(f'amenaza mayor.')
      upkeep_limit = nation.upkeep * 1.5
      logging.debug(f'upkeep increased to {upkeep_limit}.')
    logging.debug(f'amenaza {ct.seen_threat}.')
    logging.debug(f'defense_total_percent. {ct.defense_total_percent}')
    logging.debug(f'military limit. {ct.military_percent} de {ct.military_limit}.')
    units = ct.set_train_type(units)
    logging.debug(f'entrenables {len(units)}.')
    if ct.defense_total_percent >= 100 and ct.military_percent > ct.military_limit:
      logging.debug(f'military limit.')
      units = [i for i in units if i.pop == 0]
    logging.debug(f'entrenables {[i.name for i in units]}.')
    for uni in units:
      if req_unit(uni, nation, ct):
        logging.debug(f'suma upkeep {nation.upkeep+uni.upkeep }.')
        if uni.upkeep and nation.upkeep + uni.upkeep > upkeep_limit:
            logging.debug(f'toca el mantenimiento.')
            continue
        ct.train(uni)
        break
  
  logging.debug(f'time elapses. {time()-init}.')



def ai_train_comm(nation):
  logging.info(f'ai_train_comm {nation} turn {world.turn}.')
  nation.update(nation.map)
  comms = len(nation.units_comm)
  others = len([i for i in nation.units if i.comm == 0])
  logging.debug(f'{comms =: }, {others =: }, {nation.commander_rate =: }.')
  logging.debug(f'{floor(others/nation.commander_rate)= } {comms =: }.')
  if comms < floor(others / nation.commander_rate):
    for ct in nation.cities:
      # ct.update()
      logging.debug(f'{ct.defense_total_percent =: }.')
      if ct.defense_total_percent < 200 or ct.production: continue
      units = [it(nation) for it in ct.all_av_units if it.comm]
      shuffle(units)
      logging.debug(f'available commanders {len(units)}.')
      for uni in units:
        if nation.upkeep + uni.upkeep < nation.upkeep_limit and req_unit(uni, nation, ct):
          logging.debug(f'{uni} suma upkeep {nation.upkeep+uni.upkeep }.')
          ct.train(uni)
          break



def ai_unit_cast(nation):
  logging.info(f'commander cast.')
  units = [i for i in nation.units if i.spells]
  for uni in units:
    banned = []
    spells = [sp(uni) for sp in uni.spells]
    shuffle(spells)
    min_power = min(sp.cost for sp in spells)
    tries = 10
    while uni.power > min_power and tries > 0:
      tries -= 1
      for spl in spells:
        if uni.power < min_power: break
        if spl.name in banned: continue
        #print(spl.name)
        init = spl.ai_run(uni)
        if init != None: 
          uni.log[-1] += [init]
          logging.debug(init)
          banned += [spl.name]
          break



def ai_unit_disband(nation):
  logging.info(f'ai_unit_disband.')
  if nation.income < nation.upkeep and nation.gold < nation.upkeep * 1.5:
    logging.debug(f'nation income{nation.income}. upkeep {nation.upkeep}. gold {nation.gold}.')
    units = [i for i in nation.units if i.upkeep > 0 and i.comm == 0
             and i.goto == []]
    units.sort(key=lambda x: x.ranking,)
    if units: uni = units[0]
    
    uni.update()
    uni.split(5)
    uni.pos.units.remove(uni)
    uni.nation.units.remove(uni)
    uni.city.pop_back += uni.pop
    logging.debug(f'{uni} disuelta.')



def auto_attack(itm):
  local_units = get_units(itm.pos, itm.nation)
  target = itm.set_attack()
  if target:
    combat_menu(itm, itm.pos, target)
    itm.update()
    msg = f'ataque invisible.'
    itm.log[-1].append(msg)
    return 1



def check_enemy(itm, pos, is_city=0, info=0):
  if info: logging.debug(f'check enemy, {is_city=:}.')
  pos.update(itm.nation)
  if is_city and itm.nation != pos.nation:
    itm.revealed = 1
    for i in pos.units:
      i.revealed = 1
      i.update()
  itm.update()
  for uni in pos.units:
    if itm.hidden == 0 and uni.nation != itm.nation and uni.hidden == 0:
      logging.warning(f'enemigo {uni}.')
      return 1



def check_position(itm):
  logging.debug(f'checking position.')
  if itm.pos.is_city and itm.nation != itm.pos.nation and itm.hidden == 0:
    if check_enemy(itm, itm.pos, is_city=1) == None: 
      if itm.nation in world.nations and itm.pos.defense >= 50 * itm.pos.city.pop / 100: take_city(itm)
      elif itm.nation not in world.nations and itm.pos.defense >= 100 * itm.pos.city.pop / 100: take_city(itm) 



def combat_log(units):
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



def before_combat(itm):
  itm.update()
  for sk in itm.skills:
    if sk.type == 'before combat':
      sk.run(itm)
      if itm. bc_log: itm.temp_log += itm.bc_log



def after_combat(itm):
  itm.update()
  itm.skills.sort(key=lambda x: x.index)
  for sk in itm.skills:
    sk.run_after_combat(itm)
    if itm.ac_log: itm.temp_log += itm.ac_log



def before_attack(itm):
  itm.update()
  for sk in itm.skills:
    if sk.type == 'before attack': sk.run(itm)
    if itm.ba_log: itm.temp_log += itm.ba_log



def after_attack(itm):
  itm.update()
  for sk in itm.skills:
    if sk.type == 'after attack': sk.run(itm)
    if itm.aa_log: itm.temp_log += itm.aa_log



def combat_menu(itm, pos, target=None, dist=0):
  itm.update()
  if itm not in  itm.pos.units:
    logging.debug(f'itm not in itm.pos')
  _units = [it for it in pos.units if it.nation != itm.nation]
  [it.update() for it in _units]
  _units.sort(key=lambda x: sum([x.off, x.off_mod, x.str, x.str_mod]), reverse=True)
  _units.sort(key=lambda x: x.units, reverse=True)
  _units.sort(key=lambda x: x.rng >= 6, reverse=True)
  _units.sort(key=lambda x: x.comm)
  _units.sort(key=lambda x: x.mp[0] > 0, reverse=True)
  logging.debug(f'distancia inicial {dist}.')
  go = 1
  if target == None: target = _units[0]
  dist = max(itm.rng + itm.rng_mod, itm.mrng, target.rng + target.rng_mod, target.mrng)
  if itm.hidden: dist = itm.rng + itm.rng_mod
  dist += roll_dice(1)
  itm.dist = dist
  itm.pos.update()
  target.pos.update(target.nation)
  itm.attacking = 1
  itm.target = target
  itm.won = 0
  target.attacking = 0
  target.can_retreat = 1
  target.target = itm
  target.won = 0
  units = [itm, target]
  if target.pos.city: msg1 = [f'ataque en {target.pos.city}, {target.pos}, {target.pos.cords}  de {itm.pos}, {itm.pos.cords}.']
  else: msg1 = [f'ataque en {target.pos}, {target.pos.cords}  de {itm.pos}, {itm.pos.cords}.']
  logging.info(msg1[0])
  msg2 = f'{itm} ({itm.nation}) ataca a {target} ({target.nation}).'
  logging.info(msg2)
  logging.info(f'hp {itm} {itm.hp_total}, target {target} {target.hp_total}.')
  logging.info(f'ranking {itm.ranking} VS {target.ranking}.')
  info = 1 if any(i.show_info == 1 for i in units) else 0
  if info: sleep(loadsound('warn4') / 2)
  for i in units:
    if i.damage_charge: i.can_charge = 1
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
  gold_itm = itm.set_value()
  gold_target = target.set_value()
  _round = 1
  while itm.hp_total > 0 or target.hp_total > 0:
    if go:
      # logging.debug(f'ronda {_round}.')
      shuffle(units)
      [i.update() for i in units]
      units.sort(key=lambda x: x.hidden, reverse=True)
      units.sort(key=lambda x: x.moves + x.moves_mod, reverse=True)
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
      [before_combat(i) for i in units]
      for uni in units:
        if (uni.attacking 
            or uni.rng + uni.rng_mod < uni.target.rng + uni.target.rng_mod 
            and dist > uni.rng + uni.rng_mod):
          dist = combat_moves(dist, uni)
          itm.dist, target.dist = [dist, dist]
          uni.temp_log.insert(2, f'{distance_t} {units[0].dist}, {units[0].rng+units[0].rng_mod}. {units[1].dist}, {units[1].rng+units[1].rng_mod}.',)
      # combat.
      for uni in units:
        if uni.hp_total > 0 and uni.rng + uni.rng_mod >= dist:
          before_attack(uni)
          combat_fight(dist, uni, _round)
          after_attack(uni)
          # before attack retreats
          if uni.target.hp_total > 0 and uni.target.deads[-1]: 
            if uni.target.resolve + uni.target.resolve_mod <= 5: 
              uni.target.combat_retreat()
      # After attack retreats.
      [uni.combat_retreat() for uni in units if uni.resolve + uni.resolve_mod >= 6]
      
      # after combat.
      [after_combat(i) for i in units if i.hp_total > 0]
      dist = units[0].dist
      
      # fin del turno.
      combat_log(units)
      _round += 1
      for i in units:
        if dist == 1: i.charging = 0
      
      # end of combat.
      if any(i.hp_total < 1 for i in units):
        if itm.nation in world.nations: itm.mp[0] -= 1
        [i.stats_battle() for i in [itm, target] if i.hp_total >= 1]
        combat_post(itm, target)
        for i in units:
          msg = [i for i in msg1]
          msg += i.battle_log
          i.log[-1] += [msg, msg2]
          i.nation.log[-1] += [msg, msg2]
          if i.nation in i.pos.world.random_nations: i.pos.world.log[-1] += [msg, msg2]
          i.add_corpses(target.pos)
        if itm.hp_total < 1:
          if itm.pos != target.pos and itm in itm.pos.units: itm.pos.units.remove(itm)
          msg = f'{target} ({target.nation}) a vencido.'
          if target.show_info: speak(msg)
          logging.info(msg)
          target.log[-1].append(msg)
          target.nation.log[-1].append(msg)
          target.pos.world.log[-1] += [msg]
          itm.nation.log[-1].append(msg)
          if gold_itm:
            msg1 = f'gana {gold_itm} {gold_t}.'
            target.nation.gold += gold_itm
            target.nation.log[-1].append(msg1)
            logging.debug(msg1)
          if info:
            sp.speak(msg)
            sleep(loadsound('notify18') * 0.5)
          logging.info(msg)
          # check_position(target)
          return 0
        elif target.hp_total < 1:
          msg = f'{itm} ({itm.nation}) ha vencido.'
          itm.log[-1].append(msg)
          itm.nation.log[-1].append(msg)
          target.nation.log[-1].append(msg)
          target.pos.world.log[-1] += [msg]
          if gold_target:
            msg1 = f'gana {gold_target} {gold_t}.'
            itm.nation.gold += gold_target
            itm.nation.log[-1].append(msg1)
            logging.debug(msg1)
          if info:
            speak(msg=msg)
            sleep(loadsound('win1') * 0.5)
          logging.info(msg)
          # check_position(itm)
          return 1



def combat_moves(dist, itm, info=1):
    moves = itm.moves + itm.moves_mod
    if info:logging.debug(f'distancia de {itm}  {dist}.')
    if dist > itm.rng + itm.rng_mod:
      move = roll_dice(2)
      if itm.can_fly: move += 2
      if info: logging.debug(f'move {move}. moves {moves}.')
      if move > moves: move = moves
      if itm.hidden: move += 2
      dist -= move
      if dist < 1: dist = 1
      if dist < itm.rng + itm.rng_mod: dist = itm.rng + itm.rng_mod
      if info: logging.debug(f'distancia final {dist}.')
    return dist



def combat_fight(dist, itm, _round, info=0):
  itm.update()
  target = itm.target
  target.update()
  target.c_units = target.units
  if info: logging.info(f'{itm} total hp {itm.hp_total} ataca.')
  if target.armor: armor = target.armor.name
  else: armor = 'none'
  if target.shield: shield = target.shield.name
  else: shield = 'none'
  log = itm.temp_log
  log += [  
    f'{itm} {attacking_t}.',
    f'att {itm.att + itm.att_mod} (+{itm.att_mod}).'
    f'{damage_t} {itm.damage + itm.damage_mod} (+{itm.damage_mod}). '
    f'sacred damage {itm.damage_sacred_mod}.',
    f'off {itm.off + itm.off_mod} (+{itm.off_mod}). '
    f'{target} dfs {target.dfs+ target.dfs_mod} (+{target.dfs_mod}).',
    f'str {itm.str + itm.str_mod} (+{itm.str_mod}). '
    f'{target} res {target.res+ target.res_mod} (+{target.res_mod})',
    f'armor {armor}, shield {shield}.',
    ]
  for uni in range(itm.units):
    if info: logging.debug(f'unidad {uni+1} de {itm.units}.')
    attacks = itm.att + itm.att_mod
    for i in range(attacks):
      if target.hp_total < 1: break
      itm.attacks[-1] += 1
      if info: logging.debug(f'ataque {i+1} de {attacks}.')
      target.c_units = target.units
      damage = itm.damage + itm.damage_mod
      damage_critical = 0
      
      # hit
      hit_rolls = itm.hit_rolls + itm.hit_rolls_mod
      for i in range(hit_rolls):
        if info: logging.debug(f'impactos {i} de {hit_rolls}')
        hits = 0
        hit_roll = basics.roll_dice(1)
        if info: logging.debug(f'{hit_roll=:}.')
        off = itm.off + itm.off_mod
        if itm.rng + itm.rng_mod >= 6 and itm.dist < itm.rng + itm.rng_mod: 
          off -= 2
        off_need = off
        if info: logging.debug(f'off_need1  {off_need}.')
        off_need -= target.dfs + target.dfs_mod
        if info: logging.debug(f'off_need2 {off_need}.')
        off_need = basics.get_hit_mod(off_need)
        if info: logging.debug(f'off_need3 {off_need}.')
        if hit_roll >= off_need:
          hits = 1
          itm.strikes[-1] += 1
          break

      # shield.
        if target.shield:
          shield_need = basics.roll_dice(1)
          shield = basics.get_armor_mod(target.shield.dfs)
          if shield > shield_need and shield > 0: 
            hits = 0
            itm.hits_shield_blocked[-1] += 1
      
      if hits:
        wounds = 0
        hit_to = 'body'
        wound_roll = basics.roll_dice(1)
        if info:logging.debug(f'roll {wound_roll=}')
        wound_need = itm.str + itm.str_mod
        if info: logging.debug(f'wound_need1 {wound_need}.')
        res = target.res + target.res_mod
        roll = basics.roll_dice(1)
        if itm.rng + itm.rng_mod < 6:
          head_factor = 6
          size_factor = (itm.size + itm.size_mod) - (itm.target.size + itm.target.size_mod)
          head_factor -= size_factor
          head_factor -= (itm.rng + itm.rng_mod)
        elif itm.rng + itm.rng_mod >= 6 or itm.can_fly: head_factor = 6
        if roll >= head_factor:
          hit_to = 'head'
          if info:logging.debug(f'hit to the head.')
          res = target.hres + target.hres_mod
        wound_need -= res
        if info: logging.debug(f'wound_need2 {wound_need}.')
        wound_need = basics.get_wound_mod(wound_need)
        if info: logging.debug(f'wound_need3 {wound_need}.')
        if wound_roll < wound_need:
          itm.hits_resisted[-1] += 1 
          continue
        wounds = 1

        # armor
        if hit_to == 'body':
          roll = basics.roll_dice(1)
          armor = target.arm + target.arm_mod
          if target.armor: armor += target.armor.arm
          if target.armor_ign + target.armor_ign_mod == 0: armor -= itm.pn + itm.pn_mod
          else: 
            if info: logging.debug(f'{target} ignora pn.')
          armor = basics.get_armor_mod(armor)
          if info: logging.debug(f'roll{roll} necesita {armor}.')
          if roll >= armor and armor > 0:
            wounds = 0
            itm.hits_armor_blocked[-1] += 1

        # wounds.
        if wounds and target.hp_total > 0:
          if hit_to == 'body': itm.hits_body[-1] += 1
          elif hit_to == 'head': 
            itm.hits_head[-1] += 1
            damage_critical += damage
          
          if undead_t in target.traits:
            damage += itm.damage_sacred
            if info: logging.debug(f'damage holy {itm.damage_sacred}.')
          # if damage > itm.target.hp: damage = itm.target.hp
          if itm.can_charge and itm.charge:
            damage += itm.damage_charge
            if info: logging.debug(f'carga {itm.damage_charge}.')
          damage += damage_critical
          target.hp_total -= (damage)
          if info: logging.info(f'{target} recibe {damage} de daño.')
          target.update()
          itm.damage_done[-1] += damage
          target.deads[-1] += target.c_units - target.units
  
  itm.hits_failed[-1] = itm.attacks[-1] - itm.strikes[-1]
  itm.charge = 0
  if itm.damage_done[-1] and itm.target.hidden: 
    itm.temp_log += [f'{itm.target} revealed.']
    itm.target.revealed = 1
  
  log += [  
    f'{attacks_t} {itm.attacks[-1]}, {hits_failed_t} {itm.hits_failed[-1]}, '
    f'{hits_t} {itm.strikes[-1]}.',
    ]
  if itm.hits_resisted[-1]: log += [f'resisted {itm.hits_resisted[-1]}.']
  if itm.hits_armor_blocked[-1]: log += [f'armor blocked {itm.hits_armor_blocked[-1]}.']
  if itm.hits_shield_blocked[-1]: log += [f'shield blocked {itm.hits_shield_blocked[-1]}.']
  log += [f'to the head {itm.hits_head[-1]}, to the body {itm.hits_body[-1]}.',
    f'{wounds_t} {itm.hits_body[-1]+itm.hits_head[-1]}, {damage_t} {itm.damage_done[-1]}, '
    f'{deads_t} {itm.target.deads[-1]}.'
    ]



def combat_post(itm, target):
  logging.info(f'combat post.')
  for i in [itm, target]:
    if i.hp_total > 0: i.pos.update(i.nation)
    i.attacking = 0
    i.target = None
    if i.hp_total > 0:
      skills = [sk for sk in i.skills if sk.type == 'pos combat']
      [sk(i) for sk in skills]
    if i.hp_total < 1 and sum(i.fled) >= 1 and i.can_retreat:
      logging.debug(f'{i} pierde.')
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
      logging.debug(f'{unit} huyen {sum(i.fled)}.')
      if unit.units < unit.min_units / 4: continue
      unit.pos.units.append(unit)
      if unit.can_retreat:
        logging.debug(f'se retirará.')
        unit.mp[0] = unit.mp[1]
        tile = get_retreat_pos(unit)
        move_set(unit, tile)



def control_basic(event):
  global nation
  if event.type == pygame.KEYDOWN:
    if event.key == pygame.K_F1:
      sp.speak(f'{world.ambient.stime} ({world.ambient.sday_night}).', 1)
    if event.key == pygame.K_F2:
      msg = f'{world.ambient.sseason}, {world.ambient.smonth}, \
        {world.ambient.syear}.'
      sp.speak(msg, 1)
    if event.key == pygame.K_F3:
      sp.speak(f'{turn_t} {world.turn}.', 1)
    if event.key == pygame.K_F4:
      sp.speak(f'{gold_t} {round(nation.gold)}.')
      sp.speak(f'{income_t} {nation.income}, {upkeep_t} {nation.upkeep}.')
      sp.speak(f'{raid_income_t} {nation.raid_income}.')
      sp.speak(f'{raid_outcome_t} {nation.raid_outcome}.')
      sp.speak(f'({total_t} {nation.income - nation.upkeep + (nation.raid_income-nation.raid_outcome)}).')



def control_game(event):
  global east, filter_expand, inside, move, nation, pos, rng, sayland, scenary, tiers, unit, west, world, width
  global x, y

  if event.type == pygame.KEYDOWN:
    if event.key == pygame.K_7:
      pos.add_unit(VladDracul, wallachia_t, 1)
    if event.key == pygame.K_8:
      pos.add_unit(Ghouls, wallachia_t, 1)
    if event.key == pygame.K_9:
      pos.add_unit(Principes, holy_empire_t, 1)
    if event.key == pygame.K_0:
      pos.add_unit(WeetOnes, holy_empire_t, 1)
    if event.key == pygame.K_a:
      if x > -1:
        target = local_units[x].set_attack()
        if target:
          combat_menu(local_units[x], pos, target)
          x = -1
          sayland = 1
    if  ctrl and event.key == pygame.K_b:
      pos.buildings += [BrigandLair(Wild, pos)]
      return
    if event.key == pygame.K_b:
      # ver edificios.
      if x < 0 and pos in nation.map and pos.blocked == 0:
        menu_building(pos, nation)
        pos.update(nation)
      # quemar.
      elif x > -1:
        local_units[x].burn()
    if event.key == pygame.K_c:
      if x > -1 and local_units[x].buildings and pos.sight:
        if local_units[x].mp[0] < 1 or local_units[x].nation != nation:
          error(msg='sin movimientos')
          return
        itm = get_item2(items1=local_units[x].buildings, msg='crear', simple=1)
        if itm:
          if itm(nation, local_units[x].pos).can_build() == 0:
            error()
            return
          local_units[x].nation.add_city(itm, local_units[x])
          pos.pos_sight(nation, nation.map)
          sayland = 1
          x = -1
    if event.key == pygame.K_h:
      if x > -1:
        itm = local_units[x]
        cast = get_cast(itm)
        if cast:
          init = cast.init(itm)
          if init != None: 
            itm.log[-1] += [init]
            logging.debug(init)
          nation.update(scenary)
          map_update(nation, nation.map)
          sayland = 1

    if event.key == pygame.K_i:
      if x > -1: item_info(local_units[x], nation)
      elif x < 0: info_tile(pos, nation)
    if event.key == pygame.K_j:
      # unir.
      if len(unit) > 1:
        unit[0].join_units(unit, 1)
        sayland = 1
        unit = []
        x = -1
    if event.key == pygame.K_l:
      if x > -1: view_log(local_units[x].log)
    if event.key == pygame.K_m:
      # mover unidad.
      if unit:
        if pos not in nation.map:
          error()
          return
        for i in unit: move_set(i, pos)
        sayland = 1
    if event.key == pygame.K_n:
      # nombrar casilla.
      if x == -1 and pos.nation == None  or pos.nation == nation: 
        pos.name = naming()
      # nombrar unidad.
      elif x >= 0 and local_units[x].nation == nation: local_units[x].nick = naming()
    if event.key == pygame.K_p:
      pass
    if event.key == pygame.K_r:
      # saquear.
      if x > -1:
        local_units[x].raid()
    if event.key == pygame.K_s:
      if x > -1: local_units[x].split()
      sayland = 1

    if event.key == pygame.K_SPACE:
      if x > -1:
        if local_units[x] not in unit:
          loadsound('selected1')
          sp.speak(f'{selected_t}', 1.)
          unit.append(local_units[x])
        elif local_units[x] in unit:
          sp.speak(f'{unselected_t}.', 1)
          unit.remove(local_units[x])
          loadsound('unselected1')
    if event.key == pygame.K_RETURN:
      # opciones de edificio.
      if filter_expand == 0:
        if pos.is_city and pos.nation == world.nations[world.player_num]:
          sayland = 1
          [menu_city(b) for b in pos.buildings if b.type == city_t]
        elif pos.building and pos.building.nation != world.nations[world.player_num]:
          error()
      # expandir ciudad.
      elif filter_expand:
        if expand_city(city, pos):
          filter_expand = 0
          pos.update(nation)
          near_tiles = pos.get_near_tiles(2)
          pos.pos_sight(nation, nation.map)
          pos.city.update()
          nation.update(scenary)
          sayland = 1
    if event.key == pygame.K_DELETE:
      if x == -1 or (local_units and local_units[x].nation != nation):
        error()
        return
      if get_item2([0, 1], ['no', 'si'], 'Eliminar unidad',):
        local_units[x].disband()
        sayland = 1
    if  ctrl and event.key == pygame.K_TAB:
      view_log(world.log)
      return
    if event.key == pygame.K_TAB:
      view_log(nation.log)
    if event.key == pygame.K_HOME:
      unit = []
      x = -1
      if nation.cities == []:
        error(msg='no hay ciudad.', sound='errn1')
        return
      nation.cities.sort(key=lambda x: x.capital, reverse=True)
      y = basics.selector(nation.cities, y, 'up')
      try:
        pos = nation.cities[y].pos
      except:
        pos = nation.cities[0].pos
        print(f'error.')
      sayland = 1
    if event.key == pygame.K_END:
      unit = []
      x = -1
      if nation.cities == []:
        error(msg='no hay ciudad.', sound='errn1')
        return
      nation.cities.sort(key=lambda x: x.capital, reverse=True)
      y = basics.selector(nation.cities, y, 'down')
      try:
        pos = nation.cities[y].pos
      except:
        pos = nation.cities[0].pos
        print(f'error.')
      sayland = 1
    if event.key == pygame.K_PAGEUP:
      play_stop()
      if local_units == [] or pos.sight == 0:
        error(msg=empty_t)
        return
      if x == -1:
        unit = []
        x = 0
      elif x > -1:
        x = basics.selector(local_units, x, 'up')
      local_units[x].basic_info()
    if event.key == pygame.K_PAGEDOWN:
      play_stop()
      if local_units == [] or pos.sight == 0:
        error(msg=empty_t)
        return
      if x == -1:
        unit = []
        x = 0
      elif x > -1:
        x = basics.selector(local_units, x, 'down')
      local_units[x].basic_info()
    if event.key == pygame.K_F5:
      sayland = 1
      nation.update(nation.map)
      menu_unit(nation.units)
    if event.key == pygame.K_F6:
      sayland = 1
      units = []
      for ti in nation.map:
        if ti.sight:
          for uni in ti.units:
            sq = uni.pos.get_near_tiles(1)
            go = 0
            for s in sq:
              if s.nation == nation: go = 1
            if uni.nation != nation and uni.hidden == 0 and go: units.append(uni)
      menu_unit(units)
    if event.key == pygame.K_F7:
      sayland = 1
      units = []
      for ti in nation.map:
        if ti.sight:
          for uni in ti.units:
            if uni.nation != nation and uni.hidden == 0: units.append(uni)
      units.sort(key=lambda x: x.pos.get_distance(x.pos, nation.cities[0].pos))
      menu_unit(units)
    if event.key == pygame.K_F8:
      menu_nation(nation)
    if event.key == pygame.K_F11:
      world.player_num += 1
      next_play()



def control_editor(event):
  global Belongs, east, Evt, inside, Group, Name, pos, sayland, scenary, starting, xy
  if event.type == pygame.KEYDOWN:
    # Ocean.
    if event.key == pygame.K_1:
      for i in [pos] + Group:
        i.soil = Ocean()
        i.surf = EmptySurf()
        i.hill = 0
      sayland = 1
    # Plain.
    if event.key == pygame.K_2:
      for i in [pos] + Group:
        i.soil = Plains()
        i.surf = EmptySurf()
        i.hill = 0
      sayland = 1
    # Grass.
    if event.key == pygame.K_3:
      for i in [pos] + Group:
        i.soil = Grassland()
        i.surf = EmptySurf()
        i.hill = 0
      sayland = 1
    # Desert.
    if event.key == pygame.K_4:
      for i in [pos] + Group:
        i.soil = Desert()
        i.surf = EmptySurf()
        i.hill = 0
      sayland = 1
    # Tundra.
    if event.key == pygame.K_5:
      for i in [pos] + Group:
        i.soil = Tundra()
        i.surf = EmptySurf()
        i.hill = 0
      sayland = 1
    # Glassier.
    if event.key == pygame.K_6:
      for i in [pos] + Group:
        i.soil = Glacier()
        i.surf = EmptySurf()
        i.hill = 0
      sayland = 1

    if event.key == pygame.K_q:
      # river
      for i in [pos] + Group:
        i.surf = River()
        i.hill = 0
      sayland = 1
    if event.key == pygame.K_w:
      # swamp.
      for i in [pos] + Group:
        i.surf = Swamp()
        i.hill = 0
      sayland = 1
    if event.key == pygame.K_e:
      # forest
      for i in [pos] + Group:
        i.surf = Forest()
        sayland = 1
    if event.key == pygame.K_r:
      # hill
      if (pos.surf == None or pos.surf
          and pos.surf.name not in [mountain_t, river_t, swamp_t, volcano_t]):
        for i in [pos] + Group:
          i.hill = 1
      else: loadsound('errn1')
      sayland = 1
    if event.key == pygame.K_t:
      # volcano
      if pos.surf == None:
        for i in [pos] + Group:
          i.surf = Volcano()
          i.hill = 0
      else: loadsound('errn1')
      sayland = 1
    if event.key == pygame.K_y:
      # mountain
      if pos.surf == None:
        for i in [pos] + Group:
          i.surf = Mountain()
          i.hill = 0
      else: loadsound('errn1')
      sayland = 1

    if event.key == pygame.K_F1:
      pass
    if event.key == pygame.K_b:
      pass
    if event.key == pygame.K_d:
      pass
    if event.key == pygame.K_n:
      Belongs, Evt, Name = None, None, None
      Name = naming()
    if event.key == pygame.K_u:
      pass
    if event.key == pygame.K_p:
      if xy:
        sp.speak(f'{ready_t}.')
        xy[0].append(pos.x)
        xy[1].append(pos.y)
        xy = [sorted(i) for i in xy]
        for item in scenary:
          if ((item.x >= xy[0][0] and item.y >= xy[1][0])
              and (item.x <= xy[0][1] and item.y <= xy[1][1])):
            Group.append(item)
        sleep(loadsound('back1') / 2)
        xy = []
      else:
        sp.speak(f'desde.')
        sleep(loadsound('in1') / 2)
        Group = []
        xy = [[pos.x], [pos.y]]

    if event.key == pygame.K_RETURN:
      if Belongs != None:
        if Group:
          for item in Group:
            if item.belongs:
              item.belongs = None
              if item in Belongs.owns: Belongs.owns.remove(item)
            else:
              item.belongs = Belongs
              if item not in Belongs.owns: Belongs.owns.append(item)
        else:
            if pos.belongs and pos.belongs == Belongs:
              sp.speak(f'{deleted_t}.', 1)
              pos.belongs = None
            elif pos.belongs == None or pos.belongs != Belongs:
              sp.speak(f'{added_t}.', 1)
              pos.belongs = Belongs
              Belongs.owns.append(pos)
        sayland = 1
      if Evt != None:
        pass
      if Name != None:
        loadsound('set5')
        if Group:
          for item in Group:
            item.name = Name
        else:pos.name = Name
        sayland = 1

    if event.key == pygame.K_PAGEUP:
      pass
    if event.key == pygame.K_PAGEDOWN:
      pass

    if event.key == pygame.K_F9:
      if mapeditor: save_map()



def control_global(event):
  global Belongs, city_name, east, Evt, inside, Group, mapeditor, move, Name, nation_name, pos, sayland, scenary, terrain_name, unit, west, width, xy
  if event.type == pygame.KEYDOWN:
    if x > -1 and mapeditor == 0 :
      if event.key == pygame.K_5:
        sp.speak(f' garrison {local_units[x].garrison}.', 1)
        sp.speak(f'scout {local_units[x].scout}.')
        sp.speak(f'revealed value {local_units[x].revealed_val}.')
        if local_units[x].goal: sp.speak(f'goal {local_units[x].goal[0], local_units[x].goal[1].cords}.')
    if x == -1 and mapeditor == 0 :
      if event.key == pygame.K_1:
        sp.speak(f'{food_t} {pos.food_need} {of_t} {pos.food}.', 1)
        sp.speak(f'{resources_t} {pos.resource}.')
        sp.speak(f'{round(pos.pop*100/pos.food,1)}%.')
      if event.key == pygame.K_2:
        events = [ev.name for ev in pos.events]
        terrain = [ev.name for ev in pos.terrain_events]
        sp.speak(f'events {events}.')
        sp.speak(f'terrain {terrain}.')
      if event.key == pygame.K_3:
        sp.speak(f'{population_t} {pos.pop}, {public_order_t} {pos.public_order}.', 1)
        sp.speak(f'unrest {pos.unrest}.')
      if event.key == pygame.K_4:
        sp.speak(f'{income_t} {pos.income}.', 1)
        sp.speak(f'{raid_outcome_t} {pos.raided}.')
        sp.speak(f'{total_t} {pos.income-pos.raided}.')
      if event.key == pygame.K_5:
        sp.speak(f'{pos.flood= }.')
        sp.speak(f'cost {pos.cost}.')
        sp.speak(f'{size_t} {pos.size}.')

      if event.key == pygame.K_d:
        sp.speak(f'defensa {round(pos.defense, 1)}.')
        sp.speak(f'{around_defense_t} {pos.around_defense}.')
        sp.speak(f'{pos.defense_req= }')
      if event.key == pygame.K_t:
        sp.speak(f'{threat_t} {pos.threat}.')
        sp.speak(f'{around_threat_t} {pos.around_threat}.')
      if event.key == pygame.K_l:
        if pos in nation.map:
          msg = f'''
          {ocean_t} {pos.around_coast},
          {hill_t} {pos.around_hill},
          {forest_t} {pos.around_forest},
          {plains_t} {pos.around_plains},
          {swamp_t} {pos.around_swamp},
          {grassland_t} {pos.around_grassland},
          {waste_t} {pos.around_desert},
          {tundra_t} {pos.around_tundra},
          {glacier_t} {pos.around_glacier}.
          '''
          sp.speak(msg)
      if event.key == pygame.K_v:
        sp.speak(f'valor {pos.food_value}, {pos.res_value}.', 1)
        sp.speak(f'{pos.mean}.')
      
    if event.key == pygame.K_z:
      pos.update(nation)
      if pos in nation.map: sp.speak(f'{pos}')
    if event.key == pygame.K_x:
      sp.speak(f'{pos.cords}.')
    if event.key == pygame.K_F9:
      if mapeditor == 0: save_game()
    if event.key == pygame.K_F10:
      if pos.city: ct = pos.city
      Pdb().set_trace()
      sp.speak(f'pdb off.')
    if event.key == pygame.K_F12:
      sp.speak('on', 1)
      sp.speak('off', 1)
    if event.key == pygame.K_ESCAPE:
      if (Belongs or Evt or Group or Name != None or unit != [] or rng
          or filter_expand or x > -1):
        end_parameters()  
        return
      if get_item2([0, 1], ['no', 'si'], 'salir?',):
        exit()



def create_building(city, items, sound='in1'):
  sleep(loadsound(sound) / 2)
  say = 1
  sp.speak(f' {build_t}.')
  x = 0
  while True:
    sleep(0.05)
    if say:
      itm = items[x](nation, pos)
      time_cost = ceil(itm.resource_cost[1] / city.resource_total)
      sp.speak(f'{itm} {in_t} {time_cost} {turns_t}.')
      sp.speak(f'{cost_t} {itm.gold}.')
      say = 0

    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_i:
          if isinstance(items[x](nation, nation.pos), Building): item_info(items[x](nation, nation.pos), nation)
        if event.key == pygame.K_UP:
          x = basics.selector(items, x, go="up")
          say = 1
        if event.key == pygame.K_DOWN:
          x = basics.selector(items, x, go="down")
          say = 1
        if event.key == pygame.K_HOME:
          x = 0
          say = 1
        if event.key == pygame.K_END:
          x = len(items) - 1
          say = 1
        if event.key == pygame.K_RETURN:
          if itm.can_build():
            return itm
          else: error()
        if event.key == pygame.K_F12:
          sp.speak(f'debug on.', 1)
          sp.speak(f'debug off.', 1)
        if event.key == pygame.K_ESCAPE:
          sleep(loadsound('back1') / 2)
          return



def destroy_city(city):
  city.nation.cities.remove(city)
  for t in city.tiles:
    t.city = None
    t.nation = None
    t.buildings = []
    


def end_parameters(sound='unselected1'):
  global Belongs, Evt, filter_expand, Group, move, Name, rng, unit, x, xy
  loadsound(sound)
  Belongs = None
  Evt = None
  filter_expand = 0
  Group = []
  Name = None
  rng = None
  unit = []
  x = -1



def error(info=0, msg='', sound='errn1', slp=0):
  if info == 1:
    sp.speak(msg, 1)
    sleep(loadsound(sound, channel=ch4) * 5)
  logging.debug(msg)



def exit_game():
  sp.speak(f'sale')
  sleep(0.1)
  sys.exit()



def expand_city(city, pos):
  cost = get_tile_cost(city, pos)
  if city.nation.gold >= cost and pos not in city.tiles:
    city.tiles.append(pos)
    pos.city = city
    pos.nation = city.nation
    city.nation.gold -= cost
    msg = f'{city} se expandió a {pos} {pos.cords}.'
    speak(msg, num=1)
    sleep(loadsound('gold1') * 1.5)
    return True
  else:
    error(msg='ínsuficiente oro o la casilla es propia.')
    return False



def get_cast(itm):
  sleep(loadsound('in1') * 0.5)
  sp.speak(f'hechisos.')
  say = 1
  x = 0
  while True:
    sleep(0.05)
    if say and itm.spells:
      sp.speak(f'{itm.spells[x].name}. {cost_t} {itm.spells[x].cost}.', 1)
      say = 0

    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_F1:
          sp.speak(f'{power_t} {itm.power} {of_t} {itm.power_max}.')
        if event.key == pygame.K_HOME:
          x = 0
          loadsound('s2')
          say = 1
        if event.key == pygame.K_END:
          x = len(itm.spells) - 1
          loadsound('s2')
          say = 1
        if event.key == pygame.K_UP:
          x = basics.selector(itm.spells, x, go="up")
          say = 1
        if event.key == pygame.K_DOWN:
          x = basics.selector(itm.spells, x, go="down")
          say = 1
        if event.key == pygame.K_i:
          pass
        if event.key == pygame.K_RETURN:
          if itm.spells: return itm.spells[x](itm)
        if event.key == pygame.K_F12:
          sp.speak(f'on', 1)
          sp.speak(f'off', 1)
        if event.key == pygame.K_ESCAPE:
          loadsound('back3')
          return



def get_item2(items1=[], items2=[], msg='', name=None, simple=0, sound='in1'):
  x = 0
  if all(i == [] for i in [items1, items2]):
    error(info=1)
    return
  if sound: sleep(loadsound(sound) / 2)
  say = 1
  sp.speak(msg, 1)
  while True:
    sleep(0.1)
    if say:
      if items2: sp.speak(items2[x], 1)
      else:
        if name == None and simple == 0: sp.speak(items1[x](nation, pos).name, 1)
        elif name and simple:
          sp.speak(items1[x].name, 1)
          sp.speak(items1[x].id, 1)
      say = 0
    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
        info_building(items1[x](nation, nation.pos))
      if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
        x = basics.selector(items1, x, go="up")
        say = 1
      if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
        x = basics.selector(items1, x, go="down")
        say = 1
      if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
        sp.speak(msg, 1)
      if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
        sleep(loadsound('back3') / 2)
        if items2: return x
        else:
          if simple == 0:return items1[x](nation, pos)
          elif simple:return items1[x]
      if event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
        sp.speak('on', 1)
        sp.speak('off', 1)
      if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        loadsound('back3')
        sleep(0.5)
        return



def get_retreat_pos(itm):
  logging.debug(f'pocición inicial {itm.pos} {itm.pos.cords}.')
  sq = itm.pos.get_near_tiles(1)
  sq = [i for i in sq
        if i.soil.name in itm.soil and i.surf.name in itm.surf and i != itm.pos
        and (itm.can_fly == 0 and i.cost <= itm.mp[0])
        or (itm.can_fly and i.cost_fly <= itm.mp[0])]

  [s.update(itm.nation) for s in sq]
  logging.debug(f'{len(sq)} casillas para retirada.')
  shuffle(sq)
  sq.sort(key=lambda x: x.nation == None, reverse=True)
  sq.sort(key=lambda x: x.nation == itm.nation, reverse=True)
  sq.sort(key=lambda x: x.threat)
  sq.sort(key=lambda x: x.cost)
  for i in sq:
    logging.debug(f'{i}, {i.cords}.')
  for s in sq:
    if s.cost <= itm.mp[1]: return sq[0]



def get_tile_cost(city, pos):
  cost = city.nation.tile_cost
  distance = pos.get_distance(pos, city.pos)
  cost = cost ** (city.nation.tile_power + distance / 10)
  return round(cost, 2)



def get_units(pos, nation):
  units = [i for i in pos.units
           if i.hidden == 0 or i.nation == nation]
  return units



def go_home(itm):
  tiles = itm.nation.tiles
  tiles.sort(key=lambda x: x.threat)
  tiles.sort(key=lambda x: x.around_threat)
  tiles.sort(key=lambda x: x.get_distance(itm.pos, x))
  tiles.sort(key=lambda x: x.cost)
  logging.debug(f'{itm} regresa.')
  itm.goto = []
  itm.goal = [base_t, tiles[0]]
  move_set(itm, tiles[0])



def hero_set_group(itm):
  if itm.group == []:
    if itm.pos.nation == itm.nation and itm.pos.city:
      itm.create_group(itm.ranking // 2)



def info_building(itm, sound='in1'):
  sleep(loadsound(sound))
  say = 1
  x = 0
  while True:
    sleep(0.05)
    if say:
      av_units = [i.name for i in itm.av_units]
      upgrades = [i.name for i in itm.upgrade]
      lista = [
        f'{itm}, {size_t} {itm.size}.',
        f'{gold_t} {itm.gold}. {upkeep_t} {itm.upkeep}, {resources_t} {itm.resource_cost[1]}.',
        f'{units_t} {av_units if itm.av_units else str()}.',
        f'{upgrades_t} {upgrades if itm.upgrade else str()}.',
        f'{income_t} {itm.income}, {upkeep_t} {itm.upkeep}.',
        f'{food_t} {itm.food}. {resources_t} {itm.resource}.',
        f'{public_order_t} {itm.public_order}. {grouth_t} {itm.grouth}.',
        ]

      sp.speak(lista[x])
      say = 0

    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
          x = basics.selector(lista, x, go="up")
          say = 1
        if event.key == pygame.K_DOWN:
          say = 1
          x = basics.selector(lista, x, go="down")
        if event.key == pygame.K_HOME:
          x = 0
          say = 1
          loadsound('s1')
        if event.key == pygame.K_END:
          x = len(lista) - 1
          say = 1
          loadsound('s1')
        if event.key == pygame.K_F12:
          sp.speak(f'on.', 1)
          sp.speak(f'off.', 1)
        if event.key == pygame.K_ESCAPE:
          sleep(loadsound('back1') / 2)
          return



def info_tile(pos, nation, sound='in1'):
  sleep(loadsound(sound) / 2)
  say = 1
  x = 0
  while True:
    sleep(0.01)
    if say:
      if pos.corpses == []: corpses = ['no.']
      else: corpses = []
      for i in pos.corpses:
        corpses += [f'{i}: {sum(i.deads)}']
      items = [
        f'{corpses_t} {[str(it) for it in corpses]}',
        f'{pos}',
        f'{buildings_t} {len(pos.buildings)}, {units_t} {len(pos.units)}.',
        f'{population_t} {round(pos.pop,1)}, {public_order_t} {round(pos.public_order,1)}.',
        f'{income_t} {round(pos.income,1)}.',
        f'{food_t} {pos.food}. {resources_t} {pos.resource}.',
        f'{defense_t} {pos.defense}.',
        f'{grouth_t} {pos.grouth_total}.',
        f'{size_t} {pos.size}, {pos.size_total}%.',
        f'{cost_t} {pos.cost}.',
        ]

      sp.speak(f'{items[x]}')
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
        if event.key == pygame.K_END:
          x = len(items) - 1
          say = 1
        if event.key == pygame.K_RETURN:
          # construir.
          if buildings_t in items[x]:
            menu_building(pos, nation)
            say = 1
        if event.key == pygame.K_DELETE:
          pass
        if event.key == pygame.K_F12:
          sp.speak(f'debug on.', 1)
          sp.speak(f'debug off.', 1)
        if event.key == pygame.K_ESCAPE:
          sleep(loadsound('back1') / 2)
          return



def item_info(itm, nation):
  if itm.type == building_t:
    info_building(itm)
  elif itm.type in ['beast', 'civil', 'cavalry', 'infantry']:
    itm.info(nation)



def loading_map(location, filext, saved=0, sound='book_open01'):
  global east, height, ext, name, pos, scenary, west, width, world
  sleep(loadsound(sound))
  x = 0
  say = 1
  loop = 1
  maps = glob(os.path.join(location + filext))
  maps = natsort.natsorted(maps)
  while loop:
    sleep(0.01)
    if say:
      say = 0
      if maps:
        sp.speak(maps[x][int(maps[0].rfind('\\')) + 1:-4], 1)
      else:
        sp.speak(empty_t, 1)
      
    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN :
        if event.key == pygame.K_1:
          maps = natsort.natsorted(maps)
          sp.speak(f'sort by recent date time.', 1)
          say = 1
        if event.key == pygame.K_2:
          maps.sort(key=os.path.getctime, reverse=True)
          sp.speak(f'sort by recent date time.', 1)
          say = 1
        if event.key == pygame.K_3:
          maps.sort(key=os.path.getctime,)
          sp.speak(f'sort previews by date time.', 1)
          say = 1
        if event.key == pygame.K_UP:
          x = basics.selector(maps, x, go='up')
          say = 1
        if event.key == pygame.K_DOWN:
          x = basics.selector(maps, x, go='down')
          say = 1
        if event.key == pygame.K_HOME:
          x = 0
          loadsound('s1')
          say = 1
        if event.key == pygame.K_END:
          x = len(maps) - 1
          loadsound('s1')
          say = 1
        if event.key == pygame.K_PAGEUP:
          x -= 10
          if x < 0: x = 0
          loadsound('s1')
          say = 1
        if event.key == pygame.K_PAGEDOWN:
          x += 10
          if x >= len(maps): x = len(maps) - 1
          loadsound('s1')
          say = 1
        if event.key == pygame.K_RETURN:
          if maps:
            file = open(maps[x], 'rb')
            world = pickle.loads(file.read())
  
            height = world.height
            width = world.width
            east = world.east
            west = world.west
            ext = '.map'
            pos = world.map[0]
            scenary = world.map
            return
          else:
            sp.speak(empty_t, 1)
            loadsound('errn1')
        if event.key == pygame.K_ESCAPE:
          return



def map_init():
  global east, ext, height, name, pos, scenary, west, width, world

  world = World()
  ext = '.map'
  width = 40
  height = 40
  world.map = [Terrain() for i in range(width * height)]
  for t in world.map:
    t.soil = Ocean()
    t.surf = EmptySurf()
    t.scenary = world.map
  east = world.map[width - 1:len(world.map):width]
  world.east = world.map[width - 1:len(world.map):width]
  west = world.map[0:len(world.map):width]
  world.west = world.map[0:len(world.map):width]
  world.height = height
  world.width = width
  map_cords(world.map, width)
  world.name = naming()
  world.ext = ext

  map_cords(world.map, width)
  pos = world.map[0]
  scenary = world.map
  save_map()



def map_cords(item, width):
  ending = width
  num = 1
  starting = 0
  y = 1
  while starting < len(item):
    x = 1
    for t in item[starting:ending]:
      t.x = x
      t.y = y
      t.cords = f'({t.x}, {t.y})'
      x += 1
    starting += width
    num += 1
    ending *= num
    y += 1



def map_movement(event):
  global pos, sayland
  if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
    if pos not in scenary[:width]:
      play_stop()
      movepos(value=-width)
    else:
      loadsound('errn1')
  if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
    if pos not in scenary[len(scenary) - width:]:
      play_stop()
      movepos(value=width)
    else:
      loadsound('errn1')
  if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
    if pos not in west:
      movepos(value=-1)
    else:
      loadsound('errn1')
  if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
    if pos not in east:
      movepos(value=1)
    else:
      loadsound('errn1')



def map_update(nation, scenary, editing=0):
  if editing == 0:
    scenary[0].pos_sight(nation, scenary)
    [it.update(nation) for it in scenary]
  elif editing:
    for it in scenary: it.sight = 1
    pos.update(nation)



def menu_building(pos, nation, sound='in1'):
  [i.update(nation) for i in nation.map]
  pos.pos_sight(nation, nation.map)
  items = [i for i in pos.buildings if i.nation == nation or nation in i.nations]
  items.insert(0, f'{build_t}')
  if pos.city: pos.city.update()
  sleep(loadsound(sound) / 2)
  say = 0
  sp.speak(f'{buildings_t}.')
  x = 0
  while True:
    sleep(0.01)
    if say:
      items = [i for i in pos.buildings if i.nation == nation or nation in i.nations]
      items.insert(0, f'{build_t}')
      if x >= len(items): x = len(items) - 1
      if isinstance(items[x], str): sp.speak(f'{items[x]}.')
      else:
        if items[x].resource_cost[0] == items[x].resource_cost[1]:
          sp.speak(f'{items[x]} ({items[x].type}).')
        else:
          sp.speak(f'{items[x]} ({items[x].type}).')
          itm = items[x]
          time_cost = (itm.resource_cost[1] - itm.resource_cost[0]) / pos.city.resource_total
          time_cost = ceil(time_cost)
          sp.speak(f'{int(items[x].resource_cost[0]/items[x].resource_cost[1]*100)}%.')
          if items[x].nation == nation: sp.speak(f'{in_t} {time_cost} {turns_t}.')
      say = 0

    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_i:
          if isinstance(items[x], str) == False: info_building(items[x])
        if event.key == pygame.K_u  :
          if isinstance(items[x], str) == False and items[x].is_complete and items[x].upgrade:
            item = get_item2(items1=items[x].upgrade, msg='mejorar')
            if item: 
              if item.check_tile_req(pos):
                if item.gold > nation.gold:
                  loadsound('errn1')
                  return
                items[x].improve(item)
                say = 1
              else: sleep(loadsound('errn1'))
        if event.key == pygame.K_UP:
          x = basics.selector(items, x, go="up")
          say = 1
        if event.key == pygame.K_DOWN:
          x = basics.selector(items, x, go="down")
          say = 1
        if event.key == pygame.K_HOME:
          x = 0
          say = 1
        if event.key == pygame.K_END:
          x = len(items) - 1
          say = 1
        
        if event.key == pygame.K_DELETE:
          if items[x].type == city_t or items[x].resource_cost[0] == items[x].resource_cost[1]:
            loadsound('errn1')
            continue
          items[x].pos.buildings.remove(items[x])
          items[x].nation.gold += items[x].gold
          sleep(loadsound('set7')//2)
        if event.key == pygame.K_RETURN:
          # construir.
          if isinstance(items[x], str) and pos.city and pos.nation == nation:
            building = create_building(pos.city, nation.av_buildings)
            if building:
              if building.can_build() == 0:
                continue
              pos.city.add_building(building, pos)
            items += [i for i in pos.buildings if i not in items]
            say = 1
        if event.key == pygame.K_DELETE:
          pass
        if event.key == pygame.K_F12:
          sp.speak(f'debug on.', 1)
          sp.speak(f'debug off.', 1)
        if event.key == pygame.K_ESCAPE:
          sleep(loadsound('back1') / 2)
          return



def menu_city(itm, sound='in1'):
  global city, filter_expand
  loadsound(sound)
  itm.nation.update(nation.map)
  say = 1
  x = 0
  while True:
    sleep(0.05)
    if say:
      prod = empty_t
      grouth_total = round(itm.food_total * 100 / itm.pop - 100, 1)
      if itm.production:
        progress = int(ceil(itm.prod_progress / itm.resource_total))
        prod = f'{itm.production[0]} {in_t} {progress} {turns_t}.'
      lista = [
        f'{itm.nick}, {itm.name}.',
        f'{training_t} {prod}',
        f'{food_t} {itm.food_need} {of_t} {itm.food_total} ({grouth_total}%).',
        f'{resources_t} {itm.resource_total}.',
        f'{buildings_t} {len(itm.buildings)}.',
        f'{income_t} {itm.income_total}, {upkeep_t} {itm.upkeep}, {total_t} {itm.income_total-itm.upkeep}.',
        f'{public_order_t} {round(itm.public_order_total, 1)}.',
        f'{grouth_t} {round(itm.grouth_total,1)}%.',
        f'{population_t} {itm.pop}, ({itm.pop_percent}%).',
        f'militar {itm.pop_military}, ({itm.military_percent}%).',
        f'total {int(itm.pop_total)}.',
        f'{size_t} {len(itm.tiles)}.',
        ]

      sp.speak(lista[x])
      say = 0

    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_F1:
          sp.speak(f'defense total {itm.defense_total}.', 1)
          sp.speak(f'defense total percent {itm.defense_total_percent}.')
          sp.speak(f'defense_min {itm.defense_min}.')
        if event.key == pygame.K_F2:
          sp.speak(f'seen threat {itm.seen_threat}.', 1)
        if event.key == pygame.K_UP:
          x = basics.selector(lista, x, go="up")
          say = 1
        if event.key == pygame.K_DOWN:
          x = basics.selector(lista, x, go="down")
          say = 1
        if event.key == pygame.K_HOME:
          x = 0
          say = 1
        if event.key == pygame.K_END:
          x = len(lista) - 1
          say = 1
        if event.key == pygame.K_RETURN:
          if training_t in lista[x]:
            all_av_units = [i for i in itm.all_av_units]
            all_av_units.sort(key=lambda x: x.resource_cost)
            item = train_unit(itm, all_av_units, msg='entrenar')
            if item:
              itm.train(item)
              itm.update()
              itm.nation.update(scenary)
          if size_t in lista[x]:
            filter_expand = 1
            city = itm
            loadsound('set5')
            return
        if event.key == pygame.K_DELETE:
          if training_t in lista[x]:
            if itm.production:
              itm.add_pop(itm.production[0].pop)
              if itm.production[0].gold > 0:
                itm.nation.gold += itm.production[0].gold
              del(itm.production[0])
              if itm.production:
                itm.prod_progress = itm.production[0].resource_cost
              loadsound('set1')
              sp.speak(f'{deleted_t}.')
              itm.update()
              itm.nation.update(scenary)
        if event.key == pygame.K_F12:
          sp.speak(f'debug on.', 1)
          sp.speak(f'debug off.', 1)
        if event.key == pygame.K_ESCAPE:
          sleep(loadsound('back1') / 2)
          return



def menu_nation(nation, sound='book_open01'):
  global sayland
  nation.set_seen_nations()
  sleep(loadsound(sound) * 0.5)
  x = 0
  nations = [nation]
  nations += nation.seen_nations
  say = 1
  while True:
    sleep(0.01)
    if say:
      sp.speak(f'{nations[x]}', 1)
      sp.speak(f'{ranking_t} {nations[x].score}.')
      say = 0

    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
          x = basics.selector(nations, x, go="up")
          say = 1
        if event.key == pygame.K_DOWN:
          x = basics.selector(nations, x, go="down")
          say = 1
        if event.key == pygame.K_HOME:
          x = 0
          say = 1
        if event.key == pygame.K_END:
          x = len(nations) - 1
          say = 1
        if event.key == pygame.K_1:
          sp.speak(f'scouts {len(nations[x].units_scout)}',1)
        if event.key == pygame.K_2:
          sp.speak(f'comms {len(nations[x].units_comm)}',1)
        if event.key == pygame.K_F12:
          sp.speak(f'pdb on.')
          Pdb().set_trace()
          sp.speak(f'debug off.', 1)
        if event.key == pygame.K_ESCAPE:
          loadsound('back1')
          sayland = 1
          return 



def menu_unit(items, sound='in1'):
  global pos, sayland
  loadsound(sound)
  items.sort(key=lambda x: x.ranking, reverse=True)
  items.sort(key=lambda x: x.pos.get_distance(x.pos, nation.cities[0].pos))
  items.sort(key=lambda x: x.pos.around_threat, reverse=True)
  say = 1
  x = 0
  while True:
    sleep(0.01)
    if say:
      play_stop()
      if items:
        if items[x].pos.around_threat: loadsound('notify12')
        if items[x].nick: sp.speak(f'{items[x].nick}.')
        sp.speak(f'{items[x].units, items[x].name}.')
        if items[x].pos.city: sp.speak(f'en {items[x].pos.city}.')
        else:
          sp.speak(f'{in_t} {items[x].pos}.')
          sp.speak(f'{items[x].pos.cords}.')
        
      else: sp.speak(f'{empty_t}.')
      say = 0

    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_1:
          if items[x].nick: sp.speak(f'{items[x].nick}.')
          sp.speak(f'{items[x]}.')
        if event.key == pygame.K_2:
          if items[x].pos.city: sp.speak(f'{items[x].pos.city}.')
          sp.speak(f'{items[x].pos}, {items[x].pos.cords}.')
          if items[x].pos.nation: sp.speak(f'{items[x].pos.nation}.')
        if event.key == pygame.K_3:
          sp.speak(f'mp {items[x].mp[0]} {of_t} {items[x].mp[1]}.')
        if event.key == pygame.K_4:
          sp.speak(f'{defense_t} {items[x].pos.defense}, {threat_t} {items[x].pos.around_threat}.')
        if event.key == pygame.K_5:
          sp.speak(f'{food_t} {items[x].pos.food_need} {of_t} {items[x].pos.food}.')
        if event.key == pygame.K_6:
          if items[x].pos.pop:
            sp.speak(f'{population_t} {items[x].pos.pop}.')
            sp.speak(f'{public_order_t} {items[x].pos.public_order}.')
        if event.key == pygame.K_i:
          if items: item_info(items[x], nation)
        if event.key == pygame.K_UP:
          x = basics.selector(items, x, go="up")
          say = 1
        if event.key == pygame.K_DOWN:
          x = basics.selector(items, x, go="down")
          say = 1
        if event.key == pygame.K_HOME:
          x = 0
          loadsound('s1')
          say = 1
        if event.key == pygame.K_END:
          x = len(items) - 1
          loadsound('s1')
          say = 1
        if event.key == pygame.K_RETURN:
          if items:
            pos = items[x].pos
            sayland = 1
            sleep(loadsound('set6') / 2)
            return
        if event.key == pygame.K_F12:
          sp.speak(f'debug on.', 1)
          sp.speak(f'debug off.', 1)
        if event.key == pygame.K_ESCAPE:
          sleep(loadsound('back1') / 2)
          return



def movepos(value):
  global pos, sayland, x, y, z
  if move and scenary[scenary.index(pos) + value] not in move:
    loadsound('errn1')
    return
  play_stop()
  # if unit == []:
    # loadsound('mov6')
  if rng: loadsound('in1')
  elif unit:
    sp.speak(f'move', 1)
  if filter_expand == 1:
    new_pos = scenary[scenary.index(pos) + value]
    sq = new_pos.get_near_tiles(1)
    go = 0
    for s in sq:
      if s.nation == nation: go = 1
    if go == 0:
      error(msg='no puede expandir allí.')
      return
  pos = scenary[scenary.index(pos) + value]
  sayland = 1
  x = -1
  y = 0



def move_far(itm):
  logging.debug(f'{itm} mueve lejos')
  goto = itm.goto[0][1]
  
  pos = itm.pos
  
  sq = itm.pos.get_near_tiles(1)
  # logging.debug(f'{len(sq)} terrenos iniciales.')
  if goto.x > pos.x:
    # logging.debug(f'al este.')
    sq = [ti for ti in sq if ti.x > pos.x]
  if goto.x < itm.pos.x:
    # logging.debug(f'al oeste.')
    sq = [ti for ti in sq if ti.x < itm.pos.x]
  
  if goto.y < pos.y:
    # logging.debug(f'al norte.')
    sq = [ti for ti in sq if ti.y < pos.y]
  if goto.y > pos.y:
    # logging.debug(f'al sur.')
    sq = [ti for ti in sq if ti.y > pos.y]
  
  sq = [ti for ti in sq if ti.soil.name in itm.soil and ti.surf.name in itm.surf
        and ti != itm.pos]
  shuffle(sq)
  sq.sort(key=lambda x: x.cost <= itm.mp[1], reverse=True)
  sq.sort(key=lambda x: x.nation == itm.nation, reverse=True)
  # logging.debug(f'{len(sq)} terrenos finales.')
  set_favland(itm, sq)
  
  if roll_dice(2) <= itm.fear:
    # logging.debug(f'ordena por fear.')
    sq.sort(key=lambda x: x.threat)
    sq.sort(key=lambda x: x.around_threat)
  if sq:
    move_set(itm, sq[0])
  else:
    logging.debug(f'{itm} en {itm.pos} {itm.pos.cords}. no hay donde mover.')
    sq = itm.goto[0][1].get_near_tiles(2)
    sq = [ti for ti in sq if ti.soil.name in itm.soil and ti.surf.name in itm.surf
        and ti != itm.pos and ti in itm.nation.map]
    move_set(itm, choice(sq))



def move_set(itm, goto):
  itm.garrison = 0
  if (isinstance(goto, Terrain)
      and itm.can_pass(goto)):
    if itm.can_fly: cost = goto.cost_fly
    elif itm.can_fly == 0:
      cost = goto.cost
      if itm.forest_survival and goto.surf.name == forest_t: cost -= 1
      elif itm.mountain_survival and (goto.surf.name in mountain_t or goto.hill): cost -= 1
      elif itm.swamp_survival and goto.surf.name == swamp_t: cost -= 1
      elif ((goto.surf.name in [forest_t, swamp_t] or goto.hill) and mounted_t in itm.traits):
        itm.mp[0] -= 1
    if itm.goto == []: itm.goto.append([cost, goto])
    elif itm.goto: itm.goto.insert(0, [cost, goto])
    move_unit(itm)
  elif isinstance(goto, str):
    itm.goto.append(goto)
    move_unit(itm)



def move_unit(itm, info=1):
  itm.update()
  logging.debug(f'move_unit a {itm}.')
  goto = itm.goto[0][1]
  if goto == itm.pos:
    itm.goto = []
    itm.stopped = 1
    msg = f'{itm} {itm.nation}  detenido.'
    itm.log[-1].append(msg)
    if info: logging.debug(msg)
    if itm.show_info:
      speak(msg=msg)
    return 0
  if itm.going == 0:
    if itm.check_ready() == 0:
      if info: logging.debug(f'go = 0.')
      return
  if isinstance(itm.goto[0], list):
    msg = f'{itm} ({itm.nation}) se moverá a {itm.goto[0][1]}., {itm.goto[0][1].cords}'
    itm.log[-1].append(msg)
    if info: logging.debug(msg)
    if info: logging.debug(f'mp {itm.mp[0]} de {itm.mp[1]}, costo {itm.goto[0][0]}.')
    if itm.group: 
      if info: logging.debug(f'lider, grupo {len(itm.group)}.')
    elif itm.leader: 
      if info: logging.debug(f'sigue a {itm.leader}.')
    while (itm.goto and itm.mp[0] > 0 and itm.hp_total > 0
           and isinstance(itm.goto[0], list)):
      goto = itm.goto[0][1]
      square = itm.pos.get_near_tiles(1)
      if goto not in square:
        move_far(itm)
      
      elif goto in square:
        if itm.goal and goto == itm.goal[1]:
          ai_move_group(itm)
          return
        itm.going = 1
        if basics.roll_dice(1) >= 4: 
          itm.group.sort(key=lambda x: x.rng, reverse=True)
        for i in itm.group:
          if i.pos != itm.goto[0][1] and i.goto == []:
            if info: logging.debug(f'seguidor {i} se mueve')
            move_set(i, goto)
        moving_unit(itm)
      
  elif isinstance(itm.goto[0], str):
    if itm.goto[0] == 'attack':
      del(itm.goto[0])
      auto_attack(itm)
      if itm.hp_total < 1: return
    elif itm.goto[0] == 'gar':
      itm.garrison = 1
      if info: logging.debug(f'{itm} defiende {itm.pos}.')
      del(itm.goto[0])
    elif itm.goto[0] == 'join':
      basics.ai_join_units(itm)
      if info: logging.debug(f'{itm} joins.')
      del(itm.goto[0])
    elif itm.goto[0] == 'set':
      placement = choice(itm.buildings)
      if placement(itm.nation, itm.pos).check_tile_req(itm.pos):
        itm.nation.add_city(placement, itm)
      else: logging.warning(f'{itm} no puede fundar aldea en {itm.pos}.')



def moving_unit(itm, info=0):
  if info: logging.debug(f'mueve cerca {itm} {itm.id}.')
  if itm.goto == []: 
    if info: logging.debug(f'sin goto')
    return
  
  mp = itm.mp[0]
  cost = itm.goto[0][0]
  goto = itm.goto[0][1]
  if info: logging.debug(f'mp {mp}, cost {cost}.')
  # menor.
  if mp < cost:
    if info: logging.debug(f'menor.')
    itm.goto[0][0] -= itm.mp[0]
    itm.mp[0] = 0
    if itm.ai == 0: loadsound('set4')
  # mayor
  elif mp >= cost:
    if info: logging.debug(f'mayor.')
    itm.mp[0] -= cost
    itm.garrison = 0
    itm.set_hidden(goto)
    if info: logging.debug(f'hidden {itm.hidden}.')
    if itm not in itm.pos.units: 
      if info: logging.debug(f'not in position.')
    # chekeo de enemigos.
    if check_enemy(itm, goto, goto.is_city):
      if info: logging.debug(f'hay enemigos.')
      veredict = combat_menu(itm, goto)
      itm.update()
      if info: logging.debug(f'hidden {itm.hidden}.')
      if veredict == 0:
        # itm.pos.update(itm.nation)
        if info: logging.debug(f'veredict {veredict}.')
        return
      
      if check_enemy(itm, goto, goto.is_city):
        if info: logging.debug(f'still enemies.')
        del(itm.goto[0])
        return
      
    unit_arrival(goto, itm)



def naming(sound='back3'):
  say = 1
  name = str()
  sleep(loadsound(sound) / 2)
  sp.speak('type a name')
  while True:
    if say:
      sp.speak(name)
      say = 0

    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
        if len(name) > 0: name += event.unicode
        say = 1
      if event.type == pygame.KEYDOWN and event.key != pygame.K_BACKSPACE:
        if event.unicode.isalnum(): name += event.unicode
        say = 1
      if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
        if len(name) > 0:
          sp.speak(f'{name[-1]}.', 1)
          name = name[:-1]
          say = 1
        else:
          loadsound("errn1")
      if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
        sleep(loadsound('back1'))
        if name:return name
        else: return None
      if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        sleep(loadsound("back1") / 2)
        return



def nation_init():
  while True:
      done = 1
      for nat in world.nations: 
        if nat.ai == 0: nat.show_info = 1
        nation_start_position(nat, world.map)
      for n in world.nations:
        if n.pos == None: done = 0
      if done:
        for n in world.nations: nation_set_start_position(n) 
        break



def nation_start_position(itm, tiles):
  global players, pos
  logging.info(f'inicio de posición de {itm}.')
  itm.pos = None
  unallowed_tiles = [n.pos for n in world.nations if n.pos]
  tls = [t for t in tiles
         if t.soil.name in itm.soil and t.surf.name in itm.surf
         and t.hill in itm.hill]
  logging.debug(f'casillas totales {len(tls)}.')
  shuffle(tls)
  [t.update() for t in tls]
  for tl in tls:
    tl.set_around(itm)
    # logging.debug(f'checking {tl} {tl.cords}. around ocean {tl.around_coast}.')
    if itm.is_allowed_tiles(tl) == 0: 
      # logging.debug(f'fallo allowed {tl.cords}.')
      continue
    if itm.is_unallowed_tiles(tl): 
      # logging.debug(f'fallo unallowed {tl.cords}.')
      continue
    done = 1
    # logging.debug(f'done.')
    sq = tl.get_near_tiles(6)
    for t in unallowed_tiles:
        if t in sq: 
          done = 0
          logging.debug(f'unallowed tiles.')
    
    # si listo.
    if done:
      itm.pos = tl
      logging.info(f'{itm} inicia en {tl} {tl.cords}.')
    
    if done == 1: break



def nation_start_placement(nation):
  logging.debug(f'{nation} start placement in {nation.pos}.')
  pos = nation.units[0].pos
  settler = nation.initial_settler(nation)
  settler.pos = pos
  nation.add_city(nation.initial_placement, settler)



def nation_set_start_position(nation):
  logging.debug(f'{nation} set start position in {nation.pos}.')
  pos = nation.pos
  for uni in nation.start_units:
        item = uni(nation)
        item.ai = nation.ai
        item.pos = pos
        item.show_info = nation.show_info
        nation.units.append(item)
        pos.units.append(item)



def new_turn():
  global turns, sayland, ambient
  ambient = world.ambient
  ambient.update()
  last_day_night = ambient.day_night[0]
  [i.update(scenary) for i in world.nations]
  logging.debug(f'nuevo turno.')
  if world.turn > 0:
    if ambient.time[0] >= 6:
      ambient.time[0] = -1
      if ambient.week >= 1:
        ambient.week = 0
        if ambient.month[0] >= 11:
          ambient.month[0] = -1
          ambient.year += 1
        ambient.month[0] += 1
      ambient.week += 1
      
    if ambient.month[0] in [11, 0, 1]:
      ambient.season[0] = 0
    elif ambient.month[0] in [2, 3, 4]:
      ambient.season[0] = 1
    elif ambient.month[0] in [5, 6, 7]:
      ambient.season[0] = 2
    elif ambient.month[0] in [8, 9, 10]:
      ambient.season[0] = 3
      
    ambient.time[0] += 1
    
    if ambient.season[0] in [0, 3]:
      ambient.day_night[0] = 0
      if ambient.time[0] >= 3: ambient.day_night[0] = 1
    elif ambient.season[0] in [1, 2]:
      ambient.day_night[0] = 0
      if ambient.time[0] >= 4: ambient.day_night[0] = 1
  world.turn += 1
  world.log += [[f'{turn_t} {world.turn}.']]
  world.ambient.update()
  ambient = world.ambient
  
  [i.start_turn() for i in world.map]
  for n in world.nations:
    n.start_turn()
  
  
  msg = f'{turn_t} {world.turn}.'
  logging.info(msg)
  logging.info(f'{ambient.stime}, {ambient.smonth}, {ambient.syear}.')
  sp.speak(msg)
  sleep(loadsound('notify14') * 0.1)
  if ambient.day_night[0] != last_day_night:
    if ambient.day_night[0] == 0: sleep(loadsound('dawn01', channel=ch4) / 3)
    if ambient.day_night[0]: sleep(loadsound('night01', channel=ch4) / 5)
  gc.collect()



def next_play():
  global nation, pos, players, sayland, unit, x
  unit = []
  x = -1
  while True:
    if world.player_num == len(world.nations):
      new_turn()
      # init = time()
      world.player_num = 0
      ai_random()
      # print(f'ai_random. {time()-init}.')

    nation = world.nations[world.player_num]
    if nation.ai == 0:
      logging.info(f'{turn_t} {of_t} {nation}.')
      start_turn(nation)
      map_update(nation, nation.map)
      if nation.cities:pos = nation.cities[0].pos
      elif nation.units: pos = nation.units[0].pos
      nation.update(scenary)
      loadsound('notify9')
      sayland = 1
      save_game()
      return
    elif nation.ai == 1:
      init = time()
      ai_play(nation)
      # print(f'ai_play. {time()-init}.')
      map_update(nation, nation.map)
      if nation.cities:pos = nation.cities[0].pos
      elif nation.units: pos = nation.units[0].pos
      sayland = 1
      save_game()
      return
    world.player_num += 1



def oportunist_attack(itm, info=1):
  logging.info(f'ataque de oportunidad de {itm}.')
  sq = itm.pos.get_near_tiles(1)
  [i.update(itm.nation) for i in sq]
  sq = [it for it in sq if it.soil.name in itm.soil and it.surf.name in itm.surf
            and it.threat > 0]
  if info: logging.debug(f'{len(sq)} casillas.')
  for s in sq:
    if roll_dice(2) >= 3 and itm.get_favland(s) == 0:
      if info: logging.debug(f'not favland.')
      continue
    ranking = itm.ranking
    if info: logging.debug(f'{ranking=:}.')
    if itm.comm: ranking *= 0.6
    if s.surf.name == forest_t and itm.forest_survival == 0: 
      ranking -= ranking * 0.2
      if info: logging.debug(f'reduce by forest.')
    if s.surf.name == swamp_t and itm.swamp_survival == 0: 
      ranking -= ranking * 0.2
      if info: logging.debug(f'reduce by swamp.')
    if s.hill and itm.mountain_survival == 0: 
      ranking -= ranking * 0.2
      if info: logging.debug(f'reduce by mountain.')
    rnd = randint(round(ranking * 0.9), round(ranking * 1.2))
    if itm.nation not in world.nations: 
      rnd *= 1.5
      if info: logging.debug(f'rnd increased by random unit.')
    if info: logging.debug(f'{rnd=:}, {s.threat=:}, {s.around_threat=:}')
    if itm.fear in [5, 6]: fear = 1.5
    if itm.fear in [4, 3]: fear = 2
    if itm.fear <= 2: fear = 3
    if info: logging.debug(f'{rnd*fear=:}, {s.around_threat=:}.')
    if rnd * fear < s.around_threat:
      if info: logging.debug(f'afraid.')
      continue
    if rnd > s.threat and s.cost <= itm.mp[0]:
      msg = f'{itm} en {itm.pos} aprobecha y ataqua a {s}.'
      if info: logging.debug(msg)
      itm.log[-1].append(msg)
      move_set(itm, s)
      move_set(itm, 'attack')
      return 1



def play_sound(unit, sound, ch=0):
  if pos == unit.pos:
    if ch and ch.get_busy() == False:
      loadsound(sound, ch)
    else: loadsound(sound)


def random_move(itm, scenary, sq=None, value=1, info=1):
  logging.debug(f'movimiento aleatoreo para {itm} en {itm.pos}, {itm.pos.cords}.')
  done = 0
  if sq == None:
    sq = itm.pos.get_near_tiles(value)
    sq = [it for it in sq if itm.can_pass(it)]
    if info: logging.debug(f'{len(sq)} casillas iniciales.')
  if sq:
    if itm.city and itm.nation in world.random_nations: sq = [it for it in sq if it.get_distance(it,itm.city.pos) <= itm.mp[1]]
    print(f'{len(sq)= }.')
    done = 1
    fear = 0
    move = 1
    sort = 0
    shuffle(sq)
    if sq == []: 
      move_set(itm, itm.city.pos)
      return
    map_update(itm.nation, sq)
    if randint(1, 100) < itm.sort_chance:
      if info: logging.debug(f'sorted.')
      sort = 1
      [s.set_threat(itm.nation) for s in sq]
      if itm.populated_land:
        if info: logging.debug(f'casillas pobladas.')
        sq.sort(key=lambda x: x.pop, reverse=True)
      set_favland(itm, sq)
    
    if info: logging.debug(f'{itm.ranking=:}.')
    rnd = randint(round(itm.ranking * 0.9), round(itm.ranking * 1.3))
    if itm.pos.surf.name == forest_t and itm.forest_survival == 0: rnd -= rnd * 0.3
    if itm.pos.hill and itm.mountain_survival == 0: rnd -= rnd * 0.3
    if itm.pos.surf.name == swamp_t and itm.swamp_survival == 0: rnd -= rnd * 0.3
    if commander_t in itm.traits: rnd -= rnd * 0.3
    if itm.nation not in world.nations: rnd *= 1.5
    if basics.roll_dice(1) <= itm.fear:
      if info: logging.debug(f'ordena por miedo')
      fear = 1
      sq.sort(key=lambda x: x.city == None, reverse=True)
      sq.sort(key=lambda x: x.threat <= rnd, reverse=True)
      sq.sort(key=lambda x: x.around_threat <= rnd, reverse=True)
      if basics.roll_dice(1) >= 3: sq.sort(key=lambda x: x.food - x.food_need < itm.food)
      sq.sort(key=lambda x: x.defense, reverse=True)
    if itm.scout:
      if info:  logging.debug(f'ordena para exploración')
      fear = 1
      sq.sort(key=lambda x: x.has_city)
      if itm.can_fly: sq.sort(key=lambda x: x.hill, reverse=True)
      if itm.forest_survival: sq.sort(key=lambda x: x.surf.name == forest_t, reverse=True)
      elif itm.swamp_survival: sq.sort(key=lambda x: x.surf.name == swamp_t, reverse=True)
      elif itm.mountain_survival: sq.sort(key=lambda x: x.hill, reverse=True)
      if basics.roll_dice(1) >= 6: sq.sort(key=lambda x: x.hill, reverse=True)
      sq.sort(key=lambda x: x.get_distance(x, itm.city.pos), reverse=True)
    
    # casillas finales.
    sq.sort(key=lambda x: x != itm.pos, reverse=True)
    movstatus = f'fear {fear}, sort {sort}.'
    itm.log[-1].append(movstatus)
    if info: logging.debug(f'{len(sq)} casillas finales.')
    moved = 0
    for s in sq:
      if itm.fear in [6, 5]: fear = 1.5
      if itm.fear in [4, 3]: fear = 2
      if itm.fear in [2, 1]: fear = 3
      if info: logging.debug(f'{rnd*fear=:} {s.around_threat=:}.')
      if rnd * fear < s.around_threat and itm.fear >= 5: 
        if info: logging.debug(f'afraid.')
        continue
      if info: logging.debug(f'rnd {rnd} amenaza {round(s.threat)} in {s}, {s.cords}.')
      if rnd >= s.threat:
        moved = 1
        move_set(itm, s)
        break
    if moved == 0:
      msg = f'no se mueve.!'
      if info: logging.debug(msg)
      itm.log[-1].append(msg)
      itm.stopped = 1
  return done



def req_unit(itm, nation, city):
  logging.debug(f'requicitos de {itm}.')
  if city.pop < itm.pop:
    error(info=nation.show_info, msg='sin población')
    return 0
  if itm.gold > 0 and nation.gold < itm.gold:
    error(info=nation.show_info, msg='sin oro')
    return 0
  items = nation.units + nation.production
  if itm.unique and has_name(items, itm.name) == 1:
    error(info=nation.show_info, msg='unidad única.')
    return 0
  return 1



def save_map():
  global world
  speak('se guardara', slp=0.5, num=1)
  file = open(os.path.join('maps//') + world.name + ext, 'wb')
  file.write(pickle.dumps(world))
  file.close()
  speak('mapa guardado', slp=0.5)



def save_game():
  global world
  main_dir = os.getcwd() + str('/saves/')
  name = f'{world.nations[world.player_num]} {turn_t} {world.turn}'
  try:
    os.stat(main_dir)
  except:
    os.mkdir(main_dir)
    print(f'error.')
  file = open(main_dir + name + '.game', 'wb')
  file.write(pickle.dumps(world))
  file.close()



def saypos(sq):
  logging.debug(f'saypos')
  for i in sq:
    logging.debug(f'{i} {i.cords}.')



def select_item(msg, building, sound, limit=0):
  loadsound(sound)
  sp.speak(f'{msg}', 1)
  sleep(0.5)
  if len(building) == 0:
    building = [empty_t]
  say = 1
  x = 0
  while True:
    if say:
      say = 0
      if isinstance(building[x], str): sp.speak(f'{building[x]}.')
      if isinstance(building[x], str) == False: sp.speak(f'{building[x]().id[0]}.', 1)
    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
        x = basics.selector(building, x, 'up')
        say = 1
      if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
        x = basics.selector(building, x, 'down')
        say = 1
      if event.type == pygame.KEYDOWN and event.key == pygame.K_HOME:
        say = 1
        x = 0
        loadsound('s1')
      if event.type == pygame.KEYDOWN and event.key == pygame.K_END:
        say = 1
        x = len(building) - 1
        loadsound('s1')

      if event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
        sp.speak('on')
        sp.speak('off')

      if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
        if isinstance(building[x], str):
          say = 1
          continue
        if limit == 0:
          loadsound('set6')

          item = building[x]()
          return item

      if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        loadsound('back1')
        return



def set_favland(itm, sq):
  shuffle(sq)
  sq.sort(key=lambda x: itm.get_favland(x), reverse=True)
  if itm.pref_corpses: sq.sort(key=lambda x: len(x.corpses), reverse=True)



def set_group(itm):  
  logging.debug(f'set group')
  logging.debug(f'{itm} distancia a objetivo {itm.pos.get_distance(itm.pos, itm.goal[1])}.')
  units = [itm] + itm.group
  goal = itm.goal
  goto = goal[1]
  units.sort(key=lambda x: itm.pos.get_distance(goto, x.pos))
  itm = units[0]
  for i in units: logging.debug(f'distancia {itm.pos.get_distance(i.pos,goto)}.')
  units = [i for i in units if i != itm]
  itm.goal = goal
  itm.group = [i for i in units ]
  for i in units: 
    i.goal = None
    i.group = []
    i.leader = itm
  itm.leader = None
  itm.group_ranking = sum(i.ranking for i in units)
  logging.debug(f'{itm} distancia a objetivo {itm.pos.get_distance(itm.pos, itm.goal[1])}.')
  return itm



def set_logging():
  main_dir = os.getcwd() + str('/logs/')
  try:
    os.stat(main_dir)
  except:
    os.mkdir(main_dir)
    print(f'error.')



def set_near_tiles(nation, scenary):
  logging.debug(f'set_near_tiles')
  for ct in nation.cities:
    ct.tiles_near = [it for it in nation.map]
    ct.tiles_near = [it for it in ct.tiles_near if it.city == None and it.nation == None]
    ct.tiles_far = [it for it in nation.map]
    ct.tiles_far = [it for it in ct.tiles_far if it.get_distance(it, ct.pos) in [3, 4]]
    ct.tiles_far = [it for it in ct.tiles_far
                    if it.city == None and it.nation == None
                    and it.soil.name in nation.soil
                    and it.surf.name in nation.surf
                    and it.hill in ct.nation.hill]
    ct.tiles_far.sort(key=lambda x: x.mean, reverse=True)
    for ti in ct.tiles_near:
      sq = ti.get_near_tiles(1)
      go = 0
      for s in sq:
        if s.city == ct: go = 1
      if go == 0: ct.tiles_near = [it for it in ct.tiles_near if it != ti]

  nation.tiles_far = []
  for ct in nation.cities:
    if ct.tiles_far: logging.debug(f'{len(ct.tiles_far)} casillas para fundar.')
    nation.tiles_far += ct.tiles_far
    nation.tiles_far.sort(key=lambda x: x.food_value, reverse=True)
    nation.tiles_far.sort(key=lambda x: len(x.around_snations))



def set_defend_pos(defense_need, itm, pos, info=0):
  '''sent unit to defend a position.'''
  if info: logging.debug(f'set_defend {itm}.')
  if itm.ranking > defense_need * 2 and itm.squads > 1: 
    itm.split(1)
    msg = f'divided.'
    if info: logging.debug(msg)
    itm.nation.devlog[-1] += [msg]
    itm.log[-1] += [msg]
  itm.update()
  if itm.goto == [] and itm.pos == pos:
    move_set(itm, 'gar')
    defense_need -= itm.ranking
    msg = f'{itm} será guarnición.'
    if info: logging.debug(msg)
    itm.nation.devlog[-1] += [msg]
    itm.log[-1] += [msg]
    if info: logging.debug(f'necesita {round(defense_need,2)} defensa.')
    return defense_need
  elif itm.goto == [] and itm.pos != pos:
    msg = f'{itm} defenderá {pos} {pos.cords}.'
    itm.log[-1] += [msg]
    move_set(itm, pos)
    move_set(itm, 'gar')
    defense_need -= itm.ranking
    if info: logging.debug(f'necesita {round(defense_need,2)} defensa.')
    return defense_need
  elif itm.goto and  pos in itm.goto_pos:
    if info: logging.debug(f'{itm} se dirige a la ciudad.')
    defense_need -= itm.ranking
    if info: logging.debug(f'necesita {round(defense_need,2)} defensa.')
    return defense_need
  else: return defense_need



def set_settler(itm, scenary):
  logging.info(f'ajuste colono en {itm.pos}, {itm}.')
  logging.debug(f'colonos {len([i for i in nation.units if i.settler])}.units_se')
  if itm.mp[0] > 0:
    if len(itm.nation.cities) == 0:
      sq = itm.pos.get_near_tiles(1)
      done = 1
      for ti in sq:
        if ti.nation: done = 0
      logging.debug(f'done {done}.')
      if done:
        item = choice(itm.buildings)
        item = item(itm.nation, itm.pos)
        if item.can_build():
          itm.nation.add_city(item, itm)
          return 1
        else:
          random_move(itm, scenary, value=1)
    elif len(itm.nation.cities) > 0 and nation.tiles_far:
      [i.update(nation) for i in nation.tiles_far]
      nation.tiles_far.sort(key=lambda x: x.food_value, reverse=True)
      nation.tiles_far.sort(key=lambda x: len(x.around_snations))
      if len(nation.cities) < 2: nation.tiles_far.sort(key=lambda x: itm.pos.get_distance(x, itm.pos))
      for i in nation.units_scout: i.scout = 0
      if itm.pos.is_city:
        itm.pos.units.sort(key=lambda x: x.units, reverse=True)
        for i in itm.pos.units[:2]: 
          i.garrison = 0 
          i.split(1)
        
      if itm.group == []:
        logging.debug(f'sin grupo.')
        itm.create_group(int(itm.ranking*1.5))
        [unit_join_group(i) for i in itm.group]
      if itm.check_ready() :
        [i.update(nation) for i in nation.tiles_far]
        nation.tiles_far.sort(key=lambda x: x.around_threat + x.threat)
        if len(nation.cities) < 3: nation.tiles_far.sort(key=lambda x: len(x.around_nations))
        move_set(itm, nation.tiles_far[0])
        move_set(itm, 'set')
        msg = f'fundará aldea en {nation.tiles_far[0]} {nation.tiles_far[0].cords}.'
        logging.debug(msg)
        sp.speak(msg)
        sleep(1)



def game():
  # Pendiente: convertir el método game a clase. 
  global city, city_name, nation_name, terrain_name, rng, time
  global Belongs, Evt, Group, move, Name, pos, sayland, scenary, starting, xy
  global nation, num, unit, world, x, y, z
  global filter_expand
  global hell_nation, wild_nation
  global PLAYING
  global alt, ctrl, shift
  
  # change()
  if startpos: pos = scenary[startpos]
  Belongs = None
  city = None
  city_name = ''
  Evt = None
  filter_expand = 0
  Group = []
  move = []
  Name = None
  nation_name = ''
  PLAYING = True
  rng = None
  starting = None
  terrain_name = None
  unit = []
  xy = []
  sayland = 1
  x = -1  # selector de unidades.
  y = 0  # selector de ciudades.
  if mapeditor == 0 and new_game == 1:
    world.log = [[f'{turn_t} {world.turn}.']]
    # dificultad.
    world.ambient = ambient
    world.difficulty = DIFFICULTY
    world.difficulty_type = 'dynamic'
    #Random Nations.
    world.random_nations = RANDOM_FACTIONS
    #BuildingsRandom .
    world.random_buildings = random_buildings
    world.buildings_value = buildings_value
    scenary = world.map
    Unit.ambient = world.ambient
    Nation.world = world
    # choose_nation():
    world.nations = NATIONS
    shuffle(world.nations)
    world.cnation = world.nations[0]
    world.season_events()
    for t in scenary: t.world = world
    
    nation_init()
    [nt.start_turn() for nt in world.nations]
    [nation_start_placement(nt) for nt in world.nations]
    world.add_random_buildings(world.buildings_value)
    new_turn()
    next_play()
  elif new_game == 0:
    nation = world.nations[world.player_num]
    if nation.cities: pos = nation.cities[0].pos
    else: pos = nation.units[0].pos
    Unit.ambient = world.ambient
    scenary = world.map
  elif mapeditor:
    sp.speak('modo editor.')
    sleep(0.3)
    
    nation = Empty()
    nation.name = 'editor'
    nation.map = world.map
  if pos not in world.map: inside = 1
  elif pos in world.map: inside = 0
  while PLAYING:
    sleep(0.01)
    if mapeditor > 0:
      n1 = Empty()
      n1.map = scenary
      players = Empty()
      world.nations = [n1]
    terrain_info(pos, world.nations[world.player_num])
    
    pressed = list(pygame.key.get_pressed())
    alt = pressed[308]
    ctrl = pressed[305] or pressed[306]
    shift = pressed[303] or pressed[304]
    for event in pygame.event.get():
      map_movement(event)
      control_global(event)
      if mapeditor == 0:
        control_game(event)
        control_basic(event)
      elif mapeditor == 1:
        control_editor(event)



def start():
  global mapeditor, new_game
  if mapeditor == 0:
    loadsound('back1')
    run = 1
    set_logging()
    say = 1
    items = [new_t, load_t, about_t, exit_t]
    x = 0
    if dev_mode: sp.speak(f'dev mode.')
    sleep(1)
    while run:
      sleep(0.01)
      if say:
        sp.speak(f'{items[x]}.', 1)      
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
          if event.key == pygame.K_END:
            x = len(items) - 1
            say = 1
          if event.key == pygame.K_RETURN:
            if items[x] == new_t: 
              new_game = 1
              loading_map('maps//', '/*.map')
            if items[x] == load_t: 
              new_game = 0 
              loading_map('saves//', '/*.game')
            if items[x] == exit_t: return
            if 'world' in globals():
              run = 0
              game()
  if mapeditor == 1:
    loading_map('maps//', '/*.map')
    if world: game()
  if mapeditor == 2:
    mapeditor = 1
    map_init()
    game()



def start_turn(nation):
  global sayland
  if pygame.key.get_focused(): sp.speak(f'{nation}.', 1)
  sp.speak(f'{ambient.day_night[1][ambient.day_night[0]]}.')
  sayland = 1
  if nation.map: nation.map[0].pos_sight(nation, nation.map)
  else: scenary[0].pos_sight(nation, scenary)
  map_update(nation, nation.map)
  nation.update(nation.map)
  nation.set_hidden_buildings()
  # ingresos.
  nation.set_income()
  # ciudades.
  logging.debug(f'ciudades.')
  for city in nation.cities:
    city.population_change()
    city.update()
    city.check_building()
    city.check_training()
    city.status()
    city.update()
  
  # initial placement.
  if nation.cities == [] and world.turn == 1: 
    nation_start_placement(nation)
  # Unidades.
  #for uni in nation.units: uni.log.append([f'{turn_t} {world.turn}.'])
  logging.debug(f'unidades.')
  for uni in nation.units:
    uni.start_turn()
    unit_restoring(uni)
    uni.set_hidden(uni.pos)
    if uni.goto: move_unit(uni)
    unit_attrition(uni)
    uni.maintenanse()
  ai_explore(nation, scenary)
  nation.update(nation.map)
  nation.set_seen_nations()

  # otros.
  sleep(loadsound('notify10') / 2)
  warning_enemy(nation, nation.map)



def speak(msg, slp=0, num=0, sound=None):
  if sound: loadsound(sound)
  logging.debug(msg)
  sp.speak(msg, num)
  if slp: sleep(slp)



def take_city(itm):
  logging.debug(f'{itm} takes city {itm.pos}.')
  msg = f'{itm} {itm.nation} toma ciudad de {itm.pos.city}.'
  itm.nation.log[-1].append(msg)
  itm.pos.nation.log[-1].append(msg)
  logging.info(msg)
  city = itm.nation.av_cities[0](itm.nation, itm.pos)
  # city.set_name()
  city.name = itm.pos.city.name
  city.tiles = itm.pos.city.tiles
  itm.pos.city.nation.cities.remove(itm.pos.city)
  itm.pos.buildings.remove(itm.pos.city)
  for t in itm.pos.city.tiles:
    t.nation = itm.nation
    t.city = city
    t.pop -= randint(20, 40) * t.pop // 100
    t.unrest += randint(40, 80)
    for b in t.buildings:
      if b.name in [bu.name for bu in itm.nation.av_cities]: 
        b.nation = itm.nation
  itm.pos.city = city
  itm.pos.buildings += [city]
  city.update()
  itm.nation.cities.append(itm.pos.city)
  itm.nation.update(scenary)



def terrain_info(pos, nation):
  global city_name, local_units, nation_name, terrain_name, sayland
  if sayland:
    sayland = 0
    if mapeditor == 0:
      pos.pos_sight(nation, nation.map)
      pos.update(nation)
      # sq = pos.get_near_tiles(10)
      # map_update(nation, sq)
      # [it.update(nation) for it in scenary]
      # nation.update(scenary)
    elif mapeditor:
      map_update(nation, scenary, 1)
    if mapeditor in [0, 1]:
      if pos.events: sleep(loadsound('notify27', vol=(0.5, 0.5), channel=ch3) * 0.1)
      if pos.nation == nation and pos.blocked: sleep(loadsound('nav2') * 0.3)
      elif pos.nation == nation:
        sleep(loadsound('nav1') * 0.3)
      elif pos.nation != nation:
        if pos.nation == None and pos.sight: sleep(loadsound('nav4') * 0.3)
      #if pos.name and pos.sight: sp.speak(f'{pos.name}.', 1)
      if pos in nation.map:
        pos.play_ambient()
        
        if pos.threat > 0 and pos.sight:
          sp.speak(f'hostiles.')
      if pos.defense > 0:
        pass
      if pos in nation.map:
        if pos.city == None or pos.city.nick != city_name: 
          city_name = None
          if pos.city: 
            city_name = pos.city.nick
            if pos.sight or pos in nation.nations_tiles:
              sp.speak(f'{city_name}')
              loadsound('notify20')
        if pos.nation == None or str(pos.nation) != nation_name: 
          nation_name = None
          if pos.nation: 
            nation_name = str(pos.nation)
            if nation_name and pos.sight or pos in nation.nations_tiles:
              sp.speak(f'{nation_name}')
              loadsound('notify20')
        if pos.sight == 0:
          sp.speak(f'{fog_t}.')
          if pos not in nation.nations_tiles:
            city_name = None
            nation_name = None
        if pos.sight:
          local_units = get_units(pos, nation)
          local_units.sort(key=lambda x: x.damage, reverse=True)
          local_units.sort(key=lambda x: x.units, reverse=True)
          local_units.sort(key=lambda x: x.scout)
          local_units.sort(key=lambda x: x.settler)
          local_units.sort(key=lambda x: x.mp[0], reverse=True)
        if filter_expand == 0:
          if local_units and pos.sight: sp.speak(f'{squads_t} {len(local_units)}.')
          if pos.corpses and pos.sight:
            sp.speak(f'{corpses_t} {sum(sum(i.deads) for i in pos.corpses)}.')
        sp.speak(f'{pos}')
        if pos.is_city and (pos.sight or pos in nation.nations_tiles):
          sp.speak(f'{pos.city}')
          loadsound('working1')
        if filter_expand:
          cost = get_tile_cost(city, pos)
          sp.speak(f'{cost} {gold_t}.')
        if pos.sight or pos in nation.nations_tiles: 
          if pos.buildings:
            buildings = [b for b in pos.buildings 
                         if b.type == city_t or nation in b.nations or nation == b.nation ] 
            if buildings: sp.speak(f'{len(buildings)} {buildings_t}.')
          if pos.buildings and [b for b in pos.buildings if b.resource_cost[0] < b.resource_cost[1] and b.nation == nation]: 
            loadsound('construction1', channel=ch4)
          if pos.events:
            for ev in pos.events:
              sp.speak(f'{ev.name}')
              if ev == pos.events[-1]: sp.speak('.')
              else: sp.speak(',')
      else:
        local_units = []
        sp.speak(f'terra incognita.')
        city_name = None
        nation_name = None



def train_unit(city, items, msg, sound='in1'):
  sleep(loadsound(sound) / 2)
  x = 0
  say = 1
  sp.speak(msg, 1)
  while True:
    sleep(0.05)
    if say:
      item = items[x](nation)
      item.update()
      prod = item.resource_cost / city.resource_total
      prod = int(ceil(prod))
      sp.speak(f'{item} {in_t} {prod}.', 1)
      sp.speak(f'{cost_t} {item.gold}. {upkeep_t} {item.upkeep*item.units}.')
      sp.speak(f'{resources_t} {item.resource_cost}.')
      sp.speak(f'{population_t} {item.pop}.')
      say = 0
      
    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_i:
          item_info(item, nation)
          say = 1
        if event.key == pygame.K_UP:
          x = basics.selector(items, x, go='up')
          say = 1
        if event.key == pygame.K_DOWN:
          x = basics.selector(items, x, go='down')
          say = 1
        if event.key == pygame.K_RETURN:
          if req_unit(item, nation, city):
            return item
          else: error()
        if event.key == pygame.K_F12:
          sp.speak(f'debug on.', 1)
          sp.speak(f'debug off.', 1)
        if event.key == pygame.K_ESCAPE:
          sleep(loadsound('back1') / 2)
          return



def unit_arrival(goto, itm, info=0):
  if itm.hp_total < 1:
    logging.warning(f'arrival. {itm} no tiene salud.')
    return
  
  itm.pos.units.remove(itm)
  goto.units.append(itm)
  itm.pos = goto
  del(itm.goto[0])
  itm.can_retreat = 1
  itm.going = 0
  msg = f'{itm} llega a ({goto}, {goto.cords}.'
  if info: logging.debug(msg)
  itm.log[-1].append(msg)
  if itm.show_info and itm.goto == [] and itm.scout == 0: sleep(loadsound('walk_ft1') / 5)
  if itm.show_info: goto.pos_sight(itm.nation, itm.nation.map)
  pos.update(itm.nation)
  check_position(itm)
  itm.set_tile_attr()
  itm.burn()
  itm.raid()
  [b.set_hidden(itm.nation) for b in itm.pos.buildings if b.type == building_t]
  [i.set_hidden(itm.pos) for i in itm.pos.units
   if i.nation != itm.nation and i.hidden] 



def unit_attrition(itm):
  if world.turn < 2 or itm.hp_total < 1: return 
  itm.pos.update(itm.nation)
  food = itm.pos.food_need - itm.pos.food
  if food >= 80: food = 80
  resolve = itm.resolve + itm.resolve_mod - round(food / 10)
  roll = basics.roll_dice(1)
  logging.debug(f'{food =: }, {resolve =: } {roll =: }.')
  if food > 0 and itm.food and roll >= resolve:
    if itm.desert_survival and itm.pos.name == waste_t and basics.roll_dice(1) >= 3:
      logging.debug(f'sobreviviente del desierto.')
      return
    try:
      itm.hp_total -= randint(1, ceil(food * itm.hp_total / 100))
    except:
      Pdb().set_trace()
    if itm.hp_total < 1:
      msg = f'{itm} se ha disuelto por atrición.'
      itm.nation.log[-1].append(msg)
      sleep(loadsound('notify18') * 0.5)



def unit_join_group(itm):
  if itm.leader and itm.pos != itm.leader.pos:
    logging.debug(f'{itm} en {itm.pos} {itm.pos.cords} busca unirse a su lider {itm.leader}.')
    if itm.goto == []: move_set(itm, itm.leader.pos)



def unit_new_turn(itm):
  logging.info(f'new turn {world.turn=:} {to_t} {itm} {in_t} {itm.pos.cords}.')
  # print(f'new turn {world.turn=:} {to_t} {itm} {in_t} {itm.pos.cords}.')
  # init = time()
  if itm.hp_total < 1: return
  itm.start_turn()
  unit_restoring(itm)
  itm.set_hidden(itm.pos)
  if (itm.goal and itm.goal[0] == 'stalking'
      or (itm.leader and itm.leader.goal and itm.leader.goal[0] == 'stalking') 
      or itm.scout
      and itm.ai == 1):
    if itm.comm == 0: oportunist_attack(itm)
  unit_join_group(itm)
  if itm.goto: 
    move_unit(itm)
  unit_attrition(itm)
  itm.maintenanse()
  # print(f'{time()-init}')



def unit_restoring(itm, info=0):
  logging.debug(f'restaura {itm} id {itm.id}.')
  if itm.hp_total < 1:
    logging.warning(f'sin salud.')
    return
  itm.history.turns += 1
  itm.stopped = 0
  itm.revealed = 0

  # hp.
  if itm.hp_total < itm.hp * itm.units:
    res = itm.hp_res + itm.hp_res_mod
    itm.hp_total += res
    if itm.hp_total > itm.hp * itm.units: itm.hp_total = itm.hp * itm.hp * itm.units
    if info: logging.debug(f'restaura {res} hp.')
    if itm.hp_total > itm.hp * itm.units: itm.hp_total = itm.hp * itm.units

  # Refit
  if itm.pos.nation and itm.sts + itm.sts_mod:
    if itm.units < itm.min_units * itm.squads:
      sts = itm.hp * (itm.sts + itm.sts_mod)
      itm.hp_total += sts
      msg = f'recovers {sts}.'
      itm.log[-1] += {msg}
      if info: logging.debug(msg)
      reduction = round(itm.pop / itm.initial_units)
      itm.pos.city.reduce_pop(reduction)
  
  # mp.
  itm.mp[0] = itm.mp[1]
  if info: logging.debug(f'mp {itm.mp}.')

  # poder.
  power_res = itm.power_res + itm.power_res_mod
  itm.power += power_res
  if itm.power > itm.power_max: itm.power = itm.power_max

  # skills.
  for sk in itm.skills:
    if sk.type == 2:
      sk.run(itm)
    if sk.turns > 0:sk.turns -= 1
  itm.global_skills = [sk for sk in itm.global_skills if sk.turns == -1 or sk.turns > 0]
  itm.offensive_skills = [sk for sk in itm.offensive_skills if sk.turns == -1 or sk.turns > 0]
  itm.other_skills = [sk for sk in itm.other_skills if sk.turns == -1 or sk.turns > 0]
  itm.terrain_skills = [sk for sk in itm.terrain_skills if sk.turns == -1 or sk.turns > 0]



def view_log(log, sound='book_open01', x=None):
  if x != None: x = x
  else: x = len(log) - 1
  y = 0
  say = 1
  sleep(loadsound(sound))
  while True:
    if say:
      if isinstance(log[x][y], str):sp.speak(log[x][y])
      elif isinstance(log[x][y], list): sp.speak(log[x][y][0])
      say = 0
    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN:
        if  event.key == pygame.K_TAB:
          say = 1
          view_log(nation.devlog)
        if  event.key == pygame.K_LEFT:
          x = basics.selector(log, x, 'up', sound='book_pageturn3')
          y = 0
          say = 1
        if  event.key == pygame.K_RIGHT:
          x = basics.selector(log, x, 'down', sound='book_pageturn3')
          y = 0
          say = 1
        if  event.key == pygame.K_UP:
          y = basics.selector(log[x], y, 'up', sound='book_pageturn1')
          say = 1
        if  event.key == pygame.K_DOWN:
          y = basics.selector(log[x], y, 'down', sound='book_pageturn1')
          say = 1
        if  event.key == pygame.K_HOME:
          y = 0
          loadsound('book_pageturn1')
          say = 1
        if  event.key == pygame.K_END:
          y = len(log[x]) - 1
          loadsound('book_pageturn1')
          say = 1
        if  event.key == pygame.K_RETURN:
          if isinstance(log[x][y], list): view_log(log[x][y][1:], x=0)
        if  event.key == pygame.K_F12:
            sp.speak(f'debug on', 1)
            sp.speak(f'debug off', 1)
        if  event.key == pygame.K_ESCAPE:
          sleep(loadsound('back1') / 2)
          return



day_limit = 30
day_timer = [0, 20]
global_timer = [2, 2]
timer1 = [ticks(), 500]
timer2 = ticks()



def warning_enemy(nation, scenary):
  warn = 0
  for ti in nation.tiles:
    if ti.threat:
          warn = 1
  if warn: sp.speak(f'enemigos. {warn}.')

  if warn and nation.ai == 0: sleep(loadsound('warn1', channel=ch4) / 2)
  return warn



def change():
  for t in scenary:
    for uni in t.units:
      uni.history.kills_record = 0
      uni.history.raids = 0



# 0 = juego, 1 = editor de mapa, 3 = crear y editar.
mapeditor = 0

# 1 = nuevo juego, 0 = cargar partida.
new_game = 1

startpos = None

if mapeditor == 0: exec('from game_setup import *')  


start()
