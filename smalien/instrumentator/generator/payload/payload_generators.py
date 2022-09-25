import logging

from .payload_generator_utils import Utils
from .structures import PayloadDummyReturnedValue
from smalien.data_types import primitive_data_types, numeric_types_64, CHECK_CAST_TARGET
from smalien.definitions import LONG_DISTANCE_JUMP_THRESHOLD

logger = logging.getLogger(name=__name__)


class PayloadMethodHeadGenerator():
    """
    Generate payloads for method heads.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        cid = kwargs['cid']
        value_logging = kwargs['value_logging']
        is_constructor = kwargs['is_constructor']
        counter = kwargs['counter']
        use_shared_converter = kwargs['use_shared_converter']

        payloads = []
        converter_keys = set()

        position = inst.num + 1

        if (value_logging):
            # Generate payloads for logging values of parameters of both primitive and reference data types.
            # The payloads log primitive values and instance identifiers passed from callers.
            i = 0
            while i < len(inst.parameters):
                # If constructor, skip any base object logging
                # This is because a constructor's base object, p0, is uninitialized at the head and cannot be logged
                if (is_constructor and i == 0):
                    i += 1
                    continue

                param = inst.parameters[i]
                if (inst.attribute != 'static' and i == 0):
                    # Generate for base object
                    payload, converter_key = Utils.generate_code_logging_a_base_object_value(counter, cid, inst.num,
                                                                                             position, param,
                                                                                             inst.parameter_data_types[param],
                                                                                             inst.kind, None, use_shared_converter)
                else:
                    # Generate for non-base-object parameters
                    payload, converter_key = Utils.generate_code_logging_a_register_value(counter, cid, inst.num,
                                                                                          position, param,
                                                                                          inst.parameter_data_types[param],
                                                                                          inst.kind, None, use_shared_converter)
                payloads.append(payload)
                converter_keys.add(converter_key)

                # Increment i
                if (inst.parameter_data_types[param] in numeric_types_64):
                    i += 2
                else:
                    i += 1

        # If no payload is generated, generate a payload without value logging
        if (payloads == []):
            payloads.append(Utils.generate_code_logging_no_value(counter, cid, inst.num,
                                                                 position, inst.kind))

        return payloads, converter_keys

class PayloadInvokeGenerator():
    """
    Generate payloads for invoke instructions.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        cid = kwargs['cid']
        value_logging = kwargs['value_logging']
        start_at = kwargs['start_at']
        local_reg_num = kwargs['local_reg_num']
        mparam_num = kwargs['mparam_num']
        counter = kwargs['counter']
        register_reassignment = kwargs['register_reassignment']
        use_shared_converter = kwargs['use_shared_converter']
        taint_sources = kwargs['taint_sources']
        dummy_source_values = kwargs['dummy_source_values']
        instructions = kwargs['instructions']

        payloads = []
        converter_keys = set()

        # Log at the corresponding move-result, which is after the invoke finished
        move_result = inst.move_result
        # Decide logging position based on whether move-result is dummy
        if (move_result.destination is None):
            # Move result is dummy
            position = PayloadInvokeGenerator.get_position(inst.num, instructions)
        else:
            # Move result is real
            # position = move_result.num + 1 # This causes verification errors
            position = PayloadInvokeGenerator.get_position(move_result.num, instructions)

        # Log values for invoke instructions not implemented in the app
        if (value_logging and not inst.in_app):
            # Log the base object of constructors not implemented in the app
            # Note that the register can match to the corresponding move-result destination,
            # and if so, the register should not be logged as an argument.
            # This is merged to below for-loop logging reference-data-type arguments.
            # if (inst.invoke_constructor and inst.arguments[0] != move_result.destination):
            #     # Generate for base object
            #     payloads.append(Utils.generate_code_logging_a_base_object_value(counter, cid, move_result.num,
            #                                                                     position, inst.arguments[0],
            #                                                                     inst.class_name,
            #                                                                     move_result.kind))

            # Log argument registers that are reference-data-type
            logged_registers = []
            for i, arg in enumerate(inst.arguments):
                # A method can have the same register as different arguments.
                # To log such registers only once, skip the generator if the register is already processed.
                if (arg in logged_registers):
                    continue

                if (arg != move_result.destination and
                    arg != move_result.destination_pair and
                    inst.argument_data_types[arg] not in primitive_data_types and
                    inst.argument_data_types[arg] != 'Ljava/lang/Class;'
                ):
                    if (not inst.invoke_static and i == 0):
                        # Generate for base object
                        payload, converter_key = Utils.generate_code_logging_a_base_object_value(counter, cid, move_result.num,
                                                                                                 position, arg,
                                                                                                 inst.class_name,
                                                                                                 move_result.kind, None, use_shared_converter)
                    else:
                        # Generate for non base object
                        payload, converter_key = Utils.generate_code_logging_a_register_value(counter, cid, move_result.num,
                                                                                              position, arg,
                                                                                              inst.argument_data_types[arg],
                                                                                              move_result.kind, None, use_shared_converter)
                    payloads.append(payload)
                    converter_keys.add(converter_key)

                    logged_registers.append(arg)

            # Log move-result destination register if the corresponding move-result exists
            if (move_result.destination is not None):

                if (dummy_source_values is not None):
                    # Check whether the invoked method is a taint source
                    # Currently, reflection calls are not supported
                    if (inst.class_name in taint_sources.keys() and
                        inst.method_name in taint_sources[inst.class_name].keys()
                       ):
                        # Generate a dummy-source-returning instruction
                        source_key = taint_sources[inst.class_name][inst.method_name]
                        if (source_key in dummy_source_values.keys()):
                            payloads.append(Utils.generate_dummy_returned_value(position,
                                                                                move_result.destination,
                                                                                dummy_source_values[source_key]))

                # This is currently not used because Intent changes its hashCode and is not trackable by this
                # TODO: Define the list of data types for logging its representation
                # if (move_result.destination_data_type in ['Landroid/content/Intent;']):
                #     # Generate the destination class's representation
                #     payloads.append(Utils.generate_code_logging_a_base_object_value(counter, cid, move_result.num,
                #                                                                     position, move_result.destination,
                #                                                                     move_result.destination_data_type,
                #                                                                     move_result.kind))
                # else:
                # Generate the destination value
                # Check if the logged value has its toString() method implemented
                # TODO: Remove this branch because it is not necessary anymore.
                # class_data = classes.get(move_result.castable_to)
                # if (class_data is not None and class_data.tostring_implemented):
                #     # Log its representation to avoid invoking the toString()
                #     payloads.append(Utils.generate_code_logging_a_base_object_value(counter, cid, move_result.num,
                #                                                                     position, move_result.destination,
                #                                                                     move_result.destination_data_type,
                #                                                                     move_result.kind, move_result.castable_to))
                # else:
                if (True):
                    # Log the register value
                    payload, converter_key = Utils.generate_code_logging_a_register_value(counter, cid, move_result.num,
                                                                                          position, move_result.destination,
                                                                                          move_result.destination_data_type,
                                                                                          move_result.kind, move_result.castable_to,
                                                                                          use_shared_converter)
                    payloads.append(payload)
                    converter_keys.add(converter_key)

        if (register_reassignment and
            move_result.destination is not None and
            local_reg_num + mparam_num < 15):
            # Skip if additional registers are not available
            # If sum of local reg and param numbers is 14 or less, two more registers can be added

            
            # If no payload is generated, generate a payload without value logging before the register reassignment
            if (payloads == []):
                payloads.append(Utils.generate_code_logging_no_value(counter, cid, move_result.num,
                                                                     position, move_result.kind))

            PayloadInvokeGenerator.reassign_move_result_dst_register(payloads, inst,
                                                                     move_result, start_at,
                                                                     local_reg_num)

        elif (payloads == []):
            # If no payload is generated, and register reassignment is not applied,
            # decide logging point based on move-result-following instructions
            no_logging_position = PayloadInvokeGenerator.detect_move_result_conversion_pattern(position, instructions)
            payloads.append(Utils.generate_code_logging_no_value(counter, cid, move_result.num,
                                                                 no_logging_position, move_result.kind))

        return payloads, converter_keys

    @staticmethod
    def reassign_move_result_dst_register(payloads, inst, move_result, start_at, local_reg_num):
        logger.debug('reassigning move result destination register')

        # if (local_reg_num + mparam_num > 14):
        #     return

        # Prepare new destination registers
        new_dst = f'v{local_reg_num}'
        if (move_result.destination_data_type in numeric_types_64):
            new_dst2 = f'{new_dst[0]}{str(int(new_dst[1:]) + 1)}'
        else:
            new_dst2 = new_dst
        new_arg = ' {'+new_dst+' .. '+new_dst2+'}, '

        # Prepare old destination registers
        if (move_result.destination_pair is not None):
            original_dst2 = move_result.destination_pair
        else:
            original_dst2 = move_result.destination
        original_arg = ' {'+move_result.destination+' .. '+original_dst2+'}, '

        # Replace the original dst with a new register in arguments of logging method.
        # The registers will not be found if the method is implemented in app, and the values are not logged
        if (payloads[-1].invoke.find(original_arg) > -1):
            payloads[-1].invoke = payloads[-1].invoke.replace(original_arg, new_arg)

        # Replace the dummy returned value register
        if (len(payloads) > 1 and
            isinstance(payloads[-2], PayloadDummyReturnedValue) and
            payloads[-2].code.find(move_result.destination) > -1
           ):
            # Currently, support only one register (e.g., String) and not a pair registers (e.g., double)
            payloads[-2].code = payloads[-2].code.replace(move_result.destination, new_dst)

        # Generate move instruction that moves value from new to original registers
        payloads.append(Utils.generate_move(payloads[-1].num, move_result.instruction,
                                            move_result.destination, new_dst))

        # Generate .locals line that replaces the original instruction
        # .locals is at the next line of method head (start_at + 1)
        # Add two to local register number because two additional registers are required for 64bit values
        payloads.append(Utils.generate_locals(start_at+1, local_reg_num, 2))

        # Generate move-result instruction that replaces the original instruction
        payloads.append(Utils.generate_move_result(move_result.num, move_result.instruction, new_dst))

    @staticmethod
    def detect_move_result_conversion_pattern(num, instructions):
        """
        Detect the move-result conversion pattern.
        Example from
          move-result v4
          int-to-long v4, v4
        """
        while True:
            next_inst = instructions.get(num)
            if (next_inst is not None):
                if (next_inst.kind == 'unop' and next_inst.is_converter):
                    return num + 1
                else:
                    break
            num += 1
        return num

    @staticmethod
    def get_position(num, instructions):
        """
        Get instrument position for invokes.
        """

        next_inst = PayloadMonitorEnterGenerator.get_next_inst(num, instructions)
        if (next_inst.kind == 'try_end_label'):
            num = next_inst.num + 1
            assert instructions[num].kind == 'catch_data'
            # Skip the following catch data
            while True:
                next_inst = instructions.get(num+1)
                if (next_inst is None or next_inst.kind != 'catch_data'):
                    break
                num += 1

            return num + 1

        # This causes verification errors
        # elif (next_inst.kind == 'try_start_label'):
        #     return next_inst.num + 1

        return num + 1

