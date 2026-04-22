#include "SCDecoder.h"
#include <stdio.h>
#include <fstream>

#include "opencv2/imgcodecs.hpp"
#include "opencv2/highgui.hpp"
#include "opencv2/imgproc.hpp"
using namespace cv;

typedef struct _DecoderArgument {
	SCDecoder* caller;
	int start;
	int end;
}DecoderArgument;

void DecodingLoop(void* args)
{	
	DecoderArgument* argument = (DecoderArgument*)args;
	if (argument->end == -1) {
		if (argument->start == -1) {

			argument->caller->DoDecoding();
		}
		else {
			argument->caller->DoDecoding(argument->start);
		}
	}
	else {
		argument->caller->DoDecoding(argument->start, argument->end);
	}
}
SCDecoder::SCDecoder()
{
	m_pContext = NULL;
	m_pPacket = NULL;
	m_pFrame = NULL;
	m_pRGBFrame = NULL;
	m_pRGBFrameBuffer = NULL;
	m_pCodecContext = NULL;
	m_pDecCallBackFunc = NULL;
	m_pSWSContext = NULL;
	m_iDecID = -1;
	m_numFrame = -1;
}
SCDecoder::~SCDecoder()
{
	if (m_pContext) {
		avformat_close_input(&m_pContext);
		m_pContext = NULL;
	}
	if (m_pPacket) {
		av_packet_free(&m_pPacket);
		m_pPacket = NULL;
	}
	if (m_pFrame) {
		av_frame_free(&m_pFrame);
		m_pFrame = NULL;
	}
	if (m_pRGBFrame) {
		av_frame_free(&m_pRGBFrame);
		m_pRGBFrame = NULL;
	}
	if (m_pCodecContext) {
		avcodec_close(m_pCodecContext);
		avcodec_free_context(&m_pCodecContext);
		m_pCodecContext = NULL;
	}
	if (m_pRGBFrameBuffer) {
		av_free(m_pRGBFrameBuffer);
		m_pRGBFrameBuffer = NULL;
	}
	if (m_pSWSContext) {
		sws_freeContext(m_pSWSContext);
		m_pSWSContext = NULL;
	}

}
void SCDecoder::Initialize(const char* filename, const char *outputFolder, int id)
{
	Initialize(filename, id);
	m_pFoldername = outputFolder;

}
void SCDecoder::Initialize(const char* filename, int id)
{
	m_iDecID = id;
	avformat_open_input(&m_pContext, filename, nullptr, nullptr);
	avformat_find_stream_info(m_pContext, nullptr);
	m_iVideoStreamIndex = -1;
	AVCodecParameters* codec_params = nullptr;
	for (unsigned int i = 0; i < m_pContext->nb_streams; i++) {
		if (m_pContext->streams[i]->codecpar->codec_type == AVMEDIA_TYPE_VIDEO) {
			m_iVideoStreamIndex = i;
			codec_params = m_pContext->streams[i]->codecpar;
			//printf("%d, %d, %f\n", m_pContext->streams[i]->avg_frame_rate.num, m_pContext->streams[i]->avg_frame_rate.den, (float)m_pContext->streams[i]->avg_frame_rate.num / (float)m_pContext->streams[i]->avg_frame_rate.den);
			//printf("%ld\n", m_pContext->streams[i]->nb_frames);
			m_numFrame = m_pContext->streams[i]->nb_frames;
			m_fFrameRate = (float)m_pContext->streams[i]->avg_frame_rate.num / (float)m_pContext->streams[i]->avg_frame_rate.den;
			break;
		}
	}
	
	const AVCodec* codec = avcodec_find_decoder(codec_params->codec_id);
	m_pCodecContext = avcodec_alloc_context3(codec);
	
	avcodec_parameters_to_context(m_pCodecContext, codec_params);
		
	avcodec_open2(m_pCodecContext, codec, nullptr);

	m_pFrame = av_frame_alloc();
	m_pPacket = av_packet_alloc();

	m_iCurrentFrame = 0;
	
	m_pRGBFrame = av_frame_alloc();
	int num_bytes = av_image_get_buffer_size(AV_PIX_FMT_RGB24, codec_params->width, codec_params->height, 1);

	m_pRGBFrameBuffer = (unsigned char*)av_malloc(num_bytes * sizeof(unsigned char));
	av_image_fill_arrays(m_pRGBFrame->data, m_pRGBFrame->linesize, m_pRGBFrameBuffer, AV_PIX_FMT_RGB24, codec_params->width, codec_params->height, 1);
	m_pRGBFrame->width = codec_params->width;
	m_pRGBFrame->height = codec_params->height;
	m_pRGBFrame->format = AV_PIX_FMT_RGB24;
	m_iWidth = m_pRGBFrame->width;
	m_iHeight = m_pRGBFrame->height;

	m_pSWSContext = sws_getContext(codec_params->width, codec_params->height, (AVPixelFormat)codec_params->format, m_pRGBFrame->width, m_pRGBFrame->height, AV_PIX_FMT_RGB24, SWS_BILINEAR, NULL, NULL, NULL);
}
void SCDecoder::StartDecoding(int start, int end)
{
	DecoderArgument* args = new DecoderArgument;
	args->caller = this;
	args->start = start;
	args->end = end;
	m_IsFinish = false;	
	m_threadDecoding = std::thread(DecodingLoop, args);
}
void SCDecoder::StartDecoding(int start)
{
	DecoderArgument* args = new DecoderArgument;
	args->caller = this;
	args->start = start;
	args->end = -1;
	m_IsFinish = false;
	m_threadDecoding = std::thread(DecodingLoop, args);
}
void SCDecoder::StartDecoding()
{
	DecoderArgument *args = new DecoderArgument;
	args->caller = this;
	args->start = -1;
	args->end = -1;
	m_IsFinish = false;
	m_threadDecoding = std::thread(DecodingLoop, (void*)args);
}
void SCDecoder::StopDecoding()
{
	if (m_threadDecoding.joinable()) {
		m_threadDecoding.join();
	}
}
void SCDecoder::ReadyDecoding()
{
	m_bDecoderReady = true;
}
void SCDecoder::DoDecoding(int start, int end)
{
	while (av_read_frame(m_pContext, m_pPacket) >= 0) {
		if (m_pPacket->stream_index == m_iVideoStreamIndex) {
			int response = avcodec_send_packet(m_pCodecContext, m_pPacket);
			while (response >= 0) {
				response = avcodec_receive_frame(m_pCodecContext, m_pFrame);
				//printf("%d\n", frame->best_effort_timestamp);
				if (response == AVERROR(EAGAIN) || response == AVERROR_EOF) {
					break;
				}
				m_iCurrentFrame++;
				
				m_bDecoderReady = false;
				if (m_iCurrentFrame >= start && m_iCurrentFrame <= end) {

                    //SavePNGImage();
					printf("%dth decoder: %dth frame\n", m_iDecID, m_iCurrentFrame);
				
					sws_scale(m_pSWSContext, (const uint8_t* const*)m_pFrame->data, m_pFrame->linesize, 0, m_pFrame->height, m_pRGBFrame->data, m_pRGBFrame->linesize);
					m_pDecCallBackFunc(m_pRGBFrameBuffer, m_pFrame->width, m_pFrame->height, m_iCurrentFrame, m_iDecID, m_pCallerPtr);		
								
				}
				else {
					m_bDecoderReady = true;
				}
				
				while (!m_bDecoderReady) {
					std::this_thread::yield();
				}
			}
		}
		av_packet_unref(m_pPacket);
		if (m_iCurrentFrame > end) {
			break;
		}
	}
	
	m_IsFinish = true;
}


