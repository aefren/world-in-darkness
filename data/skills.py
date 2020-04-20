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
  effect = 'self' #all, friend, enemy, self.
  desc = str()
  cast = 6
  cost = 1
  name = 'skill'
  nation = None
  show = 1
  ranking = 0
  tags = []
  type = 0 #-1 before. 0 generic. 1 after combat round.
  def __init__(self, itm):
    self.itm = itm
    self.nation = self.itm.nation    
  def ai_run(self, itm):
    pass
  def run(self):
    pass


class Ambushment(Skill):
  effect = 'self'
  desc = '+1 att if unit is hidden.'
  name = 'Emboscada'
  type = 0
  def run(self, itm):
    if itm.pos and (itm.pos.hill or itm.pos.surf.name == forest_t):
      if itm.hidden:
        itm.effects += [self.name]
        itm.att_mod += 1


class BattleBrothers(Skill):
  effect = 'self'
  desc = 'agrega 1 de resolve por cada 10 unidades hasta 2'
  name = 'hermanos de batalla'
  type = 0
  def run(self, itm):
    if itm.units >= 30: 
      itm.effects.append(self.name+str( 2))
      itm.resolve_mod += 2
    elif itm.units >= 20:
      itm.effects.append(self.name+str( 1)) 
      itm.resolve_mod += 1



class CastBloodRain(Skill):
  cost = 20
  cast = 8
  name = 'blood rain'
  ranking = 10
  tags = []
  def run(self, itm):
    if itm.power < 1:
      if itm.show_info:
        sp.speak(f'{not_magic_t}.') 
        sleep(loadsound('errn1'))
      return
    if roll_dice(2) >= self.cast:
      sleep(loadsound('spell27', channel=ch5, vol=0.7)/2)
      itm.power -= self.cost
      dist = randint(3,6)
      pos = itm.pos
      sq = pos.get_near_tiles(itm.pos.scenary, dist)
      for s in sq:
        if self.name not in [ev.name for ev in s.events]:
          s.events += [BloodRaining(s)]
    else:
      if itm.show_info:
        sleep(loadsound('spell33', channel=ch5,)/2)


class BloodRaining(Skill):
  name = 'blood raining'
  desc = ''
  effects = 'all'
  turns = randint(3, 7)
  type = 0
  def run(self, itm):
    itm.effects += [self.name]
    if malignant_t in itm.tags:
      itm.resolve_mod += 1
      itm.moves_mod += 1
      itm.off_mod += 1
      itm.res_mod += 2
    else:
      itm.resolve_mod -= 1
      itm.dfs_mod -= 1
      itm.moves_mod -= 1
      itm.off_mod -= 1
      if mounted_t in itm.traits: 
        itm.moves_mod -= 1
        itm.resolve_mod -= 1
      if itm.rng+itm.rng_mod > 5:
        itm.off_mod -= 1
        itm.str_mod -= 1 
        itm.range_mod -= 5


class BloodyFeast(Skill):
  effect = 'self'
  desc = 'agrega mas 2 a la regeneración durante la noche.'
  name = 'festín nocturno'
  type = 0
  def run(self, itm):
    if itm.day_night[0]:
      itm.hp_res_mod += 2
      itm.ranking_skills += 5


class Burn(Skill):
  effect = 'self'
  desc = 'can destroy buildings'
  name = 'quemar'
  type = 0
  def run(self, itm):
    itm.can_burn = 1



class Carrion(Skill):
  effect = 'self'
  desc = '+1 res, +1 str if corpses on field.'
  name = 'carroña'
  type = 0
  def run(self, itm):
    if itm.pos and itm.pos.corpses:
      itm.effects += {self.name}
      itm.res_mod += 1
      itm.str_mod += 1


class Charge(Skill):
  effect = 'self'
  desc = 'charge damage = 2'
  name = 'carga'
  type = 0
  def run(self, itm):
    itm.damage_charge += 2


