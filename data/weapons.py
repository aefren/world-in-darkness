from data.lang.es import *
from log_module import *
from sound import *
import basics
from data import skills
from random import randint


class Weapon:
    name = str()
    desc = ""
    hit_to = None
    hits = 1
    wounds = 1
    shield = 1
    armor = 1

    sacred_damage = 0
    min_dist = 0
    max_dist = 0
    pn = 0
    push = 0

    def __init__(self, itm):
        self.itm = itm
        self.modifier = []

    def __str__(self):
        return self.name

    def run(self):
        itm = self.itm
        itm.update()
        itm.combat_fight(self)

    def set_modifier(self):
        pass

    def push_backs(self):
        if self.push and basics.roll_dice(1) <= self.push:
            c_dist = self.itm.target.dist
            back = randint(2, 5)
            self.itm.target.dist += back
            msg = f"{self.itm} puch back to {self.itm.target} from {c_dist} to {self.itm.target.dist}"
            self.itm.target.temp_log += [msg]

    def pre_melee(self):
        pass

    def after_melee(self):
        if self.push: self.push_backs()

    def effects(self):
        itm = self.itm

    def update(self):
        self = self.__class__(self.itm)
        self.set_modifier()


class Club(Weapon):
    name = "club"
    desc = ""
    ranking = 1.2
    damage = 4
    critical = 6
    range_max = 1
    range_min = 1
    pn = 0


class Crush(Weapon):
    name = "crush"
    desc = ""
    ranking = 1.1
    damage = 5
    critical = 3
    range_max = 1
    range_min = 0
    pn = 0


class Beak(Weapon):
    name = "beak"
    desc = ""
    ranking = 1.1
    damage = 2
    critical = 3
    range_max = 0
    range_min = 0
    pn = 0


class Bite(Weapon):
    name = "bite"
    desc = ""
    ranking = 1.1
    damage = 2
    critical = 2
    range_max = 0
    range_min = 0
    pn = 0


class BlessedSword(Weapon):
    name = "blessed sword"
    desc = ""
    ranking = 1.2
    damage = 4
    critical = 3
    range_max = 1
    range_min = 1
    pn = 0

    def set_modifier(self):
        if deads_t in self.int.target.tags:
            self.damage += 4
            self.critical += 4
            self.modifier += [f"{damage_t} + 4, {critical_t} + 4."]


class BloodDrinker(Weapon):
    name = "Blood drinker"
    desc = ""
    ranking = 1.2
    damage = 4
    critical = 4
    range_max = 0
    range_min = 0
    pn = 0

    def set_modifier(self):
        if deads_t not in self.itm.target.tags: pass


class BoulderClub(Weapon):
    name = "boulder club"
    desc = ""
    ranking = 1.2
    damage = 3
    critical = 2
    range_max = 1
    range_min = 1
    pn = 0
    push = 3


class Bow(Weapon):
    name = "bow"
    desc = ""
    ranking = 1.2
    ammo = 20
    damage = 3
    critical = 2
    range_max = 20
    range_min = 6


class Branch(Weapon):
    name = "branch"
    desc = ""
    ranking = 1.1
    damage = 2
    critical = 3
    range_max = 5
    range_min = 0
    pn = 0


class BroadSword(Weapon):
    name = "broad sword"
    desc = ""
    ranking = 1.3
    damage = 5
    critical = 8
    range_max = 1
    range_min = 0
    pn = 0


class BronzeAxe(Weapon):
    name = "bronze axe"
    desc = ""
    ranking = 1.1
    damage = 3
    critical = 4
    range_max = 2
    range_min = 1
    pn = 1


class BronzeJavelins(Weapon):
    name = "bronze javelins"
    desc = ""
    ranking = 1.2
    ammo = 6
    damage = 3
    range_max = 6
    range_min = 2
    pn = 0

    def pre_melee(self):
        if (self.itm.dist in range(self.range_min, self.range_max + 1)
                and self.c_ammo):
            self.itm.combat_fight()


class BronzeSpear(Weapon):
    # Note. This weapon should always be place on weapon1.
    name = "Bronze spear"
    desc = ""
    ranking = 1.2
    damage = 5
    critical = 3
    range_max = 3
    range_min = 2
    pn = 0


class BronzeScimitar(Weapon):
    name = "Bronze Scimitar"
    desc = ""
    ranking = 1.2
    damage = 4
    critical = 5
    range_max = 1
    range_min = 0
    pn = 0


