
# TODO: Make these names capitalized

primitive_data_types = ['Z', 'B', 'S', 'C', 'I', 'J', 'F', 'D']

numeric_types_integer = ['S', 'I', 'J']
numeric_types_floating_point = ['F', 'D']
boolean_type = ['Z']
character_type = ['C']
byte_type = ['B']

numeric_types_64 = ['J', 'D']

string_types = [
    'Ljava/lang/String;',
    'Ljava/lang/reflect/Method;',
    'Ljava/lang/reflect/Field;',
    'Ljava/lang/CharSequence;',
    #'Ljava/lang/Class;',
    # 'Ljava/lang/reflect/Type;',
]
string_types_identifier_logged = [
    'Ljava/lang/String;',
    'Ljava/lang/CharSequence;',
]
string_types_array = [
    '[Ljava/lang/reflect/Method;',
    '[[Ljava/lang/String;',
    #'[Ljava/lang/Class;',
    #'[Ljava/lang/reflect/Type;',
]

CHECK_CAST_TARGET = []#'Ljava/lang/Class;']

NULL_REPRESENTATION = 'n'

JAVA_TO_SMALI_PRIMITIVE_TYPE_CLASS = {
    'boolean': 'Ljava/lang/Boolean;',
    'byte': 'Ljava/lang/Byte;',
    'short': 'Ljava/lang/Short;',
    'char': 'Ljava/lang/Character;',
    'int': 'Ljava/lang/Integer;',
    'long': 'Ljava/lang/Long;',
    'float': 'Ljava/lang/Float;',
    'double': 'Ljava/lang/Double;',
}

# DATA_TYPES_IMPLEMENTED_INDIVIDUAL_CONVERTER = []
DATA_TYPES_IMPLEMENTED_INDIVIDUAL_CONVERTER = [
    # Primitive data types
    'Z', 'B', 'S', 'C', 'I', 'J', 'F', 'D',
    # Arrays of primitive data types
    '[Z', '[B', '[S', '[C', '[I', '[J', '[F', '[D',
    # Classes
    'Ljava/lang/reflect/Method;',
    'Ljava/lang/Class;',
    'Ljava/lang/reflect/Type;',
    'Ljava/lang/Object;-WITH_NULL_CHECK',
    'Ljava/lang/Object;-WITHOUT_NULL_CHECK',
]
