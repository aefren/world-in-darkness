print(f'carga units')
from math import ceil, floor
from random import randint, shuffle, choice, uniform
from time import sleep

from numpy import mean

from basics import *
from data.events import *
from data.lang.es import * 
from data.names import *
from data.skills import *
from log_module import *
from screen_reader import *
from sound import *


class Unit:
  name = str()
  nick = str()
  units = 0
  type = str()
  comm = 0
  unique = 0
  gold = 0
  upkeep = 0
  resource = 0
  pop = 0
  food = 0
  sk = []
  terrain_skills = []

  hp = 0
  mp = []
  moves = 0
  resolve = 0
  global_skills = []
  
  dfs = 0
  res = 0
  arm = 0
  armor = None
  shield = None
  defensive_skills = []

  att = 0
  damage = 0
  range = 0
  off = 0
  str = 0
  pn = 0
  offensive_skills = []
  spells = []

  other_skills = []
  buildings = [] 
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
  range = 1
  stealth = 4
  hp_res = 1
  hp_res_mod = 0
  other_skills = []
  units_min = 5

  ai = 1
  anticav = 0
  attacking = 0
  auto_attack = 0
  auto_explore = 0
  can_burn = 0
  can_charge = 0
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
  fled = 0
  fear = 4
  food = 0
  forest_survival = 0
  garrison = 0
  goal = None
  going = 0
  gold = 0
  group_score= 0
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
  sort_chance = 66
  stopped = 0
  swamp_survival = 0
  units_min = 0
  units_max = 50
  to_avoid = 0
  def __init__(self, nation):
    print(f'{self}')
    self.hp_total = self.hp*self.units
    self.initial_units = self.units
    self.nation = nation
    self.buildings = [eval(i) for i in self.buildings]
    self.defensive_skills = [i(self) for i in self.defensive_skills]
    self.global_skills = [i(self) for i in self.global_skills]
    self.offensive_skills = [i(self) for i in self.offensive_skills]
    self.other_skills = [i for i in self.other_skills]
    self.spells = [i(self) for i in self.spells]
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
    self.soil = [coast_t, glacier_t, grassland_t, plains_t, tundra_t, waste_t,]
    self.surf = [forest_t, none_t, river_t, swamp_t]
    self.status = []
    self.tags = []
    self.target = None
    self.tiles_hostile = []
    self.traits = []
    
  def __str__(self):
    if self.nick: name = f'{self.nick}. '
    else: name = ''
    if self.units > 1: name += f'{self.units}'
    name += f' {self.name}'
    
    #if self.show_info == 0: name += f' id {self.id}.'
    return name
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
  def burn(self, cost=0):
    self.pos.update(self.pos.nation)
    if (self.buildings
        and self.mp[0] >= cost and self.can_burn and self.pos.nation != self.nation): 
      
      building = choice(self.pos.buildings)
      self.update()
      damage = self.damage*self.att
      building.resource_cost[0] -= damage
      msg = f'{self} {burn_t} {self.pos.building}.'
      self.log[-1].append(msg)
      self.pos.nation.log[-1].append(msg)
      logging.debug(msg)
  def can_pass(self, pos):
    if pos.soil.name in self.soil and pos.surf.name in self.surf: return True
  def check_ready(self):
    go = 1
    if self.group_score > 0 or self.group:
      #logging.debug(f'grupo de {self}, {self.group_score} de {self.group_base}.')
      if self.group_score> 0: self.create_group(self.group_base)
      for i in self.group:
        logging.debug(f'{i} pos {i.pos.cords}. {self} pos {self.pos.cords}.')
        if i.pos != self.pos: go = 0
        if i.mp[0] < self.mp[0]: go = 0
      if self.group_score > 0: go = 0
      if self.going > 0: go = 1
    if self.group and go == 0: logging.debug(f'go {go}.')
    return go
  def combat_retreat(self, ):
    logging.debug(f' combat retreat.')
    self.update()
    logging.debug(f'{self} retreat units {self.units} hp {self.hp_total}.')
    dead = self.deads[-1]
    logging.info(f'{self} loses {dead}.')
    
    roll = roll_dice(1)
    logging.debug(f'dado {roll}.')
    roll += dead
    logging.debug(f'dado {roll}.')
    resolve = self.resolve + self.resolve_mod
    logging.debug(f'{self} resolve {resolve}.')
    if (dead and roll > resolve
        and undead_t not in self.traits):
      retreat = roll - resolve
      if retreat > self.units: retreat = self.units
      self.hp_total -= retreat*self.hp 
      self.fled[-1] += retreat
      logging.warning(f'{self} huyen {retreat} unidades.')
      self.update()
      logging.debug(f'total huídos {self.fled}.')
  def create_group(self, score, same_mp=0):
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
    units.sort(key=lambda x: x.pos == self.pos,reverse=True)
    if self.range <= 6:
      units.sort(key=lambda x: x.range >= 6, reverse=True)
    elif self.range >= 6:
      units.sort(key=lambda x: x.off, reverse=True)
    if self.settler:
      units.sort(key=lambda x: x.mp[1] == self.mp[1],reverse=True)
      units.sort(key=lambda x: x.ranking,reverse=True)
    
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
      self.pos.nation.update(self.pos.scenary)
  def get_favland(self, pos):
    if (pos.soil.name in self.favsoil and (pos.surf.name in self.favsurf 
        or pos.hill in self.favhill)):
      return 1
    else: return 0
  def get_skills(self):
    #print(f'{self}')
    self.arm_mod = 0
    self.armor_ign_mod = 0
    self.att_mod = 0
    self.damage_mod = 0
    self.damage_critical_mod = 0
    self.damage_charge = 0
    self.damage_sacred_mod = 0
    self.dfs_mod = 0
    self.hit_rolls_mod = 0
    self.hp_res_mod = 0
    self.moves_mod = 0
    self.off_mod = 0
    self.pn_mod = 0
    self.power_mod = 0
    self.power_max_mod = 0
    self.power_res_mod = 0
    self.range_mod = 0
    self.ranking_skills = 0
    self.res_mod = 0
    self.resolve_mod = 0
    self.stealth_mod = 0
    self.str_mod = 0


    self.skill_names = []
    self.effects = []
    if self.settler == 1: self.skill_names.append(f' {settler_t}.')
    
    skills = [i for i in self.skills]
    [self.skill_names.append(i.name) for i in self.skills]
    tile_skills = []
    if self.pos:
      tile_skills += [sk for sk in self.pos.skills]
      if self.attacking == 0: tile_skills += [sk for sk in self.pos.terrain_events]
      elif self.attacking: tile_skills += [sk for sk in self.target.pos.terrain_events]
    #print(f'{len(tile_skills)} de casillas.')
    for i in tile_skills:
      if i.type == 0:
        skills.append(i)
        #print(f'se agrega {i.name}')
    
    if self.target: skills += [s for s in self.target.skills if s.effect == 'enemy']    
    #print(f'run')
    for sk in skills:
      if sk.type == 0:
        #print(sk.name)
        #print(sk)
        sk.run(self)
    
    self.skill_names.sort()
  def maintenanse(self):
    #logging.debug(f'mantenimiento de {self} de {self.nation}.')
    if self.upkeep > 0 and self.nation.gold >= self.upkeep:
      self.nation.gold -= self.upkeep_total
      logging.debug(f'{self} cobra {self.upkeep}.')
    elif self.upkeep > 0 and self.nation.gold < self.upkeep:
      self.pos.units.remove(self)
      self.nation.units.remove(self)
      self.city.pop_back += self.pop
      logging.debug(f'se disuelve')
  def raid(self, cost=0):
    if (self.pos.city and self.pos.nation != self.nation and self.can_raid 
        and self.mp[0] >= cost ):  
      
      self.mp[0] -= cost
      self.update()
      self.pos.update()
      logging.info(f'{self} saquea a {self.pos.city} {self.pos.nation} en {self.pos} {self.pos.cords}')
      logging.debug(f'población {self.pos.pop}.')
      if self.pos.raided == 0:
        self.pos.raided = 1
        raided = self.pos.income
        self.pos.city.raid_outcome += raided
        self.nation.raid_income += raided
        msg = f'{self} {raid_t} {raided} {gold_t} {in_t} {self.pos} {self.pos.cords}.'
        self.pos.nation.log[-1].append(msg)
        self.log[-1].append(msg)
      dead = self.damage*randint(1,self.att+3)
      self.pos.pop -= dead
      if self.pos.pop: self.pos.unrest += dead*100/self.pos.pop
      msg= f'{dead} población perdida.'
      self.pos.nation.log[-1].append(msg)
      logging.info(f'raid_income {round(self.pos.nation.raid_income)}.')      
      self.pos.city.update()
  def set_attack(self, enemies):
    if self.mp[0] < 0: return
    logging.debug(f'ataque hidden.')
    enemies = [i for i in enemies
               if i.nation != self.nation and i.hidden == 0]
    if enemies:
      weakest = roll_dice(1)
      if self.hidden: weakest += 2
      distance = roll_dice(3)
      if weakest >= 5: enemies.sort(key=lambda x: x.ranking)
      return enemies[0], distance
  def set_auto_explore(self):
      if self.scout == 0:
        self.scout = 1
        self.ai = 1
        msg = f'exploración automática.'
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
  def set_hidden(self, pos):
    info = 0
    if info: print(f'set hidden {self} a {pos} {pos.cords}.')
    visible = self.units
    if info: print(f'visible {visible}')
    if self.nation != pos.nation: 
      visible += pos.pop
      if info: print(f'visible {visible} pop')
    visible += sum([it.units for it in pos.units if it.nation != self.nation])
    if info: print(f'visible {visible} units')
    visible = round(visible/20)
    if info: print(f'visible {visible} rond 20')
    stealth = self.stealth+self.stealth_mod
    if info: print(f'stealth {stealth}')
    if self.day_night[0]: stealth += 1
    if info: print(f'stealth {stealth} day night.')
    if pos.surf.name == forest_t or pos.hill: stealth += 1
    if info: print(f'{stealth} terrain')
    stealth -= visible
    roll = roll_dice(2)
    if info: print(f'roll {roll}. stealth {stealth}.')
    if roll >= stealth or roll == 12: 
      self.revealed = 1
    if info: print(f'revelado.')
  def set_id(self):
    num = self.id
    #logging.debug(f'id base {self} {num}.')
    self.nation.units.sort(key=lambda x: x.id)
    for i in self.nation.units:
      #logging.debug(f'{i} id {i.id}.')
      if i.id == num: num += 1
    self.id = num
    #logging.debug(f'id final {self.id}.')
  def set_level(self):
    level = self.level
    for i in self.exp_tree:
      if self.exp <= i:
        self.level = self.exp_tree.index(i)
        break
    
    if self.level > level: self.level_up()
  def set_tile_attr(self):
    info = 1
    tiles = self.pos.get_near_tiles(self.pos.scenary, 1)
    tiles = [t for t in tiles if t.nation 
           and t.nation != self.nation and t.pop]
    if info and tiles: print(f'set_tile_attr {self} en {self.pos} {self.pos.cords}')
    for t in tiles:
      t.update(self.nation)
      defense = t.pop+t.defense
      if info: print(f'defense en {t} {t.cords} {defense}')
      defense += t.around_defense*0.1
      if info: print(f'around defense {defense}')
      unrest = self.ranking*0.1
      if info: print(f'unrest {unrest}')
      if t != self.pos: unrest = unrest/2
      if info: print(f'diferente que. unrest {unrest}')
      unrest = unrest*100/defense
      if info: print(f'unrest final {unrest}')
      if unrest < 0: unrest = 0
      t.unrest += unrest
         
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
      
    #si pos.
    if self.pos:
      if self.log == []: self.log.append([f'{turn_t} {self.pos.world.turn}.'])
      if self.pos.nation != self.nation and self.pos.nation != None and self.pos not in self.tiles_hostile:
        self.tiles_hostile.append(self.pos)
        #logging.debug(f'hostiles explorados {len(self.tiles_hostile)}.')
      
      #revelado.
      if self.revealed: self.hidden = 0
    
    
    #atributos.
    self.units = ceil(self.hp_total/self.hp)
    if self.units < 0: self.units = 0
    self.upkeep_total = self.upkeep* self.units
    if undead_t in self.traits: self.can_recall = 0
    if self.can_hide: self.hidden = 1
    if self.revealed: self.hidden = 0
    
    #ranking.
    self.skills = [i for i in self.defensive_skills+self.global_skills+
                   self.offensive_skills+self.other_skills+self.terrain_skills]
    self.get_skills()
    self.effects += [s.name for s in self.other_skills]
    self.ranking = 0
    self.ranking += self.damage+self.damage_mod
    self.ranking += self.damage_sacred+self.damage_sacred_mod
    self.ranking += self.damage_charge
    self.ranking *= self.att+self.att_mod
    self.ranking *= self.units
    self.ranking += self.range//2
    self.ranking += (self.off+self.off_mod)*5
    self.ranking += self.str+self.str_mod*5
    self.ranking += (self.pn+self.pn_mod)*3
  
    self.ranking += self.mp[1]*2
    self.ranking += self.hp_total//5
    self.ranking += self.moves
    self.ranking += (self.dfs+self.dfs_mod)*2
    self.ranking += (self.res+self.res_mod)*2
    self.ranking += self.arm+self.arm_mod
    if self.armor: self.ranking += self.armor.arm*4
    try:
      if self.shield: self.ranking += self.shield.dfs*4
    except:
      pass
  
    if self.can_fly: self.ranking += 5 
    self.ranking += self.ranking_skills
    self.ranking += sum(s.ranking for s in self.skills+self.spells)
    self.ranking = round(self.ranking/2)
    if self.hidden: self.ranking += 10
    
    
    if self.leader and self.leader not in self.nation.units: 
      self.leader = None
      logging.warning(f'{self} sin lider.')
    self.group = [i for i in self.group if i.units > 0]
    self.group_ranking = self.ranking+sum(i.ranking for i in self.group)



