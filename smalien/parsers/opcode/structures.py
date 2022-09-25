from typing import Dict
from dataclasses import dataclass, field


@dataclass
class Opcode:
    """
    Base class of Op* classes.
    """
    # Identifier
    num: int = None          # The line number of the instruction

    # Instruction info
    instruction: str = None
    in_try_block: bool = False  # Indicate that the instruction is in try block.
                                # It is initially implemented for throw instruction.
                                # Currently, it is for all instructions and labels.

    # Flag
    logging: bool = False


@dataclass
class OpNop(Opcode):
    """
    Contain a nop instruction's data.
    """
    # Group
    kind: str = 'nop'


@dataclass
class OpMethodHead(Opcode):
    """
    Contain a method head's data.
    """
    # Group
    kind: str = 'method_head'

    # Specification
    parameters: list = field(default_factory=list)  # Contain parameters with maintaining the order.
    parameter_data_types: Dict[str, str] = field(default_factory=dict)  # Contain parameters' data types
    is_constructor: bool = None  # Flag suggesting the method is a constructor
    attribute: str = None        # Attribute of the method (native, abstract, static, normal)

@dataclass
class OpMethodTail(Opcode):
    """
    Contain a method tail's data.
    """
    # Group
    kind: str = 'method_tail'


@dataclass
class OpInvoke(Opcode):
    """
    Contain an invoke-kind instruction's data.
    """
    # Group
    kind: str = 'invoke'

    # Specification
    # Names
    class_name: str = None
    method_name: str = None

    # Invocation
    invoke_static: bool = None                         # Indicate that invoked method is static
    invoke_constructor: bool = None                    # Indicate that invoked method is a constructor
    invoke_super_constructor: bool = None              # Indicate that invoked method is a super class's constructor
    method_kind: str = None                            # E.g., reflection or thread
    in_app: bool = None                                # Flag suggesting whether the method is implemented in app

    # Arguments
    arguments: list = field(default_factory=list)  # Argument list with maintaining the order.
    argument_data_types: Dict[str, str] = field(default_factory=dict)  # Contain arguments' data types
    arguments_without_64bit_pairs: list = field(default_factory=list)  # Argument list without 64-bit pairs.

    # Return value
    ret_type: str = None        # The data type of the return value
    move_result: Opcode = None  # Data of the move-result immediately after this
                                # Initialized with a OpMoveResult,
                                # which is a dummy opecode with no destination.
                                # Overwritten with a corresponding move-result if it exists

    # Runtime information
    reflection_source: str = None  # Save taint source information when the invoked method is detected as a reflection of a source API
    reflective_call_class: str = None  # Save resolved reflective-method-call's class name
    reflective_call_method: str = None  # Save resolved reflective-method-call's method name
    reflective_field_name: str = None  # Save resolved reflectively-accessed field's name
    reflective_field_attr: str = None  # Save resolved reflectively-accessed field's attribute

    taint_to_ret: str = None       # At invoke execution, this field holds a taint data that will be propagated to destination at move-result execution.
                                   # Without this field, a taint propagator cannot access to arguments' taints at move-result execution if the argument and destination registers are same.
                                   # TODO: Its data type should be dataclasses Taint, not str.
    base_object: str = None        # At invoke execution, this field holds the base object's data, being used by value-based propagator at move-result execution

    is_sink: bool = False          # Indicate whether the invoked method is a sink.

@dataclass
class OpMoveResult(Opcode):
    """
    Contain a move-result instruction's data.
    """
    # Group
    kind: str = 'move_result'

    # Specification
    # Source
    source: Opcode = None  # The line of the most recent invoke or filled_new_array

    # Destination
    destination: str = None  # Destination register
    destination_pair: str = None  # Set if the destination data type is J or D
    destination_data_type: str = None  # The register's data type
    castable_to: str = None     # To which the register is castable


#
# Array Operation
#

@dataclass
class OpAget(Opcode):
    """
    Contain an aget instruction's data.
    """
    # Group
    kind: str = 'aget'

    # Specification
    destination: str = None  # Destination register
    array: str = None        # Array register
    index: str = None        # Index register
    index_data_type: str = None  # Data type of the index register

@dataclass
class OpAput(Opcode):
    """
    Contain an aput instruction's data.
    """
    # Group
    kind: str = 'aput'

    # Specification
    source: str = None   # Source register
    array: str = None    # Array register
    index: str = None    # Index register
    index_data_type: str = None  # Data type of the index register

