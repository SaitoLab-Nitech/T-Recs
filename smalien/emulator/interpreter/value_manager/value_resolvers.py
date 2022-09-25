import logging
import copy
import json
import numpy
import dataclasses

from .structures import PrimitiveValue, ClassInstanceValue, ArrayInstanceValue
from .value_resolver_utils import ValueResolver
from ..reflection_resolver import REFLECTIVE_FIELD_ACCESS
# from .api_call_edge_value_resolvers.api_call_edge_value_resolvers import api_call_edge_value_resolvers
from ...vm_manager.structures import StackFrameEntry
from ...vm_manager.exceptions import ExceptionOccurException, ClinitInvokedException
from smalien.data_types import primitive_data_types, numeric_types_64, numeric_types_floating_point, string_types, NULL_REPRESENTATION

logger = logging.getLogger(name=__name__)

# TODO: Create value_resolvers directory and split these resolvers into different files in the directory.


class MethodHeadValueResolver:
    """
    Resolve values at a method head.
    """
    @staticmethod
    def run(**kwargs):
        """
        Propagate values from caller registers (arguments) to callee registers (parameters).
        If an argument is reference data type, the instance is shared with the caller and callee,
        and tainting the instance at the callee causes the instance tainted at the caller.
        """
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']
        new_values = kwargs['new_values']
        invoked_method = kwargs['method']
        invoked_class = kwargs['clss']
        previous = kwargs['previous']
        instances = kwargs['instances']
        mattr = kwargs['mattr']
        classes = kwargs['classes']
        self_ptids = kwargs['self_ptids']
        vms = kwargs['vms']
        static_fields = kwargs['static_fields']
        detect_failures = kwargs['detect_failures']

        if (isinstance(previous, StackFrameEntry) and mattr != 'static'):
            '''
            Register p0 holds an instance maintained by the Android system.
            For example, MainActivity instances and Bundle savedInstanceState instances.
            Thread instances are also this kind.
            Such instances are managed by VM.instances in smalien.
            Instances are distinguished from each other by its representation (i.e., class name and hashCode()).
            Hence, a value is copied from an item of array instances[representation] to p0.
            If the value does not exist, the value is created first.
            '''
            logger.info('this instance method is called by the system')

            # Match the base object
            base = inst.parameters[0]
            # Search for the instance's value in StackFrameEntry.instances
            value, ptids = MethodHeadValueResolver.get_instance_value(inst.parameter_data_types[base],
                                                                      instances, base, new_values,
                                                                      self_ptids, vms, mattr)
            registers[base] = ValueResolver.get_value_copy(value)