class Amphibian:
  def __init__(self):
    self.soil = [coast_t, glacier_t, grassland_t, plains_t, ocean_t, tundra_t]
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
    self.traits = [human_t]


class Ship(Unit):
  def __init__(self, nation):
    super().__init__(nation)
    self.type = 'ship'
    self.soil = [coast_t, ocean_t] 


class Undead(Unit):
  def __init__(self, nation):
    super().__init__(nation)
    Ground.__init__(self)
    self.traits += [undead_t]


#Items.
class LightArmor:
  def __init__(self):
    self.arm = 1
    self.name = 'light armor'


class HeavyArmor:
  def __init__(self):
    self.arm = 2
    self.name = 'heavy armor'


class Shield:
  def __init__(self):
    self.dfs = 4
    self.name = 'shield'


#Vampire.
class Banshee(Undead):
  name = 'banshee'
  units = 1
  type = 'infantry'
  gold = 80
  upkeep = 20
  resource_cost = 30
  food = 0
  pop = 30

  hp = 6
  mp = [2, 2]
  moves = 8
  resolve = 8
  global_skills = [Ethereal, FearAura, Fly]

  dfs = 3
  res = 3
  arm = 0
  armor = None

  att = 1
  damage = 2
  off = 3
  str = 3
  pn = 0
  offensive_skills = [Scream]
  
  stealth = 12
  def __init__(self, nation):
    super().__init__(nation)