class Claw(Weapon):
    name = "claw"
    desc = ""
    ranking = 1.1
    damage = 2
    critical = 4
    range_max = 0
    range_min = 0
    pn = 0


class Scimitar(Weapon):
    name = "Scimitar"
    desc = ""
    ranking = 1.25
    damage = 4
    critical = 7
    range_max = 1
    range_min = 0
    pn = 0


class CrossBow(Weapon):
    name = "crossbow"
    desc = ""
    ranking = 1.2
    damage = 5
    critical = 5
    range_max = 15
    range_min = 6
    pn = 1

    def set_modifier(self):
        if self.itm.dist <= 10:
            self.damage += 1
            self.critical += 2
            self.modifier += [f"{damage_t} + 1, {self.critical} + 2"]


class Dagger(Weapon):
    name = "dagger"
    desc = ""
    ranking = 1.1
    damage = 3
    critical = 3
    range_max = 0
    range_min = 0
    pn = 1


class ElongatedFangs(Weapon):
    name = "fangs"
    desc = ""
    ranking = 1.2
    damage = 4
    critical = 4
    range_max = 1
    range_min = 0
    pn = 0


class Fangs(Weapon):
    name = "fangs"
    desc = ""
    ranking = 1.1
    damage = 3
    critical = 3
    range_max = 0
    range_min = 0
    pn = 0


class Falchion(Weapon):
    name = "Falchion"
    desc = ""
    ranking = 1.3
    damage = 4
    critical = 4
    range_max = 1
    range_min = 0
    pn = 1


class Fist(Weapon):
    name = "fist"
    desc = ""
    ranking = 1
    damage = 1
    critical = 2
    range_max = 0
    range_min = 0
    pn = 0


class Flail(Weapon):
    name = "flail"
    desc = ""
    ranking = 1.2
    damage = 2
    critical = 4
    range_max = 1
    range_min = 1
    pn = 0


class FleshEater(Weapon):
    name = "Flesh eater"
    desc = ""
    ranking = 1.2
    damage = 4
    critical = 4
    range_max = 0
    range_min = 0
    pn = 1


class GreatClub(Weapon):
    name = "great club"
    desc = ""
    ranking = 1.3
    damage = 6
    critical = 14
    range_max = 2
    range_min = 1
    pn = 0


class GreatSword(Weapon):
    name = "great sword"
    desc = ""
    ranking = 1.3
    damage = 5
    critical = 5
    range_max = 1
    range_min = 1
    pn = 0


class Halberd(Weapon):
    # Note. This weapon should always be place on weapon1.
    name = "halberd"
    desc = ""
    ranking = 1.2
    damage = 5
    critical = 5
    range_max = 3
    range_min = 1
    pn = 1

    def set_modifier(self):
        if self.itm.dist < 2:
            self.damage -= 1
            self.critical -= 2
            self.modifier += [f"{damage_t} - 1 {critical_t} - 2"]


class HeavyHoof(Weapon):
    name = "heavy hoof"
    desc = ""
    ranking = 1.2
    damage = 4
    critical = 8
    range_max = 1
    range_min = 0
    pn = 0


class Hoof(Weapon):
    name = "hoof"
    desc = ""
    ranking = 1.1
    damage = 2
    critical = 4
    range_max = 1
    range_min = 0
    pn = 0


class ImmenseClaws(Weapon):
    name = "immense claws"
    desc = ""
    ranking = 1.3
    damage = 3
    critical = 4
    range_max = 0
    range_min = 0
    pn = 1


class Lance(Weapon):
    name = "lance"
    desc = ""
    ranking = 1.3
    damage = 4
    critical = 8
    range_max = 4
    range_min = 3
    pn = 2
    push = 3


class LightLance(Weapon):
    name = "light lance"
    desc = ""
    ranking = 1.2
    damage = 4
    critical = 5
    range_max = 2
    range_min = 1
    pn = 1
    push = 2


class LongBow(Weapon):
    name = "long bow"
    desc = ""
    ranking = 1.2
    ammo = 20
    damage = 3
    critical = 2
    range_max = 40
    range_min = 6

    def set_modifier(self):
        if self.itm.dist >= 30:
            self.damage -= 1
            self.critical -= 1
            self.modifier += [f"{damage_t} - 1, {critical_t} - 1"]
        elif self.itm.dist <= 10:
            self.damage += 1
            self.critical += 1
            self.modifier += [f"{damage_t} + 1, {critical_t} + 1"]


