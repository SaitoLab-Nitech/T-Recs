import logging

from .relocator import Relocator
from .generator.generator import Generator
from .injector.injector import Injector

logger = logging.getLogger(name=__name__)


class Instrumentator():
    """
    It operates static bytecode instrumentation.
    """

    def __init__(self, app, log_buff_size, register_reassignment, multi_dex, taint_sources, dummy_source_values, use_shared_converter=True):
        logger.debug('initializing')

        self.app = app
        self.multi_dex = multi_dex
        # self.use_shared_converter = use_shared_converter
        self.use_shared_converter = False  # Disable all shared converters (i.e. using individual converters)

        self.converter_keys = set()  # Indicate necessary to-string-converter definitions

        self.generator = Generator(app,
                                   register_reassignment,
                                   self.use_shared_converter,
                                   self.converter_keys,
                                   taint_sources,
                                   dummy_source_values)
        self.injector = Injector(app,
                                 log_buff_size,
                                 multi_dex,
                                 self.use_shared_converter,
                                 self.converter_keys)
        self.relocator = Relocator(app)

    def run(self):
        """
        Execute the instrumentation.
        """
        logger.debug('running')

        self.generator.run()

        self.injector.run()

        # Relocate smali files
        if (self.multi_dex):
            self.relocator.run()

        # Remove code and payloads after the injection to keep pickle as minimum as possible
        for cdata in self.app.classes.values():
            del cdata.code
            del cdata.payloads
