import logging
import re

from .structures import *
from .opcode_parser_utils import Utils
from ..definitions import RE_METHOD_ARG_TYPES #, SPECIAL_API_METHODS
from smalien.data_types import numeric_types_64

logger = logging.getLogger(name=__name__)


class OpInvokeParser:
    """
    Parse invoke-kind instructions.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        num = kwargs['num']
        line = kwargs['line']

        instruction = Utils.get_instruction(line)
        class_name, method_name = OpInvokeParser.get_class_method_name(line)

        # Identify a static invocation
        invoke_static = OpInvokeParser.identify_static(instruction)

        # Identify an invocation of constructor
        invoke_constructor = OpInvokeParser.identify_constructor(method_name)
        # Identify an invocation of super class's constructor method
        invoke_super_constructor = OpInvokeParser.identify_super_constructor(invoke_constructor,
                                                                             class_name,
                                                                             kwargs['super_class'])

        # Currently, smalien does not rely on this approach
        # Identify special API methods such as reflection and threading
        # method_kind = OpInvokeParser.identify_method_kind(class_name, method_name,
        #                                                   kwargs['classes'])

        # Check whether the method is implemented inside or outside the app.
        # If the method's class is in the ignore list, the method is considered as it is not implemented inside the app.
        in_app = OpInvokeParser.search_method_in_app(class_name, method_name,
                                                     kwargs['classes'])

        arguments = Utils.get_method_style_argument_vars(line)
        argument_data_types, arguments_without_64bit_pairs = OpInvokeParser.get_argument_data_types(arguments, instruction,
                                                                                                    class_name, method_name)
        ret_type = OpInvokeParser.get_return_value_type(method_name)

        op_invoke = OpInvoke(num=num, instruction=instruction,
                             arguments=arguments, argument_data_types=argument_data_types,
                             arguments_without_64bit_pairs=arguments_without_64bit_pairs,
                             class_name=class_name, method_name=method_name,
                             invoke_static=invoke_static,
                             invoke_constructor=invoke_constructor,
                             invoke_super_constructor=invoke_super_constructor,
                             in_app=in_app, ret_type=ret_type)

        # Generate a dummy OpMoveResult data
        # This will be overwritten later if a corresponding one exists
        op_move_result = OpMoveResult(num=num, source=op_invoke)
        # Register the op_move_result to the op_invoke
        op_invoke.move_result = op_move_result

        return op_invoke

    @staticmethod
    def get_class_method_name(line):
        """
        Extract the invoked class and method names.
        """
        class_method_str = line.split(', ')[-1]
        return class_method_str.split('->')[0], class_method_str.split('->')[1]

    @staticmethod
    def identify_static(instruction):
        if (instruction in ['invoke-static', 'invoke-static/range']):
            return True
        return False

    @staticmethod
    def identify_constructor(mname):
        if (mname.startswith('<init>(')):
            return True
        return False

    @staticmethod
    def identify_super_constructor(invoke_constructor, cname, super_class):
        if (invoke_constructor and cname == super_class):
            return True
        return False

    # Currently, smalien detects special methods without predefined lists.
    # This method is unused.
    # @staticmethod
    # def identify_method_kind(cname, mname, classes):
    #     """
    #     Identify special methods such as reflection and threading.
    #     """
    #     for key, methods in SPECIAL_API_METHODS.items():
    #         # Search for the given cname and mname
    #         matched = methods.get(cname, None)
    #         if (matched is not None and mname in matched):
    #             return key
    #         # Search for the given cname's parent
    #         # TODO: Implement recursive search or try classes[cname].family
    #         if (cname in classes.keys()):
    #             matched = methods.get(classes[cname].parent, None)
    #             if (matched is not None and mname in matched):
    #                 return key

    #     # If the method is not matched, default value, None, is returned

    @staticmethod
    def search_method_in_app(cname, mname, classes):
        """
        Check if the method is implemented within the app.
        """
        cdata = classes.get(cname, None)
        if (cdata is not None and not cdata.ignore):
            if (mname in cdata.methods.keys()):
                # If the class is abstract, the found method might not be invoked, even if it is implemented.
                # Therefore, return False.
                if (cdata.is_abstract):
                    return False
                return cdata.methods[mname].implemented

            # Being conservative, checking only the given class.
            # This is because even the given method is implemented in one of the family members,
            # a non-in-app method can be called.
            # This is for apps requiring to log the return value of method
            # else:
            #     for member in cdata.family:
            #         mem_data = classes.get(member, None)
            #         if (mem_data is not None and not mem_data.ignore):
            #             if (mname in mem_data.methods.keys() and mem_data.methods[mname].implemented):
            #                 return True

        return False

    @staticmethod
    def get_argument_data_types(arguments, instruction, class_name, method_name):
        """
        Extract the invoked method's arguments' data types.
        Also, create a list of arguments without 64-bit pairs.
        """
        num = 0
        data_types = {}
        arguments_without_64bit_pairs = []

        if (len(arguments) > 0):
            type_list = OpInvokeParser.get_data_type_list(method_name)
            if (instruction.find('static') < 0):
                type_list.insert(0, class_name)

            for arg_type in type_list:
                data_types[arguments[num]] = arg_type
                arguments_without_64bit_pairs.append(arguments[num])

                num += 1

                if (arg_type in numeric_types_64):
                    data_types[arguments[num]] = arg_type
                    num += 1

        return data_types, arguments_without_64bit_pairs

    @staticmethod
    def get_data_type_list(mname):
        """
        Extract the invoked method's argument types.
        """
        type_str = mname[mname.find('(')+1:mname.find(')')]
        pattern = re.compile(RE_METHOD_ARG_TYPES)
        return pattern.findall(type_str)

    @staticmethod
    def get_return_value_type(mname):
        """
        Extract the return value type.
        """
        return mname.split(')')[-1]

class OpInvokeUnknownParser:
    """
    Parse invoke-unknown instructions.
    """
    @staticmethod
    def run(**kwargs):
        assert False, f'Unknown instruction is found at {kwargs = }'