#             if (self_ptids == ptids):
#                 # Same thread
#                 logger.info('same thread')
# 
#                 i = 0
#                 while i < len(inst.parameters):
#                     # TODO: Skip base object, which is already propagated
#                     param = inst.parameters[i]
#                     data_type = inst.parameter_data_types[param]
# 
#                     assert param.startswith('p'), f'param is not p*, but {param = }, {inst = }'
# 
#                     # Search for the instance's value in StackFrameEntry.instances
#                     value, ptids = MethodHeadValueResolver.get_instance_value(data_type,
#                                                                               instances,
#                                                                               param, new_values,
#                                                                               self_ptids, vms, mattr)
# 
#                     # Propagate the value
#                     registers[param] = ValueResolver.get_value_copy(value)
# 
#                     # Increment i
#                     if (data_type in numeric_types_64):
#                         i += 2
#                     else:
#                         i += 1
# 
#             else:
            if (True):
                # New thread is created
                logger.info('new thread is created')
                # Propagate based on the base object's last_invoked.
                # Using information of last-invoked is currently limited and only targets cases where the lengths of argument and parameters are same
                # because it can falsely propagate primitive-data-type arguments to non-primitive-data-type parameters.
                # TODO: Skip propagating primitive-data-type arguments because only searching the instances will be fine.
                # TODO: Check if the all arguments' and parameters' data types have one-to-one matching.
                data_types_matched = MethodHeadValueResolver.match_data_types_between_arguments_and_parameters(registers[base].last_invoked, inst)
                if (data_types_matched):
                    logger.info('the base object last invoked is saved')
                    # logger.info(registers[base].last_invoked)

                    # Copy values of non-base arguments
                    for i, arg_value in enumerate(registers[base].last_invoked_arguments):
                        # Even if the base object's last invoked is found, the caller and callee may match or may not match
                        # # Skip if the length of parameters are shorter than the length of arguments
                        # if (len(inst.parameters) <= i+1):
                        #     break

                        param = inst.parameters[i+1]

                        assert (inst.parameter_data_types[param] not in primitive_data_types) and (not isinstance(arg_value.data_type, PrimitiveValue)), (
                            f'data type {inst.parameter_data_types[param] = } or {arg_value.data_type = } is primitive-data-type, and must be checked')

                        registers[param] = ValueResolver.get_value_copy(arg_value)

                        # Save the value if it is class reference-data type
                        if (registers[param].value is not None and
                            isinstance(registers[param], ClassInstanceValue) and
                            registers[param].value != 0
                           ):
                            instances[registers[param].value].append(registers[param])
                else:
                    logger.info('the base object last invoked is not saved or used, and perform the same propagation as one for methods called by system')
                    # assert len(inst.parameters) == 1, 'parameters are more than one, and propagation is required'

                    i = 0
                    while i < len(inst.parameters):
                        # TODO: Skip base object, which is already propagated
                        param = inst.parameters[i]
                        data_type = inst.parameter_data_types[param]

                        assert param.startswith('p'), f'param is not p*, but {param = }, {inst = }'

                        # Search for the instance's value in StackFrameEntry.instances
                        value, ptids = MethodHeadValueResolver.get_instance_value(data_type,
                                                                                  instances,
                                                                                  param, new_values,
                                                                                  self_ptids, vms, mattr)

                        # Propagate the value
                        registers[param] = ValueResolver.get_value_copy(value)

                        # Increment i
                        if (data_type in numeric_types_64):
                            i += 2
                        else:
                            i += 1

            logger.debug({'inst': inst})
            logger.debug({'registers': registers})
        elif (isinstance(previous, StackFrameEntry) and len(inst.parameters) > 0):
            # For static methods called by the system, currently simply search previously-created instances for parameters.
            assert mattr == 'static'

            logger.info('generating parameter values for static method called by the system')

            i = 0
            while i < len(inst.parameters):
                param = inst.parameters[i]
                data_type = inst.parameter_data_types[param]

                # Search for the instance's value in self VM's instances
                value, ptids = MethodHeadValueResolver.get_instance_value(data_type,
                                                                          instances,
                                                                          param, new_values,
                                                                          self_ptids, vms, mattr)

                # Propagate the value
                registers[param] = ValueResolver.get_value_copy(value)

                # Increment i
                if (data_type in numeric_types_64):
                    i += 2
                else:
                    i += 1

        else:
            logger.info(f'new method is invoked by other method {previous.clss = }, {previous.method = }')
            # For methods invoked by app's other methods except threads.
            # If the callee has any parameter, perform the argument-parameter value propagation

            # If the invoked method is <init>, previous method can be new-instance.
            # If so, skip the propagation.
            if (len(inst.parameters) > 0):
                logger.info('performing value propagation for the new method')
                # Get caller's instruction and registers.
                # Then, propagate values in the registers to the callee's parameter registers

                caller_inst = classes[previous.clss].methods[previous.method].instructions[previous.pc]

                logger.info({'caller_inst': caller_inst})

                if (caller_inst.kind == 'new_instance'):
                    # Make sure that the invoked class has only one parameter
                    assert len(inst.parameters) == 1, f'more than one parameter are found at {inst = }'
                    # Make sure that the invoked method is a constructor
                    assert inst.is_constructor, f'new-instance starts non-constructor method {inst = }'

                    # Create the invoked class's base object
                    ValueResolver.set_register_value(inst.parameters[0], inst.parameter_data_types[inst.parameters[0]],
                                                     None, registers)
                    # Copy the created value to the previous new-instance instruction's destination
                    previous.registers[caller_inst.destination] = ValueResolver.get_value_copy(registers[inst.parameters[0]])
                    # Set the initialized flag
                    caller_inst.initialized = True

                elif (caller_inst.kind == 'invoke'):
                    # Propagate values between arguments and parameters one-to-one if one of below conditions is satisfied.
                    #   (1) class names and method names are matched
                    #   (2) caller invoking a constructor, and callee is a constructor, do the same
                    #         - names can be different, (e.g., init -> clinit
                    #   (3) caller's and callee's base objects are matched
                    #
                    # Prepare caller base object value.
                    if (len(caller_inst.arguments) > 0):
                        caller_base_obj_value = previous.registers[caller_inst.arguments[0]].value
                    else:
                        caller_base_obj_value = None
                    # Prepare callee base object value.
                    # Note that the below value will be None if callee is a constructor.
                    callee_base_obj = inst.parameters[0]
                    callee_base_obj_value = new_values.get(callee_base_obj)

                    if (#(caller_inst.class_name == invoked_class and caller_inst.method_name == invoked_method) or
                        (mattr == 'static' and caller_inst.method_name == invoked_method) or # and       # Class names can be different in, e.g., DroidBench.Lifecycle.FragmentLifecycle2.
                        (mattr != 'static' and caller_inst.method_name == invoked_method and caller_base_obj_value == callee_base_obj_value) or  # Hence, use values instead of class names to match base objects.
                        (caller_inst.invoke_constructor and
                         inst.is_constructor and
                         (caller_inst.class_name == invoked_class or
                          caller_inst.class_name in classes[invoked_class].family
                         )
                        )  # or
                        # (caller_base_obj_value == callee_base_obj_value)  # Currently disabled base-object-based matching because it causes false matches)
                    ):
                        logger.info('caller and callee base objects match')
                        # For debugging constructor matching
                        # logger.error(f'{caller_inst.class_name = }')
                        # logger.error(f'{classes[caller_inst.class_name].family = }')  # This can cause KeyError
                        # logger.error(f'{invoked_class = }')
                        # logger.error(f'{classes[invoked_class].family = }')

                        # if parameter length is shorter than or equals to argument length, propagate the values between arguments and parameters
                        if (len(caller_inst.arguments) >= len(inst.parameters)):
                            # Propagate their values by one-to-one mapping.
                            # Use parameters as a basis because parameters can be shorter than arguments.
                            i = 0
                            while i < len(inst.parameters):
                                param = inst.parameters[i]

                                logger.info(f'newly logged {new_values.get(param) = }')
                                logger.info(f'propagating {previous.registers[caller_inst.arguments[i]].value = } to {param = }')

                                registers[param] = ValueResolver.get_value_copy(previous.registers[caller_inst.arguments[i]])

                                if (new_values.get(param) not in [None, NULL_REPRESENTATION, 'null', 'true', 'false', '\x00', '0.0', '-0.0'] and  # Not None or Null
                                    not new_values.get(param).startswith('[') and  # Not an array's value
                                    (isinstance(registers[param], ClassInstanceValue) or
                                     (isinstance(registers[param], PrimitiveValue) and registers[param].value == 0)) and  # Instance or primitive value
                                    registers[param].data_type not in string_types and            # Not a string
                                    registers[param].data_type != 'Ljava/lang/String;' and
                                    inst.parameter_data_types[param] not in string_types and
                                    inst.parameter_data_types[param] != 'Ljava/lang/String;' and
                                    registers[param].value is not None and                        # Not None
                                    str(new_values.get(param)) != str(registers[param].value)     # Values do not match
                                   ):
                                    logger.warning(f'{previous.clss = } {previous.method = } {previous.pc = }')
                                    logger.warning(caller_inst)
                                    logger.warning(inst)
                                    logger.warning(f'newly logged {new_values.get(param) = }')
                                    logger.warning(f'propagated {registers[param].value = } to {param = }')
                                    raise Exception('newly logged and propagated values do not match, and seems something went wrong')
                                if (registers[param].data_type == 'F' and
                                    new_values.get(param) is not None and
                                    round(float(new_values.get(param)), 3) != round(float(registers[param].value), 3)):
                                    logger.warning(f'{previous.clss = } {previous.method = } {previous.pc = }')
                                    logger.warning(caller_inst)
                                    logger.warning(inst)
                                    logger.warning(f'newly logged {new_values.get(param) = }')
                                    logger.warning(f'propagated {registers[param].value = } to {param = }')
                                    raise Exception('newly logged and propagated values do not match, and seems something went wrong')

                                # Increment i
                                if (inst.parameter_data_types[param] in numeric_types_64):
                                    i += 2
                                else:
                                    i += 1
                        else:
                            # Not propagating, but searching each parameter in previously-created instances.
                            i = 0
                            while i < len(inst.parameters):
                                param = inst.parameters[i]
                                data_type = inst.parameter_data_types[param]

                                assert param.startswith('p'), f'param is not p*, but {param = }, {inst = }'

                                # Search for the instance's value in StackFrameEntry.instances
                                value, ptids = MethodHeadValueResolver.get_instance_value(data_type,
                                                                                          instances,
                                                                                          param, new_values,
                                                                                          self_ptids, vms, mattr)

                                # Propagate the value
                                registers[param] = ValueResolver.get_value_copy(value)

                                # Increment i
                                if (data_type in numeric_types_64):
                                    i += 2
                                else:
                                    i += 1

                    else:
                        # The base objects are not matched.
                        logger.info('caller and callee base objects do not match')
                        # Next, detect reflection by checking the following conditions:
                        #   (1) caller's argument length is 3.
                        #   (2) caller's second argument and callee's base object are the same.
                        #   (3) caller's third argument is an array.
                        #   (4) (the array length is 0 and callee parameter length is one) or (the array's first element matches to callee's second argument)
                        if (len(caller_inst.arguments) == 3 and
                            previous.registers[caller_inst.arguments[1]].value == callee_base_obj_value and
                            isinstance(previous.registers[caller_inst.arguments[2]], ArrayInstanceValue) and
                            ((len(previous.registers[caller_inst.arguments[2]].value) == 0 and len(inst.parameters) == 1) or
                             (previous.registers[caller_inst.arguments[2]].value[0] == new_values.get(inst.parameters[1]).split(':')[0]))
                        ):
                            # Reflection is detected.
                            # caller{Method, Obj, Array} -> callee{Obj, Array elements}

                            # Propagate the base object
                            caller_second_arg = previous.registers[caller_inst.arguments[1]]
                            registers[callee_base_obj] = ValueResolver.get_value_copy(caller_second_arg)

                            # Propagate values by mapping third_arg:[elem1, elem2, ...] -> calle {Base_Object, elem1, elem2, ...}
                            caller_third_arg = caller_inst.arguments[2]
                            elements = previous.registers[caller_third_arg].elements

                            # Make sure that callee parameter length is the array size + 1
                            assert len(inst.parameters) == len(elements) + 1, 'reflection is falsely detected.'

                            for i, element in enumerate(elements):
                                registers[inst.parameters[i+1]] = ValueResolver.get_value_copy(element)
                        else:
                            # Here, the call is none of normal invocation, constructor, reflection, or thread.
                            # Find parameter instances in self VM's instances, and if not found, generate new values
                            # E.g., Ljava/lang/Class;->newInstance()Ljava/lang/Object; invokes <init>()V, and their base objects do not match.
                            # E.g., static Landroid/os/Looper;->loop()V invokes non-static handleMessage(Landroid/os/Message;)V
                            # E.g., native method invocation invokes a java method of the app

                            logger.info('no invocation pattern is detected')

                            i = 0
                            while i < len(inst.parameters):
                                param = inst.parameters[i]
                                data_type = inst.parameter_data_types[param]

                                # Search for the instance's value in self VM's instances
                                value, ptids = MethodHeadValueResolver.get_instance_value(data_type,
                                                                                          instances,
                                                                                          param, new_values,
                                                                                          self_ptids, vms, mattr)

                                # Propagate the value
                                registers[param] = ValueResolver.get_value_copy(value)

                                # Increment i
                                if (data_type in numeric_types_64):
                                    i += 2
                                else:
                                    i += 1
                else:
                    if (detect_failures):
                        raise Exception(f'caller is not invoke-kind nor new-instance, but {caller_inst = }')
                    else:
                        # Ignore the failure, and generate values of parameters
                        i = 0
                        while i < len(inst.parameters):
                            param = inst.parameters[i]
                            data_type = inst.parameter_data_types[param]

                            # Search for the instance's value in self VM's instances
                            value, ptids = MethodHeadValueResolver.get_instance_value(data_type,
                                                                                      instances,
                                                                                      param, new_values,
                                                                                      self_ptids, vms, mattr)

                            # Propagate the value
                            registers[param] = ValueResolver.get_value_copy(value)

                            # Increment i
                            if (data_type in numeric_types_64):
                                i += 2
                            else:
                                i += 1

            else:
                # If the new method is static and has no parameter, the value propagation is skipped
                logger.info('the new method has no parameter')

                # Just in case, check if the method's attribute is static
                assert mattr == 'static', f'non-static method has no parameter, {mattr = }, {inst = }'

                # If the invoked method is clinit, update the clinit_invoked flag
                if (invoked_method == '<clinit>()V'):
                    classes[invoked_class].clinit_invoked = True

                    # Remove all static fields because they are initialized at this point
                    for field_name in classes[invoked_class].fields['static'].keys():
                        field_key = f'{invoked_class}->{field_name}'
                        if (field_key in static_fields.keys()):
                            logger.debug(f'removing static field {field_key = }')
                            del static_fields[field_key]

            logger.debug({'inst': inst})
            logger.debug({'registers': registers})

    @staticmethod
    def get_instance_value(data_type, previous_instances, reg, new_values, self_ptids, vms, mattr):
        """
        Find or create and return the instance's value in StackFrameEntry.instances.
        TODO: The name with "instance" is not appropriate because primitive values are also processed.
        """
        reg_value = new_values.get(reg, None)
        if (reg_value is not None and
            reg_value != NULL_REPRESENTATION and
            data_type not in primitive_data_types and
            data_type not in string_types and
            not data_type.startswith('[')):
            # reg's value is logged, which means the method is not a constructor
            # find reg's instance, which is previously created, based on its class name and value (i.e., hashCode())

            matched_instances = previous_instances.get(reg_value, None)

            if (matched_instances is not None):
                # The instance is found
                # Instance duplication can occur, and return the latest instance
                # # Make sure that the instance does not duplicate
                # assert len(matched_instances) == 1, f'the instance duplicates {reg_value = }, {matched_instances = }'

                return matched_instances[-1], self_ptids

            # Since the all vms' instances have been merged to a dictionary, the below search is unnecessary.
