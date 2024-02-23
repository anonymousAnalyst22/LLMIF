import struct
import sys
from datetime import datetime,timezone

DEFAULT_ENDIAN = 'little'

# Constants for parsing Command/Attribute entries in the repo
PAYLOAD_KEYWORD = 'payload'
CMDS_KEYWORD = 'cmds'
ATTRS_KEYWORD = 'attrs'
DESCRIPTION_KEYWORD = 'description'
NAME_KEYWORD = 'name'
TYPE_KEYWORD = 'type'
RANGE_KEYWORD = 'range'
ACCESS_KEYWORD = 'access'
DEFAULT_KEYWORD = 'default'
MO_KEYWORD = 'mo'

GENETIC_COMMAND_SCOPE = 'genetic'
ZCL_COMMAND_SCOPE = 'zcl'
MANUFACTURER_COMMAND_SCOPE = 'manu'
GENERAL_CLUSTER_ID = '0xCDEF' # Self-defined id for recognizing General cluster in ZCL

DEFAULT_RANGE_LOW = 0x0
DEFAULT_RANGE_HIGH = 0xffffffffffffffff

# Constants for Determining Param/Attribute types
BOOLPREFIX = 'bool'
UINTPREFIX = 'uint'
MAPPREFIX = 'map'
DATAPREFIX = 'data'
ENUMPREFIX = 'enum'
KEYPREFIX = 'key'
INTPREFIX = 'int'
SINGLEPREFIX = 'single'
UTCPREFIX = 'UTC'
EUIPREFIX = 'EUI'
STRINGPREFIX = 'string'
OCTSTRINGPREFIX = 'octstr'
STRUCTPREFIX = 'Struct'
ARRAYPREFIX = 'Array'
VARIABLEPREFIX = 'Variable'

BOOL_OCTETS = 1
UINT_OCTETS = 4
INT_OCTETS = 4
SINGLE_OCTETS = 4
UTC_OCTETS = 4
EUI_OCTETS = 8

STRUCT_VALUE_PATTERN = r"Struct\((.*?)\)"
ARRAY_VALUE_PATTERN = r"Array\[(.*?)\]"
RANGE_VALUE_PATTERN = r"\[(.*?)\.\.\.(.*?)\]"

EXPANDING_PARAM_SYMBOL = '...'
DATA_LEGAL_TYPES = [ARRAYPREFIX, STRUCTPREFIX, VARIABLEPREFIX, EUIPREFIX, UTCPREFIX, INTPREFIX, UINTPREFIX, BOOLPREFIX, STRINGPREFIX, SINGLEPREFIX, KEYPREFIX, MAPPREFIX, DATAPREFIX, ENUMPREFIX, OCTSTRINGPREFIX]
DATA_NUMERIC_TYPES = [EUIPREFIX, UTCPREFIX, INTPREFIX, UINTPREFIX, SINGLEPREFIX, KEYPREFIX, MAPPREFIX, DATAPREFIX, ENUMPREFIX]
STRING_TYPES = [STRINGPREFIX, OCTSTRINGPREFIX]
EXTENSIBLE_TYPES = [ARRAYPREFIX, STRUCTPREFIX]
NONFIXED_NBYTES_TYPES = [ARRAYPREFIX, STRUCTPREFIX, VARIABLEPREFIX, STRINGPREFIX, OCTSTRINGPREFIX]

IS_NUMERIC_TYPE = 0x0
IS_STRING_TYPE = 0x1
IS_ARRAY_TYPE = 0x2
IS_STRUCT_TYPE = 0x3

# Defined in ZCL section 2.6.2
CODE_TYPE_TABLE = {
    0x08: 'data8',
    0x09: 'data16',
    0x0a: 'data24',
    0x0b: 'data32',
    0x0c: 'data40',
    0x0d: 'data48',
    0x0e: 'data56',
    0x0f: 'data64',
    0x10: 'bool',
    0x18: 'map8',
    0x19: 'map16',
    0x1a: 'map24',
    0x1b: 'map32',
    0x1c: 'map40',
    0x1d: 'map48',
    0x1e: 'map56',
    0x1f: 'map64',
    0x20: 'uint8',
    0x21: 'uint16',
    0x22: 'uint24',
    0x23: 'uint32',
    0x24: 'uint40',
    0x25: 'uint48',
    0x26: 'uint56',
    0x27: 'uint64',
    0x28: 'int8',
    0x29: 'int16',
    0x2a: 'int24',
    0x2b: 'int32',
    0x2c: 'int40',
    0x2d: 'int48',
    0x2e: 'int56',
    0x2f: 'int64',
    0x30: 'enum8',
    0x31: 'enum16',
    0x38: 'semi',
    0x39: 'single',
    0x3a: 'double',
    0x41: 'octstr',
    0x42: 'string',
    0x43: 'octstr16',
    0x44: 'string16',
    0x48: 'Array',
    0x4c: 'Struct',
    0xe2: 'UTC',
    0xf0: 'EUI64',
    0xf1: 'key128'
}

