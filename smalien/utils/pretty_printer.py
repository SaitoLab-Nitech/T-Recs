import logging
from prettyprinter import cpprint, install_extras, set_default_style
from pygments.styles import get_style_by_name

logger = logging.getLogger(name=__name__)


class PrettyPrinter:
    """
    Use prettyprinter module to print dataclasses objects.
    """
    # TODO: Use pprint in Python 3.10, which can print dataclasses.
    # Tested once, but its highlighting was bad.
    # Need more work to print in better highlighting.
    # from pprint import pformat
    # from pygments import highlight
    # from pygments.lexers import PythonLexer
    # from pygments.formatters import Terminal256Formatter
    # logger.debug('\n'+highlight(pformat(sf.registers), PythonLexer(), Terminal256Formatter()))

    def __init__(self, app=None):
        logger.debug('initializing')

        self.app = app

        # Enable printing of dataclasses.
        install_extras(include=['dataclasses'])

        # Set color style
        set_default_style(get_style_by_name('material'))

    def pprint_data(self, data):
        """
        Print data.
        """
        cpprint(data, sort_dict_keys=True)

    def pprint_app(self, kwargs):
        """
        Print the app code to the stdout.

        :param smali_path: Path to a smali file to be printed.
        """
        logger.debug('pretty printing the app')

        print('\n ---- app data ----')
        if ('smali_path' in kwargs.keys()):
            if ('method' in kwargs.keys()):
                self.pprint_data(self.app.classes[kwargs['smali_path']].methods[kwargs['method']])
            else:
                self.pprint_data(self.app.classes[kwargs['smali_path']])
        else:
            self.pprint_data(self.app)
        print('')
