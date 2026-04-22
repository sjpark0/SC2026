import os
import ctypes
import sys
import numpy as np
import subprocess

class SCDecoder:
    def __init__(self):
        if sys.platform == "win32":
            dll = ctypes.cdll.LoadLibrary("..\\bin\\scdecoder.dll")
        else:
            #os.environ['LD_LIBRARY_PATH'] = "./" + os.environ.get("LD_LIBRARY_PATH", "")
            #dll = ctypes.cdll.LoadLibrary("./libscdecoder.so")
            os.environ['LD_LIBRARY_PATH'] = "/etri_workspace" + os.environ.get("LD_LIBRARY_PATH", "")
            dll = ctypes.cdll.LoadLibrary("/etri_workspace/libscdecoder.so")
        
        self.DecoderManager_New = dll.DecoderManager_New
        self.DecoderManager_New.restype = ctypes.c_void_p
        self.DecoderManager_New.argtypes = []

        self.DecoderManager_Prepare = dll.DecoderManager_Prepare
        self.DecoderManager_Prepare.restype = ctypes.c_int
        self.DecoderManager_Prepare.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_char_p), ctypes.c_char_p]
        
        self.DecoderManager_Initialize = dll.DecoderManager_Initialize
        self.DecoderManager_Initialize.restype = ctypes.c_int
        self.DecoderManager_Initialize.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_char_p), ctypes.c_char_p]
        
        self.DecoderManager_Initialize_Range = dll.DecoderManager_Initialize_Range
        self.DecoderManager_Initialize_Range.restype = ctypes.c_int
        self.DecoderManager_Initialize_Range.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_char_p), ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
                
        self.DecoderManager_DoDecoding = dll.DecoderManager_DoDecoding
        self.DecoderManager_DoDecoding.restype = ctypes.c_int
        self.DecoderManager_DoDecoding.argtypes = [ctypes.c_void_p]

        self.DecoderManager_Finalize = dll.DecoderManager_Finalize
        self.DecoderManager_Finalize.restype = ctypes.c_int
        self.DecoderManager_Finalize.argtypes = [ctypes.c_void_p]

        self.DecoderManager_GetNumFrame = dll.DecoderManager_GetNumFrame
        self.DecoderManager_GetNumFrame.restype = ctypes.c_int64
        self.DecoderManager_GetNumFrame.argtypes = [ctypes.c_void_p]

        self.DecoderManager_GetFrameRate = dll.DecoderManager_GetFrameRate
        self.DecoderManager_GetFrameRate.restype = ctypes.c_float
        self.DecoderManager_GetFrameRate.argtypes = [ctypes.c_void_p]

        self.DecoderManager_GetWidth = dll.DecoderManager_GetWidth
        self.DecoderManager_GetWidth.restype = ctypes.c_int
        self.DecoderManager_GetWidth.argtypes = [ctypes.c_void_p]

        self.DecoderManager_GetHeight = dll.DecoderManager_GetHeight
        self.DecoderManager_GetHeight.restype = ctypes.c_int
        self.DecoderManager_GetHeight.argtypes = [ctypes.c_void_p]

        self.DecoderManager_GetStartFrame = dll.DecoderManager_GetStartFrame
        self.DecoderManager_GetStartFrame.restype = ctypes.c_int
        self.DecoderManager_GetStartFrame.argtypes = [ctypes.c_void_p]

        self.DecoderManager_GetEndFrame = dll.DecoderManager_GetEndFrame
        self.DecoderManager_GetEndFrame.restype = ctypes.c_int
        self.DecoderManager_GetEndFrame.argtypes = [ctypes.c_void_p]
        
    def Prepare(self, input_dir, output_dir):
        self.manager = self.DecoderManager_New()
        dir_list = os.listdir(input_dir)        
        numDecoder = len(dir_list)

        foldername = output_dir.encode('utf-8')
        filenames = [os.path.join(input_dir, d).encode('utf-8') for d in dir_list]
        filenames_arr = (ctypes.c_char_p * len(filenames))(*filenames)
        
        self.DecoderManager_Prepare(self.manager, numDecoder, filenames_arr, foldername)
        return numDecoder
    
    def Initialize(self, input_dir, output_dir, start = None, end = None):
        self.manager = self.DecoderManager_New()
        dir_list = os.listdir(input_dir)        
        numDecoder = len(dir_list)

        foldername = output_dir.encode('utf-8')
        filenames = [os.path.join(input_dir, d).encode('utf-8') for d in dir_list]
        filenames_arr = (ctypes.c_char_p * len(filenames))(*filenames)
        if start is not None and end is not None:
            self.DecoderManager_Initialize_Range(self.manager, numDecoder, filenames_arr, foldername, start, end)
        else:
            self.DecoderManager_Initialize(self.manager, numDecoder, filenames_arr, foldername)
        return numDecoder
    
    def GetFrameNumber(self):
        return self.DecoderManager_GetNumFrame(self.manager)

    def GetFrameRate(self):
        return self.DecoderManager_GetFrameRate(self.manager)
    
    def GetWidth(self):
        return self.DecoderManager_GetWidth(self.manager)
    
    def GetHeight(self):
        return self.DecoderManager_GetHeight(self.manager)
    def GetStartFrame(self):
        return self.DecoderManager_GetStartFrame(self.manager)
    def GetEndFrame(self):
        return self.DecoderManager_GetEndFrame(self.manager)
    def DoDecoding(self):
        self.DecoderManager_DoDecoding(self.manager)
    
    def Finalize(self):
        self.DecoderManager_Finalize(self.manager)
