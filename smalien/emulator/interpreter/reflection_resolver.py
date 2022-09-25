import logging

from smalien.utils.java_to_smali_converter import JavaToSmaliConverter

logger = logging.getLogger(name=__name__)

REFLECTIVE_CALLl = {
    'class': 'Ljava/lang/reflect/Method;',
    'method': 'invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;',
}

REFLECTIVE_FIELD_ACCESS = {
    'class': 'Ljava/lang/reflect/Field;',
    'method': 'set(Ljava/lang/Object;Ljava/lang/Object;)V',
}

class ReflectiveCallDetector:

    @staticmethod
    def detect_reflective_calls(invoke):
        """
        Check whether the given invoke instruction is a reflective call.
        """
        if (invoke.class_name == REFLECTIVE_CALLl['class'] and
            invoke.method_name == REFLECTIVE_CALLl['method']):
            return True
        return False

class ReflectiveFieldDetector:

    @staticmethod
    def detect_reflective_field(invoke):
        """
        Check whether the given invoke instruction is a reflective field access.
        """
        if (invoke.class_name == REFLECTIVE_FIELD_ACCESS['class'] and
            invoke.method_name == REFLECTIVE_FIELD_ACCESS['method']):
            return True
        return False

class ReflectionResolver:
    """
    This class resolves target class and method names of reflective method calls.
    """

    def __init__(self, app, detect_failures):
        logger.debug('initializing')

        self.app = app
        self.detect_failures = detect_failures

    def run(self, **kwargs):
        """
        Run the reflection resolver.
        """

        inst = kwargs['inst']

        if (inst.kind != 'invoke'):
            return

        is_reflective_call = ReflectiveCallDetector.detect_reflective_calls(inst)
        if (is_reflective_call):
            try:
                self.resolve(**kwargs)
            except Exception as e:
                if (self.detect_failures):
                    raise e
                else:
                    # Ignore the failure
                    pass
            return

        is_reflective_field_access = ReflectiveFieldDetector.detect_reflective_field(inst)
        if (is_reflective_field_access):
            try:
                self.resolve_reflective_field(**kwargs)
            except Exception as e:
                if (self.detect_failures):
                    raise e
                else:
                    # Ignore the failure
                    pass

    def resolve(self, **kwargs):
        """
        Resolve target class and method names of the given invoke instruction.
        """

        inst = kwargs['inst']
        registers = kwargs['sf'].registers

        # Get target in java-style
        target_in_java = registers[inst.arguments[0]].value

        # Convert java-style target to smali
        results = JavaToSmaliConverter.convert(target_in_java)

        # Save the result
        inst.reflective_call_class = results[0]
        inst.reflective_call_method = results[1]

    def resolve_reflective_field(self, **kwargs):
        """
        Resolve target field name of the given invoke instruction.
        """

        inst = kwargs['inst']
        registers = kwargs['sf'].registers

        # Get target in java-style
        target_in_java = registers[inst.arguments[0]].value

        inst.reflective_field_attr, inst.reflective_field_name = JavaToSmaliConverter.convert_field(target_in_java)
