import logging

from .mapping import mapping
from ...vm_manager.exceptions import ExceptionOccurException, ClinitInvokedException
from smalien.utils.nops import Nop

logger = logging.getLogger(name=__name__)


class ValueManager:
    """
    Manage register values for the emulation.
    """

    def __init__(self, app, detect_failures):
        logger.debug('initializing')

        self.classes = app.classes
        self.detect_failures = detect_failures

        self.mapping = mapping

    def run(self, **kwargs):
        """
        Run the updater.
        """
        logger.debug('running')

        inst = kwargs['inst']
        sf = kwargs['sf']

        try:
            self.mapping.get(inst.kind, Nop).run(inst=inst,
                                                 clss=sf.clss,
                                                 method=sf.method,
                                                 registers=sf.registers,
                                                 new_values=sf.new_values,
                                                 previous=sf.previous,
                                                 after_invocation=sf.after_invocation,
                                                 instances=kwargs['instances'],
                                                 static_fields=kwargs['static_fields'],
                                                 mattr=self.classes[sf.clss].methods[sf.method].attribute,
                                                 is_constructor=self.classes[sf.clss].methods[sf.method].is_constructor,
                                                 classes=self.classes,
                                                 vm = kwargs['vm'],
                                                 self_ptids=kwargs['self_ptids'],
                                                 vms=kwargs['vms'],
                                                 detect_failures=self.detect_failures)
        except ExceptionOccurException as e:
            raise e
        except ClinitInvokedException as e:
            raise e
        except Exception as e:
            if (self.detect_failures):
                raise Exception(f'{sf.clss = }, {sf.method = }, {sf.pc = }') from e
            else:
                # Ignore the failure
                pass