#             # The instance can be initialized in another thread.
#             # Search other vms for reg's instance.
#             for ptids, vm_runner in vms.items():
#                 # Check only vms with different ptids
#                 if (ptids != self_ptids):
#                     matched_instances = vm_runner.vm.instances.get(reg_value, None)
# 
#                     if (matched_instances is not None):
#                         # The instance is found
#                         # Make sure that the instance does not duplicate
#                         assert len(matched_instances) == 1, 'the instance duplicates'
# 
#                         instance = matched_instances[0]
# 
#                         # Make sure that the instance is ClassInstanceValue
#                         assert isinstance(instance, ClassInstanceValue), 'the instance is not ClassInstanceValue'
# 
#                         # Save the instance to the self vm's instances (i.e., previous_instances)
#                         previous_instances[instance.value].append(instance)
# 
#                         return instance, ptids

        # Instance is not found, so create it
        if (reg == 'p0' and mattr != 'static'):
            # The assertion can be false because sometimes a class's method is called by the super class's constructor, which is called from the class's constructor.
            # # If a base object's instance is not found, the method should be a constructor, and the register (i.e., p0)'s value is not logged
            # assert reg_value is None, f'{reg_value = } is not None, but its instance is not found in {previous_instances.keys() = }'
            pass

        logger.info(f'generating {data_type = }, {reg = }, {reg_value}')
        value = ValueResolver.generate_value(data_type, reg_value)

        # Save the value if it is class reference-data type
        if (value.value not in [None, 0] and
            isinstance(value, ClassInstanceValue)
           ):
            previous_instances[value.value].append(value)

        return value, self_ptids

    @staticmethod
    def compare_values(value1, value2, data_type):
        """
        Compare array or class instances' identifiers, which are
            arrays: all elements' values
            class:  return values of hashCode().
        For class instances, currently, three patterns are found.
        Pattern1: <class_name>@<hex_string>
        Pattern2: <class_name>{<hex_string> <more_string>}
        Pattern3: Handler (<class_name>) {<hex_string>}
        Pattern4: { <string> }
        """
        assert value1 is not None, f'{value1 = }, failing to obtain a value'
        assert value2 is not None, f'{value2 = }, failing to obtain a value'

        if (data_type in primitive_data_types):
            # Primitive values can appear at method heads.
            # Currently, smalien does not match primitive values of arguments and parameters based on their values.
            return False
        elif (data_type.startswith('[')):
            # Compare array instances' values
            value1 = value1
            value2 = json.loads(value2)
            return value1 == value2
        else:
            # Compare class instances' values
            # These comparisons are incomplete and can cause false positives
            # For Pattern4, currently all comparison results will be True
            # For Pattern3, currently all comparison results will be True because of the else statement
            # TODO: Fix these comparisons
            if (value1.startswith('{') and value2.startswith('{')):
                # Pattern4
                return True
            if (value1 == value2):
                # Pattern3
                return True
            else:
                # Pattern1 and 2
                value1 = value1.split(' ')[0].rstrip('}')
                value2 = value2.split(' ')[0].rstrip('}')

                # Make sure values are not one or zero character
                assert len(value1) > 1 and len(value2) > 1, f'{value1 = }, {value2 = }'

                return value1 == value2

    @staticmethod
    def match_data_types_between_arguments_and_parameters(caller, callee):
        """
        Matching arguments' and parameters' data types.
        """
        logger.info(f'matching data types between arguments and parameters')
        logger.info(caller)
        if (caller is None):
            return False

        if (len(caller.arguments) != len(callee.parameters)):
            return False

        for i, arg in enumerate(caller.arguments):
            # Skip the base object
            if (i == 0):
                continue

            matched = False

            arg_type = caller.argument_data_types[arg]
            param_type = callee.parameter_data_types[callee.parameters[i]]
            # Primitive
            if (arg_type in primitive_data_types and
                arg_type == param_type):
                # Currently make primitive-data-type not matching because including primitive-data-type arguments causes false propagation in AndroidSpecific.View1.
                # matched = True
                pass
            # Array
            elif (arg_type.startswith('[') and
                  param_type.startswith('[')):
                if (arg_type == param_type):
                    matched = True
                elif (arg_type.endswith(';') and
                      param_type.endswith(';')):
                    # This is necessary for Threading.AsyncTask1
                    matched = True
            # Class
            elif (arg_type.startswith('L') and
                  param_type.startswith('L')):
                # Currently make class not matching because including class arguments causes false propagation in Lifecycle.FragmentLifecycle1.
                # matched = True
                pass

            if (not matched):
                return False

        return True

