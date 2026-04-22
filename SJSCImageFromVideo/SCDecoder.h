#pragma once
extern "C" {
#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>
#include <libavutil/imgutils.h>
#include <libswscale/swscale.h>
#include <libavformat/avformat.h>
#include <libavutil/opt.h>
}
#include <thread>
#include <cstdint>

typedef void(*SCDecCallBack)(unsigned char*, int, int, int, int, void*);

class SCDecoder
{
private:
	AVFormatContext* m_pContext;
	AVPacket* m_pPacket;
	AVFrame* m_pFrame;
	AVCodecContext* m_pCodecContext;
	SCDecCallBack m_pDecCallBackFunc;
	int m_iCurrentFrame;
	int m_iVideoStreamIndex;
	const char* m_pFoldername;
	
	AVFrame* m_pRGBFrame;
	unsigned char* m_pRGBFrameBuffer;
	SwsContext* m_pSWSContext;

	void* m_pCallerPtr;
	int   m_iDecID;

	std::thread m_threadDecoding;
	bool m_IsFinish;
	bool m_bDecoderReady;
	
	int64_t m_numFrame;
	float   m_fFrameRate;

	int m_iWidth;
	int m_iHeight;
public:
	SCDecoder();
	~SCDecoder();
	void Initialize(const char* filename, const char *outoutFolder, int id);
	void Initialize(const char* filename, int id);

	void StartDecoding(int start, int end);
	void StartDecoding(int start);
	void StartDecoding();
	
	void StopDecoding();

	void DoDecoding(int start, int end);
	void DoDecoding(int start);
	void DoDecoding();

	void SavePNGImage();
	void SetSCDecCallBack(SCDecCallBack callback, void* callerPtr);

	void ReadyDecoding();
	bool IsFinish();

	int GetWidth();
	int GetHeight();
	int64_t GetNumFrame();
	float GetFrameRate();
};