# Constants for recognizing param/attribute values
ALL_RANGE = '-'
ACCESS_READ = 'r'
ACCESS_WRITE = 'w'
ACCESS_REPORT = 'p'
ACCESS_SCENES = 's'
ANY_DEFAULT = '-'

ACCESS_LEGAL_TYPES = [ACCESS_READ, ACCESS_WRITE, ACCESS_REPORT, ACCESS_SCENES, ALL_RANGE]
ACCESS_READ_BIT = 0x1
ACCESS_WRITE_BIT = 0x10
ACCESS_REPORT_BIT = 0x100
ACCESS_SCENES_BIT = 0x1000
ACCESS_ALL_BITS = ACCESS_SCENES_BIT | ACCESS_REPORT_BIT | ACCESS_WRITE_BIT | ACCESS_READ_BIT
ACCESS_BIT_DICT = {
    ACCESS_READ: ACCESS_READ_BIT,
    ACCESS_WRITE: ACCESS_WRITE_BIT,
    ACCESS_REPORT: ACCESS_REPORT_BIT,
    ACCESS_SCENES: ACCESS_SCENES_BIT,
    ALL_RANGE: ACCESS_ALL_BITS,
}

MO_MANDATORY = 'm'
MO_OPTIONAL = 'o'
MO_LEGAL_TYPES = [MO_MANDATORY, MO_OPTIONAL]

class Mutable():

    """
    Genetic class to represent any data types: A bytearray
    """

    def __init__(self, byte_array) -> None:
        self.byte_array = byte_array
        self.octets = len(self.byte_array)
    
    def set_byte_array(self, byte_array:'bytearray', value_refresh=True):
        """
        This function is a type- and format-preserving function.
        Once the byte_array is updated, the corresponding value will also be updated.
        """
        self.byte_array = byte_array
        self.octets = len(self.byte_array)
        if value_refresh:
            self.refresh_value()
    
    def refresh_value(self):
        """
        Sometimes we prefer to directly updating the byte_array,
        which causes inconsistencies between the byte_array and value in child-class.
        As a result, this function is defined for keeping consistencies.
        The implementation depends on specific child class.
        """
        pass

    def copy(self):
        """
        Interface for copy
        """
        pass

"""
The Zigbee Supported Data Types are specified in Section 2.6.2, ZCL Specification
Identified Zigbee Data Types
1. bool
2. uint8, uint16, uint24, uint32, uint48
3. int8, int16, int32
4. single (float)
5. UTC
6. EUI64
7. string
8. struct
9. Array
10. Variable
"""

class ZbeeBool(Mutable):

    def __init__(self, value:'int'=0) -> None:
        self.value = value
        self.type_name = BOOLPREFIX
        self.n_bytes = BOOL_OCTETS
        self.n_minimum_bytes = BOOL_OCTETS
        self.type_prefix = BOOLPREFIX
        self.typecode = 0x10
        byte_array = self.__convert_value_to_bytearray(value)
        self.range_low = 0
        self.range_high = 1
        super().__init__(byte_array)
    
    def copy(self):
        return ZbeeBool(self.value)
    
    def refresh_value(self):
        assert(self.octets == self.n_bytes == BOOL_OCTETS)
        self.value = int.from_bytes(self.byte_array, DEFAULT_ENDIAN)

    def __convert_value_to_bytearray(self, value:'int'):
        return bytearray(value.to_bytes(BOOL_OCTETS, DEFAULT_ENDIAN))

    def assign(self, value:'int') -> None:
        if value > self.range_high:
            value = self.range_high
        elif value < self.range_low:
            value = self.range_low
        self.value = value
        byte_array = self.__convert_value_to_bytearray(value)
        self.set_byte_array(byte_array)