class InvokeValueResolver:
    """
    Resolve values at an invoke instruction.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        classes = kwargs['classes']
        current_class = kwargs['clss']
        instances = kwargs['instances']
        registers = kwargs['registers']
        new_values = kwargs['new_values']
        is_constructor = kwargs['is_constructor']
        after_invocation = kwargs['after_invocation']
        static_fields = kwargs['static_fields']

        # Decide action based on whether it is before or after the invocation
        if (after_invocation):
            # After the invocation.
            # Update values of the reference-data-type arguments if they are logged.
            # Currently, only base objects of constructors are the target
            # TODO: Target other reference-data-type arguments.
            #       Reference-data-type arguments should be handled at both this class and MoveResultValueResolver.
            if (inst.invoke_constructor):
                base = inst.arguments[0]
                if (base in new_values.keys()):
                    # Assume that the current value is None or the same as the new value
                    # The assumption can be false, and a value in the constructor and another value in the caller can be different
                    # assert registers[base].value is None or registers[base].value == new_values[base], f'{registers[base].value = }, {new_values[base] = }'

                    base_value = new_values[base]

                    # if (base_value in instances.keys()):
                    #     logger.error(f'the instance {base_value = } already exists')
                    #     registers[base] = ValueResolver.get_value_copy(instances[base_value][-1])
                    # else:
                    # Update the instance's value
                    if (inst.argument_data_types[base] in string_types):
                        # Update the string-type value
                        assert base_value.find(':') > 0, f': not found in {base_value = }'
                        registers[base].string = ':'.join(base_value.split(':')[1:])
                        registers[base].value = base_value.split(':')[0]
                    else:
                        # Update the non-string-type value
                        registers[base].value = base_value

                    # If base_value is contained in the self vm's instances,
                    # and their data types are app's classes and match
                    # (i.e., their class names are same or one inherits the other),
                    # copy value in the self vm's instances to registers[base].
                    # This is for case ICC.ServiceCommunication1,
                    # where a value of one of a method's arguments is same as a value of a constructor's base object.
                    # However, copying the value can break the chain of argument-parameter propagation for constructors.
                    # Hence, copy only components of the class value.
                    if (base_value in instances.keys() and
                        current_class in classes.keys() and
                        instances[base_value][-1].data_type in classes.keys() and
                        current_class in classes[instances[base_value][-1].data_type].family):
                        # For debugging management of a specific instance
                        # if (base_value == '133350560'):
                        #     logger.error(f'{current_class = }')
                        #     logger.error(classes[instances[base_value][-1].data_type].family)
                        #     logger.error(registers[base].fields.keys())
                        #     logger.error(instances[base_value][-1])
                        #     raise Exception(base_value)

                        # If the registers[base] has the same fields as one in instances,
                        # the registers[base] must have newer value, and skip the copying,
                        if (registers[base].fields.keys() != instances[base_value][-1].fields.keys()):
                            ValueResolver.copy_class_value_components(registers[base], instances[base_value][-1])
                    # Add the instance to the self vm's instances
                    elif (isinstance(registers[base], ClassInstanceValue) and
                          registers[base].value != 0
                         ):
                        # For debugging management of a specific instance
                        # if (base_value == '133350560'):
                        #     logger.error('instance is appended')
                        #     logger.error(registers[base])
                        instances[base_value].append(registers[base])
            else:
                # Detect reflective field access
                if (inst.class_name == REFLECTIVE_FIELD_ACCESS['class'] and
                    inst.method_name == REFLECTIVE_FIELD_ACCESS['method']
                   ):
                    logger.debug('reflective field access')
                    logger.debug(inst)

                    # Currently, only static fields are supported
                    if (inst.reflective_field_attr == 'static'):
                        static_fields[inst.reflective_field_name] = ValueResolver.get_value_copy(registers[inst.arguments[2]])

                    return

                # Update reference-data-type arguments' values
                for arg in inst.arguments:
                    if (inst.argument_data_types[arg] not in primitive_data_types and
                        inst.argument_data_types[arg].startswith('[') and  # currently only targeting arrays
                        arg in new_values.keys() and
                        new_values[arg] != NULL_REPRESENTATION and
                        registers[arg].value != new_values[arg]  # TODO: Change this because the value comparison between list and string is useless.
                       ):

                        # TODO: Taint will be removed, so requiring a method to preserve taint
                        logger.info(f'updating array {arg = } {inst.argument_data_types[arg] = } value from {registers[arg].value = } to {new_values[arg] = } after invocation')
                        # Copy new values to the array
                        array_new_value = ValueResolver.generate_value(inst.argument_data_types[arg], new_values[arg])
                        registers[arg].value = array_new_value.value
                        registers[arg].elements = array_new_value.elements
        else:
            # Before the invocation
            # Record information of the invocation into the base object for threading.
            # Ignore if the invoked method is either static or constructor
            if (not inst.invoke_static and not inst.invoke_constructor):
                base = inst.arguments[0]

                # Save the base object's data to its Opcode
                inst.base_object = registers[base]

                # Update the last_invoked
                registers[base].last_invoked = inst
                # Clear the last_invoked_arguments
                registers[base].last_invoked_arguments = []

                # Save non-base arguments' values
                if (len(inst.arguments) > 1):
                    for arg in inst.arguments_without_64bit_pairs[1:]:
                        registers[base].last_invoked_arguments.append(registers[arg])

            # Record OutputStream for backward taint propagation.
            # This is a prototype implementation.
            if (inst.invoke_constructor and len(inst.arguments) > 1 and inst.argument_data_types[inst.arguments[1]] in ['Ljava/io/OutputStream;', 'Ljava/lang/Appendable;']):
                logger.warning(f'recording OutputStream {inst.arguments[1] = } into {inst.arguments[0] = }')
                registers[inst.arguments[0]].outputstream = registers[inst.arguments[1]]

class ReturnValueResolver:
    """
    Resolve values at a return instruction.
    TODO: Implement for threading and reflection.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']

        # If there is no return value (i.e., return-void), no propagation required
        if (inst.register is None):
            return

        previous = kwargs['previous']

        # If the caller is the Android system, no propagation required
        # TODO: The return value could be saved somewhere for future analysis
        if (isinstance(previous, StackFrameEntry)):
            return

        registers = kwargs['registers']
        classes = kwargs['classes']

        # Get source and destination
        source = inst.register
        destination = ReturnValueResolver.get_return_destination(previous, classes)

        # Propagate the return value if the destination exists, which means the move-result is not dummy
        if (destination is not None):
            # Copy value from the source to destination
            previous.registers[destination] = ValueResolver.get_value_copy(registers[source])

    @staticmethod
    def get_return_destination(previous, classes):
        """
        Get the destination of the return value.
        Previous data should be of existing class and method.
        """
        caller_inst = classes[previous.clss].methods[previous.method].instructions[previous.pc]

        # Check if everything with caller_inst is fine
        assert caller_inst.kind == 'invoke', f'Caller is not invoke-kind, but {caller_inst = }'
        assert caller_inst.in_app, f'Caller is not in app, but {caller_inst = }'

        return caller_inst.move_result.destination

