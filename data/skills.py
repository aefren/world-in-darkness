# -*- coding: utf-8 -*-
from math import ceil, floor
from numpy import mean
from pdb import Pdb
from random import randint, shuffle, choice, uniform
from time import sleep, process_time

from log_module import *
import basics
from data.lang.es import *
from sound import *


class Skill:
  name = 'skill'
  desc = str()
  effect = 'self'  # all, friend, enemy, self.
  cast = 6
  cost = 1
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
  def run(self, itm):
    pass
  def tile_run(self, itm):
    pass

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




class BloodRaining(Skill):
  name = 'blood raining'
  desc = ''
  effects = 'all'
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
  def tile_run(self, itm):
    self.turn -= 1


class BloodyBeast(Skill):
  name = 'bestia sangrienta'
  desc = 'randomly kill population if tile has population.'
  effect = 'self'
  turns = 0
  type = 2

  def run(self, itm):
    if itm.pos and itm.pos.pop:
      if basics.roll_dice(1) > 4:
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
    if itm.day_night:
      itm.hp_res_mod += 5


class Burn(Skill):
  name = 'quemar'
  desc = 'can destroy buildings'
  effect = 'self'
  ranking = 2
  type = 'generic' 

  def run(self, itm):
    itm.can_burn = 1


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
        and malignant_t in itm.traits 
        and vampire_t not in itm.traits and self.name not in itm.effects):
      if itm.day_night == 0:
        itm.effects.append(self.name + str(f' ({day_t})'))
        itm.res_mod += 1
      if itm.day_night:
        itm.effects.append(self.name + str(f' ({night_t})'))
        itm.dfs_mod += 1
        itm.moves_mod += 1
        itm.off_mod += 1
        itm.res_mod += 2
        itm.str_mod += 2


class DarkVision(Skill):
  name = 'dark vision'
  desc = 'units won get night vision effects.'
  effect = 'self'
  ranking = 5
  type = 'generic'

  def run(self, itm):
    itm.effects.append(self.name) 
    itm.dark_vision = 1


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


class Eclipse(Skill):
  name = 'eclipse'
  desc = '-1 off, -1dfs, -5 range if unit range is more than 5. +2 stealth.'
  effect = 'all'
  type = 'generic'

  def run(self, itm):
    itm.effects.append(self.name)
    itm.stealth_mod += 2
    if itm.dark_vision == 0 and itm.pos.day_night == 0:
      itm.dfs_mod -= 1
      itm.off_mod -= 1
      if itm.rng + itm.rng_mod > 5: itm.rng_mod -= 5
    if malignant_t in itm.traits:
      itm.off_mod += 2
      itm.str_mod += 2
  def tile_run(self, itm):
    self.turns -= 1
    itm.events = [ev for ev in itm.events if ev.name != SecondSun.name]
    itm.day_night = 0


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
      #itm.can_hide = 1
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
  name = 'morador del bosque'
  desc = '+2 resolve, +1 off, += dfs if unit is into forest.'
  effect = 'self'
  ranking = 5
  type = 'generic'

  def run(self, itm):
    if itm.pos and itm.pos.surf.name == forest_t:
      itm.effects.append(self.name)
      itm.dfs_mod += 1
      itm.off_mod += 1
      itm.resolve_mod += 1 


class ElusiveShadow(Skill):
  name = 'sombra elusiva'
  desc = '+3 stealth on day, +6 stealth on night.'
  effect = 'self'
  ranking = 2
  ranking = 3
  type = 'generic'

  def run(self, itm):
    itm.effects.append(self.name) 
    if itm.day_night: itm.stealth_mod += 6
    elif itm.day_night == 0: itm.stealth_mod += 3



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


class Storm(Skill):
  name = 'heavy rain'
  desc = 'if unit is ranged -4 rng, -1 off.'
  effects = 'self'
  ranking = 0
  type = 'generic'

  def run(self, itm):
    if itm.rng+itm.rng_mod >= 5:
      itm.effects += [self.name]
      itm.rng_mod -= 4
      itm.off_mod -= 1
  def tile_run(self, itm):
    itm.raining = 1
    itm.flood = 2
    roll = basics.roll_dice(1)
    if roll >= 5: itm.flood += 1
    if roll >= 6: itm.flood += 1
    self.turns -= 1
    if itm.soil.name == waste_t: self.turns -= 1
    if roll >= 5:
      itm.events += [mist(itm)]
    for ev in itm.events:
      if 'miasma' in ev.tags: ev.turns -= 1


