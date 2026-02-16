import struct, math, io, numpy

def in_range(val : float, min : float, max : float) -> bool:
    return (val >= min) and (val <= max)

def getAllOffsets(pattern : bytearray, data : bytes) -> list[int]:
    start_index = 0
    offsets = []
    while True:
        try:
            index = data.find(pattern, start_index)
            if index == -1:
                break

            offsets.append(index)
            start_index = index + len(pattern)
        except ValueError:
            break
    return offsets

def read_str(byte_stream) -> str:
    line = byte_stream.read(1)
    while line and line[-1:] != b'\x00':
        line += byte_stream.read(1)
    return line.rstrip(b'\x00').decode('utf-8') 

def validatePosition(position : tuple[float, float, float], epsilon : float) -> bool:
    for coord in position:
        if (math.isnan(coord)): #  or in_range(coord, -epsilon, epsilon)
            return False
    return True

class AnimatedModel:
    def __init__(self, filename : str, exportedFilename : str|None = None):
        print(f"[+] Opening file '{filename}'...")

        try:
            with open(filename, "rb") as f:
                self.data = f.read()
        except:
            print(f"[-] Failed to open file!")
            return
        
        reader = io.BytesIO(self.data)
        print(f"[+] Opened file successfully!")

        # == HEADER == #
        print("[+] Mesh Info:")

        shaderCount = int.from_bytes(reader.read(4))
        shaders = []

        for _ in range(shaderCount):
            shaders.append(read_str(reader))
            reader.read(4) # shader name end, usually D5 00 E0 91
        print(f" [*] Shader Count: {shaderCount}")

        objectCount = int.from_bytes(reader.read(4))

        objectNameTable = []
        for _ in range(objectCount):
            objectNameTable.append(reader.read(0x20).decode().rstrip('\x00'))
        print(f" [*] Object Count: {objectCount}")

        # == VERTEX DATA == #
        print("[+] Skipping to vertex data...")
        vertexEnds = getAllOffsets(b'\x00\x00\x03\xFF\x00\x00\x00', self.data)

        vertices = []
        uvs = []

        # TODO: remove this hardcoded -32. It's the vertex stride plus 8 bytes for reading vertex stride/vertices size, but we don't know those yet.
        # Ideally, I should figure out what the block of data between the header and the vertex data is, but I'm too lazy for that.
        vertexDataStart = vertexEnds[0]-32
        reader.seek(vertexDataStart)
        print("[+] Vertex data beginning:", vertexDataStart)

        vertexStride = int.from_bytes(reader.read(4))
        verticesSize = int.from_bytes(reader.read(4))
        vertexCount = verticesSize/vertexStride
        if (not vertexCount.is_integer()):
            print("[-] Failed to parse vertex data header!")
            return
        vertexCount = int(vertexCount)

        print(" [*] Vertex Stride:", vertexStride)
        print(" [*] Vertex Data Size:", verticesSize)
        print(" [*] Calculated Vertex Count:", vertexCount)

        for _ in range(vertexCount):
            vertexData = reader.read(vertexStride)
            pos = struct.unpack(">fff", vertexData[:12])
            vertices.append(pos)

            # 4 byte normal
            # 4 byte tangent

            uvData = vertexData[20:24]

            u = numpy.frombuffer(uvData[:2], dtype=">f2")[0]
            v = numpy.frombuffer(uvData[2:], dtype=">f2")[0]

            uvs.append((u, v))

        print(f"[+] Read {len(vertices)} vertices!")

        # == INDICES == #
        print("[+] Reading index data at:", reader.tell())

        indices = []

        indicesSize = int.from_bytes(reader.read(4))
        indexStride = int.from_bytes(reader.read(4))
        indexCount = indicesSize/indexStride
        if (not indexCount.is_integer()):
            print("[-] Failed to parse index data header!")
            return
        indexCount = int(indexCount)

        print(" [*] Index Stride:", indexStride)
        print(" [*] Indices Data Size:", indicesSize)
        print(" [*] Calculated Index Count:", indexCount)

        for _ in range(indexCount):
            indices.append(int.from_bytes(reader.read(2)))

        # == WRITING TO OBJ == #
        meshPath = (filename + ".obj") if exportedFilename == None else exportedFilename
        with open(meshPath, "w") as f:
            for vertex in vertices:
                f.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")

            for uv in uvs:
                f.write(f"vt {uv[0]} {uv[1]}\n")

            for i in range(0, len(indices), 3):
                i0 = indices[i] + 1
                i1 = indices[i+1] + 1
                i2 = indices[i+2] + 1

                f.write(f"f {i0}/{i0} {i1}/{i1} {i2}/{i2}\n")
        print("[+] Wrote exported model to:", meshPath)

class StaticModel:
    def __init__(self, filename : str, exportedFilename : str|None = None):
        print(f"[+] Opening file '{filename}'...")

        try:
            with open(filename, "rb") as f:
                self.data = f.read()
        except:
            print(f"[-] Failed to open file!")
            return
        
        reader = io.BytesIO(self.data)
        print(f"[+] Opened file successfully!")

        objectCount = int.from_bytes(reader.read(4))

        print(f"[+] Model has {objectCount} object(s)")

        shaders = []

        for _ in range(objectCount):
            shaders.append(read_str(reader))
            reader.read(4) # shader type? usually D5 00 E0 91

        vertices = []
        uvs = []

        vertexStride = int.from_bytes(reader.read(4))
        vertexDataSize = int.from_bytes(reader.read(4))
        vertexCount = vertexDataSize/vertexStride

        if (not vertexCount.is_integer()):
            print("[!] Failed to find vertex count!")
            return
        vertexCount = int(vertexCount)

        print("[+] Model Data:")
        print(f" [*] Vertex Stride: {vertexStride}")
        print(f" [*] Vertex Block Size: {vertexDataSize}")
        print(f" [*] Vertex Count: {vertexCount}")

        for _ in range(vertexCount):
            vertexData = reader.read(vertexStride)

            posData = vertexData[:12]
            pos = struct.unpack(">fff", posData)
            vertices.append(pos)

            uvData = vertexData[20:24]

            u = numpy.frombuffer(uvData[:2], dtype=">f2")[0]
            v = numpy.frombuffer(uvData[2:], dtype=">f2")[0]

            uvs.append((u, v))

        indices = []

        indexDataSize = int.from_bytes(reader.read(4))
        indexCount = indexDataSize / 2

        if (not indexCount.is_integer()):
            print("[!] Failed to find index count!")
            return
        indexCount = int(indexCount)

        print(f" [*] Index Count: {indexCount}")

        reader.read(4) # unknown indices padding?

        for _ in range(indexCount):
            indices.append(int.from_bytes(reader.read(2)))

        indexOffset = 1

        modelFilePath = (filename + ".obj") if exportedFilename == None else exportedFilename
        with open(modelFilePath, "w") as f:
            for vertex in vertices:
                f.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")

            for uv in uvs:
                f.write(f"vt {uv[0]} {uv[1]}\n")

            for i in range(0, len(indices), 3):
                i0 = indices[i] + indexOffset
                i1 = indices[i+1] + indexOffset
                i2 = indices[i+2] + indexOffset

                f.write(f"f {i0}/{i0} {i1}/{i1} {i2}/{i2}\n")

        print(f"[+] Successfully exported {filename} to {modelFilePath}")