class Bats(Unit):
  name = bats_t
  units = 10
  type = 'beast'
  gold = 25
  upkeep = 3
  resource_cost = 11
  food = 3
  pop = 8
  terrain_skills = [ForestSurvival]

  hp = 1
  mp = [4, 4]
  moves = 8
  resolve = 3
  global_skills = [Fly, NightSurvival]

  dfs = 3
  res = 2
  arm = 0
  armor = None

  att = 1
  damage = 1
  off = 3
  str = 2
  pn = 0
  def __init__(self, nation):
    super().__init__(nation)
    self.favhill = [1]
    self.favsurf = [forest_t]
    self.traits += [animal_t]


class BlackKnights(Undead):
  name = black_knights_t
  units = 5
  type = 'cavalry'
  gold = 120
  upkeep = 6
  resource_cost = 22
  food = 0
  pop = 25
  terrain_skills = [Burn]

  hp = 3
  mp = [3, 3]
  moves = 10
  resolve = 10
  global_skills = [FearAura, NightFerocity, NightSurvival]

  dfs = 4
  res = 4
  arm = 2
  armor = HeavyArmor()

  att = 3
  damage = 3
  off = 5
  str = 4
  pn = 1
  offensive_skills = [HeavyCharge]
  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [BloodKnights]
    self.favhill = [0]
    self.favsoil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t]


class BloodKnights(Undead):
  name = blood_knights_t
  units = 5
  type = 'infantry'
  gold = 180
  upkeep = 9
  resource_cost = 26
  food = 0
  pop = 20

  hp = 3
  mp = [2, 2]
  moves = 6
  resolve = 10
  global_skills = [FearAura, NightFerocity, NightSurvival]

  dfs = 5
  res = 4
  arm = 0
  armor = HeavyArmor()
  shield = Shield()

  att = 2
  damage = 3
  off = 5
  str = 5
  pn = 1
  def __init__(self, nation):
    super().__init__(nation)
    self.favhill = [0]
    self.favsoil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t]


class CryptHorrors (Undead):
  name = crypt_horror_t
  units = 5
  type = 'infantry'
  gold = 60
  upkeep = 6
  resource_cost = 16
  food = 0
  pop = 15

  hp = 2
  mp = [2, 2]
  moves = 18
  resolve = 10
  global_skills = [FearAura, NightFerocity, NightSurvival]

  dfs = 3
  res = 4
  arm = 0
  armor = HeavyArmor()

  att = 2
  damage = 2
  off = 4
  str = 4
  pn = 1
  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeletons]


