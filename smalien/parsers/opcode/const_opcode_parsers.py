import logging

from .structures import *
from .opcode_parser_utils import Utils

logger = logging.getLogger(name=__name__)


class OpConstNumericParser:
    """
    Parse const numeric instructions.
    const-string instructions are parsed by OpConstStringParser.
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

        value = Utils.extract_constant_value(destination, line, instruction)

        # Decide data type based on the instruction and value
        data_type = OpConstNumericParser.get_data_type(instruction, value)

        return OpConst(num=kwargs['num'], instruction=instruction,
                       destination=destination, data_type=data_type,
                       value=value)

    @staticmethod
    def get_data_type(instruction, value):
        """
        Get data type of the const instruction.
        """
        if (instruction.find('wide') > -1):
            if (isinstance(value, int)):
                return 'J'
            else:
                return 'D'
        return 'I'

class OpConstStringParser:
    """
    Parse const-string instructions.
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
        data_type = 'Ljava/lang/String;'

        value = Utils.extract_constant_value(destination, line, instruction)

        return OpConstString(num=kwargs['num'], instruction=instruction,
                             destination=destination, data_type=data_type,
                             value=value)

class OpConstClassParser:
    """
    Parse const-class instructions.
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
        class_name = Utils.get_last(line)
        value = f'class {class_name}'

        data_type = 'Ljava/lang/Class;'

        return OpConstClass(num=kwargs['num'], instruction=instruction,
                            destination=destination,
                            data_type=data_type,
                            class_name=class_name,
                            value=value)

class OpConstUnknownParser:
    """
    Alert const-unknown instructions.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        raise Exception(f"Unknown const is found, {kwargs['num'] = }, {kwargs['line'] = }")
