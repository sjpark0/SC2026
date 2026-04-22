
docker run --gpus all -it --rm -v ../VideoData2/VideoSample:/etri_workspace/Data -v ../VideoData2/Input:/etri_workspace/Input -v ../VideoData2/Output:/etri_workspace/Output etri_scapi:0.1.4 python run_init.py
docker run --gpus all -it --rm -v ../VideoData2/VideoSample:/etri_workspace/Data -v ../VideoData2/Output:/etri_workspace/Output etri_scapi:0.1.4 python run_extract_frames.py --start 50 --end 70
docker run --gpus all -it --rm -v ../VideoData2/VideoSample:/etri_workspace/Data etri_scapi:0.1.4 python run_build_param.py --frame_number 50
SET=$(seq 50 52)
for i in $SET
do
    docker run --gpus all -it --rm -v ../VideoData2/VideoSample:/etri_workspace/Data etri_scapi:0.1.4 python run_build_layer.py --factor 4 --frame_number $i
done

docker run --gpus all -it --rm -v ../VideoData2/VideoSample:/etri_workspace/Data -v ../VideoData2/Output:/etri_workspace/Output etri_scapi:0.1.4 python run_render.py --view_range 1.0 --focal 50 --num_views 49 --frame_number 50 --save_viewing
docker run --gpus all -it --rm -v ../VideoData2/VideoSample:/etri_workspace/Data -v ../VideoData2/Output:/etri_workspace/Output etri_scapi:0.1.4 python run_render_quilt.py --view_range 1.0 --focal 50 --rows 7 --cols 7 --frame_number 50
