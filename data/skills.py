# -*- coding: utf-8 -*-
from math import ceil, floor
from numpy import mean
from pdb import Pdb
from random import randint, shuffle, choice, uniform
from time import sleep, process_time

from log_module import *
from basics import *
from data.lang.es import *

class Skill:
  effect = 'self'  # all, friend, enemy, self.
  desc = str()
  cast = 6
  cost = 1
  name = 'skill'
  nation = None
  show = 1
  sound = None
  ranking = 0
  tags = []
  type = 'generic' 
  # types: "generic', 'before combat', 'after combat', 'before attack', 'after attack'.
  turns = -1

  def __init__(self, itm):
    self.itm = itm
    self.nation = self.itm.nation    

  def ai_run(self, itm):
    pass

  def cast(self, itm):
    check = self.check_cost(itm)
    if check != 1: return check
    cast = self.check_cast()
    if cast != 1: return cast
    self.run(itm)
  def check_cast(self,itm):
    if roll_dice(2) >= self.cast: return 1
    else: 
      msg = f'{self} {failed_t}.'
      if itm.show_info: sp.speak(msg,1)
      return msg
  def check_cost(self, itm):
    if itm.power < self.cost:
      msg = f'{self}. {needs_t} {power_t}.'
      logging.debug(msg)
      itm.log[-1] += [msg]
      if itm.show_info: sp.speak(msg,1)
      return msg
    else: 
      itm.power -= self.cost
      return 1
  def run(self):
    pass


class Ambushment(Skill):
  name = 'Emboscada'
  desc = '+1 att if unit is hidden.'
  effect = 'self'
  ranking = 5
  type = 'generic'

  def run(self, itm):
    if itm.pos and (itm.pos.hill or itm.pos.surf.name == forest_t):
      if itm.hidden:
        itm.effects += [self.name]
        itm.att_mod += 1


class BattleBrothers(Skill):
  name = 'hermanos de batalla'
  desc = '+1 resolve if 2 squads. +2 resolve if 3 squads.'
  effect = 'self'
  ranking = 3
  type = 'generic'

  def run(self, itm):
    if itm.squads >= 3: 
      itm.effects.append(self.name + str(2))
      itm.resolve_mod += 2
    elif itm.squads >= 2:
      itm.effects.append(self.name + str(1)) 
      itm.resolve_mod += 1


class BattleFocus(Skill):
  name = 'Trance de batalla'
  desc = '++1 hit if unit mp is full.'
  effect = 'self'
  ranking = 3
  type = 'generic'

  def run(self, itm):
    if itm.mp[0] == itm.mp[1]: itm.hit_rolls_mod += 1



class BloodHeal(Skill):
  desc = 'sacrifica un número aleatoreo de población para curarse.'


class BloodRaining(Skill):
  name = 'blood raining'
  desc = ''
  effects = 'all'
  turns = randint(3, 7)
  ranking = 10
  type = 'generic'

  def run(self, itm):
    itm.effects += [self.name]
    if malignant_t in itm.tags:
      itm.resolve_mod += 1
      itm.moves_mod += 1
      itm.res_mod += 2
      itm.str += 2
    else:
      itm.resolve_mod -= 1
      itm.dfs_mod -= 1
      itm.moves_mod -= 1
      itm.off_mod -= 1
      if mounted_t in itm.traits: 
        itm.moves_mod -= 1
        itm.resolve_mod -= 1
      if itm.rng + itm.rng_mod > 5:
        itm.off_mod -= 1
        itm.str_mod -= 1 
        itm.range_mod -= 5



class BloodyBeast(Skill):
  effect = 'self'
  desc = 'randomly kill population if tile has population.'
  name = 'bestia sangrienta'
  turns = 0
  type = 2

  def run(self, itm):
    if itm.pos and itm.pos.pop:
      if roll_dice(1) > 4:
        deads = randint(1, itm.units)
        deads *= itm.att + itm.att_mod
        deads *= itm.damage + itm.damage_mod
        if deads > itm.pos.pop: deads = itm.pos.pop
        itm.pos.pop -= deads
        if itm.pos.pop: itm.pos.unrest += deads * 100 / itm.pos.pop
        if itm.pos.nation.show_info : sleep(loadsound('spell33') * 0.5)
        msg = f'{itm} {deads} deads {in_t} {itm.pos} {itm.pos.cords}.'
        itm.pos.nation.log[-1].append(msg)



