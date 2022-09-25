import logging

from .structures import *
from .opcode_parser_utils import Utils

logger = logging.getLogger(name=__name__)


class OpIgetParser:
    """
    Parse iget instructions.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']

        instruction = Utils.get_instruction(line)
        destination = Utils.get_first(line)
        source = Utils.get_second(line)

        third_arg = Utils.get_last(line)
        source_data_type = third_arg.split('->')[0]
        field = third_arg.split('->')[1]
        destination_data_type = field.split(':')[1]

        found, default_value = Utils.search_field_in_app(source_data_type, field, 'instance', kwargs['classes'])
        if (found):
            in_app = True
            # Update the class name
            # In Reflection.Reflection2, this is necessary to track the flow.
            third_arg = f'{found}->{field}'
        else:
            in_app = False

        return OpIget(num=kwargs['num'], instruction=instruction,
                      source=source, source_data_type=source_data_type,
                      destination=destination, destination_data_type=destination_data_type,
                      field=third_arg, in_app=in_app)
                      # field=field, in_app=in_app)

class OpIputParser:
    """
    Parse iput instructions.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']

        instruction = Utils.get_instruction(line)
        source = Utils.get_first(line)
        destination = Utils.get_second(line)

        third_arg = Utils.get_last(line)
        destination_data_type = third_arg.split('->')[0]
        field = third_arg.split('->')[1]
        source_data_type = field.split(':')[1]

        found, default_value = Utils.search_field_in_app(destination_data_type, field, 'instance', kwargs['classes'])
        if (found):
            # Currently, in_app flag is not used.
            # in_app = True
            # Update the class name
            third_arg = f'{found}->{field}'
        else:
            # Currently, in_app flag is not used.
            # in_app = False
            pass

        return OpIput(num=kwargs['num'], instruction=instruction,
                      source=source, source_data_type=source_data_type,
                      destination=destination, destination_data_type=destination_data_type,
                      field=third_arg)
                      # field=field)

class OpSgetParser:
    """
    Parse sget instructions.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        num = kwargs['num']
        line = kwargs['line']
        classes = kwargs['classes']

        instruction = Utils.get_instruction(line)
        destination = Utils.get_first(line)

        last_arg = Utils.get_last(line)
        destination_data_type = last_arg.split(':')[1]

        # Detect in-app field
        class_name = last_arg.split('->')[0]
        field = last_arg.split('->')[1]

        found, default_value = Utils.search_field_in_app(class_name, field, 'static', classes)
        if (found):
            in_app = True
            # Update the class name
            last_arg = f'{found}->{field}'
            # Get whether clinit is implemented
            clinit_implemented = classes[found].clinit_implemented
        else:
            in_app = False
            clinit_implemented = False

        # Convert default_value
        if (default_value is not None):
            # Keep it as a string, and it will be converted to the data type in the emulation
            try:
                default_value = str(Utils.convert_static_field_default_value(default_value))
            except Exception as e:
                raise Exception(f'failed to get static field {default_value = } at {num = } {line = }') from e

        return OpSget(num=num, instruction=instruction,
                      destination=destination, destination_data_type=destination_data_type,
                      class_name=class_name, default_value=default_value,
                      field=last_arg, in_app=in_app, clinit_implemented=clinit_implemented)

class OpSputParser:
    """
    Parse sput instructions.
    """
    @staticmethod
    def run(**kwargs):
        """
        Execute the parser.
        """
        logger.debug('running')

        line = kwargs['line']

        instruction = Utils.get_instruction(line)
        source = Utils.get_first(line)

        last_arg = Utils.get_last(line)
        source_data_type = last_arg.split(':')[1]

        # Detect in-app field
        class_name = last_arg.split('->')[0]
        field = last_arg.split('->')[1]

        found, default_value = Utils.search_field_in_app(class_name, field, 'static', kwargs['classes'])
        if (found):
            in_app = True
            # Update the field name
            last_arg = f'{found}->{field}'
        else:
            in_app = False

        return OpSput(num=kwargs['num'], instruction=instruction,
                      source=source, source_data_type=source_data_type,
                      class_name=class_name,
                      field=last_arg, in_app=in_app)
