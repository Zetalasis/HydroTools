#pragma endian big

import std.io;

struct Vertex {
    float x;
    float y;
    float z;
    
    // possibly packed bytes for TexCoord, Normal, and Tangent (from Generic.hlsl vertex attributes)
    padding[12];
};

struct Shader {
    char name[];
    padding[4]; // usually D5 00 E0 91
};

struct Model {
    u32 objectCount;
    Shader shaders[objectCount];
    
    u32 vertexStride;
    u32 vertexDataSize;
    u32 vertexCount = vertexDataSize/vertexStride;
    
    Vertex vertices[vertexCount];
    
    u32 indicesDataSize;
    u32 indexStride;
    u32 indexCount = indicesDataSize/indexStride;
    
    u16 indices[indexCount];
    padding[4]; // index count again
} [[hex::visualize("3d", vertices, indices)]];

Model model @ 0x00;