@dataclass
class OpNewArray(Opcode):
    """
    Contain a new-array instruction's data.
    """
    # Group
    kind: str = 'new_array'

    # Specification
    # Array
    array: str = None            # Register holding the array
    array_data_type: str = None  # Data type of the array
    # Item
    item_data_type: str = None   # Data type of items in the array
    # Size
    size: str = None             # Register holding the array size
    size_data_type: str = None   # Data type of the size

@dataclass
class OpFillArrayData(Opcode):
    """
    Contain a fill-array-data instruction's data.
    """
    # Group
    kind: str = 'fill_array_data'

    # Specification
    array: str = None          # Register holding the array
    label: str = None          # Label pointing the array_data
    array_data: Opcode = None  # Data being stored into the array

@dataclass
class OpFilledNewArray(Opcode):
    """
    Contain a filled-new-array instruction's data.
    """
    # Group
    kind: str = 'filled_new_array'

    # Specification
    arguments: list = field(default_factory=list)  # Contain arguments with maintaining the order.
    ret_type: str = None     # The data type of the return value
    move_result: Opcode = None  # An object of the move-result immediately after this

@dataclass
class OpArrayLength(Opcode):
    """
    Contain an array-length instruction's data.
    """
    # Group
    kind: str = 'array_length'

    # Specification
    # Register
    array: str = None        # Array register
    destination: str = None  # Destination register
    # Data type
    destination_data_type: str = None # Destination data type


@dataclass
class OpConst(Opcode):
    """
    Containt a const instruction's data.
    """
    # Group
    kind: str = 'const'

    # Specification
    value: str = None     # The given literal value
    # Destination
    destination: str = None  # Destination register
    data_type: str = None    # Data type of the register

@dataclass
class OpConstString(Opcode):
    """
    Containt a const-string instruction's data.
    """
    # Group
    kind: str = 'const_string'

    # Specification
    value: str = None     # The given literal value
    # Destination
    destination: str = None  # Destination register
    data_type: str = None    # Data type of the register

@dataclass
class OpConstClass(Opcode):
    """
    Containt a const-class instruction's data.
    """
    # Group
    kind: str = 'const_class'

    # Specification
    class_name: str = None     # The given class name
    value: str = None          # Value of the register
    # Destination
    destination: str = None    # Destination register
    data_type: str = None      # Data type of the register

@dataclass
class OpNewInstance(Opcode):
    """
    Contain a new-instance instruction's data.
    """
    # Group
    kind: str = 'new_instance'

    # Specification
    destination: str = None  # Destination register
    class_name: str = None   # Data type of the register
    initialized: bool = False  # Indicate whether the register is initialized.
                               # True if a constructor is called at the instruction.

@dataclass
class OpInstanceOf(Opcode):
    """
    Contain an instance-of instruction's data.
    """
    # Group
    kind: str = 'instance_of'

    # Specification
    # Source
    source: str = None         # Source register
    # Destination
    destination: str = None    # Destination register
    destination_data_type: str = None  # Data type of the register

    class_name: str = None

@dataclass
class OpMove(Opcode):
    """
    Contain a move instruction's data.
    """
    # Group
    kind: str = 'move'

    # Specification
    source: str = None
    destination: str = None

@dataclass
class OpReturn(Opcode):
    """
    Contain a return instruction's data.
    """
    # Group
    kind: str = 'return'

    # Specification
    register: str = None      # Return value register

@dataclass
class OpMonitorEnter(Opcode):
    """
    Contain a monitor-enter instruction's data.
    """
    # Group
    kind: str = 'monitor_enter'

    # Specification
    register: str = None    # Register containing an object

@dataclass
class OpMonitorExit(Opcode):
    """
    Contain a monitor-exit instruction's data.
    """
    # Group
    kind: str = 'monitor_exit'

    # Specification
    register: str = None    # Register containing an object

@dataclass
class OpCheckCast(Opcode):
    """
    Contain a check-cast instruction's data.
    The instruction checks whether the register can be cast to data_type.
    """
    # Group
    kind: str = 'check_cast'

    # Specification
    register: str = None      # Register to be checked
    class_name: str = None    # Reference to the class to be used for cast checking

    move_result_matched: bool = False  # Indicate whether there is a matched move-result


#
# Setter and Getter instructions
#

