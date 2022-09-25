import logging

from .reflection_resolver import ReflectiveCallDetector
from .taint_tracker.taint_operator import TaintOperator
from .taint_tracker.source_detector import SourceApiDetector
from .value_manager.structures import ArrayInstanceValue
from ..flow_detail_logger import FlowDetailLogger

logger = logging.getLogger(name=__name__)


ICC_CLASSES = [
    'Landroid/app/Activity;',
    'Landroid/content/Context;',
]

class FlowDetailDetectorBeforeTaint:

    def __init__(self, app, detect_failures):
        logger.debug('initializing')

        self.classes = app.classes
        self.detect_failures = detect_failures

    def run(self, **kwargs):
        """
        Detect flow details for logging before tainting.
        """
        inst = kwargs['inst']
        if (inst.kind != 'invoke'):
            return

        if (kwargs['sf'].after_invocation):
            return

        try:
            self.detect(**kwargs)
        except Exception as e:
            # raise e

            if (self.detect_failures):
                raise e
            else:
                # Ignore the failure
                pass

    def detect(self, **kwargs):

        inst = kwargs['inst']
        clss = kwargs['sf'].clss
        method = kwargs['sf'].method
        registers = kwargs['sf'].registers

        # ICC (1)
        if (inst.class_name == clss):
            # Invoked class name matches to self class, so use self class's super class.
            invoked_class_name = self.classes[clss].parent
        else:
            invoked_class_name = inst.class_name
        if (invoked_class_name in ICC_CLASSES and
            inst.method_name == 'startActivity(Landroid/content/Intent;)V'):
            # Check if the second argument is tainted
            tainted = TaintOperator.check(registers[inst.arguments[1]].taint)
            if (tainted):
                FlowDetailLogger.write(f'[ICC_STARTACTIVITY_ARG] {clss}, {method}, {inst.num}\n')
                # Update flow details
                registers[inst.arguments[1]].taint.flow_details.append('icc-startactivity-arg')
            return

        # ICC (2)
        if (inst.class_name == 'Landroid/os/Messenger;' and
            inst.method_name == 'send(Landroid/os/Message;)V'):
            # Check if the second argument is tainted
            tainted = TaintOperator.check(registers[inst.arguments[1]].taint)
            if (tainted):
                FlowDetailLogger.write(f'[ICC_SEND_ARG] {clss}, {method}, {inst.num}\n')
                # Update flow details
                registers[inst.arguments[1]].taint.flow_details.append('icc-send-arg')
            return

        # Reflection (4)
        is_reflective_call = ReflectiveCallDetector.detect_reflective_calls(inst)
        if (is_reflective_call):
            # Check if the third argument is tainted
            if (isinstance(registers[inst.arguments[2]], ArrayInstanceValue)):
                for element in registers[inst.arguments[2]].elements:
                    tainted = TaintOperator.check(element.taint)
                    if (tainted):
                        FlowDetailLogger.write(f'[REFLECTION_ARG] {clss}, {method}, {inst.num}\n')
                        # Update flow details
                        element.taint.flow_details.append('reflection-arg')

class FlowDetailDetectorAfterTaint:

    def __init__(self, detect_failures, taint_source_definition):
        logger.debug('initializing')

        self.detect_failures = detect_failures
        self.taint_source_definition = taint_source_definition

    def run(self, **kwargs):
        """
        Detect flow details for logging after tainting.
        """
        inst = kwargs['inst']
        if (inst.kind != 'move_result'):
            return
        if (inst.source.kind != 'invoke'):
            return

        # Skip if invoked method is source
        detected, call_type = SourceApiDetector.detect_sources(inst.source, self.taint_source_definition)
        if (detected):
            logger.debug(f'skipping taint souce {detected}, {call_type}')
            return

        try:
            self.detect(**kwargs)
        except Exception as e:
            # raise e

            if (self.detect_failures):
                raise e
            else:
                # Ignore the failure
                pass

    def detect(self, **kwargs):

        inst = kwargs['inst']
        clss = kwargs['sf'].clss
        method = kwargs['sf'].method
        registers = kwargs['sf'].registers

        # Reflection (3)
        is_reflective_call = ReflectiveCallDetector.detect_reflective_calls(inst.source)
        if (is_reflective_call):
            # Check if the second argument is tainted
            tainted = TaintOperator.check(registers[inst.destination].taint)
            if (tainted):
                FlowDetailLogger.write(f'[REFLECTION_RET] {clss}, {method}, {inst.source.num}, {inst.num}\n')
                # Update flow details
                registers[inst.destination].taint.flow_details.append('reflection-ret')

        # Reflection (5)
        # Logged by SourceApiDetector
