import global_conf
from io import BufferedReader

# Read byte as a number
# -------------------------------------------------------------------------------
# Bytes  | Type       | Value
# -------------------------------------------------------------------------------
# 1      | byte       | single byte number
# -------------------------------------------------------------------------------
def readByte(file:BufferedReader) -> int:
    global_conf.bytesRead += 1
    return int.from_bytes(file.read(1),'little')

# Read Int32 value
# -------------------------------------------------------------------------------
# Bytes  | Type       | Value
# -------------------------------------------------------------------------------
# 4      | byte       | single int number
# -------------------------------------------------------------------------------
def readInt32(file:BufferedReader) -> int:
    global_conf.bytesRead += 4
    i = int.from_bytes(file.read(4),'little')
    if i == 4294967295: # FFFFFFFF -> -1 
        return -1
    else:
        return i
    
# Read color value as HEX color ( no alpha, no prefix )
# -------------------------------------------------------------------------------
# Bytes  | Type       | Value
# -------------------------------------------------------------------------------
# 1 x 4  | byte       | (R, G, B, A) : 1 byte for each component
# -------------------------------------------------------------------------------
def readColor(file: BufferedReader):
    r = readByte(file)
    g = readByte(file)
    b = readByte(file)
    a = readByte(file)    
    return "{:02x}{:02x}{:02x}".format(r,g,b)

# EXTEND: STRING type
# -------------------------------------------------------------------------------
# Bytes  | Type       | Value
# -------------------------------------------------------------------------------
# 4      | byte       | string length in bytes ( N )
# 1 x N  | byte       | string content
# -------------------------------------------------------------------------------
def readString(file:BufferedReader):
    strlen = readInt32(file)
    strcontent = file.read(strlen).decode()
    global_conf.bytesRead += strlen
    return strcontent;

# EXTEND: DICT type
# -------------------------------------------------------------------------------
# Bytes    | Type       | Value
# -------------------------------------------------------------------------------
# 4        | byte       | number of key-value pairs ( N )
# PAIR x N | PAIR       | pairs
# -------------------------------------------------------------------------------
# EXTEND: PAIR (key-value pair)
# {
#   EXTEND:STRING	: key
#   EXTEND:STRING	: value
# } x N
#
def readDict(file:BufferedReader):
    keyValuePairsAmount = readInt32(file)
    if keyValuePairsAmount == 0:
        return None
    
    keyValuePairs = {}
    for i in range(keyValuePairsAmount):
        key = readString(file)
        value = readString(file)
        keyValuePairs[key] = value
    return keyValuePairs
