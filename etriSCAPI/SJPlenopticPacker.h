#pragma once
#include "SJCUDACommon.h"
#include "cuda_runtime.h"

class SJPlenopticPacker
{
private:
	int* m_pLookupImage;
	int* m_pLookupAlphaImage;
	int* m_pLookupAlphaLevel;

	int m_numImage;
	int m_numLayer;

	int m_iDecWidth;
	int m_iDecHeight;

	SJDim* m_pDim;
	SJDim* m_pMPIDim;

	void MakeLookupTableImage(int iDecWidth, int iDecHeight, SJDim numCam, SJDim width, SJDim height, int* pLookupImage);
	void MakeLookupTableLayer(int iDecWidth, int iDecHeight, SJDim numCam, SJDim layerWidth, SJDim layerHeight, SJDim layerLevel, int* pLookupAlphaImage, int* pLookupAlphaLevel);

	dim3 m_thread;
	dim3 m_grid;

	dim3 m_layerThread;
	dim3 m_layerGrid;

public:
	SJPlenopticPacker();
	~SJPlenopticPacker();

	void Initialize(SJDim* pDim, SJDim* pMPIDim, int iDecWidth, int iDecHeight, int numImage, int numLayer);

	void UnPackingImage(CUDA_UCHAR** ppDecOutCUDA, CUDA_UCHAR* pImage);
	void UnPackingImageWithIndex(CUDA_UCHAR* ppDecOutCUDA, CUDA_UCHAR* pImageCUDA, int index);

	void UnPackingImageCPU(SJDim numCam, SJDim width, SJDim height, const CPU_UCHAR** ppDecOut, int iDecWidth, int iDecHeight, int numImage, CPU_UCHAR* pImage);

	void UnPackingImageWithIndex(SJDim numCam, SJDim width, SJDim height, const CPU_UCHAR** ppDecOut, int iDecWidth, int iDecHeight, int numImage, int index, CPU_UCHAR* pImage);
	void UnPackingImageWithIndexCUDA(SJDim numCam, SJDim width, SJDim height, const CUDA_UCHAR** ppDecOutCUDA, int iDecWidth, int iDecHeight, int numImage, int index, CPU_UCHAR* pImage);
	void UnPackingLayer(CUDA_UCHAR** ppDecOutCUDA, CUDA_UCHAR* pLayer);
	void UnPackingLayerCPU(SJDim numCam, SJDim layerWidth, SJDim layerHeight, SJDim layerLevel, const CPU_UCHAR** ppDecOut, int iDecWidth, int iDecHeight, int numLayer, CPU_UCHAR* pLayer);

	void PackingImage(SJDim numCam, SJDim width, SJDim height, CPU_UCHAR** ppDecOut, CUDA_UCHAR** ppDecOutCUDA, int iDecWidth, int iDecHeight, int numImage, CPU_UCHAR* pImage);
	void PackingLayer(SJDim numCam, SJDim layerWidth, SJDim layerHeight, SJDim layerLevel, CPU_UCHAR** ppDecOut, CUDA_UCHAR** ppDecOutCUDA, int iDecWidth, int iDecHeight, int numLayer, CPU_UCHAR* pLayer);

};