@dataclass
class OpIget(Opcode):
    """
    Contain an iget instruction's data.
    """
    # Group
    kind: str = 'iget'

    # Specification
    # Source
    source: str = None            # Source register
    source_data_type: str = None  # Data type of the register
    # Destination
    destination: str = None            # Destination register
    destination_data_type: str = None  # Data type of the register
    castable_to: str = None            # to which destination register is castable

    field: str = None         # <class_name>-><field_name>
                              # To distinguish fields of sub and super classes,
                              # Use class_name as a part of the field's name.
                              # Class name is also saved as the destination register's type

    in_app: bool = False      # Indicate the field is implemented in the app

@dataclass
class OpIput(Opcode):
    """
    Contain an iput instruction's data.
    """
    # Group
    kind: str = 'iput'

    # Specification
    # Source
    source: str = None            # Source register
    source_data_type: str = None  # Data type of the register
    # Destination
    destination: str = None            # Destination register
    destination_data_type: str = None  # Data type of the register

    field: str = None         # <class_name>-><field_name>
                              # To distinguish fields of sub and super classes,
                              # Use class_name as a part of the field's name.
                              # Class name is also saved as the destination register's type

@dataclass
class OpSget(Opcode):
    """
    Contain a sget instruction's data.
    """
    # Group
    kind: str = 'sget'

    # Specification
    # Destination
    destination: str = None            # Destination register
    destination_data_type: str = None  # Data type of the register
    castable_to: str = None            # to which destination register is castable

    class_name: str = None    # Field's class name

    default_value: str = None  # Field's default value hard-coded in the smali.

    field: str = None         # <class_name>-><field_name>

    in_app: bool = False      # Indicate the field is implemented in the app
    clinit_implemented: bool = False  # Indicate clinit is implemented in the class

@dataclass
class OpSput(Opcode):
    """
    Contain a sput instruction's data.
    """
    # Group
    kind: str = 'sput'

    # Specification
    # Source
    source: str = None            # Source register
    source_data_type: str = None  # Data type of the register

    class_name: str = None    # Field's class name

    field: str = None         # <class_name>-><field_name>

    in_app: bool = False    # Indicate the field is implemented in the app

#
# Unary and Binary instructions
#

@dataclass
class OpUnop(Opcode):
    """
    Contain an unop vA, vB instruction's data.
    """
    # Group
    kind: str = 'unop'

    # Specification
    # Source
    source: str = None      # First source register
    source_data_type: str = None  # Data type of the register
    # Destination
    destination: str = None  # Destination register
    destination_data_type: str = None  # Data type of the register

    expression: str = None   # Semantics to calculate the result

    is_converter: bool = None  # Indicate the inst is a converter

@dataclass
class OpBinop(Opcode):
    """
    Contain a binop vAA, vBB, vCC instruction's data.
    """
    # Group
    kind: str = 'binop'

    # Specification
    # Registers
    source1: str = None      # First source register
    source2: str = None      # Second source register
    destination: str = None  # Destination register
    data_type: str = None    # Data type of the registers

    expression: str = None   # Semantics to calculate the result

@dataclass
class OpBinopLit8(Opcode):
    """
    Contain a binop/lit8 vAA, vBB, #+CC instruction's data.
    """
    # Group
    kind: str = 'binoplit8'

    # Specification
    # Registers
    source: str = None       # Source register
    literal: str = None      # Signed int constant (8 bits)
    destination: str = None  # Destination register
    data_type: str = None    # Data type of the registers

    expression: str = None   # Semantics to calculate the result

@dataclass
class OpBinop2addr(Opcode):
    """
    Contain a binop/2addr vA, vB instruction's data.
    """
    # Group
    kind: str = 'binop2addr'

    # Specification
    # Registers
    source2: str = None      # Source register
    destination: str = None  # Destination register
    data_type: str = None    # Data type of the registers

    expression: str = None   # Semantics to calculate the result


#
# Cmp instructions
#

@dataclass
class OpCmp(Opcode):
    """
    Contain a cmpkind vAA, vBB, vCC instruction's data.
    """
    # Group
    kind: str = 'cmp'

    # Specification
    # Source
    source1: str = None      # First source register
    source2: str = None      # Second source register
    source_data_type: str = None  # Data type of the register
    # Destination
    destination: str = None  # Destination register
    destination_data_type: str = None  # Data type of the register


#
# Control instructions
#

