#include "SJCUDARenderer.h"
#include "SJLog.h"
#include "SJPlenopticPacker.h"

#include "cuda_runtime.h"
#include "device_launch_parameters.h"
#include "helper_cuda.h"

__global__ void RenderingCompressed(const uchar3* srcImg, const unsigned char* srcAlpha, uchar3* dstRGB, SJDim imageW, SJDim imageH, SJDim originImageW, SJDim originImageH, SJDim mpiW, SJDim mpiH, SJDim mpiLevel, CUDA_FLOAT focal, const CUDA_FLOAT* matW2C, const CUDA_FLOAT* matCIF, int numBlend, const CUDA_FLOAT* newC2WCUDA, const CUDA_INT* idCUDA, const CUDA_FLOAT* weightCUDA)
{
	//__shared__ float4 smDst[BLOCKDIM_X][BLOCKDIM_Y];
	//__shared__ float4 smDst2[BLOCKDIM_X][BLOCKDIM_Y];
	const int ix = blockDim.x * blockIdx.x + threadIdx.x;
	const int iy = blockDim.y * blockIdx.y + threadIdx.y;

	//Add half of a texel to always address exact texel centers
	int i, j;
	uchar3 imgVal;
	uchar3 idxVal;
	float4 origin;
	float4 dir;
	float4 t_origin;
	float4 t_dir;
	float3 trans;
	float tr;
	int newX, newY;
	int camID;
	int z;
	int index;
	int idx1, idx2, idx3;
	int factor = (int)(originImageW / mpiW);
	float zt;
	float z_plane;
	float alpha;

	float4 dst;
	float4 dstFinal;
	if (ix < imageW && iy < imageH) {
		dstFinal = { 0, 0, 0, 0 };
		for (i = 0; i < numBlend; i++) {
			camID = idCUDA[i];
			origin.x = newC2WCUDA[12];
			origin.y = newC2WCUDA[13];
			origin.z = newC2WCUDA[14];
			origin.w = newC2WCUDA[15];

			dir.x = newC2WCUDA[0] * ((ix - imageW / 2.0) / focal) - newC2WCUDA[4] * ((iy - imageH / 2.0) / focal) - newC2WCUDA[8];
			dir.y = newC2WCUDA[1] * ((ix - imageW / 2.0) / focal) - newC2WCUDA[5] * ((iy - imageH / 2.0) / focal) - newC2WCUDA[9];
			dir.z = newC2WCUDA[2] * ((ix - imageW / 2.0) / focal) - newC2WCUDA[6] * ((iy - imageH / 2.0) / focal) - newC2WCUDA[10];
			dir.w = newC2WCUDA[3] * ((ix - imageW / 2.0) / focal) - newC2WCUDA[7] * ((iy - imageH / 2.0) / focal) - newC2WCUDA[11];

			origin.w = 1.0;
			dir.w = 0.0;

			t_origin.x = matW2C[camID * 16] * origin.x + matW2C[4 + camID * 16] * origin.y + matW2C[8 + camID * 16] * origin.z + matW2C[12 + camID * 16] * origin.w;
			t_origin.y = matW2C[1 + camID * 16] * origin.x + matW2C[5 + camID * 16] * origin.y + matW2C[9 + camID * 16] * origin.z + matW2C[13 + camID * 16] * origin.w;
			t_origin.z = matW2C[2 + camID * 16] * origin.x + matW2C[6 + camID * 16] * origin.y + matW2C[10 + camID * 16] * origin.z + matW2C[14 + camID * 16] * origin.w;
			t_origin.w = matW2C[3 + camID * 16] * origin.x + matW2C[7 + camID * 16] * origin.y + matW2C[11 + camID * 16] * origin.z + matW2C[15 + camID * 16] * origin.w;

			t_dir.x = matW2C[camID * 16] * dir.x + matW2C[4 + camID * 16] * dir.y + matW2C[8 + camID * 16] * dir.z + matW2C[12 + camID * 16] * dir.w;
			t_dir.y = matW2C[1 + camID * 16] * dir.x + matW2C[5 + camID * 16] * dir.y + matW2C[9 + camID * 16] * dir.z + matW2C[13 + camID * 16] * dir.w;
			t_dir.z = matW2C[2 + camID * 16] * dir.x + matW2C[6 + camID * 16] * dir.y + matW2C[10 + camID * 16] * dir.z + matW2C[14 + camID * 16] * dir.w;
			t_dir.w = matW2C[3 + camID * 16] * dir.x + matW2C[7 + camID * 16] * dir.y + matW2C[11 + camID * 16] * dir.z + matW2C[15 + camID * 16] * dir.w;

			dst = { 0, 0, 0, 0 };

			for (z = 0; z < mpiLevel; z++) {
				zt = z / (float)(mpiLevel - 1.f);
				//	zt = (z + 4) / (float)(32 - 1.f);

				z_plane = -1. / ((1.f - zt) / matCIF[1] + zt / matCIF[0]);
				tr = (z_plane - t_origin.z) / t_dir.z;
				trans.x = t_origin.x + tr * t_dir.x;
				trans.y = t_origin.y + tr * t_dir.y;
				trans.z = t_origin.z + tr * t_dir.z;


				newX = (int)(trans.x / -trans.z * matCIF[2] + mpiW / 2.0f + 0.5f);
				newY = (int)(-(trans.y / -trans.z * matCIF[2]) + mpiH / 2.0f + 0.5f);

				if (newX >= 0 && newY >= 0 && newX < mpiW && newY < mpiH) {
					alpha = srcAlpha[(newX + newY * mpiW + z * mpiW * mpiH + camID * mpiW * mpiH * mpiLevel)] / 255.0f;// +0.00001;
					//index = newX + newY * mpiW + camID * mpiW * mpiH;
					index = newX * factor + newY * factor * originImageW + camID * originImageW * originImageH;
					imgVal = srcImg[index];
					dst.x = dst.x * (1.0 - alpha) + imgVal.x * alpha;
					dst.y = dst.y * (1.0 - alpha) + imgVal.y * alpha;
					dst.z = dst.z * (1.0 - alpha) + imgVal.z * alpha;
					dst.w = dst.w * (1.0 - alpha) + alpha;

					/*if (alpha > dst.w) {
						dst.w = alpha;
						dst.x = imgVal.x *alpha;
						dst.y = imgVal.y *alpha;
						dst.z = imgVal.z *alpha;

					}*/
				}
			}

			dstFinal.x = dstFinal.x + dst.x * weightCUDA[i];
			dstFinal.y = dstFinal.y + dst.y * weightCUDA[i];
			dstFinal.z = dstFinal.z + dst.z * weightCUDA[i];
			dstFinal.w = dstFinal.w + dst.w * weightCUDA[i];

		}

		dstFinal.x /= (dstFinal.w + 0.00001);
		dstFinal.y /= (dstFinal.w + 0.00001);
		dstFinal.z /= (dstFinal.w + 0.00001);

		dstRGB[ix + iy * imageW].x = MIN(MAX(0, dstFinal.x), 255);
		dstRGB[ix + iy * imageW].y = MIN(MAX(0, dstFinal.y), 255);
		dstRGB[ix + iy * imageW].z = MIN(MAX(0, dstFinal.z), 255);

	}
}

