# Define Base Image
FROM nvcr.io/nvidia/tensorflow:23.03-tf1-py3
# Install dependencies


RUN apt-get update && apt-get install -y git cmake build-essential ninja-build libboost-program-options-dev libboost-graph-dev libboost-system-dev libeigen3-dev libflann-dev libfreeimage-dev libmetis-dev libgoogle-glog-dev libgtest-dev libgmock-dev libsqlite3-dev libglew-dev qtbase5-dev libqt5opengl5-dev libcgal-dev libceres-dev curl ffmpeg pkg-config python3 python3-dev rsync software-properties-common unzip libopencv-dev imagemagick

WORKDIR /opt
RUN git clone https://github.com/colmap/colmap.git
WORKDIR /opt/colmap
RUN git checkout tags/3.11.0
WORKDIR /opt/colmap/build
RUN cmake .. -GNinja
RUN ninja
RUN ninja install

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip

RUN pip3 --no-cache-dir install --upgrade ipython imageio-ffmpeg ipykernel jupyter jupyterlab matplotlib numpy==1.23.4 scipy scikit-learn Pillow scikit-image imageio==2.20.0 opencv-python pyinstaller


ENV LD_LIBRARY_PATH /usr/local/cuda/extras/CUPTI/lib64:$LD_LIBRARY_PATH
ENV DEBIAN_FRONTEND=noninteractive 
RUN echo 'ln /dev/null /dev/raw1394' >> ~/.bashrc
