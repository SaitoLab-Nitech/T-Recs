import logging

from .structures import *
from .opcode_parser_utils import Utils

logger = logging.getLogger(name=__name__)


class OpUnopParser:
    """
    Parse unop *-to-* vA, vB instructions.
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
        source = Utils.get_last(line)

        is_converter = True if instruction.find('-to-') > -1 else False

        java_style_source = instruction.split('-to-')[0] if is_converter else instruction.split('-')[1]
        java_style_destination = instruction.split('-to-')[1] if is_converter else instruction.split('-')[1]

        source_data_type = Utils.java_to_smali_data_type_styles_mapping[java_style_source]
        destination_data_type = Utils.java_to_smali_data_type_styles_mapping[java_style_destination]

        expression = Utils.unop_and_binop_expression_mapping[instruction]

        return OpUnop(num=kwargs['num'], instruction=instruction,
                      source=source, source_data_type=source_data_type,
                      destination=destination, destination_data_type=destination_data_type,
                      expression=expression, is_converter=is_converter)

class OpBinopParser:
    """
    Parse binop vAA, vBB, vCC instructions.
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
        source1 = Utils.get_second(line)
        source2 = Utils.get_last(line)

        data_type = Utils.java_to_smali_data_type_styles_mapping[instruction.split('-')[1]]
        expression = Utils.unop_and_binop_expression_mapping[instruction]

        return OpBinop(num=kwargs['num'], instruction=instruction,
                       source1=source1, source2=source2, destination=destination,
                       data_type=data_type, expression=expression)

class OpBinopLit8Parser:
    """
    Parse binop/lit8 vAA, vBB, #+CC instructions.
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
        source = Utils.get_second(line)
        literal = int(Utils.get_last(line), 16)

        data_type = Utils.java_to_smali_data_type_styles_mapping[instruction.split('-')[1].split('/')[0]]
        expression = Utils.unop_and_binop_expression_mapping[instruction.split('/')[0]]

        return OpBinopLit8(num=kwargs['num'], instruction=instruction,
                           source=source, literal=literal, destination=destination,
                           data_type=data_type, expression=expression)

class OpBinop2addrParser:
    """
    Parse binop/2addr vA, vB instructions.
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
        # The first register is the destination register
        # Hence, there is only second source register (i.e., source2) other than the destination
        source2 = Utils.get_last(line)

        data_type = Utils.java_to_smali_data_type_styles_mapping[instruction.split('-')[1].split('/')[0]]
        expression = Utils.unop_and_binop_expression_mapping[instruction]

        return OpBinop2addr(num=kwargs['num'], instruction=instruction,
                            source2=source2, destination=destination,
                            data_type=data_type, expression=expression)