class LongPoisonBow(Weapon):
    name = "long bow"
    desc = ""
    ranking = 1.2
    ammo = 20
    damage = 2
    critical = 1
    range_max = 15
    range_min = 0
    pn = 0

    def set_modifier(self):
        if self.itm.dist >= 30:
            self.damage -= 1
            self.critical -= 1
            self.modifier += [f"{damage_t} - 1, {critical_t} - 1"]
        elif self.itm.dist <= 10:
            self.damage += 1
            self.critical += 1
            self.modifier += [f"{damage_t} + 1, {critical_t} + 1"]


class LongSpear(Weapon):
    # Note. This weapon should always be place on weapon1.
    name = "long spear"
    desc = ""
    ranking = 1.4
    damage = 7
    critical = 8
    range_max = 4
    range_min = 3
    pn = 2
    push = 3


class MantisClaw(Weapon):
    name = "mantis claw"
    desc = ""
    ranking = 1.1
    damage = 3
    critical = 5
    range_max = 1
    range_min = 0
    pn = 0


class PosesedBlade(Weapon):
    name = "posesed blade"
    desc = ""
    wounds = 0
    ranking = 1.1
    damage = 7
    critical = 15
    range_max = 1
    range_min = 0
    pn = 0


class Pitchfork(Weapon):
    name = "Pitchfork"
    desc = ""
    ranking = 1
    damage = 2
    critical = 1
    range_max = 1
    range_min = 0
    pn = 0


class Pugio(Weapon):
    name = "pugio"
    desc = ""
    ranking = 1.1
    damage = 3
    critical = 2
    range_max = 0
    range_min = 0
    pn = 1


class RustSword(Weapon):
    name = "rust sword"
    desc = ""
    ranking = 1.1
    damage = 3
    critical = 3
    range_max = 1
    range_min = 1
    pn = 0


class ScreenOfSorrow(Weapon):
    name = "screen of sorrow"
    desc = ""
    wounds = 0
    hit_to = "head"
    ranking = 1.2
    damage = 4
    critical = 6
    range_max = 20
    range_min = 0

    def effects(self):
        if (basics.roll_dice(1)
                >= self.itm.target.resolve + self.itm.target.resolve_mod):
            c_dist = self.itm.target.dist
            back = randint(2, 5)
            self.itm.target.dist += back
            msg = f"{self.itm} puch back to {self.itm.target} from {c_dist} to {self.itm.target.dist}"
            self.itm.target.temp_log += [msg]


class Skythe(Weapon):
    name = "skythe"
    desc = ""
    ranking = 1.2
    damage = 4
    critical = 5
    range_max = 0
    range_min = 0


class ShortBow(Weapon):
    name = "short bow"
    desc = ""
    ranking = 1.3
    ammo = 30
    damage = 2
    critical = 2
    range_max = 12
    range_min = 4
    pn = 0


class ShortPoisonBow(Weapon):
    name = "long bow"
    desc = ""
    ranking = 1.2
    ammo = 20
    damage = 2
    critical = 2
    range_max = 15
    range_min = 0
    pn = 0


class ShortSword(Weapon):
    name = "short sword"
    desc = ""
    ranking = 1.2
    damage = 3
    critical = 2
    range_max = 1
    range_min = 0
    pn = 0


class Sling(Weapon):
    name = "ling"
    desc = ""
    ranking = 1.1
    damage = 1
    critical = 2
    range_max = 10
    range_min = 5
    pn = 0


class SoulDrain(Weapon):
    name = "soul scourge"
    desc = ""
    ranking = 1.3
    damage = 5
    critical = 10
    range_max = 1
    range_min = 0


class Spear(Weapon):
    # Note. This weapon should always be place on weapon1.
    name = "spear"
    desc = ""
    ranking = 1.3
    damage = 5
    critical = 7
    range_max = 3
    range_min = 2
    pn = 1
    push = 3


class StoneSpear(Weapon):
    name = "Bronze spear"
    desc = ""
    ranking = 1.3
    damage = 3
    critical = 3
    range_max = 3
    range_min = 2
    pn = 0


class Sword(Weapon):
    name = "sword"
    desc = ""
    ranking = 1.2
    damage = 3
    critical = 6
    range_max = 1
    range_min = 1
    pn = 0


