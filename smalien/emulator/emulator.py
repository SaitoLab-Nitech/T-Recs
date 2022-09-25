import logging

from .structures import EmulationData
from .flow_detail_logger import FlowDetailLogger
from .vm_manager.vm_manager import VMManager
from .interpreter.interpreter import Interpreter
from .runtime_log_manager import RuntimeLogManager
# from smalien.utils.loggers import FlowFilter
# from .storage_manager.storage_manager import StorageManager
# from .taint_logics.structures import TaintResults

# from smalien.taint_definitions.sources import taint_sources
# from smalien.taint_definitions.sinks import taint_sinks

logger = logging.getLogger(name=__name__)


class Emulator:
    """
    This class processes runtime log to emulate the app and detect information flows.
    Virtual machines are created based on PID and TID.
    """

    def __init__(self, app, workspace, taint_sources, taint_sinks, detect_failures=True, calculate_coverage=True):
        logger.debug('initializing')

        self.app = app

        # Initialize runtime log manager
        self.runtime_log_manager = RuntimeLogManager(app, workspace, calculate_coverage)

        # Create an emulation data object
        self.data = EmulationData()

        self.detect_failures = detect_failures

        # Setup storage
        # TODO: Implement this and pass this to vm_manager.
        # or, this can be created similar to data.static_fields
        # self.storage_manager = StorageManager()

        # Setup for interpreters and virtual machines
        self.interpreter = Interpreter(self.app, taint_sources, taint_sinks, self.detect_failures)
        self.vm_manager = VMManager(self.app, self.data.vms,
                                    self.data.instances,
                                    self.data.static_fields,
                                    self.data.intent_data,
                                    self.interpreter.modules,
                                    self.detect_failures)

        # Setup flow detail log path
        FlowDetailLogger.open_flow_detail_log_file(workspace)

        # # Add a file handler
        # handler = logging.FileHandler(workspace / path_to_log)
        # handler.setLevel(logging.DEBUG)
        # handler.setFormatter(logging.Formatter("%(levelname)-7s | %(module)s:%(lineno)s | %(message)s"))
        # handler.addFilter(FlowFilter())
        # logging.root.addHandler(handler)  # Failed
        # # logging.getLogger('smalien').addHandler(handler)  # Failed
        # # logger.addHandler(handler)  # Failed
        # # logger.critical(f'[FLOW] test {workspace}')  # Failed

    def run(self, vm_order):
        """
        Run the emulator.

        :param vm_order:   Information for ordering VMManager to start.
        """
        logger.debug({'vm_order': vm_order})

        # Start VMs based on PID and TID
        try:
            self.vm_manager.run(vm_order)
        except Exception as e:
            raise Exception(vm_order) from e

    def run_with_runtime_logs(self):
        """
        Run the emulator with runtime logs.
        """
        logger.debug('running with runtime logs')

        for vm_order in self.runtime_log_manager.run():
            # TODO: Implement timeout and memory limit
            try:
                self.run(vm_order)
            except Exception as e:
                if (vm_order.last_record):
                    logger.info('ignoring an exception thrown by VMOrder of the last record')
                else:
                    raise e

        # Trigger callback methods statically
        self.vm_manager.finish_the_emulation()

    def get_found_sources(self):
        """
        Return results of found sources.
        """
        # TODO: Improve this design.
        return self.interpreter.taint_tracker.source_detector.get_found_sources()

    def get_found_sinks(self):
        """
        Return results of found sinks.
        """
        # TODO: Improve this design.
        return self.interpreter.taint_tracker.sink_detector.get_found_sinks()

    def get_num_leaks(self):
        """
        Return the number of leaks detected.
        """
        return self.interpreter.taint_tracker.sink_detector.get_num_leaks()

    def get_taint_history(self):
        """
        Return results of recorded taint history.
        """
        return self.interpreter.taint_tracker.recorder.get_taint_history()

    def compare_taint_histories(self, history2):
        """
        Return true if the given history matched to self history.
        """
        return self.interpreter.taint_tracker.recorder.compare_taint_histories(history2)

    def append_unique_leaks(self, unique_leaks):
        """
        Append unique leaks to the given dictionary.
        """
        self.interpreter.taint_tracker.sink_detector.get_detected_leaks(unique_leaks)

    def get_coverage(self):
        """
        Returns the calculated coverage.
        """
        return self.runtime_log_manager.get_coverage()

    def get_log_num(self):
        """
        Returns the number of logs.
        """
        return self.runtime_log_manager.get_log_num()
