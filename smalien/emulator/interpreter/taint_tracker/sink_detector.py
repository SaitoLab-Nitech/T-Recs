import logging
import copy
from collections import defaultdict

from .taint_operator import TaintOperator
from ..value_manager.structures import ClassInstanceValue
from smalien.utils.nops import Nop
from smalien.emulator.flow_detail_logger import FlowDetailLogger

logger = logging.getLogger(name=__name__)


class SinkApiDetector:
    """
    Detect sinks based on API method names.
    """
    @staticmethod
    def run(inst, registers, clss, method, class_data, after_invocation, found_sinks, taint_sink_definition):
        logger.debug('running')

        # Only process an invoke instruction once when after_invocation=False
        if (after_invocation):
            return

        # Compare API class and method names with the pre-defined list.
        # Decide invoked method's class
        if (inst.class_name == clss):
            # Invoked class name matches to self class, so use self class's super class.
            logger.info(f'replacing class name to {class_data.parent = }')
            invoked_class_name = class_data.parent
        else:
            invoked_class_name = inst.class_name

        detected = SinkApiDetector.detect_sink_api(invoked_class_name, inst.method_name, taint_sink_definition, inst, registers)
        if (detected):
            # The API method leaks data
            logger.warning('found a taint sink')
            logger.warning({'class': invoked_class_name, 'method': inst.method_name})
            logger.warning({'arguments': inst.arguments})

            # Flow logging
            FlowDetailLogger.write(f'[SINK] {clss}, {method}, {inst.num}, leaks:')

            # Update instruction's is_sink flag
            inst.is_sink = True

            # Check taint tags of the arguments
            sources = []
            sink_values = []
            try:
                for i, reg in enumerate(inst.arguments_without_64bit_pairs):
                    # If argument number is more than 1, skip base object for static method invocation.
                    if (len(inst.arguments) > 1 and i == 0 and not inst.invoke_static):
                        continue

                    tainted = TaintOperator.check(registers[reg].taint)

                    if (tainted):
                        logger.warning(registers[reg])

                        # Flow logging
                        regs_sources = set(registers[reg].taint.sources)
                        if ('PRE-SINK' in regs_sources):
                            regs_sources.remove('PRE-SINK')
                        FlowDetailLogger.write(f' {regs_sources}-{registers[reg].taint.flow_details}')

                        sources = list(set(sources) | regs_sources)
                        if (isinstance(registers[reg], ClassInstanceValue) and
                            registers[reg].string is not None):
                            sink_values.append(registers[reg].string)
                        else:
                            sink_values.append(registers[reg].value)

                # Flow logging
                FlowDetailLogger.write('\n')
                        

            except AttributeError as e:
                raise Exception(f'Lost {reg = } value at some point.') from e

            if (sources):
                # The arguments are tainted, and save the found sink
                found_sinks.append({'smali_tag': f'{class_data.cid}_{inst.num}',
                                    'clss': clss,
                                    'method': method,
                                    'num': inst.num,
                                    'sink_class': invoked_class_name,
                                    'sink_method': inst.method_name,
                                    'sink_values': sink_values,
                                    'sources': sources,
                                    'returned_value': None,
                                   })
                # logger.error(found_sinks[-1])
                # raise Exception('First sink')
                # if (len(found_sinks) > 1):
                #     raise Exception('Second sink')

        # Detect reflective call sinks.
        # DroidBench has no such case, and this function is currently disabled.
        # elif (inst.reflective_call_class is not None and inst.reflective_call_method is not None):
        #     candidate_apis = taint_sinks.get(inst.reflective_call_class)
        #     if (candidate_apis is not None and inst.reflective_call_method in candidate_apis.keys()):
        #         raise Exception('reflective call sink is found')

    @staticmethod
    def detect_sink_api(class_name, method_name, taint_sinks, inst=None, registers=None, support_combination=True):
        """
        Detect sink api.
        """
        if (class_name in taint_sinks.keys()):
            for sink_method, sink_type in taint_sinks[class_name].items():
                if (method_name.find(sink_method) > -1):

                    if (sink_type == 'sink'):
                        return True

                    if (support_combination):
                        if (sink_type == 'pre-sink'):
                            # The API method is a pre-sink, works with combination methods and leaks data.
                            # Assign a mark to its arguments
                            logger.warning('pre-sink is detected')
                            for reg in inst.arguments_without_64bit_pairs:
                                registers[reg].taint = TaintOperator.create(['PRE-SINK'], TaintOperator.taint_tags['insensitive'])
                                # registers[reg].taint.sources.append('PRE-SINK')
                            return False

                        elif (sink_type == 'combination'):
                            # The API method leaks data if its argument has been processed by a pre-sink method.
                            # Check if its argument has 'PRE-SINK' as its taint
                            for reg in inst.arguments_without_64bit_pairs:
                                if ('PRE-SINK' in TaintOperator.get_sources(registers[reg].taint)):
                                    logger.warning('combination sink is detected')
                                    return True

        return False

class SinkReturnedValueSaver:
    """
    Save returned values of sinks.
    """
    @staticmethod
    def run(inst, registers, clss, method, class_data, after_invocation, found_sinks, taint_sink_definition):
        logger.debug('running')

        if (inst.kind == 'invoke' and
            inst.source.is_sink and
            found_sinks and
            clss == found_sinks[-1]['clss'] and
            inst.source.num == found_sinks[-1]['num'] and
            found_sinks[-1]['returned_value'] is None
           ):
            if (isinstance(registers[inst.destination], ClassInstanceValue) and
                registers[inst.destination].string is not None):
                found_sinks[-1]['returned_value'] = registers[inst.destination].string
            else:
                found_sinks[-1]['returned_value'] = registers[inst.destination].value

            logger.warning(f'returned value is saved {found_sinks[-1]["returned_value"]}')

class SinkDetector:
    """
    This class detects taint sinks to uncover behaviors.
    """

    def __init__(self, classes, taint_sink_definition):
        logger.debug('initializing')

        self.classes = classes
        self.taint_sink_definition = taint_sink_definition

        self.mapping = {
            'invoke': SinkApiDetector,
            'move_result': SinkReturnedValueSaver,
        }

        self.found_sinks = []

    def run(self, **kwargs):
        """
        Run the detector.
        """
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']
        clss = kwargs['clss']
        method = kwargs['method']
        after_invocation = kwargs['after_invocation']

        class_data = self.classes[clss]

        # Detect sink based on API method name
        self.mapping.get(inst.kind, Nop).run(inst=inst, registers=registers,
                                             clss=clss, method=method,
                                             class_data=class_data,
                                             after_invocation=after_invocation,
                                             found_sinks=self.found_sinks,
                                             taint_sink_definition=self.taint_sink_definition)

    def get_found_sinks(self):
        """
        Return results of detected sinks.
        """
        return self.found_sinks

    def get_num_leaks(self):
        """
        Return the number of detected leaks.
        """
        unique_sinks = defaultdict(set)
        self.get_detected_leaks(unique_sinks)

        return sum([ len(sources) for sources in unique_sinks.values() ])

    def get_detected_leaks(self, unique_sinks):
        """
        Return detected leaks.

        :param uniques_sinks:  Detected leaks are saved to this dictionary (having set as default values).
        """
        for sink in self.found_sinks:
            sink_key = f'{sink["clss"]}-{sink["method"]}-{sink["num"]}'
            logger.debug(f'{sink_key = }')
            logger.debug(f'{sink["sources"] = }')

            unique_sinks[sink_key] |= set(sink['sources'])

        # return unique_sinks
