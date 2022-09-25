import logging
import pathlib

from .loader import Loader
from .definitions import SMALIEN_LOG

from .utils.nops import NoMatch
from .utils.apk_handler import ApkHandler
from .utils.pickle_handler import PickleHandler
from .utils.pretty_printer import PrettyPrinter

from .instrumentator.instrumentator import Instrumentator

from .exerciser.exerciser import Exerciser
from .exerciser.automatic_exerciser import AutomaticExerciser

from .emulator.emulator import Emulator
from .emulator.vm_manager.structures import VMOrder

from .taint_definitions.sources import taint_sources
from .taint_definitions.sinks import taint_sinks

logger = logging.getLogger(name=__name__)


class Project:
    """
    This is the main class of the smalien module.
    It provides an interface to instrumenting, exercising, and emulating the app.
    """

    def __init__(self, target, ignore_list=[], target_packages=[],
                 rm_unpackaged=False, run_parser=True, device=None, apktool='apktool',
                 taint_source_definition=taint_sources, taint_sink_definition=taint_sinks,
                 detect_reconstruction_failures=True):
        """
        :param target:           Path to target, either *.apk or *.pickle
        :param ignore_list:      Listing package names skipped by the analysis.
                                 An item should not contain '/'.
        :param target_packages:  Listing package names targetted by the analysis.
        :param rm_unpackaged:    Remove unpackaged app's directory when the analysis failed.
        :param run_parser:       True: Run parser.
                                 False: Do not run parser. Used for exercising the app with TaintDroid.
        :param device:           Android device for exercising the app.
        :apktool:                apktool command.
        :taint_source_definition:  Definition of taint sources.
        :taint_sink_definition:    Definition of taint sinks.
        :param detect_reconstruction_failures:  If true, stop the reconstruction when a failure is detected.
                                                If false, a failure is ignored.
        """
        logger.debug('initializing')

        self.taint_sources = taint_source_definition
        self.taint_sinks = taint_sink_definition

        self.rm_unpackaged = rm_unpackaged

        # Check if the target exists
        self.target = pathlib.Path(target)
        assert self.target.exists(), 'The target does not exist.'

        # Set a workspace path
        self.workspace = self.target.parent.resolve()

        # Initialize apk handler
        self.apk_handler = ApkHandler(apktool=apktool)

        try:
            # Load the target data
            # Call a loader based on the target's extension (i.e., .pickle or .apk)
            self.app = Loader.loaders.get(self.target.suffix, NoMatch.run)(target=self.target,
                                                                           workspace=self.workspace,
                                                                           ignore_list=ignore_list,
                                                                           target_packages=target_packages,
                                                                           apk_handler=self.apk_handler,
                                                                           smalien_log=SMALIEN_LOG,
                                                                           run_parser=run_parser,
                                                                           taint_sources=self.taint_sources,
                                                                           taint_sinks=self.taint_sinks,)
            logger.debug(f'{self.app.num_potential_sources = }')
            logger.debug(f'{self.app.num_potential_sinks = }')
        except Exception as e:
            if (self.rm_unpackaged):
                # Remove the unpackaged
                self.apk_handler.rm_unpackaged(self.workspace/self.target.stem)

            raise e

        # Initialize other modules
        self.emulator = Emulator(self.app,
                                 self.workspace,
                                 self.taint_sources,
                                 self.taint_sinks,
                                 detect_failures=detect_reconstruction_failures)
        self.pprinter = PrettyPrinter(self.app)

        if (device is not None):
            self.exerciser = Exerciser(self.app, self.workspace, device)

    def pprint(self, **kwargs):
        """
        Print the app code to the stdout.

        :param smali_path: Path to a smali file to print.
        :param method:     Method name to print.
        """
        self.pprinter.pprint_app(kwargs)

    def save(self):
        """
        Save the app code to the pickle.
        """
        PickleHandler.store(self.app, self.app.pickled)

    def configure_keystore(self, **kwargs):
        """
        Set keystore information for signing the repackaged apk.

        :param keystore:         Path to your keystore
        :param storepass:        String of storepass
        :param keypass:          String of keypass
        :param alias:            String of alias
        """
        self.apk_handler.configure_keystore(kwargs)

    def instrument(self, log_buff_size=0, register_reassignment=False, multi_dex=True, dummy_source_values=None):
        """
        Launch static bytecode instrumentation.

        :param log_buff_size:          The threshold for buffering logs at runtime
        :param register_reassignment:  Reassign registers
        :param multi_dex:              Enable multi dex
        :param dummy_source_values:    Dummy source values for the injection
        """
        logger.debug('instrumenting')

        try:
            Instrumentator(self.app, log_buff_size, register_reassignment, multi_dex, self.taint_sources, dummy_source_values).run()
        except Exception as e:
            if (self.rm_unpackaged):
                # Remove the unpackaged
                self.apk_handler.rm_unpackaged(self.workspace/self.target.stem)

            raise e

    def create_new_apk(self, signer='jarsigner'):
        """
        Package and sign to create a new apk.

        :param signer:        Command name or path of signer
        """
        logger.debug('creating a new apk')

        try:
            self.apk_handler.package_and_sign(self.app.unpackaged, self.app.smaliened, signer)
        except Exception as e:
            raise e
        finally:
            if (self.rm_unpackaged):
                # Remove the unpackaged
                self.apk_handler.rm_unpackaged(self.workspace/self.target.stem)

    def remove_unpackaged(self):
        """
        Remove the unpackaged directory.
        """
        logger.debug('removing the unpackaged directory')

        self.apk_handler.rm_unpackaged(self.app.unpackaged)

    def exercise_automatically(self, devices, action_num_limit=None):
        """
        Automatically launch and exercise the app on an Android device to record runtime data.
        Returns the number of detected leaks.

        :param devices:    List of device on that the app is exercised.
        :param action_num_limit:  Limit of the number of actions the exerciser performs.
        """
        logger.debug('exercising the app automatically')

        automatic_exerciser = AutomaticExerciser(self.app, self.workspace,
                                                 self.taint_sources,
                                                 self.taint_sinks,
                                                 devices, action_num_limit)
        return automatic_exerciser.run()

        # Replace the project's emulator with the actually-used emulator
        # self.emulator = automatic_exerciser.emulator

    def emulate(self, clss, method=None, line=None):
        """
        Emulate the app code without runtime data.

        :param clss:      App's class at that the emulation begins.
        :param method:    App's method at that the emulation begins.
        :param line:      App's line at that the emulation begins.
        """
        logger.debug('emulating')

        if (line is None):
            # Use the line number of the method head as a starting point
            line = self.app.classes[clss].methods[method].start_at

        self.emulator.run(VMOrder(clss=clss, method=method, line=line))

    def emulate_with_runtime_logs(self):
        """
        Emulate the app code with runtime data.
        """
        logger.debug('emulating with runtime logs')

        try:
            self.emulator.run_with_runtime_logs()
        except Exception as e:
            raise e
        finally:
            # Before finish the emulation, print smali file paths.
            # self.emulator.runtime_log_manager.print_smali_paths()
            pass

    def print_found_sources(self):
        """
        Print detected sources.
        """
        logger.info('printing detected sources.')

        sources = self.emulator.get_found_sources()

        self.pprinter.pprint_data(sources)

    def print_taint_history(self):
        """
        Print recorded taint history.
        """
        logger.info('printing taint history.')

        taint_history = self.emulator.get_taint_history()

        self.pprinter.pprint_data(taint_history)

    def print_found_sinks(self):
        """
        Print detected sinks.
        """
        logger.info('printing detected sinks.')

        sinks = self.emulator.get_found_sinks()

        self.pprinter.pprint_data(sinks)