class BloodyFeast(Skill):
  name = 'fest�n nocturno'
  desc = '+2 hp restoration in night.'
  effect = 'self'
  ranking = 3
  type = 'generic'

  def run(self, itm):
    if itm.day_night[0]:
      itm.hp_res_mod += 5


class BreathOfTheDesert(Skill):
  desc = 'Envía aires del desierto a una casilla elegida. esto subirá la temperatura y dañara la producción de alimentos.'


class Burn(Skill):
  name = 'quemar'
  desc = 'can destroy buildings'
  effect = 'self'
  ranking = 2
  type = 'generic' 

  def run(self, itm):
    itm.can_burn = 1


class CastBloodRain(Skill):
  name = 'blood rain'
  cost = 40
  cast = 10
  ranking = 5
  type = spell_t

  def ai_run(self, itm):
    self.cast(itm)
  def run(self, itm):
    sleep(loadsound('spell27', channel = ch5, vol = 0.7) / 2)
    dist = randint(3, 6)
    pos = itm.pos
    sq = pos.get_near_tiles(itm.pos.scenary, dist)
    for s in sq:
      if self.name not in [ev.name for ev in s.events]:
        s.events += [BloodRaining(s)]


class Charge(Skill):
  name = 'carga'
  desc = 'charge damage = 1'
  effect = 'self'
  ranking = 5
  type = 'generic'

  def run(self, itm):
    itm.damage_charge_mod += 1


class DarkPresence(Skill):
  name = 'dark presence'
  desc = 'if death: in day: +2 res. '
  desc += 'if night: +1 dfs, +1 moves, +1 off, +2 res, +2 str.'
  effect = 'friend'
  ranking = 5
  type = 'generic'

  def run(self, itm):
    if (itm.nation == self.nation
        and death_t in itm.traits and vampire_t not in itm.traits 
        and self.name not in itm.effects):
      if itm.day_night[0] == 0:
        itm.effects.append(self.name + str(f' ({day_t})'))
        itm.res_mod += 1
      if itm.day_night[0]:
        itm.effects.append(self.name + str(f' ({night_t})'))
        itm.dfs_mod += 1
        itm.moves_mod += 1
        itm.off_mod += 1
        itm.res_mod += 2
        itm.str_mod += 2



class DesertSurvival(Skill):
  name = 'sobreviviente del decierto'
  desc = 'ventajas sin definir.'
  effect = 'self'
  ranking = 3
  type = 'generic'

  def run(self, itm):
    itm.desert_survival = 1
    if itm.pos and itm.pos.soil.name == waste_t: 
      itm.effects.append(self.name)
      itm.stealth_mod += 2


class Fanatism(Skill):
  name = fanatism_t
  desc = '+1 att, +1 str, -2 dfs, +1 moves, +1 resolve if enemy is death.'
  effect = 'self'
  ranking = 3
  type = 'generic'

  def run(self, itm):
    if itm.target and death_t in itm.target.traits:
      itm.effects.append(self.name)
      itm.att_mod += 1
      itm.dfs_mod -= 2
      itm.moves_mod += 1
      itm.resolve_mod += 2
      itm.str_mod += 1


class FearAura(Skill):
  effect = 'enemy'
  desc = '-2 resolve, -2 moves, -1 off, -1 dfs.'
  name = fearaura_t
  ranking = 20
  type = 'generic'  

  def run(self, itm):
    if death_t not in itm.traits and itm != self.itm:
      itm.effects.append(fear_t)
      itm.resolve_mod -= 2
      itm.moves_mod -= 2
      itm.off_mod -= 2
      itm.dfs_mod -= 2
      itm.str_mod -= 1



class FeastOfFlesh(Skill):
  desc = 'sacrifica x población para invocar ogros a su servicio.'

class FireDarts(Skill):
  pass



