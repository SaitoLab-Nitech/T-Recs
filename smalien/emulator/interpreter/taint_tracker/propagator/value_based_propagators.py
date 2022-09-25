import logging
import copy

from ...value_manager.structures import PrimitiveValue, ArrayInstanceValue, ClassInstanceValue
from smalien.data_types import primitive_data_types

logger = logging.getLogger(name=__name__)


class InvokeValueBasedPropagator:
    """
    Propagate taints at invoke instructions.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']
        intent_data = kwargs['intent_data']
        after_invocation = kwargs['after_invocation']

        if (after_invocation):
            # After the method invocation
            pass
        else:
            # Before the method invocation
            if (not inst.in_app):
                # Targets: Intent, SharedPreferences, Message, Parcel, file, PointF, Button, Bundle
                if ((inst.class_name == 'Landroid/content/Intent;' and inst.method_name == 'putExtra(Ljava/lang/String;Ljava/lang/String;)Landroid/content/Intent;') or
                    (inst.class_name == 'Landroid/content/SharedPreferences$Editor;' and inst.method_name == 'putString(Ljava/lang/String;Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;') or
                    (inst.class_name == 'Landroid/os/Message;' and inst.method_name == 'obtain(Landroid/os/Handler;III)Landroid/os/Message;') or
                    (inst.class_name == 'Landroid/os/Parcel;' and inst.method_name == 'writeValue(Ljava/lang/Object;)V') or
                    (inst.class_name == 'Ljava/io/FileOutputStream;' and inst.method_name == 'write([B)V') or
                    (inst.class_name == 'Landroid/graphics/PointF;' and inst.method_name == '<init>(FF)V') or
                    (inst.class_name == 'Landroid/widget/Button;' and inst.method_name == 'setHint(Ljava/lang/CharSequence;)V') or
                    (inst.class_name == 'Landroid/os/Bundle;' and inst.method_name == 'putString(Ljava/lang/String;Ljava/lang/String;)V')
                ):
                    if (len(inst.arguments) == 2):
                        value_register = inst.arguments[1]
                    else:
                        value_register = inst.arguments[2]

                    value = registers[value_register]

                    if (value.taint is not None):
                        InvokeValueBasedPropagator.save_intent_value(value, intent_data)

                # Prototype of memorizing values for instances' contained_values
                elif ((inst.class_name == 'Ljava/util/Map;' and inst.method_name == 'put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;') or
                      (inst.class_name == 'Ljava/util/List;' and inst.method_name == 'add(Ljava/lang/Object;)Z') or
                      (inst.class_name == 'Ljava/util/LinkedList;' and inst.method_name == 'add(Ljava/lang/Object;)Z')
                ):
                    # Check whether the method has arguments other than the base object
                    if (len(inst.arguments) > 1):
                        # Check whether base object is a class instance
                        base = registers[inst.arguments[0]]
                        if (not isinstance(base, ClassInstanceValue)):
                            return

                        # Memorize argument values
                        for arg in inst.arguments[1:]:
                            value = registers[arg]
                            # Currently only target ClassInstanceValue, even though ClassReferenceValue and PrimitiveValue also appear
                            if (isinstance(value, ClassInstanceValue) and value.string is not None):
                                logger.debug(f'saving value of {arg = } as a contained value of {inst.arguments[0] = }')
                                logger.debug(value)

                                key = InvokeValueBasedPropagator.generate_key_for_value(value)

                                if (key is not None):
                                    # This should use deepcopy to avoid being tainted after the current line
                                    base.contained_values[key] = copy.deepcopy(value)

                # Prototype of detecting transmitter with reflective calls
                elif (inst.reflective_call_class == 'Landroid/content/Intent;' and
                      inst.reflective_call_method == 'putExtra(Ljava/lang/String;Ljava/lang/String;)Landroid/content/Intent;'
                ):
                    logger.info('reflective call of Intent.putExtra')
                    array_register = inst.arguments[-1]

                    for value in registers[array_register].elements:
                        if (value.taint is not None):
                            InvokeValueBasedPropagator.save_intent_value(value, intent_data)

    @staticmethod
    def save_intent_value(value, intent_data):
        logger.info('saving the intent value')
        logger.debug(value)

        key = InvokeValueBasedPropagator.generate_key_for_value(value)

        if (key is not None):
            intent_data[key] = value

    @staticmethod
    def generate_key_for_value(value):
        """
        Generate a value as a key based on the value's string. 
        """

        if (isinstance(value, ArrayInstanceValue)):
            # Check if the array is null
            if (value.value == 0):
                key = None
            elif (value.data_type == '[B'):
                # In Java, bytes can be negative, so use & 0xff to convert it to unsigned int before applying chr()
                key = ''.join([chr(val & 0xff) for val in value.value])
            else:
                try:
                    key = ''.join(value.value)
                except Exception as e:
                    raise Exception(f'join() failed with {value = }') from e
        elif (isinstance(value, PrimitiveValue)):
            key = value.value
        else:
            # Check if the instance is null
            if (value.value == 0):
                key = None
            else:
                assert value.string is not None, f'containing string=None in {value = }'

                key = value.string

        return key

class MoveResultValueBasedPropagator:
    """
    Propagate taints at move-result instructions.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']
        intent_data = kwargs['intent_data']

        if (inst.source.kind == 'invoke' and not inst.source.in_app):
            if ((inst.source.class_name == 'Landroid/content/Intent;' and inst.source.method_name == 'getStringExtra(Ljava/lang/String;)Ljava/lang/String;') or
                (inst.source.class_name == 'Landroid/content/SharedPreferences;' and inst.source.method_name == 'getString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;') or
                (inst.source.class_name == 'Landroid/os/Bundle;' and inst.source.method_name == 'getString(Ljava/lang/String;)Ljava/lang/String;') or
                (inst.source.class_name == 'Landroid/os/Parcel;' and inst.source.method_name == 'readValue(Ljava/lang/ClassLoader;)Ljava/lang/Object;') or
                (inst.source.class_name == 'Ljava/lang/String;' and inst.source.method_name == 'trim()Ljava/lang/String;') or  # For file
                (inst.source.class_name == 'Landroid/widget/Button;' and inst.source.method_name == 'getHint()Ljava/lang/CharSequence;')
            ):
                destination = registers[inst.destination]

                if (destination.value == 0):
                    return

                key = InvokeValueBasedPropagator.generate_key_for_value(destination)

                if (key in intent_data.keys()):
                    logger.info(f'value-based propagation for {inst.destination = }')
                    logger.info(f'{key = }')

                    destination.taint = copy.deepcopy(intent_data[key].taint)
            # Prototype of matching the returned value to contained_values of the class instance
            elif ((inst.source.class_name == 'Ljava/util/Map;' and inst.source.method_name == 'get(Ljava/lang/Object;)Ljava/lang/Object;') or
                  (inst.source.class_name == 'Ljava/util/List;' and inst.source.method_name == 'get(I)Ljava/lang/Object;') or
                  (inst.source.class_name == 'Ljava/util/LinkedList;' and inst.source.method_name == 'get(I)Ljava/lang/Object;')
            ):
                # Check whether the base object has items in contained_values
                if (len(inst.source.arguments) == 0):
                    return
                base = inst.source.base_object

                assert base is not None, 'Failing to save the base object at the invocation'

                if (not isinstance(base, ClassInstanceValue)):
                    return
                if (base.contained_values):
                    destination = registers[inst.destination]
                    if (isinstance(destination, ClassInstanceValue) and destination.string is None):
                        return

                    key = InvokeValueBasedPropagator.generate_key_for_value(destination)

                    if (key in base.contained_values.keys()):
                        logger.info(f'contained_value-based propagation for {inst.destination = }')
                        logger.info(f'{key = }')
                        # This can take too long.
                        # logger.debug(f'{base.contained_values[key] = }')

                        destination.taint = copy.deepcopy(base.contained_values[key].taint)

class IgetValueBasedPropagator:
    """
    Propagate taints at iget instructions.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']
        intent_data = kwargs['intent_data']

        if ((inst.source_data_type == 'Landroid/os/Message;' and inst.field == 'arg1:I') or
            (inst.source_data_type == 'Landroid/graphics/PointF;' and inst.field == 'y:F')
        ):
            destination = registers[inst.destination]
            key = InvokeValueBasedPropagator.generate_key_for_value(destination)

            if (key in intent_data.keys()):
                logger.info(f'[iget] value-based propagation for {inst.destination = }')
                logger.info(f'{key = }')

                destination.taint = copy.deepcopy(intent_data[key].taint)
