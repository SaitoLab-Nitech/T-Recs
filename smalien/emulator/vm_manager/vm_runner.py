import logging

"""
Testing pprint with logging
"""
from pprint import pformat
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import Terminal256Formatter
from pygments.styles import get_style_by_name

from .pc_controller import PCController
from .context_manager import ContextManager
from .exceptions import *
from ..interpreter.taint_tracker.taint_operator import TaintOperator
from smalien.utils.pretty_printer import PrettyPrinter

logger = logging.getLogger(name=__name__)


class VMRunner:
    """
    Run a VM with specified PID and TID.
    """

    def __init__(self, vm, vms, classes, clss, method, line, logging, interpreters, detect_failures):
        logger.debug('initializing')
        self.vm = vm

        # Used for cases in that accessing other vms' data is required (e.g., threading)
        self.vms = vms

        self.classes = classes
        self.logging = logging
        self.interpreters = interpreters
        self.detect_failures = detect_failures

        # Initialize utility modules
        self.pc_controller = PCController()
        self.context_manager = ContextManager(self.vm.call_stack, self.classes)

        # Initialize pretty printer
        self.pprinter = PrettyPrinter()

    def run(self, **kwargs):
        """
        Execute the runner.

        :param clss:        App's class at that the emulation begins.
        :param method:      App's method at that the emulation begins.
        :param line:        App's line at that the emulation begins.
        :param values:      App's runtime values logged at the line.
        :param logging:     Flag indicating whether to use runtime values.
        """
        clss = kwargs['clss']
        method = kwargs['method']
        line = kwargs['line']
        values = kwargs['values']

        self.logging = kwargs['logging']

        logger.info(f'starting a vm {clss = }, {method = }, {line = }, {values = }')

        # Resume the emulation with the new clss, method, line, and values
        try:
            self.context_manager.resume_with_new_data(clss, method, line, values)
        except StackIsEmptyException as e:
            raise e
        except Exception as e:
            if (self.detect_failures):
                raise e
            else:
                # Ignore the failure, and create a new frame
                # self.context_manager.create(clss, method, line, values)
                raise LogPointException()  # Trying this one

        while True:

            # Run interpreter modules with the context
            try:
                self.emulate_a_method()

            except NewMethodInvokedException as e:
                logger.info(f'invoking new method {e.args[0].class_name = }, {e.args[0].method_name = }')

                invocation_data = e.args[0]
                # logger.info(invocation_data)

                # Make sure that the after_invocation flag is True, which is assigned by PCController
                assert self.vm.call_stack[-1].after_invocation == True, 'error: after_invocation is False at a new method starting'

                # If smalien is performing dynamic analysis, logs must be available for the invocation
                # Hence, exit the emulation
                if (self.logging):
                    logger.info('logging is enabled, and break the emulation')
                    raise LogPointException(invocation_data)

                else:
                    # smalien is performing static analysis
                    # If the invoked method is implemented within the app, add a new frame and continue the emulation
                    invocation_data = e.args[0]
                    if (invocation_data.in_app):
                        logger.info('logging is disabled, and an in-app method is invoked')

                        clss = invocation_data.class_name
                        method = invocation_data.method_name
                        line = self.classes[clss].methods[method].start_at
                        self.context_manager.create(clss, method, line)
                    else:
                        # The invoked method is an API method
                        logger.info('logging is disabled, and an API method is invoked')

                        # For compatibility with dynamic analysis, the invoke should be executed twice.
                        # Hence, keep the current pc.

                        # TODO: Remove below after testing static analysis
                        # Increment the current frame's pc and continue the emulation
                        # self.context_manager.resume_with_new_data(clss, method, invocation_data.num+1)

            except MethodEmulationCompletedException as e:
                logger.info('method emulation is completed')
                # logger.info(e.args[0])

                # switch the execution to the previous frame
                removed_frame = self.context_manager.switch_to_previous()

                # If the finished method is clinit, and next method's last instruction is
                # sget, sput, or new-instance, the emulation must start at there.
                # If the instruction is a logging target, break the emulation.
                # Otherwise, continue the emulation starting at the instruction.
                if (removed_frame.method == '<clinit>()V'):
                    sf = self.vm.call_stack[-1]
                    inst = self.classes[sf.clss].methods[sf.method].instructions.get(sf.pc)
                    if (inst.kind in ['sget', 'sput', 'new_instance']):
                        if (self.logging and inst.logging):
                            logger.info('logging is enabled, and break the emulation')
                            raise LogPointException(e.args[0])

                        continue

                # Make sure that the instruction is new-instance or after_invocation flag is True, which is assigned by PCController
                sf = self.vm.call_stack[-1]
                inst = self.classes[sf.clss].methods[sf.method].instructions.get(sf.pc)

                if (self.detect_failures):
                    assert inst.kind == 'new_instance' or self.vm.call_stack[-1].after_invocation == True, (
                        f'after_invocation is False at {self.vm.call_stack[-1].clss = } {self.vm.call_stack[-1].method = } {self.vm.call_stack[-1].pc = }, '
                        f'returning from {removed_frame.clss = } {removed_frame.method = } {removed_frame.pc = }')
                else:
                    # Ignore failures and fix it.
                    if (inst.kind != 'new_instance'):
                        self.vm.call_stack[-1].after_invocation = True

                # If smalien is performing dynamic analysis, logs must be available at the return target
                # Hence, exit the emulation
                if (self.logging):
                    logger.info('returning from a non-clinit method, logging is enabled, and break the emulation')
                    raise LogPointException(e.args[0])
                else:
                    logger.info('logging is disabled, and continue the emulation')
                    # For compatibility with dynamic analysis, the invoke should be executed twice.
                    # Hence, keep the current pc of the previous frame.

    def emulate_a_method(self):
        """
        Start emulating from the specified line to lines within a method.
        Finish if next PC points to a different method.
        """
        # Load the most recent stack frame
        sf = self.vm.call_stack[-1]

        # A SF could be too large to print
        # logger.debug(sf)

        # Load first instruction
        inst = self.classes[sf.clss].methods[sf.method].instructions.get(sf.pc)

        # Skip a time-wasting method by causing MethodEmulationCompletedException
        # TODO: Implement the full skipper
        if (sf.clss == 'Lcom/example/newedtester/MainActivity;' and sf.method == 'computePi()D'):
            logger.info('skipping a time-wasting method')

            raise MethodEmulationCompletedException(inst)

        while True:

            # Execute the instruction and update PC
            sf.pc = self.run_single_step(inst, sf)

            # Get next instruction at the line of PC
            inst = self.classes[sf.clss].methods[sf.method].instructions.get(sf.pc)

            # Check the next instruction before emulating it.
            # Break if it reaches a log point in a middle of the method.
            # Currently, API field accesses and instance-of instructions are the case.
            #   and more now.
            if (self.logging and inst is not None):
                if (inst.kind in ['iget', 'sget', 'sput'] and inst.logging):#not inst.in_app):
                    logger.info('a log point (iget, sget, or sput) is reached in a middle of the method')
                    raise LogPointException(inst)
                if (inst.kind == 'new_instance' and inst.logging):
                    logger.info('a log point (new-instance) is reached in a middle of the method')
                    raise LogPointException(inst)
                if (inst.kind == 'instance_of'):
                    logger.info('a log point (instance-of) is reached in a middle of the method')
                    raise LogPointException(inst)
                if (inst.kind == 'check_cast'):
                    logger.info('a log point (check-cast) is reached in a middle of the method')
                    raise LogPointException(inst)
                if (inst.kind == 'const_string'):
                    logger.info('a log point (const-string) is reached in a middle of the method')
                    raise LogPointException(inst)
                if (inst.kind == 'const_class'):
                    logger.info('a log point (const-class) is reached in a middle of the method')
                    raise LogPointException(inst)
                if (inst.kind == 'monitor_enter' and inst.logging):
                    logger.info('a log point (monitor-enter) is reached in a middle of the method')
                    raise LogPointException(inst)
                if (inst.kind == 'array_length' and inst.logging):
                    logger.info('a log point (array_length) is reached in a middle of the method')
                    raise LogPointException(inst)
                if (inst.kind == 'catch_label' and inst.logging):
                    logger.info('a log point (catch_label) is reached in a middle of the method')
                    raise LogPointException(inst)

    def run_single_step(self, inst, sf):
        """
        Perform a single step of the emulation.
        """

        # For debugging
        # if (sf.clss == '' and sf.method == '' and sf.pc == ):
        #     raise Exception('break point')

        # Only adding PC if inst is None
        if (inst is None):
            return sf.pc + 1

        logger.info(f'running a single step {sf.pc = }, {sf.after_invocation = }')
        logger.info(f'{sf.clss = }')
        logger.info(f'{sf.method = }')
        logger.info(inst)

        # Execute interpreter modules
        for module in self.interpreters:
            module.run(inst=inst, sf=sf,
                       instances=self.vm.instances,
                       static_fields=self.vm.static_fields,
                       intent_data=self.vm.intent_data,
                       vm=self.vm,
                       self_ptids=self.vm.ptids,
                       vms=self.vms)

        logger.info('interpreters finished')
        logger.info(sf.registers.keys())
        logger.debug(sf.registers)

        if (0 in self.vm.instances.keys()):
            logger.error(f'{len(self.vm.instances[0]) = }')
            logger.error(self.vm.instances[0][0])
            raise Exception('0 must not exist in self.vm.instances')

        # For debugging
        # if (inst.kind == 'method_head'):
        #     logger.error(f'{sf.clss = }')
        #     logger.error(f'{sf.method = }')
        #     logger.error(f'{sf.pc = }')
        #     logger.error(sf.registers)

        # if (hasattr(inst, 'is_sink') and inst.is_sink):
        #     raise Exception('SINK')

        # logger.error(self.vm.intent_data)

        # TODO: Implement break point function
        # if (sf.clss == '' and sf.method == '' and sf.pc == ):
        #     raise Exception('break point')

        # Update the PC based on the instruction kind
        try:
            return self.pc_controller.run(inst=inst, registers=sf.registers, sf=sf)
        except ExceptionThrownException as e:
            raise e
        except NewMethodInvokedException as e:
            raise e
        except MethodEmulationCompletedException as e:
            raise e
        except Exception as e:
            if (self.detect_failures):
                raise e
            else:
                # Ignore the failure, and force stop the emulation
                # return sf.pc + 1  # This keeps the analysis running (e.g., for 15 hours)
                # raise MethodEmulationCompletedException(inst)  # This seems working good for 2021, but not for agrigento
                raise LogPointException(inst)  # Try this one