class PayloadMoveResultGenerator():
    """
    Generate payloads for move-result instructions.
    If an invocation has no corresponding move-result, the parser generates a dummy move-result.
    The generator works for both real and dummy move-result instructions.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        counter = kwargs['counter']

        payloads = []

        # Pass filled_new_array instructions
        if (inst.source.kind == 'filled_new_array'):
            # TODO: Branch the process based on inst source kind
            return payloads

        # This is not used, and PayloadInvokeGenerator generates for move-result instructions

        return payloads, set()

class PayloadCatchLabelGenerator():
    """
    Generate payloads for catch labels.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        cid = kwargs['cid']
        value_logging = kwargs['value_logging']
        counter = kwargs['counter']
        use_shared_converter = kwargs['use_shared_converter']
        # For reassignment
        start_at = kwargs['start_at']
        local_reg_num = kwargs['local_reg_num']
        mparam_num = kwargs['mparam_num']
        register_reassignment = kwargs['register_reassignment']
        method_data = kwargs['method_data']
        instructions = kwargs['instructions']

        payloads = []
        converter_keys = set()

        # Check whether a move-exception instruction is next to the catch label,
        # inject after the move-exception to avoid runtime exception
        if (inst.move_exception is not None):
            position = inst.num + 2
        else:
            position = inst.num + 1

        if (value_logging and inst.move_exception is not None):
            payload, converter_key = Utils.generate_code_logging_a_register_value(counter, cid, inst.num,
                                                                                  position, inst.move_exception.destination,
                                                                                  inst.move_exception.destination_data_type,
                                                                                  inst.kind, None, use_shared_converter)
            payloads.append(payload)
            converter_keys.add(converter_key)

            if (inst.move_exception.in_try_block):
                # Add an extra control flow to set the logging point at the method end
                PayloadCatchLabelGenerator.modify_control_flow(payloads, method_data)

            # if (register_reassignment and inst.move_exception.in_try_block):
            #     # Use this only when the move-exception is in a try block
            #     PayloadCatchLabelGenerator.reassign_move_exception_dst_register(payloads, inst,
            #                                                                     inst.move_exception, start_at,
            #                                                                     local_reg_num, mparam_num,
            #                                                                     method_data, instructions)
        else:
            payloads.append(Utils.generate_code_logging_no_value(counter, cid, inst.num,
                                                                 position, inst.kind))

        return payloads, converter_keys

