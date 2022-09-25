import logging

logger = logging.getLogger(name=__name__)


# Exceptions for ContextManager

class StackIsEmptyException(Exception):
    """
    Raised when no stack frame left in a call stack.
    """
    pass


# Exceptions for PCController

class NewMethodInvokedException(Exception):
    """
    Raised when a new method of app is invoked.
    """
    pass

class NewReflectionException(Exception):
    """
    Raised when a method is invoked by reflection.
    TODO: remove this if not used.
    """
    pass

class NewThreadException(Exception):
    """
    Raised when a new thread is generated.
    TODO: remove this if not used.
    """
    pass

class MethodEmulationCompletedException(Exception):
    """
    Raised when a method of the app is finished.
    """
    pass

class LogPointException(Exception):
    """
    Raised when the emulator reaches a log point.
    """
    pass

class ExceptionThrownException(Exception):
    """
    Raised when the emulator detects a throw instruction.
    """
    pass

class ExceptionOccurException(Exception):
    """
    Raised when the emulator detects an exception-occurring condition, such as array index ouf of range.
    """
    pass


# Exceptions for ValueResolver

class ClinitInvokedException(Exception):
    """
    Raised when accessing a static field of the app's class not initiliazed yet.
    """
    pass
