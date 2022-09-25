import logging
from typing import Dict
from dataclasses import dataclass, field

from .structures import VM, VMOrder
from .vm_runner import VMRunner
from .callback_triggerer import CallbackTriggerer
from .exceptions import StackIsEmptyException, LogPointException, ExceptionThrownException, ExceptionOccurException, ClinitInvokedException

logger = logging.getLogger(name=__name__)


class VMCreator:
    """
    Start a new virtual machine (VM).
    """
    @staticmethod
    def run(**kwargs):
        """
        Run the creator.

        :param ptids:         PID and TID of a VM.
        :param pid:           PID of a VM.
        :param tid:           TID of a VM.
        :param vms:           Current list of VMs.
        :param classes:       App's classes data.
        :param clss:          Target class.
        :param method:        Target method.
        :param line:          Target line.
        :param logging:       Use runtime logs if logging=true.
        :param instances:     Instances.
        :param static_fields  Static field objects.
        :param interpreter:   Interpreter modules for the emulation.
        :param detect_failures:   Whether detecting failures.
        """
        ptids = kwargs['ptids']
        pid = kwargs['pid']
        tid = kwargs['tid']
        vms = kwargs['vms']
        classes = kwargs['classes']
        clss = kwargs['clss']
        method = kwargs['method']
        line = kwargs['line']
        logging = kwargs['logging']
        instances = kwargs['instances']
        static_fields = kwargs['static_fields']
        intent_data = kwargs['intent_data']
        interpreters = kwargs['interpreters']
        detect_failures = kwargs['detect_failures']

        logger.debug(f'creating a new vm {ptids = }')

        # Create a new VM
        vms[ptids] = VMRunner(VM(ptids=ptids, pid=pid, tid=tid,
                                 instances=instances,
                                 static_fields=static_fields,
                                 intent_data=intent_data),
                              vms, classes, clss, method, line,
                              logging, interpreters, detect_failures)

        # Start the new VM
        vms[ptids].run(**kwargs)

class VMManager:
    """
    Manage VMs.
    """

    def __init__(self, app, vms, instances, static_fields, intent_data, interpreters, detect_failures):
        logger.debug('initializing')

        self.app = app
        self.vms = vms
        self.instances = instances
        self.static_fields = static_fields
        self.intent_data = intent_data
        self.interpreters = interpreters
        self.detect_failures = detect_failures

        self.callback_triggerer = CallbackTriggerer(self.app.classes)

        self.pid = 0
        self.tid = 0

    def run(self, vm_order):
        """
        Create and start VMs based on PID and TID.
        """
        logger.debug('running')

        # Run VMs until a breakpoint
        while True:

            clss = vm_order.clss
            method = vm_order.method
            line = vm_order.line
            pid = vm_order.pid if vm_order.pid is not None else self.pid
            tid = vm_order.tid if vm_order.tid is not None else self.tid
            values = vm_order.values
            logging = vm_order.logging

            ptids = self.combine_ptids(pid, tid)

            try:
                # Run a VM based on PID and TID
                self.vms.get(ptids, VMCreator).run(ptids=ptids, pid=pid, tid=tid,
                                                   vms=self.vms,
                                                   classes=self.app.classes,
                                                   clss=clss, method=method,
                                                   line=line, values=values,
                                                   logging=logging,
                                                   instances=self.instances,
                                                   static_fields=self.static_fields,
                                                   intent_data=self.intent_data,
                                                   interpreters=self.interpreters,
                                                   detect_failures=self.detect_failures)
            except LogPointException as e:
                logger.info('a log point is reached')
                # logger.info(e.args[0])
                return

            except ExceptionThrownException as e:
                logger.info('an exception is thrown')
                return

            except ExceptionOccurException as e:
                logger.info('an exception occurs')
                return

            except ClinitInvokedException as e:
                logger.info('clinit will be invoked')
                return

            except StackIsEmptyException as e:
                logger.info(f'stack is empty {e = }')

                return

                # # Find a callback method to trigger
                # vm_order = self.callback_triggerer.trigger_at_constructor(self.vms.get(ptids).vm)
                # if (vm_order is None):
                #     break

    def finish_the_emulation(self):
        """
        Invoked by emulator when the emulation is exiting.
        """
        logger.debug('finishing the emulation')

        # # Trigger callbacks
        # for callback_vm_order in self.callback_triggerer.trigger_at_end(self.vms):
        #     self.run(callback_vm_order)

    def combine_ptids(self, pid, tid):
        return '{}_{}'.format(pid, tid)
