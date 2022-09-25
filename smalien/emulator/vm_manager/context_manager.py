import copy
import logging

from .structures import StackFrame, StackFrameEntry
from .exceptions import StackIsEmptyException
from smalien.parsers.opcode.structures import OpMethodHead

logger = logging.getLogger(name=__name__)


class ContextManager:
    """
    Load and switch contexts of a VM.
    """

    def __init__(self, call_stack, classes):
        logger.debug('initializing')

        # Call stack of a corresponding vm data
        self.call_stack = call_stack
        # All classes data used to identify context
        self.classes = classes

        # Initialize the call stack with a dummy entry frame
        self.call_stack.append(StackFrameEntry())

    def create(self, clss, method, line, values={}):
        """
        Create a new stack frame.
        """
        logger.debug('creating a new stack frame')
        self.call_stack.append(StackFrame(clss=clss, method=method,
                                          pc=line, new_values=values))

        # Set the previous frame.
        # This is used by the argument-parameter value propagation at method calls.
        self.call_stack[-1].previous = self.call_stack[-2]

    def resume_with_new_data(self, clss, method, line=None, values={}):
        """
        Add a new frame or update the most recent frame with the new line and values.
        It depends on whether the stack only contains the dummy frame.
        """
        logger.debug('resuming the emulation with new information')

        if (len(self.call_stack) == 1):
            logger.debug('call stack is empty, and creating a new frame')
            # The stack only contains the dummy frame
            # Add a new frame
            self.create(clss, method, line, values)

            # This context can be a thread fork
            # Currently, thread forks are not explicitly detected

        else:
            # The stack contains frames other than the dummy frame

            next_inst = self.classes[clss].methods[method].instructions.get(line)

            # For debugging
            # if (clss == '' and method == '' and line == ):
            #     logger.error(f'analyzed {clss = }, {method = }, {line = }')
            #     sf = self.call_stack[-1]
            #     logger.error(f'  prev {sf.clss = }, {sf.method = }, {sf.pc = }')
            #     # if (line == 72):
            #     #     logging.getLogger('smalien').setLevel('DEBUG')
            #     # if (line == 81):
            #     #     raise Exception('break point')

            if (next_inst is not None and next_inst.kind == 'catch_label'):
                logger.debug('next instruction is catch_label')

                self.handle_exceptional_flow(clss, method, line, values)

            else:
                # Update the most recent frame in the stack
                # Check if the next instruction is method-head to detect whether previous and next instructions are in the same running method.
                sf = self.call_stack[-1]
                if (sf.clss == clss and sf.method == method and not isinstance(next_inst, OpMethodHead)):
                    self.handle_method_update(sf, clss, method, line, values)

                else:
                    # The error message is turned off because it sometimes uses a lot of memory.
                    assert isinstance(next_inst, OpMethodHead)#, f'invoked by {sf.clss = } {sf.method = } {sf.pc = }, the next must be a method head, but {next_inst = }'

                    self.handle_method_invocation(sf, clss, method, line, values)

    def handle_exceptional_flow(self, clss, method, line, values):
        """
        Detect destination frame of given exceptional flow.
        """
        # An exception has been thrown, and the execution might jump over multiple methods.
        # Find a right frame by popping unmatched frames.
        # Even if the class names are matched and method names are matched, the method could be recursively invoked, and the right frame cannot be detected.
        # Currently, if the exception-throwing instruction is not in any try block, the right frame can be detected.
        # In other cases, the right frame cannot be detected, which is a current limitation.

        # First, remove the latest block if the previous instruction is not in any try block.
        # Currently, this is implemented only for throw instruction.
        sf = self.call_stack[-1]
        prev_inst = self.classes[sf.clss].methods[sf.method].instructions.get(sf.pc)
        if (prev_inst.kind == 'throw' and not prev_inst.in_try_block):
            self.call_stack.pop()

        sf = self.call_stack[-1]
        # TODO: Add checking whether the previous instruction is in try block.
        #       But the approach is still limited because an exception may or may not be catched by the try block.
        while (sf.clss != clss or sf.method != method):
            # The frame does not match
            # logger.error(f'method finished by exception, {sf.clss = }, {sf.method = }')

            assert len(self.call_stack) > 1, f'Stack only has the StackFrameEntry {clss = }, {method = }, {line = }'

            # Remove it from the call stack and check the next frame
            self.call_stack.pop()
            sf = self.call_stack[-1]

        # Update the matched frame
        sf.pc = line
        sf.new_values = values

    def handle_method_update(self, sf, clss, method, line, values):
        """
        New runtime data is given for the same method as previous.
        """
        logger.debug('updating line and values of the most recent stack frame')
        # New data is provided, but the current method is not changed
        # Make sure that the old and new pcs are corresponding
        # This helps to find errors relating to the log manager
        # If the logs are not different more than two, the logs are fine
        if (line < sf.pc + 3):
            pass
        else:
            # Or the next inst is a move-result corresponding to the prev_inst, which is invoke, the logs are fine
            prev_inst = self.classes[clss].methods[method].instructions.get(sf.pc)
            if (prev_inst.kind == 'invoke' and prev_inst.move_result.num == line):
                pass
            else:
                raise Exception(f'New log {line = } is not corresponding with the previous {sf.pc = }')

        # Update pc
        sf.pc = line
    
        # Update values
        sf.new_values = values

    def handle_method_invocation(self, sf, clss, method, line, values):
        """
        A new method is invoked.
        """
        logger.debug(f'detected the invocation of {method = }')
        # New method is invoked, so create a new frame
        # TODO: Update method_kind

        if (method == '<clinit>()V'):
            # Previous instruction should be sget, sput, or new-instance, which will be verified by vm_runner after clinit is finished
            pass

        else:
            prev_inst = self.classes[sf.clss].methods[sf.method].instructions.get(sf.pc)

            # Check if the prev_inst is throw
            # If so, it means the exception has not been catched, and new method is starting
            if (prev_inst.kind == 'throw'):
                # Pop the previous frame
                self.call_stack.pop()

            else:
                # Otherwise, previous instruction must be new-instance or invoke-kind
                assert prev_inst.kind in ['new_instance', 'invoke'], (
                    f'{sf.clss = } {sf.method = } {sf.pc = } with '
                    f'not invoke-kind instruction {prev_inst = } invoking {clss = }, {method = }, {line = }, {values = }')

                # If the invoke instruction's in_app flag is False, set True to the flag
                if (prev_inst.kind == 'invoke' and not prev_inst.in_app):
                    logger.warning('changing in_app from False to True')
                    logger.warning(f'{prev_inst.class_name = }')
                    logger.warning(f'{prev_inst.method_name = }')
                    prev_inst.in_app = True

        # Create a new frame
        logger.debug('creating a new frame')
        self.create(clss, method, line, values)

    def switch_to_previous(self):
        """
        Switch the context by popping the most recent frame.
        """
        logger.info('switching the context to previous')

        # Remove the most recent frame
        removed_frame = self.call_stack.pop()

        logger.info(f'previous: {self.call_stack[-1].clss = }, '
                    f'{self.call_stack[-1].method = }, '
                    f'{self.call_stack[-1].pc = }')

        # Check if the stack has only the dummy frame.
        if (len(self.call_stack) == 1):

            raise StackIsEmptyException

        return removed_frame
