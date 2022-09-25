import logging
from pprint import pformat
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.styles import get_style_by_name
from pygments.formatters import Terminal256Formatter
from dataclasses import is_dataclass


class Loggers:
    """
    It manages loggers.
    """

    def __init__(self, default_level=logging.WARNING):
        self.default_level = default_level
        self.handler = logging.StreamHandler()
        # self.handler.setFormatter(CustomFormatter(
        #     "%(asctime)-23s | %(levelname)-7s | %(name)s:%(lineno)s | %(message)s"))
        self.handler.setFormatter(CustomFormatter(
            "%(levelname)-7s | %(module)s:%(lineno)s | %(message)s"))

        # Currently not used because logs are mixed in multiple apps
        # # Add a filter to drop flow detail logs
        # self.handler.addFilter(FlowDropper())

        self.enable_root_logger()
        logging.root.setLevel(self.default_level)

    def enable_root_logger(self):
        logging.root.addHandler(self.handler)

class CustomFormatter(logging.Formatter):
    """
    Format and colorize data of dataclasses and dictionaries.
    """

    def format(self, record):
        if (is_dataclass(record.msg) or isinstance(record.msg, dict)):
            record.msg = '\n'+highlight(pformat(record.msg, width=200, depth=4, compact=True), PythonLexer(),
                                        Terminal256Formatter(style=get_style_by_name('material')))

        return super().format(record)

# class FlowFilter():
#     def filter(self, record):
#         return record.getMessage().startswith('[FLOW]')
# 
# class FlowDropper():
#     def filter(self, record):
#         return not record.getMessage().startswith('[FLOW]')
