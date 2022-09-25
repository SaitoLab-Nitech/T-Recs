import logging
import shutil
import pathlib

from .command_runner import CommandRunner

logger = logging.getLogger(name=__name__)


class ApkHandler:
    """
    This class processes the apk file.
    """

    def __init__(self, apktool='apktool', aapt='aapt'):
        """
        :param apktool:          Command name or path of apktool
        """
        logger.debug('initializing')

        self.apktool = apktool
        self.aapt = aapt

    def configure_keystore(self, kwargs):
        """
        Setup keystore for signing the apk.
        """
        logger.debug('configuring keystore')

        self.keystore = pathlib.Path(kwargs['keystore']).resolve()
        self.storepass = kwargs['storepass']
        self.keypass = kwargs['keypass']
        self.alias = kwargs['alias']

    def unpackage(self, apk, unpackaged, smaliened):
        """
        Extract the apk with apktool.
        """
        logger.debug('unpackaging')

        resource_decoded = True

        # Test if the apk is repackageable with decoding the resources
        try:
            # Unpackage
            self.unpackage_with_decoding_resources(apk, unpackaged)
            # Repackage
            self.package(unpackaged, smaliened)
        except:
            # The apk cannot be repackaged with decoding the resources
            # Therefore, unpackage the apk without decoding the resources
            self.unpackage_without_decoding_resources(apk, unpackaged)

            resource_decoded = False

        logger.error(f'{resource_decoded = }')
        return resource_decoded

    def unpackage_with_decoding_resources(self, apk, unpackaged):
        """
        Perform the unpackaging with decoding the resources.
        """
        cmd = [self.apktool,
               'decode',
               apk,
               # '--only-main-classes',  # Currently disabled because the option's effectiveness is unknown
               '--force',                # Force delete destination dir
               # '--force-manifest',     # Force decode of AndroidManifest.xml
               '--output',
               unpackaged]

        try:
            CommandRunner.run(cmd)
        except Exception as e:
            raise Exception('failed to unpackage') from e

    def unpackage_without_decoding_resources(self, apk, unpackaged):
        """
        Perform the unpackaging without decoding the resources.
        """
        cmd = [self.apktool,
               'decode',
               apk,
               # '--only-main-classes',  # Currently disabled because the option's effectiveness is unknown
               '--no-res',               # Helps to reduce resource-related errors
                                         # (from apktool doc: If only editing Java (smali) then this is recommended for faster decompile & rebuild)
                                         # Cause an installation error (Corrupt XML binary file)
               '--force',                # Force delete destination dir
               # '--force-manifest',     # Force decode of AndroidManifest.xml
               '--output',
               unpackaged]

        try:
            CommandRunner.run(cmd)
        except Exception as e:
            raise Exception('failed to unpackage') from e

    def package_and_sign(self, unpackaged, smaliened, signer):
        """
        Rebuild and sign the apk.
        """
        self.package(unpackaged, smaliened)
        self.sign(smaliened, signer)

    def package(self, unpackaged, smaliened):
        """
        Create an apk with apktool.
        """
        logger.debug('packaging')

        cmd = [self.apktool,
               'build',
               unpackaged,
               '--debug',  # Enable debugging in AndroidManifest.xml
                           # Check by aapt d xmltree <apk> AndroidManifest.xml
               '--output',
               smaliened]

        try:
            CommandRunner.run(cmd)
        except Exception as e:
            raise Exception('failed to package') from e

    def sign(self, smaliened, signer):
        """
        Sign an apk after the packaging.
        """
        logger.debug('signing')

        if (signer == 'apksigner'):
            cmd = [signer,
                   'sign',
                   '--ks',
                   self.keystore,
                   '--ks-pass',
                   'pass:'+self.storepass,
                   smaliened]

        elif (signer == 'jarsigner'):
            cmd = [signer,
                   '-verbose',
                   '-keystore',
                   self.keystore,
                   '-storepass',
                   self.storepass,
                   '-keypass',
                   self.keypass,
                   smaliened,
                   self.alias]

        else:
            raise Exception(f'unsupported {signer = }')

        try:
            CommandRunner.run(cmd)
        except Exception as e:
            # Handle some errors
            if (str(e).find('Use --min-sdk-version to override') > -1):
                logger.debug('retry signing')
                cmd = [signer,
                       'sign',
                       '--min-sdk-version',
                       '14',
                       '--ks',
                       self.keystore,
                       '--ks-pass',
                       'pass:'+self.storepass,
                       smaliened]
                try:
                    CommandRunner.run(cmd)
                except Exception as e:
                    raise Exception('failed to sign with --min-sdk-version') from e

            else:
                raise Exception('failed to sign') from e

    def rm_unpackaged(self, unpackaged):
        """
        Remove the unpackaged directory.
        """
        logger.debug('removing the unpackaged')

        shutil.rmtree(unpackaged, ignore_errors=True)

    def get_package_name(self, apk):
        """
        Get app's package name.
        """
        logger.debug('getting package name')

        cmd = [self.aapt,
               'd',
               'badging',
               apk,
               '|',
               'grep',
               '"package: name="']

        try:
            try:
                data = CommandRunner.run(cmd)
            except Exception as e:
                # Find package name in the error message.
                if (str(e).find("package: name=") > -1):
                    data = str(e)

            return str(data).split("package: name='")[1].split("' ")[0]

        except:
            # If it failed, simply return None to avoid stopping Smalien.
            # The exerciser will detect if the package name is None.
            return None
            # raise Exception('failed to get package name') from e

    def get_components(self, apk, package_name):
        """
        Get names of app's components including activity, service, and broadcast receiver.
        """
        logger.debug('getting component names')

        # If the package name is None, skip this method
        if (package_name is None):
            return [], [], []

        cmd = [self.aapt,
               'dump',
               'xmltree',
               apk,
               'AndroidManifest.xml']

        try:
            data = CommandRunner.run(cmd)
        except Exception as e:
            # If it failed, simply return empty arrays to avoid stopping Smalien.
            return [], [], []
            # raise Exception('failed to get activity names') from e

        components = {
            'service': [],
            'receiver': [],
            'activity': [],
        }
        current_type = ''

        for line in data.decode('utf-8').split('\n'):
            line = line.lstrip()

            if (line.startswith('E: ')):
                # Save current type of components: service, receiver, or activity
                current_type = line.split(' ')[1]

            elif (current_type in ['service', 'receiver', 'activity']):
                if (line.lstrip().startswith('A: android:name') and line.find('"') > -1):
                    name = line.split('"')[1]
                    if (name.startswith(package_name)):
                        components[current_type].append(package_name+'/'+name)
                    elif (name.startswith('.')):
                        components[current_type].append(package_name+'/'+package_name+name)

        logger.debug(f'{components = }')

        return components['service'], components['receiver'], components['activity']
