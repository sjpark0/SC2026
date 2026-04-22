#include "SJPlenopticPacker.h"
#include "SJLog.h"
#include <device_functions.h>
#include "cuda_runtime.h"
#include "device_launch_parameters.h"
#include <stdio.h>
#include <memory.h>
#include "opencv2/opencv.hpp"
using namespace std;
using namespace cv;
__global__ void convertDecodedToImageBuffer(const CUDA_UCHAR* src, CUDA_UCHAR* dst, SJDim imageW, SJDim imageH, SJDim imageW2, SJDim imageH2, int numCam, SJDim startIdx)
{
    const int ix = blockDim.x * blockIdx.x + threadIdx.x;
    const int iy = blockDim.y * blockIdx.y + threadIdx.y;

    int imgOffsetX = 0;
    int imgOffsetY = 0;
    int cam = startIdx;
    if (ix < imageW && iy < imageH) {

        while (true) {
            dst[(ix + iy * imageW + cam * imageW * imageH) * 3] = src[(ix + imgOffsetX + (iy + imgOffsetY) * imageW2) * 3];
            dst[(ix + iy * imageW + cam * imageW * imageH) * 3 + 1] = src[(ix + imgOffsetX + (iy + imgOffsetY) * imageW2) * 3 + 1];
            dst[(ix + iy * imageW + cam * imageW * imageH) * 3 + 2] = src[(ix + imgOffsetX + (iy + imgOffsetY) * imageW2) * 3 + 2];

            cam++;
            if (cam >= numCam) break;

            imgOffsetY += imageH;
            if (imgOffsetY >= imageH2) {
                imgOffsetX += imageW;
                imgOffsetY = 0;
            }
            if (imgOffsetX >= imageW2) {
                imgOffsetX = 0;
                break;
            }
        }
    }
}

__global__ void convertDecodedToImageBuffer_Resizing(const CUDA_UCHAR* src, CUDA_UCHAR* dst, SJDim imageW, SJDim imageH, SJDim newImageW, SJDim newImageH, SJDim imageW2, SJDim imageH2, int numCam, SJDim startIdx)
{
    const int ix = blockDim.x * blockIdx.x + threadIdx.x;
    const int iy = blockDim.y * blockIdx.y + threadIdx.y;

    int imgOffsetX = 0;
    int imgOffsetY = 0;
    int cam = startIdx;
    int factor = (int)(imageW / newImageW);
    if (ix < newImageW && iy < newImageH) {

        while (true) {
            dst[(ix + iy * newImageW + cam * newImageW * newImageH) * 3] = src[(ix * factor + imgOffsetX + (iy * factor + imgOffsetY) * imageW2) * 3 + 0];
            dst[(ix + iy * newImageW + cam * newImageW * newImageH) * 3 + 1] = src[(ix * factor + imgOffsetX + (iy * factor + imgOffsetY) * imageW2) * 3 + 1];
            dst[(ix + iy * newImageW + cam * newImageW * newImageH) * 3 + 2] = src[(ix * factor + imgOffsetX + (iy * factor + imgOffsetY) * imageW2) * 3 + 2];

            cam++;
            if (cam >= numCam) break;

            imgOffsetY += imageH;
            if (imgOffsetY >= imageH2) {
                imgOffsetX += imageW;
                imgOffsetY = 0;
            }
            if (imgOffsetX >= imageW2) {
                imgOffsetX = 0;
                break;
            }
        }
    }
}
__global__ void convertDecodedToAlphaBuffer(const CUDA_UCHAR* src, CUDA_UCHAR* alphaImage, int imageW, int imageH, int imageW2, int imageH2, int numLevel, int numCam, int startID, int levelID)
{
    const int ix = blockDim.x * blockIdx.x + threadIdx.x;
    const int iy = blockDim.y * blockIdx.y + threadIdx.y;

    int imgOffsetX = 0;
    int imgOffsetY = 0;
    int cam = startID;
    int level = levelID;
    if (ix < imageW && iy < imageH) {
        while (true) {
            if (level < numLevel - 2) {
                alphaImage[ix + iy * imageW + level * imageW * imageH + cam * imageW * imageH * numLevel] = src[(ix + imgOffsetX + (iy + imgOffsetY) * imageW2) * 3 + 0];
                alphaImage[ix + iy * imageW + (level + 1) * imageW * imageH + cam * imageW * imageH * numLevel] = src[(ix + imgOffsetX + (iy + imgOffsetY) * imageW2) * 3 + 1];
                alphaImage[ix + iy * imageW + (level + 2) * imageW * imageH + cam * imageW * imageH * numLevel] = src[(ix + imgOffsetX + (iy + imgOffsetY) * imageW2) * 3 + 2];
                level += 3;

                imgOffsetY += imageH;
                if (imgOffsetY >= imageH2) {
                    imgOffsetX += imageW;
                    imgOffsetY = 0;
                }
                if (imgOffsetX >= imageW2) {
                    imgOffsetX = 0;
                    break;
                }
            }
            else {
                alphaImage[ix + iy * imageW + level * imageW * imageH + cam * imageW * imageH * numLevel] = src[(ix + imgOffsetX + (iy + imgOffsetY) * imageW2) * 3 + 0];
                alphaImage[ix + iy * imageW + (level + 1) * imageW * imageH + cam * imageW * imageH * numLevel] = src[(ix + imgOffsetX + (iy + imgOffsetY) * imageW2) * 3 + 1];

                level = 0;
                cam++;
                if (cam >= numCam) break;

                imgOffsetY += imageH;
                if (imgOffsetY >= imageH2) {
                    imgOffsetX += imageW;
                    imgOffsetY = 0;
                }
                if (imgOffsetX >= imageW2) {
                    imgOffsetX = 0;
                    break;
                }
            }
        }
    }
}


