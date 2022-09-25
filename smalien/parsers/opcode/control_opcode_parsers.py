import logging

from .opcode_parser_utils import Utils
from .structures import *

logger = logging.getLogger(name=__name__)


class OpIfParser:
    """
    Parse if-test vA, vB, +CCCC instructions.
    """

    # A translation table for getting expression of the given "ifz" instruction.
    expression_mapping = {
        'eq': 'register_1 == register_2',
        'ne': 'register_1 != register_2',
        'lt': 'register_1 < register_2',
        'ge': 'register_1 >= register_2',
        'gt': 'register_1 > register_2',
        'le': 'register_1 <= register_2',
    }

    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']

        instruction = Utils.get_instruction(line)
        register_1 = Utils.get_first(line)
        register_2 = Utils.get_second(line)
        label = Utils.get_last(line)

        try:
            expression = OpIfParser.expression_mapping[instruction.split('-')[1]]
        except KeyError as e:
            raise Exception(f'Failed to get expression for {instruction = }') from e

        return OpIf(num=kwargs['num'], instruction=instruction,
                    register_1=register_1, register_2=register_2, label=label,
                    expression=expression)

class OpIfzParser:
    """
    Parse if-testz vAA, +BBBB instructions.
    """

    # A translation table for getting expression of the given "ifz" instruction.
    expression_mapping = {
        'eqz': 'register == 0',
        'nez': 'register != 0',
        'ltz': 'register < 0',
        'gez': 'register >= 0',
        'gtz': 'register > 0',
        'lez': 'register <= 0',
    }

    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']

        instruction = Utils.get_instruction(line)
        register = Utils.get_first(line)
        label = Utils.get_last(line)

        expression = OpIfzParser.expression_mapping[instruction.split('-')[1]]

        return OpIfz(num=kwargs['num'], instruction=instruction,
                    register=register, label=label, expression=expression)


class OpGotoParser:
    """
    Parse goto instructions.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']

        instruction = Utils.get_instruction(line)
        label = Utils.get_last(line)

        return OpGoto(num=kwargs['num'], instruction=instruction, label=label)

class OpSwitchParser:
    """
    Parse switch instructions.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']

        instruction = Utils.get_instruction(line)
        register = Utils.get_first(line)
        data_label = Utils.get_last(line)

        return OpSwitch(num=kwargs['num'], instruction=instruction,
                        register=register, data_label=data_label)

class OpThrowParser:
    """
    Parse throw instructions.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']
        try_catch_level = kwargs['try_catch_level']

        instruction = Utils.get_instruction(line)
        register = Utils.get_last(line)

        # Moved to instruction_parser
        # in_try_block = True if (try_catch_level > 0) else False

        return OpThrow(num=kwargs['num'], instruction=instruction,
                       register=register)# , in_try_block=in_try_block)

class OpMoveExceptionParser:
    """
    Parse move-exception instructions.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        num = kwargs['num']
        instructions = kwargs['instructions']

        # Ignore cases that the previous label does not exist
        if (num-1 in instructions.keys()):
            assert (instructions[num-1].kind == 'catch_label' or
                   (instructions[num-1].kind == 'try_start_label' and instructions[num-2].kind == 'catch_label')), (
                   f'instruction previous to a move-exception is neither catch label or try-start label, but {instructions[num-1] = } and {instructions[num-2] = }')


        line = kwargs['line']

        instruction = Utils.get_instruction(line)
        destination = Utils.get_last(line)

        # TODO: Implement more precise typing
        destination_data_type = 'Ljava/lang/Throwable;'

        move_exception = OpMoveException(num=num, instruction=instruction,
                                         destination=destination, destination_data_type=destination_data_type)

        # Link this to the catch label
        if (num-1 in instructions.keys()):
            instructions[num-1].move_exception = move_exception

        return move_exception
