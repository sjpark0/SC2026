#pragma once
#include <cstddef>
class SJCUDARenderer;
extern "C" {
	SJCUDARenderer* SJCUDARenderer_New();	
	int SJCUDARenderer_Initialize(SJCUDARenderer *renderer, size_t* pDim, size_t* pMPIDim, float* pC2WCPU, float* pC2WCUDA, float* pW2CCPU, float* pW2CCUDA, float* pCIFCPU, float* pCIFCUDA);
	int SJCUDARenderer_LoadMPI(SJCUDARenderer* renderer, unsigned char* pMPICPU, unsigned char* pMPICUDA);
	int SJCUDARenderer_LoadCompressedMPI(SJCUDARenderer* renderer, unsigned char* pCompressedMPICPU, unsigned char* pCompressedMPICUDA, unsigned char* pCompressedIdxCPU, unsigned char* pCompressedIdxCUDA);
	int SJCUDARenderer_InitializeRendering(SJCUDARenderer* renderer, size_t outWidth, size_t outHeight, int numBlend);
	int SJCUDARenderer_Rendering(SJCUDARenderer* renderer, float* pose_arr, unsigned char* pOutImageCUDA, unsigned char* pOutImageCPU);
	int SJCUDARenderer_Finalize(SJCUDARenderer* renderer);
	int SJCUDARenderer_LoadMPIFromFolder(char* foldername, size_t* pMPIDim, unsigned char* pMPICUDA);
	int SJCUDARenderer_LoadDataFromFolder(char* foldername, size_t* pMPIDim, float* pC2W, float* pC2WCUDA, float* pW2C, float* pW2CCUDA, float* pCIF, float* pCIFCUDA);

	unsigned char* SJCUDARenderer_CUDA_UCHAR_Alloc(size_t size);
	unsigned char* SJCUDARenderer_CPU_UCHAR_Alloc(size_t size);
	float* SJCUDARenderer_CUDA_FLOAT_Alloc(size_t size);
	float* SJCUDARenderer_CPU_FLOAT_Alloc(size_t size);

	void SJCUDARenderer_CUDA_UCHAR_Free(unsigned char* buffer);
	void SJCUDARenderer_CPU_UCHAR_Free(unsigned char* buffer);
	void SJCUDARenderer_CUDA_FLOAT_Free(float* buffer);
	void SJCUDARenderer_CPU_FLOAT_Free(float* buffer);
	float* SJCUDARenderer_GetRenderPath(char* filename);
}