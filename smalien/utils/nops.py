import logging

logger = logging.getLogger(name=__name__)


class Nop:
    """
    Do nothing.
    """
    @staticmethod
    def run(**kwargs):
        pass

class NoMatch:
    """
    This class is used to tell that nothing is matched.
    """
    @staticmethod
    def run(**kwargs):
        raise Exception("Nothing is matched")

