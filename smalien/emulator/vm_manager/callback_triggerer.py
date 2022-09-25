import logging

from .structures import VMOrder

logger = logging.getLogger(name=__name__)


class CallbackTriggerer:
    """
    Trigger callback methods that are not executed on the device.
    """

    def __init__(self, classes):
        logger.debug('initializing')

        self.classes = classes

        self.triggered_at_constructor = []

    def trigger_at_end(self, vms):
        """
        Trigger callback methods at the end of the emulation.
        """
        logger.debug('triggering at the end of the emulation')

        # Search data of VMs for onLowMemory-implemented classes
        for ptids, vmm in vms.items():
            # Search instances for instances of onLowMemory-implemented classes
            for instance_key, instance in vmm.vm.instances.items():

                # logger.warning(instance)
                # assert len(instance) == 1, f'instances duplicate, {len(instance) = }, {instance_key = }'

                instance = instance[0]

                class_data = self.classes.get(instance.data_type)
                if (class_data is not None and class_data.onlowmemory is not None):
                    logger.warning(f'Triggering onLowMemory of {instance.data_type = }')

                    # Use previously-generated value of the base object
                    values = {'p0': instance_key }

                    # Create a VMOrder
                    yield VMOrder(clss=instance.data_type, method=class_data.onlowmemory.name,
                                  line=class_data.onlowmemory.start_at,
                                  pid=vmm.vm.pid, tid=vmm.vm.tid, values=values, logging=False)

                    # Create a VMOrder
                    yield VMOrder(clss=instance.data_type, method=class_data.onlowmemory.name,
                                  line=class_data.onlowmemory.start_at,
                                  pid=vmm.vm.pid, tid=vmm.vm.tid, values=values, logging=False)

    def trigger_at_constructor(self, vm):
        """
        Return a VMOrder of a callback method of recently-created instances.
        """
        logger.debug('triggering at constructor')

        for instance_key, instance in vm.instances.items():
            if (instance_key not in self.triggered_at_constructor):
                self.triggered_at_constructor.append(instance_key)

                # logger.warning(instance)
                # assert len(instance) == 1, f'instances duplicate, {len(instance) = }, {instance_key = }'

                instance = instance[0]

                class_data = self.classes.get(instance.data_type)
                if (class_data is not None and class_data.onlowmemory is not None):
                    logger.warning(f'Triggering onLowMemory of {instance.data_type = }')

                    # Use previously-generated value of the base object
                    values = {'p0': instance_key }

                    # Create a VMOrder
                    return VMOrder(clss=instance.data_type, method=class_data.onlowmemory.name,
                                   line=class_data.onlowmemory.start_at,
                                   pid=vm.pid, tid=vm.tid, values=values, logging=False)
