from typing import Dict, Type
from collections import defaultdict
from dataclasses import dataclass, field

from ..interpreter.value_manager.structures import Value


@dataclass
class StackFrame:
    """
    Contain a method's information and local registers.
    """
    # Identifier
    clss: str       # The frame's class.
    method: str     # The frame's method.

    # State
    pc: int         # Line number of currently executed instruction.
    previous: Type['StackFrame'] = None  # Point to the previous frame.
    after_invocation: bool = False       # Indicate that an invocation has been finished
                                         # This virtually reproduces two lines at one line of method invocation

    # Data
    registers: Dict[str, Value] = field(default_factory=dict)
    new_values: Dict[str, str] = field(default_factory=dict)

@dataclass
class StackFrameEntry:
    """
    This is the first frame in a call stack.
    A real frame of an app's method points this frame as the previous.
    """
    # Identifier
    clss: str = 'ENTRY'       # The frame's class.
    method: str = 'ENTRY'     # The frame's method.

    # State
    pc: int = None

@dataclass
class VMOrder:
    """
    Contain information for ordering VMManager to start.
    """
    clss: str
    method: str
    line: int = None
    pid: int = None
    tid: int = None
    values: Dict[str, str] = field(default_factory=dict)
    logging: bool = False
    timestamp: str = None
    last_record: bool = False

@dataclass
class VM:
    """
    Store data of a virtual machine.
    """
    # Identifier
    ptids: str
    pid: int
    tid: int

    #
    # Local data
    #
    call_stack: list = field(default_factory=list)

    # This is used to keep instances maintained by the Android runtime.
    # This is a pointer to the EmulationData.instance_fields.
    # Key is instance's representaion, and value is an array of instance's Value.
    # An instance is saved in an array to detect duplication of representation.
    instances: Dict[str, list] = field(default_factory=lambda: defaultdict(list))

    # Contain a thrown exception's value
    # Used to propagate the value from throw to move-exception instructions
    exception_value: Value = None

    #
    # Global data
    #
    # Static fields, which can be globally accessed
    # This is a pointer to the EmulationData.static_fields
    # Key is "class->field" string
    static_fields: Dict[str, Value] = field(default_factory=dict)

    # Intent data used to track data stored in intents
    # This is a pointer to the EmulationData.intent_data
    # Key is a value stored in an intent
    intent_data: Dict[str, Value] = field(default_factory=dict)
