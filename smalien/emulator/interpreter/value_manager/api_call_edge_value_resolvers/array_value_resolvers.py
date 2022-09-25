import logging
import copy

from ..value_resolver_utils import ValueResolver

logger = logging.getLogger(name=__name__)


# This is currently not used.

#
# Array
#
class ArrayNewInstanceValueResolver:
    """
    Resolve values at Array.newInstance() invocation.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        registers = kwargs['registers']

        inst = kwargs['inst']
        invoke = inst.source

        # Obtain destination data type from the destination's identifier logged
        destination_value = kwargs['new_values'][inst.destination]
        assert destination_value.find('@') > 0, f'@ does not found in {destination_value = }'
        destination_data_type = destination_value.split('@')[0]

        # Obtain array's size information
        array_size_info = registers[invoke.arguments[1]].value

        # Create an array in the destination register
        ValueResolver.set_register_value(inst.destination, destination_data_type,
                                         '[]', registers)

        # Initialize array with default values, which is int 0
        element = ValueResolver.generate_value('I', 0)
        array = registers[inst.destination]
        element_data_type = destination_data_type.lstrip('[')

        if (len(array_size_info) > 1):
            # Generate element for multidimensional array
            # Note that <array_size_info> itself should not be reversed
            for i, size in enumerate(reversed(array_size_info[1:])):
                # Generate new element
                new_element = ValueResolver.generate_value(f"{'['*(i+1)}{element_data_type}", '[]')
                # Initialize the new_element with previous element
                for i in range(size):
                    # Append the element.
                    # Each element should point to a unique instance.
                    new_element.elements.append(copy.deepcopy(element))

                    # Append the value.
                    # The value points to the same instance as the element.value
                    new_element.value.append(new_element.elements[-1].value)
                # Replace the element
                element = new_element

        # Fill the destination array with the first-level size information
        for i in range(array_size_info[0]):
            # Append the element.
            # Each element should point to a unique instance.
            array.elements.append(copy.deepcopy(element))

            # Append the value.
            # The value points to the same instance as the element.value
            array.value.append(array.elements[-1].value)