class DesertSurvival(Skill):
  effect = 'self'
  desc = 'ventajas sin definir.'
  name = 'sobreviviente del decierto'
  type = 0
  def run(self, itm):
    itm.desert_survival = 1
    if itm.pos and itm.pos.soil.name == waste_t: 
      itm.effects.append(self.name)
      itm.stealth_mod += 2


class ElusiveShadow(Skill):
  effect = 'self'
  desc = '+3 stealth on day, +6 stealth on night.'
  name = 'sombra elusiva'
  ranking = 5
  type = 0
  def run(self, itm):
    itm.effects.append(self.name) 
    if itm.day_night[0]: itm.stealth_mod += 6
    elif itm.day_night[0] == 0: itm.stealth_mod += 3


class Ethereal(Skill):
  effect = 'self'
  desc = 'unidades etéreas ignoran cualquier modificador de armor.'
  name = 'etéreo'
  ranking = 10
  type = 0
  def run(self, itm):
    itm.armor_ign_mod = 1
    itm.ranking_skills += 10



class Fanatism(Skill):
  effect = 'self'
  name = fanatism_t
  desc = '+1 att, +1 str, -2 dfs, +1 moves if enemy is undead.'
  type = 0
  def run(self, itm):
    if itm.target and undead_t in itm.target.traits:
      itm.effects.append(self.name)
      itm.att_mod += 2
      itm.dfs_mod -= 2
      itm.moves_mod += 1
      itm.str_mod += 2


class FearAura(Skill):
  effect = 'enemy'
  desc = '-2 resolve, -2 moves, -1 off, -1 dfs.'
  name = fearaura_t
  ranking = 5
  type = 0  
  def run(self, itm):
    if death_t not in itm.traits and itm != self.itm:
      itm.effects.append(fear_t)
      itm.resolve_mod -= 2
      itm.moves_mod -= 2
      itm.off_mod -= 1
      itm.dfs_mod -= 1


class Fly(Skill):
  effect = 'self'
  desc = 'unit can fly. enemy can not charge.'
  name = 'vuela'
  type = 0
  def run(self, itm):
    itm.can_fly = 1
    if itm.target: itm.target.can_charge = 0



class BattleFocus(Skill):
  effect = 'self'
  desc = '++1 hit if unit mp is full.'
  name = 'Trance de batalla'
  type = 0
  def run(self, itm):
    if itm.mp[0] == itm.mp[1]: itm.hit_rolls_mod += 1


class DarkPresence(Skill):
  name = 'dark presence'
  desc = 'if undead: in day: +2 res. '
  desc += 'if night: +1 dfs, +1 moves, +1 off, +2 res, +2 str.'
  effect = 'friend'
  type = 0
  def run(self, itm):
    if (itm.nation == self.nation
        and death_t in itm.traits and vampire_t not in itm.traits 
        and self.name not in itm.effects):
      if itm.day_night[0] == 0:
        itm.effects.append(self.name+str(f' ({day_t})'))
        itm.res_mod += 1
      if itm.day_night[0]:
        itm.effects.append(self.name+str(f' ({night_t})'))
        itm.dfs_mod += 1
        itm.moves_mod += 1
        itm.off_mod += 1
        itm.res_mod += 2
        itm.str_mod += 2


class ForestSurvival(Skill):
  effect = 'self'
  desc = '+2 stealth if unit is on forest.'
  name = 'sobreviviente del bosque'
  type = 0
  def run(self, itm):
    itm.forest_survival = 1 
    if itm.pos and itm.pos.surf.name == forest_t: 
      itm.effects.append(self.name)
      itm.can_hide = 1
      itm.stealth_mod += 2
      itm.ranking_skills += 5


