#pragma endian big

import std.io;
import std.mem;

struct Shader
{
    char name[];
    padding[4];
};

struct ObjectName {
    char name[0x20];
};

struct FileHeader
{
    u32 shaderCount;
    Shader shaders[shaderCount];
    
    u32 objectCount;
    ObjectName nameTable[objectCount];
    padding[4];
};

FileHeader header @ 0x00;

struct MeshHeader {
    char animationData[header.objectCount*48];
    padding[4];

    u32 vertexStride;
    u32 verticesSize;
    u32 vertexCount = verticesSize/vertexStride;
};

MeshHeader meshHeader @ std::mem::find_sequence(0x00, 0x3F, 0x80, 0x00, 0x00, 0x3F, 0x80, 0x00, 0x00, 0x3F, 0x80);

struct Vertex {
    float x;
    float y;
    float z;
    
    padding[meshHeader.vertexStride-12];
};

struct MeshData {
    Vertex vertices[meshHeader.vertexCount];
    
    u32 indicesSize;
    u32 indexStride;
    u32 indexCount = indicesSize/indexStride;
    
    u16 indices[indexCount];
    
    padding[4]; // index count again
} [[hex::visualize("3d", vertices, indices)]];

MeshData data @ addressof(meshHeader) + sizeof(meshHeader);