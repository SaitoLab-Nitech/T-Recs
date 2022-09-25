import logging
import re

from .payload.mapping import payload_mapping, value_logging_mapping
from .payload.structures import PayloadLocals, PayloadMove, PayloadMoveResult, PayloadMoveException, PayloadGoto, PayloadGotoExtra, PayloadGotoLabel, PayloadGotoLabelExtra, PayloadCondLabel, PayloadLogging, PayloadDummyReturnedValue
from smalien.definitions import REF_LIMIT_IN_DEX

logger = logging.getLogger(name=__name__)


class Generator():
    """
    Generate code logging runtime data of the app.
    """

    def __init__(self, app, register_reassignment, use_shared_converter, converter_keys, taint_sources, dummy_source_values):
        logger.debug('initializing')

        self.app = app
        self.register_reassignment = register_reassignment  # For reassigning registers of move-result and move-exception destinations 
        self.use_shared_converter = use_shared_converter
        self.converter_keys = converter_keys

        self.taint_sources = taint_sources
        self.dummy_source_values = dummy_source_values

        self.reference_num = 0
        self.smalien_dex_id = 0


    def run(self):
        """
        Execute the generator.
        """

        for class_data in self.app.classes.values():
            # If the class not in the ignore list, perform the instrumentation
            if (not class_data.ignore):
                try:
                    self.generate_payload_for_a_class(class_data.payloads,
                                                      class_data.methods,
                                                      class_data.cid,
                                                      self.app.classes)
                except Exception as e:
                    raise Exception(f'{class_data.path = }') from e

    def generate_payload_for_a_class(self, class_payloads, methods, cid, classes):
        """
        Generate one class's payload.
        """
        for method in methods.values():
            if (not method.implemented):
                continue

            # Generate payloads for instructions in the method
            for i in range(method.start_at, method.end_at):
                inst = method.instructions.get(i, None)
                if (inst is not None and inst.kind in payload_mapping.keys()):
                    # Generate and save a payload
                    payloads, converter_keys = payload_mapping[inst.kind].run(inst=inst,
                                                                              cid=cid,
                                                                              value_logging=value_logging_mapping[inst.kind],
                                                                              start_at=method.start_at,
                                                                              local_reg_num=method.local_reg_num,
                                                                              mparam_num=len(method.parameters),
                                                                              is_constructor=method.is_constructor,
                                                                              instructions=method.instructions,
                                                                              method_data=method,
                                                                              counter=self.smalien_dex_id,
                                                                              register_reassignment=self.register_reassignment,
                                                                              # classes=classes,
                                                                              use_shared_converter=self.use_shared_converter,
                                                                              taint_sources=self.taint_sources,
                                                                              dummy_source_values=self.dummy_source_values)

                    if (payloads):
                        # payloads is an array and not empty
                        # Append the generated payloads to class's payloads
                        self.add_payload(payloads, class_payloads)

                        # save the converter keys
                        self.converter_keys |= converter_keys

                        # Mark the instruction as logged
                        inst.logging = True

                        # Check if the payload counter reaches to the limit
                        if (self.reference_num >= REF_LIMIT_IN_DEX):
                            # Increment the smalien dex id
                            self.smalien_dex_id += 1
                            # Reset the payload counter
                            self.reference_num = 0

    def add_payload(self, payloads, class_payloads):
        """
        Add the payloads to the class's data.
        """
        for payload in payloads:

            match payload:
                case PayloadLocals():
                    # Keep the largest .locals payload
                    if (not isinstance(class_payloads[payload.num][-1], PayloadLocals)):
                        class_payloads[payload.num].append(payload)
                    elif (class_payloads[payload.num][-1].increase < payload.increase):
                        # New payload's increase is larger than previous payload's
                        # So update it
                        class_payloads[payload.num][-1] = payload

                case PayloadMove():
                    class_payloads[payload.num].append(payload)

                case PayloadMoveResult():
                    class_payloads[payload.num].append(payload)

                case PayloadMoveException():
                    class_payloads[payload.num].append(payload)

                case PayloadGoto() | PayloadGotoExtra() | PayloadGotoLabel() | PayloadGotoLabelExtra() | PayloadCondLabel():
                    class_payloads[payload.num].append(payload)

                case PayloadDummyReturnedValue():
                    class_payloads[payload.num].append(payload)

                case PayloadLogging():
                    class_payloads[payload.num].append(payload)
                    # Count the reference number
                    self.reference_num += len(re.findall('invoke-', payload.definition))

                case _:
                    raise Exception(f'unsupported payload type {payload = }')
