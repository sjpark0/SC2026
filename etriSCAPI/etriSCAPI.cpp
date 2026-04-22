#include "etriSCAPI.h"
#include "SJCUDARenderer.h"
#include <stdio.h>
#include "cuda_runtime.h"
SJCUDARenderer* SJCUDARenderer_New()
{
	return new SJCUDARenderer();
}
int SJCUDARenderer_Initialize(SJCUDARenderer* renderer, size_t* pDim, size_t* pMPIDim, float* pC2WCPU, float* pC2WCUDA, float* pW2CCPU, float* pW2CCUDA, float* pCIFCPU, float* pCIFCUDA)
{
	return renderer->Initialize(pDim, pMPIDim, pC2WCPU, pC2WCUDA, pW2CCPU, pW2CCUDA, pCIFCPU, pCIFCUDA);
}
int SJCUDARenderer_LoadMPI(SJCUDARenderer* renderer, unsigned char* pMPICPU, unsigned char* pMPICUDA)
{
	return renderer->LoadMPI(pMPICPU, pMPICUDA);
}
int SJCUDARenderer_LoadCompressedMPI(SJCUDARenderer* renderer, unsigned char* pCompressedMPICPU, unsigned char* pCompressedMPICUDA, unsigned char* pCompressedIdxCPU, unsigned char* pCompressedIdxCUDA)
{
	return renderer->LoadCompressedMPI(pCompressedMPICPU, pCompressedMPICUDA, pCompressedIdxCPU, pCompressedIdxCUDA);
}
int SJCUDARenderer_InitializeRendering(SJCUDARenderer* renderer, size_t outWidth, size_t outHeight, int numBlend)
{
	return renderer->InitializeRendering(outWidth, outHeight, numBlend);
}
int SJCUDARenderer_Rendering(SJCUDARenderer* renderer, float* pose_arr, unsigned char* pOutImageCUDA, unsigned char* pOutImageCPU)
{
	return renderer->Rendering(pose_arr, pOutImageCUDA, pOutImageCPU);
}
int SJCUDARenderer_Finalize(SJCUDARenderer* renderer)
{
	renderer->Finalize();
	delete renderer;
	return 0;
}
int SJCUDARenderer_LoadMPIFromFolder(char* foldername, size_t* pMPIDim, unsigned char* pMPICUDA)
{
    char command[1024];
    FILE* fp;
    unsigned char* temp = new unsigned char[pMPIDim[2] * pMPIDim[3] * pMPIDim[4] * 4];

    for (SJDim i = 0; i < pMPIDim[0] * pMPIDim[1]; i++) {
        sprintf(command, "%s/mpi%02d/mpi.b", foldername, i);
        fp = fopen(command, "rb");
        fread(temp, 1, pMPIDim[2] * pMPIDim[3] * pMPIDim[4] * 4 * sizeof(unsigned char), fp);
        fclose(fp);

        cudaMemcpy(&pMPICUDA[i * pMPIDim[2] * pMPIDim[3] * pMPIDim[4] * 4], temp, pMPIDim[2] * pMPIDim[3] * pMPIDim[4] * 4 * sizeof(unsigned char), cudaMemcpyHostToDevice);
    }
    delete[]temp;
    return 0;
}
int SJCUDARenderer_LoadDataFromFolder(char* foldername, size_t* pMPIDim, float* pC2W, float* pC2WCUDA, float* pW2C, float* pW2CCUDA, float* pCIF, float* pCIFCUDA)
{
    char filename[1024];
    FILE* fp;
    int width, height, level;
    float focal;
    for (size_t i = 0; i < pMPIDim[0] * pMPIDim[1]; i++) {
        sprintf(filename, "%s/mpi%02d/metadata.txt", foldername, i);
        fp = fopen(filename, "r");
        fscanf(fp, "%d %d %d %f\n", &width, &height, &level, &pCIF[2 + i * 3]);
        for (int j = 0; j < 16; j++) {
            if (j % 4 != 3)
                fscanf(fp, "%f ", &pC2W[j + i * 16]);
            else
                pC2W[j + i * 16] = j < 15 ? 0. : 1.;
        }
        fscanf(fp, "%f %f", &pCIF[1 + i * 3], &pCIF[i * 3]);
        //pCIF[2 + i * 3] = pCIF[2 + i * 3] * 4;
        fclose(fp);

    }
    CPU_FLOAT* matC2W = pC2W;
    CPU_FLOAT* matW2C = pW2C;
    for (int c = 0; c < pMPIDim[0] * pMPIDim[1]; c++) {
        matW2C[c * 16] = matC2W[c * 16];
        matW2C[1 + c * 16] = matC2W[4 + c * 16];
        matW2C[2 + c * 16] = matC2W[8 + c * 16];
        matW2C[3 + c * 16] = -0.0f;
        matW2C[4 + c * 16] = matC2W[1 + c * 16];
        matW2C[5 + c * 16] = matC2W[5 + c * 16];
        matW2C[6 + c * 16] = matC2W[9 + c * 16];
        matW2C[7 + c * 16] = 0.0f;
        matW2C[8 + c * 16] = matC2W[2 + c * 16];
        matW2C[9 + c * 16] = matC2W[6 + c * 16];
        matW2C[10 + c * 16] = matC2W[10 + c * 16];
        matW2C[11 + c * 16] = -0.0f;
        matW2C[15 + c * 16] = 1.0f;
        matW2C[12 + c * 16] = -(matC2W[12 + c * 16] * matC2W[c * 16] + matC2W[13 + c * 16] * matC2W[1 + c * 16] + matC2W[14 + c * 16] * matC2W[2 + c * 16]);
        matW2C[13 + c * 16] = -(matC2W[12 + c * 16] * matC2W[4 + c * 16] + matC2W[13 + c * 16] * matC2W[5 + c * 16] + matC2W[14 + c * 16] * matC2W[6 + c * 16]);
        matW2C[14 + c * 16] = -(matC2W[12 + c * 16] * matC2W[8 + c * 16] + matC2W[13 + c * 16] * matC2W[9 + c * 16] + matC2W[14 + c * 16] * matC2W[10 + c * 16]);

    }
    cudaMemcpy(pC2WCUDA, pC2W, pMPIDim[0] * pMPIDim[1] * 16 * sizeof(CUDA_FLOAT), cudaMemcpyHostToDevice);
    cudaMemcpy(pW2CCUDA, pW2C, pMPIDim[0] * pMPIDim[1] * 16 * sizeof(CUDA_FLOAT), cudaMemcpyHostToDevice);
    cudaMemcpy(pCIFCUDA, pCIF, pMPIDim[0] * pMPIDim[1] * 3 * sizeof(CUDA_FLOAT), cudaMemcpyHostToDevice);

    return 0;
}

