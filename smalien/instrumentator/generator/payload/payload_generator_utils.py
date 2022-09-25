import logging

from .structures import PayloadLocals, PayloadMove, PayloadMoveResult, PayloadMoveException, PayloadGoto, PayloadGotoExtra, PayloadGotoLabel, PayloadGotoLabelExtra, PayloadCondLabel, PayloadLogging, PayloadDummyReturnedValue
from .definitions import SMALIEN_LOG_CLASS, CODE_WITHOUT_VL, CODE_WITH_VL
from .definitions_for_individual_converter import CODE_WITH_VL_FOR_INDIVIDUAL_CONVERTER
from smalien.data_types import primitive_data_types, numeric_types_64, string_types, string_types_array, DATA_TYPES_IMPLEMENTED_INDIVIDUAL_CONVERTER

logger = logging.getLogger(name=__name__)


class Utils:
    """
    Utility class of Payload*Generator.
    """
    @staticmethod
    def generate_locals(num, original, increase):
        """
        Generate a .locals line to be injected.
        """
        value = original + increase
        return PayloadLocals(num=num, code=f'    .locals {value}', increase=increase)

    @staticmethod
    def generate_move(num, move_result, original_dst, new_dst):
        """
        Generate a move instruction to be injected.
        """
        return PayloadMove(num=num,
                           code=f'{move_result.replace("-result", "")} {original_dst}, {new_dst}')

    @staticmethod
    def generate_move_result(num, instruction, reg):
        """
        Generate a move-result instruction to be injected.
        """
        return PayloadMoveResult(num=num, code=f'{instruction} {reg}')

    @staticmethod
    def generate_move_exception(num, instruction, reg):
        """
        Generate a move-exception instruction to be injected.
        """
        return PayloadMoveException(num=num, code=f'{instruction} {reg}')

    @staticmethod
    def generate_goto(num, instruction, label):
        """
        Generate a goto instruction to be injected.
        """
        return PayloadGoto(num=num, code=f'{instruction} {label}')

    @staticmethod
    def generate_extra_goto(num, instruction, label):
        """
        Generate an extra goto instruction to be injected.
        """
        return PayloadGotoExtra(num=num, code=f'{instruction} {label}')

    @staticmethod
    def generate_goto_label(num, label):
        """
        Generate a goto label to be injected.
        """
        return PayloadGotoLabel(num=num, code=label)

    @staticmethod
    def generate_extra_goto_label(num, label):
        """
        Generate a goto label to be injected.
        """
        return PayloadGotoLabelExtra(num=num, code=label)

    @staticmethod
    def generate_cond_label(num, label):
        """
        Generate a cond label to be injected.
        """
        return PayloadCondLabel(num=num, code=label)

    @staticmethod
    def generate_code_logging_a_register_value(counter, cid, instruction_num,
                                               position, reg, data_type,
                                               instruction_kind,
                                               castable_to, use_shared_converter, const_string=False):
        """
        Generate code that logs the given register's value.
        """
        smalien_log_class_name = Utils.get_smalien_log_class_name(counter)
        smalien_id = Utils.get_smalien_id(cid, instruction_num, reg)

        method_name = Utils.get_method_name(smalien_id, data_type)
        invoke = Utils.get_invoke(smalien_log_class_name, method_name, reg, data_type)
        definition, converter_key = Utils.get_definition(method_name, smalien_id, data_type, castable_to, True, use_shared_converter, const_string)
        smali_name = Utils.get_smali_name(smalien_log_class_name)

        return PayloadLogging(num=position, instruction_kind=instruction_kind,
                              invoke=invoke, definition=definition,
                              class_name=smalien_log_class_name, smali_name=smali_name), converter_key
    @staticmethod
    def generate_code_logging_a_base_object_value(counter, cid, instruction_num,
                                                  position, reg, data_type,
                                                  instruction_kind,
                                                  castable_to, use_shared_converter):
        """
        Generate code that logs the given base object's value.
        """
        smalien_log_class_name = Utils.get_smalien_log_class_name(counter)
        smalien_id = Utils.get_smalien_id(cid, instruction_num, reg)

        method_name = Utils.get_method_name(smalien_id, data_type)
        invoke = Utils.get_invoke(smalien_log_class_name, method_name, reg, data_type)
        # definition = Utils.get_definition_for_base_object(method_name, smalien_id, data_type, castable_to, False)
        definition, converter_key = Utils.get_definition(method_name, smalien_id, data_type, castable_to, False, use_shared_converter, False)
        smali_name = Utils.get_smali_name(smalien_log_class_name)

        return PayloadLogging(num=position, instruction_kind=instruction_kind,
                              invoke=invoke, definition=definition,
                              class_name=smalien_log_class_name, smali_name=smali_name), converter_key

    @staticmethod
    def generate_code_logging_no_value(counter, cid, instruction_num,
                                       position, instruction_kind):
        """
        Generate code that logs no value.
        """
        smalien_log_class_name = Utils.get_smalien_log_class_name(counter)
        smalien_id = Utils.get_smalien_id_without_value_logging(cid, instruction_num)

        method_name = Utils.get_method_name_without_value_logging(smalien_id)
        invoke = Utils.get_invoke_without_value_logging(smalien_log_class_name,
                                                        method_name)
        definition = Utils.get_definition_without_value_logging(method_name,
                                                                smalien_id)
        smali_name = Utils.get_smali_name(smalien_log_class_name)

        return PayloadLogging(num=position, instruction_kind=instruction_kind,
                              invoke=invoke, definition=definition,
                              class_name=smalien_log_class_name, smali_name=smali_name)


    #
    # Utility methods used for both payloads with and without value logging.
    #
    @staticmethod
    def get_smalien_log_class_name(counter):
        """
        Return a smalien class name.
        """
        return SMALIEN_LOG_CLASS.format(str(counter))

    @staticmethod
    def get_smali_name(smalien_log_class_name):
        """
        Translate smalien log class name to its smali file name.
        """
        return smalien_log_class_name[1:-1]+'.smali'


    #
    # Utility methods used for payloads with value logging.
    #
    @staticmethod
    def get_smalien_id(cid, num, reg):
        """
        Return a smalien id used to identify logged data.
        """
        return f'{str(cid)}_{str(num)}_{reg}'

    @staticmethod
    def get_method_name(smalien_id, data_type):
        """
        Return name of a smalien method logging data.
        """
        return CODE_WITH_VL['method'].format(smalien_id, data_type)

    @staticmethod
    def get_invoke(smalien_log_class_name, method_name, reg, data_type):
        """
        Return code invoking the given method.
        """
        reg2 = reg
        # If the data type is 64 bits, logs two different registers
        if (data_type in numeric_types_64):
            reg2 =  f'{reg[0]}{str(int(reg[1:]) + 1)}'

        return CODE_WITH_VL['invoke'].format(reg, reg2, smalien_log_class_name,
                                             method_name)

    @staticmethod
    def get_definition(method_name, smalien_id, data_type, castable_to, can_be_null, use_shared_converter, const_string):
        """
        Return code defining the given method.
        """
        # If the data type is not primitive, it should be array, java.lang.string, or java.lang.object
        if (data_type not in primitive_data_types):
            # if (castable_to in ['[[Ljava/lang/String;'] or castable_to in ['Ljava/lang/String;', 'Ljava/lang/reflect/Method;', '[Ljava/lang/reflect/Method', 'Ljava/lang/Class;', '[Ljava/lang/Class;']):
            if (castable_to in string_types or
                castable_to in string_types_array
               ):
                # Currently only target two dimensional array.
                data_type = 'CastableTo'+castable_to
            elif (castable_to is not None and castable_to.startswith('[')):
                if (castable_to in ['[Z', '[B', '[C', '[S', '[I', '[F', '[J', '[D']):
                    data_type = castable_to
                else:
                    data_type = 'CastableTo[Ljava/lang/Object;'
            elif (data_type.startswith('[')):
                # For primitive-data-type arrays, use different definitions of logger method
                if (data_type in ['[Z', '[B', '[C', '[S', '[I', '[F', '[J', '[D']):
                    pass
                elif (data_type in string_types_array):
                    pass
                else:
                    data_type = '[Ljava/lang/Object;'
            elif (data_type not in string_types or const_string):
                # For non-array non-string objects
                # Or const-string, which string logging is not necessary
                if (data_type == 'Ljava/lang/Object;'):
                    # For java.lang.Object, perform is-array checking.
                    data_type = 'Ljava/lang/Object;-PURE'
                elif (can_be_null):
                    data_type = 'Ljava/lang/Object;-WITH_NULL_CHECK'
                else:
                    data_type = 'Ljava/lang/Object;-WITHOUT_NULL_CHECK'

        # Number of local registers in a logging method
        # locals_num = 1
        # # If the data type is 64 bits, use two local registers
        # if (data_type in numeric_types_64):
        #     locals_num = 2
        # elif (data_type == 'Ljava/lang/String;' or castable_to == 'Ljava/lang/String;'):
        #     locals_num = 2
        # elif (data_type in ['CastableTo[Ljava/lang/Object;', '[Ljava/lang/Object;']):
        #     locals_num = 5

        # Decide to use shared or individual converter
        converter_key = data_type.replace('CastableTo', '')
        if (use_shared_converter and
            converter_key not in DATA_TYPES_IMPLEMENTED_INDIVIDUAL_CONVERTER):
             # New shared instrumentation code, which is lighter
            to_string_code = CODE_WITH_VL['definition']['to_string'].get(data_type)

            assert to_string_code is not None, f'string_valueof is used for {data_type = }'

            return to_string_code.format(method_name, smalien_id), converter_key

        else:
            # Old individual instrumentation code
            to_string_code = CODE_WITH_VL_FOR_INDIVIDUAL_CONVERTER['definition']['to_string'].get(data_type)

            assert to_string_code is not None, f'string_valueof is used for {data_type = }'

            return CODE_WITH_VL_FOR_INDIVIDUAL_CONVERTER['definition']['base'].format(method_name,#  locals_num,
                                                                                      to_string_code, smalien_id), converter_key

