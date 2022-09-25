import logging

logger = logging.getLogger(name=__name__)


class JavaToSmaliConverter:
    """
    This class converts java-style class and method names to smali-style.
    """

    @staticmethod
    def convert(java_style_name):
        """
        Run the conversion.
        """
        logger.debug(f'converting {java_style_name = }')

        assert java_style_name is not None, 'failed to obtain java_style_name'

        try:
            class_method_name = java_style_name.split(' ')[-1]
            return_data_type = java_style_name.split(' ')[-2]
        except IndexError as e:
            raise Exception(f'failed to convert {java_style_name = }') from e

        logger.debug(f'{class_method_name = }')
        logger.debug(f'{return_data_type = }')

        # Disassembly class_method_name
        class_name = '.'.join(class_method_name.split('(')[0].split('.')[:-1])
        method_name = class_method_name.split('(')[0].split('.')[-1]
        arguments = class_method_name.split('(')[-1][:-1]

        # Transform java-style to smali-style
        class_name = JavaToSmaliConverter.transform_data_type(class_name)
        arguments_in_smali = ''
        for argument in arguments.split(','):
            arguments_in_smali += JavaToSmaliConverter.transform_data_type(argument)

        return_data_type = JavaToSmaliConverter.transform_data_type(return_data_type)

        # Assembly method_name
        method_name = f'{method_name}({arguments_in_smali}){return_data_type}'

        logger.debug(f'{class_name = }')
        logger.debug(f'{method_name = }')

        return class_name, method_name

    @staticmethod
    def convert_field(java_style_name):
        """
        Run the conversion for field name.
        """
        logger.debug(f'converting {java_style_name = }')

        assert java_style_name is not None, 'failed to obtain java_style_name'

        try:
            class_name = '.'.join(java_style_name.split(' ')[-1].split('.')[:-1])
            field_name = java_style_name.split('.')[-1]
            data_type = java_style_name.split(' ')[-2]
        except IndexError as e:
            raise Exception(f'failed to convert {java_style_name = }') from e

        # Currently, only static fields are supported
        assert java_style_name.find('static') > -1

        logger.debug(f'{class_name = }')
        logger.debug(f'{field_name = }')
        logger.debug(f'{data_type = }')

        # Transform java-style to smali-style
        class_name = JavaToSmaliConverter.transform_data_type(class_name)
        data_type = JavaToSmaliConverter.transform_data_type(data_type)

        # Assembly field name
        field_name = f'{class_name}->{field_name}:{data_type}'

        logger.debug(f'{field_name = }')

        return 'static', field_name

    @staticmethod
    def transform_data_type(java_style_name):
        """
        Transform a data type of java-style to smali_style.
        """

        array_indicators, java_style_name = JavaToSmaliConverter.transform_array_incidators(java_style_name)

        match java_style_name:
            case '': return ''
            case 'void': return 'V'
            case 'boolean': return array_indicators+'Z'
            case 'byte': return array_indicators+'B'
            case 'char': return array_indicators+'C'
            case 'short': return array_indicators+'S'
            case 'int': return array_indicators+'I'
            case 'float': return array_indicators+'F'
            case 'double': return array_indicators+'D'
            case 'long': return array_indicators+'J'
            case _: return array_indicators+'L'+java_style_name.replace('.', '/')+';'

    @staticmethod
    def transform_array_incidators(java_style_name):
        result = ''
        while java_style_name.endswith('[]'):
            result += '['
            java_style_name = java_style_name[:-2]
        return result, java_style_name