class MoveResultValueResolver:
    """
    Resolve values at a move-result instruction corresponding to API methods and filled-new-array instruction.
    For Non-API methods, not this resolver, but ReturnValueResolver propagates the return value.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']

        if (inst.source.kind == 'filled_new_array'):
            # Corresponding instruction is filled_new_array
            MoveResultValueResolver.resolve_filled_new_array(**kwargs)

        elif (inst.source.kind == 'invoke'):
            # Corresponding instruction is invoke
            registers = kwargs['registers']
            instances = kwargs['instances']
            new_values = kwargs['new_values']
            self_ptids = kwargs['self_ptids']
            vms = kwargs['vms']

            reg = inst.destination
            invoke = inst.source

            # # If the destination's value is not logged, it should be in-app invocation or logging is disabled
            if (reg not in new_values.keys()):
                # If the invocation is in-app, finish the procedure
                if (invoke.in_app):
                    return

            # Handle special methods
            if (reg in new_values.keys()):
                processed = MoveResultValueResolver.handle_special_methods(invoke, reg, new_values[reg], registers, instances)
                if (processed):
                    return

            # Update reference-data-type arguments' values
            for arg in invoke.arguments:
                if (arg != reg and
                    invoke.argument_data_types[arg] not in primitive_data_types and
                    invoke.argument_data_types[arg].startswith('[') and  # currently only targeting arrays
                    arg in new_values.keys() and
                    (registers[arg].value != 0 and new_values[arg] != 'n') and
                    registers[arg].value != new_values[arg]):

                    # TODO: Elements' taint will be removed, so requiring a method to preserve taint
                    logger.info(f'updating array value from {registers[arg].value = } to {new_values[arg] = } after invocation')
                    ValueResolver.update_array_value(arg, new_values[arg], registers)
                    # ValueResolver.set_register_value(arg, invoke.argument_data_types[arg],
                    #                                  new_values[arg], registers)

            # If the emulation is pure static, move-result value should be generated with None as its value.
            new_value = new_values.get(reg)

            # Even if the value is logged, the invocation can be in-app, and a return value can exist.
            # To avoid overwriting such return value, especially in cases where the value is not primitive data type,
            # update the register only if its current value does not match with the new value.
            if (reg not in registers.keys() or
                inst.destination_data_type in primitive_data_types or
                (new_value is not None and
                 registers[reg].value != new_value.split(':')[0])
            ):
                # Currently, this resolver is disabled because it requires manual definitions.
                # Resolve values for specific API methods with pre-defined rules
                # resolvers = api_call_edge_value_resolvers.get(invoke.class_name, {})
                # if (invoke.method_name in resolvers.keys()):
                #     # Pre-defined rule is found for the method.
                #     resolvers[invoke.method_name].run(**kwargs)
                # else:
                if (True):
                    # Pre-defined rule is not found for the method.
                    # Set the new return value to the destination of the move-result.

                    # If the data type is not primitive-data-type, search the instance.
                    # This condition must be satisfied because if the value is hashCode and int data type, the value will mistakenly match with a previously-created instance
                    if (inst.destination_data_type not in primitive_data_types and inst.destination_data_type not in string_types and inst.castable_to not in string_types):
                        # Search instances for the new return value, and copy it if it is found
                        matched_instance = MoveResultValueResolver.search_previously_created_instance(new_value, instances, self_ptids, vms)
                        if (matched_instance is not None):
                            assert new_value != NULL_REPRESENTATION, f'{NULL_REPRESENTATION = } must not exist in instances'

                            # Instance is found
                            logger.info(f'returned value {new_value = }, {reg = }, of an API method call matches to a previously saved instance')
                            registers[reg] = ValueResolver.get_value_copy(matched_instance)
                            return

                    # If the new value is not found in instances, create a new one
                    # If the castable_to is not None, use it as data type
                    if (inst.castable_to is not None):
                        data_type = inst.castable_to
                    else:
                        data_type = inst.destination_data_type

                    # If the value is None, and value_logging is enabled, a log must be lost.
                    # Running the app again is required.
                    ValueResolver.set_register_value(reg, data_type,
                                                     new_value, registers)

                    # TEST_MOVE_RESULT_INSTANCE_ADD
                    if (isinstance(registers[reg], ClassInstanceValue) and
                        registers[reg].data_type not in string_types and  # Now logging the identifier of string, and the condition is unnecessary, but remove this line after fix the instance search
                        registers[reg].value != 0
                       ):
                        instances[registers[reg].value].append(registers[reg])
                    # TEST_MOVE_RESULT_INSTANCE_ADD
            elif ((inst.destination_data_type in string_types or inst.castable_to in string_types) and
                  reg in registers.keys() and
                  new_value is not None and
                  registers[reg].value == new_value.split(':')[0]):
                # Update the string to make sure that the register has the exact value.
                # This is for apps, where a string value has not the exact value because of the array-logging difficulty.
                registers[reg].string = new_value.split(':')[1]

        else:
            raise Exception('move-result corresponds to neither filled_new_array or invoke')

    @staticmethod
    def handle_special_methods(invoke, reg, new_value, registers, instances):
        """
        Detect and handle methods requiring special process.
        TODO: Need more generic method.
        """
        if (invoke.class_name == 'Ljava/lang/Object;' and
            invoke.method_name == 'clone()Ljava/lang/Object;'
           ):
            logger.info('Ljava/lang/Object;->clone()Ljava/lang/Object; is invoked')

            base_object = registers[invoke.arguments[0]]

            ValueResolver.set_register_value(reg, base_object.data_type,
                                             new_value, registers)

            # Copy from base object to the new register.
            # Currently use deepcopy instead of shallow copy, which might different from the smali code.
            registers[reg].taint = copy.deepcopy(base_object.taint)
            registers[reg].fields = copy.deepcopy(base_object.fields)

            # Add this to the instances
            instances[registers[reg].value].append(registers[reg])

            return True

        return False

    @staticmethod
    def search_previously_created_instance(value, instances, self_ptids, vms):
        """
        Search a previously-created instance that matches to the given value
        """
        # Search in the self instances
        matched_instances = instances.get(value, None)
        if (matched_instances is not None):
            # The instances can duplicate, and return the latest of them
            # # Make sure that the instance does not duplicate
            # assert len(matched_instances) == 1, 'the instance duplicates'
    
            return matched_instances[-1]

        # Since the all vms' instances have been merged to a dictionary, the below search is unnecessary.
#         # Search in the other VMs' instances
#         # The instance can be initialized in another thread.
#         for ptids, vm_runner in vms.items():
#             # Check only vms with different ptids
#             if (ptids != self_ptids):
#                 matched_instances = vm_runner.vm.instances.get(value, None)
# 
#                 if (matched_instances is not None):
#                     # The instance is found
#                     # Make sure that the instance does not duplicate
#                     # assert len(matched_instances) == 1, f'the instance duplicates for {value = }'
# 
#                     # Use the newest instance
#                     instance = matched_instances[-1]
# 
#                     # Make sure that the instance is ClassInstanceValue
#                     assert isinstance(instance, ClassInstanceValue), 'the instance is not ClassInstanceValue'
# 
#                     # Save the instance to the self vm's instances (i.e., previous_instances)
#                     instances[instance.value].append(instance)
# 
#                     return instance

    @staticmethod
    def resolve_filled_new_array(**kwargs):
        """
        Resolve values at a move-result with filled-new-array instruction.
        """
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']
        instances = kwargs['instances']

        filled_new_array = inst.source

        # The size of array depends on the number of arguments
        size = len(filled_new_array.arguments)

        # Obtain values
        values = [registers[arg].value for arg in filled_new_array.arguments]

        ValueResolver.set_register_value(inst.destination, filled_new_array.ret_type,
                                         json.dumps(values), registers)

        # Add the new array to self vm's instances
        # Currently, data type is considered as java.lang.object[]
        # TODO: This should be refined, also, class instances' data types.
        # This is disabled because the instances is used for matching base objects
        # instances['[Ljava/lang/Object;'].append(registers[inst.destination])

class ConstValueResolver:
    """
    Resolve values at a const instruction.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']

        ValueResolver.set_register_value(inst.destination, inst.data_type, inst.value, registers)