#     @staticmethod
#     def reassign_move_exception_dst_register(payloads, inst, move_exception, start_at, local_reg_num, mparam_num, method_data, instructions):
#         logger.debug('reassigning move exception destination register')
# 
#         # Skip if additional registers are not available
#         # If sum of local reg and param numbers is 15 or less, one more register can be added
#         if (local_reg_num + mparam_num > 15):
#             return
# 
#         # Prepare new destination registers
#         new_dst = f'v{local_reg_num}'
#         new_arg = ' {'+new_dst+' .. '+new_dst+'}, '
# 
#         # Prepare old destination registers
#         original_arg = ' {'+move_exception.destination+' .. '+move_exception.destination+'}, '
# 
#         # Replace the original dst with a new register in arguments of logging method.
#         payloads[-1].invoke = payloads[-1].invoke.replace(original_arg, new_arg)
# 
#         # Generate move instruction that moves value from new to original registers
#         payloads.append(Utils.generate_move(payloads[-1].num, 'move-object',
#                                             move_exception.destination, new_dst))
# 
#         # Add an extra control flow to set the logging point at the method end
#         PayloadCatchLabelGenerator.modify_control_flow(payloads, method_data)
# 
#         # # Detect the move-goto pattern
#         # goto_found, goto_inst, num = PayloadCatchLabelGenerator.detect_move_goto_pattern(move_exception.num+1, instructions)
#         # if (goto_found and not goto_inst.destination.in_try_block):
#         #     # Apply the modification only when the goto destination label is not in a try block to avoid reactive errors.
#         #     PayloadCatchLabelGenerator.modify_goto_flow(goto_inst, payloads, method_data)
#         # else:
#         #     # Move instructions may be found after the move-exception
#         #     # Change the logging point to point where after the move instructions to avoid verification errors.
#         #     payloads[-2].num = num
# 
#         # Generate .locals line that replaces the original instruction
#         # .locals is at the next line of method head (start_at + 1)
#         # Add one to local register number because one additional register is required
#         payloads.append(Utils.generate_locals(start_at+1, local_reg_num, 1))
# 
#         # Generate move-exception instruction that replaces the original instruction
#         payloads.append(Utils.generate_move_exception(move_exception.num, move_exception.instruction, new_dst))

    @staticmethod
    def modify_control_flow(payloads, method_data):
        """
        Modify goto flow.
        """
        # Get new goto labels
        # The trampoline skipper is disabled because a verification error occurs
        #   Verifier rejected: "invalid branch target"
        # For skipping the trampoline
        # method_data.goto_label_num += 1
        # new_goto_label_1 = f':goto_{hex(method_data.goto_label_num)[2:]}'

        # For going to the trampoline
        method_data.goto_label_num += 1
        new_goto_label_2 = f':goto_{hex(method_data.goto_label_num)[2:]}'
        # For going back from the trampoline
        method_data.goto_label_num += 1
        new_goto_label_3 = f':goto_{hex(method_data.goto_label_num)[2:]}'

        logger = payloads.pop(-1)

        # Generate a goto instruction that jumps to the trampoline
        payloads.insert(0, Utils.generate_extra_goto(logger.num, 'goto/32', new_goto_label_2))
        # Generate a goto_label used to get back from the trampoline
        # Insert it after the above goto and before the logging point
        payloads.insert(1, Utils.generate_extra_goto_label(logger.num, new_goto_label_3))

        # Create a trampoline right before the method end
        # Generate a goto instruction that skips the trampoline
        # payloads.append(Utils.generate_extra_goto(method_data.end_at, 'goto', new_goto_label_1))

        # Create a new goto label
        payloads.append(Utils.generate_extra_goto_label(method_data.end_at, new_goto_label_2))
        # Add the logger
        logger.num = method_data.end_at
        payloads.append(logger)
        # Create a new goto/32 instruction that jumps back from the trampoline
        payloads.append(Utils.generate_extra_goto(method_data.end_at, 'goto/32', new_goto_label_3))

        # Create a new goto label for skipping the trampoline
        # payloads.append(Utils.generate_extra_goto_label(method_data.end_at, new_goto_label_1))

