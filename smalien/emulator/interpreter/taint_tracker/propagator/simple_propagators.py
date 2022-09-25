import logging
import copy

from .value_based_propagators import *
from ..taint_operator import TaintOperator
from ...value_manager.structures import ArrayInstanceValue, ClassInstanceValue
from smalien.data_types import primitive_data_types

logger = logging.getLogger(name=__name__)


class InvokeTaintPropagator:
    """
    Propagate taints at invoke instructions.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']
        after_invocation = kwargs['after_invocation']

        # Run value-based propagator
        # This should be executed before the below conservative tainting to memorize untainted values
        InvokeValueBasedPropagator.run(**kwargs)

        # Ignore sink methods
        if (inst.is_sink):
            return

        if (after_invocation):
            # After the method invocation.
            # This will be skipped if a corresponding move-result exists.
            # Currently, do nothing.
            pass
        else:
            # Before the method invocation
            if (not inst.in_app):
                # If the invoked method is a constructor and has no argument except the base object, skip the propagation
                if (inst.invoke_constructor and len(inst.arguments) == 1):
                    return

                for i, src in enumerate(inst.arguments_without_64bit_pairs):
                    # Get src's taint
                    # For base object of both the invoked method and running method, simply use its taint
                    if ((i == 0 and not inst.invoke_static) or
                        (src == 'p0')
                    ):
                        taint = registers[src].taint
                    else:
                        taint = InvokeTaintPropagator.get_taint(registers[src])

                    if (taint is not None):
                        logger.warning(f'[invoke] taint from {src = } to arguments')
                        # Propagate the taint to other reference-data-type arguments.
                        for dst in inst.arguments:
                            if (src != dst and inst.argument_data_types[dst] not in primitive_data_types):
                                # Append taint
                                # TODO: Refact this taint appending
                                if (registers[dst].taint is None):
                                    registers[dst].taint = copy.deepcopy(taint)
                                else:
                                    TaintOperator.merge_taint(registers[dst].taint, taint)
                                    # registers[dst].taint.sources = list(set(registers[dst].taint.sources) | set(taint.sources))
                                    # registers[dst].taint.flow_details = list(set(registers[dst].taint.flow_details) | set(taint.flow_details))

                                # Propagate taint to OutputStream
                                if (isinstance(registers[dst], ClassInstanceValue) and registers[dst].outputstream is not None):
                                    registers[dst].outputstream.taint = copy.deepcopy(taint)

                        # Save the taint for propagating to move-result destination at the move-result execution.
                        # TODO: Refact this taint appending
                        if (inst.taint_to_ret is None):
                            inst.taint_to_ret = copy.deepcopy(taint)
                        else:
                            TaintOperator.merge_taint(inst.taint_to_ret, taint)
                            # inst.taint_to_ret.sources = list(set(inst.taint_to_ret.sources) | set(taint.sources))
                            # inst.taint_to_ret.flow_details = list(set(inst.taint_to_ret.flow_details) | set(taint.flow_details))

                        # # Currently, consider only one taint
                        # break

    @staticmethod
    def get_taint(reg_data):
        """
        Extract and return taint from the given register's data.
            - Array:
                Return its taint or its elements' taint.
                Currently, only single-dimensional arrays are supported.
                Currently, multi-taints are not supported.
            - Class Instance: 
                Return its taint or its fields' taint.
            - Others:
                Simply return its taint.
        """
        match reg_data:
            case ArrayInstanceValue():
                # Check array's taint
                if (reg_data.taint is not None):
                    return reg_data.taint

                # Check array's elements' taint
                for element in reg_data.elements:
                    if (element.taint is not None):
                        return element.taint

            case ClassInstanceValue():
                # Check class instance's taint
                if (reg_data.taint is not None):
                    return reg_data.taint

                # Check class instance's fields' taint
                for field in reg_data.fields.values():
                    if (field.taint is not None):
                        return field.taint

            case _:
                return reg_data.taint

class MoveResultTaintPropagator:
    """
    Propagate taints at move-result instructions.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']
        after_invocation = kwargs['after_invocation']

        if (inst.source.kind == 'invoke' and inst.source.taint_to_ret is not None):
            if (not inst.source.in_app):
                # Propagate taint by using invocation's inst.taint_to_ret
                logger.warning(f'[move-result] taint from arguments to {inst.destination = }')
                registers[inst.destination].taint = inst.source.taint_to_ret

                # Clear the saved taint
                inst.source.taint_to_ret = None
            else:
                # Propagate only sources for 'PRE-SINK'.
                # This is necessary because pre-sink methods can be falsely identified as in-app.
                # TODO: Implement a better solution to propagate 'PRE-SINK'.
                registers[inst.destination].taint = inst.source.taint_to_ret
                inst.source.taint_to_ret = None

        # Run value-based propagator
        MoveResultValueBasedPropagator.run(**kwargs)

class AputTaintPropagator:
    """
    Propagate taints at aput instructions.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']

        # Array elements' taints are collected and propagated by InvokeTaintPropagator,
        # and currently do nothing here.

        # if (registers[inst.source].taint is not None):
        #     logger.warning(f'[aput] taint from {inst.source= } to {inst.array = }')
        #     registers[inst.array].taint = copy.deepcopy(registers[inst.source].taint)

class AgetTaintPropagator:
    """
    Propagate taints at aget instructions.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']

        if (registers[inst.array].taint is not None):
            logger.warning(f'[aget] taint from {inst.array = } to {inst.destination = }')
            registers[inst.destination].taint = copy.deepcopy(registers[inst.array].taint)

class IgetTaintPropagator:
    """
    Propagate taints at iget instructions.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']

        # Propagate taint from the instance to the destination if the destination is not tainted
        if (registers[inst.source].taint is not None and
            registers[inst.destination].taint is None
           ):
            logger.warning(f'[iget] taint from {inst.source = } to {inst.destination = }')
            registers[inst.destination].taint = copy.deepcopy(registers[inst.source].taint)

        # Run value-based propagator
        IgetValueBasedPropagator.run(**kwargs)

class UnopTaintPropagator:
    """
    Propagate taints at unary operation.
    """
    @staticmethod
    def run(**kwargs):
        logger.debug('running')

        inst = kwargs['inst']
        registers = kwargs['registers']

        if (registers[inst.source].taint is not None):
            logger.warning(f'[unop] taint from {inst.source = } to {inst.destination = }')
            registers[inst.destination].taint = copy.deepcopy(registers[inst.source].taint)