class DireWolves(Undead):
  name = dire_wolves_t
  units = 6
  type = 'beast'
  gold = 100
  upkeep = 8
  resource_cost = 22
  food = 0
  pop = 15
  terrain_skills = [ForestSurvival, MountainSurvival]

  hp = 4
  mp = [3, 3]
  moves = 18
  resolve = 10
  global_skills = [NightFerocity, NightSurvival]

  dfs = 3
  res = 3
  arm = 0

  att = 1
  damage = 2
  off = 3
  str = 3
  pn = 0
  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeletons]
    self.favhill = [0, 1]
    self.favsoil = [glacier_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]


class FellBats(Undead):
  name = fell_bats_t
  units = 5
  type = 'beast'
  gold = 60
  upkeep = 6
  resource_cost = 18
  food = 0
  pop = 12
  terrain_skills = [ForestSurvival, MountainSurvival]

  hp = 2
  mp = [2, 2]
  moves = 8
  resolve = 10
  global_skills = [FearAura, Fly, NightSurvival]

  dfs = 3
  res = 3
  arm = 0

  att = 2
  damage = 2
  off = 3
  str = 3
  pn = 0
  def __init__(self, nation):
    super().__init__(nation)
    self.favsurf = [forest_t]


class Ghouls(Human):
  name = ghouls_t
  units = 10
  type = 'infantry'
  gold = 30
  upkeep = 8
  resource_cost = 13
  food = 3
  pop = 20
  terrain_skills = [Burn, Raid]

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 6
  global_skills = [NightFerocity]

  dfs = 3
  res = 3
  arm = 0

  att = 1
  damage = 2
  off = 3
  str = 3
  pn = 0
  offensive_skills = [ToxicClaws]

  pref_corpses = 1
  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Zombies]


class GraveGuards(Undead):
  name = grave_guards_t
  units = 6
  type = 'infantry'
  gold = 80
  upkeep = 14
  resource_cost = 16
  food = 0
  pop = 30

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 10
  global_skills = [FearAura, NightFerocity, NightSurvival]

  dfs = 4
  res = 4
  arm = 0
  armor = HeavyArmor()
  shield = Shield()

  att = 1
  damage = 4
  off = 4
  str = 4
  pn = 1
  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeletons]
    self.favsoil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t]


class Settler2(Human):
  name = settler_t
  units = 30
  type = 'civil'
  settler = 1
  gold = 1000
  upkeep = 0
  resource_cost = 50
  food = 4
  pop = 200

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 4

  dfs = 2
  res = 2
  arm = 0
  armor = None

  att = 1
  damage = 1
  off = 2
  str = 2
  pn = 0

  buildings = ['CursedHamlet']
  def __init__(self, nation):
    super().__init__(nation)
    self.buildings = [CursedHamlet]
    self.corpses = [Zombies]


class Skeletons(Undead):
  name = skeletons_t
  units = 5
  type = 'infantry'
  gold = 25
  upkeep = 0
  resource_cost = 12
  food = 0
  pop = 0
  terrain_skills = [Burn]

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 10
  global_skills = [NightFerocity, SkeletonLegion]

  dfs = 3
  res = 4
  arm = 0

  att = 1
  damage = 2
  off = 3
  str = 3
  pn = 0
  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = []


class Vampire(Undead):
  name = vampire_t
  units = 1
  type = 'beast'
  gold = 400
  upkeep = 15
  resource_cost = 30
  food = 0
  pop = 15
  terrain_skills = [ForestSurvival, MountainSurvival]

  hp = 12
  mp = [2, 2]
  moves = 10
  resolve = 10
  global_skills = [ElusiveShadow, FearAura, Fly, BloodyFeast, NightSurvival]

  dfs = 5
  res = 4
  arm = 0
  armor = LightArmor()

  att = 2
  damage = 3
  off = 5
  str = 4
  pn = 1
  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = []
    self.favhill = [1]
    self.favsurf = [forest_t, swamp_t]
    self.soil += [coast_t]


class Vargheist(Undead):
  name = 'vargheist'
  units = 1
  type = 'beast'
  gold = 150
  upkeep = 30
  resource_cost = 30
  food = 0
  pop = 30
  terrain_skills = [ForestSurvival, MountainSurvival]

  hp = 8
  mp = [2, 2]
  moves = 10
  resolve = 10
  global_skills =  [ElusiveShadow, FearAura, Fly, BloodyFeast, NightSurvival]

  dfs = 4
  res = 5
  arm = 0

  att = 3
  damage = 3
  off = 6
  str = 5
  pn = 1
  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = []


class VladDracul(Undead):
  name = vampire_t
  nick = 'Vlad Dracul'
  units = 1
  unique = 1
  type = 'infantry'
  comm = 1
  gold = 300
  upkeep = 25
  resource_cost = 50
  food = 0
  pop = 15
  terrain_skills = [ForestSurvival, MountainSurvival]

  hp = 18
  mp = [2, 2]
  moves = 12
  resolve = 10
  global_skills = [BloodyFeast, ElusiveShadow, FearAura, Fly, Frenzy, NightSurvival]

  dfs = 6
  res = 4
  arm = 0
  armor = LightArmor()

  att = 3
  damage = 3
  off = 6
  str = 5
  pn = 1

  spells = [RaiseDead]

  power = 1
  power_max = 2
  power_res = 1

  pref_corpses = 1
  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = []
    self.favsurf = [forest_t, swamp_t]


class VarGhul(Undead):
  name = varghul_t
  units = 10
  type = 'beast'
  gold = 80
  upkeep = 30
  resource_cost = 25
  food = 6
  pop = 15

  hp = 5
  mp = [2, 2]
  moves = 8
  resolve = 10
  global_skills = [NightFerocity, NightSurvival]

  dfs = 4
  res = 4
  arm = 2

  att = 2
  damage = 3
  off = 5
  str = 4
  def __init__(self, nation):
    super().__init__(nation)
    self.favhill = [0, 1]
    self.favsoil = [waste_t]
    self.favsurf = [forest_t, none_t, swamp_t]


