import ctypes
from misc import *
import numpy as np
import sys
import cv2
import os
os.environ['LD_LIBRARY_PATH'] = "../etriSCAPI" + os.environ.get("LD_LIBRARY_PATH", "")

dll = ctypes.cdll.LoadLibrary("../etriSCAPI/libetriSCAPI.so")
SJCUDARenderer_New = dll.SJCUDARenderer_New
SJCUDARenderer_Initialize = dll.SJCUDARenderer_Initialize
SJCUDARenderer_LoadMPI = dll.SJCUDARenderer_LoadMPI
SJCUDARenderer_InitializeRendering = dll.SJCUDARenderer_InitializeRendering
SJCUDARenderer_Rendering = dll.SJCUDARenderer_Rendering
SJCUDARenderer_Finalize = dll.SJCUDARenderer_Finalize

SJCUDARenderer_CUDA_UCHAR_Alloc = dll.SJCUDARenderer_CUDA_UCHAR_Alloc
SJCUDARenderer_CPU_UCHAR_Alloc = dll.SJCUDARenderer_CPU_UCHAR_Alloc
SJCUDARenderer_CUDA_FLOAT_Alloc = dll.SJCUDARenderer_CUDA_FLOAT_Alloc
SJCUDARenderer_CPU_FLOAT_Alloc = dll.SJCUDARenderer_CPU_FLOAT_Alloc
SJCUDARenderer_CUDA_UCHAR_Free = dll.SJCUDARenderer_CUDA_UCHAR_Free
SJCUDARenderer_CPU_UCHAR_Free = dll.SJCUDARenderer_CPU_UCHAR_Free
SJCUDARenderer_CUDA_FLOAT_Free = dll.SJCUDARenderer_CUDA_FLOAT_Free
SJCUDARenderer_CPU_FLOAT_Free = dll.SJCUDARenderer_CPU_FLOAT_Free

SJCUDARenderer_LoadMPIFromFolder = dll.SJCUDARenderer_LoadMPIFromFolder
SJCUDARenderer_LoadDataFromFolder = dll.SJCUDARenderer_LoadDataFromFolder
SJCUDARenderer_GetRenderPath = dll.SJCUDARenderer_GetRenderPath


SJCUDARenderer_New.restype = ctypes.c_void_p
SJCUDARenderer_New.argtypes = []

SJCUDARenderer_Initialize.restype = ctypes.c_int
SJCUDARenderer_Initialize.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]

SJCUDARenderer_LoadMPI.restype = ctypes.c_int
SJCUDARenderer_LoadMPI.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte)]

SJCUDARenderer_InitializeRendering.restype = ctypes.c_int
SJCUDARenderer_InitializeRendering.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_int]

SJCUDARenderer_Rendering.restype = ctypes.c_int
SJCUDARenderer_Rendering.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte)]

SJCUDARenderer_Finalize.restype = ctypes.c_int
SJCUDARenderer_Finalize.argtypes = [ctypes.c_void_p]

SJCUDARenderer_CUDA_UCHAR_Alloc.restype = ctypes.POINTER(ctypes.c_ubyte)
SJCUDARenderer_CUDA_UCHAR_Alloc.argtypes = [ctypes.c_size_t]

SJCUDARenderer_CPU_UCHAR_Alloc.restype = ctypes.POINTER(ctypes.c_ubyte)
SJCUDARenderer_CPU_UCHAR_Alloc.argtypes = [ctypes.c_size_t]

SJCUDARenderer_CUDA_FLOAT_Alloc.restype = ctypes.POINTER(ctypes.c_float)
SJCUDARenderer_CUDA_FLOAT_Alloc.argtypes = [ctypes.c_size_t]

SJCUDARenderer_CPU_FLOAT_Alloc.restype = ctypes.POINTER(ctypes.c_float)
SJCUDARenderer_CPU_FLOAT_Alloc.argtypes = [ctypes.c_size_t]

SJCUDARenderer_CUDA_UCHAR_Free.restype = None
SJCUDARenderer_CUDA_UCHAR_Free.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]

SJCUDARenderer_CPU_UCHAR_Free.restype = None
SJCUDARenderer_CPU_UCHAR_Free.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]

SJCUDARenderer_CUDA_FLOAT_Free.restype = None
SJCUDARenderer_CUDA_FLOAT_Free.argtypes = [ctypes.POINTER(ctypes.c_float)]

SJCUDARenderer_CPU_FLOAT_Free.restype = None
SJCUDARenderer_CPU_FLOAT_Free.argtypes = [ctypes.POINTER(ctypes.c_float)]

SJCUDARenderer_LoadMPIFromFolder.restype = ctypes.c_int
SJCUDARenderer_LoadMPIFromFolder.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_ubyte)]

SJCUDARenderer_LoadDataFromFolder.restype = ctypes.c_int
SJCUDARenderer_LoadDataFromFolder.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]

SJCUDARenderer_GetRenderPath.restype = ctypes.POINTER(ctypes.c_float)
SJCUDARenderer_GetRenderPath.argtypes = [ctypes.c_char_p]

inputFolder = "../Data/Sample1"
outputFolder = "../Data/RenderingResult3"

