import logging

logger = logging.getLogger(name=__name__)


class ControlFlowAnalyzer:
    """
    Create control flow graphs (CFGs) consisting of branches and try-catch jumps.
    """

    def __init__(self):
        logger.debug('initializing')