class Fly(Skill):
  effect = 'self'
  desc = 'unit can fly. enemy can not charge.'
  name = 'vuela'
  ranking = 5
  type = 'generic'

  def run(self, itm):
    itm.can_fly = 1
    if itm.target: itm.target.can_charge = 0


class Furtive(Skill):
  name = 'furtive'
  desc = '+5 stealth.'
  effect = 'self'
  ranking = 5
  type = 'generic'

  def run(self, itm):
    itm.effects.append(self.name)
    itm.stealth_mod += 5


class ForestSurvival(Skill):
  effect = 'self'
  desc = '+2 stealth if unit is on forest.'
  name = 'sobreviviente del bosque'
  ranking = 3
  type = 'generic'

  def run(self, itm):
    itm.forest_survival = 1 
    if itm.pos and itm.pos.surf.name == forest_t: 
      itm.effects.append(self.name)
      itm.can_hide = 1
      itm.stealth_mod += 2


class ForestTerrain(Skill):
  effect = 'all'
  desc = '-2 moves for grount unit, -4 move for mounted unit, -1 off, -1 dfs.unit can not charge, ignores forest survival and flying units. +2 stealth.'
  name = 'forest terrain'
  type = 'generic'

  def run(self, itm):
    itm.stealth_mod += 2
    if itm.forest_survival == 0 and itm.can_fly == 0:
      itm.effects.append(self.name)
      itm.charge = 0
      itm.moves_mod -= 2
      itm.dfs_mod -= 1
      itm.off_mod -= 1
      if mounted_t in itm.traits: itm.moves_mod -= 2


class ForestWalker(Skill):
  effect = 'self'
  desc = '+2 resolve, +1 off, += dfs if unit is into forest.'
  name = 'morador del bosque'
  ranking = 5
  type = 'generic'

  def run(self, itm):
    if itm.pos and itm.pos.surf.name == forest_t:
      itm.effects.append(self.name)
      itm.dfs_mod += 1
      itm.off_mod += 1
      itm.resolve_mod += 1 


class HealingMists(Skill):
  pass

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
    
    if units: self.cast(itm)

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



class ElusiveShadow(Skill):
  name = 'sombra elusiva'
  desc = '+3 stealth on day, +6 stealth on night.'
  effect = 'self'
  ranking = 2
  ranking = 3
  type = 'generic'

  def run(self, itm):
    itm.effects.append(self.name) 
    if itm.day_night[0]: itm.stealth_mod += 6
    elif itm.day_night[0] == 0: itm.stealth_mod += 3


class EnchantedForests(Skill):
  pass


class Ethereal(Skill):
  name = 'et�reo'
  desc = 'Ignores enemy pn.'
  effect = 'self'
  ranking = 10
  type = 'generic'

  def run(self, itm):
    itm.armor_ign_mod = 1


class HeavyCharge(Skill):
  effect = 'self'
  desc = 'charge damage = 3'
  name = 'carga pesada'
  ranking = 10
  type = 'generic'

  def run(self, itm):
    itm.damage_charge_mod += 3


class HillTerrain(Skill):
  effect = 'all'
  desc = '-2 moves for grount units, -4 move for mounted unit, unit can not charge, -1 dfs, -1 off. ignores forest survival and fying units. +5 range if unit is ranged. +2 stealth.'
  name = 'hill terrain'
  type = 'generic'

  def run(self, itm):
    if itm.rng + itm.rng_mod >= 6: itm.rng_mod += 5
    itm.stealth_mod += 2
    if itm.mountain_survival == 0 and itm.can_fly == 0:
      itm.effects.append(self.name)
      itm.charge = 0
      itm.moves_mod -= 2
      itm.dfs_mod -= 1
      itm.off_mod -= 1
      if mounted_t in itm.traits: itm.moves_mod -= 2


class HoldPositions(Skill):
  effect = 'self'
  desc = '+2 dfs if unit mp is full.'
  name = 'hold positions'
  ranking = 5
  type = 'generic'

  def run(self, itm):
    if itm.mp[0] == itm.mp[1]: 
      itm.effects.append(self.name)
      itm.dfs_mod += 2


