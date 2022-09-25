import logging

from .taint_operator import TaintOperator
from smalien.utils.nops import Nop
from smalien.emulator.flow_detail_logger import FlowDetailLogger

logger = logging.getLogger(name=__name__)


class SourceApiDetector:
    """
    Detect sources based on API method names.
    """
    @staticmethod
    def run(inst, regs, clss, method, found_sources, taint_source_definition):
        """
        Check if the source of move-result is a taint source.

        :param inst: An object of move-result instruction
        """
        logger.debug('running')

        if (inst.source.kind != 'invoke'):
            return

        invoke = inst.source

        # TODO: Detect source APIs invoked by java.lang.Object's method.
        # if (invoke.class_name == 'Ljava/lang/Object;'):
        #     logger.error(invoke.last_invoked)

        detected, call_type = SourceApiDetector.detect_sources(invoke, taint_source_definition)

        if (detected):
            logger.warning(f'found taint source {invoke.class_name} {invoke.method_name}')

            # Add taint to the register
            regs[inst.destination].taint = TaintOperator.create(detected)

            # Flow logging
            FlowDetailLogger.write(f'[SOURCE] {call_type}, {detected}, {clss}, {method}, {invoke.num}\n')
            if (call_type == 'reflection'):
                regs[inst.destination].taint.flow_details.append('source-reflection')

            # Save the result
            found_sources.append({'name': detected,
                                  'clss': clss,
                                  'method': method,
                                  'num': invoke.num,
                                  'source_class': invoke.class_name,
                                  'source_method': invoke.method_name,
                                 })

    @staticmethod
    def detect_sources(invoke, taint_source_definition):
        """
        Return a list of detected sources.
        """

        sources = []
        call_type = None 

        # Compare API class and method names with the pre-defined list.
        candidate_apis = taint_source_definition.get(invoke.class_name)

        if (candidate_apis is not None and invoke.method_name in candidate_apis.keys()):
            sources = [candidate_apis[invoke.method_name]]
            call_type = 'normal'

        # For reflective calls
        elif (invoke.reflective_call_class is not None and invoke.reflective_call_method is not None):

            candidate_apis = taint_source_definition.get(invoke.reflective_call_class)

            if (candidate_apis is not None and invoke.reflective_call_method in candidate_apis.keys()):
                sources = [candidate_apis[invoke.reflective_call_method]]
                call_type = 'reflection'

            # # Clear the current reflective call data
            # invoke.reflective_call_class = None
            # invoke.reflective_call_method = None

        return sources, call_type

# This utility is moved to reflection_resolver.py
# class ReflectionSourceApiDetector:
#     """
#     Detect sources based on reflection method arguments.
#     """
#     @staticmethod
#     def run(inst, regs, clss, method, found_sources):
#         """
#         Check if the reflection-invoked method is a taint source.
#         """
#         logger.debug('running')
# 
#         # Check if the invocation is reflection
#         if (inst.class_name == 'Ljava/lang/reflect/Method;' and
#             inst.method_name == 'invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;'
#         ):
#             # Check if the invoked method is a taint source
#             invoked = regs[inst.arguments[0]]
#             source = taint_sources_in_java.get(invoked.value)
#             if (source is not None):
#                 logger.warning(f'reflection-based taint source is found, {source = }')
#                 # Register the found source to the invoke instruction data
#                 # This will be processed by SourceApiDetector handling move-result instructions
#                 inst.reflection_source = source

# This is for B3 seminar and is currently disabled
# class SourceConstDetector:
#     """
#     Detect sources based on const instruction.
#     """
#     @staticmethod
#     def run(inst, regs, clss, method, found_sources):
#         """
#         Detect and taint destination of the given const instruction.
#         """
#         # Check whether the instruction is one of target sources
#         # If not, stop the procedure
#         if (inst.instruction not in taint_source_instructions):
#             return
# 
#         logger.warning(f'found taint source {inst} {inst.destination}')
# 
#         # Add taint to the register
#         regs[inst.destination].taint = TaintOperator.create('CONST')
#         # Save the value at the source
#         regs[inst.destination].taint.values.append(inst.value)
# 
#         # Save the result
#         found_sources.append(TaintSource(name='CONST', clss=clss, method=method,
#                                          instruction=inst))

class SourceDetector:
    """
    This class detects taint sources to introduce taints.
    """

    def __init__(self, taint_source_definition):
        logger.debug('initializing')

        self.taint_source_definition = taint_source_definition

        self.mapping = {
            # 'const': SourceConstDetector,
            'move_result': SourceApiDetector,
            # 'invoke': ReflectionSourceApiDetector,
        }

        self.found_sources = []

    def run(self, **kwargs):
        """
        Run the detector.
        """
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']
        clss = kwargs['clss']
        method = kwargs['method']

        # Detect source based on instruction
        self.mapping.get(inst.kind, Nop).run(inst=inst, regs=registers,
                                             clss=clss, method=method,
                                             found_sources=self.found_sources,
                                             taint_source_definition=self.taint_source_definition)

        # Detect source based on values
        # TODO: Implement this.

    def get_found_sources(self):
        """
        Return results of detected sources.
        """
        return self.found_sources
