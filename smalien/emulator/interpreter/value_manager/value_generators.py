import logging
import json

from .structures import PrimitiveValue, PrimitiveValue64, ArrayInstanceValue, ClassInstanceValue, ClassReferenceValue
from smalien.data_types import primitive_data_types, numeric_types_integer, numeric_types_floating_point, numeric_types_64, boolean_type, character_type, byte_type, string_types, string_types_identifier_logged, NULL_REPRESENTATION, JAVA_TO_SMALI_PRIMITIVE_TYPE_CLASS

logger = logging.getLogger(name=__name__)


class ValueGenerator:
    """
    Generate a value for a register based on the data type.
    """
    @staticmethod
    def generate(data_type, value, string=None):
        category = ValueGenerator.get_data_type_category(data_type, value)

        return value_generator_mapping[category].run(value=value, data_type=data_type, string=string)

    @staticmethod
    def get_data_type_category(data_type, value):
        try:
            if (data_type in primitive_data_types):
                return 'primitive'
            elif (data_type.startswith('[')):
                return 'array'
            elif (data_type == 'Ljava/lang/Object;' and isinstance(value, str) and value.startswith('[')):
                # java.lang.Object can be logged as an array, which is dynamically decided by the instrumented code.
                return 'array'
            # elif (data_type in ['Ljava/lang/Class;']):#, 'Ljava/lang/reflect/Type;']):
            #     return 'reference'
            elif (data_type.startswith('L')):
                return 'class'
            else:
                assert False, f'Failed to get data type category, {data_type = }'
        except AttributeError as e:
            raise Exception(f'data_type variable is not a string but {data_type = }')

class PrimitiveValueGenerator:
    """
    Generate a primitive value for a register.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        value = kwargs['value']
        data_type = kwargs['data_type']

        # Convert data type based on the data_type to use the value for calculation and branches
        # Skip if the value is NaN
        if (value != value):
            pass
        elif (data_type in numeric_types_integer or data_type in numeric_types_floating_point):
            # Converting a large number, such as -5165993188905959888, to float can lose precision.
            # So, first, check if the value is integer.
            if (str(value).find('.') < 0):
                try:
                    value = int(value)
                except (OverflowError, ValueError):
                    # Value is either float infinity or float NaN
                    value = float(value)
            else:
                value = float(value)
            # if (value.is_integer()):
            #     value = int(value)
        # elif (data_type in numeric_types_integer):
        #     value = int(value)
        # elif (data_type in numeric_types_floating_point):
        #     value = float(value)
        elif (data_type in boolean_type):
            # Convert boolean strings true/false to integer values 1/0
            assert value in ['true', True, 'false', False, 0], f'weird boolean {value = }'
            value = 1 if value in ['true', True] else 0
        elif (data_type in character_type):
            # Parser saves constant characters as int values, and Logger saves characters as string values.
            # Hence, if the given value is not int, use ord() to convert it to an int value.
            if (not isinstance(value, int)):
                value = ord(value)
        elif (data_type in byte_type):
            if (not isinstance(value, int)):
                try:
                    value = int(value)
                except Exception as e:
                    raise Exception(f'int() failed with {value = }') from e

        if (data_type in numeric_types_64):
            primitive_value =  PrimitiveValue64(value=value, data_type=data_type)
        else:
            primitive_value = PrimitiveValue(value=value, data_type=data_type)

        return primitive_value


class ArrayInstanceValueGenerator:
    """
    Generate an array instance value for a register.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        value = kwargs['value']
        data_type = kwargs['data_type']

        if (data_type == 'Ljava/lang/Object;'):
            # The data type must be logged at the end of the logged value
            data_type = '['+value[-1]
            value = value[:-1]

        # Currently, the argument value can be a list or string.
        # If it is a string, convert it to a list.
        if (not isinstance(value, list)):
            # A list can be [null], which is converted to [None] by json.loads().
            # None will be replaced with 0 by initialize_array().

            # Convert value.
            # If the value is 'n', the array is Null and not initialized yet.
            # Same as the ClassInstanceValueGenerator, returns an int value 0.
            if (value in [NULL_REPRESENTATION, 'null', 0]):
                # return PrimitiveValue(value=0, data_type='I')
                return ArrayInstanceValue(value=0, data_type=data_type,
                                          element_data_type=data_type[1:])

            # A string of comma-separated characters cannot be loaded by the json, so implement a loader.
            # A character can be used by conditional instructions, so convert each character to int number
            if (data_type == '[C' and value != '[]'):
                try:
                    value = [ ord(c) for c in value[1:-1].split(', ') ]
                except Exception as e:
                    raise Exception(f'failed to convert {value = }') from e