__global__ void RenderingOriginal(const uchar4* src, uchar3* dstRGB, SJDim imageW, SJDim imageH, SJDim mpiW, SJDim mpiH, SJDim mpiLevel, CUDA_FLOAT focal, CUDA_FLOAT* matW2C, CUDA_FLOAT* matCIF, int numBlend, CUDA_FLOAT* newC2WCUDA, CUDA_INT* idCUDA, CUDA_FLOAT* weightCUDA)
{
	//__shared__ float4 smDst[BLOCKDIM_X][BLOCKDIM_Y];
	//__shared__ float4 smDst2[BLOCKDIM_X][BLOCKDIM_Y];
	const int ix = blockDim.x * blockIdx.x + threadIdx.x;
	const int iy = blockDim.y * blockIdx.y + threadIdx.y;

	//Add half of a texel to always address exact texel centers
	int i, j;
	uchar4 val;
	float4 origin;
	float4 dir;
	float4 t_origin;
	float4 t_dir;
	float3 trans;
	float tr;
	int newX, newY;
	int camID;
	int z;
	int index;
	int idx1, idx2, idx3;
	float zt;
	float z_plane;
	float alpha;

	float4 dst;
	float4 dstFinal;
	if (ix < imageW && iy < imageH) {
		dstFinal = { 0, 0, 0, 0 };
		for (i = 0; i < numBlend; i++) {
			camID = idCUDA[i];
			origin.x = newC2WCUDA[12];
			origin.y = newC2WCUDA[13];
			origin.z = newC2WCUDA[14];
			origin.w = newC2WCUDA[15];

			dir.x = newC2WCUDA[0] * ((ix - imageW / 2.0) / focal) - newC2WCUDA[4] * ((iy - imageH / 2.0) / focal) - newC2WCUDA[8];
			dir.y = newC2WCUDA[1] * ((ix - imageW / 2.0) / focal) - newC2WCUDA[5] * ((iy - imageH / 2.0) / focal) - newC2WCUDA[9];
			dir.z = newC2WCUDA[2] * ((ix - imageW / 2.0) / focal) - newC2WCUDA[6] * ((iy - imageH / 2.0) / focal) - newC2WCUDA[10];
			dir.w = newC2WCUDA[3] * ((ix - imageW / 2.0) / focal) - newC2WCUDA[7] * ((iy - imageH / 2.0) / focal) - newC2WCUDA[11];

			origin.w = 1.0;
			dir.w = 0.0;

			t_origin.x = matW2C[camID * 16] * origin.x + matW2C[4 + camID * 16] * origin.y + matW2C[8 + camID * 16] * origin.z + matW2C[12 + camID * 16] * origin.w;
			t_origin.y = matW2C[1 + camID * 16] * origin.x + matW2C[5 + camID * 16] * origin.y + matW2C[9 + camID * 16] * origin.z + matW2C[13 + camID * 16] * origin.w;
			t_origin.z = matW2C[2 + camID * 16] * origin.x + matW2C[6 + camID * 16] * origin.y + matW2C[10 + camID * 16] * origin.z + matW2C[14 + camID * 16] * origin.w;
			t_origin.w = matW2C[3 + camID * 16] * origin.x + matW2C[7 + camID * 16] * origin.y + matW2C[11 + camID * 16] * origin.z + matW2C[15 + camID * 16] * origin.w;

			t_dir.x = matW2C[camID * 16] * dir.x + matW2C[4 + camID * 16] * dir.y + matW2C[8 + camID * 16] * dir.z + matW2C[12 + camID * 16] * dir.w;
			t_dir.y = matW2C[1 + camID * 16] * dir.x + matW2C[5 + camID * 16] * dir.y + matW2C[9 + camID * 16] * dir.z + matW2C[13 + camID * 16] * dir.w;
			t_dir.z = matW2C[2 + camID * 16] * dir.x + matW2C[6 + camID * 16] * dir.y + matW2C[10 + camID * 16] * dir.z + matW2C[14 + camID * 16] * dir.w;
			t_dir.w = matW2C[3 + camID * 16] * dir.x + matW2C[7 + camID * 16] * dir.y + matW2C[11 + camID * 16] * dir.z + matW2C[15 + camID * 16] * dir.w;

			dst = { 0, 0, 0, 0 };

			for (z = 0; z < mpiLevel; z++) {
				zt = z / (float)(mpiLevel - 1.f);
				z_plane = -1. / ((1.f - zt) / matCIF[1] + zt / matCIF[0]);
				tr = (z_plane - t_origin.z) / t_dir.z;
				trans.x = t_origin.x + tr * t_dir.x;
				trans.y = t_origin.y + tr * t_dir.y;
				trans.z = t_origin.z + tr * t_dir.z;


				newX = (int)(trans.x / -trans.z * matCIF[2] + mpiW / 2.0f + 0.5f);
				newY = (int)(-(trans.y / -trans.z * matCIF[2]) + mpiH / 2.0f + 0.5f);

				if (newX >= 0 && newY >= 0 && newX < mpiW && newY < mpiH) {
					val = src[(newX + newY * mpiW + z * mpiW * mpiH + camID * mpiW * mpiH * mpiLevel)];
					alpha = val.w / 255.0f + 0.00001;

					dst.x = dst.x * (1.0 - alpha) + val.x * alpha;
					dst.y = dst.y * (1.0 - alpha) + val.y * alpha;
					dst.z = dst.z * (1.0 - alpha) + val.z * alpha;
					dst.w = dst.w * (1.0 - alpha) + alpha;
				}

			}
			//dst.x = src[0].x;

			dstFinal.x = dstFinal.x + dst.x * weightCUDA[i];
			dstFinal.y = dstFinal.y + dst.y * weightCUDA[i];
			dstFinal.z = dstFinal.z + dst.z * weightCUDA[i];
			dstFinal.w = dstFinal.w + dst.w * weightCUDA[i];
			//dstFinal.w = 1.0;
		}

		dstFinal.x /= (dstFinal.w + 0.00001);
		dstFinal.y /= (dstFinal.w + 0.00001);
		dstFinal.z /= (dstFinal.w + 0.00001);

		dstRGB[ix + iy * imageW].z = MIN(MAX(0, dstFinal.x), 255);
		dstRGB[ix + iy * imageW].y = MIN(MAX(0, dstFinal.y), 255);
		dstRGB[ix + iy * imageW].x = MIN(MAX(0, dstFinal.z), 255);

	}
}