class ForestTerrain(Skill):
  effect = 'all'
  desc = '-2 moves for grount unit, -4 move for mounted unit, -1 off, -1 dfs.unit can not charge, ignores forest survival and flying units. +2 stealth.'
  name = 'forest terrain'
  type = 0
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
  type = 0
  def run(self, itm):
    if itm.pos and itm.pos.surf.name == forest_t:
      itm.effects.append(self.name)
      itm.dfs_mod += 1
      itm.off_mod += 1
      itm.resolve_mod += 1 
      itm.ranking_skills += 5  



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
        deads *= itm.att+itm.att_mod
        deads *= itm.damage+itm.damage_mod
        if deads > itm.pos.pop: deads = itm.pos.pop
        itm.pos.pop -= deads
        if itm.pos.pop: itm.pos.unrest += deads*100/itm.pos.pop
        if itm.pos.nation.show_info : sleep(loadsound('spell33')*0.5)
        msg = f'{itm} {deads} deads {in_t} {itm.pos} {itm.pos.cords}.'
        itm.pos.nation.log[-1].append(msg)


class HeavyCharge(Skill):
  effect = 'self'
  desc = 'charge damage = 3'
  name = 'carga pesada'
  type = 0
  def run(self, itm):
    itm.damage_charge += 3
    itm.traits += [mounted_t]


class HillTerrain(Skill):
  effect = 'all'
  desc = '-2 moves for grount units, -4 move for mounted unit, unit can not charge, -1 dfs, -1 off. ignores forest survival and fying units. +5 range if unit is ranged. +2 stealth.'
  name = 'hill terrain'
  type = 0
  def run(self, itm):
    if itm.rng+itm.rng_mod >= 6: itm.rng_mod += 5
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
  type = 0
  def run(self, itm):
    if itm.mp[0] == itm.mp[1]: 
      itm.effects.append(self.name)
      itm.dfs_mod += 2

class ImpalingRoots(Skill):
  effect = 'self'
  desc = ''
  name = 'raíces empaladoras'
  type = -1
  ranking = 10
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
        off -= target.dfs+target.dfs_mod
        hit = get_hit_mod(off)
        logging.debug(f'hit {hit}.')
        if roll_dice(1) >= hit:
          st = 6
          st -= target.res+target.res_mod
          wound = get_wound_mod(st)
          logging.debug(f'wound {wound}.')          
          if roll_dice(1) >= wound:
            damage += 2
            if roll_dice(1) == 6:
              damage += 2
      #itm.damage_done[-1] += damage
      if damage:
        if damage > target.hp_total: damage = target.hp_total
        target.hp_total -= damage
        target.update()
        target.deads[-1] += target.c_units-target.units
        itm.battlelog += [f'{self.name} ({itm}) {kills_t} {target.deads[-1]}.']
        logging.debug(f'hiere on {damage}.')


class Inspiration(Skill):
  effect = 'friend'
  desc = '+1 moves, +1 resolve'
  name = 'inspiración'
  type = 0
  def run(self, itm):
    if itm.nation == self.nation and itm != self.itm:
      itm.effects.append(self.name)
      itm.moves_mod += 1
      itm.resolve_mod += 1


class Intoxicated(Skill):
  effect = 'self'
  desc = 'Las unidades sufren un número aleatoreo de daño por turno. durante x turnos.'
  name = 'Intoxicado'
  turns = randint(3, 8)
  type = 2
  def run(self, itm):
    if itm.hp_total >= 60: itm.hp_total -= randint(2, 10)
    elif itm.hp_total >= 40: itm.hp_total -= randint(0, 8)
    elif itm.hp_total >= 20: itm.hp_total -= randint(0, 4)
    elif itm.hp_total >= 1: itm.hp_total -= randint(0, 2)


class LongBow(Skill):
  effect = 'self'
  desc = '+1 pn, +5 range, +1 str.'
  name = 'Arco largo'
  type = 0
  def run(self, itm):
    itm.effects.append(self.name)
    itm.pn_mod += 1
    itm.rng_mod += 5
    itm.str_mod += 1


class LordOfBones(Skill):
  name = 'señor de los huesos'
  effect = 'friend'
  desc = '+1 att, +1 dfs, +1 off.'
  type = 0
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
  name = 'señor de sangre'
  type = 0
  def run(self, itm):
    if (itm.nation == self.nation and itm != self.itm 
        and itm.name in [ghouls_t]):
      itm.effects.append(self.name)
      itm.dfs_mod += 1
      itm.moves_mod += 1
      itm.off_mod += 1
      itm.resolve_mod += 1

