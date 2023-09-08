from typereader import *

def read_SIZE(file:BufferedReader) -> dict:
    res = {}
    x = readInt32(file)
    res['x'] = x
    y = readInt32(file)
    res['y'] = y
    z = readInt32(file)
    res['z'] = z
    return res

def read_LAYR(file:BufferedReader):
    res = {}
    layerId = readInt32(file)
    res['layerId'] = layerId

    attrs = readDict(file)
    res['attrs'] = attrs

    reserved = readInt32(file)
    if reserved != -1:
        print('ERROR RESERVED NOT -1')
        exit(1)
    
    return res

def read_RGBA(file:BufferedReader):
    res = {}
    colors = [];
    for i in range(255):
        color = readColor(file)
        colors.append(color)
    res['colors'] = colors
    return res


def read_nTRN(file:BufferedReader):
    res = {}

    nodeId = readInt32(file)
    res['nodeId'] = nodeId

    attrs = readDict(file)
    res['attrs'] = attrs
    
    childNodeId = readInt32(file)
    res['childNodeId'] = childNodeId

    reservedid =  readInt32(file)
    if reservedid != -1:
        print('reserved not -1')
        exit(1)
    
    layerId = readInt32(file)
    res['layerId'] = layerId

    framesAmount = readInt32(file)
    frames = []
    for i in range(framesAmount):
        dict = readDict(file)
        if dict:
            frames.append(dict)
    res['frames'] = frames
    return res

def read_nGRP(file:BufferedReader) -> []:
    res = {}

    nodeId = readInt32(file)
    res['nodeId'] = nodeId

    attrs = readDict(file)
    res['attrs'] = attrs
   
    kidsAmount = readInt32(file)
    kids = []
    for kid in range(kidsAmount):
        childid = readInt32(file)
        kids.append(childid)
    
    res['childNodeIds'] = kids
    return res  

def read_nSHP(file:BufferedReader):
    res = {}

    nodeId = readInt32(file)
    res['nodeId'] = nodeId

    attrs = readDict(file)
    res['attrs'] = attrs
   
    modelsAmount = readInt32(file)

    models = []
    for model in range(modelsAmount):
        model = {}

        modelId = readInt32(file)
        model['modelId'] = modelId

        modelAttrs = readDict(file)
        model['modelAttrs'] = modelAttrs

        models.append(model)

    res['models'] = models
    
    return res

def read_XYZI(file:BufferedReader) -> []:
    numVoxels = readInt32(file)
    voxels = []
    for i in range(numVoxels):
        x = readByte(file)
        y = readByte(file)
        z = readByte(file)
        ci = readByte(file)
        voxels.append({'x':x,'y':y,'z':z,'ci':ci})
    return {'numVoxels':numVoxels, 'voxels':voxels}