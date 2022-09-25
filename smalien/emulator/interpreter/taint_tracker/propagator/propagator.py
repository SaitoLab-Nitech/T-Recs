import logging

from smalien.utils.nops import Nop
from .simple_propagators import *

logger = logging.getLogger(name=__name__)


class Propagator:
    """
    This class propagates taints to track information flows.
    """

    def __init__(self):
        logger.debug('initializing')

        self.mapping = {
            'unop': UnopTaintPropagator,
            'aput': AputTaintPropagator,
            'aget': AgetTaintPropagator,
            'iget': IgetTaintPropagator,
            'invoke': InvokeTaintPropagator,
            'move_result': MoveResultTaintPropagator,
        }

    def run(self, **kwargs):
        """
        Run the propagator.
        """
        logger.debug('running')

        inst = kwargs['inst']

        self.mapping.get(inst.kind, Nop).run(**kwargs)
