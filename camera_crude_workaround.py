# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 09:49:03 2019

@author: Georg
"""
# To use the following functions, you have to import:
import cv2
import numpy as np
import time
import datetime
# import os
# if foler manangment is needed, use: "from pathlib import Path"

# It is advised to set a working directory, like this:
#os.chdir(r'C:\SPOC\DOC\Calibration\images')

#for raspicam
def take_raspicampic(i):
    try:
        camera.close()
        print("camera closed")
    except:
        print("camera was not open")

    try:
        from picamera import PiCamera
        from picamera.array import PiRGBArray
        camera = PiCamera()
    except:
        print("camera was not closed last time or is still in use")
        #camera.close()
        #rawCapture.close()
    print("Raspberry camera")
    # import the necessary packages
    #camera = PiCamera()
    print("Raspberry Camera loaded")
    # following camera settings are not needed
    #x_res = 640
    #y_res = 480
    x_res = 320
    y_res = 240
    #x_res = y_res = 64
    camera.resolution = (x_res, y_res)
    camera.framerate = 32
    camera.exposure_mode = 'sports'
    # if the iso is set, pictures will look more similar
    camera.iso = 100
    camera.shutter_speed = 1
    #camera.vflip = True
    # alternative rawCapture = PiRGBArray(camera)
    rawCapture = PiRGBArray(camera, size=(x_res, y_res))
    # allow the camera to warmup
    time.sleep(0.1)

    camera.capture(rawCapture, format="bgr")

    image = rawCapture.array
    camera.close()
    rawCapture.close() #is this even possible?
    # display the image on screen and wait for a keypress
    #cv2.imshow("Image", image)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    filename = f"position_{i}_{timestr}.jpg"
    cv2.imwrite(filename, image)
    # if the camera is not closed, it cannot be opened again...
    # a future version might not open / close for every picture
    return filename

#take_raspicampic()

#for testing:
def take_webcampic(i):
    print("Webcam module")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) #0 is the standard number of the connected camera in windows
    #img_name = 'opencv.png'
    time.sleep(0.1)
    # Capture frame-by-frame
    ret, frame = cap.read()
    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Display the resulting frame
    #cv2.imshow('frame',gray)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    filename = f"position_{i}_{timestr}.jpg"
    cv2.imwrite(filename, gray)
    # When everything done, release the capture
    cap.release()
    #cv2.destroyAllWindows()
    return filename

def take_ids_cam_pic(i):
    # pip install pyueye
    # pip install simple-pyueye
    # take picture with pyueye!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # not implemented!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    from simple_pyueye import CameraObj as Camera

    timestr = time.strftime("%Y%m%d-%H%M%S")
    filename = f"position_{i}_{timestr}.jpg"

    # camera.capture_still(save=True,filename='img.png') # original line from https://pypi.org/project/simple-pyueye/
    camera=Camera(CamID)
    camera.open()
    camera.capture_still(save=True,filename=filename)
    camera.close()

    # image = rawCapture.array
    # # display the image on screen and wait for a keypress
    # #cv2.imshow("Image", image)
    # timestr = time.strftime("%Y%m%d-%H%M%S")
    # filename = ("position_%s_%s.jpg" % (i, timestr))
    # cv2.imwrite(filename, gray)

    return filename

if __name__ == '__main__':
    print("This module has various camera functions for import.")
    print("For now, picamera, webcam and PyCapture2 can be loaded.")
    import time
    import cv2
    from picamera import PiCamera
    from picamera.array import PiRGBArray
    # os.chdir(r'C:\Users\Georg\Documents\Python Scripts\delta_bot\dustbin')
    iterations = 10
    try:
        i = 0
        while(i <= iterations):
            print(i)
            take_raspicampic(i)
            i += 1
    except:
        take_webcampic(1)

else:
    print("Camera module loaded:")

# def variance_of_laplacian(image):
# 	# First compute the Laplacian of the image and then return the focus
# 	# measure, which is simply the variance of the Laplacian
#     # Suggestion: Use Gaussian Blur before Laplacien.
# 	return cv2.Laplacian(image, cv2.CV_64F).var()

# def autofocus(iterations, z):
#     # A maximum lap value is desired, a z position to that should be stored
#     # This needs to be optimized, maybe hill climbing works well here?
#     # https://www.geeksforgeeks.org/introduction-hill-climbing-artificial-intelligence/
    
#     lap0 = 10 # Just a starting value
#     lap1 = 20000 # Another(!) starting value
#     direction = 1 # This value is given to movement(direction), 0 = down, 1 = up
#     number = 0 # The picture number, this increases each time a new picture is taken   
#     filename = take_webcampic(number) #gives the number to take to takepic, gets filename back
    
#     # This is converting the pic to grey for  analysis
#     image = cv2.imread(filename) # Add ",0" to load pic in gray, if the picture is colored
#     #gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # Alternatively, convert to grey
#     lap0 = variance_of_laplacian(image) # This gives back a value that lies mostly between 0 and 10000
    
#     while(number <= iterations):  # A recursive "solution" to find a high laplacien value
#         #filename = takepic(number) #for debug, take pic from webcam
#         filename = take_webcampic(number) #take a picture, store the filename
#         image = cv2.imread(filename) #,0 to load pic in gray, if neccessary
#         #gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#         lap1 = variance_of_laplacian(image)

#         # This writes the calculated Laplacien on the loaded image
#         text = "Laplacian"
#         cv2.putText(image, "{}: {:.2f}".format(text, lap1), (10, 30),
#             cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
#         cv2.imwrite(filename, image)

#         number += 1
#         print(lap0)
#         print(lap1)
#         if lap0 >= lap1:
#             direction^=True #if lap0 is bigger than lap1, change direction
#             print("toggle")
#         #movement(direction) 
#         if direction:
#             z -= 1000
#         else:
#             z += 1000
#         lap0 = lap1
#     return z

# def take_webcampic_old():
#     cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) #0 is the standard number of the connected camera in windows
#     img_name = 'opencv.png'
#     time.sleep(0.1)
#     while(True):
#         # Capture frame-by-frame
#         ret, frame = cap.read()

#         # Our operations on the frame come here
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#         # Display the resulting frame
#         cv2.imshow('frame',gray)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             cv2.imwrite(img_name, gray)
#             break
    
    
#     # When everything done, release the capture
#     cap.release()
#     cv2.destroyAllWindows()