class Exaltation(Skill):
  name = 'exaltaci�n.'
  desc = 'undefined.'
  effect = 'friend'
  ranking = 0
  type = 'generic'

  def run(self, itm):
    if sacred_t in itm.traits:
      itm.effects += [self.name]
      itm.resolve_mod += 1
      itm.hit_rolls_mod += 1


class ImpalingRoots(Skill):
  effect = 'self'
  desc = ''
  name = 'impaling roots.'
  ranking = 20
  type = 'before attack'

  def run(self, itm):
    if (itm.target 
        and itm.target.dist <= 10 and itm.target.dist > 1):
      target = itm.target
      logging.debug(f'{self.name}.')
      logging.debug(f'{itm.dist=:}, {target.dist=:}.')
      damage = 0
      for r in range(5):
        if damage > target.hp_total: break
        off = 6
        off -= target.dfs + target.dfs_mod
        hit = get_hit_mod(off)
        logging.debug(f'hit {hit}.')
        if roll_dice(1) >= hit:
          st = 6
          st -= target.res + target.res_mod
          wound = get_wound_mod(st)
          logging.debug(f'wound {wound}.')          
          if roll_dice(1) >= wound:
            damage += 2
            if roll_dice(1) == 6:
              damage += 2
      # itm.damage_done[-1] += damage
      if damage:
        if damage > target.hp_total: damage = target.hp_total
        target.hp_total -= damage
        target.update()
        target.deads[-1] += target.c_units - target.units
        itm.battlelog += [f'{self.name} ({itm}) {kills_t} {target.deads[-1]}.']
        logging.debug(f'hiere on {damage}.')


class Inspiration(Skill):
  effect = 'friend'
  desc = '+1 moves, +1 resolve'
  name = 'inspiraci�n'
  ranking = 5
  type = 'generic'

  def run(self, itm):
    if itm.nation == self.nation and itm != self.itm:
      itm.effects.append(self.name)
      itm.moves_mod += 1
      itm.resolve_mod += 1


class Intoxicated(Skill):
  effect = 'self'
  desc = 'Las unidades sufren un n�mero aleatoreo de da�o por turno. durante x turnos.'
  name = intoxicated_t
  turns = randint(5, 10)
  type = 2

  def run(self, itm):
    sk = Weak(itm)
    sk.turns = self.turns
    if sk.name not in [s.name for s in itm.global_skills]:
      itm.global_skills += [sk]
    damage = randint(0, 8)
    if damage and itm.hp_total > 0:
      if damage > itm.hp_total: damage = itm.hp_total
      msg = f'{itm} loses {damage//itm.hp} by {self.name}.'
      itm.log[-1] += [msg]
      itm.nation.log[-1] += [msg]
      itm.hp_total -= damage
      if itm.show_info: sleep(loadsound('spell34', channel = ch5) / 2)


class LongBow(Skill):
  effect = 'self'
  desc = '+1 pn, +5 range, +1 str.'
  name = 'Arco largo'
  type = 'generic'

  def run(self, itm):
    itm.effects.append(self.name)
    itm.pn_mod += 1
    itm.rng_mod += 5
    itm.str_mod += 1


class LordOfBones(Skill):
  name = 'se�or de los huesos'
  effect = 'friend'
  desc = '+1 att, +1 dfs, +1 off.'
  ranking = 5
  type = 'generic'

  def run(self, itm):
    if (itm.nation == self.nation and itm != self.itm 
        and itm.name in [skeletons_t]):
      itm.effects.append(self.name)
      itm.att_mod += 1
      itm.dfs_mod += 1
      itm.off_mod += 1


class LordOfBlodd(Skill):
  effect = 'friend'
  desc = '+1 dfs, +1 moves, +1 off, +1 resolve if unit is ghoul.'
  name = 'se�or de sangre'
  ranking = 5
  type = 'generic'

  def run(self, itm):
    if (itm.nation == self.nation and itm != self.itm 
        and itm.name in [ghouls_t]):
      itm.effects.append(self.name)
      itm.dfs_mod += 1
      itm.moves_mod += 1
      itm.off_mod += 1
      itm.resolve_mod += 1


class MagicDuel(Skill):
  pass


