from typing import Dict
from dataclasses import dataclass, field

from ..taint_tracker.structures import Taint
from smalien.parsers.opcode.structures import Opcode


@dataclass
class Value:
    """
    Base class for containing a register's value.
    """
    # Information
    value: ...        # This data type can be int, float, or str
    data_type: str

    # Taint data
    taint: Taint = None

@dataclass
class PrimitiveValue(Value):
    """
    Contain a register's primitive value.
    """

@dataclass
class PrimitiveValue64(PrimitiveValue):
    """
    Contain a register's 64-bit primitive value.
    """

@dataclass
class ArrayInstanceValue(Value):
    """
    Contain a register's array instance value.
    """
    # Element information
    element_data_type: str = None  # Data type of elements
    elements: list = field(default_factory=list)

    # Last-invoked information
    last_invoked: Opcode = None  # Keep this instance's last-invoked method information
    last_invoked_arguments: list = field(default_factory=list)

@dataclass
class ClassInstanceValue(Value):
    """
    Contain a register's class instance value.
    """

    # Points to other ArrayInstance and ClassInstance
    # If this instance is tainted, the instances in the list should be tainted
    # Currently not used
    references: list = field(default_factory=list)

    # Class's fields
    fields: Dict[str, Value] = field(default_factory=dict)

    # This instance's last-invoked method
    last_invoked: Opcode = None
    last_invoked_arguments: list = field(default_factory=list)

    # Save OutputStream to support backward taint propagation
    outputstream: Value = None

    # Save values taht could be contained in this instance
    contained_values: Dict[str, Value] = field(default_factory=dict)

    # Keep string data.
    # If the class is not string-data-type, the value will be None.
    string: str = None

@dataclass
class ClassReferenceValue(Value):
    """
    Contain a reference to the class, generated by const-class instruction.
    """