class MastersEye(Skill):
  name = 'ojos del amo'
  effect = 'friend'
  desc = '+1 att, +1 hit roll, +1 str, +1 res.'
  ranking = 5
  type = 0
  def run(self, itm):
    if itm != self.itm and itm.nation == self.nation:
      itm.effects.append(self.name)
      itm.hit_rolls_mod += 1
      itm.res_mod += 1
      itm.str_mod += 1
      itm.moves_mod += 1



class Night(Skill):
  effect = 'all'
  desc = '-1 off, -1dfs, -5 range if unit range is more than 5. +2 stealth.'
  name = night_t
  type = 0
  def run(self, itm):
    if itm.day_night[0]:
      itm.effects.append(self.name)
      itm.stealth_mod += 2
      if itm.rng+itm.rng_mod > 5: itm.rng_mod -= 5
        


class NightFerocity(Skill):
  effect = 'self'
  desc = 'if night: +1 att, +1 moves.'
  name = 'ferocidad nocturna'
  type = 0
  def run(self, itm):
    if itm.day_night[0]:
      itm.effects.append(self.name) 
      itm.att_mod += 1
      itm.moves_mod += 1


class NightSurvival(Skill):
  effect = 'self'
  desc = '+1 power_restoration, +1 hp restoration.'
  name = 'sobreviviente nocturno'
  type = 0
  def run(self, itm):
    itm.night_survival = 1
    if itm.day_night[0]:
      itm.effects.append(self.name)
      if itm.power: itm.power_res_mod += 1
      itm.hp_res_mod += 1
      itm.ranking_skills += 5


class MassSpears(Skill):
  effect = 'self'
  desc = '+1  off por cada 20 unidades hasta 3.. Anula la carga enemiga de caballería.'
  name = 'lanzas en masa'
  type = 0
  def run(self, itm):
    if itm.units >= 30:
      itm.effects.append(self.name+str( 2)) 
      itm.off_mod += 2
      itm.ranking_skills += 10
    elif itm.units >= 20:
      itm.effects.append(self.name+str( 1)) 
      itm.off_mod += 1
      itm.ranking_skills += 5
    if itm.target: itm.target.can_charge = 0
    itm.anticav = 1


class MountainSurvival(Skill):
  effect = 'self'
  desc = 'invisible en las montañas., +2 stealth.'
  name = 'sobreviviente de las montañas'
  type = 0
  def run(self, itm):
    itm.mountain_survival = 1
    if itm.pos and itm.pos.hill:
      itm.effects.append(self.name)
      itm.can_hide = 1
      itm.stealth_mod += 2
      itm.ranking_skills += 5


class Organization(Skill):
  effect = 'friend'
  desc = '+1 off, +1 dfs, +1 resolve'
  name = 'organización'
  type = 0
  def run(self, itm):
    if (itm.nation == self.nation
        and human_t in itm.traits
        and all(i not in itm.traits for i in [commander_t, leader_t])):
      itm.effects.append(self.name)
      itm.dfs_mod += 1
      itm.off_mod += 1
      itm.resolve_mod += 1


class PikeSquare (Skill):
  effect = 'self'
  desc = 'agrega 1 ataque si la unidad tiene 20 o mas unidades. Anula la carga de cavallería enemiga.'
  name = 'formación de picas'
  type = 0
  def run(self, itm):
    if itm.units >= 20:
      itm.effects.append(self.name) 
      itm.att_mod += 1
    if itm.target: 
      itm.target.can_charge = 0
    itm.anticav = 1


class Raid(Skill):
  effect = 'self'
  desc = 'can raid tiles.'
  name = 'saquear'
  type = 0
  def run(self, itm):
    itm.can_raid = 1


