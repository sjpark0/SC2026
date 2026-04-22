import os
import ctypes
import sys
from misc import *
import numpy as np
import cv2
import subprocess

class SCAPI:
    def __init__(self):
        if sys.platform == "win32":
            dll = ctypes.cdll.LoadLibrary("..\\bin\\SCAPI.dll")
        else:
            #os.environ['LD_LIBRARY_PATH'] = "../etriSCAPI" + os.environ.get("LD_LIBRARY_PATH", "")
            #dll = ctypes.cdll.LoadLibrary("../etriSCAPI/libetriSCAPI.so")
            os.environ['LD_LIBRARY_PATH'] = "/etri_workspace" + os.environ.get("LD_LIBRARY_PATH", "")
            dll = ctypes.cdll.LoadLibrary("/etri_workspace/libetriSCAPI.so")
        
        self.SJCUDARenderer_New = dll.SJCUDARenderer_New
        self.SJCUDARenderer_New.restype = ctypes.c_void_p
        self.SJCUDARenderer_New.argtypes = []

        self.SJCUDARenderer_Initialize = dll.SJCUDARenderer_Initialize
        self.SJCUDARenderer_Initialize.restype = ctypes.c_int
        self.SJCUDARenderer_Initialize.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]

        self.SJCUDARenderer_LoadMPI = dll.SJCUDARenderer_LoadMPI
        self.SJCUDARenderer_LoadMPI.restype = ctypes.c_int
        self.SJCUDARenderer_LoadMPI.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte)]

        self.SJCUDARenderer_InitializeRendering = dll.SJCUDARenderer_InitializeRendering
        self.SJCUDARenderer_InitializeRendering.restype = ctypes.c_int
        self.SJCUDARenderer_InitializeRendering.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_int]

        self.SJCUDARenderer_Rendering = dll.SJCUDARenderer_Rendering
        self.SJCUDARenderer_Rendering.restype = ctypes.c_int
        self.SJCUDARenderer_Rendering.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte)]

        self.SJCUDARenderer_Finalize = dll.SJCUDARenderer_Finalize
        self.SJCUDARenderer_Finalize.restype = ctypes.c_int
        self.SJCUDARenderer_Finalize.argtypes = [ctypes.c_void_p]

        self.SJCUDARenderer_CUDA_UCHAR_Alloc = dll.SJCUDARenderer_CUDA_UCHAR_Alloc
        self.SJCUDARenderer_CUDA_UCHAR_Alloc.restype = ctypes.POINTER(ctypes.c_ubyte)
        self.SJCUDARenderer_CUDA_UCHAR_Alloc.argtypes = [ctypes.c_size_t]

        self.SJCUDARenderer_CPU_UCHAR_Alloc = dll.SJCUDARenderer_CPU_UCHAR_Alloc
        self.SJCUDARenderer_CPU_UCHAR_Alloc.restype = ctypes.POINTER(ctypes.c_ubyte)
        self.SJCUDARenderer_CPU_UCHAR_Alloc.argtypes = [ctypes.c_size_t]

        self.SJCUDARenderer_CUDA_FLOAT_Alloc = dll.SJCUDARenderer_CUDA_FLOAT_Alloc
        self.SJCUDARenderer_CUDA_FLOAT_Alloc.restype = ctypes.POINTER(ctypes.c_float)
        self.SJCUDARenderer_CUDA_FLOAT_Alloc.argtypes = [ctypes.c_size_t]

        self.SJCUDARenderer_CPU_FLOAT_Alloc = dll.SJCUDARenderer_CPU_FLOAT_Alloc
        self.SJCUDARenderer_CPU_FLOAT_Alloc.restype = ctypes.POINTER(ctypes.c_float)
        self.SJCUDARenderer_CPU_FLOAT_Alloc.argtypes = [ctypes.c_size_t]

        self.SJCUDARenderer_CUDA_UCHAR_Free = dll.SJCUDARenderer_CUDA_UCHAR_Free
        self.SJCUDARenderer_CUDA_UCHAR_Free.restype = None
        self.SJCUDARenderer_CUDA_UCHAR_Free.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]

        self.SJCUDARenderer_CPU_UCHAR_Free = dll.SJCUDARenderer_CPU_UCHAR_Free
        self.SJCUDARenderer_CPU_UCHAR_Free.restype = None
        self.SJCUDARenderer_CPU_UCHAR_Free.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]

        self.SJCUDARenderer_CUDA_FLOAT_Free = dll.SJCUDARenderer_CUDA_FLOAT_Free
        self.SJCUDARenderer_CUDA_FLOAT_Free.restype = None
        self.SJCUDARenderer_CUDA_FLOAT_Free.argtypes = [ctypes.POINTER(ctypes.c_float)]

        self.SJCUDARenderer_CPU_FLOAT_Free = dll.SJCUDARenderer_CPU_FLOAT_Free
        self.SJCUDARenderer_CPU_FLOAT_Free.restype = None
        self.SJCUDARenderer_CPU_FLOAT_Free.argtypes = [ctypes.POINTER(ctypes.c_float)]

        self.SJCUDARenderer_LoadMPIFromFolder = dll.SJCUDARenderer_LoadMPIFromFolder
        self.SJCUDARenderer_LoadMPIFromFolder.restype = ctypes.c_int
        self.SJCUDARenderer_LoadMPIFromFolder.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_ubyte)]

        self.SJCUDARenderer_LoadDataFromFolder = dll.SJCUDARenderer_LoadDataFromFolder
        self.SJCUDARenderer_LoadDataFromFolder.restype = ctypes.c_int
        self.SJCUDARenderer_LoadDataFromFolder.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]

        self.SJCUDARenderer_GetRenderPath = dll.SJCUDARenderer_GetRenderPath
        self.SJCUDARenderer_GetRenderPath.restype = ctypes.POINTER(ctypes.c_float)
        self.SJCUDARenderer_GetRenderPath.argtypes = [ctypes.c_char_p]

    def SetInputFolder(self, param_dir, mpi_dir):        
        filename = os.path.join(os.path.join(mpi_dir, "mpis_360"), "metadata.txt")
        lines = open(filename, 'r').read().split('\n')
        num, w, h, d = [int(x) for x in lines[0].split(' ')]
        
        self.pDim = (ctypes.c_size_t * 4)(1, num, h, w)
        self.pMPIDim = (ctypes.c_size_t * 5)(1, num, h, w, d)
        
        self.outWidth = self.pDim[3]
        self.outHeight = self.pDim[2]
        
        filename = os.path.join(mpi_dir, "mpis_360").encode("utf-8")
        self.pC2WCPU = self.SJCUDARenderer_CPU_FLOAT_Alloc(self.pDim[0] * self.pDim[1] * 16)
        self.pW2CCPU = self.SJCUDARenderer_CPU_FLOAT_Alloc(self.pDim[0] * self.pDim[1] * 16)
        self.pCIFCPU = self.SJCUDARenderer_CPU_FLOAT_Alloc(self.pDim[0] * self.pDim[1] * 3)
        self.pC2WCUDA = self.SJCUDARenderer_CUDA_FLOAT_Alloc(self.pDim[0] * self.pDim[1] * 16)
        self.pW2CCUDA = self.SJCUDARenderer_CUDA_FLOAT_Alloc(self.pDim[0] * self.pDim[1] * 16)
        self.pCIFCUDA = self.SJCUDARenderer_CUDA_FLOAT_Alloc(self.pDim[0] * self.pDim[1] * 3)
        
        self.SJCUDARenderer_LoadDataFromFolder(filename, self.pMPIDim, self.pC2WCPU, self.pC2WCUDA, self.pW2CCPU, self.pW2CCUDA, self.pCIFCPU, self.pCIFCUDA)

        self.pMPICUDA = self.SJCUDARenderer_CUDA_UCHAR_Alloc(self.pMPIDim[0] * self.pMPIDim[1] * self.pMPIDim[2] * self.pMPIDim[3] * self.pMPIDim[4] * 4)
        self.SJCUDARenderer_LoadMPIFromFolder(filename, self.pMPIDim, self.pMPICUDA)

        self.pImageCUDA = self.SJCUDARenderer_CUDA_UCHAR_Alloc(self.outWidth * self.outHeight * 3)
        self.pImage = self.SJCUDARenderer_CPU_UCHAR_Alloc(self.outWidth * self.outHeight * 3)

        self.renderer = self.SJCUDARenderer_New()
        self.SJCUDARenderer_Initialize(self.renderer, self.pDim, self.pMPIDim, self.pC2WCPU, self.pC2WCUDA, self.pW2CCPU, self.pW2CCUDA, self.pCIFCPU, self.pCIFCUDA)
        self.SJCUDARenderer_InitializeRendering(self.renderer, self.outWidth, self.outHeight, 5)
        self.SJCUDARenderer_LoadMPI(self.renderer, None, self.pMPICUDA)        
        
        self.poses, pts3d, perm, w2c, c2w, hwf = load_colmap_data(param_dir)
        cdepth, idepth = computecloseInfinity(self.poses, pts3d, perm)
        self.close_depth = np.min(cdepth) * 0.9
        self.inf_depth = np.max(idepth) * 2.0
        return 0
    
    def GetRenderPathFromFile(self, path, path_filename):
        filename = os.path.join(path, path_filename)
        lines = open(filename, 'r').read().split('\n')
        self.numView = int(lines[0])
        filename = os.path.join(path, path_filename).encode('utf-8')
        self.pViewArr = self.SJCUDARenderer_GetRenderPath(filename)
    
    def GetRenderPath(self, view_range, focal, N):
        #render_poses = generate_render_path_param1(self.poses, self.close_depth, self.inf_depth, view_range, focal, comps=[True, False, False], N=N)
        render_poses = generate_render_path_param_cam(self.poses, self.close_depth, self.inf_depth, view_range, focal, comps=[True, False, False], N=N)
        render_poses = np.concatenate([render_poses[...,1:2], -render_poses[...,0:1], render_poses[...,2:]], -1)
        render_poses = np.transpose(render_poses, (0, 2, 1))
        render_poses = render_poses[:,0:4,:]
        self.render_poses = render_poses            
        
        bottom_column = np.tile(np.array([0, 0, 0, 1]).reshape(1, 4, 1), (N, 1, 1))
        render_poses = np.concatenate([render_poses, bottom_column], axis=2)
                
        self.numView = render_poses.shape[0]
        render_poses = render_poses.reshape(-1).astype(np.float32)
        
        self.pViewArr = render_poses.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    
    def Rendering(self, id):
        offset_ptr = ctypes.cast(ctypes.addressof(self.pViewArr.contents) + 16 * id * ctypes.sizeof(ctypes.c_float), ctypes.POINTER(ctypes.c_float))
        self.SJCUDARenderer_Rendering(self.renderer, offset_ptr, self.pImageCUDA, self.pImage)
        return np.ctypeslib.as_array(self.pImage, (self.outHeight, self.outWidth, 3))

    def FullRendering(self, view_range, focal, N):
        self.GetRenderPath(view_range, focal, N)
        images = []
        for i in range(self.numView):
            image = self.Rendering(i)
            images.append(image.copy())
        return np.array(images)
    
    def MakeQuiltImage(self, view_range, focal, rows, cols):
        images = self.FullRendering(view_range, focal, rows * cols)
        
        quilt = np.zeros((images.shape[1] * rows, images.shape[2] * cols, images.shape[3]))
        for i in range(rows * cols):
            x = int(i % cols)
            y = int(i / cols)
            
            quilt[(rows - y - 1) * images.shape[1]:(rows - y) * images.shape[1], x * images.shape[2]:(x+1) * images.shape[2], :] = images[i,...]
        return quilt
        
    def Finalize(self):
        self.SJCUDARenderer_CPU_FLOAT_Free(self.pC2WCPU)
        self.SJCUDARenderer_CPU_FLOAT_Free(self.pW2CCPU)
        self.SJCUDARenderer_CPU_FLOAT_Free(self.pCIFCPU)
        self.SJCUDARenderer_CUDA_FLOAT_Free(self.pC2WCUDA)
        self.SJCUDARenderer_CUDA_FLOAT_Free(self.pW2CCUDA)
        self.SJCUDARenderer_CUDA_FLOAT_Free(self.pCIFCUDA)
        self.SJCUDARenderer_CUDA_UCHAR_Free(self.pMPICUDA)
        self.SJCUDARenderer_CPU_UCHAR_Free(self.pImage)
        self.SJCUDARenderer_CUDA_UCHAR_Free(self.pImageCUDA)
        self.SJCUDARenderer_Finalize(self.renderer)

    

