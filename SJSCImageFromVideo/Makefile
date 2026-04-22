DecoderManager.o : DecoderManager.cpp
	g++ -std=c++11 -m64 -I. -fPIC -c DecoderManager.cpp -o DecoderManager.o `pkg-config opencv4 --cflags --libs`

SCDecoder.o : SCDecoder.cpp
	g++ -std=c++11 -m64 -I. -fPIC -c SCDecoder.cpp -o SCDecoder.o `pkg-config opencv4 --cflags --libs`

etriSCDecoder.o : etriSCDecoder.cpp
	g++ -std=c++11 -m64 -I. -fPIC -c etriSCDecoder.cpp -o etriSCDecoder.o

libscdecoder.so : DecoderManager.o SCDecoder.o etriSCDecoder.o
	g++ -std=c++11 -m64 -I. -shared -o libscdecoder.so DecoderManager.o SCDecoder.o etriSCDecoder.o `pkg-config --cflags --libs opencv4 libavcodec libavformat libavutil libswscale`

SJSCImageFromVideo.o : SJSCImageFromVideo.cpp 
	g++ -std=c++11 -m64 -I. -fPIC -c SJSCImageFromVideo.cpp -o SJSCImageFromVideo.o

all : libscdecoder.so SJSCImageFromVideo.o
	g++ -std=c++11 -m64 SJSCImageFromVideo.o -o main `pkg-config --cflags --libs opencv4 libavcodec libavformat libavutil libswscale` -L. -lscdecoder
clean: 
	rm *.o *.so main