#     @staticmethod
#     def detect_move_goto_pattern(num, instructions):
#         """
#         Detect the move-goto pattern.
#           move-exception
#           move
#           move
#           goto :goto_label
#         """
#         while True:
#             next_inst = instructions.get(num)
#             if (next_inst is not None):
#                 if (next_inst.kind == 'goto'):
#                     return True, next_inst, num
#                 elif (next_inst.kind == 'move'):
#                     pass
#                 else:
#                     break
#             num += 1
#         return False, None, num
# 
#     @staticmethod
#     def modify_goto_flow(goto_inst, payloads, method_data):
#         """
#         Modify goto flow.
#         """
#         # Get new goto label
#         method_data.goto_label_num += 1
#         new_goto_label = f':goto_{hex(method_data.goto_label_num)[2:]}'
# 
#         # Update the logging point of the move-exception logger
#         payloads[-2].num = goto_inst.destination.num
# 
#         # Generate a goto instruction that skips the newly-created goto_label
#         # Insert it before the logging point
#         payloads.insert(0, Utils.generate_extra_goto(goto_inst.destination.num, goto_inst.instruction, goto_inst.destination.label))
# 
#         # Generate a goto_label that is the destination of new goto instruction
#         # Insert it after the above goto and before the logging point
#         payloads.insert(1, Utils.generate_extra_goto_label(goto_inst.destination.num, new_goto_label))
# 
#         # Generate a goto instruction that skips the other instructions before the original goto_label.
#         payloads.append(Utils.generate_extra_goto(goto_inst.destination.num, goto_inst.instruction, goto_inst.destination.label))
# 
#         # Generate a goto instruction that replaces the original instruction
#         payloads.append(Utils.generate_goto(goto_inst.num, goto_inst.instruction, new_goto_label))

