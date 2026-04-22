// SC2025.cpp : 이 파일에는 'main' 함수가 포함됩니다. 거기서 프로그램 실행이 시작되고 종료됩니다.
//

#include <iostream>
#include "SJCUDACommon.h"
#include "SJPlenopticPacker.h"
#include "SJCUDARenderer.h"
#include "etriSCAPI.h"

#include "cuda_runtime.h"
#include "opencv2/opencv.hpp"
#include "SJLog.h"
using namespace cv;

int LoadMetaDataFromFolder(char* folderName, CPU_FLOAT* pC2W, CPU_FLOAT* pCIF, SJDim* pMPIDim)
{
    char filename[1024];
    FILE* fp;
    int width, height, level;
    float focal;
    for (size_t i = 0; i < pMPIDim[0] * pMPIDim[1]; i++) {
        sprintf(filename, "%s/mpi%02d/metadata.txt", folderName, i);
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
    return 0;
}
void LoadMPIFromFolder(const char* folderName, unsigned char* pMPI, SJDim* pMPIDim)
{
    char command[1024];
    FILE* fp;
    unsigned char* temp = new unsigned char[pMPIDim[2] * pMPIDim[3] * pMPIDim[4] * 4];

    for (SJDim i = 0; i < pMPIDim[0] * pMPIDim[1]; i++) {
        sprintf(command, "%s/mpi%02d/mpi.b", folderName, i);
        fp = fopen(command, "rb");
        fread(temp, 1, pMPIDim[2] * pMPIDim[3] * pMPIDim[4] * 4 * sizeof(unsigned char), fp);
        fclose(fp);

        cudaMemcpy(&pMPI[i * pMPIDim[2] * pMPIDim[3] * pMPIDim[4] * 4], temp, pMPIDim[2] * pMPIDim[3] * pMPIDim[4] * 4 * sizeof(unsigned char), cudaMemcpyHostToDevice);
    }
    delete[]temp;
}
void RenderingCompressedTest()
{
    char inputFolder[] = "../Data/Sample";
    char outputFolder[] = "../Data/RenderingResult";
    SJDim pMPIDim[] = { 1, 16, 540, 960, 32 };
    SJDim pDim[] = { 1, 16, 540, 960 };
    int outWidth = pDim[3];
    int outHeight = pDim[2];
    int packingWidth = 7680;
    int packingHeight = 4320;
    int numImage = 1;
    int numLayer = 3;

    FILE* fp;
    char filename[1024];
    sprintf(filename, "mkdir %s", outputFolder);
    system(filename);

    int numView;
    float* pViewArr;

    sprintf(filename, "%s/test_path_10.txt", inputFolder);
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

    sprintf(filename, "%s/mpis_360", inputFolder);

    CPU_FLOAT* pC2WCPU = new CPU_FLOAT[pDim[0] * pDim[1] * 16];
    CPU_FLOAT* pW2CCPU = new CPU_FLOAT[pDim[0] * pDim[1] * 16];
    CPU_FLOAT* pCIFCPU = new CPU_FLOAT[pDim[0] * pDim[1] * 3];
    CUDA_FLOAT* pC2WCUDA;
    CUDA_FLOAT* pW2CCUDA;
    CUDA_FLOAT* pCIFCUDA;

    cudaMalloc((void**)&pC2WCUDA, pDim[0] * pDim[1] * 16 * sizeof(CUDA_FLOAT));
    cudaMalloc((void**)&pW2CCUDA, pDim[0] * pDim[1] * 16 * sizeof(CUDA_FLOAT));
    cudaMalloc((void**)&pCIFCUDA, pDim[0] * pDim[1] * 3 * sizeof(CUDA_FLOAT));

    LoadMetaDataFromFolder(filename, pC2WCPU, pCIFCPU, pMPIDim);

    CPU_FLOAT* matC2W = pC2WCPU;
    CPU_FLOAT* matW2C = pW2CCPU;
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

    cudaMemcpy(pC2WCUDA, pC2WCPU, pMPIDim[0] * pMPIDim[1] * 16 * sizeof(CUDA_FLOAT), cudaMemcpyHostToDevice);
    cudaMemcpy(pW2CCUDA, pW2CCPU, pMPIDim[0] * pMPIDim[1] * 16 * sizeof(CUDA_FLOAT), cudaMemcpyHostToDevice);
    cudaMemcpy(pCIFCUDA, pCIFCPU, pMPIDim[0] * pMPIDim[1] * 3 * sizeof(CUDA_FLOAT), cudaMemcpyHostToDevice);


    CUDA_UCHAR* pRGBDataCUDA;
    CUDA_UCHAR* pLayerDataCUDA;
    CUDA_UCHAR* pImageCUDA;
    CPU_UCHAR* pImage;
    cudaMalloc((void**)&pRGBDataCUDA, pDim[0] * pDim[1] * pDim[2] * pDim[3] * 3 * sizeof(unsigned char));
    cudaMalloc((void**)&pLayerDataCUDA, pMPIDim[0] * pMPIDim[1] * pMPIDim[2] * pMPIDim[3] * pMPIDim[4] * sizeof(unsigned char));
    cudaMalloc((void**)&pImageCUDA, outWidth * outHeight * 3 * sizeof(unsigned char));
    pImage = new CPU_UCHAR[outWidth * outHeight * 3];

    CUDA_UCHAR** packingImage;
    CUDA_UCHAR** packingLayer;
    packingImage = new CUDA_UCHAR * [numImage];
    packingLayer = new CUDA_UCHAR * [numLayer];
    Mat packing;
    for (int i = 0; i < numImage; i++) {
        sprintf(filename, "%s/Image_%d.png", inputFolder, i);
        cudaMalloc((void**)&packingImage[i], packingWidth * packingHeight * 3 * sizeof(unsigned char));
        packing = imread(filename);
        cudaMemcpy(packingImage[i], packing.data, packingWidth * packingHeight * 3 * sizeof(unsigned char), cudaMemcpyHostToDevice);
    }
    for (int i = 0; i < numLayer; i++) {
        sprintf(filename, "%s/Layer_%d.png", inputFolder, i);
        cudaMalloc((void**)&packingLayer[i], packingWidth * packingHeight * 3 * sizeof(unsigned char));
        packing = imread(filename);
        cudaMemcpy(packingLayer[i], packing.data, packingWidth * packingHeight * 3 * sizeof(unsigned char), cudaMemcpyHostToDevice);
    }

    SJPlenopticPacker packer;
    packer.Initialize(pDim, pMPIDim, packingWidth, packingHeight, numImage, numLayer);
    packer.UnPackingImage(packingImage, pRGBDataCUDA);
    packer.UnPackingLayer(packingLayer, pLayerDataCUDA);
    SJCUDARenderer renderer;
    renderer.Initialize(pDim, pMPIDim, pC2WCPU, pC2WCUDA, pW2CCPU, pW2CCUDA, pCIFCPU, pCIFCUDA);
    renderer.InitializeRendering(pDim[3], pDim[2], 5);
    renderer.LoadCompressedMPI(NULL, pRGBDataCUDA, NULL, pLayerDataCUDA);

    Mat img(outHeight, outWidth, CV_8UC3, pImage);
    for (int i = 0; i < numView; i++) {
        renderer.Rendering(&pViewArr[i * 16], pImageCUDA, pImage);
        sprintf(filename, "%s/%03d.png", outputFolder, i);
        imwrite(filename, img);
    }
    renderer.Finalize();

    delete[]pC2WCPU;
    delete[]pW2CCPU;
    delete[]pCIFCPU;
    delete[]pViewArr;

    delete[]pImage;
    cudaFree(pC2WCUDA);
    cudaFree(pW2CCUDA);
    cudaFree(pCIFCUDA);
    cudaFree(pRGBDataCUDA);
    cudaFree(pLayerDataCUDA);
    cudaFree(pImageCUDA);
    for (int i = 0; i < numImage; i++) {
        cudaFree(packingImage[i]);
    }
    delete[]packingImage;
    for (int i = 0; i < numLayer; i++) {
        cudaFree(packingLayer[i]);
    }
    delete[]packingLayer;

}
void RenderingOriginalTest()
{
    char inputFolder[] = "../Data/Sample";
    char outputFolder[] = "../Data/RenderingResult1";
    SJDim pMPIDim[] = { 1, 16, 540, 960, 32 };
    SJDim pDim[] = { 1, 16, 540, 960 };
    int outWidth = pDim[3];
    int outHeight = pDim[2];

    FILE* fp;
    char filename[1024];
    sprintf(filename, "mkdir %s", outputFolder);
    system(filename);

    int numView;
    float* pViewArr;

    sprintf(filename, "%s/test_path_10.txt", inputFolder);
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

    sprintf(filename, "%s/mpis_360", inputFolder);

    CPU_FLOAT* pC2WCPU = new CPU_FLOAT[pDim[0] * pDim[1] * 16];
    CPU_FLOAT* pW2CCPU = new CPU_FLOAT[pDim[0] * pDim[1] * 16];
    CPU_FLOAT* pCIFCPU = new CPU_FLOAT[pDim[0] * pDim[1] * 3];
    CUDA_FLOAT* pC2WCUDA;
    CUDA_FLOAT* pW2CCUDA;
    CUDA_FLOAT* pCIFCUDA;

    cudaMalloc((void**)&pC2WCUDA, pDim[0] * pDim[1] * 16 * sizeof(CUDA_FLOAT));
    cudaMalloc((void**)&pW2CCUDA, pDim[0] * pDim[1] * 16 * sizeof(CUDA_FLOAT));
    cudaMalloc((void**)&pCIFCUDA, pDim[0] * pDim[1] * 3 * sizeof(CUDA_FLOAT));

    LoadMetaDataFromFolder(filename, pC2WCPU, pCIFCPU, pMPIDim);

    CPU_FLOAT* matC2W = pC2WCPU;
    CPU_FLOAT* matW2C = pW2CCPU;
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

    cudaMemcpy(pC2WCUDA, pC2WCPU, pMPIDim[0] * pMPIDim[1] * 16 * sizeof(CUDA_FLOAT), cudaMemcpyHostToDevice);
    cudaMemcpy(pW2CCUDA, pW2CCPU, pMPIDim[0] * pMPIDim[1] * 16 * sizeof(CUDA_FLOAT), cudaMemcpyHostToDevice);
    cudaMemcpy(pCIFCUDA, pCIFCPU, pMPIDim[0] * pMPIDim[1] * 3 * sizeof(CUDA_FLOAT), cudaMemcpyHostToDevice);

    CUDA_UCHAR* pMPICUDA;
    cudaMalloc((void**)&pMPICUDA, pMPIDim[0] * pMPIDim[1] * pMPIDim[2] * pMPIDim[3] * pMPIDim[4] * 4 * sizeof(CUDA_UCHAR));
    LoadMPIFromFolder(filename, pMPICUDA, pMPIDim);
    CUDA_UCHAR* pImageCUDA;
    CPU_UCHAR* pImage;

    cudaMalloc((void**)&pImageCUDA, outWidth * outHeight * 3 * sizeof(unsigned char));
    pImage = new CPU_UCHAR[outWidth * outHeight * 3];


    SJCUDARenderer renderer;
    renderer.Initialize(pDim, pMPIDim, pC2WCPU, pC2WCUDA, pW2CCPU, pW2CCUDA, pCIFCPU, pCIFCUDA);
    renderer.InitializeRendering(pDim[3], pDim[2], 5);
    renderer.LoadMPI(NULL, pMPICUDA);

    Mat img(outHeight, outWidth, CV_8UC3, pImage);
    for (int i = 0; i < numView; i++) {
        renderer.Rendering(&pViewArr[i * 16], pImageCUDA, pImage);
        sprintf(filename, "%s/%03d.png", outputFolder, i);
        imwrite(filename, img);
    }
    renderer.Finalize();

    delete[]pC2WCPU;
    delete[]pW2CCPU;
    delete[]pCIFCPU;
    delete[]pViewArr;

    delete[]pImage;
    cudaFree(pC2WCUDA);
    cudaFree(pW2CCUDA);
    cudaFree(pCIFCUDA);
    cudaFree(pMPICUDA);
    cudaFree(pImageCUDA);

}

void RenderingOriginalTest_API()
{
    char inputFolder[] = "../Data/Sample";
    char outputFolder[] = "../Data/RenderingResult2";
    SJDim pMPIDim[] = { 1, 16, 540, 960, 32 };
    SJDim pDim[] = { 1, 16, 540, 960 };
    int outWidth = pDim[3];
    int outHeight = pDim[2];

    FILE* fp;
    char filename[1024];
    sprintf(filename, "mkdir %s", outputFolder);
    system(filename);

    int numView;
    float* pViewArr;

    sprintf(filename, "%s/test_path_10.txt", inputFolder);
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

    sprintf(filename, "%s/mpis_360", inputFolder);

    CPU_FLOAT* pC2WCPU = new CPU_FLOAT[pDim[0] * pDim[1] * 16];
    CPU_FLOAT* pW2CCPU = new CPU_FLOAT[pDim[0] * pDim[1] * 16];
    CPU_FLOAT* pCIFCPU = new CPU_FLOAT[pDim[0] * pDim[1] * 3];
    CUDA_FLOAT* pC2WCUDA;
    CUDA_FLOAT* pW2CCUDA;
    CUDA_FLOAT* pCIFCUDA;

    cudaMalloc((void**)&pC2WCUDA, pDim[0] * pDim[1] * 16 * sizeof(CUDA_FLOAT));
    cudaMalloc((void**)&pW2CCUDA, pDim[0] * pDim[1] * 16 * sizeof(CUDA_FLOAT));
    cudaMalloc((void**)&pCIFCUDA, pDim[0] * pDim[1] * 3 * sizeof(CUDA_FLOAT));

    LoadMetaDataFromFolder(filename, pC2WCPU, pCIFCPU, pMPIDim);

    CPU_FLOAT* matC2W = pC2WCPU;
    CPU_FLOAT* matW2C = pW2CCPU;
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

    cudaMemcpy(pC2WCUDA, pC2WCPU, pMPIDim[0] * pMPIDim[1] * 16 * sizeof(CUDA_FLOAT), cudaMemcpyHostToDevice);
    cudaMemcpy(pW2CCUDA, pW2CCPU, pMPIDim[0] * pMPIDim[1] * 16 * sizeof(CUDA_FLOAT), cudaMemcpyHostToDevice);
    cudaMemcpy(pCIFCUDA, pCIFCPU, pMPIDim[0] * pMPIDim[1] * 3 * sizeof(CUDA_FLOAT), cudaMemcpyHostToDevice);

    CUDA_UCHAR* pMPICUDA;
    cudaMalloc((void**)&pMPICUDA, pMPIDim[0] * pMPIDim[1] * pMPIDim[2] * pMPIDim[3] * pMPIDim[4] * 4 * sizeof(CUDA_UCHAR));
    LoadMPIFromFolder(filename, pMPICUDA, pMPIDim);
    CUDA_UCHAR* pImageCUDA;
    CPU_UCHAR* pImage;

    cudaMalloc((void**)&pImageCUDA, outWidth * outHeight * 3 * sizeof(unsigned char));
    pImage = new CPU_UCHAR[outWidth * outHeight * 3];


    SJCUDARenderer* renderer = SJCUDARenderer_New();
    SJCUDARenderer_Initialize(renderer, pDim, pMPIDim, pC2WCPU, pC2WCUDA, pW2CCPU, pW2CCUDA, pCIFCPU, pCIFCUDA);
    SJCUDARenderer_InitializeRendering(renderer, pDim[3], pDim[2], 5);
    SJCUDARenderer_LoadMPI(renderer, NULL, pMPICUDA);

    Mat img(outHeight, outWidth, CV_8UC3, pImage);
    for (int i = 0; i < numView; i++) {
        SJCUDARenderer_Rendering(renderer, &pViewArr[i * 16], pImageCUDA, pImage);
        sprintf(filename, "%s/%03d.png", outputFolder, i);
        imwrite(filename, img);
    }
    SJCUDARenderer_Finalize(renderer);

    delete[]pC2WCPU;
    delete[]pW2CCPU;
    delete[]pCIFCPU;
    delete[]pViewArr;

    delete[]pImage;
    cudaFree(pC2WCUDA);
    cudaFree(pW2CCUDA);
    cudaFree(pCIFCUDA);
    cudaFree(pMPICUDA);
    cudaFree(pImageCUDA);

}


void RenderingOriginalTest_API2()
{
    char inputFolder[] = "../Data/Sample";
    char outputFolder[] = "../Data/RenderingResult2";
    SJDim pMPIDim[] = { 1, 16, 540, 960, 32 };
    SJDim pDim[] = { 1, 16, 540, 960 };
    int outWidth = pDim[3];
    int outHeight = pDim[2];


    char filename[1024];
    sprintf(filename, "mkdir %s", outputFolder);
    system(filename);

    sprintf(filename, "%s/test_path_10.txt", inputFolder);

    float* pViewArr = SJCUDARenderer_GetRenderPath(filename);
    int numView = 45;
    for (int i = 0; i < numView; i++) {
        for (int j = 0; j < 16; j++) {
            printf("%f ", pViewArr[j + i * 16]);
        }
        printf("\n");
    }
    sprintf(filename, "%s/mpis_360", inputFolder);

    CPU_FLOAT* pC2WCPU = new CPU_FLOAT[pDim[0] * pDim[1] * 16];
    CPU_FLOAT* pW2CCPU = new CPU_FLOAT[pDim[0] * pDim[1] * 16];
    CPU_FLOAT* pCIFCPU = new CPU_FLOAT[pDim[0] * pDim[1] * 3];
    CUDA_FLOAT* pC2WCUDA;
    CUDA_FLOAT* pW2CCUDA;
    CUDA_FLOAT* pCIFCUDA;

    cudaMalloc((void**)&pC2WCUDA, pDim[0] * pDim[1] * 16 * sizeof(CUDA_FLOAT));
    cudaMalloc((void**)&pW2CCUDA, pDim[0] * pDim[1] * 16 * sizeof(CUDA_FLOAT));
    cudaMalloc((void**)&pCIFCUDA, pDim[0] * pDim[1] * 3 * sizeof(CUDA_FLOAT));

    //LoadMetaDataFromFolder(filename, pC2WCPU, pCIFCPU, pMPIDim);
    SJCUDARenderer_LoadDataFromFolder(filename, pMPIDim, pC2WCPU, pC2WCUDA, pW2CCPU, pW2CCUDA, pCIFCPU, pCIFCUDA);


    CUDA_UCHAR* pMPICUDA;
    cudaMalloc((void**)&pMPICUDA, pMPIDim[0] * pMPIDim[1] * pMPIDim[2] * pMPIDim[3] * pMPIDim[4] * 4 * sizeof(CUDA_UCHAR));
    SJCUDARenderer_LoadMPIFromFolder(filename, pMPIDim, pMPICUDA);
    CUDA_UCHAR* pImageCUDA;
    CPU_UCHAR* pImage;

    cudaMalloc((void**)&pImageCUDA, outWidth * outHeight * 3 * sizeof(unsigned char));
    pImage = new CPU_UCHAR[outWidth * outHeight * 3];


    SJCUDARenderer* renderer = SJCUDARenderer_New();
    SJCUDARenderer_Initialize(renderer, pDim, pMPIDim, pC2WCPU, pC2WCUDA, pW2CCPU, pW2CCUDA, pCIFCPU, pCIFCUDA);
    SJCUDARenderer_InitializeRendering(renderer, pDim[3], pDim[2], 5);
    SJCUDARenderer_LoadMPI(renderer, NULL, pMPICUDA);

    Mat img(outHeight, outWidth, CV_8UC3, pImage);
    for (int i = 0; i < numView; i++) {
        SJCUDARenderer_Rendering(renderer, &pViewArr[i * 16], pImageCUDA, pImage);
        sprintf(filename, "%s/%03d.png", outputFolder, i);
        imwrite(filename, img);
    }
    SJCUDARenderer_Finalize(renderer);

    delete[]pC2WCPU;
    delete[]pW2CCPU;
    delete[]pCIFCPU;
    delete[]pViewArr;

    delete[]pImage;
    cudaFree(pC2WCUDA);
    cudaFree(pW2CCUDA);
    cudaFree(pCIFCUDA);
    cudaFree(pMPICUDA);
    cudaFree(pImageCUDA);

}

int main()
{
    SJLog::SetLOGLevel(LOG_LEVEL::VERBOSE);
    //RenderingCompressedTest();
    //RenderingOriginalTest();
    //RenderingOriginalTest_API();
    RenderingOriginalTest_API2();

}

// 프로그램 실행: <Ctrl+F5> 또는 [디버그] > [디버깅하지 않고 시작] 메뉴
// 프로그램 디버그: <F5> 키 또는 [디버그] > [디버깅 시작] 메뉴

// 시작을 위한 팁: 
//   1. [솔루션 탐색기] 창을 사용하여 파일을 추가/관리합니다.
//   2. [팀 탐색기] 창을 사용하여 소스 제어에 연결합니다.
//   3. [출력] 창을 사용하여 빌드 출력 및 기타 메시지를 확인합니다.
//   4. [오류 목록] 창을 사용하여 오류를 봅니다.
//   5. [프로젝트] > [새 항목 추가]로 이동하여 새 코드 파일을 만들거나, [프로젝트] > [기존 항목 추가]로 이동하여 기존 코드 파일을 프로젝트에 추가합니다.
//   6. 나중에 이 프로젝트를 다시 열려면 [파일] > [열기] > [프로젝트]로 이동하고 .sln 파일을 선택합니다.
