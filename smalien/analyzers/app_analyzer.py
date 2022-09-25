import logging

from .control_flow_analyzer import ControlFlowAnalyzer

logger = logging.getLogger(name=__name__)


class AppAnalyzer(ControlFlowAnalyzer):
    """
    Analyze bytecode instructions in smali files.
    """

    def __init__(self, app_code):
        logger.debug('initializing')
        self.app_code = app_code

    def run(self):
        logger.debug('running')
