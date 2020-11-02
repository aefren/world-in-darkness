exec('from data.items import HolyEmpire, Wallachia, WoodElves, Hell, Nature, Orcs, Wild')
exec('from data.items import *')


#Difficulty.
DIFFICULTY = 30
DIFFICULTY_TYPE = 'dynamic'
#Random Buildings.
random_buildings = [BrigandLair, Campment, CaveOfDarkRites, CaveOfGhouls, 
                    FightingPit, GoblinLair, HiddenForest, HyenasLair, 
                    NecromancersLair, OathStone, OpulentTomb, TroglodyteCave,  
                    TrollCave, UnderworldEntrance, WisperingWoods, WolfLair,
                    WargsCave]
buildings_value = 12

#factions.
ELF = WoodElves()
ELF.ai = 1
HOLY = HolyEmpire()
HOLY.ai = 1
TRANS = Wallachia()
TRANS.ai = 1

NATIONS = [HOLY, ELF, TRANS]

#Random factions.
RANDOM_FACTIONS = [Hell(), Nature(), Orcs(), Wild()]