class RaiseDead(Skill):
  cost = 20
  cast = 6
  name = raise_dead_t
  ranking = 10
  tags = [raise_dead_t]
  def ai_run(self, itm):
    self.run(itm)
  def run(self, itm):
    if itm.pos.corpses == [] or itm.power < 1:
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
    raised.hp_total = sum(dead.deads)*raised.hp
    raised.update()
    logging.debug(f'unidades totales de {dead} {sum(dead.deads)}.')
    logging.debug(f'{raised} unidades {raised.units}. hp {raised.hp}.')
    roll2 = roll_dice(2)
    needs = ceil(raised.ranking/12)
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
      if itm.nation.show_info: sleep(loadsound('raiseundead1')/2)
      itm.pos.update(itm.nation)
    else:
      msg = f'fallo.'
      logging.debug(msg)
      itm.log[-1].append(msg)
      if itm.show_info: 
        sp.speak(f'{self.name} falló.')


class Regroup(Skill):
  effect = 'self'
  desc = 'si la unidad vence reagrupa todos los miembros huídos.'
  name = 'reagruparse'
  type = 1
  def run(self, itm):
    if itm.target and itm.target.hp < 1:
      itm.hp_total += sum(itm.fled)*itm.hp
      msg = f'{itm.name} recupera {sum(itm.fled)} unidades huidas.' 
      itm.log[-1] += msg
      logging.debug(msg)


class ReadyAndWaiting(Skill):
  effect = 'self'
  desc = '+1 off +1 str if unit has his max mp'
  name = 'listos y esperando'
  type = 0
  def run(self, itm):
    if itm.mp[0] == itm.mp[1]:
      itm.effects += [self.name]
      itm.off_mod += 1
      itm.str_mod += 1


class Reinforce(Skill):
  effect = 'friend'
  desc = '+1 integrante por turno hasta el máximo inicial reclutado si no se gastó mp.'
  name = 'refuerzos'
  type = 0
  def run(self, itm):
    if itm != self.itm:
      itm.effects.append(self.name)
      itm.can_regroup = 1


class SermonOfCourage(Skill):
  effect = 'friend'
  desc = '+1 resolve a las unidades humanas.'
  name = 'sermón de coraje'
  type = 0
  def run(self, itm):
    if itm != self.itm and human_t in itm.traits: 
      itm.effects.append(self.name)
      itm.resolve_mod += 1


class ShadowHunter(Skill):
  effect = 'self'
  name = 'cazador de sombras'
  desc = '+2 damage, +2 str if enemy is undead.'
  type = 0
  def run(self, itm):
    if itm.target and dark_t in itm.target.traits:
      itm.effects.append(self.name)
      itm.damage_sacred_mod += 2
      itm.moves_mod += 1
      itm.str_mod += 2



class SkeletonLegion(Skill):
  effect = 'self'
  desc = 'agrega 1 al ataque por cada 10 unidades desde 20. limite 2.'
  name = 'legion de esqueletos'
  type = 0
  def run(self, itm):
    if itm.units >= 30:
      itm.effects.append(self.name+str( 2)) 
      itm.att_mod += 2
    elif itm.units >= 20:
      itm.effects.append(self.name+str( 1)) 
      itm.att_mod += 1


class Skirmisher(Skill):
  effect = 'self'
  desc = 'units gain half moves in distanse on combat.'
  name = 'retirada'
  type = 1
  def run(self, itm):
    if itm.target and itm.dist < itm.rng+itm.rng_mod: 
      dist = randint(1, itm.moves+itm.moves_mod)
      dist = ceil(dist/2)
      itm.dist += dist
      itm.target.dist += dist
      itm.battlelog += [f'{itm} go back {dist}.']


class Spread(Skill):
  effect = 'self'
  desc = 'resucita y une enemigos caidos a la unidad.'
  cast = 6
  name = 'Plaga zombie'
  ranking = 10
  type = 1
  def run(self, itm):
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
  desc = '+1 dfs, +1 off with each 10 units since 20. limit 3.'
  name = 'rodeados'
  type = 0
  def run(self, itm):
    if itm.units >= 40:
      itm.effects.append(self.name+str( 3))
      itm.off_mod += 3
      itm.str_mod += 3
      itm.ranking_skills += 10
    elif itm.units >= 30:
      itm.effects.append(self.name+str( 2))
      itm.off_mod += 2
      itm.str_mod += 2
      itm.ranking_skills += 10
    elif itm.units >= 20:
      itm.effects.append(self.name+str( 1))
      itm.off_mod += 1
      itm.str_mod += 1


