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

// Note that this Vertex struct has to be changed depending on the Vertex Stride.
// There is no one-size-fits-all struct.
struct Vertex {
    float x;
    float y;
    float z;
    
    padding[4]; // normal
    padding[4]; // tangent
    
    padding[2]; // U (half float, not supported by imhex)
    padding[2]; // V (half float, not supported by imhex)
    
    padding[8];// unsure what this is
};

struct MeshHeader
{
    u32 shaderCount;
    Shader shaders[shaderCount];
    
    u32 objectCount;
    ObjectName nameTable[objectCount];
    padding[4];
};

MeshHeader header @ 0x00;

struct MeshData {
    u32 vertexStride;
    u32 verticesSize;
    u32 vertexCount = verticesSize/vertexStride;
    
    Vertex vertices[vertexCount];
    
    u32 indicesSize;
    u32 indexStride;
    u32 indexCount = indicesSize/indexStride;
    
    u16 indices[indexCount];
    
    padding[4]; // index count again
} [[hex::visualize("3d", vertices, indices)]];

// TODO: need to figure out how to not hardcode -33. It needs to be ()vertexStride + 8)
MeshData meshData @ std::mem::find_sequence(0x00, 0x00, 0x03, 0xFF, 0x00, 0x00, 0x00) - 33;