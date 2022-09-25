import logging

logger = logging.getLogger(name=__name__)


class CoverageCalculator:
    """
    Calculate the code coverage of the emulation.
    """

    def __init__(self, app):
        """
        Calculate the number of methods in the app.
        """
        self.method_num = 0
        self.count_method_number(app)

        self.explored_method = set()

    # TODO: This should be executed at the parsing phase
    def count_method_number(self, app):
        for clss, clss_data in app.classes.items():
            if (clss_data.ignore or
                clss.find('/R$') > -1 or
                clss.find('/R;') > -1 or
                clss.find('/BuildConfig;') > -1):
                continue
            for method, m_data in clss_data.methods.items():
                if (m_data.attribute not in ['native', 'abstract']):
                    # logger.warning(f'{clss}-{method}')
                    self.method_num += 1

    def save_explored_method(self, clss, method):
        self.explored_method.add(f'{clss}-{method}')

    def get_coverage(self):
        logger.warning(f'{len(self.explored_method) = }')
        logger.warning(f'{self.method_num = }')

        if (self.method_num == 0):
            return 0

        return len(self.explored_method) / self.method_num * 100