class PayloadInstanceOfGenerator():
    """
    Generate payloads for instance-of instructions.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        cid = kwargs['cid']
        value_logging = kwargs['value_logging']
        counter = kwargs['counter']
        use_shared_converter = kwargs['use_shared_converter']

        payloads = []
        converter_keys = set()

        position = inst.num + 1

        if (value_logging):
            payload, converter_key = Utils.generate_code_logging_a_register_value(counter, cid, inst.num,
                                                                                  position, inst.destination,
                                                                                  inst.destination_data_type,
                                                                                  inst.kind, None, use_shared_converter)
            payloads.append(payload)
            converter_keys.add(converter_key)

        return payloads, converter_keys

class PayloadGetterGenerator():
    """
    Generate payloads for iget and sget instructions.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        cid = kwargs['cid']
        value_logging = kwargs['value_logging']
        instructions = kwargs['instructions']
        counter = kwargs['counter']
        use_shared_converter = kwargs['use_shared_converter']

        payloads = []
        converter_keys = set()

        # position = inst.num + 1
        position = PayloadMonitorEnterGenerator.get_position(inst.num, instructions)

        # For all sget, the value must be logged because a value is invisibly changed in static field.
        # For all iget, the value must be logged because class instances can be transferred.
        if (value_logging):
            payload, converter_key = Utils.generate_code_logging_a_register_value(counter, cid, inst.num,
                                                                                  position, inst.destination,
                                                                                  inst.destination_data_type,
                                                                                  inst.kind, inst.castable_to,
                                                                                  use_shared_converter)
            payloads.append(payload)
            converter_keys.add(converter_key)

        # # Log values from the field, if the field is not implemented in the app
        # if (value_logging and
        #     (not inst.in_app or
        #      inst.kind == 'iget' or  # Record for all iget instructions because class instances can be transferred.
        #      (inst.kind == 'sget' and not inst.clinit_implemented)) or  # For sget accessing a field of no-clinit class,
        #                                                                 # its values must be recorded because the timing of field initialization is not observable.
        #      inst.destination_data_type.startswith('[')  # Record arrays because they can be modified by, e.g., a native method.
        # ):
        #     payloads.append(Utils.generate_code_logging_a_register_value(counter, cid, inst.num,
        #                                                                  position, inst.destination,
        #                                                                  inst.destination_data_type,
        #                                                                  inst.kind, None))
        # elif (inst.kind == 'sget'):
        #     # As same as for sput, the sget execution timing is necessary to detect clinit invocation.
        #     payloads.append(Utils.generate_code_logging_no_value(counter, cid, inst.num,
        #                                                          position, inst.kind))

        return payloads, converter_keys