SJPlenopticPacker::SJPlenopticPacker()
{
    m_pDim = NULL;
    m_pMPIDim = NULL;
    m_pLookupImage = NULL;
    m_pLookupAlphaImage = NULL;
    m_pLookupAlphaLevel = NULL;
}
SJPlenopticPacker::~SJPlenopticPacker()
{
    if (m_pDim) {
        delete[]m_pDim;
        m_pDim = NULL;
    }
    if (m_pMPIDim) {
        delete[]m_pMPIDim;
        m_pMPIDim = NULL;
    }
    if (m_pLookupImage) {
        delete[]m_pLookupImage;
        m_pLookupImage = NULL;
    }
    if (m_pLookupAlphaImage) {
        delete[]m_pLookupAlphaImage;
        m_pLookupAlphaImage = NULL;
    }
    if (m_pLookupAlphaLevel) {
        delete[]m_pLookupAlphaLevel;
        m_pLookupAlphaLevel = NULL;
    }
}
void SJPlenopticPacker::MakeLookupTableImage(int iDecWidth, int iDecHeight, SJDim numCam, SJDim width, SJDim height, int* pLookupImage)
{
    LOGGING(LOG_LEVEL::VERBOSE, "Start\n");

    int imgOffsetX;
    int imgOffsetY;
    int camID;
    int levelID;
    int encoderID;
    encoderID = camID = imgOffsetX = imgOffsetY = 0;
    pLookupImage[encoderID] = camID;
    while (true) {

        camID++;
        if (camID >= numCam) break;

        imgOffsetY += height;
        if (imgOffsetY >= iDecHeight) {
            imgOffsetX += width;
            imgOffsetY = 0;
        }
        if (imgOffsetX >= iDecWidth) {
            imgOffsetX = 0;
            encoderID++;
            pLookupImage[encoderID] = camID;
        }
    }
    LOGGING(LOG_LEVEL::VERBOSE, "End\n");

}
void SJPlenopticPacker::MakeLookupTableLayer(int iDecWidth, int iDecHeight, SJDim numCam, SJDim layerWidth, SJDim layerHeight, SJDim layerLevel, int* pLookupAlphaImage, int* pLookupAlphaLevel)
{
    LOGGING(LOG_LEVEL::VERBOSE, "Start\n");
    int imgOffsetX;
    int imgOffsetY;
    int camID;
    int levelID;
    int encoderID;


    levelID = encoderID = camID = imgOffsetX = imgOffsetY = 0;
    int preCamID = -1;
    pLookupAlphaImage[encoderID] = camID;
    pLookupAlphaLevel[encoderID] = levelID;
    while (true) {
        if (levelID < layerLevel - 2) {

            imgOffsetY += layerHeight;

            levelID += 3;

            if (imgOffsetY >= iDecHeight) {
                imgOffsetX += layerWidth;
                imgOffsetY = 0;
            }
            if (imgOffsetX >= iDecWidth) {
                imgOffsetX = 0;
                encoderID++;

                pLookupAlphaImage[encoderID] = camID;
                pLookupAlphaLevel[encoderID] = levelID;
            }
        }

        else {
            imgOffsetY += layerHeight;

            levelID = 0;
            camID++;
            if (camID >= numCam) break;

            if (imgOffsetY >= iDecHeight) {
                imgOffsetX += layerWidth;
                imgOffsetY = 0;
            }
            if (imgOffsetX >= iDecWidth) {
                imgOffsetX = 0;
                encoderID++;

                pLookupAlphaImage[encoderID] = camID;
                pLookupAlphaLevel[encoderID] = levelID;
            }

        }
    }
    LOGGING(LOG_LEVEL::VERBOSE, "End\n");

}