class MassSpears(Skill):
  effect = 'self'
  desc = '+1  off por cada 20 unidades hasta 3.. Anula la carga enemiga de caballer�a.'
  name = 'lanzas en masa'
  ranking = 5
  type = 'generic'

  def run(self, itm):
    if itm.units >= 30:
      itm.effects.append(self.name + str(2)) 
      itm.off_mod += 2
    elif itm.units >= 20:
      itm.effects.append(self.name + str(1)) 
      itm.off_mod += 1
    if itm.target: itm.target.can_charge = 0


class MastersEye(Skill):
  name = 'ojos del amo'
  effect = 'friend'
  desc = '+1 att, +1 hit roll, +1 str, +1 res.'
  ranking = 5
  type = 'generic'

  def run(self, itm):
    if itm != self.itm and itm.nation == self.nation:
      itm.effects.append(self.name)
      itm.hit_rolls_mod += 1
      itm.res_mod += 1
      itm.str_mod += 1
      itm.moves_mod += 1


class Mist(Skill):
  pass


class Night(Skill):
  effect = 'all'
  desc = '-1 off, -1dfs, -5 range if unit range is more than 5. +2 stealth.'
  name = night_t
  type = 'generic'

  def run(self, itm):
    if itm.day_night[0]:
      itm.effects.append(self.name)
      itm.stealth_mod += 2
      if itm.rng + itm.rng_mod > 5: itm.rng_mod -= 5


class NightFerocity(Skill):
  effect = 'self'
  desc = 'if night: +1 att, +1 moves.'
  name = 'ferocidad nocturna'
  ranking = 5
  type = 'generic'

  def run(self, itm):
    if itm.day_night[0]:
      itm.effects.append(self.name) 
      itm.att_mod += 1
      itm.moves_mod += 1


class NightSurvival(Skill):
  effect = 'self'
  desc = '+5 power_restoration, +3 hp restoration.'
  name = 'sobreviviente nocturno'
  ranking = 2
  type = 'generic'

  def run(self, itm):
    itm.night_survival = 1
    if itm.day_night[0]:
      itm.effects.append(self.name)
      if itm.power: itm.power_res_mod += 5
      itm.hp_res_mod += 3


class MountainSurvival(Skill):
  effect = 'self'
  desc = 'invisible en las monta�as., +2 stealth.'
  name = 'sobreviviente de las monta�as'
  ranking = 3
  type = 'generic'

  def run(self, itm):
    itm.mountain_survival = 1
    if itm.pos and itm.pos.hill:
      itm.effects.append(self.name)
      itm.can_hide = 1
      itm.stealth_mod += 2


class Organization(Skill):
  effect = 'friend'
  desc = '+1 off, +1 dfs.'
  name = 'organizaci�n'
  ranking = 3
  type = 'generic'

  def run(self, itm):
    if (itm.nation == self.nation
        and human_t in itm.traits
        and all(i not in itm.traits for i in [commander_t, leader_t])):
      itm.effects.append(self.name)
      itm.dfs_mod += 1
      itm.off_mod += 1


class PikeSquare (Skill):
  effect = 'self'
  desc = '+1 att if 2squads, +2 att if 3 squads. Enemy can not charge.'
  name = 'formaci�n de picas'
  ranking = 3
  type = 'generic'

  def run(self, itm):
    if itm.units >= 40:
      itm.effects.append(self.name) 
      itm.att_mod += 1
    if itm.target: 
      itm.target.can_charge = 0


class PoisonCloud(Skill):
  pass


class Raid(Skill):
  effect = 'self'
  desc = 'can raid tiles.'
  name = 'saquear'
  ranking = 2
  type = 'generic'

  def run(self, itm):
    itm.can_raid = 1


class RaiseDead(Skill):
  name = raise_dead_t
  cost = 20
  cast = 6
  ranking = 10
  type = 'generic'
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


class Regroup(Skill):
  name = 'reagruparse'
  desc = 'if a combat ends with a victory, all retreats are recovered.'
  effect = 'self'
  ranking = 3
  type = 'after combat'

  def run(self, itm):
    if itm.target and itm.target.hp_total < 1:
      itm.hp_total += sum(itm.fled) * itm.hp
      msg = f'{itm.name} recupera {sum(itm.fled)} unidades huidas.' 
      itm.log[-1] += [msg]
      logging.debug(msg)


