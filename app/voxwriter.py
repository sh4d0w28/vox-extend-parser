
### model = {'size': {'x': 2, 'y': 2, 'z': 2}, 'numVoxels': 4, 'voxels': [{'x': 1, 'y': 0, 'z': 0, 'ci': 65}, {'x': 1, 'y': 1, 'z': 0, 'ci': 65}, {'x': 0, 'y': 1, 'z': 0, 'ci': 65}, {'x': 1, 'y': 1, 'z': 1, 'ci': 65}]}

def generateVoxFileByModel(name, model) -> bytearray:

    #SIZECHUNK
    sizeChunkBody = bytearray()
    sizeChunkBody += model['size']['x'].to_bytes(4, byteorder='little')
    sizeChunkBody += model['size']['y'].to_bytes(4, byteorder='little')
    sizeChunkBody += model['size']['z'].to_bytes(4, byteorder='little')

    sizeChunk = bytearray()  ## [SIZEintintnit]
    sizeChunk += "SIZE".encode()
    sizeChunk += len(sizeChunkBody).to_bytes(4, byteorder='little')
    sizeChunk += (0).to_bytes(4, byteorder='little')
    sizeChunk += sizeChunkBody


    xyziChunkBody = bytearray()
    xyziChunkBody += model['numVoxels'].to_bytes(4, byteorder='little')
    for vox in model['voxels']:
        xyziChunkBody += vox['x'].to_bytes(1, byteorder='little')
        xyziChunkBody += vox['y'].to_bytes(1, byteorder='little')
        xyziChunkBody += vox['z'].to_bytes(1, byteorder='little')
        xyziChunkBody += vox['ci'].to_bytes(1, byteorder='little')


    xyziChunk = bytearray()
    xyziChunk += "XYZI".encode()
    xyziChunk += len(xyziChunkBody).to_bytes(4, byteorder='little')
    xyziChunk += (0).to_bytes(4, byteorder='little')
    xyziChunk += xyziChunkBody

    mainChunk = bytearray()  ## [MAIN0XXXXX]
    mainChunk += "MAIN".encode()
    mainChunk += (0).to_bytes(4, byteorder='little')
    mainChunk += (len(sizeChunk) + len(xyziChunk)).to_bytes(4, byteorder='little')
    mainChunk += sizeChunk
    mainChunk += xyziChunk

    fileContent = bytearray()
    fileContent += "VOX ".encode()
    fileContent += (150).to_bytes(4, byteorder='little')

    fileContent += mainChunk

    file = open(name+'.vox', 'wb')
    file.write(fileContent)
    file.close()
