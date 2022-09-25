from .value_resolvers import *

mapping = {
    # method head
    'method_head': MethodHeadValueResolver,

    # invoke
    'invoke': InvokeValueResolver,

    # move_result
    'move_result': MoveResultValueResolver,

    # return
    'return': ReturnValueResolver,

    # move
    'move': MoveValueResolver,

    # const
    'const': ConstValueResolver,
    'const_string': ConstStringValueResolver,
    'const_class': ConstClassValueResolver,

    # new_instance
    'new_instance': NewInstanceValueResolver,

    # instance_of
    'instance_of': InstanceOfValueResolver,

    #
    # Array operation
    #
    'new_array': NewArrayValueResolver,
    'fill_array_data': FillArrayDataValueResolver,

    # This is processed by MoveResultValueResolver at the corresponding move-result instructions
    # 'filled_new_array': ,

    'array_length': ArrayLengthValueResolver,

    'aput': AputValueResolver,
    'aget': AgetValueResolver,

    #
    # Setter and getter
    #
    # instance operation
    'iget': IgetValueResolver,
    'iput': IputValueResolver,

    # static operation
    'sget': SgetValueResolver,
    'sput': SputValueResolver,


    #
    # Arithmetic and logical operations
    # TODO: For J and D data type operations, a pair of registers should be updated
    #
    # unop vA, vB
    'unop': UnopValueResolver,

    # binop vAA, vBB, vCC
    'binop': BinopValueResolver,

    # binop/lit8 vAA, vBB, #+CC
    'binoplit8': BinopLit8ValueResolver,

    # binop/2addr vA, vB
    'binop2addr': Binop2addrValueResolver,


    #
    # cmpkind vAA, vBB, vCC
    #
    'cmp': CmpValueResolver,

    #
    # Try-catch
    #
    'throw': ThrowValueResolver,
    'move_exception': MoveExceptionValueResolver,

    # check-cast
    'check_cast': CheckCastValueResolver,
}