class Zombies(Undead,Ground):
  name = zombies_t
  units = 10
  type = 'infantry'
  gold = 25
  upkeep = 0
  resource_cost = 10
  food = 0
  pop = 15

  hp = 2
  mp = [2, 2]
  moves = 4
  resolve = 10
  global_skills = [Spread]

  dfs = 2
  res = 2
  arm = 0

  att = 1
  damage = 2
  off = 2
  str = 2
  pn = 0
  offensive_skills = [Surrounded]
  def __init__(self, nation):
    super().__init__(nation)


#Holy Empire.
class Commander(Human):
  name = 'commander'
  units = 5
  type = 'infantry'
  comm = 1
  gold = 200
  upkeep = 20
  resource_cost = 18
  food = 5
  pop = 30
  terrain_skills = []
  tags = ['commander']

  hp = 2
  moves = 6
  resolve = 8
  global_skills = [Organization]

  dfs = 4
  res = 4
  arm = 0
  armor = LightArmor()
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
    self.mp = [2, 2]
    self.skills = [Inspiration, Regroup, Reinforce]


class Aquilifer(Human):
  name = 'aquilifer'
  units = 5
  type = 'infantry'
  gold = 400
  upkeep = 60
  resource = 50
  food = 5
  pop = 40
  unique = 1
  tags = ['commander']

  hp = 2
  mp= [2, 2]
  moves = 6
  resolve = 8
  global_skills = [Inspiration, Regroup]

  dfs = 5
  res = 5
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


class Priest(Human):
  name = 'sacerdote'
  units = 5
  type = 'infantry'
  gold = 90
  upkeep = 40
  resource_cost = 30
  food = 3
  pop = 20
  tags = ['commander']

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 7
  global_skills = [SermonOfCourage]

  dfs = 3
  res = 3
  arm = 0
  armor = LightArmor()

  att = 1
  damage = 2
  off = 4
  str = 4
  pn = 0
  def __init__(self, nation):
    super().__init__(nation)


#unidades
class Settler(Human):
  name = settler_t
  units = 30
  type = 'civil'
  settler = 1
  gold = 1000
  upkeep = 0
  resource_cost = 50
  food = 4
  pop = 200

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 4

  dfs = 2
  res = 2
  arm = 0
  armor = None

  att = 1
  damage = 1
  off = 2
  str = 2
  pn = 0
  
  buildings = ['Hamlet']
  def __init__(self, nation):
    super().__init__(nation)
    self.buildings = [Hamlet]
    self.corpses = [Zombies]


class Flagellants(Human):
  name = flagellants_t
  units = 10
  type = 'infantry'
  gold = 25
  upkeep = 5
  resource_cost = 11
  food = 2
  pop = 12

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 7

  dfs = 3
  res = 3
  arm = 0
  armor = None

  att = 1
  damage = 2
  off = 3
  str = 3
  pn = 0
  def __init__(self, nation):
    super().__init__(nation)


class SwordsMen(Human):
  name = swordsmen_t
  units = 10
  type = 'infantry'
  gold = 50
  upkeep = 20
  resource_cost = 13
  food = 3
  pop = 20
  terrain_skills = [Burn, Raid]

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 6
  global_skills = [Regroup]

  dfs = 4
  res = 3
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


class Levy(Human):
  name = levy_t
  units = 15
  type = 'infantry'
  gold = 20
  upkeep = 5
  resource_cost = 10
  food = 3
  pop = 20
  terrain_skills = [Burn, Raid]

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 4

  dfs = 3
  res = 3
  arm = 0
  armor = None

  att = 1
  damage = 2
  off = 3
  str = 2
  pn = 0
  def __init__(self, nation):
    super().__init__(nation)


class GreatSwordsMen(Human):
  name = 'grandes espaderos'
  units = 5
  type = 'infantry'
  gold = 80
  upkeep = 40
  resource_cost = 16
  food = 4
  pop = 15
  terrain_skills = [Burn, Raid]

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 7
  global_skills = [BattleBrothers, Regroup, Reinforce]

  dfs = 4
  res = 4
  arm = 0
  armor = HeavyArmor()

  att = 2
  damage = 2
  off = 5
  str = 4
  pn = 0
  def __init__(self, nation):
    super().__init__(nation)


class SpearMen(Human):
  name = spearmen_t
  units = 10
  type = 'infantry'
  gold = 60
  upkeep = 25
  resource_cost = 14
  food = 3
  pop = 20
  terrain_skills = [Burn, Raid]

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 6
  global_skills = [BattleBrothers, Regroup]

  dfs = 5
  res = 4
  arm = 0
  armor = LightArmor()

  att = 1
  damage = 3
  off = 4
  str = 4
  pn = 1
  offensive_skills = [PikeSquare]
  def __init__(self, nation):
    super().__init__(nation)


class Halberdier(Human):
  name = 'halberdier'
  units = 10
  type = 'infantry'
  gold = 100
  upkeep = 40
  resource_cost = 0
  food = 4
  pop = 25
  terrain_skills = [Burn, Raid]

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 6
  global_skills = [BattleBrothers, Regroup, Reinforce, ]

  dfs = 4
  res = 4
  arm = 0
  armor = HeavyArmor()

  att = 2
  damage = 2
  off = 5
  str = 5
  pn = 1
  offensive_skills = [MassSpears, PikeSquare]
  def __init__(self, nation):
    super().__init__(nation)


class Inquisitors(Human):
  name = inquisitors_t
  units = 5
  type = 'infantry'
  gold = 100
  upkeep = 30
  resource_cost = 25
  food = 4
  pop = 20

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 7
  global_skills = [Regroup, Sacred]

  dfs = 3
  res = 3
  arm = 0
  armor = LightArmor()

  att = 2
  damage = 2
  off = 3
  str = 3
  pn = 0
  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Zombies]


