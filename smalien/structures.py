from typing import Dict
from collections import defaultdict
from dataclasses import dataclass, field

from .parsers.opcode.structures import Opcode


@dataclass
class AppMethod:
    """
    Store data of a method.
    """
    # Identifier
    name: str = None             # Name of the method

    # Method info
    attribute: str = None        # The attribute of the method
    is_constructor: bool = None  # Flag suggesting the method is a constructor
    parameters: list = field(default_factory=list)    # Parameter list maintaining the order
    parameter_data_types: Dict[str, str] = field(default_factory=dict)  # Dict of parameters and data types
    local_reg_num: int = None   # The number of local registers
    ret_type: str = None        # Type of return value
    goto_label_num: int = None  # Number of goto labels in the method

    # Code
    start_at: int = None        # Line number of the method's head
    end_at: int = None          # Line number of the method's tail

    # Data
    instructions: Dict[int, Opcode] = field(default_factory=dict)

    # Instrumentation
    implemented: bool = None    # Show whether the method has bytecode implementation

    # Number of taint sources and sinks invoked within the method
    num_potential_sources: int = 0
    num_potential_sinks: int = 0

@dataclass
class AppField:
    """
    Store data of a field.
    """
    # Identifiers
    key: str = None
    name: str = None
    data_type: str = None
    default_value: str = None

@dataclass
class AppClass:
    """
    Class's data.
    """
    # Identifiers
    cid: int = None     # Identifier of the class
    name: str = None    # Name of the class

    # Path
    path: str = None    # Absolute path to the class's smali file

    # Attribute
    is_abstract: bool = None  # Whether the class is abstract

    # Inheritance info
    parent: str = None  # Super class of the class
    family: set = field(default_factory=set)  # Set of inherited classes

    # Code
    linage: int = None  # The number of lines of the code
    code: list = field(default_factory=list)

    # Data
    fields: Dict[str, Dict] = field(default_factory=dict)
    methods: Dict[str, AppMethod] = field(default_factory=dict)

    # Instrumentation
    ignore: bool = False     # If true, the class is not instrumented, and its methods are considered as API
    dex_id: str = None       # Dex ID
    path_in_dex: str = None  # Smali file's path in Dex
    payloads: Dict[int, list] = field(default_factory=lambda: defaultdict(list))
    reference_num: int = 0  # Used by Relocator

    # Special method flags
    clinit_implemented: bool = False
    clinit_invoked: bool = False

    # Flag indicating toString() is overridden
    tostring_implemented: bool = False

    # Callback methods
    onlowmemory: AppMethod = None  # Save the class's overridden onLowMemory method.

@dataclass
class App:
    """
    App's data.
    """
    # Identifier
    apk: str = None               # Path to app's apk
    name: str = None              # App's apk name

    # App's information for instrumentation
    dex_ids: set = field(default_factory=set)   # Dex IDs of the app
    smalien_dex_id: str = None                  # ID of Dex writing smalien logging functions
    resource_decoded: bool = None               # Indicate whether resources are decoded
                                                # Used when injecting permissions to AndroidManifest.xml
    reference_num: int = 0                      # Number of method references in the app

    # App's information for exercising
    package: str = None           # App's package name
    # App's components
    # Format: <package_name>/<component_name>
    services: list = field(default_factory=list)     # Names of app's services
    receivers: list = field(default_factory=list)    # Names of app's broadcast receivers
    activities: list = field(default_factory=list)   # Names of app's activities

    # Paths
    pickled: str = None            # Path to app's pickled data
    smaliened: str = None          # Path to app's smaliened apk
    unpackaged: str = None         # Path to unpackaged directory
    smalien_log: str = None        # Path to runtime log on a device
    smalien_log_local: str = None  # Path to runtime log on a server
    android_manifest: str = None   # Path to app's AndroidManifest.xml
    logcat_log: str = None         # Path to save logcat log

    # Data
    classes: Dict[str, AppClass] = field(default_factory=dict)   # Name to app's classes
    cids: Dict[int, AppClass] = field(default_factory=dict)      # CID to app's classes

    # Potential taint sources and sinks
    num_potential_sources: int = 0
    num_potential_sinks: int = 0