void SJPlenopticPacker::PackingImage(SJDim numCam, SJDim width, SJDim height, CPU_UCHAR** ppDecOut, CUDA_UCHAR** ppDecOutCUDA, int iDecWidth, int iDecHeight, int numImage, CPU_UCHAR* pImage)
{
    LOGGING(LOG_LEVEL::VERBOSE, "Start\n");

    Mat matDstImg;
    Mat matSrcImg;
    //Mat tempImg;

    int imgOffsetX;
    int imgOffsetY;
    int camID;
    int levelID;
    int encoderID;

    encoderID = camID = imgOffsetX = imgOffsetY = 0;

    matDstImg = Mat(iDecHeight, iDecWidth, CV_8UC3, ppDecOut[encoderID]);
    memset(ppDecOut[encoderID], 0, iDecHeight * iDecWidth * 3);
    //tempImg = Mat::zeros(iDecHeight, iDecWidth, CV_8UC3);

    while (true) {

        matSrcImg = Mat(height, width, CV_8UC3, &pImage[camID * width * height * 3]);
        matSrcImg.copyTo(matDstImg(Rect(imgOffsetX, imgOffsetY, width, height)));
        camID++;
        if (camID >= numCam) {
            //cvtColor(tempImg, matDstImg, COLOR_RGB2BGR);
            break;
        }

        imgOffsetY += height;
        if (imgOffsetY >= iDecHeight) {
            imgOffsetX += width;
            imgOffsetY = 0;
        }
        if (imgOffsetX >= iDecWidth) {
            imgOffsetX = 0;
            //cvtColor(tempImg, matDstImg, COLOR_RGB2BGR);
            encoderID++;
            matDstImg = Mat(iDecHeight, iDecWidth, CV_8UC3, ppDecOut[encoderID]);
            memset(ppDecOut[encoderID], 0, iDecHeight * iDecWidth * 3);
            //tempImg = Mat::zeros(iDecHeight, iDecWidth, CV_8UC3);
        }
    }
    char filename[1024];
    for (int i = 0; i < numImage; i++) {
        cudaMemcpy(ppDecOutCUDA[i], ppDecOut[i], iDecHeight * iDecWidth * 3 * sizeof(CUDA_UCHAR), cudaMemcpyHostToDevice);
        //    matDstImg = Mat(iDecHeight, iDecWidth, CV_8UC3, ppDecOut[i]);
        //    sprintf_s(filename, "Image_%d.png", i);
        //    imwrite(filename, matDstImg);
    }
    LOGGING(LOG_LEVEL::VERBOSE, "End\n");

}
void SJPlenopticPacker::PackingLayer(SJDim numCam, SJDim layerWidth, SJDim layerHeight, SJDim layerLevel, CPU_UCHAR** ppDecOut, CUDA_UCHAR** ppDecOutCUDA, int iDecWidth, int iDecHeight, int numLayer, CPU_UCHAR* pLayer)
{
    LOGGING(LOG_LEVEL::VERBOSE, "Start\n");

    unsigned char* srcImage = new unsigned char[layerWidth * layerHeight * 3];

    Mat matDstImg;
    Mat matSrcImg;

    int index;
    int imgOffsetX;
    int imgOffsetY;
    int camID;
    int levelID;
    int encoderID;


    levelID = encoderID = camID = imgOffsetX = imgOffsetY = 0;
    int preCamID = -1;
    for (int i = 0; i < numLayer; i++) {
        memset(ppDecOut[i], 0, iDecWidth * iDecHeight * 3 * sizeof(unsigned char));
    }
    matDstImg = Mat(iDecHeight, iDecWidth, CV_8UC3, ppDecOut[encoderID]);
    while (true) {

        if (levelID < layerLevel - 2) {
            for (int j = 0; j < layerWidth * layerHeight; j++) {
                index = j + levelID * layerWidth * layerHeight + camID * layerWidth * layerHeight * layerLevel;
                srcImage[j * 3 + 0] = pLayer[index];
                srcImage[j * 3 + 1] = pLayer[index + layerWidth * layerHeight];
                srcImage[j * 3 + 2] = pLayer[index + layerWidth * layerHeight * 2];
            }
            matSrcImg = Mat(layerHeight, layerWidth, CV_8UC3, srcImage);

            matSrcImg.copyTo(matDstImg(Rect(imgOffsetX, imgOffsetY, layerWidth, layerHeight)));


            imgOffsetY += layerHeight;

            levelID += 3;

            if (imgOffsetY >= iDecHeight) {
                imgOffsetX += layerWidth;
                imgOffsetY = 0;
            }
            if (imgOffsetX >= iDecWidth) {
                imgOffsetX = 0;
                encoderID++;
                matDstImg = Mat(iDecHeight, iDecWidth, CV_8UC3, ppDecOut[encoderID]);
            }
        }

        else {
            for (int j = 0; j < layerWidth * layerHeight; j++) {
                index = j + levelID * layerWidth * layerHeight + camID * layerWidth * layerHeight * layerLevel;
                srcImage[j * 3 + 0] = pLayer[index];
                srcImage[j * 3 + 1] = pLayer[index + layerWidth * layerHeight];
                srcImage[j * 3 + 2] = 0;
            }
            matSrcImg = Mat(layerHeight, layerWidth, CV_8UC3, srcImage);

            matSrcImg.copyTo(matDstImg(Rect(imgOffsetX, imgOffsetY, layerWidth, layerHeight)));

            imgOffsetY += layerHeight;

            levelID = 0;
            camID++;
            if (camID >= numCam) break;

            if (imgOffsetY >= iDecHeight) {
                imgOffsetX += layerWidth;
                imgOffsetY = 0;
            }
            if (imgOffsetX >= iDecWidth) {
                imgOffsetX = 0;
                encoderID++;
                matDstImg = Mat(iDecHeight, iDecWidth, CV_8UC3, ppDecOut[encoderID]);

            }

        }
    }

    char filename[1024];
    for (int i = 0; i < numLayer; i++) {
        cudaMemcpy(ppDecOutCUDA[i], ppDecOut[i], iDecHeight * iDecWidth * 3 * sizeof(CUDA_UCHAR), cudaMemcpyHostToDevice);
        //    matDstImg = Mat(iDecHeight, iDecWidth, CV_8UC3, ppDecOut[i]);
        //    sprintf_s(filename, "Layer_%d.png", i);
        //    imwrite(filename, matDstImg);
    }
    delete[]srcImage;
    LOGGING(LOG_LEVEL::VERBOSE, "End\n");

}

