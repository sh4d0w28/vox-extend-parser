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

    # print('chunk:', chunkId, 'content:', chunkContentLenght, 'child:', childContentLenght)
    
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
    return kids

readFileHeader(file)
chunkMain = readChunk(file)

chunks = chunkMain['kids']

model_ind = 0
models = {}
singleModel = {}

nodes = {}

for chunk in chunks:
    ## chunk = {'chunkId': 'SIZE', 'body': {'x': 1, 'y': 1, 'z': 1}}
    
    if chunk['chunkId'] == 'SIZE':
        singleModel['size'] = chunk['body']
    elif chunk['chunkId'] == 'XYZI':
        singleModel['numVoxels'] = chunk['body']['numVoxels']
        singleModel['voxels'] = chunk['body']['voxels']
        models[model_ind] = singleModel
        model_ind += 1
    elif chunk['chunkId'] == 'nTRN' or chunk['chunkId'] == 'nGRP' or chunk['chunkId'] == 'nSHP':
        nodes[chunk['body']['nodeId']] = chunk
    elif chunk['chunkId'] == 'LAYR':
        continue
    else:
        print('SKIP', chunk)

## add parents
for node_ind in nodes:
    thisNode = nodes[node_ind]
    if 'childNodeId' in thisNode['body']:
        nodes[thisNode['body']['childNodeId']]['parentNodeId'] = node_ind
    elif 'childNodeIds' in thisNode['body']:
        for kidNode in thisNode['body']['childNodeIds']:
            nodes[kidNode]['parentNodeId'] = node_ind

#reverseHierarchy ( for each leaf collect all frames )
for node_ind in nodes:
    thisNode = nodes[node_ind]
    if thisNode['chunkId'] == 'nSHP':
        frames = []
        while 'parentNodeId' in thisNode:
            thisNode = nodes[thisNode['parentNodeId']]
            if 'frames' in thisNode['body']:
                frames += thisNode['body']['frames']
        nodes[node_ind]['fullFrames'] = frames

print('------------------------------ NODES ------------------------------')
for node_ind in nodes:
    if nodes[node_ind]['chunkId'] != 'nSHP':
        continue
    print(node_ind, nodes[node_ind])

print('------------------------------ MODELS -----------------------------')
for model_ind in models:
    print(model_ind, models[model_ind])

exit(0)