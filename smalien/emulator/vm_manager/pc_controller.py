import logging

from .exceptions import *
from smalien.data_types import string_types

logger = logging.getLogger(name=__name__)


class PCController:
    """
    Controll the program counter of a VM.
    """

    def __init__(self):
        logger.debug('initializing')

        self.mapping = {
            'if': self.if_branch,
            'ifz': self.ifz_branch,
            'goto': self.goto,
            'switch': self.switch,

            'throw': self.throw,
            'catch_label': self.catch_label,

            'invoke': self.invoke_method,
            'move_result': self.move_result,

            'return': self.finish_method,
            'method_tail': self.finish_method,
        }

    def run(self, **kwargs):
        """
        Return next PC based on the instruction type.
        """

        # Calculate PC based on the instruction kind
        return self.mapping.get(kwargs['inst'].kind, self.add_one)(**kwargs)

    def add_one(self, **kwargs):
        """
        Add one to the instruction's line number.
        Default method for most of the instructions.
        """
        return kwargs['inst'].num + 1

    def if_branch(self, **kwargs):
        """
        Branch is taken or not taken depending on the given expression result.
        """
        inst = kwargs['inst']
        registers = kwargs['registers']

        register_1_value = registers[inst.register_1].value
        register_2_value = registers[inst.register_2].value

        try:
            result = eval(inst.expression, {'register_1': register_1_value, 'register_2': register_2_value})
        except Exception as e:
            logger.warning('if_branch failed')
            logger.warning(inst)
            raise Exception(f'{register_1_value = }, {register_2_value = }') from e

        logger.info(f'{inst.expression = }')
        logger.info(f'{register_1_value = }, {register_2_value = }')

        if (result):
            # Branch is taken
            logger.info('branch is taken')
            return inst.destination.num

        # Branch is not taken
        logger.info('fall through')
        return self.add_one(**kwargs)

    def ifz_branch(self, **kwargs):
        """
        Branch is taken or not taken depending on the given expression result.
        """
        inst = kwargs['inst']
        registers = kwargs['registers']

        # Prepare the operand's value
        register_value = registers[inst.register].value
        # In DEX, null or '0' means 0
        if ((register_value == '0' and registers[inst.register].data_type not in string_types) or
            register_value == 'null'):
            register_value = 0

        try:
            result = eval(inst.expression, {'register': register_value})
        except Exception as e:
            logger.error('ifz_branch failed')
            logger.error(inst)
            raise Exception(f'{register_value = }') from e

        if (result):
            # Branch is taken
            logger.info(f'{inst.expression = } is true, and branch is taken')
            return inst.destination.num

        # Branch is not taken
        logger.info(f'{inst.expression = } is false, and fall through')
        return self.add_one(**kwargs)

    def goto(self, **kwargs):
        """
        Perform goto.
        """
        inst = kwargs['inst']

        return inst.destination.num

    def throw(self, **kwargs):
        """
        Perform throw.
        """

        raise ExceptionThrownException(kwargs['inst'])

    def catch_label(self, **kwargs):
        """
        Set False to sf.after_invocation at catch labels
        for cases that an invocation finished with an exception, and the corresponding move-result is skipped.
        """
        kwargs['sf'].after_invocation = False
        return self.add_one(**kwargs)

    def switch(self, **kwargs):
        """
        Jump to a target depending on the operand register value.
        """
        inst = kwargs['inst']
        registers = kwargs['registers']

        register_value = registers[inst.register].value

        if (register_value in inst.targets.keys()):
            return inst.targets[register_value].num

        # Branch is not taken
        return self.add_one(**kwargs)

    def invoke_method(self, **kwargs):
        """
        Send a signal telling a new method is invoked.
        TODO: Detect and skip time-wasting functions such as computePi()D from PI1 in DroidBench3.
        """
        sf = kwargs['sf']

        # An invoke instruction is reached
        # Decide action based on whether it is before or after the invocation.
        if (sf.after_invocation):
            # This is after the invocation, and proceed the emulation
            # Set False to the after_invocation flag to clear the state
            sf.after_invocation = False
            return self.add_one(**kwargs)
        else:
            # This is before the invocation, and raise the exception
            # Set True to the after_invocation flag
            sf.after_invocation = True

            raise NewMethodInvokedException(kwargs['inst'])

    def move_result(self, **kwargs):
        """
        Update the after_invocation flag to indicate that the invocation has been finished.
        """
        sf = kwargs['sf']
        inst = kwargs['inst']

        # This assumption is only for logging-based emulation
        # If the emulation is pure static, sf.after_invocation will always be True
        #
        # If the instruction's source is an invoke instruction, make sure that the flag is True
        # if (inst.source.kind == 'invoke'):
        #     assert sf.after_invocation, f'The after_invocation is not True'

        # Set False to the flag
        sf.after_invocation = False

        # Proceed the emulation
        return self.add_one(**kwargs)

    def finish_method(self, **kwargs):
        """
        Send a signal telling a method of the app is finished.
        """

        raise MethodEmulationCompletedException(kwargs['inst'])
