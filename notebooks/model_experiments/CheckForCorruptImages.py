from os import listdir
import cv2

directory = 'data/test/wildfire/'
#for filename in listdir('C:/tensorflow/models/research/object_detection/images/train'):
for filename in listdir(directory):
  if filename.endswith(".jpg"):
    print(directory+filename)
    #cv2.imread('C:/tensorflow/models/research/object_detection/images/train/'+filename)
    cv2.imread(directory+filename)