class PriestWarriors(Human):
  name = priest_warriors_t
  units = 10
  type = 'infantry'
  gold = 120
  upkeep = 40
  resource_cost = 20
  food = 4
  pop = 25

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 8
  global_skills = [Regroup, Reinforce, Sacred]

  dfs = 4
  res = 4
  arm = 0
  armor = HeavyArmor()
  shield = Shield()

  att = 1
  damage = 2
  off = 5
  str = 4
  pn = 0
  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Zombies]


class Sagittarii(Human):
  name = 'sagittarii'
  units = 10
  type = 'infantry'
  gold = 50
  upkeep = 15
  resource_cost = 14
  food = 3
  pop = 15

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 5

  dfs = 2
  res = 2
  arm = 0
  armor = None

  att = 1
  damage = 2
  range = 18
  off = 4
  str = 3
  pn = 0
  offensive_skills = [ReadyAndWaiting]
  def __init__(self, nation):
    super().__init__(nation)


class CrossBowMen(Human):
  name = 'CrossBowMen'
  units = 10
  type = 'infantry'
  gold = 100
  upkeep = 30
  resource_cost = 20
  food = 3
  pop = 25

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 6

  dfs = 3
  res = 3
  arm = 0
  armor = None

  att = 1
  damage = 2
  range = 12
  off = 5
  str = 4
  pn = 1
  def __init__(self, nation):
    super().__init__(nation)


class Arquebusier(Human):
  name = 'Arquebusier'
  units = 10
  type = 'infantry'
  gold = 90
  upkeep = 20
  resource_cost = 25
  food = 3
  pop = 30

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 6

  dfs = 3
  res = 3
  arm = 0
  armor = None

  att = 1
  damage = 3
  range = 12
  off = 5
  str = 4
  pn = 1
  def __init__(self, nation):
    super().__init__(nation)


class Musket(Human):
  name = 'musquet'
  units = 10
  type = 'infantry'
  gold = 150
  upkeep = 30
  resource_cost = 25
  food = 3
  pop = 30

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 6

  dfs = 3
  res = 3
  arm = 0
  armor = None

  att = 2
  damage = 3
  range = 24
  off = 5
  str = 4
  pn = 1
  def __init__(self, nation):
    super().__init__(nation)

class Equites(Human):
  name = equites_t
  units = 10
  type = 'cavalry'
  gold = 150
  upkeep = 40
  resource_cost = 18
  food = 6
  pop = 20
  terrain_skills = [Burn, Raid]

  hp = 3
  mp = [4, 4]
  moves = 9
  resolve = 6
  global_skills = [BattleBrothers]

  dfs = 3
  res = 3
  arm = 1
  armor = None

  att = 1
  damage = 2
  off = 4
  str = 3
  pn = 0
  offensive_skills = [Charge]
  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeletons]


class Equites2(Human):
  name = feudal_knights_t
  units = 10
  type = 'cavalry'
  gold = 300
  upkeep = 60
  resource_cost = 26
  food = 8
  pop = 40
  terrain_skills = [Burn, Raid]

  hp = 3
  mp = [3, 3]
  moves = 8
  resolve = 7
  global_skills = [BattleBrothers, Regroup, Reinforce]

  dfs = 5
  res = 4
  arm = 1
  armor = HeavyArmor()

  att = 2
  damage = 2
  off = 5
  str = 4
  pn = 0
  offensive_skills = [HeavyCharge]
  def __init__(self, nation):
    super().__init__(nation)


#Others.
class Archers(Human):
  name = archers_t
  units = 10
  type = 'infantry'
  gold = 30
  upkeep = 5
  resource_cost = 12
  food = 3
  pop = 12

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 4

  dfs = 2
  res = 2
  arm = 0
  armor = None

  att = 1
  damage = 2
  range = 18
  off = 3
  str = 3
  pn = 0
  
  fear = 5
  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Zombies]
    self.favhill = [1]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t, forest_t]


class Akhlut(Unit):
  name = 'akhlut'
  units = 1
  type = 'beast'
  gold = 120
  upkeep = 20
  resource_cost = 28
  food = 12
  pop = 25
  terrain_skills = [ForestSurvival, MountainSurvival]

  hp = 12
  mp = [2, 2]
  moves = 7
  resolve = 6
  global_skills = [Regroup]

  dfs = 3
  res = 5
  arm = 2
  armor = None

  att = 3
  damage = 4
  off = 5
  str = 5
  pn = 0

  stealth = 10

  fear = 2
  def __init__(self, nation):
    super().__init__(nation)
    Amphibian.__init__(self)
    self.corpses = [Skeletons]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, swamp_t]
    self.traits += [animal_t, ]


class BlackOrcs(Unit):
  name = 'orcos negros'
  units = 5
  type = 'infantry'
  gold = 80
  upkeep = 25
  resource_cost = 20
  food = 6
  pop = 30
  terrain_skills = [Burn, Raid]

  hp = 6
  mp = [2, 2]
  moves = 7
  resolve = 8

  dfs = 4
  res = 4
  arm = 0
  armor = HeavyArmor

  att = 2
  damage = 4
  off = 5
  str = 5
  pn = 1

  fear = 2
  def __init__(self, nation):
    super().__init__(nation)
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
  gold = 50
  upkeep = 20
  resource_cost = 16
  food = 3
  pop = 30
  terrain_skills = {Burn, Raid}

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 6
  global_skills = [DesertSurvival, MountainSurvival]

  dfs = 3
  res = 3
  arm = 0
  armor = LightArmor()
  shield = Shield()

  att = 1
  damage = 2
  off = 5
  str = 3
  pn = 0
  
  stealth = 8
  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Zombies]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]


class DesertNomads(Human):
  name = 'ginetes a camello'
  units = 10
  type = 'cavalry'
  gold = 70
  upkeep = 20
  resource_cost = 18
  food = 5
  pop = 20
  terrain_skills = [DesertSurvival, Burn, Raid]

  hp = 3
  mp = [4, 4]
  moves = 9
  resolve = 5

  dfs = 3
  res = 3
  arm = 0
  armor = None
  shield = None

  att = 2
  damage = 1
  off = 4
  str = 3
  pn = 0
  offensive_skills = [Charge]
  
  stealth = 6
  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeletons]
    self.favhill = [0]
    self.favsoil = [waste_t]
    self.favsurf = [none_t]


