import logging

from .structures import *
from .opcode_parser_utils import Utils

logger = logging.getLogger(name=__name__)


class OpCmpParser:
    """
    Parse cmpkind vAA, vBB, vCC instructions.
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

        try:
            source_data_type = Utils.java_to_smali_data_type_styles_mapping[instruction.split('-')[1]]
        except KeyError as e:
            raise Exception(f'Failed to get data type, {instruction = }') from e

        # Destination is 8 bits, which assumed that data type is byte (B)
        destination_data_type = 'B'

        return OpCmp(num=kwargs['num'], instruction=instruction,
                     source1=source1, source2=source2, source_data_type=source_data_type,
                     destination=destination, destination_data_type=destination_data_type)
