import logging

from ..value_manager.structures import ClassInstanceValue

logger = logging.getLogger(name=__name__)


class Recorder:
    """
    This class records taint history.
    """

    def __init__(self):
        logger.debug('initializing')

        self.taint_history = []

    def run(self, **kwargs):
        """
        Run the recorder.
        """
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']
        clss = kwargs['clss']
        method = kwargs['method']

        tainted = self.get_tainted_registers_and_fields(registers)
        if (tainted):
            if (self.taint_history):
                # If taint history is not empty, compare the new flow to the history elements.
                # If they are matched, the updating is not necessary and is skipped.
                # Parse the history in reverse because the most recent element is most likely to match.
                for history in reversed(self.taint_history):
                    matched = self.compare(history, clss, method, tainted)
                    if (matched):
                        return

            # Update taint history with the new information
            self.update_taint_history(clss, method, inst, tainted)

    def get_tainted_registers_and_fields(self, registers):
        """
        Extract tainted registers from register list.
        """
        tainted = []

        for reg, value in registers.items():
            if (value.taint is not None):
                tainted.append(reg)

            # Check fields if value is reference-data-type
            if (isinstance(value, ClassInstanceValue)):
                for field_key, field_value in value.fields.items():
                    if (field_key not in tainted and field_value.taint is not None):
                        tainted.append(field_key)

        return tainted

    def compare(self, prev, clss, method, tainted):
        """
        Compare previous history with the new information.
        """
        return (prev['class'] == clss and prev['method'] == method and prev['tainted'] == tainted)

    def update_taint_history(self, clss, method, inst, tainted):
        """
        Add an item to taint_history.
        """
        self.taint_history.append({
            'class': clss,
            'method': method,
            'num': inst.num,
            'instruction': inst.instruction,
            # 'inst': inst,
            'tainted': tainted,
        })

    def get_taint_history(self):
        """
        Return results of recorded taint history.
        """
        return self.taint_history

    def compare_taint_histories(self, history2):
        """
        Compare the self history to the given history.
        """

        if (len(self.taint_history) != len(history2)):
            return False

        for i, h1 in enumerate(self.taint_history):
            h2 = history2[i]

            matched = (h1['class'] == h2['class'] and
                     h1['method'] == h2['method'] and
                     h1['num'] == h2['num'] and
                     h1['tainted'] == h2['tainted'])

            if (not matched):
                return False

        return True
