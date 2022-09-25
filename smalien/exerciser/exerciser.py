import logging
import copy
import time
import itertools
from xml.etree import ElementTree
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process

from ..utils.command_runner import CommandRunner

logger = logging.getLogger(name=__name__)


def mitmdump_recorder(params):
    """
    Read mitmdump's output and write it to file with timestamp.
    """
    logger.debug('starting mitmdump recorder thread')

    process = params[0]
    mitmdump_log = params[1]

    with open(mitmdump_log, 'w') as f:
        for line in iter(process.stdout.readline, b''):
            try:
                line = line.rstrip().decode('utf-8')
            except:
                continue

            if (not line.startswith(' ') and line != ''):
                line = f'{time.time()} {line}'

            line += '\n'

            f.write(line)

class Exerciser:
    """
    This module exercises the app and obtains runtime data.
    """

    def __init__(self, app, workspace, device):
        logger.debug('initializing')

        # Setup paths
        self.workspace = workspace
        self.device = device
        self.package = app.package
        self.original = str(app.apk)
        self.smaliened = str(app.smaliened)
        self.smalien_log = app.smalien_log
        self.smalien_log_local = app.smalien_log_local

        # Logcat
        self.logcat_log = app.logcat_log
        self.logcat_process = None

        # mitmdump and ts
        self.mitmdump_log = app.logcat_log.parent / 'mitmdump.log'
        self.mitmdump_process = None
        self.mitmdump_recorder_pool = None

        # Setup ADB command
        self.adb = ['adb']
        if (self.device is not None):
            self.adb.extend([
                '-s',
                self.device])
        logger.debug(f'{self.adb = }')

        # Installation timeout (seconds)
        self.installation_timeout = 1200  # 20 minutes

    def sleep(self, seconds):
        """
        Sleep for <seconds> seconds
        """
        logger.debug(f'sleeping for {seconds = }')
        time.sleep(seconds)

    def clear(self):
        """
        Clear previously saved smalien logs.
        """
        logger.debug(f'clearing {self.smalien_log} on {self.device}')

        # Create a command
        cmd = copy.copy(self.adb)
        cmd.extend([
            'shell',
            'rm',
            self.smalien_log])

        # Run the command
        try:
            CommandRunner.run(cmd)
        except Exception as e:
            logger.debug(f'{e = }')

    def clear_app_data(self):
        """
        Clear the app's previously-saved data.
        """
        logger.debug(f'clearing app data on {self.device}')

        assert self.package is not None

        # Create a command
        cmd = copy.copy(self.adb)
        cmd.extend([
            'shell',
            'pm',
            'clear',
            self.package])

        # Run the command
        try:
            CommandRunner.run(cmd)
        except Exception as e:
            logger.debug(f'{e = }')

    def clean_storage(self):
        """
        Clean all files on external storage.
        """
        logger.debug(f'cleaning files in /sdcard/* of {self.device}')

        # Create a command
        cmd = copy.copy(self.adb)
        cmd.extend([
            'shell',
            'rm',
            '-rf',
            '/sdcard/*',
            'sdcard/.*'])

        # Run the command
        try:
            CommandRunner.run(cmd)
        except Exception as e:
            logger.debug(f'{e = }')

    def reboot(self, seconds=0):
        """
        Reboot the device.

        :param seconds:  Smalien sleeps for <seconds> after the device reboot command.
        """
        logger.debug(f'Rebooting {self.device = }')

        # Create a command
        cmd = copy.copy(self.adb)
        cmd.extend([
            'reboot'])

        # Run the command
        try:
            CommandRunner.run(cmd)
        except Exception as e:
            raise Exception('failed to reboot') from e

        # Sleep
        self.sleep(seconds)

    def install(self, seconds=0):
        """
        Install the app to the device.

        :param seconds:     smalien stops for <seconds> after the installation.
        """
        logger.debug(f'installing {self.smaliened} to {self.device}, {self.installation_timeout = }')

        self.run_adb_install(self.smaliened)

        # Sleep
        self.sleep(seconds)

    def install_original(self, seconds=0, install_without_g_option=False):
        """
        Install the original app to the device.

        :param seconds:     smalien stops for <seconds> after the installation.
        """
        logger.debug(f'installing original {self.original} to {self.device}, {self.installation_timeout = }')

        self.run_adb_install(self.original, install_without_g_option=install_without_g_option)

        # Sleep
        self.sleep(seconds)

    def run_adb_install(self, target, install_without_g_option=False):
        """
        Run adb install command with the given target.
        """

        # Create a command
        cmd = copy.copy(self.adb)
        if (install_without_g_option):
            # For old devices, install the app without -g option at first
            cmd.extend([
                'install',
                target])
        else:
            cmd.extend([
                'install',
                '-g',
                target])

        # Run the command
        try:
            result = str(CommandRunner.run(cmd, timeout=self.installation_timeout))

            if (result.find('Error: Unknown option: -g') > 0):
                # The installation is failed because of '-g' option,
                # which is invalid for old devices.
                # Try it again without '-g' option
                logger.debug('failed to install because of -g option, and trying again')
                # Create a command
                cmd = copy.copy(self.adb)
                cmd.extend([
                    'install',
                    target])

                # Run the command
                result = str(CommandRunner.run(cmd, timeout=self.installation_timeout))

        except Exception as e:
            # Handle some adb errors
            if (str(e).find('INSTALL_FAILED_INSUFFICIENT_STORAGE') > -1):
                # This error is sometimes caused with the large datasets of Google Play and Anzhi apps.
                # Reboot the device to fix it
                self.reboot(seconds=60)

                # Run the command again
                try:
                    result = str(CommandRunner.run(cmd, timeout=self.installation_timeout))
                except Exception as e:
                    raise Exception('failed to install') from e

            else:
                raise Exception('failed to install') from e

        if (result.find('FAILED') > 0):
            # Installation failed because of the SDK version of the device
            raise Exception(f'failed to install: {result}')

    def launch(self, seconds=0):
        """
        Launch the app on the device.

        :param seconds:     smalien stops for <seconds> after the operation.
        """
        logger.debug(f'launching {self.package}')

        assert self.package is not None

        # Create a command
        cmd = copy.copy(self.adb)
        cmd.extend([
            'shell',
            'monkey',
            '-p',
            self.package,
            '-c',
            'android.intent.category.LAUNCHER',
            '1'])

        # Run the command
        try:
            CommandRunner.run(cmd)
        except Exception as e:
            logger.debug(f'failed to launch {e = }')

    def uninstall(self, timeout=None):
        """
        Uninstall the app on the device.

        :param timeout:  Timeout seconds for the uninstallation.
        """
        logger.debug(f'uninstalling {self.package} with {timeout = }')

        assert self.package is not None

        # Create a command
        cmd = copy.copy(self.adb)
        cmd.extend([
            'uninstall',
            self.package])

        # Run the command
        try:
            if (timeout is None):
                CommandRunner.run(cmd)
            else:
                CommandRunner.run(cmd, timeout=timeout)
        except Exception as e:
            raise Exception('failed to uninstall') from e

    def collect(self):
        """
        Collect the app's log on the device.
        """
        logger.debug(f'collecting {self.smalien_log}')

        # Create a command
        cmd = copy.copy(self.adb)
        cmd.extend([
            'pull',
            self.smalien_log,
            self.workspace])

        # Run the command
        try:
            CommandRunner.run(cmd)

            # Successfully collected
            return True

        except Exception as e:
            logger.debug(f'failed to collect {e = }')

            return False

    def press_home_button(self, seconds=0):
        """
        Press home button.

        :param seconds:     smalien stops for <seconds> after the operation.
        """
        logger.debug(f'pressing home button of {self.device}')

        # Create a command
        cmd = copy.copy(self.adb)
        cmd.extend([
            'shell',
            'input',
            'keyevent',
            'KEYCODE_HOME'])

        # Run the command
        try:
            CommandRunner.run(cmd)
        except Exception as e:
            raise Exception('failed to press home button') from e

        # Sleep
        self.sleep(seconds)

    def press_back_button(self, seconds=0):
        """
        Press back button.

        :param seconds:     smalien stops for <seconds> after the operation.
        """
        logger.debug(f'pressing back button of {self.device}')

        # Create a command
        cmd = copy.copy(self.adb)
        cmd.extend([
            'shell',
            'input',
            'keyevent',
            'KEYCODE_BACK'])

        # Run the command
        try:
            CommandRunner.run(cmd)
        except Exception as e:
            raise Exception('failed to press back button') from e

        # Sleep
        self.sleep(seconds)

    # def press_switch_button(self, seconds=0):
    #     """
    #     Press switch button.

    #     :param seconds:     smalien stops for <seconds> after the operation.
    #     """
    #     logger.debug(f'pressing switch button of {self.device}')

    #     # Create a command
    #     cmd = copy.copy(self.adb)
    #     cmd.extend([
    #         'shell',
    #         'input',
    #         'keyevent',
    #         'KEYCODE_APP_SWITCH'])

    #     # Run the command
    #     try:
    #         CommandRunner.run(cmd)
    #     except Exception as e:
    #         raise Exception('failed to press switch button') from e

    #     # Sleep
    #     self.sleep(seconds)

    def start_activity(self, activity, seconds=0):
        """
        Start the given activity with ActivityManager.

        :param activity:    activity to be started
        :param seconds:     smalien stops for <seconds> after the operation
        """
        logger.debug(f'starting {activity = }')

        # Create a command
        cmd = copy.copy(self.adb)
        cmd.extend([
            'shell',
            'am',
            'start',
            '-n',
            activity])

        # Run the command
        try:
            CommandRunner.run(cmd)
        except Exception as e:
            raise Exception('failed to start activity') from e

        # Sleep
        self.sleep(seconds)

    def send_broadcast(self, receiver, seconds=0):
        """
        Send a broadcast with the given receiver.

        :param receiver:    receiver of a broadcast
        :param seconds:     smalien stops for <seconds> after the operation
        """
        logger.debug(f'sending a broadcast for {receiver = }')

        # Create a command
        cmd = copy.copy(self.adb)
        cmd.extend([
            'shell',
            'am',
            'broadcast',
            '-n',
            receiver])

        # Run the command
        try:
            CommandRunner.run(cmd)
        except Exception as e:
            raise Exception('failed to send a broadcast') from e

        # Sleep
        self.sleep(seconds)

    def start_service(self, service, seconds=0):
        """
        Start the given service by using am command.
        Requires root account of adb.

        :param service:    service name
        :param seconds:     smalien stops for <seconds> after the operation
        """
        logger.debug(f'starting {service = }')

        # Create a command
        cmd = copy.copy(self.adb)
        cmd.extend([
            'shell',
            'su',
            'root',
            'am',
            'start-service',
            '-n',
            service])

        # Run the command
        try:
            CommandRunner.run(cmd)
        except Exception as e:
            raise Exception('failed to start the service') from e

        # Sleep
        self.sleep(seconds)

    def kill(self, seconds=0):
        """
        Kill processes of the package.

        :param seconds:     smalien stops for <seconds> after the operation
        """
        logger.debug(f'killing processes of {self.package = }')

        assert self.package is not None

        # Create a command
        cmd = copy.copy(self.adb)
        cmd.extend([
            'shell',
            'run-as',
            self.package,
            'ps',
            '-A',
            '-o',
            'PID'])

        # Run the command
        try:
            pids = CommandRunner.run(cmd).decode()

            if (pids.startswith('USER ')):
                # Device is old, and pids must be obtained with the different command
                logger.debug('obtaining PIDS with the different command')
                cmd = copy.copy(self.adb)
                cmd.extend([
                    'shell',
                    'run-as',
                    self.package,
                    'ps',
                    '|',
                    'grep',
                    self.package])

                pids = CommandRunner.run(cmd).decode()
                # Extract a pid of the process
                # E.g., the command returns 'u0_a163   3174  194   1534004 54704 ffffffff b6eca97c S de.ecspride'
                pids = pids.split()[1] if pids != '' else ''

            logger.debug(f'{pids = }')
            for pid in pids.split('\n'):
                if (pid in ['  PID', '']):
                    continue

                logger.debug(f'killing process {pid = }')
                # Create a command
                cmd = copy.copy(self.adb)
                cmd.extend([
                    'shell',
                    'run-as',
                    self.package,
                    'kill',
                    '-9',
                    pid])
                # Run the command
                try:
                    output = CommandRunner.run(cmd)
                    logger.debug(f'{output = }')
                except Exception as e:
                    logger.debug(f'{e = }')
        except Exception as e:
            raise Exception('failed to kill processes') from e

        # Sleep
        self.sleep(seconds)

    def rotate_screen(self, rotate_to='landscape', seconds=0):
        """
        Rotate the screen to the given mode, then reset the screen rotation to portrait.

        :param rotate_to:    Rotation mode. landscape or portrait.
        :param seconds:     smalien stops for <seconds> after the operation
        """
        logger.debug(f'rotating screen to {rotate_to= }')

        try:
            # Disable automatic rotation
            cmd = copy.copy(self.adb)
            cmd.extend([
                'shell',
                'settings',
                'put',
                'system',
                'accelerometer_rotation',
                '0'])
            CommandRunner.run(cmd)

            # Rotate
            user_rotation = '3' if (rotate_to == 'landscape') else '0'

            cmd = copy.copy(self.adb)
            cmd.extend([
                'shell',
                'settings',
                'put',
                'system',
                'user_rotation',
                user_rotation])
            CommandRunner.run(cmd)

            self.sleep(seconds)

            # Reset the screen to portrait
            if (rotate_to == 'landscape'):
                cmd = copy.copy(self.adb)
                cmd.extend([
                    'shell',
                    'settings',
                    'put',
                    'system',
                    'user_rotation',
                    '0'])
                CommandRunner.run(cmd)

        except Exception as e:
            raise Exception('failed to rotate screen') from e

        finally:
            # Enable automatic rotation
            cmd = copy.copy(self.adb)
            cmd.extend([
                'shell',
                'settings',
                'put',
                'system',
                'accelerometer_rotation',
                '1'])
            CommandRunner.run(cmd)

        # Sleep
        self.sleep(seconds)

    def tap_screen(self, x, y, seconds=0):
        """
        Tap the given coordinates of screen.

        :param x, y:        coordinates to be tapped
        :param seconds:     smalien stops for <seconds> after the operation
        """
        logger.debug(f'tapping screen {x = }, {y = }')

        # Create a command
        cmd = copy.copy(self.adb)
        cmd.extend([
            'shell',
            'input',
            'tap',
            str(x),
            str(y)])

        # Run the command
        try:
            CommandRunner.run(cmd)
        except Exception as e:
            raise Exception('failed to tap screen') from e

        # Sleep
        self.sleep(seconds)

    def get_permutations_of_clickable_ui_coordinates(self):
        """
        Extract coordinates of clickable elements on currently-visible UI.
        """
        logger.debug(f'extracting coordinates of clickable elements on currently-visible UI')

        assert self.package is not None

        coordinates = []

        # Create a command
        cmd = copy.copy(self.adb)
        cmd.extend([
            'shell',
            'uiautomator',
            'dump'])

        # Run the command
        try:
            output = CommandRunner.run(cmd).decode()

            assert output.startswith('UI hierchary dumped to: ')

            path_to_dumped = output.split(' ')[-1].rstrip() # Remove '\r' at the tail

            # Create a command to obtain the dumped contents
            cmd = copy.copy(self.adb)
            cmd.extend([
                'shell',
                'cat',
                path_to_dumped])

            # Run the command
            output = CommandRunner.run(cmd).decode()

            logger.debug(f'{output = }')

            root = ElementTree.fromstring(output)

            for node in root.findall('.//node'):
                if (node.attrib['package'] == self.package and
                    # For Button
                    (node.attrib['clickable'] == 'true' and
                     node.attrib['focusable'] == 'true' and
                     node.attrib['long-clickable'] == 'false') or
                    # For ListView in FragmentLifecycle2
                    (node.attrib['clickable'] == 'false' and
                     node.attrib['focusable'] == 'true' and
                     node.attrib['focused'] == 'true')
                   ):
                    bounds = node.attrib['bounds']
                    x = bounds.split(']')[0].split(',')[0][1:]
                    y = bounds.split(']')[0].split(',')[1]

                    # Add 1 to x and y
                    x = int(x) + 1
                    y = int(y) + 1

                    logger.debug(f"UI clickable is found {node.attrib['class'] }, {node.attrib['text'] = }, {x = }, {y = }")

                    coordinates.append([x, y])

        except Exception as e:
            raise Exception('failed to extract coordinates of clickable elements on the screen') from e

        # Generate combinations of the coordinates
        permutations = []

        # Considering combinations and permutations.
        # This is unnecessary for DroidBench
        # for size in range(len(coordinates)):
        #     logger.debug(f'{size = }')
        #     for subset in itertools.combinations(coordinates, size+1):
        #         for permutationin itertools.permutations(subset):
        #             logger.debug(f'{permutation = }')
        #             permutations.append(permutation)

        for permutation in itertools.permutations(coordinates):
            if (permutation):
                permutations.append(list(permutation))

        logger.debug(f'{permutations = }')

        return permutations

    def logcat_dump(self, logcat_log=None):
        """
        Dump logcat log.

        :param logcat_log:  Path to log file. If None, save logs to the default file in the app's directory.
        """
        if (logcat_log is None):
            logcat_log = self.logcat_log

        logger.debug(f'Running logcat to dump and save logs to {logcat_log = }')

        # Create a command
        cmd = copy.copy(self.adb)
        cmd.extend([
            'logcat',
            '-v',
            'time',
            '-d'])

        # Run the command
        try:
            results = CommandRunner.run(cmd)

            # Write to file
            with open(logcat_log, 'w') as f:
                f.write(results.decode('utf-8'))
        except Exception as e:
            raise Exception('failed to dump logcat log') from e

    def logcat_clear(self):
        """
        Clear logcat log.
        """
        logger.debug(f'Clearing old logcat logs')

        # Create a command
        cmd = copy.copy(self.adb)
        cmd.extend([
            'logcat',
            '-c'])

        # Run the command
        try:
            CommandRunner.run(cmd)
        except Exception as e:
            # logcat_clear can be failed, but it is ok to ignore it.
            pass

    def logcat_start(self, logcat_log=None):
        """
        Start dumping logcat log.
        Save a logcat process to self.logcat_process.

        :param logcat_log:  Path to log file. If None, save logs to the default file in the app's directory.
        """
        if (logcat_log is None):
            logcat_log = self.logcat_log

        logger.debug(f'Starting logcat to dump and save logs to {logcat_log = }')

        # Create a command
        cmd = copy.copy(self.adb)
        cmd.extend([
            'logcat',
            '-v',
            'time'])

        # Run the command
        try:
            self.logcat_process = CommandRunner.start_process_with_redirecting_to_file(cmd, logcat_log)

            assert self.logcat_process is not None

        except Exception as e:
            raise Exception('failed to start logcat process') from e

    def logcat_stop(self):
        """
        Stop dumping logcat log.
        """
        logger.debug(f'Stopping logcat')

        assert self.logcat_process is not None, 'Logcat is already stopped'

        self.logcat_process.terminate()

    def python2_script(self, script, arguments):
        """
        Run the script with python2.

        :param script:     Path to script to execute.
        :param arguments:  Arguments passed to the script.
        """
        logger.debug(f'Running python2 {script = } {arguments = }')

        # Create a command
        cmd = [
            'python2',
            script]
        cmd.extend(arguments)

        # Run the command
        try:
            result = CommandRunner.run(cmd)
            return result

        except Exception as e:
            raise Exception('failed to run python2 script') from e

    def mitmdump_start(self, mitmdump_log=None, mitmdump_port=18080):
        """
        Start dumping the traffic with mitmdump.
        Save the process to self.mitmdump_process.

        :param mitmdump_log:   Path to log file. If None, save logs to the default file in the app's directory.
        :param mitmdump_port:  Port to be listened.
        """
        if (mitmdump_log is None):
            mitmdump_log = self.mitmdump_log

        logger.debug(f'Starting mitmdump to dump and save logs to {mitmdump_log = }')

        # Create commands
        cmd = [
            'mitmdump',
            '--set',
            'block_global=false',
            '--set',
            'flow_detail=4',
            '--set',
            'listen_port='+str(mitmdump_port),
            '--set',
            'tls_version_client_min=UNBOUNDED',
            '--showhost']

        # Run the command
        try:
            self.mitmdump_process = CommandRunner.start_process(cmd)

            assert self.mitmdump_process is not None

            self.mitmdump_recorder_pool = ThreadPoolExecutor(max_workers=1)
            self.mitmdump_recorder_pool.submit(mitmdump_recorder, (self.mitmdump_process, mitmdump_log))

        except Exception as e:
            raise Exception('failed to start mitmdump process') from e

    def mitmdump_stop(self):
        """
        Stop mitmdump.
        """
        logger.debug(f'Stopping mitmdump')

        assert self.mitmdump_process is not None, 'mitmdump is already stopped'

        self.mitmdump_process.terminate()
        self.mitmdump_recorder_pool.shutdown()
