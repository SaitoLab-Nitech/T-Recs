import logging
import dataclasses

from .structures import PrimitiveValue
from .value_generators import ValueGenerator

logger = logging.getLogger(name=__name__)


class ValueResolver:
    """
    Utility class for *ValueResolver classes.
    """
    @staticmethod
    def generate_value(data_type, value):
        """
        Generate a new value.
        """
        return ValueGenerator.generate(data_type, value)

    @staticmethod
    def set_register_value(reg, data_type, value, registers, string=None):
        """
        Set a register a new value.
        """
        registers[reg] = ValueGenerator.generate(data_type, value, string=string)

    @staticmethod
    def update_array_value(reg, value, registers):
        """
        Update the array with the new values.
        """
        array = registers[reg]

        new_array = ValueGenerator.generate(array.data_type, value)

        # Copy elements' values
        array.value = new_array.value
        # Copy elements
        array.elements = new_array.elements

        # Remove the new_array
        del new_array

    @staticmethod
    def copy_class_value_components(dst, src):
        """
        Copy class value's components to another class.
        """

        # Make sure that the destination has no data of fields
        assert len(dst.fields.keys()) == 0, f'deleting {dst.fields.keys() = }, {dst.data_type = }, {src.data_type = }, {src.fields.keys() = }'

        # Currently, skipping some components because they seem unnecessary
        dst.taint = src.taint
        dst.fields = src.fields
        dst.contained_values = src.contained_values

    @staticmethod
    def get_value_copy(value):
        """
        Return a copy of the value depending on the value type.
        """
        if (isinstance(value, PrimitiveValue)):
            # Copy the value if it is primitive type.
            # Note that replace() is a shallow copy.
            return dataclasses.replace(value)
        return value

    @staticmethod
    def move_value_between_registers(source, destination, registers):
        """
        Move a register's value to another register.
        """
        registers[destination] = ValueResolver.get_value_copy(registers[source])

    @staticmethod
    def check_clinit_invoked(class_name, classes):
        """
        Return true if the given class's clinit has been invoked.
        Otherwise, return the result of checking the class's parent.
        """
        if (class_name in classes.keys() and
            not classes[class_name].ignore
           ):
            if (classes[class_name].clinit_implemented
               ):
                return classes[class_name].clinit_invoked
            else:
                return ValueResolver.check_clinit_invoked(classes[class_name].parent, classes)

        return True
