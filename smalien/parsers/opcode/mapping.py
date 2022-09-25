from .cmp_opcode_parsers import *
from .other_opcode_parsers import *
from .invoke_opcode_parsers import *
from .const_opcode_parsers import *
from .array_opcode_parsers import *
from .control_opcode_parsers import *
from .unary_and_binary_opcode_parsers import *
from .setter_and_getter_opcode_parsers import *

from .label_parsers import *

opcode_mapping = {
    #
    # Nop operation
    #
    'nop': OpNopParser,


    #
    # Move operation
    #
    'move': OpMoveParser,
    'move/16': OpMoveParser,
    'move/from16': OpMoveParser,
    'move-wide': OpMoveParser,
    'move-wide/16': OpMoveParser,
    'move-wide/from16': OpMoveParser,
    'move-object': OpMoveParser,
    'move-object/16': OpMoveParser,
    'move-object/from16': OpMoveParser,


    #
    # Invoke and move-result operation
    #
    # invoke
    # invoke-kind
    'invoke-virtual': OpInvokeParser,
    'invoke-super': OpInvokeParser,
    'invoke-direct': OpInvokeParser,
    'invoke-static': OpInvokeParser,
    'invoke-interface': OpInvokeParser,
    # invoke-kind/range
    'invoke-virtual/range': OpInvokeParser,
    'invoke-super/range': OpInvokeParser,
    'invoke-direct/range': OpInvokeParser,
    'invoke-static/range': OpInvokeParser,
    'invoke-interface/range': OpInvokeParser,
    # invoke_unknown
    'invoke-polymorphic': OpInvokeUnknownParser,
    'invoke-polymorphic/range': OpInvokeUnknownParser,
    'invoke-custom': OpInvokeUnknownParser,
    'invoke-custom/range': OpInvokeUnknownParser,

    # move_result
    'move-result': OpMoveResultParser,
    'move-result-wide': OpMoveResultParser,
    'move-result-object': OpMoveResultParser,


    #
    # Const operation
    #
    # Numeric
    'const': OpConstNumericParser,
    'const/4': OpConstNumericParser,
    'const/16': OpConstNumericParser,
    'const/high16': OpConstNumericParser,
    'const-wide': OpConstNumericParser,
    'const-wide/16': OpConstNumericParser,
    'const-wide/32': OpConstNumericParser,
    'const-wide/high16': OpConstNumericParser,
    # String
    'const-string': OpConstStringParser,
    'const-string/jumbo': OpConstStringParser,
    # Class
    'const-class': OpConstClassParser,
    # Method
    'const-method-handle': OpConstUnknownParser,
    'const-method-type': OpConstUnknownParser,


    #
    # Monitor operation
    #
    'monitor-enter': OpMonitorEnterParser,
    'monitor-exit': OpMonitorExitParser,


    #
    # check-cast
    #
    'check-cast': OpCheckCastParser,

    #
    # array operation
    #
    # aget
    'aget': OpAgetParser,
    'aget-wide': OpAgetParser,
    'aget-object': OpAgetParser,
    'aget-boolean': OpAgetParser,
    'aget-byte': OpAgetParser,
    'aget-char': OpAgetParser,
    'aget-short': OpAgetParser,
    # aput
    'aput': OpAputParser,
    'aput-wide': OpAputParser,
    'aput-object': OpAputParser,
    'aput-boolean': OpAputParser,
    'aput-byte': OpAputParser,
    'aput-char': OpAputParser,
    'aput-short': OpAputParser,

    # new_array
    'new-array': OpNewArrayParser,

    # filled_new_array
    'filled-new-array': OpFilledNewArrayParser,
    'filled-new-array/range': OpFilledNewArrayParser,

    # array_length
    'array-length': OpArrayLengthParser,

    # fill_array_data
    'fill-array-data': OpFillArrayDataParser,


    #
    # Instance operation
    #
    # new_instance
    'new-instance': OpNewInstanceParser,

    # instance_of
    'instance-of': OpInstanceOfParser,

    # instance field operation
    # iget
    'iget': OpIgetParser,
    'iget-byte': OpIgetParser,
    'iget-short': OpIgetParser,
    'iget-char': OpIgetParser,
    'iget-boolean': OpIgetParser,
    'iget-wide': OpIgetParser,
    'iget-object': OpIgetParser,
    # iput
    'iput': OpIputParser,
    'iput-byte': OpIputParser,
    'iput-short': OpIputParser,
    'iput-char': OpIputParser,
    'iput-boolean': OpIputParser,
    'iput-wide': OpIputParser,
    'iput-object': OpIputParser,

    # static field operation
    # sget
    'sget': OpSgetParser,
    'sget-byte': OpSgetParser,
    'sget-short': OpSgetParser,
    'sget-char': OpSgetParser,
    'sget-boolean': OpSgetParser,
    'sget-wide': OpSgetParser,
    'sget-object': OpSgetParser,
    # sput
    'sput': OpSputParser,
    'sput-byte': OpSputParser,
    'sput-short': OpSputParser,
    'sput-char': OpSputParser,
    'sput-boolean': OpSputParser,
    'sput-wide': OpSputParser,
    'sput-object': OpSputParser,


    #
    # unop vA, vB
    # Negation
    'neg-int': OpUnopParser,
    'not-int': OpUnopParser,
    'neg-long': OpUnopParser,
    'not-long': OpUnopParser,
    'neg-float': OpUnopParser,
    'neg-double': OpUnopParser,
    # Data type conversion
    # int-to-*
    'int-to-byte': OpUnopParser,
    'int-to-char': OpUnopParser,
    'int-to-short': OpUnopParser,
    'int-to-long': OpUnopParser,
    'int-to-float': OpUnopParser,
    'int-to-double': OpUnopParser,
    # long-to-*
    'long-to-int': OpUnopParser,
    'long-to-float': OpUnopParser,
    'long-to-double': OpUnopParser,
    # float-to-*
    'float-to-int': OpUnopParser,
    'float-to-long': OpUnopParser,
    'float-to-double': OpUnopParser,
    # double-to-*
    'double-to-int': OpUnopParser,
    'double-to-long': OpUnopParser,
    'double-to-float': OpUnopParser,

    # binop vAA, vBB, vCC
    # int
    'add-int': OpBinopParser,
    'sub-int': OpBinopParser,
    'mul-int': OpBinopParser,
    'div-int': OpBinopParser,
    'rem-int': OpBinopParser,
    'and-int': OpBinopParser,
    'or-int': OpBinopParser,
    'xor-int': OpBinopParser,
    'shl-int': OpBinopParser,
    'shr-int': OpBinopParser,
    'ushr-int': OpBinopParser,
    # long
    'add-long': OpBinopParser,
    'sub-long': OpBinopParser,
    'mul-long': OpBinopParser,
    'div-long': OpBinopParser,
    'rem-long': OpBinopParser,
    'and-long': OpBinopParser,
    'or-long': OpBinopParser,
    'xor-long': OpBinopParser,
    'shl-long': OpBinopParser,
    'shr-long': OpBinopParser,
    'ushr-long': OpBinopParser,
    # float
    'add-float': OpBinopParser,
    'sub-float': OpBinopParser,
    'mul-float': OpBinopParser,
    'div-float': OpBinopParser,
    'rem-float': OpBinopParser,
    # double
    'add-double': OpBinopParser,
    'sub-double': OpBinopParser,
    'mul-double': OpBinopParser,
    'div-double': OpBinopParser,
    'rem-double': OpBinopParser,

    # binop/2addr vA, vB
    # int
    'add-int/2addr': OpBinop2addrParser,
    'sub-int/2addr': OpBinop2addrParser,
    'mul-int/2addr': OpBinop2addrParser,
    'div-int/2addr': OpBinop2addrParser,
    'rem-int/2addr': OpBinop2addrParser,
    'and-int/2addr': OpBinop2addrParser,
    'or-int/2addr': OpBinop2addrParser,
    'xor-int/2addr': OpBinop2addrParser,
    'shl-int/2addr': OpBinop2addrParser,
    'shr-int/2addr': OpBinop2addrParser,
    'ushr-int/2addr': OpBinop2addrParser,
    # long
    'add-long/2addr': OpBinop2addrParser,
    'sub-long/2addr': OpBinop2addrParser,
    'mul-long/2addr': OpBinop2addrParser,
    'div-long/2addr': OpBinop2addrParser,
    'rem-long/2addr': OpBinop2addrParser,
    'and-long/2addr': OpBinop2addrParser,
    'or-long/2addr': OpBinop2addrParser,
    'xor-long/2addr': OpBinop2addrParser,
    'shl-long/2addr': OpBinop2addrParser,
    'shr-long/2addr': OpBinop2addrParser,
    'ushr-long/2addr': OpBinop2addrParser,
    # float
    'add-float/2addr': OpBinop2addrParser,
    'sub-float/2addr': OpBinop2addrParser,
    'mul-float/2addr': OpBinop2addrParser,
    'div-float/2addr': OpBinop2addrParser,
    'rem-float/2addr': OpBinop2addrParser,
    # double
    'add-double/2addr': OpBinop2addrParser,
    'sub-double/2addr': OpBinop2addrParser,
    'mul-double/2addr': OpBinop2addrParser,
    'div-double/2addr': OpBinop2addrParser,
    'rem-double/2addr': OpBinop2addrParser,

    # binop/lit16 vA, vB, #+CCCC
    # TODO: Currently, these instructions are parsed by the lit8 parser
    #       So, check if this works
    'add-int/lit16': OpBinopLit8Parser,
    'rsub-int': OpBinopLit8Parser,
    'mul-int/lit16': OpBinopLit8Parser,
    'div-int/lit16': OpBinopLit8Parser,
    'rem-int/lit16': OpBinopLit8Parser,
    'and-int/lit16': OpBinopLit8Parser,
    'or-int/lit16': OpBinopLit8Parser,
    'xor-int/lit16': OpBinopLit8Parser,

    # binop/lit8 vAA, vBB, #+CC
    'add-int/lit8': OpBinopLit8Parser,
    'rsub-int/lit8': OpBinopLit8Parser,
    'mul-int/lit8': OpBinopLit8Parser,
    'div-int/lit8': OpBinopLit8Parser,
    'rem-int/lit8': OpBinopLit8Parser,
    'and-int/lit8': OpBinopLit8Parser,
    'or-int/lit8': OpBinopLit8Parser,
    'xor-int/lit8': OpBinopLit8Parser,
    'shl-int/lit8': OpBinopLit8Parser,
    'shr-int/lit8': OpBinopLit8Parser,
    'ushr-int/lit8': OpBinopLit8Parser,


    # 
    # return
    #
    'return-void': OpReturnParser,
    'return': OpReturnParser,
    'return-wide': OpReturnParser,
    'return-object': OpReturnParser,


    #
    # cmp
    #
    'cmpl-float': OpCmpParser,
    'cmpg-float': OpCmpParser,
    'cmpl-double': OpCmpParser,
    'cmpg-double': OpCmpParser,
    'cmp-long': OpCmpParser,


    #
    #  Control-related Instructions
    #  Parsed by control_opcode_parsers.py
    #

    # throw
    'throw': OpThrowParser,

    # move-exception
    'move-exception': OpMoveExceptionParser,

    # goto
    'goto': OpGotoParser,
    'goto/16': OpGotoParser,
    'goto/32': OpGotoParser,

    # switch
    'packed-switch': OpSwitchParser,
    'sparse-switch': OpSwitchParser,

    # if-test
    'if-eq': OpIfParser,
    'if-ne': OpIfParser,
    'if-lt': OpIfParser,
    'if-ge': OpIfParser,
    'if-gt': OpIfParser,
    'if-le': OpIfParser,

    # if-testz
    'if-eqz': OpIfzParser,
    'if-nez': OpIfzParser,
    'if-ltz': OpIfzParser,
    'if-gez': OpIfzParser,
    'if-gtz': OpIfzParser,
    'if-lez': OpIfzParser,
}


label_mapping = {
    #
    # :cond_*
    #
    ':cond': CondLabelParser,

    #
    # :goto_*
    #
    ':goto': GotoLabelParser,

    #
    # :pswitch, :pswitch_data, :sswitch, and :sswitch_data
    #
    ':pswitch': SwitchLabelParser,
    ':sswitch': SwitchLabelParser,

    #
    # :array_*
    #
    ':array': ArrayLabelParser,

    #
    # :try_start and :try_end
    #
    ':try': TryLabelParser,

    #
    # .catch and .catchall
    #
    '.catch': CatchDataParser,
    '.catchall': CatchDataParser,

    #
    # :catch and :catchall
    #
    ':catch': CatchLabelParser,
    ':catchall': CatchLabelParser,
}
