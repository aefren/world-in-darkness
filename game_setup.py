#exec("from data.items import HolyEmpire, valahia, WoodElves, Hell, Nature, Orcs, Wild")
exec("from data.items import *")
exec("import data.items")


#Difficulty.
DIFFICULTY = 70
DIFFICULTY_TYPE = "dynamic"
#Random Buildings.
random_buildings = data.items.random_buildings
buildings_value = 20

#factions.
ELF = WoodElves()
ELF.ai = 1
HOLY = HolyEmpire()
HOLY.ai = 0
TRANS = valahia()
TRANS.ai = 1

NATIONS = [HOLY, ELF, TRANS]

#Random factions.
RANDOM_FACTIONS = [Death(), Hell(), Nature(), Neutral(), Orcs(), Wild()]

