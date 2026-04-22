docker run --gpus all -it --rm -v /:/host -v ../DS_100005/Input:/etri_workspace/Input -v ../DS_100005/data:/etri_workspace/Data -v ../DS_100005/Output:/etri_workspace/Output etri_scapi:0.1.3
#docker run --gpus all -it --rm -v /:/host -v ../VideoData2/Input:/etri_workspace/Input -v ../VideoData2/VideoSample:/etri_workspace/Data -v ../VideoData2/Output:/etri_workspace/Output etri_scapi:0.1.3
