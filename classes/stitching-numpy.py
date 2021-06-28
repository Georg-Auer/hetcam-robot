# https://www.programmersought.com/article/76474360721/
import glob
import numpy as np
from cv2 import imread,imwrite, imshow, waitKey			#cv2 from OpenCV-Python extension library
# import cv2

imgs,heights,widths = [],[],[]
for f in glob.glob("*.jpg"):
    img = imread(f,-1)
    print("original:",img.shape)
    h,w = img.shape[:2]
    heights.append(h)
    widths.append(w)
    imgs.append(img)

print(imgs)
# imshow("test img2", imgs)
# waitKey(0) 