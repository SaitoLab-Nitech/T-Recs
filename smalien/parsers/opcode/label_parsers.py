import logging

from .opcode_parser_utils import Utils
from .structures import *

logger = logging.getLogger(name=__name__)


class CondLabelParser:
    """
    Parse :cond_* labels.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']

        label = Utils.get_instruction(line)

        return CondLabel(num=kwargs['num'], instruction=label, label=label)

class GotoLabelParser:
    """
    Parse :goto_* labels.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']

        label = Utils.get_instruction(line)

        return GotoLabel(num=kwargs['num'], instruction=label, label=label)

class SwitchLabelParser:
    """
    Parse switch labels.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        if (kwargs['line'].find('_data_') > -1):
            return SwitchLabelParser.parse_switch_data(kwargs)
        else:
            return SwitchLabelParser.parse_switch_label(kwargs)

    @staticmethod
    def parse_switch_data(kwargs):
        """
        Parse :pswitch_data_* and :sswitch_data_* labels.
        """
        logger.debug('parsing a switch data')

        num = kwargs['num']
        code = kwargs['code']
        line = kwargs['line']

        label = Utils.get_instruction(line)

        if (label.startswith(':pswitch_data_')):
            targets = SwitchLabelParser.parse_packed_switch_payload(num, code)
        elif (label.startswith(':sswitch_data_')):
            targets = SwitchLabelParser.parse_sparse_switch_payload(num, code)
        else:
            raise Exception(f'unknown switch data is found, {line = }')

        return SwitchDataLabel(num=kwargs['num'], instruction=label, label=label,
                               targets=targets)

    @staticmethod
    def parse_packed_switch_payload(num, code):
        """
        Extract a packed-switch data from multiple lines.
        """
        # Start from the line next to the label
        i = num + 1
        assert code[i].find('.packed-switch') > -1, f'switch data extraction failed, {i = }, {code[i] = }'

        # Get the first (and lowest) switch case value.
        # It is n in the line of '.packed-switch n'
        case_value = int(Utils.get_last(code[i]), 16)

        # Trace code from the next line of '.packed-switch' until '.end packed-switch' is found
        i += 1
        targets = {}
        while True:
            line = code[i].lstrip()
            if (line == '.end packed-switch'):
                break
            targets[case_value] = line
            case_value += 1
            i += 1

        return targets

    @staticmethod
    def parse_sparse_switch_payload(num, code):
        """
        Extract a sparse-switch data from multiple lines.
        """
        # Start from the line next to the label
        i = num + 1
        assert code[i].find('.sparse-switch') > -1, f'switch data extraction failed, {i = }, {code[i] = }'

        # Trace code from the next line of '.sparse-switch' until '.end sparse-switch' is found
        i += 1
        targets = {}
        while True:
            line = code[i].lstrip()
            if (line == '.end sparse-switch'):
                break
            case_value = int(line.split(' -> ')[0], 16)
            target = line.split(' -> ')[1]
            targets[case_value] = target
            i += 1

        return targets

    @staticmethod
    def parse_switch_label(kwargs):
        """
        Parse :pswitch_* and :sswitch_* labels.
        """
        logger.debug('parsing a switch label')

        line = kwargs['line']

        label = Utils.get_instruction(line)

        return SwitchLabel(num=kwargs['num'], instruction=label, label=label)

class ArrayLabelParser:
    """
    Parse array-initializing data defined with :array_* labels.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        num = kwargs['num']
        code = kwargs['code']
        line = kwargs['line']

        label = Utils.get_instruction(line)
        array_data, element_width = ArrayLabelParser.get_array_data(num, code)

        return ArrayLabel(num=kwargs['num'], instruction=label, label=label,
                          array_data=array_data, element_width=element_width)

    @staticmethod
    def get_array_data(num, code):
        """
        Extract an array's data from multiple lines.
        """
        # Start from the line next to the label
        i = num + 1

        if (code[i].find('.array-data') < 0):
            logger.debug(f'array data extraction failed, {i = }, {code[i] = }')
            return [], None

        # Get the number of bytes in each element.
        # It is n in the line of '.array-data n'
        element_width = Utils.get_last(code[i])

        # Trace code from the next line of '.array-data' until '.end array-data' is found
        i += 1
        array_data = []
        while True:
            line = code[i].lstrip()
            if (line == '.end array-data'):
                break
            array_data.append(Utils.convert_hex_string_of_primitive_data(line))
            i += 1

        return array_data, element_width

# TODO: Match try and catch data
class TryLabelParser:
    """
    Parse try labels.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']

        label = Utils.get_instruction(line)

        if (label.startswith(':try_start_')):
            return TryStartLabel(num=kwargs['num'], instruction=label, label=label)
        elif (label.startswith(':try_end_')):
            return TryEndLabel(num=kwargs['num'], instruction=label, label=label)
        else:
            raise Exception(f'unknown try label is found, {label = }')

class CatchDataParser:
    """
    Parse catch data.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']

        label = Utils.get_instruction(line)

        exception, try_start_label, try_end_label, target = CatchDataParser.parse_data(line)

        return CatchData(num=kwargs['num'], instruction=label, exception=exception,
                         try_start_label=try_start_label, try_end_label=try_end_label,
                         target=target)

    @staticmethod
    def parse_data(line):
        """
        Extract exception, try_start_label, try_end_label, and target from the given .catch line.
        """

        exception = line.split(' {')[0].split(' ')[-1]
        try_start_label = line.split(' {')[-1].split(' .. ')[0]
        try_end_label = line.split(' .. ')[-1].split('} ')[0]
        target = line.split('} ')[-1]

        return exception, try_start_label, try_end_label, target

class CatchLabelParser:
    """
    Parse catch labels.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']

        label = Utils.get_instruction(line)

        return CatchLabel(num=kwargs['num'], instruction=label)