class PayloadSetterGenerator():
    """
    Generate payloads for sput instructions.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        cid = kwargs['cid']
        instructions = kwargs['instructions']
        counter = kwargs['counter']

        payloads = []

        # position = inst.num + 1
        position = PayloadMonitorEnterGenerator.get_position(inst.num, instructions)

        payloads.append(Utils.generate_code_logging_no_value(counter, cid, inst.num,
                                                             position, inst.kind))

        return payloads, set()

class PayloadCheckCastGenerator():
    """
    Generate payloads for check-cast instructions.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        cid = kwargs['cid']
        value_logging = kwargs['value_logging']
        counter = kwargs['counter']
        use_shared_converter = kwargs['use_shared_converter']

        payloads = []
        converter_keys = set()

        position = inst.num + 1

        if (value_logging and not inst.move_result_matched and inst.class_name in CHECK_CAST_TARGET):
            payload, converter_key = Utils.generate_code_logging_a_register_value(counter, cid, inst.num,
                                                                                  position, inst.register,
                                                                                  inst.class_name,
                                                                                  inst.kind, None,
                                                                                  use_shared_converter)
            payloads.append(payload)
            converter_keys.add(converter_key)
        else:
            payloads.append(Utils.generate_code_logging_no_value(counter, cid, inst.num,
                                                                 position, inst.kind))

        return payloads, converter_keys