class Draugr(Unit):
  name = 'Draugr'
  units = 5
  type = 'infantry'
  gold = 70
  upkeep = 12
  resource_cost = 18
  food = 3
  pop = 20
  terrain_skills = [Burn, Raid] 

  hp = 4
  mp = [2, 2]
  moves = 6
  resolve = 10
  global_skills = [Regroup, NightFerocity]

  dfs = 3
  res = 4
  arm = 0

  att = 2
  damage = 2
  off = 4
  str = 4
  pn = 0
  
  stealth = 6

  fear = 2
  pref_corpses = 1
  def __init__(self, nation):
    super().__init__(nation)
    Ground.__init__(self)
    self.corpses = [Skeletons]
    self.favhill = [0, 1]
    self.favsoil = [tundra_t]
    self.favsurf = [none_t, forest_t, swamp_t]


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
  units = 5
  type = 'beast'
  gold = 60
  upkeep = 15
  resource_cost = 18
  food = 8
  pop = 15
  terrain_skills = [ForestSurvival, MountainSurvival]

  hp = 3
  mp = [2, 2]
  moves = 8
  resolve = 4
  global_skills = [Regroup]

  dfs = 4
  res = 4
  arm = 2
  armor = None

  att = 2
  damage = 2
  off = 5
  str = 5
  pn = 0
  
  stealth = 6

  fear = 3
  def __init__(self, nation):
    super().__init__(nation)
    Ground.__init__(self)
    self.corpses = [DireWolves]
    self.favhill = [0, 1]
    self.favsoil = [tundra_t]
    self.favsurf = [none_t, forest_t]
    self.traits += [animal_t, ]


class Goblins(Unit):
  name = goblins_t
  units = 10
  type = 'infantry'
  gold = 30
  upkeep = 3
  resource_cost = 8
  food = 2
  pop = 14
  terrain_skills = [Burn, ForestSurvival, MountainSurvival, Raid]

  hp = 2
  mp = [2, 2]
  moves = 7
  resolve = 4

  dfs = 3
  res = 2
  arm = 0
  armor = None

  att = 2
  damage = 1
  range = 18
  off = 2
  str = 2
  pn = 0
  
  stealth = 8

  fear = 5
  def __init__(self, nation):
    super().__init__(nation)
    Ground.__init__(self)
    self.corpses = [Skeletons]
    self.favsoil = [waste_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, swamp_t]
    self.favhill = [0, 1]
    self.traits += [goblin_t]


class Harpy(Unit):
  name = harpy_t
  units = 5
  type = 'beast'
  gold = 40
  upkeep = 10
  resource_cost = 16
  food = 0
  pop = 15
  terrain_skills = [ForestSurvival, MountainSurvival, Raid]

  hp = 3
  mp = [4, 4]
  moves = 8
  resolve = 4
  global_skills = [Fly]

  dfs = 3
  res = 3
  arm = 0
  armor = None

  att = 1
  damage = 2
  off = 2
  str = 3
  pn = 0
  
  stealth = 12

  fear = 5
  def __init__(self, nation):
    super().__init__(nation)
    self.favhill = [0, 1]    
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [forest_t, swamp_t]
    self.soil += [coast_t]
    self.traits += [mounster_t]


class HellHounds(Undead):
  name = hellhounds_t
  units = 5
  type = 'beast'
  gold = 160
  upkeep = 20
  resource_cost = 30
  food = 6
  pop = 25
  terrain_skills = [ForestSurvival, MountainSurvival]

  hp = 4
  mp = [2, 2]
  moves = 7
  resolve = 10
  global_skills = [BloodyFeast, Regroup, NightFerocity, NightSurvival]

  dfs = 4
  res = 4
  arm = 2
  armor = None

  att = 2
  damage = 4
  off = 5
  str = 5
  pn = 0
  
  stealth = 12

  fear = 2
  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeletons]
    self.favhill = [0]
    self.favsoil = [plains_t, tundra_t, waste_t]


class Hyaenas(Unit):
  name = 'hyaenas'
  units = 10
  type = 'beast'
  gold = 40
  upkeep = 10
  resource_cost = 15
  food = 6
  pop = 25

  hp = 2
  mp = [2, 2]
  moves = 8
  resolve = 4
  global_skills = [NightSurvival, Regroup]

  dfs = 3
  res = 4
  arm = 0
  armor = None

  att = 1
  damage = 3
  off = 4
  str = 3
  pn = 1
  
  stealth = 6

  fear = 3
  def __init__(self, nation):
    super().__init__(nation)
    Ground.__init__(self)
    self.corpses = [HellHounds]
    self.favhill = [0]
    self.favsoil = [plains_t]
    self.favsurf = [none_t, swamp_t]
    self.traits += [animal_t]


class Hunters(Human):
  name = hunters_t
  units = 10
  type = 'infantry'
  gold = 20
  upkeep = 3
  resource_cost = 12
  food = 3
  pop = 12
  terrain_skills = [ForestSurvival, MountainSurvival]

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 4

  dfs = 2
  res = 2
  arm = 0
  armor = None

  att = 1
  damage = 2
  range = 18
  off = 4
  str = 4
  pn = 0
  
  stealth = 8
  
  arm = 6
  att = 2
  damage = 1
  att = 6
  moves = 6
  range = 10
  resolve = 5
  ranged = 4
  str = 4
  stealth = 6
  units = 5
  units_hp = 2
  
  favored_land = 2
  fear = 90
  food = 3
  forest_survival = 1
  gold = 30
  name = hunters_t
  pop = 7
  populated_land = 0
  sort_chance = 75
  resource_cost = 11
  upkeep = 4
  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Zombies]
    self.favhill = [1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]


