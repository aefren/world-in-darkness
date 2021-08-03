# -*- coding: utf-8 -*-
from math import ceil, floor
from pdb import Pdb
from random import randint, shuffle, choice, uniform
from time import sleep, process_time

#from numpy import mean

from language import *
from log_module import *
from sound import *
import basics


class Skill:
    name = "skill"
    desc = str()
    effect = "self"  # all, friend, enemy, self.
    sound = None
    vol = 0.5
    cast = 6
    cost = 1
    food = 1
    res = 1
    income = 1
    unrest = 1
    index = 0
    nation = None
    passive_ranking = 1
    ranking = 1
    show = 1
    tags = []
    # types: "generic", "before combat", "after combat", "before attack",
    # "after attack", "start turn".
    type = 0
    turns = -1

    def __init__(self, itm):
        self.itm = itm
        self.nation = self.itm.nation

    def __str__(self):
        return self.name

    def run_after_combat(self, itm):
        pass

    def run(self, itm):
        pass

    def tile_run(self, itm):
        pass


class Ambushment(Skill):
    name = "Emboscada"
    desc = "+2 dfs, +2 moves if unit is hidden and unit is in forest, swamp or hill."
    effect = "self"
    ranking = 1.2
    type = "generic"

    def run(self, itm):
        if (itm.pos and (itm.pos.hill or itm.pos.surf.name == forest_t
                         or itm.pos.surf.name == swamp_t) and itm.hidden):
            itm.effects += [self.name]
            itm.ln_mod *= 2
            itm.dfs_mod += 2
            itm.moves_mod += 2


class BattleBrothers(Skill):
    name = "hermanos de batalla"
    desc = "+1 resolve if 20 units. +2 resolve if 30 units."
    effect = "self"
    ranking = 1.1
    type = "generic"

    def run(self, itm):
        if itm.units >= 30:
            itm.effects.append(self.name + str(2))
            itm.ranking *= self.ranking
            itm.resolve_mod += 2
        elif itm.units >= 20:
            itm.effects.append(self.name + str(1))
            itm.ranking *= self.ranking
            itm.resolve_mod += 1


class BattleFocus(Skill):
    name = "Trance de batalla"
    desc = "++1 hit if unit mp is full."
    effect = "self"
    ranking = 1.1
    type = "generic"

    def run(self, itm):
        if itm.mp[0] == itm.mp[1]:
            self.effects += [self.name]
            itm.ranking *= self.ranking
            itm.hit_rolls_mod += 1


class BlessedWeapons(Skill):
    name = "armas bendecidas"
    desc = "+2 strn if target is malignant or hell."
    effect = "self"
    ranking = 1.2
    type = "generic"

    def run(self, itm):
        if (itm.target and itm.target.aligment == malignant_t
                or itm.target == hell_t):
            itm.strn_mod += 2


class BloodLord(Skill):
    name = "señor de sangre"
    desc = "+1 dfs, +1 off, +1 moves, +1 resolve if unit is blood drinker."
    effect = "leading"
    ranking = 1.2
    type = "generic"
    tags = ["leader"]

    def run(self, itm):
        if (itm.nation in self.itm.belongs and itm != self.itm
                and blood_drinker_t in itm.physical_traits):
            itm.effects += [self.name]
            itm.dfs_mod += 1
            itm.ln_mod += 2
            itm.moves_mod += 1
            itm.resolve_mod += 1
            itm.off_mod += 1


class BloodRaining(Skill):
    name = "blood raining"
    desc = ""
    effects = "all"
    ranking = 10
    type = "generic"

    def run(self, itm):
        itm.effects += [self.name]
        if itm.aligment in [malignant_t, hell_t]:
            itm.resolve_mod += 1
            itm.moves_mod += 1
            itm.res_mod += 2
            itm.strn += 2
        else:
            itm.resolve_mod -= 1
            itm.dfs_mod -= 1
            itm.moves_mod -= 1
            itm.off_mod -= 1
            if itm.mounted:
                itm.moves_mod -= 1
                itm.resolve_mod -= 1
            if itm.range[1] > 5:
                itm.off_mod -= 1
                itm.strn_mod -= 1
                itm.range_mod -= 5

    def tile_run(self, itm):
        self.turn -= 1


class BloodyBeast(Skill):
    name = "bestia sangrienta"
    desc = "randomly kill population if tile has population."
    effect = "self"
    turns = 0
    type = "start turn"

    def run(self, itm):
        if itm.pos and itm.pos.pop:
            if basics.roll_dice(2) >= 10:
                deads = randint(1, itm.units)
                deads *= itm.att1 + itm.att1_mod
                deads *= itm.strn + itm.strn_mod
                if deads > itm.pos.pop: deads = itm.pos.pop
                itm.pos.pop -= deads
                if itm.pos.pop: itm.pos.unrest += deads * 100 / itm.pos.pop
                corpses = choice(itm.pos.nation.population_type)
                corpses.deads = [deads]
                corpses.units = 0
                corpses.hp_total = 0
                itm.pos.units += [corpses]
                if itm.pos.nation.show_info: sleep(loadsound("spell33") * 0.5)
                msg = f"{itm} {deads} deads {in_t} {itm.pos} {itm.pos.cords}."
                itm.pos.nation.log[-1].append(msg)


class BloodyFeast(Skill):
    name = "fest�n nocturno"
    desc = "+2 hp restoration in night."
    effect = "self"
    ranking = 1.1
    type = "generic"

    def run(self, itm):
        if itm.pos and itm.pos.day_night:
            itm.hp_res_mod += 5


class Burn(Skill):
    name = "quemar"
    desc = "can destroy buildings"
    effect = "self"
    type = "generic"

    def run(self, itm):
        itm.can_burn = 1


class ColdResist(Skill):
    name = blizzard_wanderer_t
    desc = "ignores storm penalties."
    effect = "self"
    ranking = 1.1
    type = "generic"

    def run(self, itm):
        itm.coldres = 1
        if itm.pos and itm.pos.raining:
            itm.effects.append(self.name)
        if itm.pos and itm.pos.storm:
            itm.can_hide = 1
            itm.stealth_mod += 2


