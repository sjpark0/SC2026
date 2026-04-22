
SET=$(seq 0 3)
#for i in $SET
#do
#    docker run --gpus all -it --rm -v ~/SC2025/VideoData/VideoSample:/etri_workspace/Data -v ~/SC2025/VideoData/Input:/etri_workspace/Input etri_scapi:0.1.0 python run_init_video.py --frame_number $i
#done

#docker run --gpus all -it --rm -v ~/SC2025/VideoData/VideoSample:/etri_workspace/Data etri_scapi:0.1.0 python run_build_param_video.py --frame_number 0

for i in $SET
do
#    docker run --gpus all -it --rm -v ~/SC2025/VideoData/VideoSample:/etri_workspace/Data etri_scapi:0.1.0 python run_build_layer_video.py --factor 4 --frame_number $i
    docker run --gpus all -it --rm -v ~/SC2025/VideoData/VideoSample:/etri_workspace/Data -v ~/SC2025/VideoData/Output:/etri_workspace/Output etri_scapi:0.1.4 python run_render_quilt_video.py --view_range 1.0 --focal 50 --rows 7 --cols 7 --frame_number $i
done
