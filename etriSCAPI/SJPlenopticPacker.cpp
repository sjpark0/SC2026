#include "SJPlenopticPacker.h"
#include "SJLog.h"
#include <stdio.h>
#include "opencv2/opencv.hpp"
using namespace std;
using namespace cv;


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