class ZbeeUInt(Mutable):

    def __init__(self, value=0, type_name=UINTPREFIX) -> None:
        self.type_name = type_name
        self.type_prefix = UINTPREFIX
        self.n_bytes = self.__detemrine_int_octets()
        self.n_minimum_bytes = self.n_bytes
        self.typecode = self.__determine_type_code()
        self.value = value
        byte_array = self.__convert_value_to_bytearray(value)
        super().__init__(byte_array)
        self.range_low = 0x0
        self.range_high = int((1 << (self.n_bytes * 8)) - 1)

    def __determine_type_code(self):
        typecode_dict = {
            1: 0x20,
            2: 0x21,
            3: 0x22,
            4: 0x23,
            5: 0x24,
            6: 0x25,
            7: 0x26,
            8: 0x27
        }
        return typecode_dict[self.n_bytes]
    
    def copy(self):
        return ZbeeUInt(self.value, self.type_name)

    def __detemrine_int_octets(self):
        assert(self.type_name.startswith((UINTPREFIX, INTPREFIX)))
        n_bytes = 4
        segs = self.type_name.split(INTPREFIX)
        if len(segs[1]) > 0:
            n_bits = int(segs[1])
            n_bytes = int(n_bits / 8)
        return n_bytes

    def __convert_value_to_bytearray(self, value:'int'):
        return bytearray(value.to_bytes(self.n_bytes, DEFAULT_ENDIAN))

    def refresh_value(self):
        assert(self.octets == self.n_bytes)
        self.value = int.from_bytes(self.byte_array, DEFAULT_ENDIAN)

    def assign(self, value) -> None:
        if value > self.range_high:
            value = self.range_high
        elif value < self.range_low:
            value = self.range_low
        self.value = value
        byte_array = self.__convert_value_to_bytearray(value)
        self.set_byte_array(byte_array)

class ZbeeMap(Mutable):

    def __init__(self, value=0, type_name=MAPPREFIX) -> None:
        self.type_name = type_name
        self.type_prefix = MAPPREFIX
        self.n_bytes = self.__detemrine_octets()
        self.n_minimum_bytes = self.n_bytes
        self.typecode = self.__determine_type_code()
        self.value = value
        byte_array = self.__convert_value_to_bytearray(value)
        super().__init__(byte_array)
        self.range_low = 0x0
        self.range_high = int((1 << (self.n_bytes * 8)) - 1)

    def __determine_type_code(self):
        typecode_dict = {
            1: 0x18,
            2: 0x19,
            3: 0x1a,
            4: 0x1b,
            5: 0x1c,
            6: 0x1d,
            7: 0x1e,
            8: 0x1f
        }
        return typecode_dict[self.n_bytes]
    
    def copy(self):
        return ZbeeMap(self.value, self.type_name)

    def refresh_value(self):
        assert(self.octets == self.n_bytes)
        self.value = int.from_bytes(self.byte_array, DEFAULT_ENDIAN)

    def __detemrine_octets(self):
        assert(self.type_name.startswith(MAPPREFIX))
        n_bytes = 4
        segs = self.type_name.split(MAPPREFIX)
        if len(segs[1]) > 0:
            n_bits = int(segs[1])
            n_bytes = int(n_bits / 8)
        return n_bytes

    def __convert_value_to_bytearray(self, value:'int'):
        return bytearray(value.to_bytes(self.n_bytes, DEFAULT_ENDIAN))

    def assign(self, value) -> None:
        if value > self.range_high:
            value = self.range_high
        elif value < self.range_low:
            value = self.range_low
        self.value = value
        byte_array = self.__convert_value_to_bytearray(value)
        self.set_byte_array(byte_array)

