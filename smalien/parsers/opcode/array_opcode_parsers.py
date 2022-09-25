import logging

from .structures import *
from .opcode_parser_utils import Utils

logger = logging.getLogger(name=__name__)


class OpAgetParser:
    """
    Parse aget instructions.
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
        array = Utils.get_second(line)
        index = Utils.get_last(line)

        # Currently, leave data types of source and array unknown
        # The index register is defined by const/4, which is I type.
        index_data_type = 'I'

        return OpAget(num=kwargs['num'], instruction=instruction,
                      destination=destination, array=array,
                      index=index, index_data_type=index_data_type)

class OpAputParser:
    """
    Parse aput instructions.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']

        instruction = Utils.get_instruction(line)
        source = Utils.get_first(line)
        array = Utils.get_second(line)
        index = Utils.get_last(line)

        # Currently, leave data types of source and array unknown
        # The index register is defined by const/4, which is I type.
        index_data_type = 'I'

        return OpAput(num=kwargs['num'], instruction=instruction,
                      source=source, array=array,
                      index=index, index_data_type=index_data_type)

class OpNewArrayParser:
    """
    Parse new-array instructions.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']

        instruction = Utils.get_instruction(line)
        array = Utils.get_first(line)
        size = Utils.get_second(line)

        # Get data types of the array and items
        array_data_type = Utils.get_last(line)
        assert array_data_type[0] == '[', f'Not an array, {line = }'
        item_data_type = array_data_type[1:]

        # Size register is definied by const/16, which is I type.
        size_data_type = 'I'

        # Note that array and size can be the same register.
        # If so, size is overwritten by array, and only array is kept after the execution.

        return OpNewArray(num=kwargs['num'], instruction=instruction,
                          array=array, array_data_type=array_data_type,
                          size=size, size_data_type=size_data_type,
                          item_data_type=item_data_type)

class OpFillArrayDataParser:
    """
    Parse fill-array-data instructions.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']

        instruction = Utils.get_instruction(line)
        array = Utils.get_first(line)
        label = Utils.get_last(line)

        return OpFillArrayData(num=kwargs['num'], instruction=instruction,
                               array=array, label=label)

class OpFilledNewArrayParser:
    """
    Parse filled-new-array instructions.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']

        instruction = Utils.get_instruction(line)
        arguments = Utils.get_method_style_argument_vars(line)
        ret_type = Utils.get_last(line)

        return OpFilledNewArray(num=kwargs['num'], instruction=instruction,
                                arguments=arguments, ret_type=ret_type)

class OpArrayLengthParser:
    """
    Parse array-length instructions.
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
        array = Utils.get_last(line)

        # The destination register's type is int
        destination_data_type = 'I'

        return OpArrayLength(num=kwargs['num'], instruction=instruction,
                             destination=destination, array=array,
                             destination_data_type=destination_data_type)
