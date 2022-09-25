import logging
# from androguard.core.bytecodes.axml import AXMLPrinter

from ..generator.payload.structures import PayloadLocals, PayloadMove, PayloadMoveResult, PayloadMoveException, PayloadGoto, PayloadGotoExtra, PayloadGotoLabel, PayloadGotoLabelExtra, PayloadCondLabel, PayloadLogging, PayloadDummyReturnedValue
from .definitions import PERMISSION_WRITE_EXTERNAL_STORAGE_FOR_ENCODED_XML, PERMISSION_WRITE_EXTERNAL_STORAGE_FOR_DECODED_XML, SMALIEN_CLASS_HEADER_TEMPLATE, SMALIEN_WRITER_SMALI_NAME, SMALIEN_WRITER_CLASS_NAME, SMALIEN_WRITER
from .definitions_of_to_string_converters import TO_STRING_CONVERTERS
from smalien.data_types import DATA_TYPES_IMPLEMENTED_INDIVIDUAL_CONVERTER
from smalien.utils.command_runner import CommandRunner

logger = logging.getLogger(name=__name__)


class Injector:
    """
    Inject the generated code into smali files of the app.
    """

    def __init__(self, app, log_buff_size, multi_dex, use_shared_converter, converter_keys, xml2axml='xml2axml'):
        logger.debug('initializing')

        self.app = app
        self.smalien_writer = SMALIEN_WRITER.replace(
            'LOG_BUFF_SIZE', str(hex(log_buff_size))
        ).replace(
            'LOG_PATH', app.smalien_log)

        self.use_shared_converter = use_shared_converter
        self.converter_keys = converter_keys
        self.xml2axml = xml2axml

        # Set destination directory of smalien logging class
        if (multi_dex):
            self.app.smalien_dex_id = self.get_unused_dex_id()
        else:
            self.app.smalien_dex_id = self.app.dex_ids.pop()
        self.smalien_dir = app.unpackaged / self.app.smalien_dex_id

    def get_unused_dex_id(self):
        """
        Return unused dex id.
        """
        largest = 1
        for dex_id in self.app.dex_ids:
            if (dex_id != 'smali'):
                num = int(dex_id.replace('smali_classes', ''))
                if (largest < num):
                    largest = num

        return f'smali_classes{largest+1}'

    def run(self):
        """
        Execute the injector.
        """
        logger.debug('running')

        # Add WRITE_EXTERNAL_STORAGE permission to AndroidManifest.xml
        if (self.app.resource_decoded):
            self.inject_permission_to_decoded_xml(PERMISSION_WRITE_EXTERNAL_STORAGE_FOR_DECODED_XML)

            self.remove_extractNativeLibs_from_decoded_xml()

        else:
            # (currently disabled) The extractNativelibs is also removed by the method
            self.inject_permission_to_encoded_xml(PERMISSION_WRITE_EXTERNAL_STORAGE_FOR_ENCODED_XML)

        # Create a smali file containing SmalienWriter and to-string converters
        self.inject_smalien_writer()

        for class_data in self.app.classes.values():
            # Inject payload for each class, and update its reference number
            class_data.reference_num += self.inject_payload_for_a_class(class_data.payloads, class_data.path,
                                                                        class_data.linage, class_data.code)

    def inject_permission_to_decoded_xml(self, permission):
        """
        Add a uses-permission sentence to decoded AndroidManifest.xml
        """
        logger.debug('injecting the permission to decoded AndroidManifest.xml')

        with open(self.app.android_manifest, 'r') as f:
            data = f.read()
            if (data.find(permission) > -1):
                return
        with open(self.app.android_manifest, 'w') as f:
            data = data.split('\n')
            output = data[0]+'\n'+permission+'\n'+'\n'.join(data[1:])
            f.write(output)

    def remove_extractNativeLibs_from_decoded_xml(self):
        """
        Remove extractNativeLibs from decoded AndroidManifest.xml
        """
        logger.debug('Removing extractNativeLibs from decoded AndroidManifest.xml')

        with open(self.app.android_manifest, 'r') as f:
            data = f.read()

        data = data.replace('android:extractNativeLibs="false" ', '')

        with open(self.app.android_manifest, 'w') as f:
            f.write(data)

    def inject_permission_to_encoded_xml(self, permission):
        """
        Add a uses-permission sentence to encoded AndroidManifest.xml
        """
        logger.debug('injecting the permission to encoded AndroidManifest.xml')

        decoded = self.app.unpackaged.parent / self.app.android_manifest.name

        # Decode binary AndroidManifest.xml
        cmd = [self.xml2axml,
               'd',
               self.app.android_manifest,
               decoded]
        try:
            CommandRunner.run(cmd)
        except Exception as e:
            raise Exception('failed to decode AndroidManifest.xml') from e

        with open(decoded, 'r') as f:
            data = f.read()

        # Remove extractNativeLibs
        # Currently disable this because it decreases the install success rate
        # data = data.replace('android:extractNativeLibs="false"', '')

        # Add the permission
        with open(decoded, 'w') as f:
            # Check whether the permission is defined
            if (data.find(permission) > -1):
                logger.debug('the permission is already defined')
                # output = data
                # Currently, removing extractNativeLibs is disabled,
                # and do nothing if editing the manifest is not necessary.
                return
            else:
                data = data.split('\n')
                for i, line in enumerate(data):
                    if (line.startswith('\t>')):
                        # The line must the end of <manifest>
                        break
                output = '\n'.join(data[:i+1])
                output += '\n\t<uses-permission\n'
                output += f'\t\t{permission}\n'
                output += '\t\t>\n'
                output += '\t</uses-permission>\n'
                output += '\n'.join(data[i+1:])

            f.write(output)

        # Encode plane AndroidManifest.xml
        cmd = [self.xml2axml,
               'e',
               decoded,
               self.app.android_manifest]
        try:
            CommandRunner.run(cmd)
        except Exception as e:
            raise Exception('failed to encode AndroidManifest.xml') from e

        # Stopped using androguard because it cannot encode plane xml to binary axml
        # with open(self.app.android_manifest, 'rb') as f:
        #     data = AXMLPrinter(f.read()).get_xml().decode('utf-8')
        #     if (data.find(permission) > -1):
        #         return
        # with open(self.app.android_manifest, 'wb') as f:
        #     data = data.split('\n')
        #     output = data[0]+'\n  '+permission+'\n'+'\n'.join(data[1:])
        #     output = output.encode('utf-8')
        #     f.write(output)

    def inject_smalien_writer(self):
        """
        Inject the SmalienWriter and shared converters.
        """
        # logger.error(len(self.converter_keys))
        # logger.error(self.converter_keys)
        # Inject converters
        for converter_key in self.converter_keys:

            # Skip if the key is specified to use individual converter
            if (self.use_shared_converter and
                converter_key not in DATA_TYPES_IMPLEMENTED_INDIVIDUAL_CONVERTER):
                self.smalien_writer += TO_STRING_CONVERTERS[converter_key]

        # Write to file
        self.inject_definition(SMALIEN_WRITER_SMALI_NAME, SMALIEN_WRITER_CLASS_NAME,
                               self.smalien_writer)

    def inject_payload_for_a_class(self, payloads, path, linage, code):
        """
        Inject the payload for one class.
        """
        output = ''
        reference_num = 0

        for i in range(linage):
            keep_original = True

            if (i in payloads.keys()):

                for payload in payloads[i]:
                    match payload:
                        case PayloadLogging():
                            # Inject the invoke
                            output += payload.invoke + '\n'
                            # Increment the reference number
                            reference_num += 1

                            # Inject the definition
                            self.inject_definition(payload.smali_name,
                                                   payload.class_name,
                                                   payload.definition)

                        case PayloadMove():
                            # Inject the code
                            output += payload.code + '\n'

                        case PayloadDummyReturnedValue():
                            # Inject the code
                            output += payload.code + '\n'

                        case PayloadGotoExtra() | PayloadGotoLabelExtra() | PayloadCondLabel():
                            # Inject the code
                            output += payload.code + '\n'

                        case PayloadLocals() | PayloadMoveResult() | PayloadMoveException() | PayloadGoto() | PayloadGotoLabel():
                            # Inject the code
                            output += payload.code + '\n'
                            # Set the flag to replace the original
                            keep_original = False

                        case _:
                            raise Exception(f'unsupported payload type {payload = }')

            if (keep_original):
                output += code[i] + '\n'

        with open(path, 'w') as f:
            f.write(output)

        return reference_num

    def inject_definition(self, smali_name, class_name, definition):
        """
        Inject the definition code of smalien methods.
        """
        path = self.smalien_dir / smali_name
        if (not path.parent.exists()):
            # Create a dex directory
            path.parent.mkdir()
        if (not path.exists()):
            # Create a smali file
            self.write_smalien_class_header(path, class_name)

        with open(path, 'a') as f:
            f.write(definition)

    def write_smalien_class_header(self, path, class_name):
        with open(path, 'w') as f:
            f.write(SMALIEN_CLASS_HEADER_TEMPLATE.format(class_name))
