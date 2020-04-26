from data.lang.es import wood_t
exec('from data.items import *')


#difficulty.
DIFFICULTY = 30
DIFFICULTY_TYPE = 'dynamic'

#factions.
HOLY = HolyEmpire()
HOLY.ai = 0
TRANS = Walachia()
TRANS.ai = 0
ELF = WoodElves()
ELF.ai = 1
NATIONS = [HOLY]

#Random factions.
RANDOM_FACTIONS = [Hell(), Wild()]