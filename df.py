# -*- coding: utf-8 -*-
#!/usr/bin/env python
from glob import glob
from math import ceil, floor
from pdb import Pdb
from random import choice, randint, uniform, shuffle
from time import sleep, time
import gc
import pickle
import sys

from pygame.time import get_ticks as ticks
import natsort
import pygame

from language import *
#import numpy as np


dev_mode = 0
if dev_mode == 0:
    exec("import basics")
    exec("import log_module")
    exec("from data.skills import *")
    from screen_reader import *
    exec("from sound import *")
if dev_mode:
    import basics
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
        self.time = [0, [morning_t, noon_t, afternoon_t,
                         evening_t, night_t, midnight_t, dawn_t]]
        self.week = 1
        self.year = 1
        self.update()

    def update(self):
        self.sseason = f"{self.season[1][self.season[0]]}"
        self.stime = f"{self.time[1][self.time[0]]}"
        self.smonth = f" {self.month[1][self.month[0]]}"
        self.syear = f"{year_t} {self.year}"
        self.sday_night = f"{self.day_night[1][self.day_night[0]]}"


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
    grouth = 0
    resource = 1
    temp = 0
    daytemp = [0, 0, 0, 0]
    nighttemp = [0, 0, 0, 0]
    sight = 0
    type = "tile"
    unrest = 0
    world = None
    food_rate = None

    def __init__(self):
        if self.surf.__class__ == EmptySurf: self.surf.name == none_t
        self.buildings = []
        self.corpses = []
        self.effects = []
        self.events = []
        self.food_rate = None
        self.items = []
        self.log = []
        self.skills = []
        self.skill_names = []
        self.terrain_events = []
        self.units = []
        self.units_blocked = []
        if self.soil: self.update()

    def __str__(self):
        name = ""
        if self.name: name += f" {self.name}."
        if self.hill: name += f" {hill_t},"
        if self.surf.name != none_t:
            name += f" {self.surf.name}, {self.soil.name}"
        elif self.surf.name == none_t:
            name += f" {self.soil.name}."
        return name

    def add_corpses(self, corpse, number):
        corpse.deads = [number]
        corpse.units = 0
        corpse.hp_total = 0
        self.units += [corpse]

    def add_ghouls(self):
        roll = basics.roll_dice(2)
        if self.units: roll -= 1
        if roll >= 10:
            unit = self.add_unit(Ghoul, hell_t)
            unit.hp_total = unit.hp * randint(5, 10)
            unit.update()

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

    def add_unit(self, unit, nation, revealed=0, squads=None, units=None):
        global sayland
        done = 0
        for nt in world.nations + world.random_nations:
            if nt.name == nation:
                unit = unit(nt)
                done = 1
        if done == 0: Pdb().set_trace()
        unit.log += [[f"{turn_t} {world.turn}."]]
        unit.pos = self
        self.units.append(unit)
        unit.update()
        unit.set_hidden(unit.pos)
        unit.revealed = revealed
        unit.show_info = unit.nation.show_info
        if squads: unit.set_squads(squads)
        if units: unit.units = units
        unit.set_tile_attr()
        unit.nation.update(unit.pos.scenary)
        sayland = 1
        return unit

    def get_around_tiles(self, nation, info=0):
        sp.speak(f"around tiles.", 1)
        forest = [forest_t, 0]
        glacier = [glacier_t, 0]
        grassland = [grassland_t, 0]
        hill = [hill_t, 0]
        mountain = [mountain_t, 0]
        ocean = [ocean_t, 0]
        plains = [plains_t, 0]
        tundra = [tundra_t, 0]
        swamp = [swamp_t, 0]
        volcano = [volcano_t, 0]
        waste = [waste_t, 0]
        items = [forest, glacier, grassland, hill, mountain,
                 ocean, plains, tundra, swamp, volcano, waste]
        for tl in self.get_near_tiles(1):
            if tl == self: continue
            if tl not in nation.map: continue
            if tl.hill: hill[1] += 1
            elif tl.surf.name != none_t:
                if tl.surf.name == swamp_t: swamp[1] += 1
                if tl.surf.name == forest_t: forest[1] += 1
                if tl.surf.name == mountain_t: mountain[1] += 1
                if tl.surf.name == volcano_t: volcano[1] += 1
            elif tl.surf.name == none_t:
                if tl.soil.name == coast_t: ocean[1] += 1
                if tl.soil.name == plains_t: plains[1] += 1
                if tl.soil.name == grassland_t: grassland[1] += 1
                if tl.soil.name == waste_t: waste[1] += 1
                if tl.soil.name == tundra_t: tundra[1] += 1
                if tl.soil.name == glacier_t: glacier[1] += 1

        items = [it for it in items if it[1]]
        items.sort(key=lambda x: x[1], reverse=True)
        for it in items:
            sp.speak(f"{it[0]}: {it[1]}.")

    def get_comm_units(self, nation):
        units = []
        for i in self.units:
            if i.leadership == 0: continue
            if i.hidden and nation not in i.belongs: continue
            units += [i]
        return units

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
        distance = 0
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
                self.mean = basics.mean([self.food_value, self.res_value])

    def get_free_squads(self, nation):
        units = []
        for it in self.units:
            if it.leader and nation in it.belongs and it.pos == it.leader.pos: continue
            # if it.leader and it.hidden: continue
            if it.leader and it.leader.revealed and it.pos == it.leader.pos: continue
            if it.leadership: continue
            if it.hidden and nation not in it.belongs: continue
            units += [it]
        return units

    def get_squads(self, nation):
        units = []
        for i in self.units:
            if i.leadership: continue
            if i.hidden and nation not in i.belongs: continue
            units += [i]

        return units

    def launch_avalanche(self):
        if self.hill and self.flood >= 4 and basics.roll_dice(1) >= 5:
            show_info = 0
            if self.nation and self.nation.show_info: show_info = 1
            rate = randint(5, 15)
            if basics.roll_dice(1) >= 6: rate *= 2
            if basics.roll_dice(1) >= 6: rate *= 2
            self.flood -= ceil(rate * self.flood / 100)
            tiles = [it for it in self.get_near_tiles(1)
                     if it.hill == 0 and it != self]
            tile = choice(tiles)
            pop_deads = round(rate * tile.pop / 100)
            tile.pop -= pop_deads
            if tile.nation:
                msg = f"avalanche in {tile} {tile.cords} {pop_deads} {deads_t}."
                tile.nation.log[-1] += [msg]
            if tile.nation:
                tile.add_corpses(choice(tile.nation.population_type), pop_deads)

            units = [it for it in tile.units
                     if it.can_fly == 0 and it.hp_total >= 1]
            for it in units:
                if it.nation.show_info: show_info = 1
                msg = f"{it} losses "
                _units = it.units
                unit_deads = rate * it.hp_total / 100
                it.hp_total -= unit_deads * it.hp_total / 100
                if unit_deads / it.hp: it.deads += [unit_deads / it.hp]
                it.update()
                it.add_corpses(tile)
                msg += f"{_units - it.units} {units_t}."
                it.nation.log[-1] += [msg]
                it.log[-1] += [msg]

            if show_info:
                sp.speak(f"{rate=:}")
                sleep(loadsound("avalanche1", channel=CHTE3) / 2)

    def map_update(self, nation, scenary, editing=0):
        if editing == 0:
            scenary[0].pos_sight(nation, scenary)
            [it.update(nation) for it in scenary]
        elif editing:
            for it in scenary: it.sight = 1
            pos.update(nation)

    def play_events(self):
        if pos.events and pos.sight:
            if len(pos.events) >= 1 and CHTE1.get_busy() == False:
                if self.events[0].sound:
                    ev = choice(self.events[0].sound)
                    vol = self.events[0].vol
                    loadsound(ev, vol=vol, channel=CHTE1)
            if len(pos.events) >= 2 and CHTE2.get_busy() == False:
                if self.events[1].sound:
                    ev = choice(self.events[1].sound)
                    vol = self.events[1].vol
                    loadsound(ev, vol=vol, channel=CHTE2)
            if len(pos.events) >= 3 and CHTE3.get_busy() == False:
                if self.events[2].sound:
                    ev = choice(self.events[2].sound)
                    vol = self.events[2].vol
                    loadsound(ev, vol=vol, channel=CHTE3)

    def play_tile(self):
        for ch in [CHTE1, CHTE2, CHTE3]:
            ch.stop()
        if self.hill: loadsound("terra_hill5", vol=(0.5, 0.5), channel=CHT3)
        if self.surf.name == forest_t: loadsound("terra_forest1", channel=CHT2)
        elif self.surf.name == swamp_t: loadsound("terra_swamp1", channel=CHT2, vol=(0.5, 0.5))
        elif self.soil.name == waste_t: loadsound("terra_waste1", channel=CHT1)
        elif self.soil.name == grassland_t: loadsound("terra_grass1", channel=CHT1)
        elif self.soil.name == plains_t: loadsound("terra_plains1", channel=CHT1)
        elif self.soil.name == ocean_t: loadsound("terra_ocean1", channel=CHT3, vol=0.1)
        elif self.soil.name == coast_t: loadsound("terra_ocean1", channel=CHT3, vol=0.1)
        elif self.soil.name == tundra_t: loadsound("terra_tundra1", channel=CHT1, vol=0.2)

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
                if nation in uni.belongs:
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
                                    # print(f"se agrega {s1}.")
                                if s1.surf.name not in [forest_t] and s1.hill not in [1]:
                                    s1.sight = 1

    def set_around(self, nation):
        # logging.info(f"{self}.")
        score = 0
        if self.city:
            for i in self.city.units: score += i.ranking
        self.around_coast = 0
        self.around_corpses = 0
        self.around_defense = 0
        self.around_forest = 0
        self.around_grassland = 0
        self.around_glacier = 0
        self.around_hill = 0
        self.around_mountain = 0
        self.around_nations = []
        self.around_snations = []
        self.around_plains = 0
        self.around_swamp = 0
        self.coast = 0
        self.around_threat = 0
        self.around_tundra = 0
        self.around_volcano = 0
        self.around_waste = 0
        self.buildings_tags = []
        self.buildings_nation = []
        self.units_aligment = []
        self.units_effects = []
        self.units_traits = []
        self.units_tags = []
        sq = self.get_near_tiles(1)
        for tl in sq:
            if tl != self:
                if tl.hill: self.around_hill += 1
                elif tl.surf.name != none_t:
                    if tl.surf.name == swamp_t: self.around_swamp += 1
                    if tl.surf.name == forest_t: self.around_forest += 1
                    if tl.surf.name == mountain_t: self.around_mountain += 1
                    if tl.surf.name == volcano_t: self.around_volcano += 1
                elif tl.surf.name == none_t:
                    if tl.soil.name == coast_t: self.around_coast += 1
                    if tl.soil.name == plains_t: self.around_plains += 1
                    if tl.soil.name == grassland_t: self.around_grassland += 1
                    if tl.soil.name == waste_t: self.around_waste += 1
                    if tl.soil.name == tundra_t: self.around_tundra += 1
                    if tl.soil.name == glacier_t: self.around_glacier += 1

            if tl.sight and tl != self:
                self.around_corpses += len(tl.corpses)
                if nation:
                    if tl.nation != nation and tl.nation != None:
                        self.around_nations += [tl.nation]
                    if tl.nation == nation: self.around_snations += [tl.nation]
                    units = tl.get_free_squads(
                        nation) + tl.get_comm_units(nation)
                    for uni in units:
                        uni.update()
                        if nation not in uni.belongs:
                            self.around_threat += uni.ranking
                        if uni.nation == nation:
                            self.around_defense += uni.ranking

        # datos finales.
        units = self.get_free_squads(nation) + self.get_squads(nation)
        for uni in self.units:
            self.units_aligment += [uni.aligment]
            self.units_effects += uni.effects
            self.units_tags += uni.tags
            self.units_traits += uni.traits
        for bu in self.buildings:
            self.buildings_tags += bu.tags
            self.buildings_nation += [bu.nation]
        if self.soil.name == ocean_t and any(i for i in [self.around_plains,
                                                         self.around_grassland, self.around_waste, self.around_tundra, self.around_glacier, self.around_forest, self.around_swamp]):
            self.coast = 1
            self.soil.name = coast_t
        elif self.soil.name != ocean_t and self.around_coast:
            self.coast = 1

    def set_blocked(self):
        self.blocked = 0
        for uni in self.units:
            if (uni.hidden == 0 and self.nation not in uni.belongs
                    and self.is_city == 0):
                self.blocked = 1
                break

    def set_corpses(self):
        if self.corpses:
            self.add_miasma()
            self.add_ghouls()
            for cr in self.corpses:
                reducing = randint(5, 20) // cr.hp
                cr.deads[0] -= reducing

    def set_defense(self, nation, info=0):
        if info: logging.info(f"set_defense for {self}.")
        self.defense = 0
        for u in self.units:
            if u.leader: continue
            u.update()
            if nation and nation in u.belongs:
                self.defense += u.ranking
                if info: logging.debug(f"{u.id}  {u.hidden}, {u.ranking}.")

    def set_grouth(self):
        self.grouth_base = self.city.grouth_base
        #self.grouth_food = (self.food - self.pop) / self.city.grouth_factor
        self.grouth_food = self.pop * 100 / self.food
        self.grouth_food = 100 - self.grouth_food
        self.grouth = self.grouth_food * 0.1
        if self.grouth_food > 80: self.grouth *= 1.4
        elif self.grouth_food > 60: self.grouth *= 1.25
        elif self.grouth_food <= 40: self.grouth *= 0.8
        elif self.grouth_food <= 20: self.grouth *= 0.8
        for bu in self.buildings:
            if self.city.nation != bu.nation: continue
            if bu.type == city_t:
                self.grouth += bu.grouth * self.grouth / 100
            elif bu.type == building_t:
                if bu.is_complete == 0: self.grouth += bu.grouth_pre * self.grouth / 100
                if bu.is_complete: self.grouth += bu.grouth * self.grouth / 100
        self.grouth *= self.nation.grouth_rate
        if self.hill not in self.nation.main_pop_hill: self.grouth *= 0.6
        if self.soil.name not in self.nation.main_pop_soil: self.grouth *= 0.8
        if self.surf.name not in self.nation.main_pop_surf: self.grouth *= 0.6

    def set_income(self):
        if self.nation == None or self.pop == 0: return
        if self.pop: self.populated = round(self.pop / self.food * 100)
        self.income = self.pop * self.nation.gold_rate
        self.incomes = [self.income]
        self.income += self.public_order * self.income / 100
        self.incomes += [self.income]
        # de edificios.
        for b in self.buildings:
            self.income += b.income_pre * self.income / 100
            if b.is_complete or b.type == city_t:
                self.income += b.income * self.income / 100
                self.incomes += [str(f"{b}"), self.income]

    def set_public_order(self, info=0):
        if info: logging.debug(f"set_public_order.")
        if self.nation == None: return
        if self.pop < 1:
            self.pop = 0
            self.public_order = 0
            self.unrest = 0
            return

        # From food.
        self.public_order = 100
        if self.pop / self.food * 100 > 50: self.public_order -= 10
        elif self.pop / self.food * 100 > 75: self.public_order -= 30
        elif self.pop / self.food * 100 > 100: self.public_order -= 50
        elif self.pop / self.food * 100 > 150: self.public_order -= 70
        elif self.pop / self.food * 100 > 200: self.public_order -= 80
        self.after_food = self.public_order
        if info: logging.debug(f"after food {self.public_order= }.")

        # From unrest.
        if self.unrest: self.public_order -= abs(
            self.unrest * self.public_order / 100)
        self.after_unrest = self.public_order
        if info: logging.debug(f"after unrest {self.public_order= }.")

        # From city.
        # if self.is_city == 0: self.public_order += abs(self.city.public_order * self.public_order / 100)
        # self.after_city = self.public_order
        if info: logging.debug(f"after if is city {self.public_order= }.")

        # From buildings.
        self.public_order_buildings = 0
        for b in self.buildings:
            self.public_order_buildings += b.public_order_pre
            if b.is_complete or b.type == city_t:
                self.public_order_buildings += b.public_order
        self.public_order += self.public_order_buildings * self.public_order / 100
        self.after_buildings = self.public_order
        if info: logging.debug(f"after buildings {self.public_order= }.")

        # From units.
        if self.defense and self.pop: self.public_order += self.defense / self.pop * 100
        self.after_defense = self.public_order
        if info: logging.debug(f"after units defense {self.public_order= }.")

        if self.public_order > 100: self.public_order = 100
        if self.public_order < -100: self.public_order = -100
        if self.unrest > 100: self.unrest = 100
        self.unrest = round(self.unrest)

    def set_skills(self, info=0):
        if info: logging.debug(f"set_skills")
        self.skills = []
        self.skill_names = []
        self.units.sort(key=lambda x: x.ranking, reverse=True)
        for uni in self.units:
            if uni.hp_total > 0:
                unit_skills = uni.get_skills()
                for sk in unit_skills:
                    if sk.effect in ["all", "friend"] and sk.name not in self.skill_names:
                        self.skills += [sk]
                        self.skill_names += [sk.name]

            self.skill_names.sort()
            [sk.tile_run(self) for sk in self.skills]

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
        if self.soil.name == tundra_t:
            # self.terrain_events = [e for e in self.terrain_events
                                 # if e.name != SwampTerrain.name]
            if TundraTerrain.name not in [e.name for e in self.terrain_events]:
                self.terrain_events += [TundraTerrain(self)]
        # day.
        if self.world.ambient.day_night[0] == 0:
            self.terrain_events = [e for e in self.terrain_events
                                   if e.name != night_t]
        # night.
        if self.world.ambient.day_night[0]:
            if Night.name not in [e.name for e in self.terrain_events]:
                self.terrain_events += [Night(self)]

    def set_threat(self, nation):
        self.threat = 0
        if self.sight:
            units = self.get_free_squads(nation) + self.get_comm_units(nation)
            for uni in units:
                uni.update()
                if nation in uni.belongs: continue
                self.threat += uni.ranking

    def start_turn(self):
        self.raining = 0
        self.storm = 0
        for ev in self.events:
            ev.tile_run(self)
        self.events = [ev for ev in self.events if ev.turns > 0]
        self.burned = 0
        self.corpses = [i for i in self.corpses + self.units if i.hp_total < 1 and sum(i.deads) > 0
                        and i.corpses]
        if self.city: self.city.raid_outcome = 0
        if self.flood > 0: self.flood -= 1
        if self.ambient.sseason == summer_t: self.flood -= 1
        self.raided = 0
        if self.unrest > 0: self.unrest -= randint(1, 2)
        if self.unrest > 0: self.unrest -= self.defense * 0.1
        if self.unrest < 0: self.unrest = 0
        self.units_blocked + [u for u in self.units if u.blocked > 0]
        for u in self.units_blocked: u.blocked -= 1
        self.units += [u for u in self.units_blocked if u.blocked < 1]
        self.units_blocked = [u for u in self.units_blocked if u.blocked > 0]
        self.set_corpses()

    def stats_buildings(self):
        for b in self.buildings:
            if b.type == building_t: b.update()
            if b.is_complete == 0:
                self.food += b.food_pre * self.food / 100
                self.resource += b.resource_pre * self.resource / 100
            if b.is_complete or b.type == city_t:
                self.food += b.food * self.food / 100
                self.resource += b.resource * self.resource / 100

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
        self.grouth = 0
        self.resource = self.soil.resource
        self.resource *= self.surf.resource
        if self.hill:
            self.cost += 1
            self.food *= 0.6
            self.resource *= 2

    def update(self, nation=None, info=0):
        if info: logging.debug(f"update {self} {self.cords}.")
        if self.surf.__class__ == EmptySurf: self.surf.name = none_t
        self.effects = []
        if mapeditor == 0:
            self.ambient = world.ambient
            self.set_skills()
            self.set_tile_skills()
        self.has_city = 1 if self.city else 0
        self.is_city = 1 if [
            i for i in self.buildings if i.type == city_t] else 0
        self.set_around(nation)

        if nation:
            self.get_tile_value(nation, nation.map)
            self.set_threat(nation)

        # eliminando unidades, generando corpses.
        try:
            self.corpses = [i for i in self.corpses + self.units if i.hp_total < 1
                            and sum(i.deads) > 0 and i.corpses]
        except: Pdb().set_trace()
        self.units = [it for it in self.units
                      if it.hp_total >= 1]
        self.set_blocked()

        # calculando defensa.
        self.set_defense(nation)

        # destruyendo edificios.
        for b in self.buildings:
            if b.resource_cost[0] < 1:
                msg = f"{b} {destroyed_t} {in_t} {self} {self.cords}."
                if self.nation: self.nation.log[-1].append(msg)
                logging.debug(msg)
                sleep(loadsound("set8") / 2)

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
        if self.city: self.set_grouth()
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
        self.pop = round(self.pop, 1)
        self.public_order = round(self.public_order)
        self.resource = round(self.resource)
        self.threat = round(self.threat)

        self.day_night = self.ambient.day_night[0]
        self.month = self.ambient.smonth
        self.season = self.ambient.sseason
        self.time = self.ambient.stime
        self.week = self.ambient.week
        self.year = self.ambient.year


