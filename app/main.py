from io import BufferedReader
import global_conf

from chunkreader import *
from typereader import readInt32

file = open('voxfiles/2px.vox', 'rb')

# Read 4 bytes as chars
def readChunkId(file:BufferedReader) -> str:
    global_conf.bytesRead += 4
    return file.read(4).decode('utf-8')

# 1. File Structure : RIFF style
# -------------------------------------------------------------------------------
# # Bytes  | Type       | Value
# -------------------------------------------------------------------------------
# 1x4      | char       | id 'VOX ' : 'V' 'O' 'X' 'space', 'V' is first
# 4        | int        | version number : 150
def readFileHeader(file:BufferedReader):
    vox_ = readChunkId(file)
    if(vox_ != 'VOX '):
        print('[VOX ] not found. wrong file') 
        exit(1)
    else: 
        print('[VOX ] found.... ')

    version = readInt32(file)
    print('file version', version)

# 2. Chunk Structure
# -------------------------------------------------------------------------------
# # Bytes  | Type       | Value
# -------------------------------------------------------------------------------
# 1x4      | char       | chunk id
# 4        | int        | num bytes of chunk content (N)
# 4        | int        | num bytes of children chunks (M)

# N        |            | chunk content

# M        |            | children chunks
# -------------------------------------------------------------------------------
def readChunk(file:BufferedReader):
    result = {}
    chunkId = readChunkId(file)
    result['chunkId'] = chunkId

    chunkContentLenght = readInt32(file)
    childContentLenght = readInt32(file)

    print('chunk:', chunkId, 'content:', chunkContentLenght, 'child:', childContentLenght)
    
    if chunkContentLenght > 0:
        body = readChunkBody(chunkId, file)
        result['body'] = body
    
    if childContentLenght > 0:
        child = readChild(file, childContentLenght)
        result['kids'] = child

    return result
        
def readChunkBody(chunkId, file:BufferedReader) -> dict:
    if chunkId == 'SIZE':
        return read_SIZE(file)
    elif chunkId == 'XYZI':
        return read_XYZI(file)
    elif chunkId == 'nTRN':
        return read_nTRN(file)
    elif chunkId == 'nGRP':
        return read_nGRP(file)
    elif chunkId == 'nSHP':
        return read_nSHP(file)
    elif chunkId == 'LAYR':
        return read_LAYR(file)
    elif chunkId == 'RGBA':
        return read_RGBA(file)
    else:
        print(chunkId)

def readChild(file:BufferedReader, childContentLenght):
    curpos = global_conf.bytesRead
    kids = []
    while global_conf.bytesRead < childContentLenght + curpos:
        data = readChunk(file)
        kids.append(data)
        print('read: ',global_conf.bytesRead, 'limit: ', childContentLenght + curpos)
    return kids

readFileHeader(file)
cg = readChunk(file)

print(cg)
exit(0)