from typing import Dict
from dataclasses import dataclass, field

# TODO: Remove this after re-organized project
# from ..value_manager.structures import Value
# from ....parsers.opcode.structures import Opcode


@dataclass
class Taint:
    """
    Represent a taint tag.
    """
    # Tag value
    tag: int = 0

    # Sources of the tracked information
    sources: list = field(default_factory=list)

    # Values at the sources
    values: list = field(default_factory=list)

    # For flow logging
    flow_details: list = field(default_factory=list)

# TaintSource and TaintSink are urrently not used
# @dataclass
# class TaintSource:
#     """
#     Represent a taint source.
#     """
#     name: str = None         # Type of sensitive information
#     clss: str = None
#     method: str = None
#     num: int = None
#     # instruction: str = None  # Detected instruction
#     source_class: str = None
#     source_method: str = None
# 
# @dataclass
# class TaintSink:
#     """
#     Represent a taint sink.
#     """
#     # TODO: Fix this type issue.
#     clss: str = None
#     method: str = None
#     num: int = None
#     sink_class: str = None
#     sink_method: str = None
#     sink_values: list = field(default_factory=list)
#     # instruction: str = None
#     # registers: str = None
# 
#     sources: set = field(default_factory=set)
#     # instruction: Opcode = None
#     # registers: Dict[str, Value] = field(default_factory=dict)

@dataclass
class TaintHistory:
    """
    Represent a taint history (i.e., information flow).
    """
    name: str

@dataclass
class TaintResults:
    """
    Store taint results.
    """
    sources: list = field(default_factory=list)
    sinks: list = field(default_factory=list)
    histories: list = field(default_factory=list)