class Reinvigoration(Skill):
  desc = 'sacrifica x población para regenerar poder.'


class ReadyAndWaiting(Skill):
  effect = 'self'
  desc = '+1 off +1 str if unit has his max mp'
  name = 'listos y esperando'
  ranking = 3
  type = 'generic'

  def run(self, itm):
    if itm.mp[0] == itm.mp[1]:
      itm.effects += [self.name]
      itm.off_mod += 1
      itm.str_mod += 1


class Refit(Skill):
  name = 'refuerzos'
  desc = '+2 sts if at friendly position and units less than maximum units.'
  effect = 'self'
  ranking = 3
  type = 'generic'

  def run(self, itm):
    if itm.pos and itm.pos.nation == itm.nation:
      itm.effects.append(self.name)
      itm.sts_mod += 2


class SanguineHeritage(Skill):
  desc = 'la unidad infectada tiene x probabilidades de volverse vampiro.'


class SermonOfCourage(Skill):
  effect = 'friend'
  desc = '+1 resolve a las unidades humanas.'
  name = 'serm�n de coraje'
  ranking = 3
  type = 'generic'

  def run(self, itm):
    if itm != self.itm and human_t in itm.traits: 
      itm.effects.append(self.name)
      itm.resolve_mod += 1


class SecondSun(Skill):
  desc = 'crea un segundo sol negando la noche y dañando la agricultura de los lugares afectados.'


class ShadowHunter(Skill):
  effect = 'self'
  name = 'cazador de sombras'
  desc = '+2 damage, +2 str if enemy is death.'
  ranking = 5
  type = 'generic'

  def run(self, itm):
    if itm.target and death_t in itm.target.traits:
      itm.effects.append(self.name)
      itm.damage_sacred_mod += 2
      itm.moves_mod += 1
      itm.str_mod += 2


class SkeletonLegion(Skill):
  effect = 'self'
  desc = '+1 att if 2 squads, +2 if 3 squads.'
  name = 'legion de esqueletos'
  ranking = 5
  type = 0

  def run(self, itm):
    if itm.squads >= 3:
      itm.effects.append(self.name + str(2)) 
      itm.att_mod += 2
    elif itm.squads >= 2:
      itm.effects.append(self.name + str(1)) 
      itm.att_mod += 1


class Skirmisher(Skill):
  name = 'retirada'
  desc = 'units gain half moves in distanse on combat.'
  effect = 'self'
  ranking = 8
  type = 'after attack'

  def run(self, itm):
    if itm.target and itm.dist < itm.rng + itm.rng_mod: 
      if itm.target.hp_total < 1: return
      dist = randint(1, itm.moves + itm.moves_mod)
      dist = ceil(dist / 2)
      itm.dist += dist
      itm.target.dist += dist
      itm.battlelog += [f'{itm} go back {dist}.']


class Spread(Skill):
  effect = 'self'
  desc = 'resucita y une enemigos caidos a la unidad.'
  cast = 4
  name = 'Plaga zombie'
  ranking = 10
  type = 'after attack'

  def run(self, itm):
    if death_t not in itm.target.traits:
      deads = sum(itm.target.deads)
      for i in range(deads):
        roll = roll_dice(2)
        if roll >= self.cast:
          itm.hp_total += itm.hp
          itm.raised[-1] += 1
          itm.target.deads[-1] -= 1
          if itm.target.deads[-1] < 0: itm.target.deads[-1] = 0
          logging.debug(f'reanima {itm.raised[-1]}.')


class Surrounded(Skill):
  effect = 'self'
  desc = '+1 off, str if 2 squads. +2 off, str if 3 squads.. +3 off, str if 4 squads.'
  name = 'rodeados'
  type = 'generic'

  def run(self, itm):
    if itm.squads >= 4:
      itm.effects.append(self.name + str(3))
      itm.off_mod += 3
      itm.str_mod += 3
    elif itm.squads >= 3:
      itm.effects.append(self.name + str(2))
      itm.off_mod += 2
      itm.str_mod += 2
    elif itm.squads >= 2:
      itm.effects.append(self.name + str(1))
      itm.off_mod += 1
      itm.str_mod += 1