pDim = (ctypes.c_size_t * 4)(1, 16, 540, 960)
pMPIDim = (ctypes.c_size_t * 5)(1, 16, 540, 960, 32)

outWidth = pDim[3]
outHeight = pDim[2]

#poses_arr = np.load(os.path.join(inputFolder, 'poses_bounds.npy'))
#poses = poses_arr[:, :-2].reshape([-1, 3, 5]).transpose([1,2,0])
#bds = poses_arr[:, -2:].transpose([1,0])
#render_poses = generate_render_path_param(poses, bds, 1.0, 10.0, comps=[True, False, False], N=49)

poses, pts3d, perm, w2c, c2w, hwf = load_colmap_data(inputFolder)
cdepth, idepth = computecloseInfinity(poses, pts3d, perm)
close_depth = np.min(cdepth) * 0.9
inf_depth = np.max(idepth) * 2.0
render_poses = generate_render_path_param1(poses, close_depth, inf_depth, 1.0, 10.0, comps=[True, False, False], N=49)

render_poses = np.concatenate([render_poses[...,1:2], -render_poses[...,0:1], render_poses[...,2:]], -1)

render_poses = np.transpose(render_poses, (0, 2, 1))
render_poses = render_poses[:,0:4,:]
bottom_column = np.tile(np.array([0, 0, 0, 1]).reshape(1, 4, 1), (49, 1, 1))
render_poses = np.concatenate([render_poses, bottom_column], axis=2)

numView = render_poses.shape[0]
render_poses = render_poses.reshape(-1).astype(np.float32)
pViewArr = render_poses.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

#numView = 45
#filename = (inputFolder + "\\path.txt").encode("utf-8")
#pViewArr = SJCUDARenderer_GetRenderPath(filename)

filename = (inputFolder + "/mpis_360").encode("utf-8")
pC2WCPU = SJCUDARenderer_CPU_FLOAT_Alloc(pDim[0] * pDim[1] * 16)
pW2CCPU = SJCUDARenderer_CPU_FLOAT_Alloc(pDim[0] * pDim[1] * 16)
pCIFCPU = SJCUDARenderer_CPU_FLOAT_Alloc(pDim[0] * pDim[1] * 3)
pC2WCUDA = SJCUDARenderer_CUDA_FLOAT_Alloc(pDim[0] * pDim[1] * 16)
pW2CCUDA = SJCUDARenderer_CUDA_FLOAT_Alloc(pDim[0] * pDim[1] * 16)
pCIFCUDA = SJCUDARenderer_CUDA_FLOAT_Alloc(pDim[0] * pDim[1] * 3)

SJCUDARenderer_LoadDataFromFolder(filename, pMPIDim, pC2WCPU, pC2WCUDA, pW2CCPU, pW2CCUDA, pCIFCPU, pCIFCUDA)

pMPICUDA = SJCUDARenderer_CUDA_UCHAR_Alloc(pMPIDim[0] * pMPIDim[1] * pMPIDim[2] * pMPIDim[3] * pMPIDim[4] * 4)
SJCUDARenderer_LoadMPIFromFolder(filename, pMPIDim, pMPICUDA)

pImageCUDA = SJCUDARenderer_CUDA_UCHAR_Alloc(outWidth * outHeight * 3)
pImage = SJCUDARenderer_CPU_UCHAR_Alloc(outWidth * outHeight * 3)

renderer = SJCUDARenderer_New()
SJCUDARenderer_Initialize(renderer, pDim, pMPIDim, pC2WCPU, pC2WCUDA, pW2CCPU, pW2CCUDA, pCIFCPU, pCIFCUDA)
SJCUDARenderer_InitializeRendering(renderer, outWidth, outHeight, 5)
SJCUDARenderer_LoadMPI(renderer, None, pMPICUDA)

for i in range(numView):
    offset_ptr = ctypes.cast(ctypes.addressof(pViewArr.contents) + 16 * i * ctypes.sizeof(ctypes.c_float), ctypes.POINTER(ctypes.c_float))
    SJCUDARenderer_Rendering(renderer, offset_ptr, pImageCUDA, pImage)
    image = np.ctypeslib.as_array(pImage, (outHeight, outWidth, 3))
    cv2.imwrite(outputFolder + "/{:03d}.png".format(i), image)

#SJCUDARenderer_CPU_FLOAT_Free(pViewArr)
SJCUDARenderer_CPU_FLOAT_Free(pC2WCPU)
SJCUDARenderer_CPU_FLOAT_Free(pW2CCPU)
SJCUDARenderer_CPU_FLOAT_Free(pCIFCPU)
SJCUDARenderer_CUDA_FLOAT_Free(pC2WCUDA)
SJCUDARenderer_CUDA_FLOAT_Free(pW2CCUDA)
SJCUDARenderer_CUDA_FLOAT_Free(pCIFCUDA)
SJCUDARenderer_CUDA_UCHAR_Free(pMPICUDA)
SJCUDARenderer_CPU_UCHAR_Free(pImage)
SJCUDARenderer_CUDA_UCHAR_Free(pImageCUDA)
SJCUDARenderer_Finalize(renderer)