class ChaliceOfBlood(Skill):
    name = "ChaliceOfBlood"
    desc = "After attack round restores 1 hp if the unit has make damage on the enemy."
    effect = "self"
    passive_ranking = 1.2
    ranking = 1.2
    type = "after attack"

    def run(self, itm):
        if (itm.hp_total < itm.hp
                and itm.damage_done[-1] > itm.hp * 0.3):
            itm.hp_total += 2
            msg = f"{self.name}: {itm} restores 2 hp."
            itm.temp_log += [msg]


class Champion(Skill):
    name = "champion"
    desc = "+1 resolve."
    effect = "friend"
    ranking = 1.2
    type = "generic"
    tags = ["leader"]

    def run(self, itm):
        if self.itm == itm: return
        if itm.nation not in self.itm.belongs: return
        itm.effects.append(self.name)
        itm.resolve_mod += 1


class Charge(Skill):
    name = "carga"
    desc = "charge damage = 1"
    effect = "self"
    ranking = 1.3
    type = "generic"

    def run(self, itm):
        itm.can_charge = 1


class Coesion(Skill):
    name = "coesion"
    desc = "+2 ln."
    effect = "leading"
    ranking = 1.2
    type = "generic"
    tags = ["leader"]

    def run(self, itm):
        if itm.nation in self.itm.belongs and human_t in itm.physical_traits:
            itm.effects.append(self.name)
            itm.ln_mod += 2


class DarkPresence(Skill):
    name = "dark presence"
    desc = """
    if death: in day: +2 res.
    if night: +1 dfs, +1 moves, +1 off, +2 res, +2 str.
    """
    effect = "friend"
    ranking = 1.1
    type = "generic"
    tags = ["leader"]

    def run(self, itm):
        if (itm.nation in self.itm.belongs
                and malignant_t in itm.physical_traits and self.name not in itm.effects):
            if itm.pos and itm.pos.day_night == 0:
                itm.effects.append(self.name + str(f" ({day_t})"))
                itm.res_mod += 1
            if itm.pos and itm.pos.day_night:
                itm.effects.append(self.name + str(f" ({night_t})"))
                itm.dfs_mod += 1
                itm.moves_mod += 1
                itm.off_mod += 1
                itm.res_mod += 2
                itm.strn_mod += 2


class DarkVision(Skill):
    name = "dark vision"
    desc = "units won get night vision effects."
    effect = "self"
    ranking = 1.1
    type = "generic"

    def run(self, itm):
        if itm.pos and itm.pos.day_night:
            itm.effects.append(self.name)
            itm.dark_vision = 1


class DeepestDarkness(Skill):
    name = "deepest darkness"
    desc = "night on tile."
    effect = "all"
    type = "generic"

    def run(self, itm):
        if itm.pos and itm.pos.day_night:
            itm.effects.append(self.name)
            itm.stealth_mod += 2
            if itm.dark_vision == 0:
                itm.dfs_mod -= 1
                itm.off_mod -= 1
                if itm.range[1] > 5: itm.off_mod -= 1

    def tile_run(self, itm):
        itm.day_night = 1
        print(f"done deepest")


class DesertSurvival(Skill):
    name = "sobreviviente del decierto"
    desc = "ventajas sin definir."
    effect = "self"
    passive_ranking = 1.1
    type = "generic"

    def run(self, itm):
        itm.desert_survival = 1
        if itm.pos and itm.pos.soil.name == waste_t:
            itm.effects.append(self.name)
            itm.stealth_mod += 2


class DHLevels(Skill):
    name = "demon hunter level 2"
    desc = ""
    effect = "self"
    index = 1
    type = "generic"

    def run_after_combat(self, itm):
        if (itm.target.hp_total < 1
                and itm.target.aligment in [malignant_t, hell_t]):
            itm.demon_souls += sum(itm.target.deads) // itm.squads
            print(f"deads {sum(itm.target.deads)}.")
        if itm.demon_souls >= 20:
            itm.name = "demon unters level 2"
            itm.level = 2

    def run(self, itm):
        if itm.level == 2:
            itm.off_mod += 1
            itm.strn_mod += 1


class Diseased(Skill):
    name = "diseased"
    desc = "probability to dead."
    effect = "self"
    ranking = 1
    type = "start turn"

    def run(self, itm):
        itm.effects += [self.name]
        if basics.roll_dice(2) >= 12:
            itm.hp_total = 0
            if itm.show_info:
                sleep(loadsound("notify36"))
            msg = f"{itm} has dead by disease."
            self.nation.log[-1] += [msg]
            if itm.nation in itm.pos.world.random_nations: logging.debug(msg)


class Eclipse(Skill):
    name = "eclipse"
    desc = "if unit is not dark vision: -1 off, -1dfs, -5 range if unit range is more than 5. +2. stealth."
    effect = "all"
    type = "generic"

    def run(self, itm):
        itm.effects.append(self.name)
        if itm.dark_vision == 0 and itm.pos and itm.pos.day_night == 0:
            itm.dfs_mod -= 1
            itm.off_mod -= 1
            if itm.range[1] > 5: itm.off_mod -= 1

    def tile_run(self, itm):
        self.turns -= 1
        itm.events = [ev for ev in itm.events if ev.name != SecondSun.name]
        itm.day_night = 0


class Fanatism(Skill):
    name = fanatism_t
    desc = """
    +5 ln, +2 resolve if enemy is death.
    """
    effect = "self"
    type = "generic"

    def run(self, itm):
        if itm.target and death_t in itm.target.physical_traits:
            itm.effects += [self.name]
            itm.ln_mod += 5
            itm.resolve_mod += 2


class FearAura(Skill):
    name = fearaura_t
    desc = "if target is not mindless. -2 resolve, -2 moves, -1 off, -1 dfs."
    effect = "enemy"
    ranking = 1.3
    type = "generic"
    tags = ["fear aura"]

    def run(self, itm):
        if mindless_t in itm.physical_traits: return
        if itm == self.itm: return
        if itm.nation in self.itm.belongs: return
        itm.effects.append(fear_t)
        itm.dfs_mod -= 2
        itm.ln_mod -= 2
        itm.moves_mod -= 2
        itm.off_mod -= 2
        itm.resolve_mod -= 2


class FeedingFrenzy(Skill):
    name = "feeding frenzy"
    desc = "+1 moves, +1 resolve, +1 res, +2 strn."
    effect = "self"
    ranking = 1.1
    type = "generic"

    def run(self, itm):
        itm.can_join_mod -= 1
        itm.moves_mod += 1
        itm.res_mod += 1
        itm.resolve_mod += 1
        itm.strn_mod += 2


