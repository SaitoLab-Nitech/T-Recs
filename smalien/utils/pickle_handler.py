import logging
import bz2
import pickle

logger = logging.getLogger(name=__name__)


class PickleHandler:
    """
    This class processes pickle files.
    """
    @staticmethod
    def load(path):
        """
        Load the app code from the pickle.
        """
        logger.debug(f'loading pickle from {path = }')

        with bz2.BZ2File(path, 'rb') as f:
            return pickle.load(f)

    @staticmethod
    def store(data, path):
        """
        Store the app code into a pickle.
        """
        logger.debug(f'storing pickle to {path = }')

        with bz2.BZ2File(path, 'wb') as f:
            pickle.dump(data, f)