class HillTerrain(Skill):
  name = 'hill terrain'
  desc = '-2 moves for grount units, -4 move for mounted unit, unit can not charge, -1 dfs, -1 off. ignores forest survival and fying units. +5 range if unit is ranged. +2 stealth.'
  effect = 'all'
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
  #ranking = 20
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
        if basics.roll_dice(1) >= hit:
          st = 6
          st -= target.res + target.res_mod
          wound = get_wound_mod(st)
          logging.debug(f'wound {wound}.')          
          if basics.roll_dice(1) >= wound:
            damage += 2
            if basics.roll_dice(1) == 6:
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
  name = 'inspiraci�n'
  desc = '+1 hit roll, +1 resolve.'
  effect = 'friend'
  ranking = 5
  type = 'generic'

  def run(self, itm):
    if itm.nation == self.nation and itm != self.itm:
      itm.effects.append(self.name)
      itm.hit_rollss_mod += 1
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
  desc = '+1 att, +1 hit roll, +1 str, +1 res.'
  effect = 'friend'
  ranking = 5
  type = 'generic'

  def run(self, itm):
    if itm != self.itm and itm.nation == self.nation:
      itm.effects.append(self.name)
      itm.hit_rolls_mod += 1
      if death_t in itm.traits:
        itm.effects += [f'{death_t}.']
        itm.moves_mod += 1
        itm.res_mod += 1
        itm.str_mod += 1
      if malignant_t in itm.traits:
        itm.effects += [f'{malignant_t}']
        itm.resolve_mod += 1



class Miasma(Skill):
  name = 'miasma'
  desc = ''
  effects = 'self'
  ranking = 0
  type = 2
  turns = -1
  tags = ['miasma']
  def run(self, itm):
    itm.effects += [self.name]
    roll = basics.roll_dice(1)
    if roll >= 5:
      if self.name not in [ev.name for ev in itm.pos.events]:
        sk = Miasma(itm.pos)
        sk.turns = randint(5, 15)
        itm.pos.events += [sk]
        msg = f'miasma in {itm.pos} {itm.pos.cords}.'
        if itm.pos.nation: itm.pos.nation.log[-1] += [msg]
        logging.debug(msg)
        if itm.pos.nation and itm.pos.nation.show_info:
          sleep(loadsound('notify25', channel=ch4) *0.3)
  def tile_run(self, itm):
    self.turns -= 1
    if itm.pop: 
      pop_death = randint(2, 10)
      msg = f'miasma {kills_t} {pop_death*itm.pop/100}.'
      logging.debug(msg)
      itm.nation.log[-1] += [msg]
      itm.pop -= pop_death*itm.pop/100
      if itm.nation.show_info: sleep(loadsound('notify23'))
    roll = basics.roll_dice(1)
    if roll >= 6 and itm.units:
      units = [u for u in itm.units if poisonres_t not in u.traits
               and death_t not in u.traits]
      if units:
        unit = choice(units)
        turns = randint(1,3)
        roll = basics.roll_dice(1)
        if roll >= 6: turns += 5
        elif roll >= 5: turns += 3
        else: turns += 1
        sk = Intoxicated(unit)
        sk.turns = turns        
        if Intoxicated.name not in [s.name for s in unit.skills]: 
          unit.other_skills += [sk]


class mist(Skill):
  name = 'mist'
  desc = '-1 rng if ranged unit, +3 stealth.'
  effect = 'all'
  type = 'generic'

  def run(selfself, itm):
    itm.effects += [self.name]
    itm.stealth_mod += 3
    if itm.rng+itm.rng_mod > 5: itm.rng_mod -= 3

class Night(Skill):
  name = night_t
  desc = '-1 off, -1dfs, -5 range if unit range is more than 5. +2 stealth.'
  effect = 'all'
  type = 'generic'

  def run(self, itm):
    if (itm.day_night 
        and SecondSun.name not in [ev.name for ev in itm.pos.events]):
      itm.effects.append(self.name)
      itm.stealth_mod += 2
      if itm.dark_vision == 0:
        itm.dfs_mod -= 1
        itm.off_mod -= 1
        if itm.rng + itm.rng_mod > 5: itm.rng_mod -= 5


class NightFerocity(Skill):
  name = 'ferocidad nocturna'
  desc = 'if night: +1 att, +1 moves.'
  effect = 'self'
  ranking = 5
  type = 'generic'

  def run(self, itm):
    if itm.day_night:
      itm.effects.append(self.name) 
      itm.att_mod += 1
      itm.moves_mod += 1


class NightSurvival(Skill):
  name = 'sobreviviente nocturno'
  desc = '+5 power_restoration, +2 hp restoration.'
  effect = 'self'
  ranking = 2
  type = 'generic'

  def run(self, itm):
    itm.night_survival = 1
    if itm.day_night:
      itm.effects.append(self.name)
      if itm.power: itm.power_res_mod += 5
      itm.hp_res_mod += 2


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
  name = 'organizaci�n'
  desc = '+1 off, +1 dfs. +1 resolve if unit is not sacred.'
  effect = 'friend'
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


