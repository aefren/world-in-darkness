exec('from data.items import *')


#difficulty.
DIFFICULTY = 20
DIFFICULTY_TYPE = 'dynamic'

#factions.
HOLY = HolyEmpire()
HOLY.ai = 0
TRANS = Transylvania()
TRANS.ai = 1
SILVAN = SilvanElves()
SILVAN.ai = 1
NATIONS = [HOLY, TRANS, SILVAN]

#Random factions.
RANDOM_FACTIONS = [Hell(), Wild()]