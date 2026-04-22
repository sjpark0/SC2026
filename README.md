# SC2025

## 1. installation
### pyinstaller로 실행파일 생성한뒤에 _internal폴더에 dynamic library를 추가하면, layer파일 생성가능
- 실행파일 생성 : pyinstaller make_layer.py
- dist폴더에 생성된 _internal폴더에 libcudnn과 관련된 so파일들과 libcublas관련된 so파일들 추가로 넣어줌
- llff는 특별한 환경을 갖추지 않아도 동작함
### colmap추가 설치 (3.11.0으로 설치)
- sudo apt-get install -y git cmake build-essential ninja-build libboost-program-options-dev libboost-graph-dev libboost-system-dev libeigen3-dev libflann-dev libfreeimage-dev libmetis-dev libgoogle-glog-dev libgtest-dev libgmock-dev libsqlite3-dev libglew-dev qtbase5-dev libqt5opengl5-dev libcgal-dev libceres-dev curl ffmpeg pkg-config python3 python3-dev rsync software-properties-common unzip libopencv-dev imagemagick
- git clone https://github.com/colmap/colmap.git
- cd colmap
- git checkout tags/3.11.0
- mkdir build
- cd build
- cmake .. -GNinja
- ninja
- sudo ninja install