void SCDecoder::DoDecoding(int start)
{
	while (av_read_frame(m_pContext, m_pPacket) >= 0) {
		if (m_pPacket->stream_index == m_iVideoStreamIndex) {
			int response = avcodec_send_packet(m_pCodecContext, m_pPacket);

			while (response >= 0) {
				response = avcodec_receive_frame(m_pCodecContext, m_pFrame);
				//printf("%d\n", frame->best_effort_timestamp);
				if (response == AVERROR(EAGAIN) || response == AVERROR_EOF) {
					break;
				}
				m_iCurrentFrame++;

				m_bDecoderReady = false;

				if (m_iCurrentFrame >= start) {

					//SavePNGImage();
					printf("%dth decoder: %dth frame\n", m_iDecID, m_iCurrentFrame);
				
					sws_scale(m_pSWSContext, (const uint8_t* const*)m_pFrame->data, m_pFrame->linesize, 0, m_pFrame->height, m_pRGBFrame->data, m_pRGBFrame->linesize);
					m_pDecCallBackFunc(m_pRGBFrameBuffer, m_pFrame->width, m_pFrame->height, m_iCurrentFrame, m_iDecID, m_pCallerPtr);
					

				}
				else {
					m_bDecoderReady = true;
				}
				
				while (!m_bDecoderReady) {
					std::this_thread::yield();
				}
			}
		}
		av_packet_unref(m_pPacket);		
	}
	m_IsFinish = true;

}
void SCDecoder::DoDecoding()
{
	while (av_read_frame(m_pContext, m_pPacket) >= 0) {
		if (m_pPacket->stream_index == m_iVideoStreamIndex) {
			int response = avcodec_send_packet(m_pCodecContext, m_pPacket);

			while (response >= 0) {
				response = avcodec_receive_frame(m_pCodecContext, m_pFrame);
				//printf("%d\n", frame->best_effort_timestamp);
				if (response == AVERROR(EAGAIN) || response == AVERROR_EOF) {
					break;
				}
				m_iCurrentFrame++;

				//SavePNGImage();
				m_bDecoderReady = false;

				printf("%dth decoder: %dth frame\n", m_iDecID, m_iCurrentFrame);
				sws_scale(m_pSWSContext, (const uint8_t* const*)m_pFrame->data, m_pFrame->linesize, 0, m_pFrame->height, m_pRGBFrame->data, m_pRGBFrame->linesize);
				m_pDecCallBackFunc(m_pRGBFrameBuffer, m_pFrame->width, m_pFrame->height, m_iCurrentFrame, m_iDecID, m_pCallerPtr);

				
				while (!m_bDecoderReady) {
					std::this_thread::yield();
				}

			}
		}
		av_packet_unref(m_pPacket);		
	}
	m_IsFinish = true;

}
void SCDecoder::SavePNGImage()
{     	
    sws_scale(m_pSWSContext, (const uint8_t* const*)m_pFrame->data, m_pFrame->linesize, 0, m_pFrame->height, m_pRGBFrame->data, m_pRGBFrame->linesize);

	char filename[1024];
	Mat img;
	Mat cvtImg;
	img = Mat(m_pFrame->height, m_pFrame->width, CV_8UC3, m_pRGBFrameBuffer);
	snprintf(filename, sizeof(filename), "%s\\frame_%04d.png", m_pFoldername, m_iCurrentFrame);
	cvtColor(img, cvtImg, COLOR_BGR2RGB);
	imwrite(filename, cvtImg);
	
}

void SCDecoder::SetSCDecCallBack(SCDecCallBack callback, void *callerPtr)
{
	m_pDecCallBackFunc = callback;
	m_pCallerPtr = callerPtr;
}
bool SCDecoder::IsFinish()
{
	return m_IsFinish;
}

int64_t SCDecoder::GetNumFrame()
{
	return m_numFrame;
}
float SCDecoder::GetFrameRate()
{
	return m_fFrameRate;
}

int SCDecoder::GetWidth()
{
	return m_iWidth;
}

int SCDecoder::GetHeight()
{
	return m_iHeight;
}