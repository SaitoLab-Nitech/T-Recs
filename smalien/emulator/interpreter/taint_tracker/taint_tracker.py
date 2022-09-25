import logging

from .recorder import Recorder
from .propagator.propagator import Propagator
from .source_detector import SourceDetector
from .sink_detector import SinkDetector

logger = logging.getLogger(name=__name__)


class TaintTracker:
    """
    This class runs taint logics that interpret app's instructions.
    """

    def __init__(self, app, taint_source_definition, taint_sink_definition, detect_failures):
        logger.debug('initializing')

        self.app = app
        self.detect_failures = detect_failures

        # Initialize modules
        self.source_detector = SourceDetector(taint_source_definition)
        self.sink_detector = SinkDetector(self.app.classes, taint_sink_definition)
        self.propagator = Propagator()
        self.recorder = Recorder()

        # Register modules
        # If a module processes instructions that inst.kind=invoke, after_invocation flag should be considered.
        # A step where after_invocation = True can be skipped, if there is a corresponding move-result.
        self.taint_logics = [
            # The ordering can affect the tracking performance
            self.source_detector,
            self.sink_detector,
            self.propagator,
            self.recorder,
        ]

    def run(self, **kwargs):
        """
        Run the taint logics.
        """

        inst = kwargs['inst']
        sf = kwargs['sf']
        static_fields = kwargs['static_fields']
        intent_data = kwargs['intent_data']

        try:
            for taint_logic in self.taint_logics:
                taint_logic.run(inst=inst, registers=sf.registers, new_values=sf.new_values,
                                clss=sf.clss, method=sf.method, static_fields=static_fields,
                                intent_data=intent_data, after_invocation=sf.after_invocation)
        except Exception as e:
            # raise e

            if (self.detect_failures):
                raise e
            else:
                # Ignore the failure
                pass
