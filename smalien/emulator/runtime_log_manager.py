import logging
import io
import re
import json

from .coverage_calculator import CoverageCalculator
from .vm_manager.structures import VMOrder

logger = logging.getLogger(name=__name__)


class RuntimeLogManager:
    """
    This class arranges the runtime log and passes it to the emulator.
    """

    def __init__(self, app, workspace, calculate_coverage):
        logger.debug('initializing')

        self.app = app
        logger.debug(f'{self.app.cids.keys() = }')

        self.local_log = app.smalien_log_local

        self.app_launch_time = None

        self.smali_paths = set()

        # For calculating coverage
        self.coverage_calculator = None
        if (calculate_coverage):
            self.coverage_calculator = CoverageCalculator(app)

        # For counting the number of logs
        self.log_num = 0

    def run(self):
        """
        Read and transform runtime logs for the emulator.
        """
        logger.debug('running')

        # Create a container of VM orders.
        # Key is the VM order's PTIDs.
        # This keeps multiple VM orders because multiple logs at the same line, which should be consecutive,
        # can be separated by other logs from different threads.
        vm_orders = {}
        for time, pid, tid, cid, line, reg, value in self.parse_logs():
            if (self.app_launch_time is None):
                self.app_launch_time = time
                logger.debug(f'app launched at {self.app_launch_time = }')

            # Resolve class and method names from cid and line
            cdata = self.app.cids[cid]
            clss = cdata.name
            method = self.get_method_of_line(cdata, line)
            values = {reg: value} if (reg is not None) else {}

            # For calculating coverage
            if (self.coverage_calculator):
                self.coverage_calculator.save_explored_method(clss, method)

            # For debugging
            # Skip 'const' and 'if' records
            inst = cdata.methods[method].instructions[line]
            if (inst.kind in ['const', 'if', 'ifz', 'binoplit8']):
                continue

            # Register smali path
            self.register_smali_path(cdata.path)

            # Generate a key for storing a vm order
            ptids = self.combine_ptids(pid, tid)

            if (ptids in vm_orders.keys()):
                # The same PTIDs VM order is previously created.
                # Check if the logging location is the same.
                # Also, check if the logged register is different.
                if (vm_orders[ptids].clss == clss and
                    vm_orders[ptids].line == line and
                    reg is not None and
                    reg not in vm_orders[ptids].values.keys()):
                    # The location matches.
                    # For example. multiple logs appear at a method head with multiple parameters.
                    # If two logs are matched, the second register should have a value
                    # assert reg is not None, f'two logs matched, but reg is None, {reg = }, {vm_orders[ptids] = }'

                    # Add the new value to the VM order
                    vm_orders[ptids].values[reg] = value

                # If registers previously and newly logged are the same and not None, the logs should be different.
                # For example, such logs can appear at point where after reccursive invocation of methods
                else:
                    # The location does not match.
                    # Return the previous VM order.
                    yield vm_orders[ptids]

                    # Create a new VM order with the new log.
                    vm_orders[ptids] = VMOrder(clss=clss, method=method, line=line, pid=pid, tid=tid, values=values, logging=True, timestamp=time)
            else:
                # No VM order of the same PTIDs is previously created.
                # Create a new VM order with the new log.
                vm_orders[ptids] = VMOrder(clss=clss, method=method, line=line, pid=pid, tid=tid, values=values, logging=True, timestamp=time)

        # Return the last vm_orders
        for vm_order in vm_orders.values():
            vm_order.last_record = True

            yield vm_order

    def combine_ptids(self, pid, tid):
        return '{}_{}'.format(pid, tid)

    def get_method_of_line(self, cdata, line):
        """
        Get method name containing the code of the line.
        """
        for method, mdata in cdata.methods.items():
            if (mdata.start_at <= line <= mdata.end_at):
                return method
        raise Exception(f'Failed to find method of {line = } in {cdata.name = }')

    def parse_logs(self):
        """
        Parse smalien logs.
        """
        logger.debug('parsing logs')
        for log_list in self.read_logs():
            for log in log_list:
                # logger.info({'log': log})

                # A log can be None when not a log string but a null is logged by the app.
                # The cause must be investigated, and currently raise an error
                assert log is not None, 'a log is none, meaning null is logged by the app'

                assert re.match(r'^\d{13}:\d+:\d+:\d+_\d+', log) is not None, f'Corrupted, {log = }'

                time = int(log.split(':')[0])
                pid = int(log.split(':')[1])
                tid = int(log.split(':')[2])

                smalien_id = log.split(':')[3]
                cid = int(smalien_id.split('_')[0])
                line = int(smalien_id.split('_')[1])

                reg = smalien_id.split('_')[-1] if (len(smalien_id.split('_')) > 2) else None
                value = ':'.join(log.split(':')[4:]) if (reg is not None) else None

                # Count the number of logs
                self.log_num += 1

                # Delete log to free memory
                del log

                yield time, pid, tid, cid, line, reg, value

            # Delete log list to free memory
            del log_list

    def read_logs(self):
        """
        Read smalien logs from self.local_log.
        """
        logger.debug(f'reading {self.local_log = }')
        try:
            with io.open(self.local_log, 'r', encoding='utf-8', errors='ignore') as f:
                for string in f:
                    yield json.loads(string)
        except Exception as e:
            logger.warning('smalien log is not found')
            return []

    def register_smali_path(self, path):
        """
        Register the given path to self.smali_paths.
        """
        logger.debug('registering a smali path')

        self.smali_paths.add(path)

    def print_smali_paths(self):
        """
        Print smali file paths of logged code.
        """
        logger.debug('printing smali paths')

        # Print all smali paths

        # This assertion causes a failure in test of androidspecific.inactiveactivity
        # assert len(self.smali_paths) > 0

        if (len(self.smali_paths) > 0):
            for smali_path in self.smali_paths:
                print(f'vi {smali_path}')

            # Print smalien logger definition
            print(f'vi {smali_path.split("/smali/")[0]}/smali_classes2/SmalienLog_0.smali')

    def get_coverage(self):
        """
        Returns the calculated coverage.
        """
        return self.coverage_calculator.get_coverage()

    def get_log_num(self):
        """
        Returns the number of logs.
        """
        return self.log_num
