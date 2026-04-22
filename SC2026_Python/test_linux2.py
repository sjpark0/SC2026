import sys
#sys.path.append('/etri_workspace')
import SCAPI
import subprocess
import cv2

layerFolder = "../Data/Layer"
imageFolder = "../Data/Sample5"
paramFolder = "../Data/Param"
api = SCAPI.SCAPI()
m = api.SetInputFolder(paramFolder, imageFolder, layerFolder, 4)
q = api.MakeQuiltImage(1.0, 50, 7, 7)
cv2.imwrite('test1.png', q)
#for i in range(49):
#    cv2.imwrite('test_{:03d}.png'.format(i), v[i,...])
#m = api.MakeLayer(inputFolder, 4)
print(m)
#api.SetInputFolder(inputFolder)
