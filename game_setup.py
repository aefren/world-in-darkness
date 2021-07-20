dev_mode = 0
if dev_mode == 0:
    exec("from data.items import *")
elif dev_mode:
    from data.items import *


# Difficulty.
DIFFICULTY = 66
DIFFICULTY_TYPE = "dynamic"
# Random Buildings.
random_buildings = random_buildings
buildings_value = 10

# factions.
#ELF = WoodElves()
#ELF.ai = 1
#HOLY = HolyEmpire()
#HOLY.ai = 0
#TRANS = Valahia()
#TRANS.ai = 1

#NATIONS = [HOLY, ELF, TRANS]

# Random factions.
#RANDOM_FACTIONS = [Malignant(), Hell(), Nature(), Order(), Orcs(), Wild()]

lang = "es"  # en, es.