SJCUDARenderer::SJCUDARenderer()
{
	m_pPoseArrCUDA = NULL;
	m_pWeightsCUDA = NULL;
	m_pBlendIDCUDA = NULL;
	m_pDistance = NULL;
	m_pBlendID = NULL;
	m_pWeights = NULL;
	m_pLevelCUDA = NULL;
}
SJCUDARenderer::~SJCUDARenderer()
{
	Finalize();
}

SJDim SJCUDARenderer::iDivUp(SJDim a, SJDim b)
{
	return ((a % b) != 0) ? (a / b + 1) : (a / b);
}
int SJCUDARenderer::Initialize(SJDim* pDim, SJDim* pMPIDim, CPU_FLOAT* pC2WCPU, CUDA_FLOAT* pC2WCUDA, CPU_FLOAT* pW2CCPU, CUDA_FLOAT* pW2CCUDA, CPU_FLOAT* pCIFCPU, CUDA_FLOAT* pCIFCUDA)
{
	m_pDim = pDim;
	m_pMPIDim = pMPIDim;
	m_pC2W = pC2WCPU;
	m_pC2WCUDA = pC2WCUDA;

	m_pW2C = pW2CCPU;
	m_pW2CCUDA = pW2CCUDA;

	m_pCIF = pCIFCPU;
	m_pCIFCUDA = pCIFCUDA;

	return 0;
}
int SJCUDARenderer::LoadMPI(CPU_UCHAR* pMPICPU, CUDA_UCHAR* pMPICUDA)
{
	m_pMPI = pMPICPU;
	m_pMPICUDA = pMPICUDA;
	bCompressed = false;
	return 0;
}

