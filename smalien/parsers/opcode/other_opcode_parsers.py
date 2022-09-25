import logging

from .structures import *
from .opcode_parser_utils import Utils

logger = logging.getLogger(name=__name__)


class OpMoveResultParser:
    """
    Parse move-result instructions.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']

        instruction = Utils.get_instruction(line)
        destination = Utils.get_last(line)

        return OpMoveResult(num=kwargs['num'], instruction=instruction,
                            destination=destination)

class OpNewInstanceParser:
    """
    Parse new-instance instructions.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']

        instruction = Utils.get_instruction(line)
        destination = Utils.get_first(line)
        class_name = Utils.get_latter_half(destination, line)

        return OpNewInstance(num=kwargs['num'], instruction=instruction,
                             destination=destination, class_name=class_name)

class OpInstanceOfParser:
    """
    Parse instance-of instructions.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']

        instruction = Utils.get_instruction(line)
        source = Utils.get_second(line)
        class_name = Utils.get_last(line)
        destination = Utils.get_first(line)

        # destination will be 1 if the source is an instance of class_name, or 0 if not
        # currently, assume that the data type is integer
        destination_data_type = 'I'

        return OpInstanceOf(num=kwargs['num'], instruction=instruction,
                            source=source, class_name=class_name,
                            destination=destination, destination_data_type=destination_data_type)

class OpMoveParser:
    """
    Parse move instructions.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']

        instruction = Utils.get_instruction(line)
        source = Utils.get_last(line)
        destination = Utils.get_first(line)

        return OpMove(num=kwargs['num'], instruction=instruction,
                      source=source, destination=destination)

class OpReturnParser:
    """
    Parse return instructions.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']

        instruction = Utils.get_instruction(line)
        register = OpReturnParser.get_return_value_register(instruction, line)

        return OpReturn(num=kwargs['num'], instruction=instruction,
                        register=register)

    @staticmethod
    def get_return_value_register(instruction, line):
        """
        Get return value register of the given instruction.
        If the given instruction is "return-void", there is no register.
        """
        last_item = Utils.get_last(line)
        if (instruction == last_item):
            return None
        return last_item

class OpNopParser:
    """
    Parse nop instructions.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']

        instruction = Utils.get_instruction(line)

        return OpNop(num=kwargs['num'], instruction=instruction)


class OpMonitorEnterParser:
    """
    Parse monitor-enter instructions.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']

        instruction = Utils.get_instruction(line)
        register = Utils.get_last(line)

        return OpMonitorEnter(num=kwargs['num'], instruction=instruction,
                              register=register)

class OpMonitorExitParser:
    """
    Parse monitor-exit instructions.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']

        instruction = Utils.get_instruction(line)
        register = Utils.get_last(line)

        return OpMonitorExit(num=kwargs['num'], instruction=instruction,
                             register=register)


class OpCheckCastParser:
    """
    Parse check-cast instructions.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        num = kwargs['num']
        line = kwargs['line']
        instructions = kwargs['instructions']

        instruction = Utils.get_instruction(line)
        reg = Utils.get_first(line)
        class_name = Utils.get_last(line)

        move_result_matched = False

        # check-cast instruction checks whether the register can be cast to the data_type.
        # Hence, the register's type is unknown.
        # However, the register is likely the data_type.
        # Save the castable data type if the registers are the same.
        prev_inst = instructions.get(num-2)
        if (prev_inst is not None):
            if (prev_inst.kind == 'move_result'):
                if (prev_inst.destination == reg):
                    prev_inst.castable_to = class_name
                    move_result_matched = True
            elif (prev_inst.kind in ['iget', 'sget']):
                if (prev_inst.destination == reg):
                    prev_inst.castable_to = class_name

        return OpCheckCast(num=kwargs['num'], instruction=instruction,
                           register=reg, class_name=class_name,
                           move_result_matched=move_result_matched)
