from .payload_generators import *


"""
To map between instructions and generators, add information to the two mappings below.
"""

# TODO: Move this to the parent directory.

# Mapping between instructions and pyaload generators
payload_mapping = {
    'method_head': PayloadMethodHeadGenerator,
    'invoke': PayloadInvokeGenerator,
    # 'move_result': PayloadMoveResultGenerator,
    'instance_of': PayloadInstanceOfGenerator,

    #  Should consider instructions appear right after catch labels
    #    usually monitor-exit and move-exception appears.
    #      - If the logging point is right before move-exception, some verification errors occur
    #          because it adds a path where the move-exception dst has not been updated.
    #      - If the logging point is right after move-exception, some verification errors occur
    #          because it adds a path where the move-exception dst is updated. (in co_happybits)
    'catch_label': PayloadCatchLabelGenerator,

    # iget logging is required to log field values of a transferred instance
    'iget': PayloadGetterGenerator,
    'sget': PayloadGetterGenerator,

    # Instrument without value logging.
    # sput can trigger clinit, so the sput execution timing should be recorded.
    'sput': PayloadSetterGenerator,

    # new-instance can trigger clinit, so the new-instance execution timing should be recorded.
    'new_instance': PayloadNewInstanceGenerator,

    'check_cast': PayloadCheckCastGenerator,

    # Logs the object's identifier for method parameter matching.
    'const_string': PayloadConstStringGenerator,

    # For observing the timing of code
    'monitor_enter': PayloadMonitorEnterGenerator,

    # The const-class destination has its object identifier.
    'const_class': PayloadConstClassGenerator,

    # Since it is dificcult to log all arrays' elements, arrays' lengths must be logged.
    'array_length': PayloadArrayLengthGenerator,

    # Modify long-distance jumpers, if and goto instructions
    'if': PayloadIfGenerator,
    'ifz': PayloadIfGenerator,
    'goto': PayloadGotoGenerator,

    # # For debugging purpose
    # # Their logs are ignored by runtime_log_manager in emulation
    # 'const': PayloadConstGenerator,
    # 'binoplit8': PayloadBinopLit8Generator,
}

# Mapping between instructions and value-logging flags
# To enable/disable the value logging for instructions, set True/False
value_logging_mapping = {
    'method_head': True,
    'invoke': True,
    # 'move_result': True,

    'instance_of': True,

    'catch_label': True,

    'iget': True,
    'sget': True,
    'sput': False,

    'check_cast': True,

    'const_string': True,

    'monitor_enter': False,

    'const_class': True,

    'new_instance': False,

    'array_length': True,

    'if': False,
    'ifz': False,
    'goto': False,

    # # For debugging purpose
    # 'const': True,
    # 'binoplit8': True,
}
