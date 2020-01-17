print(f'carga nations.')
import copy
from math import ceil, floor
from random import randint, shuffle, choice, uniform
from time import sleep, clock

from numpy import mean

from basics import *
from data.buildings import *
from data.events import *
from data.lang.es import * 
from data.names import *
from data.skills import *
from log_module import *
from screen_reader import *
from sound import *


class Empty:
  pass


class Nation:
  ai = 0
  anphibian = 0
  attack_factor = 300
  capture = 0
  city_change = 250
  city_req_pop_base = 600
  corruption = 50
  defense_total_percent = 0
  defense_mean = 0
  food_limit_builds = 200
  gold = 1000
  gold_rate = 1
  grouth_base = 0
  grouth_rate = 100
  income = 0
  
  name = 'unnamed'
  military_percent = 0
  military_pop = 0
  pop_limit = 50
  public_order = 0
  raid_income = 0
  raid_outcome = 0
  scout_factor = 4
  show_info = 1
  stalk = 0
  stalk_rate = 50 # cuantos stalk se envian.
  tile_cost = 400
  tile_power = 1
  tile_area_limit = 3
  type = nation_t
  unit_number = 0
  upkeep_base = 50
  upkeep_change = 100
  def __init__(self):
    #Casilla inicial permitida.
    self.hill = [0, 1]
    self.soil = [waste_t, glacier_t, grassland_t, ocean_t, plains_t, tundra_t]
    self.surf = [none_t]
    #Terrenos adyacentes permitidos
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
    #terrenos adyacentes no permitidos.
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
    
    #terrenos de comida.
    self.for_food = Empty()
    self.for_food.soil = [grassland_t, plains_t]
    self.for_food.surf = [none_t]
    self.for_food.hill = [0]
    #terrenos de recursos.
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
    
  def __str__(self):
    name = f'{self.name}'
    return name
  def add_city(self, itm, pos, scenary, unit):
    itm.nation = self
    pop = (27*100//30) *unit.pop//100
    itm.pop = pop
    itm.pos = pos
    pos.buildings.append( itm)
    unit.pos.units.remove(unit)
    if self.city_names: 
      shuffle(self.city_names)
      itm.nick = self.city_names.pop()
    if len(self.cities) == 0: itm.capital = 1
    if itm.capital: itm.set_capital_bonus()
    tiles = pos.get_near_tiles(scenary, 1)
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
           and it.comm == 0]
    
    return self.units_free
  def is_allowed_tiles(self, tile):
    go = 1
    if tile.around_desert < self.allow_around_desert: go = 0
    if tile.around_forest < self.allow_around_forest: go = 0
    if tile.around_glacier < self.allow_around_glacier: go = 0
    if tile.around_grassland < self.allow_around_grassland: go = 0
    if tile.around_hill < self.allow_around_hill: go = 0
    if tile.around_mountain < self.allow_around_montain: go = 0
    if tile.around_coast < self.allow_around_ocean: go = 0
    if tile.around_plains < self.allow_around_plains: go = 0
    if tile.around_swamp < self.allow_around_swamp: go = 0
    if tile.around_tundra < self.allow_around_tundra: go = 0
    if tile.around_volcano < self.allow_around_volcano: go = 0
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
  
  def set_income(self):
    [ct.income_change() for ct in self.cities]
    self.gold += self.raid_income
    logging.debug(f'gana {self.raid_income} por saqueos.')
    self.raid_income = 0
  def set_seen_nations(self, info=0):
    sp.speak(f'revisando mapa.',1)
    for t in self.map:
      t.update(self)
      if (t.nation != None and str(t.nation) != str(self) 
          and str(t.nation) not in self.str_nations and t.sight):
        nt = t.nation.__class__()
        self.str_nations.append(str(t.nation))
        self.seen_nations.append(nt)
        logging.debug(f'{nt} descubierta.')
        sleep(loadsound('notify1')/2)
        
    for nt in self.seen_nations:
      nt.seen_units = []
      seen_score = 0
      for t in self.map:
        if str(t.nation) == str(nt) and t.sight: 
          if t not in nt.seen_tiles: nt.seen_tiles.append(t)
          for uni in t.units:
            if str(uni.nation) == str(nt): 
              seen_score += uni.ranking
              nt.seen_units.append(uni)
      
      nt.seen_score.insert(0, seen_score)
      nt.max_score = max(nt.seen_score[:20])
      nt.mean_score = mean(nt.seen_score[:20])
    
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
    cities = [i for i in self.cities if i.capital == 0]
    self.city_req_pop = self.city_req_pop_base
    self.city_req_pop += len(cities)*self.city_change
  
  
  def status(self, info=0):
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
      if ct.defense < ct.defense_total: self.defense_need -= ct.defense_total/2
      self.pop += ct.pop
      
      for uni in self.units: 
        self.pop_military += uni.pop
    
      self.pop_total = self.pop_military + self.pop
      self.military_percent = round(self.pop_military*100/self.pop_total)
      self.pop_percent = round(self.pop*100/self.pop_total)
      self.upkeep_percent = round(self.upkeep*100/self.income, 1)
      
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
  def start_bonus(self):
    for uni in self.units:
      if uni.settler: uni.pop += self.settler_start_bonus
  def update(self, scenary):
    if self.cities: self.pos = self.cities[0].pos
    else: self.pos = None
    self.buildings = []
    self.cities = []
    self.score = 0
    self.tiles = [t for t in scenary if t.nation == self]
    self.units = []
    self.upkeep = 0
    for t in scenary:
      for b in t.buildings:
        if b.nation == self:
          if b.type != city_t: self.buildings.append(b)
          if b.type == city_t: self.cities.append(b)
      for uni in t.units:
        if uni.nation == self: self.units.append(uni)
    
    self.production = []
    for c in self.cities: 
      for p in c.production:
        self.production.append(p) 
    self.units_comm = [it for it in self.units if it.comm]
    self.units_scout = [i for i in self.units if i.scout]
    self.upkeep += sum(b.upkeep for b in self.buildings if b.is_complete)
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
    self.upkeep_limit += round(self.pop/self.upkeep_change)
    if self.upkeep_limit > 100: self.upkeep_limit = 100
    self.upkeep_limit = round(self.upkeep_limit*self.income//100)
    self.cities.sort(key=lambda x: x.capital, reverse=True)
    self.set_new_city_req()
    self.units.sort(key=lambda x: len(x.group))


class HolyEmpire(Nation):
  attack_factor = 250
  capture_rate = 200
  city_change = 500
  city_req_pop_base = 800
  corruption = 0
  food_limit_builds = 300
  food_limit_upgrades = 400
  gold = 10000
  grouth_base = 1
  scout_factor = 4
  settler_start_bonus = 0
  stalk_rate = 100
  name = 'Holy Empire'
  nick = nation_phrase1_t
  pop_limit = 50
  public_order = 0
  upkeep_base = 55
  upkeep_change = 100
  def __init__(self):
    super().__init__()
    #Casilla inicial permitida.
    self.hill = [0]
    self.soil = [plains_t, grassland_t]
    self.surf = [none_t]
    #Terrenos adyacentes permitidos
    self.allow_around_grassland = 1
    self.allow_around_plains = 1
    #terrenos adyacentes no permitidos.
    self.unallow_around_ocean = 2 
    self.unallow_around_swamp = 2
    
    #edificios iniciales disponibles.
    self.av_buildings = [Fields, Dock, MeetingCamp, Pastures, TrainingCamp, SawMill, Quarry]
    self.city_names = roman_citynames
    
    #terrenos de comida.
    self.for_food.soil = [grassland_t, plains_t]
    self.for_food.surf = [none_t]
    self.for_food.hill = [0]
    #terrenos de recursos.
    self.for_res.soil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.for_res.surf = [2]
    self.for_res.hill = [0, 1]
    
    #Unidades iniciales.
    self.start_units = [Levy, Levy, Settler]


class Transylvania(Nation):
  attack_factor = 150
  capture_rate = 150
  city_change = 400
  city_req_pop_base = 700
  corruption = 0
  food_limit_builds = 700
  food_limit_upgrades = 500
  gold = 10000
  grouth_base = 0
  name = 'Silvania'
  nick = nation_phrase2_t
  pop_limit = 40
  public_order= 0
  scout_factor = 2
  settler_start_bonus = 0
  stalk_rate = 80
  upkeep_base = 40
  upkeep_change = 100
  def __init__(self):
    super().__init__()
    #Casilla inicial permitida.
    self.hill = [0]
    self.soil = [plains_t, waste_t]
    self.surf = [none_t]
    #Terrenos adyacentes permitidos
    self.allow_around_plains= 1
    self.allow_around_desert = 2
    #terrenos adyacentes no permitidos.
    self.unallow_around_ocean = 2
    
    #edificios iniciales disponibles.
    self.av_buildings = [Cemetery, DesecratedRuins, Dock, SmallWood, Gallows, Pit, Quarry, SawMill]
    self.city_names = death_citynames
    #terrenos de comida.
    self.for_food.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.for_food.surf = [none_t]
    self.for_food.hill = [0]
    #terrenos de recursos.
    self.for_res.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.for_res.surf = [none_t, forest_t]
    self.for_res.hill = [0, 1]
    
    #Unidades iniciales.
    self.start_units = [Settler2, Zombies, Zombies, VladDracul]


class Hell(Nation):
  name = hell_t
  show_info = 0
  def __init__(self):
    super().__init__()
    self.log = [[hell_t]]
    self.av_units = [Ghouls, Goblins, Harpy, HellHounds, Hyaenas, Orcs, 
                     Orc_Archers, Skeletons, VarGhul, Wargs, Zombies]


class Wild(Nation):
  name = wild_t
  show_info = 0
  def __init__(self):
    super().__init__()
    self.log = [[wild_t]]
    self.av_units = [Akhlut, DesertNomads, Hunters, NomadsRiders, Raiders,
                     Warriors, Wolves]