class Staff(Weapon):
    name = "staff"
    desc = ""
    ranking = 1
    damage = 1
    critical = 3
    range_max = 1
    range_min = 0
    pn = 0


class Talon(Weapon):
    name = "talon"
    desc = ""
    ranking = 1.1
    damage = 4
    critical = 4
    range_max = 0
    range_min = 0
    pn = 1


class TigerFangs(Weapon):
    name = "tiger fangs"
    desc = ""
    ranking = 1.2
    damage = 4
    critical = 5
    range_max = 0
    range_min = 0
    pn = 1


class ToxicClaw(Weapon):
    name = "toxic claw"
    desc = ""
    ranking = 1.15
    damage = 2
    critical = 3
    damage_need = 50
    range_max = 0
    range_min = 0
    pn = 0

    def effects(self):
        itm = self.itm
        if (sum(itm.damage_done) >= self.damage_need * itm.target.hp_total / 100
            and itm.target.hp_total >= 1
            and death_t not in itm.target.physical_traits
                and poisonres_t not in itm.target.physical_traits):
            logging.debug(f"{self.name} damage done {itm.damage_done}.")
            if basics.roll_dice(1) >= 4:
                sk = skills.Intoxicated(itm.target)
                sk.turns = sum(itm.damage_done)
                if skills.Intoxicated.name not in [s.name for s in self.itm.target.other_skills]:
                    itm.target.other_skills += [sk]
                    msg = [f"{itm.target} {is_t} intoxicated by {itm}. {sk.turns}"]
                    itm.target.log[-1] += [msg]
                    itm.temp_log += [msg]


class ToxicDagger(Weapon):
    name = "dagger"
    desc = ""
    ranking = 1.1
    damage = 3
    critical = 3
    damage_need = 10
    range_max = 0
    range_min = 0
    pn = 1

    def effects(self):
        itm = self.itm
        if (sum(itm.damage_done) >= self.damage_need * itm.target.hp_total / 100
            and itm.target.hp_total >= 1
            and death_t not in itm.target.physical_traits
                and poisonres_t not in itm.target.physical_traits):
            logging.debug(f"{self.name} damage done {itm.damage_done}.")
            if basics.roll_dice(1) >= 4:
                sk = skills.Intoxicated(itm.target)
                sk.turns = sum(itm.damage_done)
                if skills.Intoxicated.name not in [s.name for s in self.itm.target.other_skills]:
                    itm.target.other_skills += [sk]
                    msg = [f"{itm.target} {is_t} intoxicated by {itm}. {sk.turns}"]
                    itm.target.log[-1] += [msg]
                    itm.temp_log += [msg]


class ToxicFangs(Weapon):
    name = "toxic fangs"
    desc = ""
    ranking = 1.15
    damage = 3
    critical = 3
    damage_need = 30
    range_max = 0
    range_min = 0
    pn = 0

    def effects(self):
        itm = self.itm
        if (sum(itm.damage_done) >= self.damage_need * itm.target.hp_total / 100
            and itm.target.hp_total >= 1
            and death_t not in itm.target.physical_traits
                and poisonres_t not in itm.target.physical_traits):
            logging.debug(f"{self.name} damage done {itm.damage_done}.")
            if basics.roll_dice(1) >= 4:
                sk = skills.Intoxicated(itm.target)
                sk.turns = sum(itm.damage_done)
                if skills.Intoxicated.name not in [s.name for s in self.itm.target.other_skills]:
                    itm.target.other_skills += [sk]
                    msg = [f"{itm.target} {is_t} intoxicated by {itm}. {sk.turns}"]
                    itm.target.log[-1] += [msg]
                    itm.temp_log += [msg]


class Trident(Weapon):
    name = "trident"
    desc = ""
    ranking = 1.2
    damage = 4
    critical = 6
    range_max = 1
    range_min = 0
    pn = 0


class Tusk(Weapon):
    name = "tusk"
    desc = ""
    ranking = 1.2
    damage = 4
    critical = 6
    range_max = 1
    range_min = 0
    pn = 0


class VampireBite(Weapon):
    name = "vampire bite"
    desc = ""
    ranking = 1.2
    damage = 5
    critical = 11
    range_max = 0
    range_min = 0
    pn = 0


class ZombieBite(Weapon):
    name = "Zombie bite"
    desc = ""
    ranking = 1.1
    damage = 2
    critical = 4
    range_max = 0
    range_min = 0
    pn = 0


"""
Created on 3 nov. 2020

@author: Alfred
"""