@dataclass
class OpIf(Opcode):
    """
    Contain if-test instructions' data.
    """
    # Group
    kind: str = 'if'

    # Specification
    register_1: str = None           # First register to test
    register_2: str = None           # Second register to test
    expression: str = None           # Expression
    label: str = None                # Branch's label
    destination: Opcode = None       # Branch's instruction data

@dataclass
class OpIfz(Opcode):
    """
    Contain if-testz instructions' data.
    This is different from if-test because this takes only one register.
    TODO: Investigate whether OpIf and OpIfz should be a same kind.
    """
    # Group
    kind: str = 'ifz'

    # Specification
    register: str = None             # register to test
    expression: str = None           # Expression
    label: str = None                # Branch's label
    destination: Opcode = None       # Branch's instruction data

@dataclass
class OpGoto(Opcode):
    """
    Contain goto instruction's data.
    """
    # Group
    kind: str = 'goto'

    # Specification
    label: str = None           # Branch's label
    destination: Opcode = None  # Branch's instruction data

@dataclass
class OpSwitch(Opcode):
    """
    Contain switch instructions' data.
    TODO: Investigate whether sswitch and pswitch should be a same kind.
    """
    # Group
    kind: str = 'switch'

    # Specification
    register: str = None                                      # register to test
    data_label: str = None                                    # Switch data label
    targets: Dict[int, Opcode] = field(default_factory=dict)  # Branch targets data


#
# Labels
# Group: label
#

@dataclass
class CondLabel(Opcode):
    """
    Contain :cond labels' data.
    """
    # Group
    kind: str = 'cond_label'

    # Specification
    label: str = None                # Name of label
    next_instruction: Opcode = None  # Instruction next to this label
    extra_trampoline: bool = False   # Extra trampoline for long-distance jumpers

@dataclass
class GotoLabel(Opcode):
    """
    Contain :goto labels' data.
    """
    # Group
    kind: str = 'goto_label'

    # Specification
    label: str = None                # Name of label
    next_instruction: Opcode = None  # Instruction next to this label

@dataclass
class SwitchLabel(Opcode):
    """
    Contain switch labels' data.
    """
    # Group
    kind: str = 'switch_label'

    # Specification
    label: str = None                # Name of label

@dataclass
class SwitchDataLabel(Opcode):
    """
    Contain switch data labels' data.
    """
    # Group
    kind: str = 'switch_data_label'

    # Specification
    label: str = None                # Name of label
    targets: Dict[int, str] = field(default_factory=dict)  # Key: case value, Value: target label

@dataclass
class ArrayLabel(Opcode):
    """
    Contain :array labels' data.
    """
    # Group
    kind: str = 'array_label'

    # Specification
    label: str = None                               # Name of label
    array_data: list = field(default_factory=list)  # Data
    element_width: str = None        # Number of bytes in each element


#
# Try and catch
#

@dataclass
class OpThrow(Opcode):
    """
    Contain throw instructions' data.
    """
    # Group
    kind: str = 'throw'

    # Specification
    register: str = None                                      # register containing an Exception

@dataclass
class OpMoveException(Opcode):
    """
    Contain move-exception instruction's data.
    """
    # Group
    kind: str = 'move_exception'

    # Specification
    destination: str = None   # Destination register
    destination_data_type: str = None  # Data type of the register

@dataclass
class TryStartLabel(Opcode):
    """
    Contain :try_start_* labels' data.
    """
    # Group
    kind: str = 'try_start_label'

    # Specification
    label: str = None                # Name of label
    try_end: Opcode = None           # Corresponding :try_end_* label data
    catch_data: Opcode = None        # Corresponding .catch data

@dataclass
class TryEndLabel(Opcode):
    """
    Contain :try_end_* labels' data.
    """
    # Group
    kind: str = 'try_end_label'

    # Specification
    label: str = None                # Name of label

@dataclass
class CatchData(Opcode):
    """
    Contain .catch data.
    """
    # Group
    kind: str = 'catch_data'

    # Specification
    exception: str = None            # Exception to be catched
    try_start_label: str = None      # Corresponding :try_start_* label name
    try_end_label: str = None        # Corresponding :try_end_* label name
    target: str = None               # Target :catch_* label name

@dataclass
class CatchLabel(Opcode):
    """
    Contain :catch_* labels' data.
    """
    # Group
    kind: str = 'catch_label'

    # Specification
    label: str = None                # Name of label
    move_exception: OpMoveException = None  # The move-exception right after the label
