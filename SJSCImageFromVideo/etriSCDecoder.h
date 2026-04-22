#pragma once
#include <cstdint>
#include <cstddef>
class DecoderManager;
extern "C" {
	DecoderManager* DecoderManager_New();
	int DecoderManager_Prepare(DecoderManager* manager, int numDecoder, char** filenames, const char *foldername);
	int DecoderManager_Initialize(DecoderManager* manager, int numDecoder, char** filenames, const char *foldername);
	int DecoderManager_Initialize_Range(DecoderManager* manager, int numDecoder, char** filenames, const char *foldername, int start, int end);	
	int DecoderManager_DoDecoding(DecoderManager* manager);
	int DecoderManager_Finalize(DecoderManager* manager);
	int64_t DecoderManager_GetNumFrame(DecoderManager* manager);
	float DecoderManager_GetFrameRate(DecoderManager* manager);
	int DecoderManager_GetWidth(DecoderManager* manager);
	int DecoderManager_GetHeight(DecoderManager* manager);
	int DecoderManager_GetStartFrame(DecoderManager* manager);
	int DecoderManager_GetEndFrame(DecoderManager* manager);

}