int SJCUDARenderer::LoadCompressedMPI(CPU_UCHAR* pCompressedMPICPU, CUDA_UCHAR* pCompressedMPICUDA, CPU_UCHAR* pCompressedIdxCPU, CUDA_UCHAR* pCompressedIdxCUDA)
{
	m_pMPI = pCompressedMPICPU;
	m_pMPICUDA = pCompressedMPICUDA;
	m_pMPIIdx = pCompressedIdxCPU;
	m_pMPIIdxCUDA = pCompressedIdxCUDA;
	bCompressed = true;
	return 0;
}
int SJCUDARenderer::InitializeRendering(SJDim outWidth, SJDim outHeight, int numBlend)
{
	LOGGING(LOG_LEVEL::VERBOSE, "Start\n");
	m_iWidth = outWidth;
	m_iHeight = outHeight;
	float factor = (float)outHeight / (float)m_pMPIDim[2];
	m_fFocal = factor * m_pCIF[2];
	m_numBlend = numBlend;

	m_pDistance = new CPU_FLOAT[m_pMPIDim[0] * m_pMPIDim[1]];
	m_pBlendID = new CPU_INT[m_pMPIDim[0] * m_pMPIDim[1]];
	m_pWeights = new CPU_FLOAT[m_pMPIDim[0] * m_pMPIDim[1]];

	int deviceID;
	size_t mem_free;
	size_t mem_total;
	checkCudaErrors(cudaMalloc((void**)&m_pPoseArrCUDA, 16 * sizeof(CUDA_FLOAT)));
	checkCudaErrors(cudaMalloc((void**)&m_pBlendIDCUDA, m_pMPIDim[0] * m_pMPIDim[1] * sizeof(CUDA_INT)));
	checkCudaErrors(cudaMalloc((void**)&m_pWeightsCUDA, m_pMPIDim[0] * m_pMPIDim[1] * sizeof(CUDA_FLOAT)));
	LOGGING(LOG_LEVEL::VERBOSE, "End\n");
	return 0;
}