class PayloadConstStringGenerator():
    """
    Generate payloads for const-string instructions.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        cid = kwargs['cid']
        value_logging = kwargs['value_logging']
        counter = kwargs['counter']
        use_shared_converter = kwargs['use_shared_converter']
        instructions = kwargs['instructions']

        payloads = []
        converter_keys = set()

        # position = inst.num + 1
        position = PayloadMonitorEnterGenerator.get_position(inst.num, instructions)

        if (value_logging):
            payload, converter_key = Utils.generate_code_logging_a_register_value(counter, cid, inst.num,
                                                                                  position, inst.destination,
                                                                                  inst.data_type,
                                                                                  inst.kind, None,
                                                                                  use_shared_converter,
                                                                                  const_string=True)
            payloads.append(payload)
            converter_keys.add(converter_key)

        return payloads, converter_keys

class PayloadConstClassGenerator():
    """
    Generate payloads for const-class instructions.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        cid = kwargs['cid']
        value_logging = kwargs['value_logging']
        counter = kwargs['counter']
        use_shared_converter = kwargs['use_shared_converter']

        payloads = []
        converter_keys = set()

        position = inst.num + 1

        if (value_logging):
            payload, converter_key = Utils.generate_code_logging_a_register_value(counter, cid, inst.num,
                                                                                  position, inst.destination,
                                                                                  inst.data_type,
                                                                                  inst.kind, None,
                                                                                  use_shared_converter)
            payloads.append(payload)
            converter_keys.add(converter_key)

        return payloads, converter_keys

class PayloadMonitorEnterGenerator():
    """
    Generate payloads for monitor-enter instructions.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        cid = kwargs['cid']
        instructions = kwargs['instructions']
        counter = kwargs['counter']

        payloads = []

        position = PayloadMonitorEnterGenerator.get_position(inst.num, instructions)

        payloads.append(Utils.generate_code_logging_no_value(counter, cid, inst.num,
                                                             position, inst.kind))

        return payloads, set()

    @staticmethod
    def get_position(num, instructions):
        """
        Get instrument position for monitor-enter.
        """

        next_inst = PayloadMonitorEnterGenerator.get_next_inst(num, instructions)
        if (next_inst.kind == 'try_end_label'):
            num = next_inst.num + 1
            assert instructions[num].kind == 'catch_data'
            # Skip the following catch data
            while True:
                next_inst = instructions.get(num+1)
                if (next_inst is None or next_inst.kind != 'catch_data'):
                    break
                num += 1

            return num + 1

        elif (next_inst.kind == 'try_start_label'):
            return next_inst.num + 1

        return num + 1

    @staticmethod
    def get_next_inst(num, instructions):
        """
        Return an instruction right after the monitor-enter.
        """
        while True:
            num += 1
            if (num in instructions.keys()):
                return instructions[num]

# Note that logging value of new-instance throws a verifier rejected error "register has type Uninitialized Reference"
class PayloadNewInstanceGenerator():
    """
    Generate payloads for new-instance instructions.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        cid = kwargs['cid']
        counter = kwargs['counter']

        payloads = []

        position = inst.num + 1

        payloads.append(Utils.generate_code_logging_no_value(counter, cid, inst.num,
                                                             position, inst.kind))

        return payloads, set()

class PayloadArrayLengthGenerator():
    """
    Generate payloads for array-length instructions.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        cid = kwargs['cid']
        value_logging = kwargs['value_logging']
        counter = kwargs['counter']
        use_shared_converter = kwargs['use_shared_converter']

        payloads = []
        converter_keys = set()

        position = inst.num + 1

        if (value_logging):
            payload, converter_key = Utils.generate_code_logging_a_register_value(counter, cid, inst.num,
                                                                                  position, inst.destination,
                                                                                  inst.destination_data_type,
                                                                                  inst.kind, None,
                                                                                  use_shared_converter)
            payloads.append(payload)
            converter_keys.add(converter_key)

        return payloads, converter_keys

class PayloadIfGenerator():
    """
    Generate payloads for if instructions.
    No logging, but modify long-distance jumpers.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        # For modifying long-distance if-cond flow
        inst = kwargs['inst']
        method_data = kwargs['method_data']

        payloads = []
        converter_keys = set()

        if (abs(inst.num - inst.destination.num) > LONG_DISTANCE_JUMP_THRESHOLD and
            not inst.destination.extra_trampoline
           ):
            # The jump skips more than 20k lines
            logger.error(f'if-cond: {inst.num = } {inst.destination.num = } {inst.num - inst.destination.num = }')
            PayloadIfGenerator.modify_if_cond_flow(inst, payloads, method_data)
            inst.destination.extra_trampoline = True

        return payloads, converter_keys

    @staticmethod
    def modify_if_cond_flow(if_inst, payloads, method_data):
        """
        Modify if-cond flow by creating a trampoline right before the if instruction.
        """
        # Get new goto labels
        # For skipping the trampoline
        method_data.goto_label_num += 1
        new_goto_label_1 = f':goto_{hex(method_data.goto_label_num)[2:]}'
        # For the trampoline
        method_data.goto_label_num += 1
        new_goto_label_2 = f':goto_{hex(method_data.goto_label_num)[2:]}'

        # Create a trampoline right before the if instruction
        # Generate a goto instruction that skips the trampoline
        payloads.append(Utils.generate_extra_goto(if_inst.num, 'goto', new_goto_label_1))
        # Create a new cond label
        payloads.append(Utils.generate_cond_label(if_inst.num, if_inst.destination.label))
        # Create a new goto/32 instruction that jumps to point of the original cond 
        payloads.append(Utils.generate_extra_goto(if_inst.num, 'goto/32', new_goto_label_2))
        # Create a new goto label for skipping the trampoline
        payloads.append(Utils.generate_extra_goto_label(if_inst.num, new_goto_label_1))

        # Replace the original cond with the new goto label
        payloads.append(Utils.generate_goto_label(if_inst.destination.num, new_goto_label_2))