class SummonAwakenTree(Skill):
  name = 'summon awaken tree'
  cost = 50
  cast = 9
  ranking = 5
  type = 'spell'
  tags = ['summon']

  def ai_run(self, itm):
    self.cast(itm)

  def run(self, itm):
    itm.pos.add_unit(AwakenTree, itm.nation.name)
    msg = f'{AwakenTree} has been sommoned'
    logging.debug(msg)
    itm.log[-1] += [msg]


class SummonDevourerOfDemons(Skill):
  name = 'summon devourer of demons'
  cost = 30
  cast = 10
  ranking = 5
  type = 'spell'
  tags = ['summon']

  def ai_run(self, itm):
    if itm.pos.around_nations and itm.pos.around_snation == []:
      self.cast(itm)

  def run(self, itm):
    itm.pos.add_unit(DevourerOfDemons, wild_t)
    msg = f'{AwakenTree} has been sommoned'
    logging.debug(msg)
    itm.log[-1] += [msg]


class SummonDriads(Skill):
  name = 'summon driads'
  cost = 40
  cast = 7
  ranking = 5
  type = 'spell'
  tags = ['summon']

  def ai_run(self, itm):
    self.cast(itm)

  def run(self, itm):
    itm.pos.add_unit(Driads, itm.nation.name)
    msg = f'{AwakenTree} has been sommoned'
    logging.debug(msg)
    itm.log[-1] += [msg]



class SummonForestBears(Skill):
  name = 'summon forest bears'
  cost = 20
  cast = 8
  ranking = 5
  type = 'spell'
  tags = ['summon']

  def ai_run(self, itm):
    if itm.pos.surf and itm.pos.surf == forest_t: self.cast(itm)

  def run(self, itm):
    itm.pos.add_unit(ForestBears, itm.nation.name)
    msg = f'{AwakenTree} has been sommoned'
    logging.debug(msg)
    itm.log[-1] += [msg]



class SummonForestFalcons(Skill):
  name = 'summon forest falcons'
  cost = 10
  cast = 6
  ranking = 5
  type = 'spell'
  tags = ['summon']

  def ai_run(self, itm):
    if itm.pos.surf and itm.pos.surf == forest_t: self.cast(itm)

  def run(self, itm):
    itm.pos.add_unit(SummonForestFalcons, itm.nation.name)
    msg = f'{AwakenTree} has been sommoned'
    logging.debug(msg)
    itm.log[-1] += [msg]


class SummonSpectralInfantry(Skill):
  name = 'summon spectral infantry'
  cost = 20
  cast = 8
  ranking = 5
  type = 'spell'
  tags = ['summon']

  def ai_run(self, itm):
    self.cast(itm)

  def run(self, itm):
    itm.pos.add_unit(SpectralInfantry, itm.nation.name)
    msg = f'{AwakenTree} has been sommoned'
    logging.debug(msg)
    itm.log[-1] += [msg]


class Scavenger(Skill):
  effect = 'self'
  desc = '+1 res, +1 str if corpses on field.'
  name = 'carro�a'
  ranking = 5
  type = 'generic'

  def run(self, itm):
    if itm.pos and itm.pos.corpses:
      itm.effects += {self.name}
      itm.res_mod += 1
      itm.str_mod += 1


class Scream(Skill):
  effect = 'selv'
  desc = 'if roll >= 4 enemy morale check fails..'
  name = 'grito ardiente'
  ranking = 10
  type = 'before attack'

  def run(self, itm):
    if itm.target:
      target = itm.target
      logging.debug(f'grito ardiente.')
      if death_t not in target.traits:
        roll = roll_dice(1)
        if roll >= 5: 
          damage = randint(4, 10)
          itm.damage_done[-1] += damage
          target.hp_total -= damage
          target.update()
          target.deads[-1] += target.c_units - target.units
          logging.debug(f'hiere.')
        if roll >= 3: target.combat_retreat()