class Fly(Skill):
    name = fly_t
    desc = "unit can fly. enemy can not charge."
    effect = "self"
    ranking = 1.1
    type = "generic"

    def run(self, itm):
        itm.can_fly = 1
        if itm.target: itm.target.can_charge = 0


class Furtive(Skill):
    name = "furtive"
    desc = "+5 stealth."
    effect = "self"
    ranking = 1.1
    type = "generic"

    def run(self, itm):
        itm.effects.append(self.name)
        itm.stealth_mod += 5


class ForestSurvival(Skill):
    name = "forest survival"
    desc = "+4 stealth if unit is on forest."
    effect = "self"
    ranking = 1.1
    type = "generic"

    def run(self, itm):
        itm.forest_survival = 1
        if itm.pos and itm.pos.surf.name == forest_t:
            itm.effects.append(self.name)
            itm.stealth_mod += 4


class ForestTerrain(Skill):
    name = "forest terrain"
    effect = "all"
    desc = """
    -2 moves for grount unit, -4 move for mounted unit, -1 off,
    -1 dfs. unit can not charge.
    -30% ln.
    ignores forest survival and flying units.+4 stealth.
    """
    type = "generic"

    def run(self, itm):
        itm.stealth_mod += 4
        if itm.forest_survival == 0 and itm.can_fly == 0:
            itm.effects.append(self.name)
            itm.charges = 0
            itm.ln_mod -= itm.ln // 3
            itm.moves_mod -= 2
            if itm.mounted: itm.moves_mod -= 2
            itm.dfs_mod -= 1
            itm.off_mod -= 1


class ForestWalker(Skill):
    name = "forest walker"
    desc = "+1 resolve, +1 off, +1 dfs, +1 moves if unit is into forest."
    effect = "self"
    ranking = 1.1
    type = "generic"

    def run(self, itm):
        if itm.pos and itm.pos.surf.name == forest_t:
            itm.effects.append(self.name)
            itm.dfs_mod += 1
            itm.moves_mod += 1
            itm.off_mod += 1
            itm.resolve_mod += 1


class ElusiveShadow(Skill):
    name = "elusive shadow"
    desc = "+8 stealth on day, +10 stealth on night."
    effect = "self"
    type = "generic"

    def run(self, itm):
        itm.effects.append(self.name)
        if itm.pos and itm.pos.day_night: itm.stealth_mod += 10
        elif itm.pos and itm.pos.day_night == 0: itm.stealth_mod += 8


class Ethereal(Skill):
    name = "ethereal"
    desc = "Ignores enemy pn."
    effect = "self"
    ranking = 1.2
    type = "generic"

    def run(self, itm):
        itm.armor_ign_mod = 1
        itm.dfs_mod += 10


class HeavyCharge(Skill):
    name = "heavy charge"
    desc = "charge damage = 3"
    effect = "self"
    ranking = 1.3
    type = "generic"

    def run(self, itm):
        itm.can_charge = 1


class Storm(Skill):
    name = "storm"
    desc = "if unit is ranged -4 rng, -1 off."
    effects = "self"
    sound = ["storm1", "storm2"]
    vol = 0.05
    ranking = 1
    type = "generic"

    def run(self, itm):
        if itm.can_fly and itm.coldres == 0:
            itm.effects += [self.name]
            itm.moves_mod -= 3
        if itm.range[1] >= 5 and itm.coldres == 0:
            itm.effects += [self.name]
            itm.off_mod -= 2

    def tile_run(self, itm):
        itm.raining = 1
        itm.storm = 1
        itm.flood += 2
        roll = basics.roll_dice(1)
        if roll >= 5: itm.flood += 1
        if roll >= 6: itm.flood += 1
        self.turns -= 1
        if itm.soil.name == waste_t: self.turns -= 1
        if roll >= 5:
            itm.events += [mist(itm)]
        for ev in itm.events:
            if "miasma" in ev.tags: ev.turns -= 1


class HillTerrain(Skill):
    name = "hill terrain"
    desc = """
    -2 moves for grount units, -4 move for mounted unit.
    -30% ln.
    unit can not charge, -1 dfs, -1 off.
    ignores mountain survival and fying units. +5 range if unit is ranged.
    +4 stealth.
    """
    effect = "all"
    type = "generic"

    def run(self, itm):
        if itm.range[1] >= 6: itm.off_mod += 1
        itm.stealth_mod += 4
        if itm.mountain_survival == 0 and itm.can_fly == 0:
            itm.effects.append(self.name)
            itm.charges = 0
            itm.ln_mod -= itm.ln // 3
            itm.moves_mod -= 2
            itm.dfs_mod -= 1
            itm.off_mod -= 1
            if itm.mounted: itm.moves_mod -= 2


class HoldPositions(Skill):
    name = "hold positions"
    desc = "+2 dfs if unit mp is full."
    effect = "leading"
    ranking = 1.2
    type = "generic"

    def run(self, itm):
        if itm.mp[0] == itm.mp[1]:
            itm.effects.append(self.name)
            itm.dfs_mod += 2


class HolyAura(Skill):
    name = "holy aura"
    desc = """-2 moves, -2 dfs, -2 off if enemy is death and malignant.
  """
    effect = "enemy"
    ranking = 1.2
    type = "generic"
    tags = ["holy aura"]

    def run(self, itm):
        if itm.target.aligment in [malignant_t, hell_t]:
            itm.effects += [f"{self.name}"]
            itm.moves_mod -= 2
            itm.off_mod -= 2
            itm.dfs_mod -= 2


class Exaltation(Skill):
    name = "exaltation"
    desc = "undefined."
    effect = "friend"
    ranking = 1
    type = "generic"

    def run(self, itm):
        if sacred_t in itm.physical_traits:
            itm.effects += [self.name]
            itm.resolve_mod += 1
            itm.hit_rolls_mod += 1


