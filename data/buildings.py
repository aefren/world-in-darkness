print(f'carga buildings.')
from data.units import *
from log_module import *


class Building:
  around_coast = 0
  base = None
  citylevel = None
  corruption = 0
  corruption_pre = 0
  defense_terrain = 0
  food = 0
  food_pre = 0
  free_terrain = 0
  gold = 0
  grouth = 0
  grouth_total = 0
  grouth_pre = 0
  income = 0
  income_pre = 0
  is_complete = 0
  name = None
  nation = None
  nick = None
  own_terrain = 1
  prod_progress = 0
  public_order = 0
  public_order_pre = 0
  resource = 0
  res_pre = 0
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
      self.corruption_pre = base.corruption
      self.food_pre = base.food
      self.grouth_pre = base.grouth_total
      self.income_pre = base.income
      self.public_order_pre = base.public_order
      self.res_pre = base.resource 
  
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
    if pos.around_coast < self.around_coast: go = 0
    if pos.nation and self.free_terrain: go = 0
    if pos.nation != self.nation and self.own_terrain: go = 0    
    return go
  def __str__(self):
    name = f'{self.name}.' 
    if self.nick:
      name += f' {self.nick}.'
    return name
  def update(self):
    self.is_complete = 1 if self.resource_cost[0] >= self.resource_cost[1] else 0


#Holy Empire.
class TrainingCamp(Building):
  gold = 3000
  name = 'campo de entrenamiento'
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
  gold = 5000
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
  base = ImprovedTrainingCamp
  gold = 7000
  name = 'cuartel'
  public_order = 10
  tags = [military_t, unrest_t]
  unique = 1
  upkeep = 10
  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [SpearMen, GreatSwordsMen, Aquilifer]
    self.resource_cost = [0, 120]
    self.size = 0
    self.upgrade = [ImprovedBarracks]


class ImprovedBarracks(Barracks, Building):
  base = Barracks
  gold = 10000
  name = 'cuartel mejorado'
  public_order = 15
  tags = [military_t, unrest_t]
  unique = 1
  upkeep = 15
  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Halberdier, CrossBowMen]
    self.resource_cost = [0, 200]
    self.size = 0


class Pastures(Building):
  food = 25
  gold = 6000
  income = 20
  name = 'pasturas'
  own_terrain = 1
  size = 6
  tags = [military_t]
  unique = 1
  upkeep = 10
  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Equites]
    self.resource_cost = [0, 80]
    self.soil = [grassland_t, plains_t]
    self.surf = [none_t]
    self.hill = [0]
    self.upgrade = [Stables]


class Stables(Pastures, Building):
  base = Pastures
  gold = 10500
  name = 'establos'
  upkeep = 25
  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Equites2]
    self.resource_cost = [0, 140]
    self.size = 0
    self.hill = [0]
    self.upgrade = []


class MeetingCamp(Building):
  gold = 2000
  name = 'campo de reunión'
  own_terrain = 1
  public_order = 10
  size = 4
  tags = [military_t]
  unique = 1
  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Flagellants]
    self.resource_cost = [0, 50]
    self.soil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [0]
    self.upgrade = [CultOfLight]


class CultOfLight(MeetingCamp, Building):
  base = MeetingCamp
  gold = 3200
  name = 'culto de la luz'
  public_order = 25
  upkeep = 10
  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Inquisitors, PriestWarriors]
    self.resource_cost = [0, 100]
    self.size = 0
    self.upgrade = [TempleOfLight]


class TempleOfLight(CultOfLight, Building):
  base = CultOfLight
  gold = 6000
  name = 'templo de la luz'
  public_order = 50
  upkeep = 20
  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Priest]
    self.resource_cost = [0, 160]
    self.size = 0
    self.upgrade = []



#Vampire.
class Cemetery(Building):
  gold = 2000
  name = cemetery_t
  own_terrain = 1
  size = 4
  tags = [military_t]
  unique = 1
  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Ghouls, Skeletons]
    self.resource_cost = [0, 30]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [none_t]
    self.hill = [0]
    self.upgrade = [Barrow]


class Barrow(Cemetery, Building):
  base = Cemetery
  gold = 4500
  name = 'túmulos'
  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [CryptHorrors, GraveGuards]
    self.resource_cost = [0, 70]
    self.size = 0
    self.upgrade = [Mausoleum]


class Mausoleum(Barrow, Building):
  base = Barrow
  gold = 10000
  name = 'mausoleo'
  upkeep = 10
  public_order = 20
  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units += [Vargheist, VladDracul]
    self.resource_cost = [0, 150]
    self.size = 0
    self.upgrade = []