int SJCUDARenderer::Rendering(float* pose_arr, CUDA_UCHAR* pOutImageCUDA, CPU_UCHAR* pOutImage)
{
	LOGGING(LOG_LEVEL::VERBOSE, "Start\n");
	int idx;
	for (SJDim j = 0; j < m_pMPIDim[0] * m_pMPIDim[1]; j++) {
		m_pBlendID[j] = j;
		m_pDistance[j] = sqrt((pose_arr[12] - m_pC2W[12 + j * 16]) * (pose_arr[12] - m_pC2W[12 + j * 16]) + (pose_arr[13] - m_pC2W[13 + j * 16]) * (pose_arr[13] - m_pC2W[13 + j * 16]) + (pose_arr[14] - m_pC2W[14 + j * 16]) * (pose_arr[14] - m_pC2W[14 + j * 16]));
	}
	for (SJDim j = 0; j < m_pMPIDim[0] * m_pMPIDim[1] - 1; j++) {
		for (SJDim k = j; k < m_pMPIDim[0] * m_pMPIDim[1]; k++) {
			if (m_pDistance[m_pBlendID[j]] > m_pDistance[m_pBlendID[k]]) {
				idx = m_pBlendID[j];
				m_pBlendID[j] = m_pBlendID[k];
				m_pBlendID[k] = idx;
			}
		}
	}
	for (int i = 0; i < m_pMPIDim[0] * m_pMPIDim[1]; i++) {
		//	printf("%d ", m_pBlendID[i]);
		m_pWeights[i] = exp(-m_pDistance[m_pBlendID[i]]);
	}
	//printf("\n");

	checkCudaErrors(cudaMemcpy(m_pPoseArrCUDA, pose_arr, 16 * sizeof(CUDA_FLOAT), cudaMemcpyHostToDevice));
	checkCudaErrors(cudaMemcpy(m_pBlendIDCUDA, m_pBlendID, m_pMPIDim[0] * m_pMPIDim[1] * sizeof(CUDA_INT), cudaMemcpyHostToDevice));
	checkCudaErrors(cudaMemcpy(m_pWeightsCUDA, m_pWeights, m_pMPIDim[0] * m_pMPIDim[1] * sizeof(CUDA_FLOAT), cudaMemcpyHostToDevice));

	dim3 threads(BLOCKDIM_X, BLOCKDIM_Y);
	dim3 grid(iDivUp(m_iWidth, BLOCKDIM_X), iDivUp(m_iHeight, BLOCKDIM_Y));

	//makeCompressedRenderingGlobalNew << < grid, threads >> > ((uchar3*)m_pMPICUDA, m_pMPIIdxCUDA, (uchar3*)pOutImageCUDA, m_iWidth, m_iHeight, m_pMPIDim[3], m_pMPIDim[2], m_pMPIDim[4], m_fFocal, m_pW2CCUDA, m_pCIFCUDA, m_numBlend, m_pPoseArrCUDA, m_pBlendIDCUDA, m_pWeightsCUDA);
	if (bCompressed) {
		RenderingCompressed << < grid, threads >> > ((uchar3*)m_pMPICUDA, m_pMPIIdxCUDA, (uchar3*)pOutImageCUDA, m_iWidth, m_iHeight, m_pDim[3], m_pDim[2], m_pMPIDim[3], m_pMPIDim[2], m_pMPIDim[4], m_fFocal, m_pW2CCUDA, m_pCIFCUDA, m_numBlend, m_pPoseArrCUDA, m_pBlendIDCUDA, m_pWeightsCUDA);
	}
	else {
		RenderingOriginal << < grid, threads >> > ((uchar4*)m_pMPICUDA, (uchar3*)pOutImageCUDA, m_iWidth, m_iHeight, m_pMPIDim[3], m_pMPIDim[2], m_pMPIDim[4], m_fFocal, m_pW2CCUDA, m_pCIFCUDA, m_numBlend, m_pPoseArrCUDA, m_pBlendIDCUDA, m_pWeightsCUDA);
	}
	if (pOutImage) {
		cudaMemcpy(pOutImage, pOutImageCUDA, sizeof(unsigned char) * m_iWidth * m_iHeight * 3, cudaMemcpyDeviceToHost);
	}
	LOGGING(LOG_LEVEL::VERBOSE, "End\n");
	return 0;
}
int SJCUDARenderer::Finalize()
{
	LOGGING(LOG_LEVEL::VERBOSE, "Start\n");
	if (m_pPoseArrCUDA) {
		checkCudaErrors(cudaFree(m_pPoseArrCUDA));
		m_pPoseArrCUDA = NULL;
	}
	if (m_pBlendIDCUDA) {
		checkCudaErrors(cudaFree(m_pBlendIDCUDA));
		m_pBlendIDCUDA = NULL;
	}
	if (m_pWeightsCUDA) {
		checkCudaErrors(cudaFree(m_pWeightsCUDA));
		m_pWeightsCUDA = NULL;
	}
	if (m_pLevelCUDA) {
		checkCudaErrors(cudaFree(m_pLevelCUDA));
		m_pLevelCUDA = NULL;

	}
	LOGGING(LOG_LEVEL::VERBOSE, "End\n");
	return 0;
}