unsigned char* SJCUDARenderer_CUDA_UCHAR_Alloc(size_t size)
{
    unsigned char* buffer;
    cudaMalloc((void**)&buffer, size * sizeof(unsigned char));
    return buffer;
}
unsigned char* SJCUDARenderer_CPU_UCHAR_Alloc(size_t size)
{
    return new unsigned char[size];
}
float* SJCUDARenderer_CUDA_FLOAT_Alloc(size_t size)
{
    float* buffer;
    cudaMalloc((void**)&buffer, size * sizeof(float));
    return buffer;
}
float* SJCUDARenderer_CPU_FLOAT_Alloc(size_t size)
{
    return new float[size];
}

void SJCUDARenderer_CUDA_UCHAR_Free(unsigned char* buffer)
{
    cudaFree(buffer);
}
void SJCUDARenderer_CPU_UCHAR_Free(unsigned char* buffer)
{
    delete[]buffer;
}
void SJCUDARenderer_CUDA_FLOAT_Free(float* buffer)
{
    cudaFree(buffer);
}
void SJCUDARenderer_CPU_FLOAT_Free(float* buffer)
{
    delete[]buffer;
}
float* SJCUDARenderer_GetRenderPath(char* filename)
{
    FILE* fp;
    int numView;
    float* pViewArr;

    
    fp = fopen(filename, "r");
    fscanf(fp, "%d", &numView);
    pViewArr = new float[16 * numView];
    float temp;

    for (int i = 0; i < numView; i++) {
        for (int j = 0; j < 3; j++) {
            for (int k = 0; k < 3; k++) {
                fscanf(fp, "%f ", &pViewArr[k + j * 4 + i * 16]);
            }
        }
        pViewArr[3 + i * 16] = pViewArr[7 + i * 16] = pViewArr[11 + i * 16] = 0;
        fscanf(fp, "%f ", &pViewArr[12 + i * 16]);
        fscanf(fp, "%f ", &pViewArr[13 + i * 16]);
        fscanf(fp, "%f ", &pViewArr[14 + i * 16]);
        pViewArr[15 + i * 16] = 1.0;

        fscanf(fp, "%f ", &temp);
        fscanf(fp, "%f ", &temp);
        fscanf(fp, "%f ", &temp);


    }
    fclose(fp);

    return pViewArr;
}
