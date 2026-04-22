import SCAPI
import cv2
import os
import sys
#sys.path.append('../LLFF')
#from make_layer import make_layer1


inputFolder = "../Data/Sample3"
outputFolder = "../Data/RenderingResult5"

#make_layer1(inputFolder, 4)

if not os.path.exists(outputFolder):
    os.makedirs(outputFolder)

api = SCAPI.SCAPI()
api.SetInputFolder(inputFolder)
res = api.FullRendering(1.0, 10.0, 100)
for i in range(api.numView):    
    cv2.imwrite(os.path.join(outputFolder, "%03d.png" % i), res[i,...])
api.Finalize()