void SJPlenopticPacker::Initialize(SJDim* pDim, SJDim* pMPIDim, int iDecWidth, int iDecHeight, int numImage, int numLayer)
{
    LOGGING(LOG_LEVEL::VERBOSE, "Start\n");
    m_iDecWidth = iDecWidth;
    m_iDecHeight = iDecHeight;
    m_numImage = numImage;
    m_numLayer = numLayer;

    m_pDim = new SJDim[4];
    m_pMPIDim = new SJDim[5];
    memcpy(m_pDim, pDim, 4 * sizeof(SJDim));
    memcpy(m_pMPIDim, pMPIDim, 5 * sizeof(SJDim));

    m_pLookupImage = new int[numImage];
    MakeLookupTableImage(iDecWidth, iDecHeight, pDim[0] * pDim[1], pDim[3], pDim[2], m_pLookupImage);

    m_pLookupAlphaImage = new int[numLayer];
    m_pLookupAlphaLevel = new int[numLayer];
    MakeLookupTableLayer(iDecWidth, iDecHeight, m_pMPIDim[0] * m_pMPIDim[1], m_pMPIDim[3], m_pMPIDim[2], m_pMPIDim[4], m_pLookupAlphaImage, m_pLookupAlphaLevel);

    m_layerThread.x = m_thread.x = BLOCKDIM_X;
    m_layerThread.y = m_thread.y = BLOCKDIM_Y;
    m_layerThread.z = m_thread.z = 1;

    m_grid.x = iDivUp(m_pDim[3], BLOCKDIM_X);
    m_layerGrid.x = iDivUp(m_pMPIDim[3], BLOCKDIM_X);
    m_grid.y = iDivUp(m_pDim[2], BLOCKDIM_Y);
    m_layerGrid.y = iDivUp(m_pMPIDim[2], BLOCKDIM_X);
    m_layerGrid.z = m_grid.z = 1;
    LOGGING(LOG_LEVEL::VERBOSE, "End\n");

}


