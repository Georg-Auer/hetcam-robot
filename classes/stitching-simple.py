import cv2

import glob, os
# https://stackoverflow.com/questions/52220609/stitcher-api-seems-to-be-missing-from-my-python-opencv-bindings
images = []
for file in glob.glob("*.jpg"):
    images.append(cv2.imread(file))

print(len(images))

#################################
stitcher = cv2.Stitcher.create()
#################################
cv2.imshow("test img1", images[1])
cv2.imshow("test img2", images[2])
cv2.waitKey(0) 

status, pano = stitcher.stitch([images[2],images[3]])
# status, pano = stitcher.stitch([images[3],images[4]])
# status, pano = stitcher.stitch(images)
# status, pano = stitcher.stitch([pano,images[6]])
# status, pano = stitcher.stitch([pano,images[4]])
print("output:")
print(status)
print(pano)
print("Stitcher exit status = " + str(status))
cv2.imshow('Stitched Image', pano)
cv2.imwrite("stitched.png", pano)