class ZbeeData(Mutable):

    def __init__(self, value=0, type_name=DATAPREFIX) -> None:
        self.type_name = type_name
        self.type_prefix = DATAPREFIX
        self.n_bytes = self.__detemrine_octets()
        self.n_minimum_bytes = self.n_bytes
        self.typecode = self.__determine_type_code()
        self.value = value
        byte_array = self.__convert_value_to_bytearray(value)
        super().__init__(byte_array)
        self.range_low = 0x0
        self.range_high = int((1 << (self.n_bytes * 8)) - 1)

    def __determine_type_code(self):
        typecode_dict = {
            1: 0x08,
            2: 0x09,
            3: 0x0a,
            4: 0x0b,
            5: 0x0c,
            6: 0x0d,
            7: 0x0e,
            8: 0x0f
        }
        return typecode_dict[self.n_bytes]
    
    def copy(self):
        return ZbeeData(self.value, self.type_name)

    def refresh_value(self):
        assert(self.octets == self.n_bytes)
        self.value = int.from_bytes(self.byte_array, DEFAULT_ENDIAN)

    def __detemrine_octets(self):
        assert(self.type_name.startswith(DATAPREFIX))
        n_bytes = 4
        segs = self.type_name.split(DATAPREFIX)
        if len(segs[1]) > 0:
            n_bits = int(segs[1])
            n_bytes = int(n_bits / 8)
        return n_bytes

    def __convert_value_to_bytearray(self, value:'int'):
        return bytearray(value.to_bytes(self.n_bytes, DEFAULT_ENDIAN))

    def assign(self, value) -> None:
        if value > self.range_high:
            value = self.range_high
        elif value < self.range_low:
            value = self.range_low
        self.value = value
        byte_array = self.__convert_value_to_bytearray(value)
        self.set_byte_array(byte_array)

class ZbeeEnum(Mutable):

    def __init__(self, value=0, type_name=ENUMPREFIX) -> None:
        self.type_name = type_name
        self.type_prefix = ENUMPREFIX
        self.n_bytes = self.__detemrine_octets()
        self.n_minimum_bytes = self.n_bytes
        self.typecode = self.__determine_type_code()
        self.value = value
        byte_array = self.__convert_value_to_bytearray(value)
        super().__init__(byte_array)
        self.range_low = 0x0
        self.range_high = int((1 << (self.n_bytes * 8)) - 1)

    def __determine_type_code(self):
        typecode_dict = {
            1: 0x30,
            2: 0x31,
        }
        return typecode_dict[self.n_bytes]
    
    def copy(self):
        return ZbeeEnum(self.value, self.type_name)

    def refresh_value(self):
        assert(self.octets == self.n_bytes)
        self.value = int.from_bytes(self.byte_array, DEFAULT_ENDIAN)

    def __detemrine_octets(self):
        assert(self.type_name.startswith(ENUMPREFIX))
        n_bytes = 4
        segs = self.type_name.split(ENUMPREFIX)
        if len(segs[1]) > 0:
            n_bits = int(segs[1])
            n_bytes = int(n_bits / 8)
        return n_bytes

    def __convert_value_to_bytearray(self, value:'int'):
        return bytearray(value.to_bytes(self.n_bytes, DEFAULT_ENDIAN))

    def assign(self, value) -> None:
        if value > self.range_high:
            value = self.range_high
        elif value < self.range_low:
            value = self.range_low
        self.value = value
        byte_array = self.__convert_value_to_bytearray(value)
        self.set_byte_array(byte_array)

class ZbeeInt(Mutable):

    def __init__(self, value=0, type_name=INTPREFIX) -> None:
        self.type_name = type_name
        self.type_prefix = INTPREFIX
        self.n_bytes = self.__detemrine_int_octets()
        self.n_minimum_bytes = self.n_bytes
        self.typecode = self.__determine_type_code()
        self.value = value
        byte_array = self.__convert_value_to_bytearray(value)
        super().__init__(byte_array)
        self.range_low = -(1 << ((self.n_bytes * 8) - 1))
        self.range_high = (1 << ((self.n_bytes * 8) - 1)) - 1
    
    def copy(self):
        return ZbeeInt(self.value, self.type_name)

    def refresh_value(self):
        assert(self.octets == self.n_bytes)
        self.value = int.from_bytes(self.byte_array, DEFAULT_ENDIAN)

    def __detemrine_int_octets(self):
        assert(self.type_name.startswith((UINTPREFIX, INTPREFIX)))
        n_bytes = 4
        segs = self.type_name.split(INTPREFIX)
        if len(segs[1]) > 0:
            n_bits = int(segs[1])
            n_bytes = int(n_bits / 8)
        return n_bytes

    def __determine_type_code(self):
        typecode_dict = {
            1: 0x28,
            2: 0x29,
            3: 0x2a,
            4: 0x2b,
            5: 0x2c,
            6: 0x2d,
            7: 0x2e,
            8: 0x2f
        }
        return typecode_dict[self.n_bytes]

    def __convert_value_to_bytearray(self, value:'int'):
        value_bytes = value.to_bytes(self.n_bytes, DEFAULT_ENDIAN) if value > 0 else \
                      value.to_bytes(self.n_bytes, DEFAULT_ENDIAN, signed=True)
        return bytearray(value_bytes)

    def assign(self, value) -> None:
        if value > self.range_high:
            value = self.range_high
        elif value < self.range_low:
            value = self.range_low
        byte_array = self.__convert_value_to_bytearray(value)
        self.set_byte_array(byte_array)
        self.value = value

