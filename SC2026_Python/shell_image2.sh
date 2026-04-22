SET1=$(seq 10 5 150)
SET2=$(seq 0.4 0.2 1.0)
for i in $SET1
do
    for j in $SET2
    do
        #docker run --gpus all -it --rm -v ../Data2/Sample:/etri_workspace/Data -v ../Data2/Output:/etri_workspace/Output etri_scapi:0.1.2 python run_render.py --view_range 0.2 --focal $i --num_views 49 --result Result-$i-0.4
        docker run --gpus all -it --rm -v ../Data2/Sample:/etri_workspace/Data -v ../Data2/Output:/etri_workspace/Output etri_scapi:0.1.4 python run_render_quilt.py --view_range $j --focal $i --rows 7 --cols 7
    done
done