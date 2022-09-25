import logging

from .array_value_resolvers import *

logger = logging.getLogger(name=__name__)


# This is currently not used.
# api_call_edge_value_resolvers = {
#     # Array
#     'Ljava/lang/reflect/Array;': {
#         'newInstance(Ljava/lang/Class;[I)Ljava/lang/Object;': ArrayNewInstanceValueResolver,
#     },
# }
