import logging

from ..structures import AppField

logger = logging.getLogger(name=__name__)


class FieldParser:
    """
    Parse app fields in smali files.
    """

    def __init__(self, linage, code, fields):
        logger.debug('initializing')

        self.linage = linage
        self.code = code
        self.fields = fields

        self.fields['static'] = {}
        self.fields['instance'] = {}

    def run(self):
        """
        Execute the parser for finding fields in a class.
        """
        logger.debug('running')

        i = 0
        while i < self.linage:
            line = self.code[i]

            if (line.startswith('.field')):
                field_name = line.split(':')[0].split(' ')[-1]
                field_data_type = line.split(':')[1].split(' ')[0]

                field_key = f'{field_name}:{field_data_type}'

                field_kind = 'static' if (line.find(' static ') > -1) else 'instance'

                default_value = ' = '.join(line.split(' = ')[1:]) if (line.find(' = ') > -1) else None

                # Register the field
                self.fields[field_kind][field_key] = AppField(key=field_key,
                                                              name=field_name,
                                                              data_type=field_data_type,
                                                              default_value=default_value)

            # Assuming no field is defined after method definitions
            if (line.startswith('.method')):
                break

            i += 1