void SJPlenopticPacker::UnPackingImage(CUDA_UCHAR** ppDecOutCUDA, CUDA_UCHAR* pImageCUDA)
{
    //LOGGING(LOG_LEVEL::VERBOSE, "Start\n");

    for (int i = 0; i < m_numImage; i++) {
        convertDecodedToImageBuffer << <m_grid, m_thread >> > (ppDecOutCUDA[i], pImageCUDA, m_pDim[3], m_pDim[2], m_iDecWidth, m_iDecHeight, m_pDim[0] * m_pDim[1], m_pLookupImage[i]);
    }
    //LOGGING(LOG_LEVEL::VERBOSE, "End\n");
}

void SJPlenopticPacker::UnPackingImageWithIndex(CUDA_UCHAR* ppDecOutCUDA, CUDA_UCHAR* pImageCUDA, int index)
{
    //LOGGING(LOG_LEVEL::VERBOSE, "Start\n");

    convertDecodedToImageBuffer << <m_grid, m_thread >> > (ppDecOutCUDA, pImageCUDA, m_pDim[3], m_pDim[2], m_iDecWidth, m_iDecHeight, m_pDim[0] * m_pDim[1], m_pLookupImage[index]);
    //LOGGING(LOG_LEVEL::VERBOSE, "End\n");
}

void SJPlenopticPacker::UnPackingLayer(CUDA_UCHAR** ppDecOutCUDA, CUDA_UCHAR* pLayerCUDA)
{
    //dim3 threads(BLOCKDIM_X, BLOCKDIM_Y);
    //dim3 grid(iDivUp(m_pMPIDim[3], BLOCKDIM_X), iDivUp(m_pMPIDim[2], BLOCKDIM_Y));

    for (int i = 0; i < m_numLayer; i++) {
        convertDecodedToAlphaBuffer << <m_layerGrid, m_layerThread >> > (ppDecOutCUDA[i], pLayerCUDA, m_pMPIDim[3], m_pMPIDim[2], m_iDecWidth, m_iDecHeight, m_pMPIDim[4], m_pMPIDim[0] * m_pMPIDim[1], m_pLookupAlphaImage[i], m_pLookupAlphaLevel[i]);
    }
}

