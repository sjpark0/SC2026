#pragma once
#include <cstddef>
//#define RGB_24
//#define VERBOSE
#define NUM_POSSIBLE_CAM 100

#define BLOCKDIM_X 16
#define BLOCKDIM_Y 16

#define MIN(a,b) (((a)<(b))?(a):(b))
#define MAX(a,b) (((a)>(b))?(a):(b))

typedef float CPU_FLOAT;
typedef float CUDA_FLOAT;

typedef int   CPU_INT;
typedef int   CUDA_INT;

typedef unsigned int CPU_UINT;
typedef unsigned int CUDA_UINT;

typedef unsigned char CPU_UCHAR;
typedef unsigned char CUDA_UCHAR;

typedef size_t SJDim;

int SJCUDAMallocHost(void **pOut, SJDim nSizeBytes);
int SJCUDAMallocDevice(void **pOut, SJDim nSizeBytes);
int SJCUDAFreeHost(void *pPtr);
int SJCUDAFreeDevice(void *pPtr);
SJDim iDivUp(SJDim a, SJDim b);
int CUDAReset();
int SJCUDAMemcpyD2H(void *pOut, void *pSrc, SJDim nSizeBytes);
int SJCUDAMemcpyH2D(void *pOut, void *pSrc, SJDim nSizeBytes);