class ZbeeSingle(Mutable):

    def __init__(self, value=0.0) -> None:
        self.type_name = SINGLEPREFIX
        self.type_prefix = SINGLEPREFIX
        self.typecode = 0x39
        self.n_bytes = SINGLE_OCTETS
        self.n_minimum_bytes = self.n_bytes
        self.value = value
        byte_array = self.__convert_value_to_bytearray(value)
        super().__init__(byte_array)

        self.range_low = sys.float_info.min
        self.range_high = sys.float_info.max
    
    def copy(self):
        return ZbeeSingle(self.value)

    def refresh_value(self):
        assert(self.octets == self.n_bytes == SINGLE_OCTETS)
        self.value = struct.unpack('f', self.byte_array)

    def __convert_value_to_bytearray(self, value:'float'):
        byte_array = bytearray(struct.pack("<f", value)) if DEFAULT_ENDIAN == 'little' else \
                     bytearray(struct.pack(">f", value))
        assert(len(byte_array) == SINGLE_OCTETS)
        return byte_array

    def assign(self, value:float) -> None:
        if value > self.range_high:
            value = self.range_high
        elif value < self.range_low:
            value = self.range_low
        self.value = value
        byte_array = self.__convert_value_to_bytearray(value)
        self.set_byte_array(byte_array)

class ZbeeUTC(Mutable):

    def __init__(self, value=0) -> None:
        self.type_name = UTCPREFIX
        self.type_prefix = UTCPREFIX
        self.n_bytes = UTC_OCTETS
        self.n_minimum_bytes = self.n_bytes
        self.typecode = 0xe2
        self.value = value
        byte_array = self.__convert_value_to_bytearray(value)
        super().__init__(byte_array)
        self.range_low = 0x0
        self.range_high = int((1 << (self.n_bytes * 8)) - 1)
    
    def copy(self):
        return ZbeeUTC(self.value)

    def __convert_value_to_bytearray(self, value:'int'):
        return bytearray(value.to_bytes(self.n_bytes, DEFAULT_ENDIAN))

    def refresh_value(self):
        assert(self.octets == self.n_bytes)
        self.value = int.from_bytes(self.byte_array, DEFAULT_ENDIAN)

    def assign(self, value) -> None:
        if value > self.range_high:
            value = self.range_high
        elif value < self.range_low:
            value = self.range_low
        self.value = value
        byte_array = self.__convert_value_to_bytearray(value)
        self.set_byte_array(byte_array)

class ZbeeEUI(Mutable):

    def __init__(self, value=0, type_name=EUIPREFIX) -> None:
        self.type_name = type_name
        self.type_prefix = EUIPREFIX
        self.typecode = 0xf0
        self.value = value
        self.n_bytes = EUI_OCTETS
        self.n_minimum_bytes = self.n_bytes
        byte_array = self.__convert_value_to_bytearray(value)
        super().__init__(byte_array)
        self.range_low = 0x0
        self.range_high = 0xffffffffffffffff
    
    def copy(self):
        return ZbeeEUI(self.value, self.type_name)
    
    def __convert_value_to_bytearray(self, value):
        byte_array = bytearray(value.to_bytes(EUI_OCTETS, DEFAULT_ENDIAN))
        return byte_array

    def assign(self, value) -> None:
        if value > self.range_high:
            value = self.range_high
        elif value < self.range_low:
            value = self.range_low
        byte_array = self.__convert_value_to_bytearray(value)
        self.set_byte_array(byte_array)
        self.value = value

class ZbeeKey(Mutable):

    def __init__(self, value=0, type_name=KEYPREFIX) -> None:
        self.type_name = type_name
        self.type_prefix = KEYPREFIX
        self.n_bytes = 8
        self.n_minimum_bytes = self.n_bytes
        self.typecode = 0xf1
        self.value = value
        byte_array = self.__convert_value_to_bytearray(value)
        super().__init__(byte_array)
        self.range_low = 0x0
        self.range_high = int((1 << (self.n_bytes * 8)) - 1)
    
    def copy(self):
        return ZbeeUInt(self.value, self.type_name)

    def refresh_value(self):
        assert(self.octets == self.n_bytes == 8)
        self.value = int.from_bytes(self.byte_array, DEFAULT_ENDIAN)

    def __convert_value_to_bytearray(self, value:'int'):
        return bytearray(value.to_bytes(self.n_bytes, DEFAULT_ENDIAN))

    def assign(self, value) -> None:
        if value > self.range_high:
            value = self.range_high
        elif value < self.range_low:
            value = self.range_low
        self.value = value
        byte_array = self.__convert_value_to_bytearray(value)
        self.set_byte_array(byte_array)