class DesecratedRuins (Building):
  gold = 3500
  name = 'ruinas profanadas'
  own_terrain = 1
  size = 4
  tags = [military_t]
  unique = 1
  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Zombies]
    self.resource_cost = [0, 50]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [0, 1]
    self.upgrade = [CircleOfBlood]


class CircleOfBlood(DesecratedRuins, Building):
  base = DesecratedRuins
  gold = 4500
  name = 'circulo de sangre'
  upkeep = 5
  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Vampire, BlackKnights]
    self.resource_cost = [0, 100]
    self.size = 0
    self.upgrade = [DarkMonolit]


class DarkMonolit(CircleOfBlood, Building):
  base = CircleOfBlood
  gold = 8000
  name = 'monolito oscuro'
  own_terrain = 1
  size = 4
  upkeep = 20
  public_order = 50
  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [Banshee]
    self.resource_cost = [0, 250]
    self.size = 0
    self.upgrade = []


class SmallWood(Building):
  gold = 2000
  name = 'Bosquecillo'
  own_terrain = 1
  size = 5
  tags = [military_t]
  unique = 1
  def __init__(self, nation, pos):
    super().__init__(nation,pos)
    self.av_units = [Bats]
    self.resource_cost = [0, 60]
    self.surf = [forest_t]
    self.hill = [0]
    self.upgrade = [SinisterForest]


class SinisterForest(SmallWood, Building):
  base = SmallWood
  gold = 5000
  name = 'bosque abyssal'
  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.av_units = [DireWolves, FellBats]
    self.resource_cost = [0, 100]
    self.size = 0
    self.upgrade = []


class Gallows(Building):
  gold = 1000
  income = 15
  name = 'Gallows'
  own_terrain = 1
  size = 2
  tags = [income_t, unrest_t]
  public_order = 20
  def __init__(self, nation, pos):
    super().__init__(nation,pos)
    self.resource_cost = [0, 40]
    self.soil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t, swamp_t]
    self.hill = [0, 1]
    self.upgrade = [ImpaledField]


class ImpaledField(Gallows, Building):
  base = Gallows
  gold = 2000
  income = 30
  name = 'campo de empalados'
  public_order = 66
  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 60]
    self.size = 0
    self.upgrade = []


class Pit(Building):
  food = 50
  gold = 500
  grouth = 20
  name = 'fosa'
  own_terrain = 1
  resource_cost = 0
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
  base = Pit
  food = 120
  gold = 1500
  grouth = 60
  income = 20
  name = 'mazmorra funeraria'
  resource_cost = 1
  tags = [food_t, resource_t]
  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 80]
    self.size = 0
    self.upgrade = []


#Others.
class Dock(Building):
  food = 0
  gold = 4000
  grouth= 20
  income = 25
  name = 'dock'
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
  food = 50
  gold = 800
  grouth= 20
  income = 10
  name = fields_t
  own_terrain = 1
  size = 6
  tags = [food_t]
  def __init__(self, nation, pos):
    super().__init__(nation,pos)
    self.resource_cost = [0, 40]
    self.soil = [grassland_t, plains_t]
    self.surf = [none_t]
    self.hill = [0]
    self.upgrade = [Farm]


class Farm(Fields, Building):
  base = Fields
  food = 100
  gold = 2000
  grouth = 50
  income = 20
  name = farm_t
  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 80]
    self.size = 0
    self.upgrade = []


class ExtendedFarm(Farm, Building):
  base = Farm
  food = 200
  gold = 3500
  grouth = 40
  income = 40
  name = extendedfarm_t
  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    Farm.__init__(self)
    self.resource_cost = [0, 150]
    self.size = 0
    self.upgrade = []


class Market(Building):
  food = 25
  gold = 200
  income = 20
  resource_cost = 50
  tags = [food_t, income_t, rest_t]


class Quarry(Building):
  gold = 2500
  income = 20
  name = 'cantera'
  own_terrain = 1
  resource_cost = 100
  size = 6
  tags = [resource_t]
  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 70]
    self.soil = [waste_t, glacier_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t, none_t]
    self.hill = [1]



class SawMill(Building):
  gold = 3000
  name = 'aserradero'
  own_terrain = 1
  resource_cost = 50
  size = 6
  tags = [resource_t]
  def __init__(self, nation, pos):
    super().__init__(nation, pos)
    self.resource_cost = [0, 60]
    self.soil = [waste_t, grassland_t, plains_t, tundra_t]
    self.surf = [forest_t]
    self.hill = [0, 1]




# Naciones.



# Unidades.






