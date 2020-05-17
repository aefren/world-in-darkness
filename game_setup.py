exec('from data.items import *')


#difficulty.
DIFFICULTY = 40
DIFFICULTY_TYPE = 'dynamic'

#factions.
HOLY = HolyEmpire()
HOLY.ai = 1
TRANS = Walachia()
TRANS.ai = 0
ELF = WoodElves()
ELF.ai = 1
NATIONS = [ELF]

#Random factions.
RANDOM_FACTIONS = [Hell(), Wild()]