from data.items import HolyEmpire, Walachia, WoodElves, Hell, Wild
exec('from data.items import *')


#difficulty.
DIFFICULTY = 20
DIFFICULTY_TYPE = 'dynamic'

#factions.
HOLY = HolyEmpire()
HOLY.ai = 0
TRANS = Walachia()
TRANS.ai = 1
ELF = WoodElves()
ELF.ai = 0
NATIONS = [ELF]

#Random factions.
RANDOM_FACTIONS = [Hell(), Wild()]