class Helophobia(Skill):
    name = "helophobia"
    desc = "-2 att, -2 damage, -2 dfs, -2 moves, -2 off, -2 res, -2 str if night."
    effect = "self"
    ranking = 1
    type = "generic"

    def run(self, itm):
        if itm.pos and itm.pos.day_night == 0:
            itm.effects += [self.name]
            if itm.att1 + itm.att1_mod > 2: itm.att1_mod -= 2
            itm.dfs_mod -= 2
            itm.moves_mod -= 2
            itm.off_mod -= 2
            itm.res_mod -= 2
            itm.strn_mod -= 2


class ImpalingRoots(Skill):
    effect = "self"
    desc = ""
    name = "impaling roots."
    # ranking = 1.3
    type = "before attack"

    def run(self, itm):
        if (itm.target
                and itm.target.dist <= 10 and itm.target.dist > 1):
            target = itm.target
            logging.debug(f"{self.name}.")
            logging.debug(f"{itm.dist=:}, {target.dist=:}.")
            damage = 0
            for r in range(5):
                if damage > target.hp_total: break
                off = 6
                off -= target.dfs + target.dfs_mod
                hit = basics.get_hit_mod(off)
                logging.debug(f"hit {hit}.")
                if basics.roll_dice(1) >= hit:
                    st = 6
                    st -= target.res + target.res_mod
                    wound = basics.get_wound_mod(st)
                    logging.debug(f"wound {wound}.")
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
                itm.temp_log += [
                    f"{self.name} ({itm}) {kills_t} {target.deads[-1]}."]
                logging.debug(f"hiere on {damage}.")


class Intoxicated(Skill):
    name = intoxicated_t
    desc = "Las unidades sufren un n�mero aleatoreo de da�o por turno. durante x turnos."
    effect = "self"
    sound = ["diseased1"]
    turns = 3
    type = "start turn"

    def run(self, itm):
        if itm.hp_total < 1: return
        sk = Weak(itm)
        sk.turns = randint(2, 4)
        if sk.name not in [s.name for s in itm.other_skills]:
            itm.other_skills += [sk]
        if basics.roll_dice(1) >= 5:
            deads = randint(10, 20)
            if basics.roll_dice(1) >= 5: deads *= 2
            if basics.roll_dice(1) >= 6: deads *= 2
            if deads > 100: deads = 100
            deads = deads*itm.hp_total/100
            msg = f"{itm} loses {floor(deads/itm.hp_total)} by {self.name} in {itm.pos}. ({itm.pos.cords})"
            itm.log[-1] += [msg]
            itm.nation.log[-1] += [msg]
            itm.hp_total -= deads
            itm.update()
            if itm.show_info: sleep(loadsound("spell34", channel=CHTE3) / 2)


class Inspiration(Skill):
    name = "inspiration"
    desc = "+1 hit roll, +4 resolve."
    effect = "friend"
    ranking = 1.2
    type = "generic"
    tags = ["leader"]

    def run(self, itm):
        if self.itm == itm: return
        if itm.nation not in self.itm.belongs: return
        itm.effects.append(self.name)
        itm.hit_rolls_mod += 1
        itm.resolve_mod += 4


class LeadershipExceeded(Skill):
    name = "leadership exceeded"
    desc = ""
    effect = "leading"
    ranking = 1
    type = "generic"
    tags = ["leader"]

    def run(self, itm):
        if itm.leader is None: return
        if itm.leader.extra_leading >= 1:
            itm.effects += [f"{self.name} {itm.leader.extra_leading}%."]
            factor = itm.leader.extra_leading
            if factor >= 60:
                itm.moves_mod -= 3
                itm.resolve_mod -= 3
            elif factor >= 40:
                itm.moves_mod -= 2
                itm.resolve_mod -= 2
            elif factor >= 20:
                itm.moves_mod -= 1
                itm.resolve_mod -= 1


class LocustSwarm(Skill):
    name = "locust swarm"
    desc = ""
    effect = "self"
    food = 1
    type = "generic"
    turns = 5
    tags = ["plague"]

    def run(self, itm):
        pass

    def tile_run(self, itm):
        self.turns -= 1
        if itm.raining and itm.ambient.sseason in [
            spring_t, summer_t]: self.turns += randint(1, 2)
        elif itm.ambient.sseason == winter_t: self.turns -= 1
        if basics.roll_dice(2) >= 10: self.food -= 0.1
        needs = 11
        if itm.ambient.sseason in [spring_t, summer_t]: needs -= 2
        if basics.roll_dice(2) >= needs:
            tiles = itm.get_near_tiles(1)
            tiles = [t for t in tiles if t.soil.name not in [ocean_t]
                     and t != itm]
            shuffle(tiles)
            if self.name not in [ev.name for ev in tiles[0].events]:
                event = LocustSwarm(tiles[0])
                tiles[0].events += [event]
            elif self.name in [ev.name for ev in tiles[0].events]:
                for ev in tiles[0].events:
                    if ev.name == self.name: ev.turns += randint(1, 3)


class LordOfBones(Skill):
    name = "lord of bones"
    desc = """
    if unit is skeleton or skeleton warrior: +2 ln, +1 off, +1 strn.
    """
    effect = "leading"
    ranking = 1.2
    type = "generic"
    tags = ["leader"]

    def run(self, itm):
        if (itm.nation in self.itm.belongs and itm != self.itm
                and itm.name in [skeleton_t, "blood skeleton"]):
            itm.effects.append(self.name)
            itm.ln_mod += 2
            itm.off_mod += 1
            itm.strn_mod += 1


class MassSpears(Skill):
    effect = "self"
    desc = "+1  off por cada 20 unidades hasta 3.. Anula la carga enemiga de caballer�a."
    name = "lanzas en masa"
    ranking = 1.1
    type = "generic"

    def run(self, itm):
        if itm.squads >= 3:
            itm.effects.append(self.name + str(2))
            itm.off_mod += 2
        elif itm.squads >= 2:
            itm.effects.append(self.name + str(1))
            itm.off_mod += 1
        if itm.target: itm.target.can_charge = 0


class MastersEye(Skill):
    name = "ojos del amo"
    desc = "+1 att, +1 hit roll, +4 ln, +1 str, +1 res."
    effect = "friend"
    ranking = 1.3
    type = "generic"
    tags = ["leader"]

    def run(self, itm):
        if itm == self.itm: return
        if itm.nation not in self.itm.belongs: return
        itm.effects.append(self.name)
        itm.hit_rolls_mod += 1
        if death_t in itm.physical_traits:
            itm.effects += [f" {death_t}."]
            itm.ln_mod += 4
            itm.moves_mod += 1
            itm.res_mod += 1
            itm.strn_mod += 1
        if itm.aligment == malignant_t:
            itm.effects += [f" {malignant_t}"]
            itm.ln_mod += 4
            itm.resolve_mod += 1


