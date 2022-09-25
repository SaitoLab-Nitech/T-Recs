
from .project import *


# Setup loggers
import logging
logging.getLogger('smalien').addHandler(logging.NullHandler())
from .utils.loggers import Loggers
loggers = Loggers()
del Loggers
del logging
