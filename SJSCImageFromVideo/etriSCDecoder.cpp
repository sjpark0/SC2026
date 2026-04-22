#include "etriSCDecoder.h"
#include "DecoderManager.h"
DecoderManager* DecoderManager_New()
{
	return new DecoderManager();
}
int DecoderManager_Prepare(DecoderManager* manager, int numDecoder, char** filenames, const char *foldername)
{
	manager->Prepare(numDecoder, filenames, foldername);
	return 0;
}
	
int DecoderManager_Initialize(DecoderManager* manager, int numDecoder, char** filenames, const char *foldername)
{
	manager->Initialize(numDecoder, filenames, foldername, 0);
	return 0;
}	
int DecoderManager_Initialize_Range(DecoderManager* manager, int numDecoder, char** filenames, const char *foldername, int start, int end)
{
	manager->Initialize(numDecoder, filenames, foldername, start, end, 0);
	return 0;
}
int DecoderManager_DoDecoding(DecoderManager* manager)
{
	manager->DoDecoding();
	return 0;
}
int DecoderManager_Finalize(DecoderManager* manager)
{
	delete manager;
	return 0;
}
int64_t DecoderManager_GetNumFrame(DecoderManager* manager)
{
	return manager->GetNumFrame();
}
float DecoderManager_GetFrameRate(DecoderManager* manager)
{
	return manager->GetFrameRate();
}
int DecoderManager_GetWidth(DecoderManager* manager)
{
	return manager->GetWidth();
}
int DecoderManager_GetHeight(DecoderManager* manager)
{
	return manager->GetHeight();
}
int DecoderManager_GetStartFrame(DecoderManager* manager)
{
	return manager->GetStartFrame();
}
int DecoderManager_GetEndFrame(DecoderManager* manager)
{
	return manager->GetEndFrame();
}