class ConstStringValueResolver:
    """
    Resolve values at a const-string instruction.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']
        new_values = kwargs['new_values']

        ValueResolver.set_register_value(inst.destination, inst.data_type,
                                         new_values.get(inst.destination), registers,
                                         string=inst.value)

class ConstClassValueResolver:
    """
    Resolve values at a const-class instruction.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']
        new_values = kwargs['new_values']

        ValueResolver.set_register_value(inst.destination,
                                         inst.data_type,
                                         new_values.get(inst.destination),
                                         registers)

class NewInstanceValueResolver:
    """
    Resolve values at a new-instance instruction.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']
        new_values = kwargs['new_values']
        instances = kwargs['instances']
        classes = kwargs['classes']

        # The class's clinit() method should be called
        # if the class is implemented in the app, and the class has a clinit() method.
        clinit_invoked = ValueResolver.check_clinit_invoked(inst.class_name, classes)
        if (not clinit_invoked):
            # Raise the exception to break the emulation
            raise ClinitInvokedException(inst)

        # Set the register's value if the register has not been initialized.
        if (not inst.initialized):
            ValueResolver.set_register_value(inst.destination, inst.class_name, None, registers)

        # Reset the flag for next execution
        inst.initialized = False

        # The new instance is not registered to self vm's instances here, because the instance representation is unknown at this point.
        # The new instance will be registered when the instance is initialized with its constructor.

class InstanceOfValueResolver:
    """
    Resolve values at an instance-of instruction.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']
        new_values = kwargs['new_values']

        ValueResolver.set_register_value(inst.destination, inst.destination_data_type,
                                         new_values.get(inst.destination), registers)

#
# Array operation
#
class NewArrayValueResolver:
    """
    Resolve values at a new-array instruction.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']
        instances = kwargs['instances']

        # Array and size registers can be the same, so the size's value should be preserved first.
        size = registers[inst.size].value

        ValueResolver.set_register_value(inst.array, inst.array_data_type,
                                         '[]', registers)

        # Initialize array with default values
        NewArrayValueResolver.initialize_array_with_default_value(registers[inst.array], size, inst.item_data_type)

        # Add the new array to self vm's instances
        # Currently, data type is considered as java.lang.object[]
        # TODO: This should be refined, also, class instances' data types.
        # This is disabled because the instances is used for matching base objects
        # instances['[Ljava/lang/Object;'].append(registers[inst.array])

    @staticmethod
    def initialize_array_with_default_value(array, size, data_type):
        """
        Add <size> elements of default_value, which is 0, to <array>.
        """
        default_value = 0
        for i in range(size):
            array.elements.append(ValueResolver.generate_value('I', default_value))
            array.value.append(default_value)

class FillArrayDataValueResolver:
    """
    Resolve values at a fill-array-data instruction.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']

        array = registers[inst.array]

        for i, value in enumerate(inst.array_data.array_data):
            # Generate an element value
            element = ValueResolver.generate_value(array.element_data_type, value)

            # Append the element to the array
            array.elements[i] = element
            array.value[i] = element.value

class ArrayLengthValueResolver:
    """
    Resolve values at an array-length instruction.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']
        new_values = kwargs['new_values']

        if (inst.logging and inst.destination in new_values.keys()):
            value = new_values[inst.destination]
        else:
            value = len(registers[inst.array].value)

        ValueResolver.set_register_value(inst.destination, inst.destination_data_type,
                                         value, registers)

class AputValueResolver:
    """
    Resolve values at an aput instruction.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']

        index = registers[inst.index]
        source = registers[inst.source]

        # Update array's elements
        registers[inst.array].elements[index.value] = source

        # Update array's value
        registers[inst.array].value[index.value] = source.value

