from typing import Dict
from dataclasses import dataclass, field


@dataclass
class Payload:
    """
    Base class of Payload* classes.
    """
    # Identifier
    num: int         # The line number after that code is injected

@dataclass
class PayloadLocals(Payload):
    """
    Contain a .locals line to be injected.
    """
    # Instrumentation recipe
    code: str   # .locals line to be injected
    increase: int   # Number of added registers

@dataclass
class PayloadMove(Payload):
    """
    Contain a move instruction to be injected.
    """
    # Instrumentation recipe
    code: str   # move to be injected

@dataclass
class PayloadMoveResult(Payload):
    """
    Contain a move-result instruction to be injected.
    """
    # Instrumentation recipe
    code: str   # move-result to be injected

@dataclass
class PayloadMoveException(Payload):
    """
    Contain a move-exception instruction to be injected.
    """
    # Instrumentation recipe
    code: str   # move-exception to be injected

@dataclass
class PayloadGoto(Payload):
    """
    Contain a goto instruction to be injected.
    """
    # Instrumentation recipe
    code: str   # goto instruction to be injected

@dataclass
class PayloadGotoExtra(Payload):
    """
    Contain an extra goto instruction to be injected.
    """
    # Instrumentation recipe
    code: str   # extra goto instruction to be injected

@dataclass
class PayloadGotoLabel(Payload):
    """
    Contain a goto label instruction to be injected.
    """
    # Instrumentation recipe
    code: str   # goto label to be injected

@dataclass
class PayloadGotoLabelExtra(Payload):
    """
    Contain an extra goto label instruction to be injected.
    """
    # Instrumentation recipe
    code: str   # extra goto label to be injected

@dataclass
class PayloadCondLabel(Payload):
    """
    Contain a cond label instruction to be injected.
    """
    # Instrumentation recipe
    code: str   # cond label to be injected

@dataclass
class PayloadLogging(Payload):
    """
    Payload of a logging method.
    """
    # Instruction
    instruction_kind: str  # The type of the target instruction

    # Instrumentation recipe
    invoke: str      # SmalienMethod-invoking code to be injected
    definition: str  # SmalienMethod-defining code to be injected
    class_name: str  # Name of class in that the code is defined
    smali_name: str  # Name of smali file in that the class is written

@dataclass
class PayloadDummyReturnedValue(Payload):
    """
    Contain a dummy returned value instruction to be injected.
    """
    # Instrumentation recipe
    code: str   # const-string to be injected
