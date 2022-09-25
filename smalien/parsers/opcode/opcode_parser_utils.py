import logging
import struct
import numpy

from smalien.data_types import NULL_REPRESENTATION

logger = logging.getLogger(name=__name__)


class Utils:
    """
    Uitlity class for Op*Parsers.
    """

    @staticmethod
    def get_instruction(line):
        """
        Extract an instruction from a line.
        Return an empty string if an instruction is not found.
        """
        if (len(line) > 0):
            return line.split()[0]
        return ''

    @staticmethod
    def get_first(line):
        """
        Extract the first argument.
        """
        reg = line.split()[1]
        assert reg.endswith(','), f'Failed to get the first argument for {line = }'

        return reg[:-1]

    @staticmethod
    def get_second(line):
        """
        Extract the second argument.
        """
        reg = line.split()[2]
        assert reg.endswith(','), f'Failed to get the first argument for {line = }'

        return reg[:-1]

    @staticmethod
    def get_last(line):
        """
        Extract the last argument.
        """
        return line.split()[-1]

    @staticmethod
    def get_latter_half(reg, line):
        """
        Extract the latter half splitted by the given register.
        """
        delimiter = f' {reg}, '
        return delimiter.join(line.split(delimiter)[1:])

    @staticmethod
    def get_method_style_argument_vars(line):
        """
        Extract the method style argument varriables (i.e., variables within {}).
        """

        # E.g., '{v0, v1},' -> 'v0, v1'
        args_str = line[line.find('{')+1:line.find('}')]

        # Transform string to list
        if (args_str.find(' .. ') > -1):
            prefix = args_str.split(' ')[0][0]
            start = int(args_str.split(' ')[0][1:])
            end = int(args_str.split(' ')[-1][1:]) + 1
            return [ prefix + str(i) for i in range(start, end) ]
        elif (len(args_str) > 0):
            return args_str.split(', ')
        return []

    @staticmethod
    def search_field_in_app(cname, field, field_kind, classes):
        """
        Check if the field is implemented within the app.
        Return found class name and default value.
        """
        cdata = classes.get(cname, None)
        if (cdata is not None and not cdata.ignore):
            if (field in cdata.fields[field_kind].keys()):
                return cname, cdata.fields[field_kind][field].default_value
            else:
                for member in cdata.family:
                    mem_data = classes.get(member, None)
                    if (mem_data is not None and not mem_data.ignore and field in mem_data.fields[field_kind].keys()):
                        return member, mem_data.fields[field_kind][field].default_value

        return False, None

    @staticmethod
    def extract_constant_value(reg, line, instruction):
        """
        Extract a literal value from the const instruction.
        """
        val = Utils.get_latter_half(reg, line)
        if (instruction in ['const', 'const/high16']):
            # Instruction specific conversion
            # IEEE binary representation
            # Remove a comment following the value
            # val = val.split('#')[0].rstrip()
            # return struct.unpack('>f', int(val, 16).to_bytes(4, byteorder='big', signed=True))[0]

            # The conversion depends on the data type.
            # Currently, use a comment (e.g. # 0.75f) to create a value.
            if (val.find(' # ') > 0):
                if (val.split(' # ')[-1] in ['Float.NaN', 'Float.POSITIVE_INFINITY', 'Float.NEGATIVE_INFINITY', 'Float.MAX_VALUE', '(float)Math.PI', '(float)Math.E']):
                    # Generate one of the special values
                    val = val.split('#')[0].rstrip()
                    return struct.unpack('>f', int(val, 16).to_bytes(4, byteorder='big', signed=True))[0]
                else:
                    # Use the comment
                    return float(val.split(' # ')[-1][:-1])
            else:
                # Simply convert the hex string to integer
                # Remove a comment following the value
                val = val.split('#')[0].rstrip()
                return int(val, 16)

        if (val.startswith('"') and val.endswith('"')):
            # Value is a string
            # Remove quotation marks before and after the value
            return val[1:-1]
        elif (val.startswith('0x') or val.startswith('-0x')):
            # Value is a hex string and primitive-data-type
            return Utils.convert_hex_string_of_primitive_data(val)
        else:
            # Value is unknown
            raise Exception(f'unknown constant is found, {line = }, {val = }')

    @staticmethod
    def convert_static_field_default_value(val):
        """
        Convert a smali-hard-coded value of static fields.
        Compatibility with the ValueGenerator must be provided.
        """
        if (val.startswith('"') and val.endswith('"')):
            # Value is a string
            # Remove quotation marks before and after the value
            return val[1:-1]
        elif (val == 'null'):
            # Value is not a string and is null
            return NULL_REPRESENTATION
        elif (val in ['true', 'false']):
            # Value is boolean, and returns as it is
            return val
        elif (val.startswith("'\\u")):
            # Value is character, e.g. '\u0000'
            return chr(int(val[3:-1], 16))
        elif (val.startswith('0x') or val.startswith('-0x')):
            # Value is a hex string and primitive-data-type
            return Utils.convert_hex_string_of_primitive_data(val)
        elif (val.endswith('f')):
            return float(val[:-1])
        elif (len(val) == 3 and
              val[0] == "'" and
              val[2] == "'"
             ):
            # Value is a character, e.g., 'X'
            return ord(val[1])
        else:
            # Try to convert the value to int number
            try:
                # Converting a large number, such as -5165993188905959888, to float can lose precision.
                # So, first, check if the value is integer.
                if (str(val).find('.') < 0):
                    try:
                        return int(val)
                    except (OverflowError, ValueError):
                        # Value is either float infinity or float NaN
                        return float(val)
                else:
                    return float(val)

                # Old implementation failed in many apps from Google Play
                #   e.g., value = 4.9E-324
                # float_value = float(val)
                # int_value = int(float_value)
                # assert float_value == int_value
                # return int_value

            except Exception as e:
                # Value is unknown
                raise Exception(f'found an unknown value {val = }') from e

    @staticmethod
    def convert_hex_string_of_primitive_data(value_with_comment):
        """
        Convert the given hex string of primitive-data-type value to raw value.
        """
        # Remove a comment following the value
        val = value_with_comment.split('#')[0].rstrip()

        # First, try to use the comment
        if (value_with_comment.find('#') > -1):
            if (val.endswith('L')):
                # Value is in hex and IEEE binary64 formats
                # Convert it to a decimal integer
                return struct.unpack('>d', int(val[:-1], 16).to_bytes(8,
                                                                      byteorder='big',
                                                                      signed=True))[0]
            else:
                # Value is 32 bit float
                return numpy.float32(struct.unpack('>f', int(val, 16).to_bytes(4,
                                                                               byteorder='big',
                                                                               signed=True))[0])
        # Decide converter based on the last character of the value
        elif (val.endswith('L')):
            return int(val[:-1], 16)
        elif (val.endswith('t')):
            # Value is a byte
            # return chr(int(val[:-1], 16))
            return int(val[:-1], 16)
        elif (val.endswith('s')):
            # Value is a character
            # Convert it to a decimal integer
            return int(val[:-1], 16)
        else:
            # Value is in hex format
            # Convert it to a decimal integer
            return int(val, 16)

    # Translate data type in java style to smali style
    java_to_smali_data_type_styles_mapping = {
        'byte': 'B',
        'short': 'S',
        'char': 'C',
        'int': 'I',
        'long': 'J',
        'float': 'F',
        'double': 'D',
    }

    """
    Translate instruction's prefix to expression.
    Currently used by unary and binary opcode parsers.
    Expressions are used for calculation at the emulation.
    Expressions are represented by a string instead of a function,
    because expressions are going to be saved into a file,
    and we don't want to save functions.
    """
    unop_and_binop_expression_mapping = {
        # unop vA, vB
        # Negation
        'neg-int': '-source',
        'not-int': '~source',
        'neg-long': '-source',
        'not-long': '~source',
        'neg-float': '-source',
        'neg-double': '-source',
        # Data type conversion
        # TODO: Update these conversions
        'int-to-long':     'source',
        'int-to-float':    'source',
        'int-to-double':   'source',
        'long-to-int':     'source & 0xFFFFFFFF',
        'long-to-float':   'source',
        'long-to-double':  'source',
        'float-to-int':    'int(source) if (source == source) else 0',  # If source == nan, return 0
        'float-to-long':   'int(source) if (source == source) else 0',  # If source == nan, return 0
        'float-to-double': 'source',
        'double-to-int':   'int(source) if (source == source) else 0',  # If source == nan, return 0
        'double-to-long':  'int(source) if (source == source) else 0',  # If source == nan, return 0
        'double-to-float': 'source',
        'int-to-byte':     '(source << 24) >> 24',
        'int-to-char':     'source & 0xffff',
        'int-to-short':    '(source << 16) >> 16',

        # binop vAA, vBB, vCC
        # int
        'add-int': 'int(source1 + source2)',
        'sub-int': 'int(source1 - source2)',
        'mul-int': 'int(source1 * source2)',
        'div-int': 'int(source1 / source2)',
        'rem-int': 'int(source1 % source2)',
        'and-int': 'int(source1 & source2)',
        'or-int':  'int(source1 | source2)',
        'xor-int': 'int(source1 ^ source2)',
        'shl-int': 'int(source1 << source2)',
        'shr-int': 'int(source1 >> source2)',
        # Python does not have bitwise unsigned shift right operation
        # Hence, source1 is converted to 32-bit unsigned value and then shifted
        # TODO: Test if this works
        'ushr-int': 'int((source1 & 0xffffffff) >> (source2 & 0x1f))',
        # long
        'add-long': 'int(source1 + source2)',
        'sub-long': 'int(source1 - source2)',
        'mul-long': 'int(source1 * source2)',
        'div-long': 'int(source1 / source2)',
        'rem-long': 'int(source1 % source2)',
        'and-long': 'int(source1 & source2)',
        'or-long':  'int(source1 | source2)',
        'xor-long': 'int(source1 ^ source2)',
        'shl-long': 'int(source1 << (source2 & 0x3f))',
        'shr-long': 'int(source1 >> (source2 & 0x3f))',
        # Python does not have bitwise unsigned shift right operation
        # Hence, source1 is converted to 64-bit unsigned value and then shifted
        # TODO: Test if this works
        'ushr-long': 'int((source1 & 0xffffffffffffffff) >> (source2 & 0x3f))',
        # float
        'add-float': 'source1 + source2',
        'sub-float': 'source1 - source2',
        'mul-float': 'source1 * source2',
        'div-float': 'source1 / source2',
        'rem-float': 'source1 % source2',
        # double
        'add-double': 'source1 + source2',
        'sub-double': 'source1 - source2',
        'mul-double': 'source1 * source2',
        'div-double': 'source1 / source2',
        'rem-double': 'source1 % source2',

        # binop/2addr vA, vB
        # int
        'add-int/2addr': 'int(source1 + source2)',
        'sub-int/2addr': 'int(source1 - source2)',
        'mul-int/2addr': 'int(source1 * source2)',
        'div-int/2addr': 'int(source1 / source2)',
        'rem-int/2addr': 'int(source1 % source2)',
        'and-int/2addr': 'int(source1 & source2)',
        'or-int/2addr':  'int(source1 | source2)',
        'xor-int/2addr': 'int(source1 ^ source2)',
        'shl-int/2addr': 'int(source1 << source2)',
        'shr-int/2addr': 'int(source1 >> source2)',
        # Python does not have bitwise unsigned shift right operation
        # Hence, source1 is converted to 32-bit unsigned value and then shifted
        # TODO: Test if this works
        'ushr-int/2addr': 'int((source1 & 0xffffffff) >> (source2 & 0x1f))',
        # long
        'add-long/2addr': 'int(source1 + source2)',
        'sub-long/2addr': 'int(source1 - source2)',
        'mul-long/2addr': 'int(source1 * source2)',
        'div-long/2addr': 'int(source1 / source2)',
        'rem-long/2addr': 'int(source1 % source2)',
        'and-long/2addr': 'int(source1 & source2)',
        'or-long/2addr':  'int(source1 | source2)',
        'xor-long/2addr': 'int(source1 ^ source2)',
        'shl-long/2addr': 'int(source1 << (source2 & 0x3f))',
        'shr-long/2addr': 'int(source1 >> (source2 & 0x3f))',
        # Python does not have bitwise unsigned shift right operation
        # Hence, source1 is converted to 64-bit unsigned value and then shifted
        # TODO: Test if this works
        'ushr-long/2addr': 'int((source1 & 0xffffffffffffffff) >> (source2 & 0x3f))',
        # float
        'add-float/2addr': 'source1 + source2',
        'sub-float/2addr': 'source1 - source2',
        'mul-float/2addr': 'source1 * source2',
        'div-float/2addr': 'source1 / source2',
        'rem-float/2addr': 'source1 % source2',
        # double
        'add-double/2addr': 'source1 + source2',
        'sub-double/2addr': 'source1 - source2',
        'mul-double/2addr': 'source1 * source2',
        'div-double/2addr': 'source1 / source2',
        'rem-double/2addr': 'source1 % source2',

        # binop/lit16 vA, vB, #+CCCC
        'add-int/lit16': 'int(source1 + source2)',
        'rsub-int':      'int(source2 - source1)',
        'mul-int/lit16': 'int(source1 * source2)',
        'div-int/lit16': 'int(source1 / source2)',
        'rem-int/lit16': 'int(source1 % source2)',
        'and-int/lit16': 'int(source1 & source2)',
        'or-int/lit16':  'int(source1 | source2)',
        'xor-int/lit16': 'int(source1 ^ source2)',

        # binop/lit8 vAA, vBB, #+CC
        'add-int/lit8':  'int(source1 + source2)',
        'rsub-int/lit8': 'int(source2 - source1)',
        'mul-int/lit8':  'int(source1 * source2)',
        'div-int/lit8':  'int(source1 / source2)',
        'rem-int/lit8':  'int(source1 % source2)',
        'and-int/lit8':  'int(source1 & source2)',
        'or-int/lit8':   'int(source1 | source2)',
        'xor-int/lit8':  'int(source1 ^ source2)',
        'shl-int/lit8':  'int(source1 << (source2 & 0x1f))',
        'shr-int/lit8':  'int(source1 >> (source2 & 0x1f))',
        # Python does not have bitwise unsigned shift right operation
        # Hence, source1 is converted to 32-bit unsigned value and then shifted
        # TODO: Test if this works
        'ushr-int/lit8': 'int((source1 & 0xffffffff) >> (source2 & 0x1f))',
    }