class SwampSurvival(Skill):
  effect = 'selv'
  desc = '+3 stealth in swams.'
  name = 'sobreviviente del pantano'
  ranking = 3
  type = 'generic'

  def run(self, itm):
    if itm.pos and itm.pos.name == swamp_t:
      itm.effects += [self.name]
      itm.stealth_mod += 3


class SwampTerrain(Skill):
  effect = 'all'
  desc = '-1 dfs, -1 off,-2 moves for grount unit, -4 move for mounted unit, unit can not charge. ignores swamp survival and flying units.'
  name = 'swamp terrain'
  type = 'generic'

  def run(self, itm):
    if itm.swamp_survival == 0 and itm.can_fly == 0:
      itm.effects.append(self.name)
      itm.charge = 0
      itm.dfs_mod -= 1
      itm.moves_mod -= 2
      itm.off_mod -= 1
      if mounted_t in itm.traits: itm.moves_mod -= 2


class TerrainEffects(Skill):
  effect = 'self'
  desc = ''
  name = 'terrain effects.'
  show = 0
  type = 'generic'

  def run(self, itm):
    if itm.flying == 0 and itm.pos:
      if itm.pos.surf.name == forest_t:
        itm.skills.append(ForestTerrain)
      if itm.surf.name == swamp_t:
        itm.skills.append(SwampTerrain)


class TheBeast(Skill):
  name = 'la bestia'  
  effect = 'self'
  desc = 'Randomly kills population in position.'
  turns = 0
  type = 2

  def run(self, itm):
    if itm.pos and roll_dice(2) >= 6 and itm.day_night[0]:
      if itm.pos.pop:
        deads = randint(2, 5) * itm.units
        if deads > itm.pos.pop: deads = itm.pos.pop
        itm.pos.pop -= deads
        if itm.pos.pop: itm.pos.unrest += deads * 100 / itm.pos.pop
        if itm.pos.nation.show_info : sleep(loadsound('spell33') * 0.5)
        msg = f'{itm} {deads} deads {in_t} {itm.pos} {itm.pos.cords}.'
        itm.nation.log[-1].append(msg)
      elif itm.pos.pop == 0 and roll_dice(2) >= 10:
        if itm.nation.show_info: sleep(loadsound('spell36') * 0.5)
        msg = f'{itm} es ahora {itm.align()}.'
        itm.nation.log[-1].append(msg)
        itm.set_default_align()


class ToxicClaws(Skill):
  effect = 'self'
  desc = 'units loses x damage per turn during x turns.'
  name = 'garras t�xicas.'
  ranking = 5
  type = 'after attack'

  def run(self, itm):
    if (itm.target and sum(itm.damage_done)
        and death_t not in itm.target.traits):
      logging.debug(f'{self.name} damage done {itm.damage_done}.')
      if roll_dice(1) >= 3:
        sk = Intoxicated(itm.target)
        sk.turns = sum(itm.damage_done)
        if Intoxicated.name not in [s.name for s in itm.target.skills]: 
          itm.target.other_skills += [sk]
          msg = [f'{itm.target} {is_t} intoxicated by {itm}. {sk.turns}']
          itm.target.log[-1] += [msg]
          itm.battlelog += [msg]


class VigourMourtis(Skill):
  effect = 'friend'
  desc = '+1 hit roll si la unidad es death'
  name = 'vigor mortis'
  ranking = 5
  type = 'generic'

  def run(self, itm):
    if itm != self.itm and death_t in itm.traits:
      itm.effects.append(self.name)
      itm.hit_rolls_mod += 1


class WailingWinds(Skill):
  desc = 'un nigromante invoca vientos de lamentos. estos vientos reducirán la moral de las unidades enemigas.'


class Weak(Skill):
  effect = 'self'
  desc = '-2 off, -2 dfs, -2 moves, -2 str.'
  name = weak_t
  ranking = -5
  type = 'generic'

  def run(self, itm):
    itm.effects += [self.name]
    itm.dfs_mod -= 2
    itm.moves_mod -= 2
    itm.off_mod -= 2
    itm.str_mod -= 2