class MasterOfBones(Skill):
    name = "master of bones"
    desc = """
    if unit is skeleton or skeleton warrior: +2 ln, +1 off, +1 strn.
    """
    effect = "leading"
    ranking = 1.2
    type = "generic"
    tags = ["leader"]

    def run(self, itm):
        if (itm.nation in self.itm.belongs and itm != self.itm
                and itm.name in [skeleton_t, "blood skeleton"]):
            itm.effects.append(self.name)
            itm.ln_mod += 2
            itm.off_mod += 1
            itm.strn_mod += 1


class Miasma(Skill):
    name = "miasma"
    desc = ""
    effects = "self"
    sound = ["miasma1"]
    ranking = 1
    type = "start turn"
    turns = -1
    tags = ["miasma"]

    def run(self, itm):
        itm.effects += [self.name]
        roll = basics.roll_dice(1)
        if roll >= 3:
            if self.name not in [ev.name for ev in itm.pos.events]:
                sk = Miasma(itm.pos)
                sk.turns = randint(3, 7)
                itm.pos.events += [sk]
                msg = f"miasma in {itm.pos} {itm.pos.cords}."
                if itm.pos.nation: itm.pos.nation.log[-1] += [msg]
                itm.log[-1] += [msg]
                itm.pos.world.log[-1] += [msg]
                logging.debug(msg)
                if itm.pos.nation and itm.pos.nation.show_info:
                    sleep(loadsound("notify25", channel=CHTE2) * 0.3)

    def tile_run(self, itm):
        self.turns -= 1
        if itm.ambient.sseason == winter_t: self.turns -= 1
        if itm.pop and basics.roll_dice(2) >= 10:
            pop_death = randint(5, 10)
            deads = pop_death * itm.pop // 100
            msg = f"miasma: {deads_t} {deads} in {itm} {itm.cords}."
            if itm.city: msg += f" ({itm.city})"
            logging.debug(msg)
            itm.nation.log[-1] += [msg]
            corpse = choice(
                [cr for cr in itm.nation.population_type if cr.poisonres == 0])
            itm.add_corpses(corpse, deads)
            itm.pop -= deads
            if itm.nation.show_info: sleep(
                loadsound("notify23", channel=CHTE2) // 1.5)

        units = [
            it for it in itm.units if it.poisonres == 0 and death_t not in it.physical_traits and Intoxicated.name not in [
                s.name for s in it.skills] and it.hp_total >= 1]
        roll = basics.roll_dice(1)
        if roll >= 6 and units:
            unit = choice(units)
            turns = randint(1, 2)
            roll = basics.roll_dice(1)
            if roll >= 6: turns += 5
            elif roll >= 5: turns += 3
            sk = Intoxicated(unit)
            sk.turns = turns
            if Intoxicated.name not in [s.name for s in unit.skills]:
                unit.other_skills += [sk]
                if unit.nation.show_info: sleep(loadsound("notify28"))
                try:
                    msg = f"{unit} at {unit.pos} {unit.pos.cords} has been intoxicated."
                except Exception: Pdb().set_trace()
                unit.log[-1] += [msg]
                unit.nation.log[-1] += [msg]
                unit.pos.world.log[-1] += [msg]


class mist(Skill):
    name = "mist"
    desc = "-1 rng if ranged unit, +3 stealth."
    effect = "all"
    type = "generic"

    def run(self, itm):
        itm.effects += [self.name]
        itm.stealth_mod += 3
        if itm.range[1] > 5: itm.off_mod -= 1


class Night(Skill):
    name = night_t
    desc = """if unit is not dark vision: -2 off,
  -2 dfs, -1 resolve. +2 stealth,
  -4 ln."""
    effect = "all"
    type = "generic"

    def run(self, itm):
        if itm.pos and itm.pos.day_night:
            itm.effects.append(self.name)
            itm.stealth_mod += 2
            if itm.dark_vision == 0:
                itm.dfs_mod -= 2
                itm.ln_mod -= 4
                itm.off_mod -= 2
                itm.resolve_mod -= 1


class NightFerocity(Skill):
    name = "ferocidad nocturna"
    desc = "if night: +2 strn1, +1 moves."
    effect = "self"
    type = "generic"

    def run(self, itm):
        if itm.pos and itm.pos.day_night:
            itm.effects.append(self.name)
            itm.strn_mod += 2
            itm.moves_mod += 1


class NightSurvival(Skill):
    name = "sobreviviente nocturno"
    desc = "+5 power_restoration, +2 hp restoration."
    effect = "self"
    type = "generic"

    def run(self, itm):
        itm.night_survival = 1
        if itm.pos and itm.pos.day_night:
            itm.effects.append(self.name)
            if itm.power: itm.power_res_mod += 5
            itm.hp_res_mod += 2


class MountainSurvival(Skill):
    effect = "self"
    desc = "invisible en las monta�as., +2 stealth."
    name = "sobreviviente de las monta�as"
    ranking = 1.1
    type = "generic"

    def run(self, itm):
        itm.mountain_survival = 1
        if itm.pos and itm.pos.hill:
            itm.effects.append(self.name)
            itm.can_hide = 1
            itm.stealth_mod += 2


class Organization(Skill):
    name = "organization"
    desc = "+1 off, +1 dfs."
    effect = "leading"
    ranking = 1.2
    type = "generic"
    tags = ["leader"]

    def run(self, itm):
        if itm.nation in self.itm.belongs and human_t in itm.physical_traits:
            itm.effects.append(self.name)
            itm.dfs_mod += 1
            itm.off_mod += 1


class Pestilence(Skill):
    name = "pestilence"
    desc = ""
    effects = "self"
    sound = ["miasma1"]
    ranking = 1
    type = "start turn"
    turns = -1
    tags = ["miasma"]

    def run(self, itm):
        itm.effects += [self.name]
        roll = basics.roll_dice(1)
        if roll >= 3:
            if Miasma.name not in [ev.name for ev in itm.pos.events]:
                sk = Miasma(itm.pos)
                sk.turns = randint(2, 5)
                itm.pos.events += [sk]
                msg = f"miasma in {itm.pos} {itm.pos.cords}."
                if itm.pos.nation: itm.pos.nation.log[-1] += [msg]
                itm.log[-1] += [msg]
                itm.pos.world.log[-1] += [msg]
                logging.debug(msg)
                if itm.pos.nation and itm.pos.nation.show_info:
                    sleep(loadsound("notify25", channel=CHTE2) * 0.1)

    def tile_run(self, itm):
        self.turns -= 1
        if itm.ambient.sseason == winter_t: self.turns -= 1
        if itm.pop and basics.roll_dice(2) >= 10:
            pop_death = randint(5, 10)
            deads = pop_death * itm.pop // 100
            msg = f"miasma: {deads_t} {deads} in {itm} {itm.cords}."
            if itm.city: msg += f" ({itm.city})"
            logging.debug(msg)
            itm.nation.log[-1] += [msg]
            corpse = choice(
                [cr for cr in itm.nation.population_type if cr.poisonres == 0])
            itm.add_corpses(corpse, deads)
            # corpse.deads = [pop_death * itm.pop // 100]
            # corpse.units=0
            # corpse.hp_total = 0
            # itm.units += [corpse]
            itm.pop -= deads
            if itm.nation.show_info: sleep(
                loadsound("notify23", channel=CHTE2) // 1.5)
        units = [u for u in itm.units if u.poisonres == 0
                 and death_t not in u.physical_traits and Intoxicated.name not in [s.name for s in u.skills]]
        roll = basics.roll_dice(1)
        if roll >= 6 and units:
            unit = choice(units)
            turns = randint(1, 3)
            roll = basics.roll_dice(1)
            if roll >= 6: turns += 5
            elif roll >= 5: turns += 3
            sk = Intoxicated(unit)
            sk.turns = turns
            if Intoxicated.name not in [s.name for s in unit.skills]:
                unit.other_skills += [sk]
                if unit.nation.show_info: sleep(loadsound("notify28"))
                msg = f"{unit} at {unit.pos} {unit.pos.cords} has been intoxicated."
                unit.log[-1] += [msg]
                unit.nation.log[-1] += [msg]
                unit.pos.world.log[-1] += [msg]


class PikeSquare (Skill):
    effect = "self"
    desc = "+1 att1 if 2 squadss, +2 att1 if 3 squads. Enemy can not charge."
    name = "formaci�n de picas"
    ranking = 1.1
    type = "generic"

    def run(self, itm):
        if itm.target is None: return
        if itm.dist not in range(itm.weapon1.range_min, itm.weapon1.range_max + 1): return
        if itm.squads >= 2:
            itm.effects.append(self.name + str(1))
            itm.att1_mod += 1
        elif itm.squads >= 3:
            itm.effects.append(self.name + str(2))
            itm.att1_mod += 2
        if itm.target:
            itm.target.can_charge = 0


class PyreOfCorpses(Skill):
    name = "pyre of corpses"
    desc = "burn corpses at position."
    effect = "self"
    type = "start turn"

    def run(self, itm):
        for cr in itm.pos.corpses:
            cleaning = itm.hp_total // 2
            if cr.deads:
                cr.deads[0] -= cleaning // cr.hp
                cr.deads[0] = int(cr.deads[0])


class Raid(Skill):
    effect = "self"
    desc = "can raid tiles."
    name = "saquear"
    type = "generic"

    def run(self, itm):
        itm.can_raid = 1


class Rain(Skill):
    name = "raining"
    desc = ""
    effects = "self"
    sound = ["rain1"]
    type = "generic"

    def run(self, itm):
        if itm.can_fly:
            itm.effects += [self.name]
            itm.moves_mod -= 2
        if itm.range[1] > 5:
            itm.effects += [self.name]
            itm.off_mod -= 1

    def tile_run(self, itm):
        self.turns -= 1
        itm.raining = 1
        itm.flood += 1
        roll = basics.roll_dice(1)
        if roll >= 6: itm.flood += 1
        if itm.soil.name == waste_t: self.turns -= 2
        for ev in itm.events:
            if "miasma" in ev.tags: ev.turns -= 1


class Regroup(Skill):
    name = "reagruparse"
    desc = "if a combat ends with a victory, all retreats are recovered."
    effect = "leading"
    type = "after combat"

    def run_after_combat(self, itm):
        if itm.target and itm.target.hp_total < 1:
            itm.hp_total += sum(itm.fled) * itm.hp
            msg = f"{itm.name} recupera {sum(itm.fled)} unidades huidas."
            itm.log[-1] += [msg]
            logging.debug(msg)


class ReadyAndWaiting(Skill):
    effect = "self"
    desc = "+1 off +1 str if unit has his max mp"
    name = "listos y esperando"
    ranking = 1.1
    type = "generic"

    def run(self, itm):
        if itm.mp[0] == itm.mp[1]:
            itm.effects += [self.name]
            itm.off_mod += 1
            itm.strn_mod += 1


class Refit(Skill):
    name = "refuerzos"
    desc = "+4 sts if at friendly position and units less than maximum units."
    effect = "self"
    type = "generic"

    def run(self, itm):
        if itm.pos and itm.pos.nation == itm.nation:
            itm.effects.append(self.name)
            itm.sts_mod += 4


class SermonOfCourage(Skill):
    name = "serm�n de coraje"
    desc = "+2 resolve if unit is sacred and human."
    effect = "leading"
    ranking = 1.1
    type = "generic"
    tags = ["leader"]

    def run(self, itm):
        if itm != self.itm and human_t in itm.physical_traits and sacred_t in itm.aligment:
            itm.effects.append(self.name)
            itm.resolve_mod += 2


class ShadowHunter(Skill):
    name = "cazador de sombras"
    desc = "+2 sacred damage."
    effect = "self"
    ranking = 1.2
    type = "generic"

    def run(self, itm):
        itm.effects.append(self.name)
        itm.damage_sacred_mod += 2


class SkeletonLegion(Skill):
    name = "legion de esqueletos"
    desc = "+1 att if 2 squads, +2 if 3 squads."
    effect = "self"
    ranking = 1.1
    type = 0

    def run(self, itm):
        if itm.squads >= 3:
            itm.effects.append(self.name + str(2))
            itm.att1_mod += 2
        elif itm.units >= 2:
            itm.effects.append(self.name + str(1))
            itm.att1_mod += 1


class Skirmisher(Skill):
    name = "skirmisher"
    desc = "units backs up a maximum half of self moves in distanse on combat."
    effect = "self"
    passive_ranking = 1.2
    type = "before attack"

    def run(self, itm):
        if itm.target and itm.dist < itm.range[1]:
            if itm.target.hp_total < 1: return
            if itm.moves + itm.moves_mod < 1: return
            if basics.roll_dice(1) >= 4:
                moves = itm.moves + itm.moves_mod
                moves = ceil(moves / 2)
                dist = randint(1, moves)
                itm.dist += dist
                itm.target.dist += dist
                msg = f"{self}: {itm} go back {dist}."
                itm.temp_log += [msg]


class Spread(Skill):
    effect = "self"
    desc = "resucita y une enemigos caidos a la unidad."
    cast = 4
    name = "Plaga zombie"
    passive_ranking = 1.2
    type = "after attack"

    def run(self, itm):
        if death_t not in itm.target.physical_traits:
            deads = sum(itm.target.deads)
            raised = 0
            for i in range(deads):
                roll = basics.roll_dice(2)
                if roll >= self.cast:
                    itm.hp_total += itm.hp
                    itm.raised[-1] += 1
                    raised += 1
                    itm.target.deads[-1] -= 1
                    if itm.target.deads[-1] < 0: itm.target.deads[-1] = 0
            if raised:
                msg = f"reanima {itm.raised[-1]}."
                logging.debug(msg)
                itm.temp_log += [msg]


class Surrounded(Skill):
    effect = "self"
    desc = """
    +10 ln if 3 squads.
    +20 ln if 6 squads.
    +30 ln if 10 squads.
    """
    name = "rodeados"
    type = "generic"

    def run(self, itm):
        if itm.squads >= 10:
            itm.effects.append(self.name + str(3))
            itm.ln_mod += 10
        elif itm.squads >= 7:
            itm.effects.append(self.name + str(2))
            itm.ln_mod += 10
        elif itm.squads >= 3:
            itm.effects.append(self.name + str(1))
            itm.ln_mod += 10


class Scavenger(Skill):
    name = "carro�a"
    desc = "+1 moves, +1 res, +1 str if corpses on field."
    effect = "self"
    ranking = 1.1
    type = "generic"

    def run(self, itm):
        if itm.pos and itm.pos.corpses:
            itm.effects += {self.name}
            itm.moves_mod += 1
            itm.res_mod += 1
            itm.strn_mod += 1


class Scream(Skill):
    name = "grito ardiente"
    effect = "selv"
    desc = "if roll >= 3 enemy morale check fails.."
    passive_ranking = 1.4
    type = "before attack"

    def run(self, itm):
        if itm.target:
            target = itm.target
            logging.debug(f"grito ardiente.")
            if death_t not in target.physical_traits:
                roll = basics.roll_dice(1)
                if roll >= 5:
                    damage = randint(4, 10)
                    itm.damage_done[-1] += damage
                    target.hp_total -= damage
                    target.update()
                    target.deads[-1] += target.c_units - target.units
                    logging.debug(f"hiere.")
                if roll >= 3: target.combat_retreat()


class SecondSun(Skill):
    name = "second sun"
    desc = "negates the night."
    effects = "self"
    ranking = 1
    type = "generic"

    def run(self, itm):
        if itm.pos and itm.pos.day_night == 0: itm.effects += [self.name]
        if (itm.aligment in [malignant_t, hell_t] and itm.pos
                and itm.pos.day_night == 0):
            itm.effects += [burned_t]
            itm.moves -= 2
            itm.dfs_mod -= 2
            itm.off_mod -= 2
            itm.strn_mod -= 2
            itm.resolve -= 2

    def tile_run(self, itm):
        self.turns -= 1
        itm.events = [ev for ev in itm.events if ev.name != Eclipse.name]
        itm.day_night = 1
        if any(i not in [Rain.name, Storm.name]
               for i in [ev.name for ev in itm.events]):
            for uni in itm.units:
                roll = basics.roll_dice(2)
                if uni.aligment in [malignant_t, hell_t]:
                    uni.hp_total -= roll
                    msg = f"{self.name} {kills_t} {roll//uni.hp}."
                    uni.log[-1] += [msg]
                    if uni.nation:
                        sleep(loadsound("notify25", channel=CHTE2) * 0.5)


class SwampSurvival(Skill):
    effect = "selv"
    desc3 = "+4 stealth in swams."
    name = "sobreviviente del pantano"
    ranking = 1.1
    type = "generic"

    def run(self, itm):
        itm.swamp_survival = 1
        if itm.pos and itm.pos.surf.name == swamp_t:
            itm.effects += [self.name]
            itm.stealth_mod += 4


class SwampTerrain(Skill):
    effect = "all"
    desc = """
    -1 dfs, -1 off,-2 moves for grount unit, -4 move for mounted unit.
    -30% ln.
    unit can not charge. ignores swamp survival and flying units.
    """
    name = "swamp terrain"
    type = "generic"

    def run(self, itm):
        if itm.swamp_survival == 0 and itm.can_fly == 0:
            itm.effects.append(self.name)
            itm.charges = 0
            itm.ln_mod -= itm.ln // 3
            itm.dfs_mod -= 1
            itm.moves_mod -= 2
            itm.off_mod -= 1
            if itm.mounted: itm.moves_mod -= 2


class TerrainEffects(Skill):
    effect = "self"
    desc = ""
    name = "terrain effects."
    show = 0
    type = "generic"

    def run(self, itm):
        if itm.flying == 0 and itm.pos:
            if itm.pos.surf.name == forest_t:
                itm.skills.append(ForestTerrain)
            if itm.surf.name == swamp_t:
                itm.skills.append(SwampTerrain)


class TheBeast(Skill):
    name = "la bestia"
    desc = "Randomly kills population in position."
    effect = "self"
    turns = 0
    type = "start turn"

    def run(self, itm):
        if itm.pos and basics.roll_dice(2) >= 10 and itm.pos.day_night:
            if itm.pos.pop:
                deads = randint(6, 25) * itm.units
                if deads > itm.pos.pop: deads = itm.pos.pop
                itm.pos.pop -= deads
                if deads > 0: itm.pos.add_corpses(
                    choice(itm.pos.nation.population_type), deads)
                if itm.pos.pop: itm.pos.unrest += deads * 100 / itm.pos.pop
                if itm.pos.nation.show_info: sleep(loadsound("spell33") * 0.5)
                msg = f"{itm} {deads} deads {in_t} {itm.pos} {itm.pos.cords}."
                itm.nation.log[-1].append(msg)
            elif itm.pos.pop == 0 and basics.roll_dice(2) >= 10:
                if itm.nation.show_info: sleep(loadsound("spell36") * 0.5)
                msg = f"{itm} es ahora {itm.align()}."
                itm.nation.log[-1].append(msg)
                itm.set_default_align()


class RainOfToads(Skill):
    name = "lluvia de sapos"
    desc = "adds unrest and chance to creates miasma by toads corpses. Batallion can get Weak"
    effects = "self"
    ranking = 1
    type = "generic"

    def run(self, itm):
        pass

    def tile_run(self, itm):
        self.turns -= 1
        itm.unrest += randint(5, 10)
        units = [uni for uni in itm.units if death_t not in uni.physical_traits]
        for uni in units:
            roll = basics.roll_dice(1)
            if roll >= 6:
                sk = Weak(uni)
                sk.turns = randint(4, 8)
                uni.other_skills += [sk]


class ToxicArrows(Skill):
    name = "toxic arrows"
    desc = "poisons target."
    effect = "self"
    passive_ranking = 1.2
    type = "after attack"

    def run(self, itm):
        if (itm.target and sum(itm.damage_done)
                and all(i not in [death_t, spirit_t] for i in itm.target.physical_traits)
                and itm.target.poisonres == 0
                and itm.ethereal == 0):
            logging.debug(f"{self.name} damage done {itm.damage_done}.")
            if basics.roll_dice(1) >= 5:
                sk = Intoxicated(itm.target)
                sk.turns = randint(2, 5)
                if Intoxicated.name not in [s.name for s in itm.target.skills]:
                    itm.target.other_skills += [sk]
                    msg = [f"{itm.target} {is_t} intoxicated by {itm}. {sk.turns}"]
                    itm.target.log[-1] += [msg]
                    itm.temp_log += [msg]


class ToxicClaws(Skill):
    name = "ToxicClawicas."
    desc = "units loses x damage per turn during x turns."
    effect = "self"
    passive_ranking = 1.2
    type = "after attack"

    def run(self, itm):
        if (itm.target and sum(itm.damage_done) and itm.target.hp_total >= 1
                and death_t not in itm.target.physical_traits
                and itm.poisonres == 0
                and itm.ethereal == 0):
            logging.debug(f"{self.name} damage done {itm.damage_done}.")
            if basics.roll_dice(1) >= 3:
                sk = Intoxicated(itm.target)
                sk.turns = randint(2,5)
                if Intoxicated.name not in [s.name for s in itm.target.skills]:
                    itm.target.other_skills += [sk]
                    msg = [f"{itm.target} {is_t} intoxicated by {itm}. {sk.turns}"]
                    itm.target.log[-1] += [msg]
                    itm.temp_log += [msg]


class TundraTerrain(Skill):
    name = "tundra terrain"
    effect = "all"
    desc = "-1 moves for non coldresist units."
    type = "generic"

    def run(self, itm):
        if itm.coldres == 0:
            itm.effects.append(self.name)
            itm.moves_mod -= 1


class VigourMourtis(Skill):
    name = "vigor mortis"
    desc = "+1 hit roll si la unidad es death"
    effect = "friend"
    ranking = 1.2
    type = "generic"

    def run(self, itm):
        if itm != self.itm and death_t in itm.physical_traits:
            itm.effects.append(self.name)
            itm.hit_rolls_mod += 1


class Undisciplined(Skill):
    name = "undisciplined"
    desc = """if unit is not leaded.
  at start of each turn one of those options can occur:
  loss a random unit number.
  generate unrest in tile if unit is in a city tile."""
    effect = "self"
    ranking = 1
    type = "start turn"

    def run(self, itm):
        if itm.leader: return
        roll = basics.roll_dice(1)
        if roll <= 5:
            if itm.pos and itm.pos.nation: itm.pos.unrest += randint(1, 2)
        else: itm.hp_total -= itm.hp * randint(1, 3)


class WailingWinds(Skill):
    name = "wailing winds"
    desc = "-1 resolve for all units. ignores (death, malignant."
    effects = "all"
    sound = ["wailing winds1", "wailing winds2"]
    vol = 0.1
    ranking = 1
    type = "generic"

    def run(self, itm):
        itm.effects += [self.name]
        if any(i not in itm.physical_traits for i in [death_t]): itm.resolve_mod -= 1


class WarCry(Skill):
    name = "war cry"
    desc = "+1 resolve if unit is human ."
    effect = "leading"
    ranking = 1.1
    type = "generic"

    def run(self, itm):
        if itm.nation in self.itm.belongs and itm != self.itm and human_t in itm.physical_traits:
            itm.effects.append(self.name)
            itm.resolve_mod += 1


class Weak(Skill):
    name = weak_t
    desc = "-2 off, -2 dfs, -2 moves, -2 res, -2 str."
    effect = "self"
    ranking = 0.5
    type = "generic"

    def run(self, itm):
        itm.effects += [self.name]
        itm.dfs_mod -= 2
        itm.moves_mod -= 2
        itm.off_mod -= 2
        itm.res_mod -= 2
        itm.strn_mod -= 2


class Withdrawall(Skill):
    name = "withdrawall"
    desc = "unit will withdraw from combat if a dise roll is 6 and enemy is at 3 or less distanse.."
    effect = "self"
    passive_ranking = 1.2
    type = "after attack"

    def run(self, itm):
        if itm.target and itm.hp_total >= 1:
            if itm.target.ranking < self.ranking * 1.5: return
            if itm.dist > itm.target.range[1]: return
            base = itm.moves - itm.moves_mod
            base -= itm.target.moves + itm.target.moves_mod
            if basics.roll_dice(2) + base >= 9:
                itm.retreats = 1
                itm.mp[0] -= 1
                msg = f"{self} {itm} have fled."
                itm.temp_log += [msg]