class PayloadGotoGenerator():
    """
    Generate payloads for goto instructions.
    No logging, but modify long-distance jumpers.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        # For modifying long-distance goto flow
        inst = kwargs['inst']
        method_data = kwargs['method_data']

        payloads = []
        converter_keys = set()

        if (abs(inst.num - inst.destination.num) > LONG_DISTANCE_JUMP_THRESHOLD):
            # The jump skips more than 20k lines
            logger.error(f'goto: {inst.num = } {inst.destination.num = } {inst.num - inst.destination.num = }')

            # Generate a goto instruction that replaces the original goto
            payloads.append(Utils.generate_goto(inst.num, 'goto/32', inst.destination.label))

        return payloads, converter_keys

# For debugging purpose
class PayloadConstGenerator():
    """
    Generate payloads for const instructions.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        cid = kwargs['cid']
        value_logging = kwargs['value_logging']
        counter = kwargs['counter']
        use_shared_converter = kwargs['use_shared_converter']

        payloads = []
        converter_keys = set()

        position = inst.num + 1

        if (value_logging):
            payload, converter_key = Utils.generate_code_logging_a_register_value(counter, cid, inst.num,
                                                                                  position, inst.destination,
                                                                                  inst.data_type,
                                                                                  inst.kind, None,
                                                                                  use_shared_converter)
            payloads.append(payload)
            converter_keys.add(converter_key)

        return payloads, converter_keys

# For debugging purpose
class PayloadBinopLit8Generator():
    """
    Generate payloads for binop/lit8 instructions.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        cid = kwargs['cid']
        value_logging = kwargs['value_logging']
        counter = kwargs['counter']
        use_shared_converter = kwargs['use_shared_converter']

        payloads = []
        converter_keys = set()

        position = inst.num + 1

        if (value_logging):
            payload, converter_key = Utils.generate_code_logging_a_register_value(counter, cid, inst.num,
                                                                                  position, inst.destination,
                                                                                  inst.data_type,
                                                                                  inst.kind, None,
                                                                                  use_shared_converter)
            payloads.append(payload)
            converter_keys.add(converter_key)

        return payloads, converter_keys

# This payload only produces [null] because the array is always empty.
# Therefore, this is not used.
# class PayloadNewArrayGenerator():
#     """
#     Generate payloads for new-array instructions.
#     """
#     @staticmethod
#     def run(inst, cid, value_logging, is_constructor, counter):
#         logger.debug('running')
# 
#         payloads = []
# 
#         position = inst.num + 1
# 
#         if (value_logging):
#             payloads.append(Utils.generate_code_logging_a_register_value(counter, cid, inst.num,
#                                                                          position, inst.array,
#                                                                          inst.array_data_type,
#                                                                          inst.kind))
# 
#         return payloads