class ZbeeString(Mutable):
    """
    We simply treat string as a list of uint8
    Initially, we set the string as "00"
    Note that in Zigbee, each string is prefixed with an 8-bit integer denoting its
    """

    def __init__(self, value=[]):
        self.type_name = STRINGPREFIX
        self.type_prefix = STRINGPREFIX
        self.typecode = 0x42
        self.value = value
        self.n_minimum_bytes = 1
        byte_array = self.__convert_value_to_bytearray(value)
        self.n_bytes = len(byte_array)
        super().__init__(byte_array)
    
    def copy(self):
        return ZbeeString(self.value)

    def refresh_value(self):
        assert(self.octets == len(self.byte_array) == self.byte_array[0]+1)
        self.value = []
        for i in range(self.octets):
            self.value.append(self.byte_array[i])
        self.n_bytes = self.octets

    def __convert_value_to_bytearray(self, value):
        """
        We accept two types of inputs from users as values:
        (1) A list of uint8
        (2) A string like "Hello world"
        Eventually case (2) will also be transformed to case (1)
        """ 
        if isinstance(value, str):
            input_str = value
            value = []
            for ch in input_str:
                value.append(ord(ch))
            if len(value) > 0:
                value = [len(value)] + value
        
        check_flags = []
        for val in value: # Check if each val is within uint8 range, i.e., [0x0, 0xff]
            check_flags.append(val >= 0x0 and val <= 0xff)
        assert(all(check_flags))
        return bytearray(value)

    def assign(self, value) -> None:
        self.value = value
        byte_array = self.__convert_value_to_bytearray(value)
        self.set_byte_array(byte_array)

    def identify_sensitive_positions(self):
        """
        Given a payload, this function identifies the byte positions which are insensitive to format errors.
        The following cases are format-sensitive.
        (1) String length.
        """
        return [0]

class ZbeeOctString(Mutable):
    """
    We simply treat string as a list of uint8
    Initially, we set the string as "00"
    Note that in Zigbee, each string is prefixed with an 8-bit integer denoting its
    """

    def __init__(self, value=[]):
        self.type_name = OCTSTRINGPREFIX
        self.type_prefix = OCTSTRINGPREFIX
        self.typecode = 0x41
        self.value = value
        self.n_minimum_bytes = 1
        byte_array = self.__convert_value_to_bytearray(value)
        self.n_bytes = len(byte_array)
        super().__init__(byte_array)
    
    def copy(self):
        return ZbeeString(self.value)

    def refresh_value(self):
        assert(self.octets == len(self.byte_array) == self.byte_array[0]+1)
        self.value = []
        for i in range(self.octets):
            self.value.append(self.byte_array[i])
        self.n_bytes = self.octets

    def __convert_value_to_bytearray(self, value):
        """
        We accept two types of inputs from users as values:
        (1) A list of uint8
        (2) A string like "Hello world"
        Eventually case (2) will also be transformed to case (1)
        """ 
        if isinstance(value, str):
            input_str = value
            value = []
            for ch in input_str:
                value.append(ord(ch))
            if len(value) > 0:
                value = [len(value)] + value
        
        check_flags = []
        for val in value: # Check if each val is within uint8 range, i.e., [0x0, 0xff]
            check_flags.append(val >= 0x0 and val <= 0xff)
        assert(all(check_flags))
        return bytearray(value)

    def assign(self, value) -> None:
        self.value = value
        byte_array = self.__convert_value_to_bytearray(value)
        self.set_byte_array(byte_array)

    def identify_sensitive_positions(self):
        """
        Given a payload, this function identifies the byte positions which are insensitive to format errors.
        The following cases are format-sensitive.
        (1) String length.
        """
        return [0]

