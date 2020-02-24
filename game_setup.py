exec('from data.items import *')


#difficulty.
DIFFICULTY = 20
DIFFICULTY_TYPE = 'dynamic'

#factions.
HOLY = HolyEmpire()
TRANS = Transylvania()
TRANS.ai = 1
SILVAN = SilvanElves()
SILVAN.ai = 1
NATIONS = [HOLY, TRANS, SILVAN]

#Random factions.
RANDOM_FACTIONS = [Hell(), Wild()]