class AgetValueResolver:
    """
    Resolve values at an aget instruction.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']
        instances = kwargs['instances']
        self_ptids = kwargs['self_ptids']
        vms = kwargs['vms']

        index = registers[inst.index]
        array = registers[inst.array]

        # Update array's elements
        try:
            element = array.elements[index.value]

            if (isinstance(element, ClassInstanceValue)):
                # and element.data_type not in string_types):  # Now logging the identifier of string, and the condition is unnecessary.

                # Check whether the value is a previously-created instance
                matched_instance = MoveResultValueResolver.search_previously_created_instance(element.value, instances, self_ptids, vms)
                logger.info(f'searching aget element {element.value = } in instances, result is {matched_instance is not None}')
                if (matched_instance is not None):
                    # Instance is found
                    logger.info('aget element value matches to a previously-created instance')
                    # Copy the instance to the destination
                    registers[inst.destination] = ValueResolver.get_value_copy(matched_instance)
                    # Replace the array's value with the found value
                    array.elements[index.value] = ValueResolver.get_value_copy(matched_instance)
                    array.value[index.value] = matched_instance.value

                    return

            # For others, copy the element value to the destination register
            registers[inst.destination] = ValueResolver.get_value_copy(element)

        except IndexError as e:
            # Detected that ArrayIndexOutOfBoundsException is occurring
            # Make sure the index equals to or greater than the array length
            assert index.value >= len(array.elements), f'{index.value = } < {len(array.elements) = }'

            logger.info('ArrayIndexOutOfBoundsException occured')

            raise ExceptionOccurException(inst)

class MoveValueResolver:
    """
    Resolve values at a move instruction.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']

        ValueResolver.move_value_between_registers(inst.source, inst.destination,
                                                   registers)

class IgetValueResolver:
    """
    Resolve values at an iget instruction.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']
        new_values = kwargs['new_values']
        instances = kwargs['instances']
        self_ptids = kwargs['self_ptids']
        vms = kwargs['vms']

        instance_value = registers[inst.source]

        # Detect NullPointerException
        if (instance_value.value == 0):

            logger.info('NullPointerException occured')

            raise ExceptionOccurException(inst)

        if (inst.castable_to is not None):
            data_type = inst.castable_to
        else:
            data_type = inst.destination_data_type

        if (inst.field not in instance_value.fields.keys()):
            # The field has not been initialized
            # Check wehther the field's value is available
            # inst.logging must be checked because a previously-logged value of the register at another location might exist in new_values
            value = new_values.get(inst.destination)
            if (value is not None and inst.logging):
                # Check whether the value is a previously-created instance
                # If the data type is not primitive-data-type, search the instance.
                # This condition must be satisfied because if the value is hashCode and int data type, the value will mistakenly match with a previously-created instance
                if (data_type not in primitive_data_types and data_type not in string_types):
                    # Search instances for the new return value, and copy it if it is found
                    matched_instance = MoveResultValueResolver.search_previously_created_instance(value, instances, self_ptids, vms)
                    if (matched_instance is not None):
                        # Instance is found
                        logger.info('iget destination value matches to a previously-created instance')
                        registers[inst.destination] = ValueResolver.get_value_copy(matched_instance)
                        return

                # If the new value is not found in instances, create a new one
                ValueResolver.set_register_value(inst.destination, data_type, value, registers)
            else:
                # Use default value, which is PrimitiveValue int value=0
                # TODO: This can be merged with SgetValueResolver
                # TODO: For more precision, data_type should be 'F' if data_type is 'F'
                ValueResolver.set_register_value(inst.destination, 'I', 0, registers)
        else:

            # Move an instance field's value to a register.
            try:
                registers[inst.destination] = ValueResolver.get_value_copy(instance_value.fields[inst.field])
            except (AttributeError, KeyError) as e:
                raise Exception(f'Moving from {inst.source = } {inst.field = } to {inst.destination = } failed') from e

            # The field exists.
            # However, it can have been modified by, e.g., a native method.
            # Check wehther the field's value is available.
            value = new_values.get(inst.destination)
            if (value is not None and inst.logging):
                # Compare the newly-logged value with the value previously saved.
                new_logged_value = ValueResolver.generate_value(data_type, value)
                if (new_logged_value.value != registers[inst.destination].value):
                    logger.info(f'newly-logged iget {inst.field = } {value = } does not match to the previously-saved value')
                    if (isinstance(registers[inst.destination], ArrayInstanceValue)):
                        # Keep the current ArrayInstanceValue instance, and copy only values
                        ValueResolver.update_array_value(inst.destination, value, registers)
                    else:
                        # Set the newly-logged value
                        ValueResolver.set_register_value(inst.destination, data_type,
                                                         value, registers)
                        # Also, update the instance's field
                        instance_value.fields[inst.field] = ValueResolver.get_value_copy(registers[inst.destination])

class IputValueResolver:
    """
    Resolve values at an iput instruction.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']
        mattr = kwargs['mattr']

        # Move a register's value to an instance field.
        try:
            registers[inst.destination].fields[inst.field] = ValueResolver.get_value_copy(registers[inst.source])
        except (AttributeError, KeyError) as e:
            raise Exception(f'Moving from {inst.source = } to {inst.destination = } {inst.field = } failed') from e

class SgetValueResolver:
    """
    Resolve values at a sget instruction.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']
        static_fields = kwargs['static_fields']
        new_values = kwargs['new_values']
        classes = kwargs['classes']

        # This can get too large to print
        # logger.info(static_fields)

        if (inst.field not in static_fields.keys()):
            # The field has not been initialized.
            # Check wehther the field's value is available
            value = new_values.get(inst.destination)
            # inst.logging should be checked because the register's old value can exist in new_values.
            if (value is not None and inst.logging):
                logger.debug('new logged value is set to sget destination')
                # Set the new value
                ValueResolver.set_register_value(inst.destination, inst.destination_data_type,
                                                 value, registers)
            else:
                # The class's clinit() method should be called
                # if the field is implemented in the app, and the class has a clinit() method.
                clinit_invoked = ValueResolver.check_clinit_invoked(inst.class_name, classes)
                if (not clinit_invoked):
                    # Raise the exception to break the emulation
                    raise ClinitInvokedException(inst)

                logger.debug('no value is logged, and generating a default value for sget destination')
                if (inst.default_value is not None):
                    logger.info(f'using {inst.default_value = } for {inst.destination = }')
                    registers[inst.destination] = ValueResolver.generate_value(inst.destination_data_type, inst.default_value)
                else:
                    # For other fields, set a default value that are either 0 or Null.
                    # Currently, both values are represented by int primitive value with value=0.
                    ValueResolver.set_register_value(inst.destination, 'I', 0, registers)
        else:
            # The field has been initialized once.
            # However, it can have been re-initialized.
            # Check wehther the field's value is available.
            value = new_values.get(inst.destination)
            if (value is not None and inst.logging):
                # Compare the newly-logged value with the value previously saved.
                new_logged_value = ValueResolver.generate_value(inst.destination_data_type, value)
                if (new_logged_value.value != static_fields[inst.field].value):
                    logger.debug(f'newly-logged sget field {value = } does not match to the previously-saved value')
                    # Set the newly-logged value
                    ValueResolver.set_register_value(inst.destination, inst.destination_data_type,
                                                     value, registers)
                    # Also, update the static_fields' data
                    static_fields[inst.field] = ValueResolver.get_value_copy(registers[inst.destination])

                    return

            # Move a static field's value to a register.
            try:
                logger.debug(f'moving value from {inst.field = } to {inst.destination = }')
                registers[inst.destination] = ValueResolver.get_value_copy(static_fields[inst.field])
            except (AttributeError, KeyError) as e:
                raise Exception(f'Moving from {inst.field = } to {inst.destination = } failed') from e

class SputValueResolver:
    """
    Resolve values at a sput instruction.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']
        static_fields = kwargs['static_fields']
        classes = kwargs['classes']

        assert inst.field.find(';->') > 0, f'strange field name {inst.field = }'

        # The class's clinit() method should be called
        # if the field is implemented in the app, and the class has a clinit() method.
        clinit_invoked = ValueResolver.check_clinit_invoked(inst.class_name, classes)
        if (not clinit_invoked):
            # Raise the exception to break the emulation
            raise ClinitInvokedException(inst)

        # Move a register's value to a static field
        try:
            static_fields[inst.field] = ValueResolver.get_value_copy(registers[inst.source])
        except (AttributeError, KeyError) as e:
            raise Exception(f'Moving from {inst.source = } to {inst.field = } failed') from e