class ZbeeStruct(Mutable):
    # Currently, Struct does not support to encode Array/Struct inside it.
    def __init__(self, value:'list[Mutable]'=[], type_name=STRUCTPREFIX) -> None:
        assert(len(value) > 0)
        self.type_name = type_name
        self.type_prefix = STRUCTPREFIX
        self.typecode = 0x4c
        self.value = value
        self.n_minimum_bytes = self.calculate_minimum_bytes()
        byte_array = self.__convert_value_to_bytearray(value)
        self.n_bytes = len(byte_array)
        super().__init__(byte_array)
    
    def calculate_minimum_bytes(self):
        n_bytes = 0
        for element in self.value:
            n_bytes += element.n_minimum_bytes
        return n_bytes
    
    def copy(self):
        copied_value = [x.copy() for x in self.value]
        return ZbeeStruct(copied_value, self.type_name)
    
    def refresh_value(self):
        n_consumed_bytes = 0
        for element in self.value:
            n_needed_bytes = 0
            if element.type_prefix in DATA_NUMERIC_TYPES:
                n_needed_bytes = element.n_bytes
            elif element.type_prefix in STRING_TYPES:
                # When meeting string-type element: The number of allocated bytes depends on its length
                n_needed_bytes = self.byte_array[n_consumed_bytes] + 1
            elif element.type_prefix == VARIABLEPREFIX:
                # When meeting variable-type element: Allocate all remaining bytes
                n_needed_bytes = self.octets - n_consumed_bytes
            else:
                assert(0)
            assert(n_consumed_bytes + n_needed_bytes <= self.octets)
            element.set_byte_array(bytearray(self.byte_array[n_consumed_bytes:n_consumed_bytes+n_needed_bytes]))
            element.refresh_value()
            n_consumed_bytes += n_needed_bytes
        self.n_bytes = self.octets
    
    def determine_n_construction_bytes(self, byte_array:'bytearray'):
        """
        According to the struct definition and the byte_array, determine how many bytes are needed to fill in self.
        If the length of byte_array is not needed, just return a very large number of integers to inform of the insufficient bytes.
        """
        n_consumed_bytes = 0
        for element in self.value:
            n_needed_bytes = 0
            if element.type_prefix in DATA_NUMERIC_TYPES:
                n_needed_bytes = element.n_bytes
            elif element.type_prefix in STRING_TYPES:
                # When meeting string-type element: The number of allocated bytes depends on its length
                n_needed_bytes = byte_array[n_consumed_bytes] + 1
            elif element.type_prefix == VARIABLEPREFIX:
                # When meeting variable-type element: Allocate all remaining bytes
                n_needed_bytes = self.octets - n_consumed_bytes
            else:
                assert(0)
            if n_consumed_bytes + n_needed_bytes > len(byte_array):
                return 10000
            n_consumed_bytes += n_needed_bytes
        return n_consumed_bytes

    def __convert_value_to_bytearray(self, value:'list[Mutable]'):
        object_check_flags = [isinstance(x, Mutable) for x in value]
        assert(all(object_check_flags)) # Make sure each element is a Mutable object
        element_check_flags = [x.type_prefix not in [STRUCTPREFIX, ARRAYPREFIX] for x in value]
        assert(all(element_check_flags)) # Currently, Struct does not support to encode Array/Struct inside it.
        byte_array = bytearray()
        for val in value:
            byte_array += val.byte_array
        return byte_array
    
    def assign(self, value:'list[Mutable]'):
        self.value = value
        byte_array = self.__convert_value_to_bytearray(value)
        self.set_byte_array(byte_array)
    
    def identify_sensitive_positions(self):
        """
        Given a payload, this function identifies the byte positions which are insensitive to format errors.
        The following cases are format-sensitive.
        (1) String length.
        """
        cur_pos = 0
        sensitive_pos = []
        for element in self.value:
            if element.type_prefix in STRING_TYPES:
                sensitive_pos.append(cur_pos)
            cur_pos += element.octets
        return sensitive_pos

