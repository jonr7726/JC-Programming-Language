from .base import Base
from llvmlite import ir

# Constants for each data type
VOID_TYPE = ir.VoidType()
BOOLEAN_TYPE = ir.IntType(1)
CHARACTER_TYPE = ir.IntType(8)

SHORT_TYPE = ir.IntType(16)
INTEGER_TYPE = ir.IntType(32)
LONG_TYPE = ir.IntType(64)

HALF_TYPE = ir.HalfType()
FLOAT_TYPE = ir.FloatType()
DOUBLE_TYPE = ir.DoubleType()