class UnopValueResolver:
    """
    Resolve values at an unop instruction.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')
        
        inst = kwargs['inst']
        registers = kwargs['registers']

        source = registers[inst.source].value

        result = eval(inst.expression, {'source': source})

        # Convert data type
        try:
            if (inst.destination_data_type == 'F'):
                result = numpy.float32(result)
            elif (inst.destination_data_type == 'I'):
                result = numpy.int32(result)
        except Exception as e:
            raise Exception(f'failed to convert {result = }') from e

        ValueResolver.set_register_value(inst.destination, inst.destination_data_type,
                                         result, registers)

class BinopValueResolver:
    """
    Resolve values at a binop instruction.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')
        
        inst = kwargs['inst']
        registers = kwargs['registers']

        source1 = registers[inst.source1].value
        source2 = registers[inst.source2].value

        # Detect float divid-by-zero computation
        # The result will be positive or negative infinity
        if (inst.expression.find(' / ') > -1 and
            inst.data_type in numeric_types_floating_point and
            float(source2) == 0
           ):
            result = source1 * float('inf')

        elif (inst.instruction.find('shl-int') > -1):
            result = numpy.left_shift(source1, source2)

        else:
            try:
                result = eval(inst.expression, {'source1': source1, 'source2': source2})
            except Exception as e:
                logger.error(registers)
                raise Exception(f'Operation {inst.instruction = } ({inst.data_type = }) failed with {source1 = } and {source2 = }') from e

        # Convert data type
        try:
            if (inst.data_type == 'F'):
                result = numpy.float32(result)
            elif (inst.data_type == 'I'):
                result = numpy.int32(result)
        except Exception as e:
            raise Exception(f'failed to convert {result = }') from e

        ValueResolver.set_register_value(inst.destination, inst.data_type,
                                         result, registers)

class BinopLit8ValueResolver:
    """
    Resolve values at a binop/lit8 instruction.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')
        
        inst = kwargs['inst']
        registers = kwargs['registers']

        source = registers[inst.source].value

        # Detect float divid-by-zero computation
        # The result will be positive or negative infinity
        if (inst.expression.find(' / ') > -1 and
            inst.data_type in numeric_types_floating_point and
            float(inst.literal) == 0
           ):
            result = source * float('inf')

        elif (inst.instruction.find('shl-int') > -1):
            result = numpy.left_shift(source, inst.literal)

        else:
            try:
                result = eval(inst.expression, {'source1': source, 'source2': inst.literal})
            except Exception as e:
                raise Exception(f'Operation {inst.instruction = } ({inst.data_type = }) failed with {source = } and {inst.literal = }') from e

        # Check data type
        # Convert data type
        try:
            if (inst.data_type == 'F'):
                result = numpy.float32(result)
            elif (inst.data_type == 'I'):
                result = numpy.int32(result)
        except Exception as e:
            raise Exception(f'failed to convert {result = }') from e

        ValueResolver.set_register_value(inst.destination, inst.data_type,
                                         result, registers)

class Binop2addrValueResolver:
    """
    Resolve values at a binop/2addr instruction.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')
        
        inst = kwargs['inst']
        registers = kwargs['registers']

        # The first source register is the destination register
        source1 = registers[inst.destination].value
        source2 = registers[inst.source2].value

        # Detect float divid-by-zero computation
        # The result will be positive or negative infinity
        if (inst.expression.find(' / ') > -1 and
            inst.data_type in numeric_types_floating_point and
            float(source2) == 0
           ):
            result = source1 * float('inf')

        elif (inst.instruction.find('shl-int') > -1):
            result = numpy.left_shift(source1, source2)

        else:
            try:
                result = eval(inst.expression, {'source1': source1, 'source2': source2})
            except Exception as e:
                raise Exception(f'Operation {inst.instruction = } ({inst.data_type = }) failed with {source1 = } and {source2 = }') from e

        # Check data type
        # Convert data type
        try:
            if (inst.data_type == 'F'):
                result = numpy.float32(result)
            elif (inst.data_type == 'I'):
                result = numpy.int32(result)
        except Exception as e:
            raise Exception(f'failed to convert {result = }') from e

        ValueResolver.set_register_value(inst.destination, inst.data_type,
                                         result, registers)

class CmpValueResolver:
    """
    Resolve values at a cmp instruction.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']

        source1 = registers[inst.source1].value
        source2 = registers[inst.source2].value

        # cmp sets destination to 1 if source1 > source2
        # cmp sets destination to -1 if source1 < source2
        # cmp sets destination to 0 if source1 == source2
        # cmp has bias, but currently the bias is not emulated by this expression
        # TODO: Emulate the bias
        result = 1 if (source1 > source2) else (-1 if (source1 < source2) else 0)

        ValueResolver.set_register_value(inst.destination, inst.destination_data_type,
                                         result, registers)

#
# Try-catch
#

class ThrowValueResolver:
    """
    Resolve values at a throw instruction.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        vm = kwargs['vm']
        inst = kwargs['inst']
        registers = kwargs['registers']

        # Save exception value to the VM's field
        vm.exception_value = registers[inst.register]

class MoveExceptionValueResolver:
    """
    Resolve values at a move-exception instruction.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        vm = kwargs['vm']
        inst = kwargs['inst']
        registers = kwargs['registers']
        new_values = kwargs['new_values']

        new_exception_value = new_values.get(inst.destination)

        # Restore exception value to the VM's field
        if (vm.exception_value is not None and vm.exception_value.value == new_exception_value):
            # Move the exception value
            registers[inst.destination] = vm.exception_value

            # Clear the exception value
            vm.exception_value = None

        else:
            ValueResolver.set_register_value(inst.destination, inst.destination_data_type,
                                             new_exception_value, registers)

class CheckCastValueResolver:
    """
    Resolve values at a check-cast instruction.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        vm = kwargs['vm']
        inst = kwargs['inst']
        registers = kwargs['registers']
        new_values = kwargs['new_values']

        if (inst.register in new_values.keys()):

            assert inst.class_name == 'Ljava/lang/Class;', f'need more implementation for {inst.class_name = }'

            assert inst.register in registers.keys()

            # Update the value and type
            # Note that this stops the taint propagation
            ValueResolver.set_register_value(inst.register, inst.class_name,
                                             new_values.get(inst.register), registers)