class EmptySurf(Terrain):
    name = none_t


class Desert(Terrain):
    cost = 2
    cost_fly = 2
    food = 100
    name = waste_t
    resource = 1


class Glacier(Terrain):
    cost = 2
    cost_fly = 2
    food = 60
    name = glacier_t
    resource = 0


class Grassland(Terrain):
    cost = 2
    cost_fly = 2
    food = 300
    name = grassland_t
    resource = 1


class Forest(Terrain):
    name = forest_t
    cost = 1
    food = 0.7
    resource = 2

    def __init__(self):
        Terrain.__init__(self)
        self.tile_effects = [ForestTerrain]


class Mountain(Terrain):
    cost = 2
    cost_fly = 1
    food = 0.5
    name = mountain_t
    resource = 0


class Swamp(Terrain):
    name = swamp_t
    cost = 1
    food = 0.8
    resource = 1

    def __init__(self):
        Terrain.__init__(self)
        self.tile_effects = [SwampTerrain]


class Ocean(Terrain):
    cost = 1
    cost_fly = 2
    food = 150
    name = ocean_t
    resource = 0


class Plains(Terrain):
    name = plains_t
    cost = 2
    cost_fly = 2
    food = 200
    resource = 1


class River(Terrain):
    cost = 1
    food = 150
    name = river_t
    resource = 0


