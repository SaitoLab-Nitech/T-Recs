import logging

from .file_manager import FileManager
from ..structures import Storage

logger = logging.getLogger(name=__name__)


class StorageManager:
    """
    Manage virtual storage that can be accessed globally.
    Objects:
        * files
        * unmonitored memories (TODO: implement this.)
    """

    def __init__(self):
        logger.debug('initializing')

        self.storage = Storage()
        self.file_manager = FileManager()

    def get_storage(self):
        return self.storage
