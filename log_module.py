import logging
import os
from datetime import datetime


path_log = os.getcwd()+str('/logs/log.log')
logging.basicConfig(filename=path_log, filemode='w', level=logging.DEBUG, 
                    format='%(levelname)s. %(message)s --- %(funcName)s. (%(lineno)d)')
t = datetime.now()
date = f'{t.day}_{t.month}_{t.year}: {t.hour}:{t.minute}'
logging.warning(f'{date}')