class ZbeeArray(Mutable):

    def __init__(self, value=[], type_name=ARRAYPREFIX) -> None:
        assert(len(value) > 0)
        self.type_prefix = ARRAYPREFIX
        self.type_name = type_name
        self.typecode = 0x48
        self.value = value
        self.length = len(value)
        self.n_minimum_bytes = value[0].n_minimum_bytes
        byte_array = self.__convert_value_to_bytearray(value)
        self.n_bytes = len(byte_array)
        super().__init__(byte_array)

    def copy(self):
        copied_value = [x.copy() for x in self.value]
        return ZbeeArray(copied_value, self.type_name)

    def refresh_value(self):
        assert(self.octets > 0) # We don't want the array to be empty; Otherwise we cannot recover the element type.
        n_consumed_bytes = 0
        new_value = []
        while self.octets - n_consumed_bytes > 0:
            element = self.value[0].copy()
            n_needed_bytes = 0
            if element.type_prefix in DATA_NUMERIC_TYPES:
                n_needed_bytes = element.n_bytes
            elif element.type_prefix in STRING_TYPES:
                # When meeting string-type element: The number of allocated bytes depends on its length
                n_needed_bytes = self.byte_array[n_consumed_bytes] + 1
            elif element.type_prefix == STRUCTPREFIX:
                n_needed_bytes = element.determine_n_construction_bytes(bytearray(self.byte_array[n_consumed_bytes:]))
            elif element.type_prefix == VARIABLEPREFIX:
                # When meeting variable-type element: Allocate all remaining bytes
                n_needed_bytes = self.octets - n_consumed_bytes
            else:
                assert(0)
            assert(n_consumed_bytes + n_needed_bytes <= self.octets)
            element.set_byte_array(bytearray(self.byte_array[n_consumed_bytes:n_consumed_bytes+n_needed_bytes]))
            element.refresh_value()
            n_consumed_bytes += n_needed_bytes
            new_value.append(element)
        self.value = new_value
        self.length = len(new_value)
        self.n_bytes = self.octets

    def __convert_value_to_bytearray(self, value:'list[Mutable]'):
        object_check_flags = [isinstance(x, Mutable) for x in value]
        assert(all(object_check_flags)) # Make sure each element is a Mutable object
        element_check_flags = [x.type_prefix not in [ARRAYPREFIX] for x in value]
        assert(all(element_check_flags)) # Currently, Array does not support nested Array.
        assert(len(value) == 0 or len(set([type(x) for x in value])) == 1) # Also, make sure all elements in the array should be the same
        byte_array = bytearray()
        for val in value:
            byte_array += val.byte_array
        return byte_array

    def assign(self, value:'list[Mutable]'):
        self.value = value
        self.length = len(value)
        byte_array = self.__convert_value_to_bytearray(value)
        self.set_byte_array(byte_array)

    def identify_sensitive_positions(self):
        """
        Given a payload, this function identifies the byte positions which are insensitive to format errors.
        The following cases are format-sensitive.
        (1) String length.
        """
        cur_pos = 0
        sensitive_pos = []
        if self.value[0].type_prefix in STRING_TYPES:
            for element in self.value:
                sensitive_pos.append(cur_pos)
                cur_pos += element.octets
        elif self.value[0].type_prefix == STRUCTPREFIX:
            for element in self.value:
                struct_sensitive_pos = element.identify_sensitive_positions()
                for pos in struct_sensitive_pos:
                    sensitive_pos.append(cur_pos+pos)
                cur_pos += element.octets
        return sensitive_pos

class ZbeeVariable(Mutable):
    """
    Variant of ZbeeString which removes the first-byte-length requirement
    """
    def __init__(self, value=[]):
        self.type_name = VARIABLEPREFIX
        self.type_prefix = VARIABLEPREFIX
        self.typecode = 0x41
        self.value = value
        self.octets = len(self.value)
        self.n_minimum_bytes = 0
        byte_array = self.__convert_value_to_bytearray(value)
        self.n_bytes = len(byte_array)
        super().__init__(byte_array)
    
    def copy(self):
        return ZbeeVariable(self.value)

    def refresh_value(self):
        self.value = []
        for i in range(self.octets):
            self.value.append(self.byte_array[i])
        self.n_bytes = self.octets

    def __convert_value_to_bytearray(self, value):
        """
        We accept two types of inputs from users as values:
        (1) A list of uint8
        (2) A string like "Hello world"
        Eventually case (2) will also be transformed to case (1)
        """ 
        if isinstance(value, str):
            input_str = value
            value = []
            for ch in input_str:
                value.append(ord(ch))
        
        check_flags = []
        for val in value: # Check if each val is within uint8 range, i.e., [0x0, 0xff]
            check_flags.append(val >= 0x0 and val <= 0xff)
        assert(all(check_flags))
        return bytearray(value)

    def assign(self, value) -> None:
        byte_array = self.__convert_value_to_bytearray(value)
        self.set_byte_array(byte_array)
        self.value = value
        self.octets = len(byte_array)

