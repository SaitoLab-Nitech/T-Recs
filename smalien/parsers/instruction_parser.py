import logging
from collections import defaultdict

from .opcode.structures import *
from .opcode.mapping import opcode_mapping, label_mapping
from .opcode.opcode_parser_utils import Utils
from smalien.data_types import numeric_types_64
from smalien.emulator.interpreter.reflection_resolver import ReflectiveCallDetector
from smalien.emulator.interpreter.taint_tracker.source_detector import SourceApiDetector
from smalien.emulator.interpreter.taint_tracker.sink_detector import SinkApiDetector

logger = logging.getLogger(name=__name__)


class InstructionParser:
    """
    Parse instructions in app methods' body.
    """

    def __init__(self, method_data, code, parent, classes, referenced_methods, taint_sources, taint_sinks):
        logger.debug('initializing')
        self.method_data = method_data
        self.instructions = method_data.instructions
        self.code = code
        self.parent = parent
        self.classes = classes
        self.referenced_methods = referenced_methods
        self.taint_sources = taint_sources
        self.taint_sinks = taint_sinks

        # Categorized instructions according to opecode
        # Key: opecode kind, Value: data of the most recent instruction
        # TODO: Use this instead of other fields
        self.categorized = {}

        self.most_recent_mr_source = None

        # For parsing multiple control instructions and labels
        self.control_labels = {}                          # Key: label, Value: instruction
        self.control_instructions = defaultdict(list)     # Key: label, Value: [ instruction, ]
                                                          # A list contains multiple instructions that jump to the same label.

        # For parsing multiple switch instructions and labels
        self.switch_labels = {}        # Key: label, Value: label data
        self.switch_instructions = {}  # Key: label, Value: switch data

        # For parsing multiple array instructions and labels
        self.fill_array_data_instructions = defaultdict(list)  # Key: label, value: [ fill_array_data, ]

        # For identifying whether each instruction is in a try-catch block.
        # If not in a block, the level is 0.
        self.try_catch_level = 0

    def run(self):
        """
        Parse instructions in the given method.
        """
        # Count method reference number in the give method.
        reference_num = 0

        body_starts_at = self.method_data.start_at + 2
        for i in range(body_starts_at, self.method_data.end_at):
            line = self.code[i].lstrip()
            inst = Utils.get_instruction(line)
            if (inst in opcode_mapping.keys()):
                # The line contains an instruction
                self.instructions[i] = opcode_mapping[inst].run(num=i, line=line,
                                                           instructions=self.instructions,
                                                           super_class=self.parent,
                                                           classes=self.classes,
                                                           categorized=self.categorized,
                                                           try_catch_level=self.try_catch_level)

                # If the instruction is invoke-kind and not counted, increment the reference counter
                if (self.instructions[i].kind == 'invoke'):
                    reference_num += 1
                    # referenced = instructions[i].class_name+instructions[i].method_name
                    # if (referenced not in self.referenced_methods):
                    #     reference_num += 1
                    #     self.referenced_methods.append(referenced)

                # TODO: move below methods to opcode parsers.
                # Matching parsed results of multiple instructions
                self.match_move_result_and_source(self.instructions[i])

                # Find actual destinations of label jumps
                self.resolve_labels_next_instruction(self.instructions[i])

                # Match instructions (i.e., 'if' and 'goto') with labels
                self.match_control_instruction_to_labels(self.instructions[i])

                # Save switch instructions for resolving their switch_data
                self.save_switch_instruction(self.instructions[i])

                # Save fill_array_data instructions for resolving their array_data
                self.save_fill_array_data(self.instructions[i])

                # Count potential taint sources and sinks
                self.count_potential_taint_sources_and_sinks(self.instructions[i])

            elif (inst.split('_')[0] in label_mapping.keys()):
                # The line contains a label
                self.instructions[i] = label_mapping[inst.split('_')[0]].run(num=i, line=line,
                                                                             classes=self.classes,
                                                                             code=self.code)

                # Match labels with instructions (i.e., 'if' and 'goto')
                self.match_label_to_control_instructions(self.instructions[i])

                # Save the control label to resolve the inst's next instruction
                self.save_control_label(self.instructions[i])

                # Save and match switch labels and data labels to previously found switch instructions
                self.save_and_match_switch_labels_and_instructions(self.instructions[i])

                # Match array_data label to previously found fill_array_data instructions
                self.match_array_data_to_fill_array_data(self.instructions[i])

                # Update the try_catch_level
                self.update_try_catch_level(self.instructions[i])

                # Update goto label number
                self.update_goto_label_num(self.instructions[i])

            if (i in self.instructions):
                # Update the found instruction's or label's in_try_block flag
                self.instructions[i].in_try_block = True if (self.try_catch_level > 0) else False

        return reference_num

    def match_move_result_and_source(self, inst):
        """
        Match move-result and its sources (invoke and filled-new-array) instructions.
        """
        if (inst.kind in ['invoke', 'filled_new_array']):
            # Save the new inst as the most recent mr source
            self.most_recent_mr_source = inst

        elif (inst.kind == 'move_result'):
            assert self.most_recent_mr_source is not None, f'Failed to match {inst = }'

            # Update move-result's data
            inst.source = self.most_recent_mr_source
            inst.destination_data_type = self.most_recent_mr_source.ret_type
            if (inst.destination_data_type in numeric_types_64):
                inst.destination_pair = f'{inst.destination[0]}{int(inst.destination[1:])+1}'

            # Update the source's data
            self.most_recent_mr_source.move_result = inst
            self.most_recent_mr_source = None

    def resolve_labels_next_instruction(self, inst):
        """
        Find each label's next instruction.
        The instruction is next to a label if the label's next_instruction is empty.
        """
        if (isinstance(inst, CondLabel) or
            isinstance(inst, GotoLabel) or
            isinstance(inst, SwitchLabel) or
            isinstance(inst, SwitchDataLabel) or
            isinstance(inst, ArrayLabel)
           ):
            raise Exception(f'{inst = } should not be a label')

        for label_data in self.control_labels.values():
            if (label_data.next_instruction is None):
                label_data.next_instruction = inst

    def match_control_instruction_to_labels(self, inst):
        """
        Match control instruction to previously found labels.
        """
        if (isinstance(inst, OpIf) or
            isinstance(inst, OpIfz) or
            isinstance(inst, OpGoto)
           ):
            # Check if the corresponding label is previously found
            if (inst.label in self.control_labels.keys()):
                # The label is found, so update the inst
                inst.destination = self.control_labels[inst.label]
            else:
                # The label is not found, so save the inst
                self.control_instructions[inst.label].append(inst)

    def match_label_to_control_instructions(self, inst):
        """
        Match label to previously found instructions.
        The argument inst should be a label (i.e., should has a field "label").
        """
        if (inst.kind in ['cond_label', 'goto_label']):
            # Find control instructions jumping to the inst label
            matched = self.control_instructions.get(inst.label, [])
            for control_inst_data in matched:
                control_inst_data.destination = inst

            # Remove the matched control instructions
            self.control_instructions.pop(inst.label, None)

    def save_control_label(self, inst):
        """
        Save the label if it is a control label.
        The argument inst should be a label.
        """
        if (isinstance(inst, CondLabel) or
            isinstance(inst, GotoLabel)
           ):
            # Labels should not be duplicate
            assert inst.label not in self.control_labels.keys(), f'{inst = }, {self.control_labels = }'

            self.control_labels[inst.label] = inst

    def save_switch_instruction(self, inst):
        """
        Save switch instructions for resolving their switch_data.
        Assuming that switch_data always comes later than switch instructions.
        """
        if (inst.kind == 'switch'):
            self.switch_instructions[inst.data_label] = inst

    def save_and_match_switch_labels_and_instructions(self, inst):
        """
        Save switch labels.
        Match switch data to previously found switch labels and instructions.
        """
        if (inst.kind == 'switch_label'):
            self.switch_labels[inst.label] = inst
        elif (inst.kind == 'switch_data_label'):
            switch_inst = self.switch_instructions.get(inst.label, None)

            assert switch_inst is not None, f'switch instruction not found for switch data'

            for case_value, target_label in inst.targets.items():
                switch_inst.targets[case_value] = self.switch_labels[target_label]

    def save_fill_array_data(self, inst):
        """
        Save fill_array_data instructions for resolving their array_data.
        Assuming that array_data always comes later than fill_array_data instructions.
        """
        if (inst.kind == 'fill_array_data'):
            self.fill_array_data_instructions[inst.label].append(inst)

    def count_potential_taint_sources_and_sinks(self, inst):
        """
        Count potential taint sources and sinks.
        """
        if (inst.kind == 'invoke'):
            # Count sources
            is_source, _ = SourceApiDetector.detect_sources(inst, self.taint_sources)
            is_reflective_call = ReflectiveCallDetector.detect_reflective_calls(inst)
            if (is_source or is_reflective_call):
                self.method_data.num_potential_sources += 1
            else:
                # Count sinks
                is_sink = SinkApiDetector.detect_sink_api(inst.class_name, inst.method_name, self.taint_sinks, support_combination=False)
                if (is_sink):
                    self.method_data.num_potential_sinks += 1

    def match_array_data_to_fill_array_data(self, inst):
        """
        Match array_data to previously saved fill_array_data instructions.
        """
        if (inst.kind == 'array_label'):
            # Find fill_array_data instructions referencing array_data of the label
            matched = self.fill_array_data_instructions.get(inst.label, [])
            for fill_array_data in matched:
                fill_array_data.array_data = inst

            # Remove the matched instructions
            self.fill_array_data_instructions.pop(inst.label, None)

    def update_try_catch_level(self, inst):
        """
        Detect try_start and try_end labels and update the level.
        """
        if (inst.kind == 'try_start_label'):
            self.try_catch_level += 1
        elif (inst.kind == 'try_end_label'):
            self.try_catch_level -= 1

    def update_goto_label_num(self, inst):
        """
        Update the method's goto label number.
        """
        if (inst.kind == 'goto_label'):
            label_num = int(inst.label.split('_')[-1], 16)
            if (label_num > self.method_data.goto_label_num):
                self.method_data.goto_label_num = label_num
