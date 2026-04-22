from llff.inference.mpi_utils import run_inference
from llff.poses.pose_utils import load_colmap_data, save_poses
from llff.poses.pose_utils import load_data
from llff.inference.mpi_tester import DeepIBR
import os
import imageio
import numpy as np

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('scenedir', type=str, help='input scene directory')
parser.add_argument('imagedir', type=str, help='input image directory')
parser.add_argument('mpidir', type=str, help='output mpi directory')
parser.add_argument('factor', type=int, help = 'factor')

args = parser.parse_args()

def gen_mpis(basedir, imagedir, savedir, factor, logdir, num_planes):
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    
    # load up images, poses, w/ scale factor
    poses, bds, imgfiles = load_data(basedir, imagedir, factor) # 220628 deleted
    print("load data finished")
    # load up model
    ibr_runner = DeepIBR()
    ibr_runner.load_graph(logdir)
    
    
    #patched = imgs.shape[0] * imgs.shape[1] * num_planes > 640*480*32
    
    N = len(imgfiles)
    close_depths = [bds.min()*.9] * N
    inf_depths = [bds.max()*2.] * N
    mpi_bds = np.array([close_depths, inf_depths])
    
    for i in range(N):
         run_inference(imgfiles, i, poses, mpi_bds, ibr_runner, num_planes, savedir)
    
    imgs = imageio.imread(imgfiles[0])
    
    with open(os.path.join(savedir, 'metadata.txt'), 'w') as file:
        file.write('{} {} {} {}\n'.format(N, imgs.shape[1], imgs.shape[0], num_planes))
    
    print( 'Saved to', savedir )
    return True

if __name__=='__main__':
    checkpoint = '/etri_workspace/checkpoints/papermodel/checkpoint'
    numplanes = 32
    
    #gen_poses(args.scenedir)           
    mpidir = os.path.join(args.mpidir, 'mpis_360')
    poses, pts3d, perm = load_colmap_data(args.scenedir)    
    save_poses(args.scenedir, poses, pts3d, perm) 
    
    gen_mpis(args.scenedir, args.imagedir, mpidir, args.factor, checkpoint, numplanes)
