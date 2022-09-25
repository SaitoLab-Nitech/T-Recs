import logging
from .structures import Taint

logger = logging.getLogger(name=__name__)


class TaintOperator:
    """
    Performs taint operations: creation, checking, and deletion.
    """

    taint_tags = {
        'sensitive': 1,
        'insensitive': 0,
    }

    @staticmethod
    def create(sources, tag=taint_tags['sensitive']):
        """
        Create a sensitive taint tag.
        """
        return Taint(tag=tag, sources=sources)

    # @staticmethod
    # def clear(taint):
    #     """
    #     Clear the taint.
    #     """
    #     taint.tag = TaintOperator.taint_tags['insensitive']
    #     taint.sources = []

    @staticmethod
    def check(taint):
        """
        Check if the taint tag is sensitive.
        """
        if (taint is not None and taint.tag == TaintOperator.taint_tags['sensitive']):
            return True
        return False

    @staticmethod
    def get_sources(taint):
        """
        Get sources.
        """
        if (taint is not None):
            return taint.sources
        return []

    @staticmethod
    def merge_taint(taint1, taint2):
        """
        Merge taint2 into taint1.
        """
        taint1.sources = list(set(taint1.sources) | set(taint2.sources))
        taint1.flow_details = list(set(taint1.flow_details) | set(taint2.flow_details))
