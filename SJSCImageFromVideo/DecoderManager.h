#pragma once
#include <cstdint>
class SCDecoder;

class DecoderManager
{
private:
	int m_numDecoder;
	bool* m_bStored;
	SCDecoder* m_pDecoder;
	
	unsigned char** m_ppDecoderFrame;
	char m_pFoldername[1024];
	int *m_pWidth;
	int *m_pHeight;
	int m_iCurrentFrame;
	int m_mode;
	int64_t m_numFrame;
	float m_fFrameRate;
	int m_iStartFrame;
	int m_iEndFrame;
public:
	DecoderManager();
	~DecoderManager();
	void Prepare(int numDecoder, char** filenames, const char* foldername);
	void Initialize(int numDecoder, char** filenames, const char *foldername, int mode);
	void Initialize(int numDecoder, char** filenames, const char *foldername, int start, int end, int mode);
	
	void DoDecoding();
	void DecodingProcess(unsigned char* frameBuffer, int frameID, int decoderID);

	int64_t GetNumFrame();
	float GetFrameRate();

	int GetWidth();
	int GetHeight();

	int GetStartFrame();
	int GetEndFrame();
};

