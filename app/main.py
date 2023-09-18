from io import BufferedReader
import global_conf

from json import dumps
from copy import copy
from chunkreader import *
from typereader import readInt32
from voxwriter import generateVoxFileByModel

file = open('voxfiles/test-copy.vox', 'rb')

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
        print('chunkId unknown: ', chunkId)

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
    if chunk['chunkId'] == 'SIZE':
        singleModel['size'] = chunk['body']
    elif chunk['chunkId'] == 'XYZI':
        singleModel['numVoxels'] = chunk['body']['numVoxels']
        singleModel['voxels'] = chunk['body']['voxels']
        models[model_ind] = copy(singleModel)
        model_ind += 1
    elif chunk['chunkId'] == 'nTRN' or chunk['chunkId'] == 'nGRP' or chunk['chunkId'] == 'nSHP':
        nodes[chunk['body']['nodeId']] = chunk
        print('NID', chunk['body']['nodeId'], chunk)
    elif chunk['chunkId'] == 'LAYR':
        continue
    elif chunk['chunkId'] == 'RGBA':
        continue
    else:
        print('SKIP', chunk)

## add parents
for node_ind in nodes:
    thisNode = nodes[node_ind]
    if 'childNodeId' in thisNode['body']:

        if 'parentNodeId' not in nodes[thisNode['body']['childNodeId']]:
            nodes[thisNode['body']['childNodeId']]['parentNodeId'] = []    

        nodes[thisNode['body']['childNodeId']]['parentNodeId'].append(node_ind)
    elif 'childNodeIds' in thisNode['body']:
        for kidNode in thisNode['body']['childNodeIds']:
            if 'parentNodeId' not in nodes[kidNode]:
                nodes[kidNode]['parentNodeId'] = []    

            nodes[kidNode]['parentNodeId'].append(node_ind)


shp_nodes = []
for node_ind in nodes:
    if nodes[node_ind]['chunkId'] != 'nSHP':
        continue
    if 'parentNodeId' not in nodes[node_ind]:
        continue
    for parent in nodes[node_ind]['parentNodeId'] :
        copyNode = copy(nodes[node_ind])
        copyNode['parentNodeId'] = [parent]
        shp_nodes.append(copyNode)

#reverseHierarchy ( for each leaf collect all frames )
for node in shp_nodes:
    frames = []
    name = ''
    thisNode = copy(node)
    while 'parentNodeId' in thisNode:
        thisNode = nodes[thisNode['parentNodeId'][0]]
        if 'frames' in thisNode['body']:
            frames += thisNode['body']['frames']
        if thisNode['body']['attrs']:
            if '_name' in thisNode['body']['attrs']:
                name += thisNode['body']['attrs']['_name'] + '_'
    node['fullFrames'] = frames
    if name != '':
        node['name'] = name


res = {}
print('------------------------------ MODELS -----------------------------')
res['models'] = {}
for model_ind in models:
    print('models', model_ind, models[model_ind])
    generateVoxFileByModel("splitvox/model"+str(model_ind), models[model_ind])
    res['models'][str(model_ind)] = 'model'+str(model_ind)+'.vox'

print('------------------------------ NODES ------------------------------')
res['scene'] = []
for node in shp_nodes:
    modelId = node['body']['models'][0]['modelId']
    frames = node['fullFrames']
    dx = 0
    dy = 0
    dz = 0
    ra = 0
    if len(frames) > 0:
        if '_t' in frames[0]:
            ts = frames[0]['_t'].split(' ')
            dx = int(ts[0])
            dy = int(ts[1])
            dz = int(ts[2])
        if '_r' in frames[0]:
            ra = frames[0]['_r']


    res['scene'].append({
        "model":modelId,
        "dx":dx,
        "dy":dy,
        "dz":dz,
        "ra":ra
    })
print(res)

json_object = dumps(res)

fileresult = open("splitvox/result.json","w")
fileresult.write(json_object)
