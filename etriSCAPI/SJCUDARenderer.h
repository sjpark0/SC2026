#pragma once
#include "SJCUDACommon.h"

class SJCUDARenderer
{
protected:
	CUDA_UCHAR* m_pMPICUDA;
	CUDA_UCHAR* m_pMPIIdxCUDA;
	CUDA_FLOAT* m_pC2WCUDA;
	CUDA_FLOAT* m_pW2CCUDA;
	CUDA_FLOAT* m_pCIFCUDA;

	CPU_UCHAR* m_pMPI;
	CPU_UCHAR* m_pMPIIdx;
	CPU_FLOAT* m_pC2W;
	CPU_FLOAT* m_pW2C;
	CPU_FLOAT* m_pCIF;
	SJDim* m_pMPIDim;
	SJDim* m_pDim;
	SJDim m_iWidth;
	SJDim m_iHeight;
	CPU_FLOAT m_fFocal;
	int   m_numBlend;
	int   m_numLevel;
	int   m_numFactor;
	int* m_pThreshold;
	int   m_Threshold;

	CUDA_FLOAT* m_pPoseArrCUDA;
	CUDA_INT* m_pBlendIDCUDA;
	CUDA_FLOAT* m_pWeightsCUDA;
	CUDA_INT* m_pLevelCUDA;

	CPU_FLOAT* m_pDistance;
	CPU_INT* m_pBlendID;
	CPU_FLOAT* m_pWeights;

	bool bCompressed;
	SJDim iDivUp(SJDim a, SJDim b);

public:
	SJCUDARenderer();
	~SJCUDARenderer();
	int Initialize(SJDim* pDim, SJDim* pMPIDim, CPU_FLOAT* pC2WCPU, CUDA_FLOAT* pC2WCUDA, CPU_FLOAT* pW2CCPU, CUDA_FLOAT* pW2CCUDA, CPU_FLOAT* pCIFCPU, CUDA_FLOAT* pCIFCUDA);
	int LoadMPI(CPU_UCHAR* pMPICPU, CUDA_UCHAR* pMPICUDA);
	int LoadCompressedMPI(CPU_UCHAR* pCompressedMPICPU, CUDA_UCHAR* pCompressedMPICUDA, CPU_UCHAR* pCompressedIdxCPU, CUDA_UCHAR* pCompressedIdxCUDA);
	int InitializeRendering(SJDim outWidth, SJDim outHeight, int numBlend);
	int Rendering(float* pose_arr, CUDA_UCHAR* pOutImageCUDA, CPU_UCHAR* pOutImageCPU);
	int Finalize();
};