# Old Implementation
#                 i = 0
#                 string_value = value
#                 value = []
#                 while True:
#                     c = string_value[i]
# 
#                     if (i == 0):
#                         assert c == '['
#                         i += 1
# 
#                     elif (i == len(string_value) - 2):
#                         # This must be the last item
#                         value.append(c)
#                         break
# 
#                     else:
#                         value.append(c)
# 
#                         assert string_value[i+1:i+3] == ', ', f'{string_value[i+1:i+3] = }'
#                         i += 3

            else:
                # Other arrays are logged starting and ending with '[' and ']' and must be json-loadable
                try:
                    value = json.loads(value)
                except json.decoder.JSONDecodeError as e:
                    raise Exception(f'failed with {value = }, {data_type = }') from e

        assert isinstance(value, list), f'value should be a list, {value = }, {data_type = }'

        array = ArrayInstanceValue(value=value, data_type=data_type,
                                   element_data_type=data_type[1:])

        # Initialize array's elements
        # For arrays created by new-array instructions, the arrays are not initialized here but in NewArrayValueResolver
        ArrayInstanceValueGenerator.initialize_array(array)

        return array

    @staticmethod
    def initialize_array(array):
        """
        Add elements to the array.
        """
        for i in range(len(array.value)):
            if (array.value[i] is None):
                # Generate a null value
                array.elements.append(ValueGenerator.generate('I', 0))
                # Replace None with 0
                array.value[i] = 0
            else:
                # Generate a non-null value
                # If the element_data_type is an object, the value, which is hashCode, must be str
                element = ValueGenerator.generate(array.element_data_type, array.value[i])
                # if (isinstance(element, ClassInstanceValue)):
                #     element.value = str(element.value)

                array.elements.append(element)
                array.value[i] = element.value

class ClassInstanceValueGenerator:
    """
    Generate a class instance value for a register.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        value = kwargs['value']
        data_type = kwargs['data_type']
        string = kwargs['string']

        #     # If the data_type is string, and the value is 'null', convert it to a NULL representation
        #     # if (value == 'null'):
        #     #     return PrimitiveValue(value=0, data_type='I')
        #     pass
        # else:
        #     # If the data_type is not a string, and the logged value is 'n' (indicating null), convert it to a NULL representation, which is int value 0
        # If the instruction is new-instance, the value will be None.
        if (value in [NULL_REPRESENTATION, None, 'null', 0]):
            # return PrimitiveValue(value=0, data_type='I')
            return ClassInstanceValue(value=0, data_type=data_type, string=string)

        if (data_type in string_types_identifier_logged and
            string is None and       # Instruction is not const-string
            isinstance(value, str)  # Value can be int if it's an array's element.
            # and value is not None  # Instruction is not new-instance
           ):
            # The string must be logged in the format of <hashCode>:<string>.
            if (value.find(':') > 0):
                string = ':'.join(value.split(':')[1:])
                value = value.split(':')[0]
            else:
                # If the value is a part of an array, the hashCode might not be logged,
                # which is currently a limitation.
                # The identifier is unknown, and use the string as the identifier by
                # just copying the value to the string.
                string = value

        logger.debug(f'{data_type = }')
        logger.debug(f'{value = }')
        # assert value is None or str(value).find(':') < 0, f'{value = } must not have ":"'
        assert str(value).find(':') < 0, f'{value = } must not have ":"'

        # Generate non-null value
        return ClassInstanceValue(value=str(value), data_type=data_type, string=string)

class ClassReferenceValueGenerator:
    """
    Generate a class reference value for a register.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        value = kwargs['value']
        data_type = kwargs['data_type']

        # If the logged value is 'null', convert it to a NULL representation, which is int value 0
        if (value == 'null'):
            # return PrimitiveValue(value=0, data_type='I')
            return ClassReferenceValue(value=0, data_type=data_type)

        if (value in JAVA_TO_SMALI_PRIMITIVE_TYPE_CLASS.keys()):
            # Value represents primitive-data-type, e.g., int.
            # Convert it to smali style.
            value = JAVA_TO_SMALI_PRIMITIVE_TYPE_CLASS[value]
        else:
            if (value == 'void' or
                value.startswith('class ') or
                value.startswith('interface')
               ):
                if (value == 'void'):
                    # Convert it to smali style
                    value = 'Ljava/lang/Void;'
                elif (not value.endswith(';')):
                    # Value is in java style.
                    # Covert it to smali style.
                    prefix = value.split(' ')[0]
                    java_style = value.split(' ')[-1]
                    smali_style = 'L'+java_style.replace('.', '/')+';'
                    value = f'{prefix} {smali_style}'
            else:
                # For some values of Ljava/lang/reflect/Type;
                # Further investigation of "ParameterizedType" is required.
                # Try converting it to smali style.
                # value = 'L'+value.replace('.', '/')+';'
                # logger.error(value)
                pass

        # The prefix can be 'class ' or 'interface ',
        # but currently smalien does not know which, so generate value without the prefix

        value = value.split(' ')[-1]

        return ClassReferenceValue(value=value, data_type=data_type)

value_generator_mapping = {
    'primitive': PrimitiveValueGenerator,
    'array': ArrayInstanceValueGenerator,
    'class': ClassInstanceValueGenerator,
    'reference': ClassReferenceValueGenerator,
}