class NomadsRiders(Human):
  name = nomads_riders_t
  units = 10
  type = 'cavalry'
  gold = 60
  upkeep = 15
  resource_cost = 18
  food = 6
  pop = 20
  terrain_skills = [Burn, Raid]

  hp = 3
  mp = [4, 4]
  moves = 9
  resolve = 4

  dfs = 3
  res = 3
  arm = 1
  armor = None

  att = 1
  damage = 3
  off = 4
  str = 4
  pn = 0
  offensive_skills = [Charge]
  
  stealth = 6
  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Skeletons]
    self.favhill = [0]
    self.favsoil = [plains_t, grassland_t, tundra_t]
    self.favsurf = [none_t]
    self.traits += [mounted_t]


class Orc_Archers(Unit):
  name = orc_archers_t
  units = 15
  type = 'infantry'
  gold = 20
  upkeep = 3
  resource_cost = 12
  food = 3
  pop = 20
  terrain_skills = [Burn, ForestSurvival, Raid]

  hp = 3
  mp = [2, 2]
  moves = 6
  resolve = 4

  dfs = 3
  res = 2
  arm = 0
  armor = None

  att = 3
  damage = 1
  range = 18
  off = 3
  str = 3
  pn = 0
  
  stealth = 6
  def __init__(self, nation):
    super().__init__(nation)
    Ground.__init__(self)
    self.corpses = [Skeletons]
    self.favhill = [1]    
    self.favsoil = [waste_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t, forest_t]
    self.traits += [orc_t]


class Orcs(Unit):
  name = 'orcos'
  units = 15
  type = 'infantry'
  gold = 30
  upkeep = 8
  resource_cost = 10
  food = 3
  pop = 20
  terrain_skills = [Burn, ForestSurvival, MountainSurvival]

  hp = 3
  mp = [2, 2]
  moves = 7
  resolve = 5

  dfs = 3
  res = 3
  arm = 0
  armor = None

  att = 2
  damage = 2
  off = 3
  str = 3
  pn = 0
  
  stealth = 6
  def __init__(self, nation):
    super().__init__(nation)
    Ground.__init__(self)
    self.corpses = [Skeletons]
    self.favsoil = [waste_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t, forest_t]
    self.traits += [orc_t]


class PeasantLevies(Human):
  name = peasant_levies_t
  units = 10
  type = 'infantry'
  gold = 15
  upkeep = 3
  resource_cost = 10
  food = 3
  pop = 15

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 4

  dfs = 2
  res = 2
  arm = 0
  armor = None

  att = 1
  damage = 2
  off = 2
  str = 2
  pn = 0

  fear = 5
  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Zombies]
    self.favhill = [0, 1]    
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, none_t]


class Raiders(Human):
  name = raiders_t
  units = 10
  type = 'infantry'
  gold = 50
  upkeep = 15
  resource_cost = 14
  food = 3
  pop = 20
  terrain_skills = [Burn, ForestSurvival, MountainSurvival, Raid]

  hp = 2
  mp = [2, 2]
  moves = 6
  resolve = 4

  dfs = 3
  res = 3
  arm = 0
  armor = LightArmor()

  att = 2
  damage = 2
  off = 4
  str = 3
  pn = 0
  
  stealth = 8

  fear = 2
  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Zombies]
    self.favhill = [1]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [forest_t]


class TheKnightsTemplar(Human):
  name = the_knights_templar_t
  units = 5
  type = 'cavalry'
  gold = 150
  upkeep = 60
  resource_cost = 30
  food = 8
  pop = 30
  terrain_skills = [Burn, Raid]

  hp = 3
  mp = [3, 3]
  moves = 8
  resolve = 8
  global_skills = [BattleBrothers, Regroup, Reinforce]

  dfs = 5
  res = 4
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
    self.corpses = [BloodKnights]
    self.favhill = [0]
    self.favsoil = [grassland_t, plains_t, tundra_t, waste_t]
    self.favsurf = [none_t]


class Wargs(Unit):
  name = 'huargos'
  units = 10
  type = 'beast'
  gold = 60
  upkeep = 20
  resource_cost = 18
  food = 6
  pop = 30
  terrain_skills = [ForestSurvival, MountainSurvival]

  hp = 3
  mp = [2, 2]
  moves = 8
  resolve = 5
  global_skills = [Regroup]

  dfs = 4
  res = 4
  arm = 2
  armor = None

  att = 1
  damage = 2
  off = 4
  str = 5
  pn = 0
  
  stealth = 8

  fear = 3
  def __init__(self, nation):
    super().__init__(nation)
    Ground.__init__(self)
    self.corpses = [Skeletons]
    self.favhill = [0, 1]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t]
    self.traits += [mounster_t]


class Warriors(Human):
  name = warriors_t
  units = 10
  type = 'infantry'
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
  res = 3
  arm = 0
  armor = None

  att = 1
  damage = 2
  off = 4
  str = 3
  pn = 0
  def __init__(self, nation):
    super().__init__(nation)
    self.corpses = [Zombies]
    self.favsoil = [glacier_t, grassland_t, plains_t, tundra_t]
    self.favsurf = [forest_t, none_t]


class Wolves(Unit):
  name = wolves_t
  units = 10
  type = 'beast'
  gold = 50
  upkeep = 6
  resource_cost = 14
  food = 4
  pop = 20
  terrain_skills = [ForestSurvival]

  hp = 2
  mp = [2, 2]
  moves = 8
  resolve = 4
  global_skills = [NightFerocity, Regroup]

  dfs = 3
  res = 3
  arm = 0
  armor = None

  att = 1
  damage = 2
  off = 4
  str = 4
  pn = 0
  
  stealth = 10

  fear = 5
  def __init__(self, nation):
    super().__init__(nation)
    Ground.__init__(self)
    self.corpses = [DireWolves]
    self.favhill = [0]
    self.favsoil = [grassland_t, plains_t, tundra_t]
    self.favsurf = [none_t, forest_t]
    self.traits = [animal_t,]