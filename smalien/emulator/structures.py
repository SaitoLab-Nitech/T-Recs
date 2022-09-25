from typing import Dict
from collections import defaultdict
from dataclasses import dataclass, field

from .vm_manager.structures import VM
from .interpreter.value_manager.structures import Value

@dataclass
class DataFile:
    """
    Represent a file.
    """
    name: int

@dataclass
class Storage:
    """
    Represent a storage that can be accessed globally.
    """
    files: Dict[str, DataFile] = field(default_factory=dict)

@dataclass
class EmulationData:
    """
    Store data of the emulation
    """
    # VM data
    vms: Dict[str, VM] = field(default_factory=dict)

    # Global data
    # Instances
    instances: Dict[str, list] = field(default_factory=lambda: defaultdict(list))
    # Static fields
    static_fields: Dict[str, Value] = field(default_factory=dict)

    # Intent data
    intent_data: Dict[str, Value] = field(default_factory=dict)

    # Storage
    # Currently not used
    storage: Storage = None
