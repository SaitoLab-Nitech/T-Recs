import logging

from .reflection_resolver import ReflectionResolver
from .value_manager.value_manager import ValueManager
from .taint_tracker.taint_tracker import TaintTracker
from .flow_detail_detector import FlowDetailDetectorBeforeTaint, FlowDetailDetectorAfterTaint

logger = logging.getLogger(name=__name__)


class Interpreter:
    """
    This class runs various modules that interpret app's instructions.
    """

    def __init__(self, app, taint_source_definition, taint_sink_definition, detect_failures):
        logger.debug('initializing')

        # Initialize modules
        self.value_manager = ValueManager(app, detect_failures)
        self.taint_tracker = TaintTracker(app, taint_source_definition, taint_sink_definition, detect_failures)
        self.reflection_resolver = ReflectionResolver(app, detect_failures)
        self.flow_detail_detector_before_taint = FlowDetailDetectorBeforeTaint(app, detect_failures)
        self.flow_detail_detector_after_taint = FlowDetailDetectorAfterTaint(detect_failures, taint_source_definition)

        # Register modules
        self.modules = [
            self.reflection_resolver,
            self.value_manager,
            self.flow_detail_detector_before_taint,
            self.taint_tracker,
            self.flow_detail_detector_after_taint,
        ]
