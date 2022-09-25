import logging
import re

from .definitions import METHOD_ATTRIBUTES, IMPLEMENTEDS, RE_METHOD_ARG_TYPES
from ..structures import AppMethod
from .opcode.structures import OpMethodHead, OpMethodTail
from smalien.data_types import numeric_types_64

logger = logging.getLogger(name=__name__)


class MethodParser:
    """
    Parse app methods in smali files.
    """

    def __init__(self, clss, class_name, linage, code, methods):
        logger.debug('initializing')

        self.clss = clss
        self.class_name = class_name
        self.linage = linage
        self.code = code
        self.methods = methods

    def run(self):
        """
        Execute the parser for finding methods in a class.
        """
        logger.debug('running')

        i = 0
        while i < self.linage:
            line = self.code[i]

            if (line.startswith('.method')):
                head1 = line
                head2 = self.code[i+1]
                j = i
                while j < self.linage:
                    line = self.code[j]
                    if (line.startswith('.end method')):
                        try:
                            app_method = self.create(i, head1, head2, j)
                            self.methods[app_method.name] = app_method
                            break
                        except Exception as e:
                            raise Exception(f'Method parser failed, {i = }') from e
                    j += 1
                i = j + 1

            else:
                i += 1

    def create(self, start_at, head1, head2, end_at):
        """
        Create an object of the found method.
        """
        attr = self.get_method_attribute(head1)
        parameters, parameter_data_types = self.get_parameters(head1, attr)
        is_constructor = self.detect_constructor(head1)

        app_method = AppMethod(name=self.get_method_name(head1),
                               start_at=start_at,
                               end_at=end_at,
                               attribute=attr,
                               is_constructor=is_constructor,
                               implemented=IMPLEMENTEDS[attr],
                               parameters=parameters,
                               parameter_data_types=parameter_data_types,
                               ret_type=self.get_ret_type(head1),
                               local_reg_num=self.get_local_reg_number(head2, attr),
                               goto_label_num=0)

        # Add pseudo instructions for method head and tail
        app_method.instructions[start_at] = OpMethodHead(num=start_at, parameters=parameters,
                                                         parameter_data_types=parameter_data_types,
                                                         is_constructor=is_constructor,
                                                         attribute=attr)
        app_method.instructions[end_at] = OpMethodTail(num=end_at)

        # Detect special methods
        match app_method.name:
            # clinit()
            case '<clinit>()V':
                self.clss.clinit_implemented = True

            # toString()
            case 'toString()Ljava/lang/String;':
                self.clss.tostring_implemented = True

            # onLowMemory
            case 'onLowMemory()V':
                self.clss.onlowmemory = app_method

        return app_method

    def get_method_name(self, line):
        """
        Extract the method name.
        """
        return line.split(' ')[-1]

    def get_method_attribute(self, line):
        """
        Extract the method attribution.
        """
        for mattr in METHOD_ATTRIBUTES:
            if (line.find(mattr[0]) > -1):
                return mattr[1]

    def get_parameters(self, line, attribute):
        """
        Extract the method parameters.
        """
        num = 0
        params = []
        data_types = {}

        if (attribute != 'static'):
            p = 'p'+str(num)
            params.append(p)
            data_types[p] = self.class_name
            num += 1

        type_str = line[line.find('(')+1:line.find(')')]
        pattern = re.compile(RE_METHOD_ARG_TYPES)
        type_list = pattern.findall(type_str)

        for p_type in type_list:
            p = 'p'+str(num)
            params.append(p)
            data_types[p] = p_type
            num += 1
            if (p_type in numeric_types_64):
                p = 'p'+str(num)
                params.append(p)
                data_types[p] = p_type
                num += 1

        return params, data_types

    def detect_constructor(self, line):
        """
        Check whether the method is a constructor.
        """
        # TODO: Test this to check whether all constructors are detected.
        if (line.find(' constructor <init>') > -1):
            return True
        return False

    def get_ret_type(self, line):
        """
        Extract data type of the method return value.
        """
        return line.split(')')[-1]

    def get_local_reg_number(self, line, attribute):
        """
        Extract the number of the method local registers.
        """
        if (attribute in ['static', 'normal']):
            # Some smali files have ".registers" instead of ".locals"
            assert line.find('.locals') > -1 or line.find('.registers') > -1, (
                f'.locals or .registers not found but {line}')
            return int(line.split(' ')[-1])
        return 0
