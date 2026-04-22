SJCUDACommon.o : SJCUDACommon.cpp
	nvcc -ccbin g++ -std=c++11 -m64 -I. -Xcompiler -fPIC -c SJCUDACommon.cpp -o SJCUDACommon.o
SJCUDARenderer.o : SJCUDARenderer.cu
	nvcc -ccbin g++ -std=c++11 -m64 -I. -Xcompiler -fPIC -c SJCUDARenderer.cu -o SJCUDARenderer.o
SJPlenopticPacker.o : SJPlenopticPacker.cu
	nvcc -ccbin g++ -std=c++11 -m64 -I. -Xcompiler -fPIC -c SJPlenopticPacker.cu -o SJPlenopticPacker.o `pkg-config opencv4 --cflags --libs`
SJLog.o : SJLog.cpp
	nvcc -ccbin g++ -std=c++11 -m64 -I. -Xcompiler -fPIC -c SJLog.cpp -o SJLog.o
etriSCAPI.o : etriSCAPI.cpp
	nvcc -ccbin g++ -std=c++11 -m64 -I. -Xcompiler -fPIC -c etriSCAPI.cpp -o etriSCAPI.o
libetriSCAPI.so : SJCUDACommon.o SJCUDARenderer.o SJPlenopticPacker.o SJLog.o etriSCAPI.o
	nvcc -ccbin g++ -std=c++11 -m64 -I. -shared -o libetriSCAPI.so SJCUDACommon.o SJCUDARenderer.o SJPlenopticPacker.o SJLog.o etriSCAPI.o `pkg-config opencv4 --cflags --libs`
main.o : main.cpp 
	nvcc -ccbin g++ -std=c++11 -m64 -I. -c main.cpp -o main.o `pkg-config opencv4 --cflags --libs`
all : main.o libetriSCAPI.so
	nvcc -ccbin g++ -std=c++11 -m64 main.o -o etriSCAPI `pkg-config opencv4 --cflags --libs` -L. -letriSCAPI
	rm *.o
clean: 
	rm *.o *.so etriSCAPI