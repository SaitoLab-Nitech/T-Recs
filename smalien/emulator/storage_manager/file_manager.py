import logging

from ..structures import DataFile

logger = logging.getLogger(name=__name__)


class FileManager:
    """
    Manage a file stored in the virtual storage.
    """

    def __init__(self):
        logger.debug('initializing')

    def new(self, name: str):
        return DataFile(name=name)
