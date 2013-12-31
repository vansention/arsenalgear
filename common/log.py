import logging ,os 
from settings import LOG_FILE,LOG_LEVEL

print LOG_FILE
logging.basicConfig(filename = os.path.join('/var/log/ArsenalGear/', LOG_FILE), level = logging.INFO, format = '%(asctime)s - %(levelname)s: %(message)s')  
logger = logging.getLogger()