class PyreOfCorpses(Skill):
  name = 'pyre of corpses'
  desc = 'burn corpses at position.'
  effect = 'self'
  type = 2

  def run(self, itm):
    if itm.pos.corpses: 
      crp = choice(itm.pos.corpses)
      crp.deads[0] -= (itm.units//2)//crp.hp
      




class Raid(Skill):
  effect = 'self'
  desc = 'can raid tiles.'
  name = 'saquear'
  ranking = 2
  type = 'generic'

  def run(self, itm):
    itm.can_raid = 1


class Rain(Skill):
  name = 'raining'
  desc = ''
  effects = 'self'
  ranking = 0
  type = 'generic'

  def run(self, itm):
    if itm.rng+itm.rng_mod > 5:      
      itm.effects += [self.name]
      itm.off_mod -= 1
  def tile_run(self, itm):
    itm.raining = 1
    itm.flood += 1
    roll = basics.roll_dice(1)
    if roll >= 5: itm.flood += 1
    if roll >= 6: itm.flood += 1
    self.turns -= 1
    if itm.soil.name == waste_t: self.turns -= 1
    for ev in itm.events:
      if 'miasma' in ev.tags: ev.turns -= 1


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



class SermonOfCourage(Skill):
  name = 'serm�n de coraje'
  desc = '+2 resolve if unit is sacred and human.'
  effect = 'friend'
  ranking = 3
  type = 'generic'

  def run(self, itm):
    if itm != self.itm and human_t in itm.traits and sacred_t in itm.traits: 
      itm.effects.append(self.name)
      itm.resolve_mod += 2


class ShadowHunter(Skill):
  name = 'cazador de sombras'
  desc = '+2 damage, +2 str if enemy is death.'
  effect = 'self'
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
        roll = basics.roll_dice(2)
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
        roll = basics.roll_dice(1)
        if roll >= 5: 
          damage = randint(4, 10)
          itm.damage_done[-1] += damage
          target.hp_total -= damage
          target.update()
          target.deads[-1] += target.c_units - target.units
          logging.debug(f'hiere.')
        if roll >= 3: target.combat_retreat()


class SecondSun(Skill):
  name = 'second sun'
  desc = 'negates the night.'
  effects = 'self'
  ranking = 0
  type = 'generic'

  def run(self, itm):
    itm.effects += [self.name]
    if malignant_t in itm.traits:
      itm.effects += ['burden']
      itm.moves -= 2
      itm.dfs_mod -= 2
      itm.off_mod -= 2
      itm.str_mod -= 2
      itm.resolve -= 2
  def tile_run(self, itm):
    self.turns -= 1
    itm.events = [ev for ev in itm.events if ev.name != Eclipse.name]
    itm.day_night = 1 


class SwampSurvival(Skill):
  effect = 'selv'
  desc = '+3 stealth in swams.'
  name = 'sobreviviente del pantano'
  ranking = 3
  type = 'generic'

  def run(self, itm):
    itm.swamp_survival = 1
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
    if itm.pos and basics.roll_dice(2) >= 6 and itm.day_night[0]:
      if itm.pos.pop:
        deads = randint(2, 5) * itm.units
        if deads > itm.pos.pop: deads = itm.pos.pop
        itm.pos.pop -= deads
        if itm.pos.pop: itm.pos.unrest += deads * 100 / itm.pos.pop
        if itm.pos.nation.show_info : sleep(loadsound('spell33') * 0.5)
        msg = f'{itm} {deads} deads {in_t} {itm.pos} {itm.pos.cords}.'
        itm.nation.log[-1].append(msg)
      elif itm.pos.pop == 0 and basics.roll_dice(2) >= 10:
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
      if basics.roll_dice(1) >= 3:
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
  name = 'wailing winds'
  desc = '-1 resolve for all units. ignores (death, malignant.'
  effects = 'all'
  ranking = 0
  type = 'generic'

  def run(self, itm):
    itm.effects += [self.name]
    if any(i not in itm.traits for i in [death_t, malignant_t]):
      itm.resolve_mod -= 1


class WarCry(Skill):
  name = 'war cry'
  desc = '+1 resolve if unit is human .'
  effect = 'friend'
  ranking = 3
  type = 'generic'

  def run(self, itm):
    if itm.nation == self.nation and itm != self.itm and human_t in itm.traits: 
      itm.effects.append(self.name)
      itm.resolve_mod += 1


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