#     @staticmethod
#     def get_definition_for_base_object(method_name, smalien_id, data_type):
#         """
#         Return code defining the given method.
#         """
# 
#         # Number of local registers in a logging method
#         # OLD_REPRESENTATION
#         # locals_num = 2
#         # OLD_REPRESENTATION
#         # TEST_NEW_REPRESENTATION
#         locals_num = 1
#         # TEST_NEW_REPRESENTATION
# 
#         if (data_type.startswith('[')):
#             # data type is [Ljava/lang/Object;
#             to_string_code = CODE_WITH_VL['definition']['to_string']['[Ljava/lang/Object;'].format()
#         else:
#             # data_type is Ljava/lang/Object;
#             to_string_code = CODE_WITH_VL['definition']['to_representation']
# 
#         return CODE_WITH_VL['definition']['base'].format(method_name, locals_num,
#                                                          to_string_code,
#                                                          smalien_id)


    #
    # Utility methods used for payloads without value logging.
    #
    @staticmethod
    def get_smalien_id_without_value_logging(cid, num):
        """
        Return a smalien id used to identify logged data.
        """
        return f'{str(cid)}_{str(num)}'

    @staticmethod
    def get_method_name_without_value_logging(smalien_id):
        """
        Return a smalien method name logging data.
        """
        return CODE_WITHOUT_VL['method'].format(smalien_id)

    @staticmethod
    def get_invoke_without_value_logging(smalien_log_class_name, method_name):
        """
        Return code invoking the given method.
        """
        return CODE_WITHOUT_VL['invoke'].format(smalien_log_class_name, method_name)

    @staticmethod
    def get_definition_without_value_logging(method_name, smalien_id):
        """
        Return code defining the given method.
        """
        return CODE_WITHOUT_VL['definition'].format(method_name, smalien_id)

    @staticmethod
    def generate_dummy_returned_value(num, reg, value):
        """
        Generate a constant definition for a dummy returned value.
        """
        return PayloadDummyReturnedValue(num=num,
                                         code='    const-string {}, "{}"\n'.format(reg, value))