class Tundra(Terrain):
    cost = 2
    cost_fly = 2
    food = 150
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
    difficulty_type = "simple"  # simple, dynamic.
    difficulty_change = 100
    east = 0
    events = []
    ext = None
    height = 0
    log = []
    name = "Unnamed"
    nations = []
    nations_score = 0
    map = []
    player_num = 0
    random_score = 0
    units = []
    turn = 0
    units = []
    west = 0
    width = 0

    def add_random_buildings(self, value, info=1):
        logging.info(f"add_random_buildings {world.turn=:}.")
        tiles = [t for t in self.map if t.buildings == []
                 and t.get_nearest_nation() <= 4]
        [t.update() for t in tiles]
        shuffle(tiles)
        shuffle(self.random_buildings)
        while value:
            for bu in self.random_buildings:
                tile = tiles.pop()
                for nt in self.random_nations:
                    if nt.name == bu.nation: bu = bu(nt, tile)
                if info: logging.debug(f"adding_t {bu}.")
                if bu.common:
                    roll = randint(1, 13)
                    if info: logging.debug(f"{bu.common=:}, {roll=:}.")
                    if roll > bu.common: continue
                if City.check_tile_req(bu, tile) and len(tile.buildings) < 1:
                    msg = f"{bu} added in {tile} {tile.cords}."
                    if info: logging.debug(msg)
                    self.log[-1] += [msg]
                    bu.size = 0
                    bu.resource_cost[0] = bu.resource_cost[1]
                    tile.buildings += [bu]
                    self.buildings += [bu]
                    value -= 1
                    if value < 1: break

    def add_random_unit(self, value, info=1):
        logging.info(f"add_random_unit {value=:}.")
        count = randint(1, 3)
        if basics.roll_dice(1) == 6: count += 1
        tries = 20
        if info:
            msg = f"{count=:}."
            self.log[-1] += [msg]
            logging.debug(msg)
        while tries > 0 and value > 0 and count > 0:
            count -= 1
            tries -= 1
            shuffle(self.buildings)
            self.buildings.sort(key=lambda x: len(x.units))
            building = self.buildings[0]
            shuffle(building.av_units)
            if basics.roll_dice(1) >= 5:
                building.av_units.sort(
                    key=lambda x: x.leadership > 1, reverse=True)
            if info: logging.debug(f"adding unit from {building}.")
            for uni in building.av_units:
                logging.debug(f"adding {uni.name}.")
                if uni.common:
                    roll = randint(1, 13)
                    if info: logging.debug(f"{uni.common=:}, {roll=:}.")
                    if roll > uni.common: continue
                uni = uni(building.nation)
                uni.city = building
                building.units += [uni]
                if info: logging.debug(f"agregará {uni}.")
                try:
                    uni.update()
                except: Pdb().set_trace
                if uni.units > 1 and uni.leadership == 0:
                    if info: logging.debug(f"randomly set units number")
                    uni.hp_total = randint(30, 60) * uni.hp_total / 100
                    uni.update()
                uni.pos = building.pos
                uni.nation.update(uni.nation.map)
                loadsound("set10")
                building.pos.units += [uni]
                self.units.append(uni)
                if uni.leadership:
                    av_units = [
                        it for it in building.av_units if it.leadership == 0]
                    for r in range(randint(1, 3)):
                        if av_units == []: break
                        if uni.leading > uni.leadership * 0.75: break
                        if info: logging.debug(f"adding squads to {uni}.")
                        squad = choice(av_units)(uni.nation)
                        squad.hp_total = randint(40, 60) * squad.hp_total / 100
                        squad.city = uni.city
                        squad.leader = uni
                        squad. pos = uni.pos
                        uni.pos.units += [squad]
                        uni.leads += [squad]
                        squad.update()
                        uni.update()
                        if info: logging.debug(f"added {squad}")
                value -= uni.ranking
                self.log[-1] += [f"{uni} {added_t} {in_t} {building.pos} {building.pos.cords}."]
                if info: logging.debug(f"{uni}. ranking {uni.ranking}.")
                break

    def autum_events(self):
        for r in range(len(self.map) // 50):
            events = [CastRain]
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
            sp.speak(f"Defeat.", 1)
            PLAYING = False
        elif hu and ai == []:
            sp.speak(f"Victory!")
            PLAYING = False

    def building_restoration(self):
        for b in self.buildings:
            units = [uni for uni in b.pos.units if b.nation not in uni.belongs]
            if units: continue
            if b.resource_cost[0] < b.resource_cost[1]:
                b.resource_cost[0] += b.resource_cost[1] * 0.2
                if b.resource_cost[0] > b.resource_cost[1]:
                    b.resource_cost[0] = b.resource_cost[1]

    def generic_events(self):
        pass

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

    def show_random_buildings(self, sound="in1"):
        sleep(loadsound(sound) / 2)
        items = self.buildings
        say = 1
        x = 0
        while True:
            sleep(0.001)
            if say:
                if items: sp.speak(
                    f"{items[x]}. on {items[x].pos} {items[x].pos.cords}")
                else: sp.speak(f"{empty_t}.")
                if items[x].pos.city: sp.speak(f"{items[x].pos.city}.")
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
                    if event.key == pygame.K_i:
                        items[x].info()
                    if event.key == pygame.K_RETURN:
                        pass
                    if event.key == pygame.K_ESCAPE:
                        sleep(loadsound("back1") / 2)
                        return

    def show_random_units(self, sound="in1"):
        sleep(loadsound(sound) / 2)
        self.update(self.map)
        units = [i for i in self.units if i.hp_total >= 1
                 and i.leader == None]
        items = units
        self.nations_score = sum(n.score for n in self.nations)

        self.random_score = sum(u.ranking for u in self.units)
        say = 1
        x = 0
        while True:
            sleep(0.001)
            if say:
                if items:
                    sp.speak(f"{items[x]}. ", 1)
                    sp.speak(f"({items[x].aligment}).")
                    if items[x].leads:
                        sp.speak(
                            f"leads {items[x].leading}, ({len(items[x].leads)}).")
                    sp.speak(f"on {items[x].pos} {items[x].pos.cords}")
                else: sp.speak(f"{empty_t}.")
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
                    if event.key == pygame.K_F1:
                        max_score = self.difficulty * self.nations_score / 100
                        sp.speak(
                            f"{self.difficulty=: }. {self.nations_score=: } .", 1)
                        sp.speak(f"{self.random_score=: } of {max_score}.")
                    if event.key == pygame.K_l:
                        items[x].set_army(items[x].nation)
                    if event.key == pygame.K_i:
                        items[x].info(items[x].nation)
                    if event.key == pygame.K_F12 and ctrl and shift:
                        sp.speak(f"on", 1)
                        Pdb().set_trace()
                        sp.speak(f"off", 1)
                    if event.key == pygame.K_RETURN:
                        global pos
                        pos = items[x].pos
                        sleep(loadsound("back1") / 2)
                        return
                    if event.key == pygame.K_ESCAPE:
                        sleep(loadsound("back1") / 2)
                        return

    def summer_events(self):
        for r in range(len(self.map) // 50):
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
        for r in range(len(self.map) // 50):
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
        for r in range(len(self.map) // 50):
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
                if uni.nation in self.random_nations: self.units += [uni]
        for bu in self.buildings:
            bu.units = [uni for uni in bu.units if uni.hp_total >= 1]
        self.nations_score = sum(n.score for n in self.nations)
        self.units = [i for i in self.units if i.hp_total >= 1]

        self.random_score = sum(u.ranking for u in self.units)
        [nt.update(scenary) for nt in self.random_nations]


class Ai:

    def ai_action_random(self, itm, info=1):
        itm.update()
        itm.pos.update(itm.nation)
        logging.debug(
            f"acción aleatórea para {itm} en {itm.pos} {itm.pos.cords}.")
        if info: logging.debug(f"salud {itm.hp_total}. mp {itm.mp}")
        tries = 3
        while (itm.mp[0] > 0 and itm.hp_total > 0 and itm.goto == []
               and tries > 0 and itm.stopped == 0):
            # si está en movimiento.
            if itm.goto:
                if info: logging.debug(
                    f"se dirije a {itm.goto[0][1]} en {itm.goto[0][0]}.")
                return
            # si no descansa y no se mueve.
            elif itm.goto == []:
                # cast spells.
                if itm.spells: self.ai_unit_cast(itm.nation)
                # ataque hidden.
                itm.pos.update(itm.nation)
                rnd = itm.ranking * uniform(0.6, 1.2)
                if itm.pos.surf.name == forest_t and itm.forest_survival == 0: rnd -= rnd * 0.2
                if itm.pos.hill and itm.mountain_survival == 0: rnd -= rnd * 0.2
                if itm.pos.surf.name == swamp_t and itm.swamp_survival == 0: rnd -= rnd * 0.2
                if itm.leadership: rnd -= rnd * 0.2
                if info: logging.debug(f"{rnd=:}, {itm.pos.threat=:}.")
                if rnd > itm.pos.threat:
                    try:
                        itm.auto_attack()
                    except: Pdb().set_trace()
                    if any(i <= 0 for i in [itm.mp[0], itm.hp_total]): return

                # moves.
                if itm.mp[0] > 0 and itm.will_less == 0:
                    if itm.pos.around_threat + itm.pos.threat < itm.ranking and basics.roll_dice(1) >= 5:
                        if info: logging.debug(f"no moves by randomness.")
                        return
                    itm.random_move()
                    # cast spells.
                    if itm.spells: self.ai_unit_cast(itm.nation)
                if itm.will_less: return logging.debug(f"will_less.")
            tries -= 1
            if tries <= 0:
                logging.debug(f"tries at 0.")
                Pdb().set_trace()

    def ai_add_settler(self, nation, info=1):
        """buscará entrenar colonos para fundar nueva ciudad."""
        logging.info(f"ai_add_settler. gold {nation.gold}.")
        if info: logging.debug(
            f"pop_req  {nation.pop} de {nation.city_req_pop}.")
        if nation.pop < nation.city_req_pop or min(c.defense_total_percent for c in nation.cities) < 200: return
        settlers = [i for i in nation.units if i.settler]
        for ct in nation.cities:
            if ct.production and ct.production[0].settler: settlers += [
                ct.production]
        if info: logging.debug(
            f"settlers {len(settlers)}, tiles far {len(nation.tiles_far)}.")
        if len(nation.tiles_far) and settlers == []:
            for ct in nation.cities:
                if ct.nation.defense_total_percent < 200:
                    if info: logging.debug(f"not enough defense total percent.")
                    continue
                if len(ct.tiles_far) < 1:
                    if info: logging.debug(f"not land to set.")
                    continue
                if info: logging.debug(f"pop {in_t} {ct} {ct.pop}.")
                if info: logging.debug(
                    f"defense_total_percent {ct.defense_total_percent}. de ")
                if info: logging.debug(f"seen threat {ct.seen_threat}.")
                if ct.seen_threat > 30 * ct.defense_total // 100:
                    if info: logging.debug(f"high threat.")
                    continue
                if ct.production == []:
                    ct.update()
                    if info: logging.debug(f"gold {ct.nation.gold}.")
                    units = [it(nation) for it in ct.all_av_units]
                    [i.update() for i in units]
                    units = [it for it in units if it.settler]
                    shuffle(units)
                    if units: unit = units[0]
                    if req_unit(unit, nation, ct):
                        ct.train(unit)
                    break

    def ai_add_explorer(self, nation, info=1):
        logging.info(f"ai_add_explorer {nation}. {world.turn= }.")
        if info: logging.debug(f"{nation.score=:}, {nation.seen_threat=:}.")
        for uni in nation.units_scout:
            distanse_limit = uni.mp[1] + uni.nation.explore_range
            if (uni.pos.get_distance(uni.pos, uni.city.pos) >= distanse_limit - 1
                    and basics.roll_dice(2) >= 10):
                uni.scout = 0
                msg = f"{uni} in {uni.pos} {uni.pos.cords} stops exploring."
                uni.log[-1] += [msg]
                logging.debug(msg)
            elif nation.defense_mean < 100:
                uni.scout = 0
                msg = f"{uni} stops exploring by threats."
                uni.log[-1] += [msg]
                logging.debug(msg)

        nation.update(nation.map)
        if nation.units_free == []:
            if info: logging.debug(f"not available units.")
            return
        if nation.defense_mean < 100:
            if info: logging.debug(f"lack of defense.")
            return
        scouts = len(nation.units_scout)
        if nation.defense_mean >= 200: scout_limit = 6
        elif nation.defense_mean >= 150: scout_limit = 4
        elif nation.defense_mean >= 100: scout_limit = 2
        if info: logging.debug(f"{scouts=:}, {scout_limit=:}.")
        if scouts >= scout_limit: return
        shuffle(nation.cities)
        for ct in nation.cities:
            if info: logging.debug(f"{ct}.")
            if info: logging.debug(
                f"defense_total_percent {ct.defense_total_percent}.")
            if info: logging.debug(f"initial units {len(ct.units)}.")
            if ct.defense_total_percent > 100:
                units = [it for it in ct.nation.get_free_squads()
                         if it.will_less == 0]
                if info: logging.debug(f"final units {len(units)}.")
                units.sort(key=lambda x: x.mp[1] >= 2
                           or (x.can_fly or x.forest_survival or x.mountain_survival
                               or x.swamp_survival), reverse=True)
                units.sort(key=lambda x: x.ranking, reverse=True)
                for it in units:
                    if info:
                        msg = f"{it} squads {it.squads}."
                        logging.debug(msg)
                    if it.squads < 2: basics.ai_join_units(it)
                    it.scout = 1
                    msg = f"{it} is now explorer."
                    if info: logging.debug(msg)
                    it.log[-1] += [msg]
                    return

    def ai_attack(self, nation, info=1):
        logging.info(f"ai_attack")
        if nation.expanding or nation.seen_nations == []: return
        [i.update(nation) for i in nation.map]
        nation.set_seen_nations()
        nation.status()
        if info: logging.debug(
            f"defense mean {nation.defense_mean}. attack factor {nation.attack_factor}.")
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

        if info: logging.debug(
            f"capture {nation.capture}, stalk {nation.stalk}.")
        nation.seen_nations.sort(key=lambda x: x.score)
        for nt in nation.seen_nations:
            if info: logging.debug(f"stalk a {nt}.")
            if info: logging.debug(f"seen tiles {len(nt.seen_tiles)}.")
            if info: logging.debug(f"seen units {len(nt.seen_units)}.")
            if info: logging.debug(
                f"seen cities {len([c for c in nt.seen_tiles if c.is_city])}.")
            if info: logging.debug(f"score {nt.score}.")
            shuffle(nt.seen_tiles)
            nt.seen_tiles.sort(key=lambda x: x.around_forest, reverse=1)
            nt.seen_tiles.sort(key=lambda x: x.around_hill, reverse=1)
            if basics.roll_dice(1) >= 5:
                nt.seen_tiles.sort(key=lambda x: x.hill, reverse=True)
            # stalk.
            for it in nt.seen_tiles:
                logging.debug(f"can_stalk {can_stalk}.")
                if can_stalk < 1: break
                units = nation.get_free_squads()
                units = [i for i in units if i.leader == 0
                         and i.pos.get_distance(i.pos, it) <= 5]
                if info: logging.debug(f"{len(units)} unidades disponibles.")
                if len(units) == 0: break
                units.sort(key=lambda x: x.ranking)
                if it.surf.name == forest_t: units.sort(
                    key=lambda x: x.forest_survival, reverse=True)
                if it.surf.name == swamp_t: units.sort(
                    key=lambda x: x.swamp_survival, reverse=True)
                if it.hill:
                    units.sort(key=lambda x: x.mountain_survival, reverse=True)
                    units.sort(key=lambda x: x.ranged, reverse=True)
                units.sort(key=lambda x: x.mp[1] >= 2)
                itm = units[0]
                if itm.squads == 1:
                    basics.ai_join_units(itm, randint(1, 2))
                itm.goal = [stalk_t, t]
                itm.move_set(it)
                can_stalk -= 1

            # capture.
            tiles = [i for i in nt.seen_tiles]
            [i.update(nation) for i in tiles]
            tiles = [i for i in tiles
                     if i.sight and (i.bu or i.is_city)]
            tiles.sort(key=lambda x: len(x.buildings), reverse=True)
            tiles.sort(key=lambda x: basics.mean([x.threat, x.around_threat]))
            for it in tiles:
                logging.debug(f"can_capture {can_capture}.")
                if can_capture < 1: break
                units = [uni for uni in nation.units_comm
                         if uni.leading / uni.leadership >= 0.8
                         and uni.pos.around_threat + uni.pos.threat == 0]
                units = [uni for uni in units if uni.pos.city
                         and uni.pos.get_distance(uni.pos.city.pos, it) <= 3]
                logging.debug(f"unidades {len(units)}.")
                if len(units) < 1: break
                logging.debug(f"ranking de {it} {it.threat}")
                units.sort(key=lambda x: x.ranking, reverse=True)
                itm = units[0]
                threat = t.threat
                itm.goal = [capture_t, it]
                itm.move_set(it)

    def ai_divide_units(self, nation):
        units = [i for i in nation.units
                 if i.can_join and i.goto == []
                 and i.leader == None and i.leads == []]
        for i in units:
            i.pos.update(i.nation)
            if i.pos.around_threat > i.ranking * 0.5: continue
            city = i.pos.city
            if city: city.set_defense()
            roll = basics.roll_dice(1)
            needs = 6 - i.squads
            if i.scout: needs -= 2
            if i.pos.hill or i.ranged: needs += 2
            if i.pos.food_need >= i.pos.food: needs = 2
            if city and city.around_threat > city.defense: needs += 3
            if roll >= needs:
                i.split()

    def ai_expand_city(self, city, info=1):
        """buscará expandir la ciudad."""
        logging.info(f"ai_expand_city {city}. gold {city.nation.gold}")
        city.nation.devlog[-1] += [f"expanding {city}"]
        if (city.nation.path.build_military == "improve"
                and basics.roll_dice(1) >= 2):
            if info: logging.debug(f"skipping by build military path.")
            return
        if city.buildings_military_complete == []: return "not military buildings."
        if len(city.tiles) >= 11 and len(city.buildings_military_complete) < 2: return "lack of military buildings."
        if len(city.tiles) >= 13 and len([b for b in city.buildings_military_complete if b.level == 2]) < 2: return "lack of military buildings."
        if city.seen_threat > 50 * city.defense_total / 100:
            msg = f"seen threat {city.seen_threat}. total defense {city.defense_total} hight threatss. to expand"
            city.nation.devlog[-1] += [msg]
            return msg

        rnd = basics.roll_dice(1)
        if rnd >= 5: request = "res"
        else: request = "food"
        logging.debug(f"{request=:}, {rnd=:}.")

        # revisara requisitos extras.

        defense_percent_need = 120
        if len(city.tiles) >= 11: defense_percent_need = 160
        if len(city.tiles) >= 13: defense_percent_need = 200
        if len(city.tiles) >= 15: defense_percent_need = 300

        if request == "food":
            logging.debug(f"request food.")
            tiles = city.get_tiles_food(city.tiles_near)
            shuffle(tiles)
            tiles.sort(key=lambda x: x.food, reverse=True)
            tiles.sort(key=lambda x: x.get_distance(city.pos, x))
        elif request == "res":
            logging.debug(f"request res.")
            tiles = city.get_tiles_res(city.tiles_near)
            shuffle(tiles)
            tiles.sort(key=lambda x: x.resource, reverse=True)
            tiles.sort(key=lambda x: x.get_distance(city.pos, x))
        tiles.sort(key=lambda x: len(x.around_snations), reverse=True)

        tiles = [t for t in tiles if t.blocked == 0]
        if tiles:
            msg = f"{tiles[0]}. {len(tiles)} tiles to expand."
            logging.debug(msg)
            cost = city.nation.tile_cost
            distance = city.pos.get_distance(tiles[0], city.pos)
            cost = cost ** (city.nation.tile_power + distance / 10)
            cost = int(cost)
            logging.debug(f"costo {cost}")
            city.nation.devlog[-1] += [f"cost {cost}."]
            city.nation.devlog[-1] += [
                f"need defense {defense_percent_need}. total defense percent {city.defense_total_percent}"]
            if tiles[0].threat + tiles[0].around_threat:
                msg = f"threat seen."
                logging.debug(msg)
                city.nation.devlog[-1] += [msg]
                return
            if (city.nation.gold - cost > 0
                    and city.defense_total_percent >= defense_percent_need):
                city.nation.gold -= cost
                city.tiles.append(tiles[0])
                tiles[0].city = city
                tiles[0].nation = city.nation
                msg = f"{city} se expandió a {tiles[0]}, {tiles[0].cords}. costo {cost}."
                if city.nation.show_info: sp.speak(msg)
                nation.log[-1].append(msg)
                loadsound("warn3")
                return msg

    def ai_explore(self, nation, scenary, info=0):
        logging.info("ai_explore {nation}. {world.turn= }..")
        if info: sp.speak(f" explorando.", 1)
        units = [it for it in nation.units if it.goto == [] and it.mp[0] > 0
                 and it.ai and (it.scout or it.auto_explore)]
        if units: logging.debug(f"{len(units)} exploradores.")
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
                if sq: uni.random_move(sq=sq)
                else:
                    msg = f"sin lugar donde explorar"
                    logging.debug(msg)
                    sleep(1)

    def ai_free_groups(self, nation):
        logging.info(f"ajuste de grupos")
        nation.get_groups()
        if nation.groups: logging.debug(f"grupos {len(nation.groups)}.")
        if nation.groups_free: logging.debug(
            f"grupos libres {len(nation.groups_free)}.")

        for itm in nation.groups_free:
            logging.debug(f"{itm} misión {itm.goal[0]} en {itm.goal[1]}.")
            itm.pos.update(itm.nation)
            # capture.
            if itm.goal[0] == capture_t:
                units = itm.leads
                units.sort(key=lambda x: x.ranking)
                units.sort(key=lambda x: x.leadership)
                if itm.leads == []:
                    logging.debug(
                        f"{itm} sin grupo no mantiene casilla en {itm.pos} {itm.pos.cords}.")
                    itm.break_group()
                    return
                itm.pos.update(itm.pos.nation)
                if itm.goal[1] == itm.pos: itm.break_group()

            # settle.
            if itm.goal[0] == "settle":
                settler = None
                for it in itm.leads:
                    if it.settler: settler = it

                if settler:
                    if settler.set_settlemment():
                        itm.goal = None
                        return
                    else: Pdb().set_trace()
                elif settler == None:
                    itm.go_home()
            # stalk.
            if itm.goal[0] == stalk_t:
                roll = roll_dice(1)
                finish = 4
                if itm.pos.hill: finish -= 1
                if itm.pos.surf.name == forest_t: finish -= 1
                if (itm.pos.bu and itm.pos.nation not in itm.belongs
                        and any(i for i in [itm.can_burn, itm.can_raid])):
                    logging.debug(
                        f"{itm} está en edificio enemigo ({itm.pos.building}. skip {finish}.")
                    continue
                if itm.pos.around_threat > (
                    itm.pos.defense + itm.pos.around_defense) * 1.5: finish += 3
                logging.debug(f"roll {roll}. finish {finish}.")
                if roll < finish:
                    logging.debug(f"{itm} se retira.")
                    itm.break_group()

    def ai_free_units(self, nation, info=1):
        logging.info(f"unidades libres.")
        for uni in nation.units_free:
            if uni.squads >= 3 and uni.pos.around_threat + uni.pos.threat < uni.ranking * 0.4:
                uni.split(1)
                logging.debug(f"splits.")
        nation.get_free_squads()
        if nation.units_free and info: logging.debug(
            f"{len(nation.units_free)} unidades libres.")
        nation.units_free.sort(key=lambda x: x.ranking, reverse=True)
        banned_tiles = []
        for uni in nation.units_free:
            if info: logging.debug(
                f"{uni}. ranking {uni.ranking} en {uni.pos} {uni.pos.cords}.")
            if uni.will_less: continue
            msg = f"free moves in {uni.pos} {uni.pos.cords}."
            uni.log[-1] += [msg]
            move = 1
            num = 1
            while uni.goto == [] and move and uni.mp[0] > 1:
                uni.pos.update(uni.nation)
                if uni.pos.nation == uni.nation:
                    uni.oportunist_attack()
                    if any(i < 1 for i in [uni.mp[0], uni.hp_total]): break

                if uni.pos.nation not in uni.belongs:
                    skip = 0
                    msg = f"out of nation."
                    if info: logging.debug(msg)
                    uni.log[-1] += [msg]
                elif uni.pos.food_need > uni.pos.food:
                    skip = 1
                    msg = f"lack of food ({uni.pos.food_need}, {uni.pos.food})."
                    if info: logging.debug(msg)
                    uni.log[-1] += [msg]
                elif uni.pos.public_order < 60:
                    skip = 6
                    msg = f"low public order {uni.pos.public_order}."
                    if info: logging.debug(msg)
                    uni.log[-1] += [msg]
                elif uni.pos.is_city:
                    skip = 1
                    msg = f"own city."
                    if info: logging.debug(msg)
                    uni.log[-1] += [msg]
                elif uni.pos.nation == uni.nation and uni.pos.buildings:
                    skip = 6
                    msg = f"have buildings."
                    if info: logging.debug(msg)
                    uni.log[-1] += [msg]
                elif uni.pos.nation == nation and uni.pos.bu == 0:
                    skip = 2
                    msg = f"not buildings."
                    if info: logging.debug(msg)
                    uni.log[-1] += [msg]
                    if ((uni.forest_survival or uni.ranged)
                            and uni.pos.surf.name == forest_t):
                        skip += 3
                        msg = f"forest survival."
                        if info: logging.debug(msg)
                        uni.log[-1] += [msg]
                    if uni.pos.hill:
                        skip += 3
                        msg = f"with hills."
                        if info: logging.debug(msg)
                        uni.log[-1] += [msg]
                    if uni.pos.around_hill or uni.pos.around_forest:
                        skip += 3
                        msg = f"around hills or forests.."
                        if info: logging.debug(msg)
                        uni.log[-1] += [msg]

                roll = basics.roll_dice(1)
                if info: logging.debug(f"roll {roll}, skip {skip}.")
                if skip >= roll:
                    msg = f"salta."
                    if info: logging.debug(msg)
                    uni.log[-1] += [msg]
                    break
                sq = uni.pos.get_near_tiles(num)
                sq = [it for it in sq if uni.can_pass(it)
                      and it != uni.pos and it.nation == uni.nation
                      and it not in banned_tiles]
                msg = f"num {num} tiles {len(sq)}."
                if info: logging.debug(msg)
                uni.log[-1] += [msg]
                num += 1
                if num == 5:
                    msg = f"no tiles found."
                    if info: logging.debug(msg)
                    uni.log[-1] += [msg]
                    uni.move_set(uni.city.pos)
                    return
                [it.set_around(nation) for it in sq]
                shuffle(sq)
                sq.sort(key=lambda x: x.around_forest, reverse=True)
                sq.sort(key=lambda x: x.around_hill, reverse=True)
                sq.sort(key=lambda x: x.hill and x.defense == 0, reverse=True)
                sq.sort(key=lambda x: len(x.buildings)
                        and x.defense == 0, reverse=True)
                sq.sort(key=lambda x: x.public_order, reverse=True,)
                if uni.ranged:
                    sq.sort(key=lambda x: x.hill
                            or (x.surf and x.surf.name == forest_t), reverse=True)
                sq.sort(key=lambda x: uni.get_favland(x), reverse=True)
                sq.sort(key=lambda x: x.defense_req - x.defense, reverse=True)
                sq.sort(key=lambda x: military_t in x.buildings_tags
                        and x.defense_req > x.defense, reverse=True)
                for it in sq:
                    rnd = uni.ranking * uniform(0.75, 1.25)
                    if it.food < it.food_need + uni.food_total:
                        if info: logging.debug(f"food needs")
                        continue
                    if it.bu: rnd += rnd * 0.3
                    if it.cost > uni.mp[0]: move = 0
                    elif it.cost <= uni.mp[0]: move = 1
                    if info: logging.debug(
                        f"defense {it.defense} rnd {rnd} threat {it.threat}. {it} {it.cords}.")
                    if rnd > it.threat:
                        if info:
                            msg = f"se moverá."
                            logging.debug(msg)
                            uni.log[-1] += [msg]
                        uni.move_set(it)
                        num -= 1
                        banned_tiles += [it]
                        break

    def ai_garrison(self, nation, info=0):
        logging.info(f"ai_garrison.")
        nation.devlog[-1] += [f"acciones de unidades en guarnición."]
        nation.update(nation.map)
        banned = []
        if info: logging.debug(
            f"unidades iniciales {len([i for i in nation.units if i.garrison])}.")
        nation.devlog[-1] += [
            f"unidades iniciales {len([i for i in nation.units if i.garrison and i.pos.around_threat+i.pos.threat])}."]
        # joining forcetl.
        for uni in [i for i in nation.units if i.garrison and i.pos.around_threat + i.pos.threat]:
            if uni.hp_total < 1 or uni.will_less: continue
            nation.devlog[-1] += [f"{uni} in {uni.pos} {uni.pos.cords}."]
            sq = uni.pos.get_near_tiles(1)
            [i.update(nation) for i in sq]
            sq = [i for i in sq if i.threat]
            for tl in sq:
                units = tl.get_free_squads(nation) + tl.get_comm_units(nation)
                rnd = uni.ranking
                msg = f"ranking {rnd}."
                nation.devlog[-1] += [msg]
                if info: logging.debug(msg)
                try:
                    moves = max(it.moves + it.moves_mod for it in units
                                if nation not in it.belongs)
                except: Pdb().set_trace()
                rng = max(it.range[1]
                          for it in units if nation not in it.belongs)
                if info: logging.debug(f"rnd inicial {rnd}.")
                if tl.around_threat:
                    rnd *= 0.8
                    msg = f"reduced by around_threat to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.leadership and uni.leads == []:
                    rnd *= 0.6
                    msg = f"reduced by comm to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.dark_vision == 0 and uni.pos.day_night:
                    rnd *= 0.6
                    msg = f"reduced by dark vision."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.forest_survival and tl.surf.name != forest_t:
                    rnd *= 0.8
                    msg = f"reduced by not forest tile to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.swamp_survival and tl.surf.name != swamp_t:
                    rnd *= 0.8
                    msg = f"reduced by not swamp tile to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.mountain_survival and tl.hill == 0:
                    rnd *= 0.8
                    msg = f"reduced by not mountaint tile to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.mounted and tl.surf.name in [forest_t, swamp_t] or tl.hill:
                    rnd *= 0.5
                    msg = f"reduced by forest or hill or swamp to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.forest_survival == 0 and tl.surf.name in [forest_t]:
                    rnd *= 0.5
                    msg = f"reduced by forest to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.swamp_survival == 0 and tl.surf.name in [swamp_t]:
                    rnd *= 0.5
                    msg = f"reduced by swamp to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.mountain_survival == 0 and tl.hill:
                    rnd *= 0.5
                    msg = f"reduced by hill to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if moves > uni.moves + uni.moves_mod:
                    rnd *= 0.7
                    msg = f"reduced by hight moves to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if (rng >= 6 and uni.range[1] < rng
                        and uni.shield == None and uni.armor == None):
                    rnd *= 0.6
                    msg = f"reduced by rng{rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if tl.nation != nation:
                    rnd *= 0.8
                    msg = f"reduced by not nation tile."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if tl.nation != nation and tl.nation:
                    rnd *= 0.8
                    msg = f"reduced by other nation tile to {rnd} and nation."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                max_ranking = max(it.ranking for it in units if
                                  nation not in it.belongs)
                nation.devlog[-1] += [f"rnd {rnd} max_ranking {max_ranking}."]
                if rnd * 0.8 < max_ranking:
                    msg = f"joining forces."
                    nation.devlog[-1] += [msg]
                    if info: logging.debug(msg)
                    if rnd * \
                        0.8 < max_ranking: basics.ai_join_units(uni, count=1)
                    elif max_ranking > rnd * 1.5: basics.ai_join_units(uni, count=2)
                    elif max_ranking > rnd * 2: basics.ai_join_units(uni, count=4)
                    elif max_ranking > rnd * 3: basics.ai_join_units(uni, count=20)

        # Ranged garrison.
        units = [it for it in nation.units if it.garrison and it.range[1] >= 6
                 and it.leadership == 0 and it.pos.around_threat + it.pos.threat
                 and it.mp[0] >= 2 and it.will_less == 0]
        if info: logging.debug(f"unidades ranged. {len(units)}.")
        nation.devlog[-1] += [f"unidades ranged. {len(units)}."]
        units.sort(key=lambda x: x.ranking)
        units.sort(key=lambda x: x.mp[0], reverse=True)
        units.sort(key=lambda x: x.ranged, reverse=True)
        for uni in units:
            rnd = uni.ranking * uniform(1.3, 0.7)
            if uni.pos.threat and rnd >= uni.pos.threat: uni.auto_attack()
            if uni.hp_total < 1: continue
            sq = uni.pos.get_near_tiles(1)
            sq = [it for it in sq if uni.can_pass(it)
                  and it != uni.pos and it.threat > 0]
            sq.sort(key=lambda x: x.threat)
            for tl in sq:
                tl.update(uni.nation)
                if tl.threat < 1 or tl in banned: continue
                units = tl.get_free_squads(nation) + tl.get_comm_units(nation)
                [it.update() for it in units]
                if uni.pos.is_city:
                    uni.pos.city.set_defense()
                    if uni.pos.defense < uni.pos.around_threat * 2:
                        if info: logging.debug(f"pocas unidades..")
                        continue
                rnd = uni.ranking * uniform(1.1, 0.9)
                msg = f"initial rnd {rnd}."
                nation.devlog[-1] += [msg]
                if info: logging.debug(msg)
                moves = max(it.moves + it.moves_mod for it in units
                            if nation not in it.belongs)
                rng = max(it.range[1]
                          for it in units if nation not in it.belongs)
                if info: logging.debug(f"rnd inicial {rnd}.")
                if tl.around_threat:
                    rnd *= 0.8
                    msg = f"reduced by around_threat to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.leadership and uni.leads == []:
                    rnd *= 0.6
                    msg = f"reduced by comm to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.dark_vision == 0 and uni.pos.day_night:
                    rnd *= 0.6
                    msg = f"reduced by dark vision."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.forest_survival and tl.surf.name != forest_t:
                    rnd *= 0.8
                    msg = f"reduced by not forest tile to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.swamp_survival and tl.surf.name != swamp_t:
                    rnd *= 0.8
                    msg = f"reduced by not swamp tile to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.mountain_survival and tl.hill == 0:
                    rnd *= 0.8
                    msg = f"reduced by not mountaint tile to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.mounted and tl.surf.name in [forest_t, swamp_t] or tl.hill:
                    rnd *= 0.5
                    msg = f"reduced by forest or hill or swamp to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.forest_survival == 0 and tl.surf.name in [forest_t]:
                    rnd *= 0.5
                    msg = f"reduced by forest to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.swamp_survival == 0 and tl.surf.name in [swamp_t]:
                    rnd *= 0.5
                    msg = f"reduced by swamp to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.mountain_survival == 0 and tl.hill:
                    rnd *= 0.5
                    msg = f"reduced by hill to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if moves > uni.moves + uni.moves_mod:
                    rnd *= 0.7
                    msg = f"reduced by hight moves to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if tl.nation != nation:
                    rnd *= 0.8
                    msg = f"reduced by not nation tile."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if tl.nation != nation and tl.nation:
                    rnd *= 0.8
                    msg = f"reduced by other nation tile to {rnd} and nation."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                max_ranking = max(
                    it.ranking for it in units if nation not in it.belongs)
                if info: logging.debug(
                    f"{uni} rnd {round(rnd)}, trheat {tl.threat}.")
                if info: logging.debug(f"max ranking {max_ranking}.")
                nation.devlog[-1] += [
                    f"{uni} rnd {round(rnd)} max ranking {round(max_ranking)}."]
                nation.devlog[-1] += [f"a threat {tl.around_threat}."]
                if (rnd > max_ranking and tl.defense > tl.around_threat):
                    msg = f"garrison attack to {s} {tl.cords}. "
                    msg += f"rnd {rnd}, threat {tl.threat}, around threat {tl.around_threat}."
                    nation.devlog[-1] += [msg]
                    uni.move_set(tl)
                    uni.move_set("attack")
                    if uni.ranking > (
                        tl.threat + tl.around_threat) * 3: banned += [tl]
                    break

        # Melee garrison.
        units = [it for it in nation.units if it.garrison == 1
                 and it.scout == 0 and it.settler == 0 and it.leadership == 0
                 and it.ranged == 0 and it.mp[0] >= 2
                 and it.pos.around_threat + it.pos.threat and it.will_less == 0]
        if info: logging.debug(f"unidades melee. {len(units)}.")
        nation.devlog[-1] += [f"unidades melee. {len(units)}."]
        shuffle(units)
        units.sort(key=lambda x: x.ranking, reverse=True)
        if basics.roll_dice(1) >= 4: units.sort(key=lambda x: x.pos.is_city)
        for uni in units:
            rnd = uni.ranking * uniform(1.3, 0.7)
            uni.pos.update(nation)
            if rnd >= uni.pos.threat: uni.auto_attack()
            if uni.hp_total < 1: continue
            sq = uni.pos.get_near_tiles(1)
            sq = [it for it in sq if uni.can_pass(it)
                  and it != uni.pos and it.threat > 0]
            sq.sort(key=lambda x: x.threat)
            for s in sq:
                tl.update(nation)
                units = tl.get_free_squads(nation) + tl.get_comm_units(nation)
                [i.update() for i in units]
                if tl.threat < 1 or s in banned: continue
                if uni.pos.is_city:
                    uni.pos.city.set_defense()
                    if uni.pos.defense < uni.pos.around_threat * 1.5:
                        if info: logging.debug(f"pocas unidade..")
                        continue
                nation.devlog[-1] += [f"{uni} in {uni.pos} {uni.pos.cords}."]
                rnd = uni.ranking * uniform(1.1, 0.9)
                msg = f"initial rnd {rnd}."
                nation.devlog[-1] += [msg]
                if info: logging.debug(msg)
                moves = max(it.moves + it.moves_mod for it in units
                            if nation not in it.belongs)
                rng = max(it.ranged for it in units if nation not in it.belongs)
                if info: logging.debug(f"rnd inicial {rnd}.")
                if tl.around_threat:
                    rnd *= 0.8
                    msg = f"reduced by around_threat to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.leadership and uni.leads == []:
                    rnd *= 0.6
                    msg = f"reduced by comm to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.dark_vision == 0 and uni.pos.day_night:
                    rnd *= 0.6
                    msg = f"reduced by dark vision."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.forest_survival and tl.surf.name != forest_t:
                    rnd *= 0.8
                    msg = f"reduced by not forest tile to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.swamp_survival and tl.surf.name != swamp_t:
                    rnd *= 0.8
                    msg = f"reduced by not swamp tile to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.mountain_survival and tl.hill == 0:
                    rnd *= 0.8
                    msg = f"reduced by not mountaint tile to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.mounted and tl.surf.name in [forest_t, swamp_t] or tl.hill:
                    rnd *= 0.5
                    msg = f"reduced by forest or hill or swamp to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.forest_survival == 0 and tl.surf.name in [forest_t]:
                    rnd *= 0.5
                    msg = f"reduced by forest to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.swamp_survival == 0 and tl.surf.name in [swamp_t]:
                    rnd *= 0.5
                    msg = f"reduced by swamp to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if uni.mountain_survival == 0 and tl.hill:
                    rnd *= 0.5
                    msg = f"reduced by hill to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if moves > uni.moves + uni.moves_mod:
                    rnd *= 0.75
                    msg = f"reduced by hight moves to {rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if (rng >= 6 and uni.range[1] < rng
                        and uni.shield == None and uni.armor == None):
                    rnd *= 0.6
                    msg = f"reduced by rng{rnd}."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if tl.nation != nation:
                    rnd *= 0.8
                    msg = f"reduced by not nation tile."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                if tl.nation != nation and tl.nation:
                    rnd *= 0.8
                    msg = f"reduced by other nation tile to {rnd} and nation."
                    nation.devlog[-1] += {msg}
                    if info: logging.debug(msg)
                max_ranking = max(
                    it.ranking for it in units if nation not in it.belongs)
                if info: logging.debug(
                    f"{uni} rnd {round(rnd)}, trheat {tl.threat}.")
                if info: logging.debug(f"max ranking {max_ranking}.")
                nation.devlog[-1] += [
                    f"{uni} rnd {round(rnd)} max ranking {round(max_ranking)}."]
                if (rnd > max_ranking and uni.mp[0] >= 2):
                    if uni.ranking > (
                        max_ranking + tl.around_threat) * 2.5: uni.split(1)
                    elif uni.ranking > (max_ranking + tl.around_threat) * 4: uni.split(1)
                    msg = f"garrison attack to {s} {tl.cords}. "
                    msg += f"rnd {rnd}, threat {tl.threat}, around threat {tl.around_threat}."
                    nation.devlog[-1] += [msg]
                    uni.move_set(tl)
                    uni.move_set("attack")
                    if uni.ranking > (
                        tl.threat + tl.around_threat) * 3: banned += [s]
                    break

    def ai_get_extra_units(self, defense_req, nation):
        logging.info(f"extra unidades. requiere {defense_req}.")
        for ct in nation.cities:
            defense = ct.pos.defense
            logging.debug(
                f"defensa en {ct} {defense.defense} amenaza {ct.pos.around_threat}.")
            for uni in ct.pos.units:
                if ct.pos.defense - uni.ranking > ct.pos.around_threat and defense_req > 0:
                    uni.garrison = 0
                    defense_req -= uni.ranking
                    logging.debug(
                        f"{uni} ya no es guarnición en {ct}. requiere {defense_req}.")

    def ai_commander_moves(self, nation, info=1):
        logging.info(f"commander move for {nation}.")
        units = [it for it in nation.units_comm
                 if it.leadership and it.mp[0] > 0 and it.hp_total >= 1
                 and it.goto == [] and it.check_ready()]
        # checking position threat.
        for uni in units:
            goto = None
            if uni.goto:
                if info: logging.debug(f"check goto for {uni}.")
                for r in range(len(uni.goto) - 1, 0, -1):
                    if isinstance(uni.goto[r][1],
                                  str) == False: goto = uni.goto[r][1]
                if goto and goto.threat + goto.around_threat == 0:
                    msg = f"stops moving to {goto} {goto.cords}."
                    if info: logging.debug(msg)
                    uni.log[-1] += [msg]
                    uni.goto = []

        for uni in units:
            # combat.
            ranking = uni.ranking
            if uni.leadership and uni.leading == 0: ranking = uni.ranking * 0.8
            if uni.pos.threat * 1.2 < ranking:
                uni.auto_attack()

            # moves.
            if uni.pos.nation == uni.nation:
                if info: logging.debug(f"same nation..")
                oportunist_attack = uni.oportunist_attack()
                if any(v < 1 for v in [uni.mp[0], uni.hp_total]): continue
                if oportunist_attack:
                    uni.pos.update(uni.nation)
                    if uni.pos.around_threat > uni.ranking:
                        uni.create_group(uni.leadership - uni.leading)

                threat = (uni.pos.around_threat + uni.pos.threat) * 0.75
                if threat and threat < uni.ranking:
                    msg = f"{uni} will defend. { threat=:} in { uni.pos} {uni.pos.cords}."
                    logging.debug(msg)
                    uni.log[-1] += [msg]
                    continue
                if threat < uni.ranking and uni.pos.public_order <= 70 or uni.pos.unrest >= 15:
                    msg = f"will reduce the unrest or public_order."
                    logging.debug(msg)
                    uni.log[-1] += [msg]
                    continue
                buildings = [bu for bu in uni.pos.buildings
                             if bu.nation in uni.pos.world.random_nations
                             and uni.nation in bu.nations]
                if buildings:
                    # uni.get_hire_units(auto=1)
                    msg = f"will stay until destroy buildings."
                    if info: logging.debug(msg)
                    uni.log[-1] += [msg]
                    continue
                sq = uni.pos.city.tiles
                sq = [it for it in sq
                      if it.get_distance(uni.pos, it) <= ceil(uni.mp[1] / 2)]
                sq = [it for it in sq if uni.can_pass(
                    it) and it.nation == uni.nation]
                sq.sort(key=lambda x: len(x.buildings)
                        and x.defense_req > x.defense, reverse=True)
                sq.sort(key=lambda x: military_t in x.buildings_tags
                        and x.defense_req > x.defense, reverse=True)
                sq.sort(key=lambda x: x.public_order)
                if "healer" in uni.spells_tags: sq.sort(
                    key=lambda x: intoxicated_t in x.units_effects)
                uni_food = uni.pos.food_need
                if info:
                    logging.debug(f"casillas {len(sq)}.")
                    logging.debug(f"{uni_food=:}.")
                for it in sq:
                    if info:
                        msg = f"""{it} {it.cords}. {it.food_need=:}, {it.food=:}, 
            {it.defense=:}, {it.around_threat+it.threat=:}."""
                        uni.log[-1] += [msg]
                        logging.debug(msg)
                    if (uni.food_total + it.food_need > it.food
                            and it.defense + 1 > it.around_threat + it.threat):

                        if info:
                            msg = f"not enoug food."
                            uni.log[-1] += [msg]
                            logging.debug(msg)
                        continue
                    if it.around_threat + it.threat < it.defense + 1:
                        if info:
                            msg = f"city {it.city} but there is not threat."
                            uni.log[1] += [msg]
                            logging.debug(msg)
                        continue
                    if uni.ranking + it.defense > it.around_threat:
                        if uni.pos != it:
                            msg = f"""free move to {it} {it.cords}. 
              defense {it.defense}, around threat {it.around_threat}."""
                            if info: logging.debug(msg)
                            uni.log[-1] += [msg]
                        uni.move_set(it)
                        uni.move_set("attack")
                        break

            # return to home.
            elif uni.pos.nation != uni.nation and uni.goal == None:
                if info: logging.debug(f"out of nation.")
                num = 1
                tries = 6
                num += 1
                while True:
                    sq = uni.pos.get_near_tiles(num)
                    uni.set_favland(sq)
                    if info: logging.debug(f"tiles {len(sq)} num {num}.")
                    tries -= 1
                    if tries < 1: Pdb().set_trace()
                    for it in sq:
                        threat = it.around_threat + it.threat
                        if info:
                            msg = f"""{uni} ranking {uni.ranking}. threat {threat}.
              {tries=:}."""
                            logging.debug(msg)
                        if uni.ranking + it.defense > threat and it.nation in uni.belongs:
                            uni.move_set(it)
                            return

    def nation_play(self, nation, info=0):
        logging.info(
            f"{turn_t} {of_t} {nation}. ai = {nation.ai}, info = {nation.show_info}.")
        init = time()
        if dev_mode: sp.speak(f"{nation}.")
        # nation population changes.
        [city.population_change()
         for city in nation.cities if city.pos.world.turn > 1]
        # nation income.
        if nation.pos.world.turn > 1: nation.set_income()
        if info: logging.debug(f"{nation} nation.set_income {time()-init}.")
        nation.set_hidden_buildings()

        # cities.
        [city.check_events() for city in nation.cities]
        [city.set_downgrade() for city in nation.cities]
        [city.set_upgrade() for city in nation.cities]
        [city.check_training() for city in nation.cities]
        [city.check_building() for city in nation.cities]
        [city.status() for city in nation.cities]
        [city.set_seen_units(new=1) for city in nation.cities]
        [city.set_av_units() for city in nation.cities]
        if info: logging.debug(f"cities {time()-init}.")
        print(f"ready.")
        nation.set_income()

        # units.
        logging.debug(f"movimiento de unidades.")
        nation.update(scenary)
        nation.units.sort(key=lambda x: x.leadership == 0, reverse=True)
        for uni in nation.units:
            uni.unit_new_turn()
        if info: logging.debug(f"units {time()-init}.")

        # actualizar vista.
        if nation.map == []:
            nation.pos.map_update(nation, scenary)
        else:
            nation.pos.map_update(nation, nation.map)
        if info: logging.debug(f"nation updates {time()-init}.")
        nation.set_seen_nations()
        if info: logging.debug(f"seen nations {time()-init}.")
        # parametros de casillas cercanas.
        set_near_tiles(nation, scenary)
        # initial placement.
        # if nation.cities == [] and world.turn == 1:
        # nation_start_placement(nation)
        # nation.update(nation.map)
        # colonos.
        logging.debug(f"colonos {len([i for i in nation.units if i.settler])}.")
        [set_settler(it) for it in nation.units
         if it.settler and it.leader == None]
        # liberar unidades de edificios que no son amenazados.
        self.set_free_units(nation)
        if info: logging.debug(f"ai_set_free units {time()-init}.")
        # entrenar colonos.
        self.ai_add_settler(nation)
        if info: logging.debug(f"ai_add_settler {time()-init}.")
        # train commanders
        self.ai_train_comm(nation)
        if info: logging.debug(f"ai_train_comm {time()-init}.")
        # entrenar unidades.
        self.ai_train(nation)
        if info: logging.debug(f"ai_train {time()-init}.")
        # edificios.
        [nation.improve_military(ct) for ct in nation.cities]
        if info: logging.debug(f"improve_military {time()-init}.")
        [nation.set_new_buildings(ct) for ct in nation.cities]
        if info: logging.debug(f"nation.build {time()-init}.")
        [nation.improve_misc(ct) for ct in nation.cities]
        if info: logging.debug(f"nation.improve_misc {time()-init}.")
        [nation.improve_food(ct) for ct in nation.cities]
        if info: logging.debug(f"nation.improve_food {time()-init}.")
        # expandir ciudad.
        for ct in nation.cities: self.ai_expand_city(ct)
        if info: logging.debug(f"expand city {time()-init}.")
        # setup commander.
        nation.setup_commanders()
        if info: logging.debug(f"setup_commanders {time()-init}.")
        # agregar exploradores.
        self.ai_add_explorer(nation)
        if info: logging.debug(f"ai_add_explorer {time()-init}.")
        # asignar unidades a proteger casillas.
        self.ai_protect_tiles(nation)
        if info: logging.debug(f"ai_protect_tiles {time()-init}.")
        # commander.
        self.ai_commander_moves(nation)
        if info: logging.debug(f"ai_hero_moves {time()-init}.")
        self.ai_unit_cast(nation)
        if info: logging.debug(f"ai_unit_cast {time()-init}.")
        # acciones de unidades en guarnición.
        self.ai_garrison(nation)
        if info: logging.debug(f"ai_garrison {time()-init}.")
        # explorar
        self.ai_explore(nation, scenary)
        if info: logging.debug(f"ai_explore {time()-init}.")
        # atacar.
        self.ai_attack(nation)
        if info: logging.debug(f"ai_attack {time()-init}.")
        # grupos.
        self.ai_free_groups(nation)
        if info: logging.debug(f"ai_free_group {time()-init}.")
        # unidades libres.
        self.ai_free_units(nation, scenary)
        if info: logging.debug(f"ai_free_units {time()-init}.")
        # commander move again.
        self.ai_commander_moves(nation)
        if info: logging.debug(f"ai_hero_moves {time()-init}.")
        self.ai_unit_cast(nation)
        if info: logging.debug(f"ai_unit_cast {time()-init}.")
        # setup commander again.
        nation.setup_commanders()
        # desbandando unidades.
        self.ai_unit_disband(nation)
        if info: logging.debug(f"ai_disband {time()-init}.")

    def ai_protect_tiles(self, nation, info=1):
        logging.info(f"proteger casillas {nation} turno {world.turn}..")
        nation.devlog[-1] += [f"protect tiles."]
        init = time()
        shuffle(nation.tiles)
        [i.set_around(nation) for i in nation.tiles]
        nation.set_tiles_defense()
        nation.tiles.sort(key=lambda x: x.hill, reverse=True)
        nation.tiles.sort(key=lambda x: len(x.around_nations) > 0, reverse=True)
        nation.tiles.sort(key=lambda x: x.defense_req, reverse=True)
        nation.tiles.sort(
            key=lambda x: military_t in x.buildings_tags, reverse=True)
        nation.tiles.sort(key=lambda x: x.around_threat +
                          x.threat, reverse=True)
        nation.tiles.sort(
            key=lambda x: x.is_city and x.around_threat + x.threat, reverse=True)
        nation.tiles.sort(
            key=lambda x: x.city.capital and x.is_city and x.around_threat + x.threat, reverse=True)
        for tl in nation.tiles:
            if tl.blocked: continue
            defense_needs = tl.around_threat
            if tl.is_city: defense_needs *= 1.5
            if tl.defense_req > defense_needs: defense_needs = tl.defense_req
            defense = sum(uni.ranking for uni in tl.units
                          if nation in uni.belongs and uni.goto == []
                          and uni.leader == None)
            if defense < 80 * defense_needs / 100:
                if info:
                    msg1 = f"{tl}. {tl.cords} needs {defense_needs-defense} defense."
                    logging.debug(msg1)
                    nation.devlog[-1] += [msg1]
                units = []
                ranking = 0
                if tl.is_city == 0: sq = tl.get_near_tiles(1)
                elif tl.is_city == 0 and tl.capital: sq = tl.get_near_tiles(2)
                elif tl.is_city: sq = tl.get_near_tiles(3)
                sq = [s for s in sq if s != tl and s.units]
                [i.set_around(nation) for i in sq]
                sq.sort(key=lambda x: x.get_distance(x, tl))
                sq.sort(key=lambda x: x.hill)
                sq.sort(key=lambda x: x.around_threat + x.threat)
                for s in sq:
                    if ranking >= 80 * defense_needs / 100:
                        nation.devlog[-1] += [f"breaks tile checking by 80% defense."]
                        break
                    if s.units and info:
                        msg2 = f"""checking units in {s} {s.cords} 
            {s.around_threat=:}, {s.threat=:}."""
                        nation.devlog[-1] += [msg2]
                    for uni in s.units:
                        if nation not in uni.belongs or uni.settler: continue
                        if uni.will_less and s != tl: continue
                        if uni. leader or uni.scout or uni.goto: continue
                        if uni.check_ready() == 0 or uni.mp[0] < 2: continue
                        if ranking >= 80 * defense_needs / 100:
                            if info:
                                msg = f"breaks unit checking by 80% defense."
                                nation.devlog[-1] += [msg]
                                logging.debug(msg)
                            break
                        if info:
                            msg = f"""{uni}, garrison {uni.garrison}, mp {uni.mp}."""
                            nation.devlog[-1] += [msg]
                            logging.debug(msg)
                            uni.log[-1] += [f"{msg1} {msg2} {msg}"]
                        if uni.goal:
                            if info:
                                msg = f"continues by unit has goal."
                                uni.log[-1] += [msg]
                                nation.devlog[-1] += [msg]
                                logging.debug(msg)
                            continue
                        if uni.leadership and tl.is_city and tl.around_threat + tl.threat < 1:
                            if info:
                                msg = f"continues by unit is comm and tile is city but no threats."
                                uni.log[-1] += [msg]
                                nation.devlog[-1] += [msg]
                                logging.debug(msg)
                            continue
                        if s.is_city and s.city.capital and s.around_threat + s.threat:
                            if info:
                                msg = f"breaks by threat in capital."
                                uni.log[-1] += [msg]
                                nation.devlog[-1] += [msg]
                                logging.debug(msg)
                            continue
                        if (tl.is_city and tl.around_threat + tl.threat == 0
                                and s.around_threat + s.threat and uni.garrison):
                            if info:
                                msg = f"breaks by threat."
                                uni.log[-1] += [msg]
                                nation.devlog[-1] += [msg]
                                logging.debug(msg)
                            continue
                        if s.is_city and uni.garrison and len(uni.pos.units) < 2:
                            if info:
                                msg = f"breaks by city less than 3 garrison.."
                                uni.log[-1] += [msg]
                                nation.devlog[-1] += [msg]
                                logging.debug(msg)
                            continue
                        if tl.is_city == 0 and s.around_threat + s.threat and uni.garrison:
                            if info:
                                msg = f"breakcs by unit defending."
                                uni.log[-1] += [msg]
                                nation.devlog[-1] += [msg]
                                logging.debug(msg)
                            continue
                        if tl.is_city == 0 and tl.around_threat + tl.threat == 0 and uni.garrison:
                            if info:
                                msg = f"breakcs by not need defense"
                                uni.log[-1] += [msg]
                                nation.devlog[-1] += [msg]
                                if info: logging.debug(msg)
                            continue
                        if tl.is_city == 0 and uni.pos.city != tl.city and uni.garrison:
                            if info:
                                msg = f"breakcs by unit not same city."
                                uni.log[-1] += [msg]
                                nation.devlog[-1] += [msg]
                                logging.debug(msg)
                            continue
                        buildings = [bu for bu in s.buildings
                                     if bu.nation in s.world.random_nations]
                        if tl.around_threat + tl.threat < 1 and buildings:
                            if info:
                                msg = f"destroying enemy building."
                                uni.log[-1] += [msg]
                                nation.devlog[-1] += [msg]
                                logging.debug(msg)
                            continue
                        if tl.around_threat + tl.threat < 1 and s.unrest >= 15:
                            if info:
                                msg = f"unit is reducing unrest."
                                uni.log[-1] += [msg]
                                nation.devlog[-1] += [msg]
                                logging.debug(msg)
                            continue
                        if tl.around_threat + tl.threat < 1 and s.public_order < 50:
                            if info:
                                msg = f"unit is reducing public order."
                                uni.log[-1] += [msg]
                                nation.devlog[-1] += [msg]
                                logging.debug(msg)
                            continue
                        if (uni.food_total + tl.food_need > tl.food
                                and tl.around_threat + tl.threat < tl.defense):
                            if info:
                                msg = f"not enough food."
                                uni.log[-1] += [msg]
                                nation.devlog[-1] += [msg]
                                logging.debug(msg)
                            continue
                        buildings = [bu for bu in s.buildings
                                     if bu.nation == nation and military_t in bu.tags]
                        if buildings and tl.around_threat + tl.threat < tl.defense:
                            if info:
                                msg = f"defending military buildings."
                                uni.log[-1] += [msg]
                                nation.devlog[-1] += [msg]
                                logging.debug(msg)
                            continue
                        units += {uni}
                        ranking += uni.ranking
                        nation.devlog[-1] += [f"added."]
                if info:
                    msg = f"""{len(units)} unidades disponibles iniciales. 
          ranking total {ranking}."""
                    logging.debug(msg)
                if units == []: continue
                units.sort(key=lambda x: tl.food_need +
                           x.food_total <= tl.food, reverse=True)
                if tl.surf.name == forest_t:
                    units.sort(
                        key=lambda x: x.forest_survival or x.ranged, reverse=True)
                    if info: logging.debug(f"sort to forest.")
                if tl.surf.name == swamp_t:
                    units.sort(
                        key=lambda x: x.swamp_survival or x.ranged, reverse=True)
                    if info: logging.debug(f"sort to swamp.")
                if tl.hill:
                    units.sort(
                        key=lambda x: x.mountain_survival or x.ranged, reverse=True)
                    if info: logging.debug(f"sort to hill.")
                if tl.surf.name in [forest_t, swamp_t] or tl.hill:
                    units.sort(key=lambda x: x.mounted)
                    units.sort(key=lambda x: x.can_fly, reverse=True)
                    if info: logging.debug(f"sort by not mounted.")
                units.sort(key=lambda x: x.pos.get_distance(x.pos, tl))
                nation.devlog[-1] += [
                    f"defense {defense} needs {defense_needs}, ranking {ranking}."]
                for uni in units:
                    if uni.pos == tl and uni.garrison: continue
                    if defense > defense_needs:
                        if info:
                            nation.devlog[-1] += [f"defense > defense_need."]
                        break
                    uni.log[-1] += [f"protect tile at {tl} {tl.cords}."]
                    if (uni.food_total > tl.food
                            and tl.around_threat + tl.threat <= tl.defense):
                        if info: uni.log[-1] += [f"lack of food and not threat found."]
                        continue
                    if defense + uni.ranking > defense_needs * 1.2 and tl.around_threat + tl.threat == 0:
                        uni.split((1))
                        msg = f"splited."
                        if info: logging.debug(msg)
                        nation.devlog[-1] += [msg]
                    defense += uni.ranking
                    if uni.garrison:
                        uni.garrison = 0
                        uni.scout = 0
                        msg = f"{uni} leaves garrison on {uni.pos} {uni.pos.cords}."
                        uni.log[-1] += [msg]
                        nation.devlog[-1] += [msg]
                        if info: logging.debug(msg)
                    msg = f"{uni} de {uni.pos.cords} defenderá {tl} {tl.cords}."
                    if info: logging.debug(msg)
                    nation.devlog[-1] += [msg]
                    uni.log[-1] += [msg]
                    msg = f"defensa {defense} needs {defense_needs}."
                    logging.debug(msg)
                    nation.devlog[-1] += [msg]
                    uni.log[-1] += [msg]
                    if uni.pos != tl:
                        uni.move_set(tl)
                        uni.move_set("gar")
                    elif uni.pos == tl:
                        uni.gar = 1
                        if info:
                            msg = f"set to garrison"
                            uni.log[-1] += [msg]
                            nation.devlog[-1] += [msg]
                            logging.debug(msg)

        if info: logging.debug(f"time elapses. {time()-init}.")

    def set_free_units(self, nation, req=0):
        logging.info(f"set_free_units. {nation}")
        nation.devlog[-1] += [f"ai set free units."]
        init = time()

        for t in nation.tiles:
            # if t.is_city: continue
            units = [u for u in t.units if nation in u.belongs and u.garrison
                     and u.leader == None]
            defense = sum(u.ranking for u in units if u.garrison)
            defense_need = max(t.defense_req, t.around_threat + t.threat)
            if defense > defense_need: continue
            if t.surf.name in [forest_t, swamp_t] or t.hill:
                units.sort(key=lambda x: x.ranged)
            for uni in units:
                if defense > defense_need * 4: uni.split(3)
                elif defense > defense_need * 3: uni.split(2)
                elif defense > defense_need * 1.5: uni.split(1)
                if defense - uni.ranking >= defense_need:
                    uni.garrison = 0
                    defense -= uni.ranking
                    msg = f"{uni} es ahora libre de {t} {t.cords}."
                    logging.debug(msg)
                    nation.devlog[-1] += [msg]
                    uni.log[-1] += [msg]

        logging.debug(f"time elapses. {time()-init}.")

    def ai_train(self, nation):
        logging.info(f"entrenamiento {nation}. turno {world.turn}.")
        init = time()
        nation.update(nation.map)
        for ct in nation.cities:
            logging.debug(f"{ct}.")
            if ct.production: continue
            if ct.commander_request:
                if ct.pop_percent < 40 and ct.defense_total_percent >= 100: continue
                logging.debug(f"can not train units due to commander request.")
                continue
            ct.set_seen_units()
            upkeep_limit = nation.upkeep_limit
            logging.debug(f"upkeep_limit ={upkeep_limit}.")
            units = [it(nation) for it in ct.all_av_units if it.settler ==
                     0 and it.leadership == 0]
            ct.set_defense()
            if ct.defense_total < ct.defense_min:
                logging.debug(f"amenaza mayor.")
                upkeep_limit = nation.upkeep * 1.5
                logging.debug(f"upkeep increased to {upkeep_limit}.")
            logging.debug(f"amenaza {ct.seen_threat}.")
            logging.debug(f"defense_total_percent. {ct.defense_total_percent}")
            logging.debug(
                f"military limit. {ct.military_percent} de {ct.military_limit}.")
            units = ct.set_train_type(units)
            if ct.defense_total_percent >= 150:
                roll = basics.roll_dice(1)
                if roll >= 5: units.sort(
                    key=lambda x: x.off + x.off_mod, reverse=True)
                elif roll >= 3: units.sort(key=lambda x: x.dfs + x.dfs_mod, reverse=True)
                else: units.sort(key=lambda x: x.resolve + x.resolve_mod, reverse=True)
            logging.debug(f"entrenables {len(units)}.")

            if ct.defense_total_percent >= 100 and ct.military_percent > ct.military_limit:
                logging.debug(f"military limit.")
                units = [i for i in units if i.pop == 0]
            logging.debug(f"entrenables {[i.name for i in units]}.")
            for uni in units:
                if req_unit(uni, nation, ct):
                    logging.debug(f"suma upkeep {nation.upkeep+uni.upkeep }.")
                    if uni.upkeep and nation.upkeep + uni.upkeep > upkeep_limit:
                        logging.debug(
                            f"exceeds upkeep limit of {nation.upkeep_limit}.")
                        continue
                    ct.train(uni)
                    break

        logging.debug(f"time elapses. {time()-init}.")

    def ai_train_comm(self, nation, info=1):
        logging.info(f"ai_train_comm {nation} turn {world.turn}.")
        nation.update(nation.map)
        units = sum([i.units for i in nation.units
                     if i.leader == None and i.leadership == 0
                     and i.settler == 0])
        comms = sum(com.leadership - com.leading for com in nation.units_comm)
        if info: logging.debug(f"{units=:}, {comms=:}.")
        if units - comms > 40 or comms == 0:
            for ct in nation.cities:
                if ct.production: continue
                # ct.update()
                logging.debug(f"{ct.defense_total_percent =: }.")
                if ct.pop_percent < 40 and ct.defense_total_percent >= 100: continue
                ct.commander_request = 1
                units = [it(nation) for it in ct.all_av_units if it.leadership]
                shuffle(units)
                logging.debug(f"available commanders {len(units)}.")
                for uni in units:
                    if nation.upkeep + uni.upkeep > nation.upkeep_limit:
                        logging.debug(
                            f"exceds the upkeep limit {nation.upkeep_limit}.")
                        break
                    if req_unit(uni, nation, ct):
                        logging.debug(
                            f"{uni} suma upkeep {nation.upkeep+uni.upkeep }.")
                        ct.train(uni)
                        ct.commander_request = 0
                        break
        else:
            logging.debug(f"not comm need.")
            for ct in nation.cities:
                ct.commander_request = 0

    def ai_unit_cast(self, nation, info=0):
        logging.info(f"commander cast.")
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
                    if info: logging.debug(spl.name)
                    init = spl.ai_run(uni)
                    if init != None:
                        uni.log[-1] += [init]
                        logging.debug(init)
                        banned += [spl.name]
                        break

    def ai_unit_disband(self, nation):
        logging.info(f"ai_unit_disband.")
        if nation.income < nation.upkeep and nation.gold < nation.upkeep * 1.5:
            logging.debug(
                f"nation income{nation.income}. upkeep {nation.upkeep}. gold {nation.gold}.")
            units = [i for i in nation.units if i.upkeep > 0 and i.leadership == 0
                     and i.goto == []]
            units.sort(key=lambda x: x.ranking,)
            if units: uni = units[0]

            uni.update()
            uni.split(5)
            uni.disband()
            logging.debug(f"{uni} disuelta.")

# funciones.


def create_building(city, items, sound="in1"):
    sleep(loadsound(sound) / 2)
    say = 1
    sp.speak(f" {build_t}.")
    x = 0
    while True:
        sleep(0.001)
        if say:
            itm = items[x](nation, pos)
            time_cost = ceil(itm.resource_cost[1] / city.resource_total)
            sp.speak(f"{itm} {in_t} {time_cost} {turns_t}.")
            sp.speak(f"{cost_t} {itm.gold}.")
            say = 0

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    if isinstance(items[x](nation, nation.pos), Building): item_info(
                        items[x](nation, nation.pos), nation)
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
                if event.key == pygame.K_F12 and ctrl and shift:
                    sp.speak(f"debug on.", 1)
                    Pdb().set_trace()
                    sp.speak(f"debug off.", 1)
                if event.key == pygame.K_ESCAPE:
                    sleep(loadsound("back1") / 2)
                    return


def destroy_city(city):
    city.nation.cities.remove(city)
    for t in city.tiles:
        t.city = None
        t.nation = None
        t.buildings = []


def end_parameters(sound="unselected1"):
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


def error(info=0, msg="", sound="errn1", slp=0):
    if info == 1:
        sleep(loadsound(sound) * 0.5)
        sp.speak(msg, 1)
    logging.debug(msg)


def exit_game():
    sp.speak(f"sale")
    sleep(0.001)
    sys.exit()


def expand_city(city, pos):
    cost = get_tile_cost(city, pos)
    if city.nation.gold >= cost and pos not in city.tiles:
        city.tiles.append(pos)
        pos.city = city
        pos.nation = city.nation
        city.nation.gold -= cost
        msg = f"{city} se expandió a {pos} {pos.cords}."
        speak(msg, num=1)
        sleep(loadsound("gold1") * 1.5)
        return True
    else:
        error(msg="ínsuficiente oro o la casilla es propia.")
        return False


def get_item2(items1=[], items2=[], msg="", name=None, simple=0, sound="in1"):
    x = 0
    if all(i == [] for i in [items1, items2]):
        error(info=1)
        return
    if sound: sleep(loadsound(sound) / 2)
    say = 1
    sp.speak(msg, 1)
    while True:
        sleep(0.011)
        if say:
            if items2: sp.speak(items2[x])
            else:
                if name == None and simple == 0: sp.speak(
                    items1[x](nation, pos).name, 1)
                elif name and simple:
                    sp.speak(items1[x].name, 1)
                    sp.speak(items1[x].id, 1)
            say = 0
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
                items1[x](nation, nation.pos).info()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                x = basics.selector(items1, x, go="up")
                say = 1
            if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                x = basics.selector(items1, x, go="down")
                say = 1
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                sp.speak(msg, 1)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                sleep(loadsound("back3") / 2)
                if items2: return x
                else:
                    if simple == 0: return items1[x](nation, pos)
                    elif simple: return items1[x]
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_F12 and ctrl
                    and shift):
                sp.speak("on", 1)
                Pdb().set_trace()
                sp.speak("off", 1)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                loadsound("back3")
                sleep(0.001)
                return


def get_tile_cost(city, pos):
    cost = city.nation.tile_cost
    distance = pos.get_distance(pos, city.pos)
    cost = cost ** (city.nation.tile_power + distance / 10)
    return round(cost, 2)


def hero_set_group(itm):
    if itm.leads == []:
        if itm.pos.nation == itm.nation and itm.pos.city:
            itm.create_group(itm.ranking // 2)


def info_tile(pos, nation, sound="in1"):
    sleep(loadsound(sound) / 2)
    say = 1
    x = 0
    while True:
        sleep(0.001)
        if say:
            if pos.corpses == []: corpses = ["no."]
            else: corpses = []
            for i in pos.corpses:
                corpses += [f"{i}: {round(sum(i.deads))}"]
            items = [
                f"{corpses_t} {[str(it) for it in corpses]}",
                f"{pos}",
                f"{buildings_t} {len(pos.buildings)}, {units_t} {len(pos.units)}.",
                f"{population_t} {round(pos.pop,1)}, {public_order_t} {round(pos.public_order,1)}.",
                f"{income_t} {round(pos.income,1)}.",
                f"{food_t} {pos.food}. {resources_t} {pos.resource}.",
                f"{defense_t} {pos.defense}.",
                f"{grouth_t} {pos.grouth}.",
                f"{size_t} {pos.size}, {pos.size_total}%.",
                f"{cost_t} {pos.cost}.",
            ]

            sp.speak(f"{items[x]}")
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
                if event.key == pygame.K_F12 and ctrl and shift:
                    sp.speak(f"debug on.", 1)
                    Pdb().set_trace()
                    sp.speak(f"debug off.", 1)
                if event.key == pygame.K_ESCAPE:
                    sleep(loadsound("back1") / 2)
                    return


def item_info(itm, nation):
    if itm.type == building_t:
        itm.info()
    elif itm.type in ["beast", "civil", "cavalry", "infantry"]:
        itm.info(nation)


def loading_map(location, filext, saved=0, sound="book_open01"):
    global east, height, ext, name, pos, scenary, west, width, world
    sleep(loadsound(sound))
    x = 0
    say = 1
    loop = 1
    maps = glob(os.path.join(location + filext))
    maps = natsort.natsorted(maps)
    while loop:
        sleep(0.001)
        if say:
            say = 0
            if maps:
                sp.speak(maps[x][int(maps[0].rfind("\\")) + 1:-4], 1)
            else:
                sp.speak(empty_t, 1)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    maps = natsort.natsorted(maps)
                    sp.speak(f"sort by recent date time.", 1)
                    say = 1
                if event.key == pygame.K_2:
                    maps.sort(key=os.path.getctime, reverse=True)
                    sp.speak(f"sort by recent date time.", 1)
                    say = 1
                if event.key == pygame.K_3:
                    maps.sort(key=os.path.getctime,)
                    sp.speak(f"sort previews by date time.", 1)
                    say = 1
                if event.key == pygame.K_UP:
                    x = basics.selector(maps, x, go="up")
                    say = 1
                if event.key == pygame.K_DOWN:
                    x = basics.selector(maps, x, go="down")
                    say = 1
                if event.key == pygame.K_HOME:
                    x = 0
                    loadsound("s1")
                    say = 1
                if event.key == pygame.K_END:
                    x = len(maps) - 1
                    loadsound("s1")
                    say = 1
                if event.key == pygame.K_PAGEUP:
                    x -= 10
                    if x < 0: x = 0
                    loadsound("s1")
                    say = 1
                if event.key == pygame.K_PAGEDOWN:
                    x += 10
                    if x >= len(maps): x = len(maps) - 1
                    loadsound("s1")
                    say = 1
                if event.key == pygame.K_RETURN:
                    if maps:
                        file = open(maps[x], "rb")
                        world = pickle.loads(file.read())

                        height = world.height
                        width = world.width
                        east = world.east
                        west = world.west
                        ext = ".map"
                        pos = world.map[0]
                        scenary = world.map
                        return
                    else:
                        sp.speak(empty_t, 1)
                        loadsound("errn1")
                if event.key == pygame.K_ESCAPE:
                    return


def map_init():
    global east, ext, height, name, pos, scenary, west, width, world

    world = World()
    ext = ".map"
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
            t.cords = f"({t.x}, {t.y})"
            x += 1
        starting += width
        num += 1
        ending *= num
        y += 1


def menu_building(pos, nation, sound="in1"):
    [i.update(nation) for i in nation.map]
    pos.pos_sight(nation, nation.map)
    items = [i for i in pos.buildings if i.nation ==
             nation or nation in i.nations]
    items.insert(0, f"{build_t}")
    if pos.city: pos.city.update()
    sleep(loadsound(sound) / 2)
    say = 0
    sp.speak(f"{buildings_t}.")
    x = 0
    while True:
        sleep(0.001)
        if say:
            items = [i for i in pos.buildings if i.nation ==
                     nation or nation in i.nations]
            items.insert(0, f"{build_t}")
            if x >= len(items): x = len(items) - 1
            if isinstance(items[x], str): sp.speak(f"{items[x]}.")
            else:
                if items[x].resource_cost[0] == items[x].resource_cost[1]:
                    sp.speak(f"{items[x]} ({items[x].type}).")
                else:
                    sp.speak(f"{items[x]} ({items[x].type}).")
                    itm = items[x]
                    time_cost = (
                        itm.resource_cost[1] - itm.resource_cost[0]) / pos.city.resource_total
                    time_cost = ceil(time_cost)
                    sp.speak(
                        f"{int(items[x].resource_cost[0]/items[x].resource_cost[1]*100)}%.")
                    if items[x].nation == nation: sp.speak(
                        f"{in_t} {time_cost} {turns_t}.")
            say = 0

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    if isinstance(items[x], str) == False: items[x].info()
                if event.key == pygame.K_u:
                    if pos.blocked:
                        loadsound("errn1")
                        continue
                    if isinstance(items[x], str) == False and items[x].is_complete and items[x].upgrade:
                        item = get_item2(items1=items[x].upgrade, msg="mejorar")
                        if item:
                            if item.check_tile_req(pos):
                                if item.gold > nation.gold:
                                    loadsound("errn1")
                                    return
                                items[x].improve(item)
                                say = 1
                            else: sleep(loadsound("errn1"))
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
                    if (items[x].type == city_t
                        or items[x].resource_cost[0] == items[x].resource_cost[1]
                            or items[x].pos.blocked):
                        loadsound("errn1")
                        continue
                    items[x].pos.buildings.remove(items[x])
                    items[x].nation.gold += items[x].gold
                    sleep(loadsound("set7") // 2)
                if event.key == pygame.K_RETURN:
                    # construir.
                    if pos.blocked:
                        loadsound("errn1")
                        continue
                    if isinstance(items[x], str) and pos.city and pos.nation == nation:
                        building = create_building(
                            pos.city, nation.av_buildings)
                        if building:
                            if building.can_build() == 0:
                                continue
                            pos.city.add_building(building, pos)
                        items += [i for i in pos.buildings if i not in items]
                        say = 1
                if event.key == pygame.K_DELETE:
                    pass
                if event.key == pygame.K_F12 and ctrl and shift:
                    sp.speak(f"debug on.", 1)
                    Pdb().set_trace()
                    sp.speak(f"debug off.", 1)
                if event.key == pygame.K_ESCAPE:
                    sleep(loadsound("back1") / 2)
                    return


def menu_city(itm, sound="in1"):
    global city, filter_expand
    loadsound(sound)
    itm.update()
    itm.nation.update(nation.map)
    say = 1
    x = 0
    while True:
        sleep(0.001)
        if say:
            prod = empty_t
            grouth = round(itm.food_total * 100 / itm.pop - 100, 1)
            if itm.production:
                progress = int(ceil(itm.prod_progress / itm.resource_total))
                prod = f"{itm.production[0]} {in_t} {progress} {turns_t}."
            lista = [
                f"{itm.nick}, {itm.name}.",
                f"{training_t} {prod}",
                f"{food_t} {itm.food_need} {of_t} {itm.food_total} ({grouth}%).",
                f"{resources_t} {itm.resource_total}.",
                f"{buildings_t} {len(itm.buildings)}.",
                f"{income_t} {itm.income_total}, {upkeep_t} {itm.upkeep}, {total_t} {itm.income_total-itm.upkeep}.",
                f"{public_order_t} {round(itm.public_order_total, 1)}.",
                f"{grouth_t} {round(itm.grouth_total,2)}.",
                f"{population_t} {itm.pop}, ({itm.pop_percent}%).",
                f"{military_t} {itm.pop_military}, ({itm.military_percent}%).",
                f"total {int(itm.pop_total)}.",
                f"{size_t} {len(itm.tiles)}.",
            ]

            sp.speak(lista[x])
            say = 0

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1 and dev_mode:
                    sp.speak(f"defense total {itm.defense_total}.", 1)
                    sp.speak(
                        f"defense total percent {itm.defense_total_percent}.")
                    sp.speak(f"defense_min {itm.defense_min}.")
                if event.key == pygame.K_F2 and dev_mode:
                    sp.speak(f"seen threat {itm.seen_threat}.", 1)
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
                if event.key == pygame.K_TAB and dev_mode:
                    view_log(nation.devlog, nation)
                if event.key == pygame.K_RETURN:
                    if training_t in lista[x]:
                        all_av_units = [i for i in itm.all_av_units]
                        all_av_units.sort(key=lambda x: x.resource_cost)
                        item = train_unit(itm, all_av_units, msg="entrenar")
                        if item:
                            itm.train(item)
                            itm.update()
                            itm.nation.update(scenary)
                    if size_t in lista[x]:
                        filter_expand = 1
                        city = itm
                        loadsound("set5")
                        return
                if event.key == pygame.K_DELETE:
                    if training_t in lista[x]:
                        if itm.production:
                            itm.add_pop(itm.production[0].total_pop)
                            if itm.production[0].gold > 0:
                                itm.nation.gold += itm.production[0].gold
                            del(itm.production[0])
                            if itm.production:
                                itm.prod_progress = itm.production[0].resource_cost
                            loadsound("set1")
                            sp.speak(f"{deleted_t}.")
                            itm.update()
                            itm.nation.update(scenary)
                if event.key == pygame.K_F12 and ctrl and shift:
                    sp.speak(f"debug on.", 1)
                    Pdb().set_trace()
                    sp.speak(f"debug off.", 1)
                if event.key == pygame.K_ESCAPE:
                    sleep(loadsound("back1") / 2)
                    return


def menu_nation(nation, sound="book_open01"):
    global sayland
    nation.set_seen_nations()
    [ct.update() for ct in nation.cities]
    nation.update(nation.map)
    nation.status()
    sleep(loadsound(sound) * 0.5)
    x = 0
    nations = [nation]
    nations += nation.seen_nations
    say = 1
    while True:
        sleep(0.001)
        if say:
            sp.speak(f"{nations[x]}", 1)
            sp.speak(f"{ranking_t} {nations[x].score}.")
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
                if event.key == pygame.K_1 and dev_mode:
                    sp.speak(f"scouts {len(nations[x].units_scout)}", 1)
                    sp.speak(f"comms {len(nations[x].units_comm)}")
                if event.key == pygame.K_2 and dev_mode:
                    sp.speak(
                        f"build military path {nation.path.build_military}", 1)
                    sp.speak(f"build food path {nation.path.build_food}")
                    sp.speak(
                        f"upkeep_limit {nation.upkeep} of {nation.upkeep_limit}.")
                if event.key == pygame.K_3 and dev_mode:
                    sp.speak(
                        f"{nation.defense_mean=:}, {nation.attack_factor=:}.")
                    sp.speak(
                        f"stalk rate {nation.defense_mean/nation.stalk_rate}.")
                    sp.speak(
                        f"capture rate {nation.defense_mean/nation.capture_rate}.")
                if event.key == pygame.K_4 and dev_mode:
                    stalk = 0
                    capture = 0
                    for uni in nation.units:
                        if uni.goal == capture: capture += 1
                        if uni.goal == stalk_t: stalk += 1
                    sp.speak(f"{capture=:}, {stalk=:}.", 1)
                if event.key == pygame.K_F12 and ctrl and shift:
                    sp.speak(f"pdb on.")
                    Pdb().set_trace()
                    sp.speak(f"debug off.", 1)
                if event.key == pygame.K_ESCAPE:
                    loadsound("back1")
                    sayland = 1
                    return


def menu_unit(items, sound="in1"):
    global pos, sayland
    loadsound(sound)
    items.sort(key=lambda x: x.ranking, reverse=True)
    items.sort(key=lambda x: x.pos.get_distance(x.pos, nation.cities[0].pos))
    items.sort(key=lambda x: x.pos.around_threat, reverse=True)
    say = 1
    x = 0
    while True:
        sleep(0.001)
        if say:
            play_stop()
            if items:
                if items[x].pos.around_threat: loadsound("notify12")
                sp.speak(f"{items[x]}.")
                if items[x].leads:
                    sp.speak(
                        f" leads {items[x].leading} ({len(items[x].leads)}) ")
                if items[x].pos.city: sp.speak(f"en {items[x].pos.city}.")
                else:
                    sp.speak(f"{in_t} {items[x].pos}.")
                    sp.speak(f"{items[x].pos.cords}.")

            else: sp.speak(f"{empty_t}.")
            say = 0

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    if items:
                        sp.speak(f"{items[x]}.")
                        if items[x].leads:
                            sp.speak(
                                f"{leading_t} {len(items[x].leads)} {squads_t}.")
                            sp.speak(f"{items[x].leading} {units_t}.")
                if event.key == pygame.K_2:
                    if items:
                        if items[x].pos.city: sp.speak(f"{items[x].pos.city}.")
                        sp.speak(f"{items[x].pos}, {items[x].pos.cords}.")
                        if items[x].pos.nation: sp.speak(
                            f"{items[x].pos.nation}.")
                if event.key == pygame.K_3:
                    if items:
                        sp.speak(
                            f"mp {items[x].mp[0]} {of_t} {items[x].mp[1]}.")
                if event.key == pygame.K_4:
                    if items:
                        sp.speak(
                            f"{defense_t} {items[x].pos.defense}, {threat_t} {items[x].pos.around_threat}.")
                if event.key == pygame.K_5:
                    if items:
                        sp.speak(
                            f"{food_t} {items[x].pos.food_need} {of_t} {items[x].pos.food}.")
                if event.key == pygame.K_6:
                    if items:
                        if items[x].pos.pop:
                            sp.speak(f"{population_t} {items[x].pos.pop}.")
                            sp.speak(
                                f"{public_order_t} {items[x].pos.public_order}.")
                            sp.speak(f"{unrest_t} {items[x].pos.unrest}.")
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
                    loadsound("s1")
                    say = 1
                if event.key == pygame.K_END:
                    x = len(items) - 1
                    loadsound("s1")
                    say = 1
                if event.key == pygame.K_RETURN:
                    if items:
                        pos = items[x].pos
                        sayland = 1
                        sleep(loadsound("set6") / 2)
                        return
                if event.key == pygame.K_F12 and ctrl and shift:
                    sp.speak(f"debug on.", 1)
                    Pdb().set_trace()
                    sp.speak(f"debug off.", 1)
                if event.key == pygame.K_ESCAPE:
                    sleep(loadsound("back1") / 2)
                    return


def movepos(value):
    global pos, sayland, x, y, z
    if move and scenary[scenary.index(pos) + value] not in move:
        loadsound("errn1")
        return
    play_stop()
    # if unit == []:
    # loadsound("mov6")
    if unit:
        sp.speak(f"move", 1)
    if filter_expand == 1:
        new_pos = scenary[scenary.index(pos) + value]
        sq = new_pos.get_near_tiles(1)
        go = 0
        for s in sq:
            if s.nation == nation: go = 1
        if go == 0:
            error(msg="no puede expandir allí.")
            return
    pos = scenary[scenary.index(pos) + value]
    sayland = 1
    x = -1
    y = 0


def naming(sound="back3"):
    say = 1
    name = str()
    sleep(loadsound(sound) / 2)
    sp.speak("type a name")
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
                    sp.speak(f"{name[-1]}.", 1)
                    name = name[:-1]
                    say = 1
                else:
                    loadsound("errn1")
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                sleep(loadsound("back1"))
                if name: return name
                else: return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                sleep(loadsound("back1") / 2)
                return


def nation_init():
    while True:
        done = 1
        shuffle(world.nations)
        for nat in world.nations:
            if nat.ai == 0: nat.info = 1
            nation_start_position(nat, world.map)
        for nat in world.nations:
            if nat.pos == None: done = 0
        if done:
            for nat in world.nations: nation_set_start_position(nat)
            break


def nation_start_position(itm, tiles, info=1):
    global players, pos
    logging.info(f"inicio de posición de {itm}.")
    itm.pos = None
    unallowed_tiles = [n.pos for n in world.nations if n.pos]
    tls = [it for it in tiles
           if it.soil.name in itm.soil and it.surf.name in itm.surf
           and it.hill in itm.hill]
    if info: logging.debug(f"casillas totales {len(tls)}.")
    shuffle(tls)
    [t.update() for t in tls]
    for tl in tls:
        tl.set_around(itm)
        if info: logging.debug(
            f"checking {tl} {tl.cords}. around ocean {tl.around_coast}.")
        if itm.check_min_tiles(tl) == 0:
            if info: logging.debug(f"min request failed..")
            continue
        if itm.check_max_tiles(tl):
            if info: logging.debug(f"max request failed..")
            continue
        done = 1
        sq = tl.get_near_tiles(6)
        for it in unallowed_tiles:
            if it in sq:
                done = 0
                if info: logging.debug(f"in sq.")

        # si listo.
        if done:
            itm.pos = tl
            if info: logging.debug(f"{itm} starts in {tl} {tl.cords}.")

        if done == 1: break


def nation_start_placement(nation):
    logging.debug(f"{nation} start placement in {nation.pos}.")
    pos = nation.units[0].pos
    settler = nation.initial_settler(nation)
    settler.pos = pos
    nation.add_city(nation.initial_placement, settler)


def nation_set_start_position(nation):
    logging.debug(f"{nation} set start position in {nation.pos}.")
    pos = nation.pos
    if nation.ai: nation.show_info = 0
    else: nation.show_info = 1
    for uni in nation.start_units:
        uni = uni(nation)
        uni.ai = nation.ai
        #uni.belongs += [nation]
        uni.pos = pos
        uni.show_info = nation.show_info
        nation.units.append(uni)
        pos.units.append(uni)


def play_sound(unit, sound, ch=0):
    if pos == unit.pos:
        if ch and ch.get_busy() == False:
            loadsound(sound, ch)
        else: loadsound(sound)


def req_unit(itm, nation, city):
    itm.update()
    logging.info(f"requicitos de {itm}.")
    if city.pop < itm.total_pop:
        error(info=nation.show_info, msg="sin población")
        return 0
    if itm.gold > 0 and nation.gold < itm.gold:
        error(info=nation.show_info, msg="sin oro")
        return 0
    items = nation.units + nation.production
    if itm.unique and basics.has_name(items, itm.name) == 1:
        city.commander_request = 0
        error(info=nation.show_info, msg="unidad única.")
        return 0
    return 1


def save_map():
    global world
    speak("se guardara", slp=0.5, num=1)
    file = open(os.path.join("maps//") + world.name + ext, "wb")
    file.write(pickle.dumps(world))
    file.close()
    speak("mapa guardado", slp=0.5)


def save_game():
    global world
    main_dir = os.getcwd() + str("/saves/")
    name = f"{world.nations[world.player_num]} {turn_t} {world.turn}"
    try:
        os.stat(main_dir)
    except:
        os.mkdir(main_dir)
        print(f"error.")
    file = open(main_dir + name + ".game", "wb")
    file.write(pickle.dumps(world))
    file.close()
    sp.speak(f"game saved.")


def saypos(sq):
    logging.debug(f"saypos")
    for i in sq:
        logging.debug(f"{i} {i.cords}.")


def select_item(msg, building, sound, limit=0):
    loadsound(sound)
    sp.speak(f"{msg}", 1)
    sleep(0.01)
    if len(building) == 0:
        building = [empty_t]
    say = 1
    x = 0
    while True:
        if say:
            say = 0
            if isinstance(building[x], str): sp.speak(f"{building[x]}.")
            if isinstance(building[x], str) == False: sp.speak(
                f"{building[x]().id[0]}.", 1)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                x = basics.selector(building, x, "up")
                say = 1
            if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                x = basics.selector(building, x, "down")
                say = 1
            if event.type == pygame.KEYDOWN and event.key == pygame.K_HOME:
                say = 1
                x = 0
                loadsound("s1")
            if event.type == pygame.KEYDOWN and event.key == pygame.K_END:
                say = 1
                x = len(building) - 1
                loadsound("s1")

            if (event.type == pygame.KEYDOWN and event.key == pygame.K_F12 and ctrl
                    and shift):
                sp.speak("on")
                Pdb().set_trace()
                sp.speak("off")

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if isinstance(building[x], str):
                    say = 1
                    continue
                if limit == 0:
                    loadsound("set6")

                    item = building[x]()
                    return item

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                loadsound("back1")
                return


def set_group(itm):
    logging.debug(f"set leads")
    logging.debug(
        f"{itm} distancia a objetivo {itm.pos.get_distance(itm.pos, itm.goal[1])}.")
    units = [itm] + itm.leads
    goal = itm.goal
    goto = goal[1]
    units.sort(key=lambda x: itm.pos.get_distance(goto, x.pos))
    itm = units[0]
    for i in units: logging.debug(
        f"distancia {itm.pos.get_distance(i.pos,goto)}.")
    units = [i for i in units if i != itm]
    itm.goal = goal
    itm.leads = [i for i in units]
    for i in units:
        i.goal = None
        i.leads = []
        i.leader = itm
    itm.leader = None
    itm.group_ranking = sum(i.ranking for i in units)
    logging.debug(
        f"{itm} distancia a objetivo {itm.pos.get_distance(itm.pos, itm.goal[1])}.")
    return itm


def set_logging():
    main_dir = os.getcwd() + str("/logs/")
    try:
        os.stat(main_dir)
    except:
        os.mkdir(main_dir)
        print(f"error.")


def set_near_tiles(nation, scenary):
    logging.debug(f"set_near_tiles")
    for ct in nation.cities:
        ct.tiles_near = [it for it in nation.map]
        ct.tiles_near = [it for it in ct.tiles_near if it.city ==
                         None and it.nation == None]
        ct.tiles_far = [it for it in nation.map]
        ct.tiles_far = [it for it in ct.tiles_far if it.get_distance(it, ct.pos) in [
            3, 4]]
        ct.tiles_far = [it for it in ct.tiles_far
                        if it.city == None and it.nation == None
                        and it.soil.name in nation.generic_soil
                        and it.surf.name in nation.generic_surf
                        and it.hill in ct.nation.generic_hill]
        ct.tiles_far.sort(key=lambda x: x.mean, reverse=True)
        for ti in ct.tiles_near:
            sq = ti.get_near_tiles(1)
            go = 0
            for s in sq:
                if s.city == ct: go = 1
            if go == 0: ct.tiles_near = [it for it in ct.tiles_near if it != ti]

    nation.tiles_far = []
    for ct in nation.cities:
        if ct.tiles_far: logging.debug(
            f"{len(ct.tiles_far)} casillas para fundar.")
        nation.tiles_far += ct.tiles_far
        nation.tiles_far.sort(key=lambda x: x.food_value, reverse=True)
        nation.tiles_far.sort(key=lambda x: len(x.around_snations))


def set_defend_pos(defense_need, itm, pos, info=0):
    """sent unit to defend a position."""
    if info: logging.debug(f"set_defend {itm}.")
    if itm.ranking > defense_need * 2 and itm.squads > 1:
        itm.split(1)
        msg = f"divided."
        if info: logging.debug(msg)
        itm.nation.devlog[-1] += [msg]
        itm.log[-1] += [msg]
    itm.update()
    if itm.goto == [] and itm.pos == pos:
        itm.move_set("gar")
        defense_need -= itm.ranking
        msg = f"{itm} será guarnición."
        if info: logging.debug(msg)
        itm.nation.devlog[-1] += [msg]
        itm.log[-1] += [msg]
        if info: logging.debug(f"necesita {round(defense_need,2)} defensa.")
        return defense_need
    elif itm.goto == [] and itm.pos != pos:
        msg = f"{itm} defenderá {pos} {pos.cords}."
        itm.log[-1] += [msg]
        itm.move_set(pos)
        itm.move_set("gar")
        defense_need -= itm.ranking
        if info: logging.debug(f"necesita {round(defense_need,2)} defensa.")
        return defense_need
    elif itm.goto and pos in itm.goto_pos:
        if info: logging.debug(f"{itm} se dirige a la ciudad.")
        defense_need -= itm.ranking
        if info: logging.debug(f"necesita {round(defense_need,2)} defensa.")
        return defense_need
    else: return defense_need


def set_settler(itm, info=1):
    logging.info(f"ajuste colono en {itm.pos}, {itm.pos.cords}.")
    if info: logging.debug(
        f"colonos {len([i for i in nation.units if i.settler])}.units_se")
    if itm.pos.city.defense_total < itm.pos.city.seen_threat * 1.5:
        if info: logging.debug(f"lack of defense.")
        return
    if nation.tiles_far:
        [it.update(nation) for it in nation.tiles_far]
        nation.tiles_far.sort(key=lambda x: x.food_value, reverse=True)
        nation.tiles_far.sort(key=lambda x: len(x.around_snations))
        if len(nation.cities) < 2: nation.tiles_far.sort(
            key=lambda x: itm.pos.get_distance(x, itm.pos))
        tile = nation.tiles_far[0]
        comms = [cm for cm in nation.units_comm
                 if cm.goal == None and cm.pos.around_threat + cm.pos.threat == 0]
        comms.sort(key=lambda x: itm.pos.get_distance(itm.pos, x.pos))
        if comms:
            comm = comms[0]
            itm.leader = comm
            # itm.join_group()
            comm.leads += [itm]
            comm.update()
            comm.set_lead_disband()
            if comm.leadership > comm.leading: comm.create_group(
                comm.leadership)
            comm.set_army_auto()
            if comm.pos != itm.pos: comm.move_set(itm.pos)
            comm.goal = ["settle", tile]
            comm.move_set(tile)
            msg = f"fundará aldea en {tile} {tile.cords}."
            if info:
                logging.debug(msg)
                comm.nation.log[-1] += [msg]
                comm.log[-1] += [msg]
            if dev_mode: 
                sp.speak(msg)
            sleep(1)


class Game:
    ai = Ai()

    def ai_random(self):
        global world
        logging.debug("ai_random")
        sp.speak(f"randoms.")
        world.update(scenary)
        world.add_random_buildings(world.buildings_value - len(world.buildings))
        world.building_restoration()

        if world.difficulty_type == "dynamic":
            difficulty = world.nations_score
        else: difficulty = world.difficulty
        if world.random_score < difficulty:
            # init = time()
            world.add_random_unit(world.nations_score - world.random_score / 2)
            # print(f"add_random_unit. {time()-init}.")
            world.update(scenary)

        # Setup commanders.
        for nt in world.random_nations:
            nt.setup_commanders()
        # Ai units joins.
        for uni in world.units:
            if uni.leader: continue
            if (uni.pos.around_threat +
                uni.pos.threat) > uni.ranking: basics.ai_join_units(uni)
            elif uni.pos.food_need > uni.pos.food:
                uni.split(randint(1, 2))
        world.update(scenary)
        world.units.sort(key=lambda x: x.leadership == 0, reverse=True)
        for uni in world.units:
            if uni.hp_total >= 1:
                uni.log.append([f"{turn_t} {world.turn}."])
                uni.restoring()
                uni.set_hidden(uni.pos)
                if uni.goto: uni.moving_unit()
                if uni.goto == [] and uni.will_less == 0 and uni.leader == None:
                    uni.oportunist_attack()
                uni.attrition()
                if uni.leader == None: self.ai.ai_action_random(uni)

    def control_basic(self, event):
        global nation
        if event.type == pygame.KEYDOWN:
            if ctrl == 0:
                if event.key == pygame.K_F1:
                    sp.speak(
                        f"{world.ambient.stime} ({world.ambient.sday_night}).", 1)
                if event.key == pygame.K_F2:
                    msg = f"{world.ambient.sseason}, {world.ambient.smonth}, \
            {world.ambient.syear}."
                    sp.speak(msg, 1)
                if event.key == pygame.K_F3:
                    sp.speak(f"{turn_t} {world.turn}.", 1)
                if event.key == pygame.K_F4:
                    sp.speak(f"{gold_t} {round(nation.gold)}.")
                    sp.speak(
                        f"{income_t} {nation.income}, {upkeep_t} {nation.upkeep}.")
                    sp.speak(f"{raid_income_t} {nation.raid_income}.")
                    sp.speak(f"{raid_outcome_t} {nation.raid_outcome}.")
                    sp.speak(
                        f"({total_t} {nation.income - nation.upkeep + (nation.raid_income-nation.raid_outcome)}).")

    def control_editor(self, event):
        global Belongs, east, Evt, inside, Group, Name, pos, sayland, scenary, starting, xy
        if event.type == pygame.KEYDOWN:
            # Ocean.
            if event.key == pygame.K_1:
                for i in [pos] + Group:
                    i.soil = Ocean()
                    i.surf = EmptySurf()
                    i.hill = 0
                sayland = 1
                play_stop()
            # Plain.
            if event.key == pygame.K_2:
                for i in [pos] + Group:
                    i.soil = Plains()
                    i.surf = EmptySurf()
                    i.hill = 0
                sayland = 1
                play_stop()
            # Grass.
            if event.key == pygame.K_3:
                for i in [pos] + Group:
                    i.soil = Grassland()
                    i.surf = EmptySurf()
                    i.hill = 0
                sayland = 1
                play_stop()
            # Desert.
            if event.key == pygame.K_4:
                for i in [pos] + Group:
                    i.soil = Desert()
                    i.surf = EmptySurf()
                    i.hill = 0
                sayland = 1
                play_stop()
            # Tundra.
            if event.key == pygame.K_5:
                for i in [pos] + Group:
                    i.soil = Tundra()
                    i.surf = EmptySurf()
                    i.hill = 0
                sayland = 1
                play_stop()
            # Glassier.
            if event.key == pygame.K_6:
                for i in [pos] + Group:
                    i.soil = Glacier()
                    i.surf = EmptySurf()
                    i.hill = 0
                sayland = 1
                play_stop()
            if event.key == pygame.K_q:
                # river
                for i in [pos] + Group:
                    i.surf = River()
                    i.hill = 0
                sayland = 1
                play_stop()
            if event.key == pygame.K_w:
                # swamp.
                for i in [pos] + Group:
                    i.surf = Swamp()
                    i.hill = 0
                sayland = 1
                play_stop()
            if event.key == pygame.K_e:
                # forest
                for i in [pos] + Group:
                    i.surf = Forest()
                    sayland = 1
                    play_stop()
            if event.key == pygame.K_r:
                # hill
                if (pos.surf == None or pos.surf
                        and pos.surf.name not in [mountain_t, river_t, swamp_t, volcano_t]):
                    for i in [pos] + Group:
                        i.hill = 1
                else: loadsound("errn1")
                sayland = 1
                play_stop()
            if event.key == pygame.K_t:
                # volcano
                if pos.surf == None:
                    for i in [pos] + Group:
                        i.surf = Volcano()
                        i.hill = 0
                else: loadsound("errn1")
                sayland = 1
                play_stop()
            if event.key == pygame.K_y:
                # mountain
                if pos.surf == None:
                    for i in [pos] + Group:
                        i.surf = Mountain()
                        i.hill = 0
                else: loadsound("errn1")
                sayland = 1
                play_stop()

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
                    sp.speak(f"{ready_t}.")
                    xy[0].append(pos.x)
                    xy[1].append(pos.y)
                    xy = [sorted(i) for i in xy]
                    for item in scenary:
                        if ((item.x >= xy[0][0] and item.y >= xy[1][0])
                                and (item.x <= xy[0][1] and item.y <= xy[1][1])):
                            Group.append(item)
                    sleep(loadsound("back1") / 2)
                    xy = []
                else:
                    sp.speak(f"from.")
                    sleep(loadsound("in1") / 2)
                    Group = []
                    xy = [[pos.x], [pos.y]]

            if event.key == pygame.K_RETURN:
                if Belongs != None:
                    if Group:
                        for item in Group:
                            if item.belongs:
                                item.belongs = None
                                if item in Belongs.owns: Belongs.owns.remove(
                                    item)
                            else:
                                item.belongs = Belongs
                                if item not in Belongs.owns: Belongs.owns.append(
                                    item)
                    else:
                        if pos.belongs and pos.belongs == Belongs:
                            sp.speak(f"{deleted_t}.", 1)
                            pos.belongs = None
                        elif pos.belongs == None or pos.belongs != Belongs:
                            sp.speak(f"{added_t}.", 1)
                            pos.belongs = Belongs
                            Belongs.owns.append(pos)
                    sayland = 1
                    play_stop()
                if Evt != None:
                    pass
                if Name != None:
                    loadsound("set5")
                    if Group:
                        for item in Group:
                            item.name = Name
                    else: pos.name = Name
                    sayland = 1
                    play_stop()

            if event.key == pygame.K_PAGEUP:
                pass
            if event.key == pygame.K_PAGEDOWN:
                pass

            if event.key == pygame.K_F9:
                if mapeditor: save_map()

    def control_game(self, event):
        global east, filter_expand, inside, move, nation, pos, rng, sayland, scenary, tiers, unit, west, world, width
        global x, y

        if event.type == pygame.KEYDOWN:
            if ctrl:
                if event.key == pygame.K_7 and dev_mode:
                    pos.add_unit(OrcWarrior, orcs_t, 1)
                if event.key == pygame.K_8 and dev_mode:
                    pos.add_unit(Velites, holy_empire_t, 1)
                if event.key == pygame.K_9 and dev_mode:
                    pos.add_unit(OrcCaptain, orcs_t, 1)
                if event.key == pygame.K_0 and dev_mode:
                    pos.add_unit(Decarion, holy_empire_t, 1)
                if event.key == pygame.K_F1:
                    if dev_mode: world.show_random_units()
                if event.key == pygame.K_F2:
                    if dev_mode: world.show_random_buildings()
                if event.key == pygame.K_TAB and dev_mode:
                    basics.view_log(world.log, nation)
                if event.key == pygame.K_l and dev_mode:
                    if x < 0: return
                    item = local_units[x]
                    basics.view_log(item.log, item.nation)
            if ctrl == 0:
                if event.key == pygame.K_a:
                    if x > -1:
                        local_units[x].auto_attack()
                if event.key == pygame.K_b:
                    # ver edificios.
                    if x < 0 and pos in nation.map:
                        menu_building(pos, nation)
                        pos.update(nation)
                if event.key == pygame.K_b:
                    if x > -1 and local_units[x].buildings and pos.sight:
                        if local_units[x].mp[0] < 1:
                            error(info=1, msg="sin movimientos")
                            return
                        itm = get_item2(
                            items1=local_units[x].buildings, msg="crear", simple=1)
                        if itm:
                            if itm(nation, local_units[x].pos).can_build() == 0:
                                error()
                                return
                            local_units[x].nation.add_city(itm, local_units[x])
                            pos.pos_sight(nation, nation.map)
                            sayland = 1
                            x = -1
                if event.key == pygame.K_c:
                    if x > -1:
                        local_units[x].set_cast()
                        sayland = 1

                if event.key == pygame.K_h:
                    pass
                    # Hire.
                    # if pos.buildings == []: return
                    # if nation in local_units[x].belongs and local_units[x].can_hire:
                    # local_units[x].get_hire_units()
                    # pass

                if event.key == pygame.K_i:
                    if x > -1: local_units[x].info(nation)
                    elif x < 0: info_tile(pos, nation)
                if event.key == pygame.K_j:
                    # unir.
                    if len(unit) > 1:
                        unit[0].join_units(unit, 1)
                        sayland = 1
                        unit = []
                        x = -1
                if event.key == pygame.K_l:
                    if x < 0: return
                    if (x > -1 and nation in local_units[x].belongs
                            and local_units[x].leadership):
                        local_units[x].set_leads()
                    elif local_units[x].leadership:
                        local_units[x].set_army(nation, view_mode=1)
                    sayland = 1
                if event.key == pygame.K_m:
                    # mover unidad.
                    if unit:
                        if pos not in nation.map:
                            error()
                            return
                        for i in unit: i.move_set(pos)
                        sayland = 1
                if event.key == pygame.K_n:
                    # nombrar casilla.
                    if x == -1 and pos.nation == None or pos.nation == nation:
                        pos.name = naming()
                    # nombrar unidad.
                    elif x >= 0 and local_units[x].nation == nation: local_units[x].nick = naming()
                if event.key == pygame.K_p:
                    if x > -1 and local_units[x].leadership:
                        local_units[x].set_army(nation)
                    else: loadsound("errn1")

                if event.key == pygame.K_s:
                    if local_units and nation in local_units[x].belongs: local_units[x].split(
                    )
                    sayland = 1
                if event.key == pygame.K_SPACE:
                    if x > -1:
                        if local_units[x] not in unit:
                            loadsound("selected1")
                            sp.speak(f"{selected_t}", 1.)
                            unit.append(local_units[x])
                        elif local_units[x] in unit:
                            sp.speak(f"{unselected_t}.", 1)
                            unit.remove(local_units[x])
                            loadsound("unselected1")
                if event.key == pygame.K_RETURN:
                    # opciones de edificio.
                    if filter_expand == 0:
                        if pos.is_city and pos.nation == world.nations[world.player_num]:
                            sayland = 1
                            [menu_city(b)
                             for b in pos.buildings if b.type == city_t]
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
                    if x == -1 or (local_units and nation not in local_units[x].belongs):
                        error()
                        return
                    if get_item2([0, 1], ["no", "si"], "Eliminar unidad",):
                        local_units[x].disband()
                        sayland = 1
                        x -= 1

                if event.key == pygame.K_TAB:
                    basics.view_log(nation.log, nation)
                if event.key == pygame.K_HOME:
                    unit = []
                    x = -1
                    if nation.cities == []:
                        error(msg="no hay ciudad.", sound="errn1")
                        return
                    nation.cities.sort(key=lambda x: x.capital, reverse=True)
                    y = basics.selector(nation.cities, y, "up")
                    try:
                        pos = nation.cities[y].pos
                    except:
                        pos = nation.cities[0].pos
                        print(f"error.")
                    sayland = 1
                if event.key == pygame.K_END:
                    unit = []
                    x = -1
                    if nation.cities == []:
                        error(msg="no hay ciudad.", sound="errn1")
                        return
                    nation.cities.sort(key=lambda x: x.capital, reverse=True)
                    y = basics.selector(nation.cities, y, "down")
                    try:
                        pos = nation.cities[y].pos
                    except:
                        pos = nation.cities[0].pos
                        print(f"error.")
                    sayland = 1
                if event.key == pygame.K_PAGEUP:
                    # play_stop()
                    if local_units == [] or pos.sight == 0:
                        error(msg=empty_t)
                        return
                    if x == -1:
                        unit = []
                        x = 0
                    elif x > -1:
                        x = basics.selector(local_units, x, "up")
                    local_units[x].basic_info(nation)
                if event.key == pygame.K_PAGEDOWN:
                    # play_stop()
                    if local_units == [] or pos.sight == 0:
                        error(msg=empty_t)
                        return
                    if x == -1:
                        unit = []
                        x = 0
                    elif x > -1:
                        x = basics.selector(local_units, x, "down")
                    local_units[x].basic_info(nation)
                if event.key == pygame.K_F5:
                    sayland = 1
                    nation.update(nation.map)
                    units = [uni for uni in nation.units if uni.leader == None]
                    menu_unit(units)
                if event.key == pygame.K_F6:
                    sayland = 1
                    units = []
                    for ti in nation.map:
                        if ti.sight:
                            units += ti.get_free_squads(nation) + \
                                ti.get_comm_units(nation)
                    units = [i for i in units if len(i.pos.around_snations)
                             and nation not in i.belongs]
                    menu_unit(units)
                if event.key == pygame.K_F7:
                    sayland = 1
                    units = []
                    for ti in nation.map:
                        if ti.sight:
                            units += ti.get_free_squads(nation) + \
                                ti.get_comm_units(nation)
                    units = [i for i in units if nation not in i.belongs]
                    units.sort(key=lambda x: x.pos.get_distance(
                        x.pos, nation.cities[0].pos))
                    menu_unit(units)
                if event.key == pygame.K_F8:
                    menu_nation(nation)
                if event.key == pygame.K_F11:
                    world.player_num += 1
                    self.next_play()

    def control_global(self, event):
        global Belongs, city_name, east, Evt, inside, Group, mapeditor, move, Name, nation_name, pos, sayland, scenary, terrain_name, unit, west, width, xy
        if event.type == pygame.KEYDOWN:
            if x > -1 and mapeditor == 0:
                itm = local_units[x]
                if event.key == pygame.K_1:
                    sp.speak(
                        f"{itm}. leading {itm.leading} {of_t} {itm.leadership}.")
                    sp.speak(f"{itm.nation}.")
                if event.key == pygame.K_2:
                    sp.speak(f"hp: {itm.hp_total}")
                    if itm.hp_res: sp.speak(
                        f"hp res: {itm.hp_res+itm.hp_res_mod}.")
                    sp.speak(f"mp {itm.mp[0]} {of_t} {itm.mp[1]}.")
                if event.key == pygame.K_3:
                    sp.speak(f"{itm.get_total_food()}")
                if event.key == pygame.K_4:
                    sp.speak(
                        f"power {itm.power} {of_t} {itm.power_max+itm.power_max_mod}.")
                    sp.speak(f"power res {itm.power_res}.")
                if event.key == pygame.K_5:
                    sp.speak(f"level {itm.level} (xp {itm.xp}).", 1)
                if event.key == pygame.K_0:
                    sp.speak(f" garrison {local_units[x].garrison}.", 1)
                    sp.speak(f"scout {local_units[x].scout}.")
                    sp.speak(f"revealed value {local_units[x].revealed_val}.")
                    if local_units[x].goal: sp.speak(
                        f"goal {local_units[x].goal[0], local_units[x].goal[1].cords}.")
            if x == -1 and mapeditor == 0:
                if event.key == pygame.K_1:
                    sp.speak(
                        f"{food_t}: {pos.food_need}. {of_t} {pos.food}.", 1)
                    sp.speak(f"{resources_t}: {pos.resource}.")
                    if pos.pop: sp.speak(f"{pos.populated}%.")
                if event.key == pygame.K_2:
                    events = [ev.name for ev in pos.events]
                    terrain = [ev.name for ev in pos.terrain_events]
                    sp.speak(f"events {events}.")
                    sp.speak(f"terrain {terrain}.")
                if event.key == pygame.K_3:
                    sp.speak(f"{population_t}: {pos.pop}.", 1)
                    sp.speak(f"{public_order_t}: {pos.public_order}.")
                    sp.speak(f"unrest: {pos.unrest}.")
                if event.key == pygame.K_4:
                    sp.speak(f"{grouth_t}: {round(pos.grouth,2)}.", 1)
                    sp.speak(f"{income_t}: {pos.income}.")
                    sp.speak(f"{raid_outcome_t}:  {pos.raided}.")
                    sp.speak(f"{total_t}: {pos.income-pos.raided}.")
                if event.key == pygame.K_5:
                    sp.speak(f"cost {pos.cost}.")
                    sp.speak(f"{size_t} {pos.size}.")
                if event.key == pygame.K_6 and dev_mode:
                    sp.speak(pos.food_rate, 1)
                    sp.speak(f"{pos.flood= }.")
                    sp.speak(f"{len(nation.units_comm)=:}.")
                    sp.speak(f"{len(nation.units_scout)=:}.")

                if event.key == pygame.K_d:
                    sp.speak(f"defensa {round(pos.defense, 1)}.")
                    sp.speak(f"{around_defense_t} {pos.around_defense}.")
                    if dev_mode: sp.speak(f"{pos.defense_req= }")
                if event.key == pygame.K_t:
                    sp.speak(f"{threat_t} {pos.threat}.")
                    sp.speak(f"{around_threat_t} {pos.around_threat}.")
                if event.key == pygame.K_l:
                    if pos in nation.map:
                        pos.get_around_tiles(nation)
                if event.key == pygame.K_v:
                    pass
                    #sp.speak(f"valor {pos.food_value}, {pos.res_value}.", 1)
                    # sp.speak(f"{pos.mean}.")
            if event.key == pygame.K_z:
                pos.update(nation)
                sayland = 1
            if event.key == pygame.K_x:
                sp.speak(f"{pos.cords}.")
            if ctrl == 0 and event.key == pygame.K_F9:
                if mapeditor == 0: save_game()
            if ctrl == 0 and event.key == pygame.K_F10:
                pass
            if event.key == pygame.K_F12 and ctrl and shift:
                sp.speak("on", 1)
                Pdb().set_trace()
                sp.speak("off", 1)
            if event.key == pygame.K_ESCAPE:
                if (Belongs or Evt or Group or Name != None or unit != [] or rng
                        or filter_expand or x > -1):
                    end_parameters()
                    return
                if get_item2([0, 1], [not_t, yes_t], msg_exit_t,):
                    exit()

    def editor_tile_info(self, pos, nation):
        global sayland
        if sayland:
            sayland = 0
            pos.update()
            sp.speak(str(pos))
            pos.play_tile()

    def map_movement(self, event):
        global pos, sayland
        if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
            if pos not in scenary[:width]:
                play_stop()
                movepos(value=-width)
            else:
                loadsound("errn1")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
            if pos not in scenary[len(scenary) - width:]:
                play_stop()
                movepos(value=width)
            else:
                loadsound("errn1")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
            if pos not in west:
                movepos(value=-1)
            else:
                loadsound("errn1")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            if pos not in east:
                movepos(value=1)
            else:
                loadsound("errn1")

    def next_play(self):
        global nation, pos, players, sayland, unit, x
        unit = []
        x = -1
        while True:
            if world.player_num == len(world.nations):
                self.new_turn()
                # init = time()
                world.player_num = 0
                self.ai_random()
                # print(f"ai_random. {time()-init}.")

            nation = world.nations[world.player_num]
            if nation.ai == 0:
                logging.info(f"{turn_t} {of_t} {nation}.")
                self.start_turn(nation)
                nation.pos.map_update(nation, nation.map)
                if nation.cities: pos = nation.cities[0].pos
                elif nation.units: pos = nation.units[0].pos
                nation.update(scenary)
                loadsound("notify9")
                sayland = 1
                save_game()
                return
            elif nation.ai:
                init = time()
                self.ai.nation_play(nation)
                # print(f"nation_play. {time()-init}.")
                nation.pos.map_update(nation, nation.map)
                if nation.cities: pos = nation.cities[0].pos
                elif nation.units: pos = nation.units[0].pos
                sayland = 1
                if dev_mode:
                    save_game()
                    return
            world.player_num += 1

    def new_turn(self):
        global turns, sayland, ambient
        ambient = world.ambient
        ambient.update()
        last_day_night = ambient.day_night[0]
        [i.update(scenary) for i in world.nations]
        logging.debug(f"nuevo turno.")
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
        world.log += [[f"{turn_t} {world.turn}."]]
        world.ambient.update()
        ambient = world.ambient

        [i.start_turn() for i in world.map]
        for n in world.nations:
            n.start_turn()

        msg = f"{turn_t} {world.turn}."
        logging.info(msg)
        logging.info(f"{ambient.stime}, {ambient.smonth}, {ambient.syear}.")
        sp.speak(msg)
        sleep(loadsound("notify14") * 0.1)
        if ambient.day_night[0] != last_day_night:
            if ambient.day_night[0] == 0: sleep(
                loadsound("dawn01", channel=CHTE2) / 3)
            if ambient.day_night[0]: sleep(
                loadsound("night01", channel=CHTE2) / 5)
        # gc.collect()

    def start(self):
        global mapeditor, new_game
        loadsound("back1")
        run = 1
        set_logging()
        say = 1
        items = [new_t, load_t, world_editor_t, world_creator_t, exit_t]
        x = 0
        if dev_mode: sp.speak(f"dev mode.")
        sleep(2)
        while run:
            sleep(0.01)
            if say:
                sp.speak(f"{items[x]}.", 1)
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
                            loading_map("maps//", "/*.map")
                        if items[x] == load_t:
                            new_game = 0
                            loading_map("saves//", "/*.game")
                        if items[x] == world_editor_t:
                            mapeditor = 1
                            loading_map("maps//", "/*.map")
                            if world: Game().run()
                        if items[x] == world_creator_t:
                            mapeditor = 2
                            map_init()
                            Game().run()
                        if items[x] == exit_t: return
                        if new_game:
                            if ("world" in globals()
                                    and self.set_nations(globals()["world"]) == None):
                                del(globals()["world"])
                        if "world" in globals():
                            run = 0
                            Game().run()

    def set_nations(self, world):
        say = 1
        x = 0
        items = [nt() for nt in nations]
        for it in items: it.ai = 1
        world.nations = []
        while True:
            sleep(0.01)
            items.sort(key=lambda x: x in world.nations, reverse=True)
            if say:
                itm = items[x]
                if itm in world.nations: sp.speak(f"{selected_t}.", 1)
                sp.speak(f"{itm.name}")
                if itm.ai == 0: sp.speak(f"{human_t}.")
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
                    if event.key == pygame.K_a:
                        itm = items[x]
                        if itm.ai: itm.ai = 0
                        else: itm.ai = 1
                        say = 1
                    if event.key == pygame.K_SPACE:
                        itm = items[x]
                        say = 1
                        if itm not in world.nations:
                            world.nations += [itm]
                            sp.speak(f"{selected_t}.", 1)
                            sleep(loadsound("set6"))
                        else:
                            world.nations.remove(itm)
                            sp.speak(f"{removed_t}.", 1)
                            sleep(loadsound("set6"))
                    if event.key == pygame.K_RETURN:
                        go = 0
                        for nt in world.nations:
                            if nt.ai == 0: go += 1
                        if len(world.nations) >= 2 and go:
                            loadsound("set5")
                            return 1
                        else:
                            sp.speak(f"""needs at least two nations 
              and one nation set to human.""", 1)
                            sleep(loadsound("errn1"))
                            say = 1
                    if event.key == pygame.K_ESCAPE:
                        loadsound("back1")
                        return

    def start_turn(self, nation):
        global sayland
        if pygame.key.get_focused(): sp.speak(f"{nation}.", 1)
        sp.speak(f"{ambient.day_night[1][ambient.day_night[0]]}.")
        sayland = 1
        if nation.map: nation.map[0].pos_sight(nation, nation.map)
        else: scenary[0].pos_sight(nation, scenary)
        nation.pos.map_update(nation, nation.map)
        nation.update(nation.map)
        if nation.pos.world.turn > 1: nation.set_hidden_buildings()
        # nation population changes.
        [city.population_change()
         for city in nation.cities if city.pos.world.turn > 1]
        # nation income.
        if nation.pos.world.turn > 1: nation.set_income()
        # cities.
        logging.debug(f"ciudades.")
        [city.check_events() for city in nation.cities]
        [city.update() for city in nation.cities]
        [city.check_building() for city in nation.cities]
        [city.check_training() for city in nation.cities]
        [city.status() for city in nation.cities]

        # initial placement.
        if nation.cities == [] and world.turn == 1:
            nation_start_placement(nation)
        # Unidades.
        # for uni in nation.units: uni.log.append([f"{turn_t} {world.turn}."])
        logging.debug(f"unidades.")
        for uni in nation.units:
            uni.start_turn()
            if uni.pos.world.turn > 1: uni.restoring()
            uni.set_hidden(uni.pos)
            if uni.goto: uni.move_unit()
            if uni.pos.world.turn > 1:uni.attrition()
            if uni.pos.world.turn > 1: uni.maintenanse()
        self.ai.ai_explore(nation, scenary)
        nation.update(nation.map)
        nation.set_seen_nations()

        # otros.
        sleep(loadsound("notify10") / 2)
        warning_enemy(nation, nation.map)

    def tile_info(self, pos, nation):
        global city_name, local_units, nation_name, terrain_name, sayland
        if sayland:
            sayland = 0
            pos.pos_sight(nation, nation.map)
            pos.update(nation)
            sq = pos.get_near_tiles(2)
            nation.pos.map_update(nation, sq)
            # [it.update(nation) for it in scenary]
            # nation.update(scenary)
            if pos.nation == nation and pos.blocked: sleep(
                loadsound("nav2") * 0.3)
            elif pos.nation == nation:
                sleep(loadsound("nav1") * 0.3)
            elif pos.nation != nation:
                if pos.nation == None and pos.sight: sleep(
                    loadsound("nav4") * 0.3)
            # if pos.name and pos.sight: sp.speak(f"{pos.name}.", 1)
            if pos in nation.map:
                pos.play_tile()

                if pos.threat > 0 and pos.sight:
                    sp.speak(f"hostiles.")
            if pos.defense > 0:
                pass
            if pos in nation.map:
                if pos.city == None or pos.city.nick != city_name:
                    city_name = None
                    if pos.city:
                        city_name = pos.city.nick
                        if pos.sight or pos in nation.nations_tiles:
                            sp.speak(f"{city_name}")
                            loadsound("notify20")
                if pos.nation == None or str(pos.nation) != nation_name:
                    nation_name = None
                    if pos.nation:
                        nation_name = str(pos.nation)
                        if nation_name and pos.sight or pos in nation.nations_tiles:
                            sp.speak(f"{nation_name}")
                            loadsound("notify20")
                if pos.sight == 0:
                    sp.speak(f"{fog_t}.")
                    if pos not in nation.nations_tiles:
                        city_name = None
                        nation_name = None
                if pos.sight:
                    squad_units = pos.get_free_squads(nation)
                    total_squads = pos.get_squads(nation)
                    comm_units = pos.get_comm_units(nation)
                    local_units = comm_units + squad_units
                    local_units.sort(key=lambda x: x.scout)
                    local_units.sort(key=lambda x: x.settler)
                    local_units.sort(key=lambda x: x.mp[0], reverse=True)
                    local_units.sort(key=lambda x: len(x.leads), reverse=True)
                    local_units.sort(key=lambda x: x.leadership, reverse=True)
                if filter_expand == 0 and pos.sight:
                    if comm_units: sp.speak(f"commanders {len(comm_units)}.")
                    if squad_units: sp.speak(f"{squads_t} {len(local_units)}.")
                    if len(total_squads) + len(comm_units):
                        sp.speak(f"({len(comm_units)+len(total_squads)}).")
                    if pos.corpses and pos.sight:
                        corpses = round(sum(sum(i.deads) for i in pos.corpses))
                        sp.speak(f"{corpses_t} {corpses}.")
                sp.speak(f"{pos}")
                if pos.is_city and (pos.sight or pos in nation.nations_tiles):
                    sp.speak(f"{pos.city}")
                    loadsound("working1")
                if filter_expand:
                    cost = get_tile_cost(city, pos)
                    sp.speak(f"{cost} {gold_t}.")
                if pos.sight or pos in nation.nations_tiles:
                    if pos.buildings:
                        buildings = [b for b in pos.buildings
                                     if b.type == city_t or nation in b.nations or nation == b.nation]
                        if buildings: sp.speak(
                            f"{len(buildings)} {buildings_t}.")
                    if pos.buildings and [b for b in pos.buildings if b.resource_cost[0] < b.resource_cost[1] and b.nation == nation]:
                        loadsound("construction1", channel=CHTE2)
                    if pos.events:
                        for ev in pos.events:
                            sp.speak(f"{ev.name}")
                            if ev == pos.events[-1]: sp.speak(".")
                            else: sp.speak(",")
            else:
                local_units = []
                sp.speak(f"terra incognita.")
                city_name = None
                nation_name = None

    def run(self):
        global city, city_name, nation_name, terrain_name, rng, time
        global Belongs, Evt, Group, move, Name, pos, sayland, scenary, starting, xy
        global nation, num, unit, world, x, y, z
        global filter_expand
        global PLAYING
        global alt, ctrl, shift

        # change()
        if startpos: pos = scenary[startpos]
        Belongs = None
        city = None
        city_name = ""
        Evt = None
        filter_expand = 0
        Group = []
        move = []
        Name = None
        nation_name = ""
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
            world.log = [[f"{turn_t} {world.turn}."]]
            # dificultad.
            world.ambient = ambient
            world.difficulty = DIFFICULTY
            world.difficulty_type = "dynamic"
            # Random Nations.
            world.random_nations = RANDOM_FACTIONS
            # BuildingsRandom .
            world.random_buildings = random_buildings
            world.buildings_value = buildings_value
            scenary = world.map
            Unit.ambient = world.ambient
            Nation.world = world
            shuffle(world.nations)
            world.cnation = world.nations[0]
            world.season_events()
            for it in scenary:
                it.world = world
                it.update()

            nation_init()
            [nt.start_turn() for nt in world.nations]
            [nation_start_placement(nt) for nt in world.nations]
            world.add_random_buildings(world.buildings_value)
            self.new_turn()
            self.next_play()
        elif mapeditor == 0 and new_game == 0:
            nation = world.nations[world.player_num]
            if nation.cities: pos = nation.cities[0].pos
            else: pos = nation.units[0].pos
            Unit.ambient = world.ambient
            Unit.ai = Ai
            scenary = world.map
        elif mapeditor:
            sp.speak("modo editor.")
            sleep(0.01)

            nation = Empty()
            nation.name = "editor"
            nation.map = world.map
        if pos not in world.map: inside = 1
        elif pos in world.map: inside = 0
        while PLAYING:
            sleep(0.001)
            if mapeditor > 0:
                n1 = Empty()
                n1.map = scenary
                players = Empty()
                world.nations = [n1]
            if mapeditor == 0: self.tile_info(
                pos, world.nations[world.player_num])
            else: self.editor_tile_info(pos, world.nations[world.player_num])
            pos.play_events()

            pressed = list(pygame.key.get_pressed())
            alt = pressed[308]
            ctrl = pressed[305] or pressed[306]
            shift = pressed[303] or pressed[304]
            for event in pygame.event.get():
                self.map_movement(event)
                self.control_global(event)
                if mapeditor == 0:
                    self.control_game(event)
                    self.control_basic(event)
                elif mapeditor in [1, 2]:
                    self.control_editor(event)


def speak(msg, slp=0, num=0, sound=None):
    if sound: loadsound(sound)
    logging.debug(msg)
    sp.speak(msg, num)
    if slp: sleep(slp)


def train_unit(city, items, msg, sound="in1"):
    sleep(loadsound(sound) / 2)
    x = 0
    say = 1
    sp.speak(msg, 1)
    while True:
        sleep(0.001)
        if say:
            item = items[x](nation)
            item.update()
            prod = item.resource_cost / city.resource_total
            prod = int(ceil(prod))
            sp.speak(f"{item} {in_t} {prod}.", 1)
            sp.speak(
                f"{cost_t} {item.gold}. {upkeep_t} {item.upkeep*item.units}.")
            sp.speak(f"{resources_t} {item.resource_cost}.")
            sp.speak(f"{population_t} {item.total_pop}.")
            say = 0

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    item.info(nation)
                    say = 1
                if event.key == pygame.K_UP:
                    x = basics.selector(items, x, go="up")
                    say = 1
                if event.key == pygame.K_DOWN:
                    x = basics.selector(items, x, go="down")
                    say = 1
                if event.key == pygame.K_RETURN:
                    if req_unit(item, nation, city):
                        return item
                    else: error()
                if event.key == pygame.K_F12 and ctrl and shift:
                    sp.speak(f"debug on.", 1)
                    Pdb().set_trace()
                    sp.speak(f"debug off.", 1)
                if event.key == pygame.K_ESCAPE:
                    sleep(loadsound("back1") / 2)
                    return


#day_limit = 30
#day_timer = [0, 20]
#global_timer = [2, 2]
#timer1 = [ticks(), 500]
#timer2 = ticks()


def warning_enemy(nation, scenary):
    warn = 0
    for ti in nation.tiles:
        if ti.threat:
            warn = 1
    if warn: sp.speak(f"enemigos. {warn}.")

    if warn and nation.ai == 0: sleep(loadsound("warn1", channel=CHTE2) / 2)
    return warn



# 0 = juego, 1 = editor de mapa, 3 = crear y editar.
mapeditor = 0

# 1 = nuevo juego, 0 = cargar partida.
new_game = 1

startpos = None

if mapeditor == 0: exec("from game_setup import *")


def change():
    for it in scenary:
        if it.surf.name == "nada": it.surf.name = none_t


Game().start()