void SJPlenopticPacker::UnPackingImageCPU(SJDim numCam, SJDim width, SJDim height, const CPU_UCHAR** ppDecOut, int iDecWidth, int iDecHeight, int numImage, CPU_UCHAR* pImage)
{
    LOGGING(LOG_LEVEL::VERBOSE, "Start\n");

    int numElementImage = (iDecWidth / width) * (iDecHeight / height);
    CUDA_UCHAR** ppDecOutCUDA = new CUDA_UCHAR * [numImage];
    CUDA_UCHAR* pImageCUDA;
    for (int i = 0; i < numImage; i++) {
        cudaMalloc((void**)&ppDecOutCUDA[i], iDecWidth * iDecHeight * 3 * sizeof(CUDA_UCHAR));
        cudaMemcpy(ppDecOutCUDA[i], ppDecOut[i], iDecWidth * iDecHeight * 3 * sizeof(CUDA_UCHAR), cudaMemcpyHostToDevice);
    }
    cudaMalloc((void**)&pImageCUDA, width * height * 3 * numCam * sizeof(CUDA_UCHAR));

    int* pLookupImage = new int[numImage];
    MakeLookupTableImage(iDecWidth, iDecHeight, numCam, width, height, pLookupImage);

    dim3 threads(BLOCKDIM_X, BLOCKDIM_Y);
    dim3 grid(iDivUp(width, BLOCKDIM_X), iDivUp(height, BLOCKDIM_Y));

    LOGGING(LOG_LEVEL::VERBOSE, "CUDA Kernel Invoke\n");

    for (int i = 0; i < numImage; i++) {
        convertDecodedToImageBuffer << <grid, threads >> > (ppDecOutCUDA[i], pImageCUDA, width, height, iDecWidth, iDecHeight, numCam, pLookupImage[i]);
    }
    LOGGING(LOG_LEVEL::VERBOSE, "CUDA Kernel Finish\n");

    cudaMemcpy(pImage, pImageCUDA, numCam * width * height * 3 * sizeof(CUDA_UCHAR), cudaMemcpyDeviceToHost);
    for (int i = 0; i < numImage; i++) {
        cudaFree(ppDecOutCUDA[i]);
    }
    cudaFree(pImageCUDA);

    delete[]ppDecOutCUDA;
    delete[]pLookupImage;
    LOGGING(LOG_LEVEL::VERBOSE, "End\n");


}
void SJPlenopticPacker::UnPackingImageWithIndex(SJDim numCam, SJDim width, SJDim height, const CPU_UCHAR** ppDecOut, int iDecWidth, int iDecHeight, int numImage, int index, CPU_UCHAR* pImage)
{
    LOGGING(LOG_LEVEL::VERBOSE, "Start\n");

    int numElementImage = (iDecWidth / width) * (iDecHeight / height);
    int numImageID = index / numElementImage;
    int numElementID = index % numElementImage;
    CUDA_UCHAR* pDecOutCUDA;
    CUDA_UCHAR* pImageCUDA;
    cudaMalloc((void**)&pDecOutCUDA, iDecWidth * iDecHeight * 3 * sizeof(CUDA_UCHAR));
    cudaMalloc((void**)&pImageCUDA, width * height * 3 * numElementImage * sizeof(CUDA_UCHAR));

    cudaMemcpy(pDecOutCUDA, ppDecOut[numImageID], iDecWidth * iDecHeight * 3 * sizeof(CUDA_UCHAR), cudaMemcpyHostToDevice);

    dim3 threads(BLOCKDIM_X, BLOCKDIM_Y);
    dim3 grid(iDivUp(width, BLOCKDIM_X), iDivUp(height, BLOCKDIM_Y));

    LOGGING(LOG_LEVEL::VERBOSE, "CUDA Kernel Invoke\n");

    convertDecodedToImageBuffer << <grid, threads >> > (pDecOutCUDA, pImageCUDA, width, height, iDecWidth, iDecHeight, numCam, 0);

    LOGGING(LOG_LEVEL::VERBOSE, "CUDA Kernel Finish\n");


    cudaMemcpy(pImage, &pImageCUDA[numElementID * width * height * 3], width * height * 3 * sizeof(CUDA_UCHAR), cudaMemcpyDeviceToHost);

    cudaFree(pDecOutCUDA);
    cudaFree(pImageCUDA);
    LOGGING(LOG_LEVEL::VERBOSE, "End\n");

}
void SJPlenopticPacker::UnPackingImageWithIndexCUDA(SJDim numCam, SJDim width, SJDim height, const CUDA_UCHAR** ppDecOut, int iDecWidth, int iDecHeight, int numImage, int index, CPU_UCHAR* pImage)
{
    LOGGING(LOG_LEVEL::VERBOSE, "Start\n");

    int numElementImage = (iDecWidth / width) * (iDecHeight / height);
    int numImageID = index / numElementImage;
    int numElementID = index % numElementImage;
    CUDA_UCHAR* pImageCUDA;

    cudaMalloc((void**)&pImageCUDA, width * height * 3 * numElementImage * sizeof(CUDA_UCHAR));

    dim3 threads(BLOCKDIM_X, BLOCKDIM_Y);
    dim3 grid(iDivUp(width, BLOCKDIM_X), iDivUp(height, BLOCKDIM_Y));

    LOGGING(LOG_LEVEL::VERBOSE, "CUDA Kernel Invoke\n");

    convertDecodedToImageBuffer << <grid, threads >> > (ppDecOut[numImageID], pImageCUDA, width, height, iDecWidth, iDecHeight, numCam, 0);

    LOGGING(LOG_LEVEL::VERBOSE, "CUDA Kernel Finish\n");


    cudaMemcpy(pImage, &pImageCUDA[numElementID * width * height * 3], width * height * 3 * sizeof(CUDA_UCHAR), cudaMemcpyDeviceToHost);

    cudaFree(pImageCUDA);
    LOGGING(LOG_LEVEL::VERBOSE, "End\n");

}
void SJPlenopticPacker::UnPackingLayerCPU(SJDim numCam, SJDim layerWidth, SJDim layerHeight, SJDim layerLevel, const CPU_UCHAR** ppDecOut, int iDecWidth, int iDecHeight, int numLayer, CPU_UCHAR* pLayer)
{
    LOGGING(LOG_LEVEL::VERBOSE, "Start\n");

    CUDA_UCHAR** ppDecOutCUDA = new CUDA_UCHAR * [numLayer];
    CUDA_UCHAR* pLayerCUDA;

    for (int i = 0; i < numLayer; i++) {
        cudaMalloc((void**)&ppDecOutCUDA[i], iDecWidth * iDecHeight * 3 * sizeof(CUDA_UCHAR));
        cudaMemcpy(ppDecOutCUDA[i], ppDecOut[i], iDecWidth * iDecHeight * 3 * sizeof(CUDA_UCHAR), cudaMemcpyHostToDevice);
    }
    cudaMalloc((void**)&pLayerCUDA, layerWidth * layerHeight * layerLevel * numCam * sizeof(CUDA_UCHAR));

    int* pLookupAlphaImage = new int[numLayer];
    int* pLookupAlphaLevel = new int[numLayer];
    MakeLookupTableLayer(iDecWidth, iDecHeight, numCam, layerWidth, layerHeight, layerLevel, pLookupAlphaImage, pLookupAlphaLevel);

    dim3 threads(BLOCKDIM_X, BLOCKDIM_Y);
    dim3 grid(iDivUp(layerWidth, BLOCKDIM_X), iDivUp(layerHeight, BLOCKDIM_Y));

    LOGGING(LOG_LEVEL::VERBOSE, "CUDA Kernel Invoke\n");

    for (int i = 0; i < numLayer; i++) {
        convertDecodedToAlphaBuffer << <grid, threads >> > (ppDecOutCUDA[i], pLayerCUDA, layerWidth, layerHeight, iDecWidth, iDecHeight, layerLevel, numCam, pLookupAlphaImage[i], pLookupAlphaLevel[i]);
    }

    LOGGING(LOG_LEVEL::VERBOSE, "CUDA Kernel Finish\n");

    cudaMemcpy(pLayer, pLayerCUDA, numCam * layerWidth * layerHeight * layerLevel * sizeof(CUDA_UCHAR), cudaMemcpyDeviceToHost);

    for (int i = 0; i < numLayer; i++) {
        cudaFree(ppDecOutCUDA[i]);
    }
    cudaFree(pLayerCUDA);

    delete[]ppDecOutCUDA;
    delete[]pLookupAlphaImage;
    delete[]pLookupAlphaLevel;
    LOGGING(LOG_LEVEL::VERBOSE, "End\n");

}