class SwampTerrain(Skill):
  effect = 'all'
  desc = '-1 dfs, -1 off,-2 moves for grount unit, -4 move for mounted unit, unit can not charge. ignores swamp survival and flying units.'
  name = 'swamp terrain'
  type = 0
  def run(self, itm):
    if itm.swamp_survival == 0 and itm.can_fly == 0:
      itm.effects.append(self.name)
      itm.charge = 0
      itm.dfs_mod -= 1
      itm.moves_mod -= 2
      itm.off_mod -= 1
      if mounted_t in itm.traits: itm.moves_mod -= 2


class Scream(Skill):
  effect = 'selv'
  desc = 'if roll >= 4 enemy morale check fails..'
  name = 'grito ardiente'
  type = -1
  ranking = 10
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
          target.deads[-1] += target.c_units-target.units
          logging.debug(f'hiere.')
        if roll >= 3: target.combat_retreat()


class SwampSurvival(Skill):
  effect = 'selv'
  desc = 'invissible en pantanos.'
  name = 'sobreviviente del pantano'
  type = 0
  def run(self, itm):
    if itm.pos and itm.pos.name == swamp_t:
      itm.can_hide = 1
      itm.stealth_mod += 3
      itm.ranking_skills += 5


class TerrainEffects(Skill):
  effect = 'self'
  desc = ''
  name = 'terrain effects.'
  show = 0
  type = 0
  def run(self, itm):
    if itm.flying == 0 and itm.pos:
      if itm.pos.surf.name == forest_t:
        itm.skills.append(ForestTerrain)
      if itm.surf.name == swamp_t:
        itm.skills.append(SwampTerrain)


class TheBeast(Skill):
  name = 'la bestia'  
  effect = 'self'
  desc = 'if roll :� 5 unit attack in tile if there is any enemy.'
  turns = 0
  type = 2
  def run(self, itm):
    if itm.pos and roll_dice(2) >= 6 and itm.day_night[0]:
      if itm.pos.pop:
        deads = randint(2, 5)*itm.units
        if deads > itm.pos.pop: deads = itm.pos.pop
        itm.pos.pop -= deads
        if itm.pos.pop: itm.pos.unrest += deads*100/itm.pos.pop
        if itm.pos.nation.show_info : sleep(loadsound('spell33')*0.5)
        msg = f'{itm} {deads} deads {in_t} {itm.pos} {itm.pos.cords}.'
        itm.nation.log[-1].append(msg)
      elif itm.pos.pop == 0 and roll_dice(2) >= 10:
        if itm.nation.show_info: sleep(loadsound('spell36')*0.5)
        msg = f'{itm} es ahora {itm.align()}.'
        itm.nation.log[-1].append(msg)
        itm.set_default_align()


class ToxicClaws(Skill):
  effect = 'self'
  desc = 'units loses x damage per turn during x turns.'
  name = 'garras tóxicas.'
  ranking = 5 
  type = 1
  def run(self, itm):
    if itm.target and sum(itm.damage_done):
      logging.debug(f'{self.name} damage done {itm.damage_done}.')
      if roll_dice(1) >= 4:
        if Intoxicated.name not in [s.name for s in itm.target.other_skills]: 
          itm.target.other_skills.append(Intoxicated(itm))



class VigourMourtis(Skill):
  effect = 'friend'
  desc = '+1 hit roll si la unidad es undead'
  name = 'vigor mortis'
  type = 0
  def run(self, itm):
    if itm != self.itm and undead_t in itm.traits:
      itm.effects.append(self.name)
      itm.hit_rolls_mod += 1



