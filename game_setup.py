exec('from data.items import HolyEmpire, Walachia, WoodElves, Hell, Nature, Orcs, Wild')
exec('from data.items import *')


#difficulty.
DIFFICULTY = 20
DIFFICULTY_TYPE = 'dynamic'

#factions.
ELF = WoodElves()
ELF.ai = 1
HOLY = HolyEmpire()
HOLY.ai = 1
TRANS = Walachia()
TRANS.ai = 1

NATIONS = [HOLY, ELF, TRANS]

#Random factions.
RANDOM_FACTIONS = [Hell(), Nature(), Orcs(), Wild()]