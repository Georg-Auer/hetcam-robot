import os
import cv2
from base_camera import BaseCamera


class Camera(BaseCamera):
    video_source = 0

    def __init__(self):
        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        super(Camera, self).__init__()

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    # @staticmethod
    # def set_video_low_resolution():
    #     # Camera.video_resolution = resolution
    #     camera = cv2.VideoCapture(Camera.video_source)
    #     camera.set(3, 640)
    #     camera.set(4, 480)

    # # new method for setting resolution
    # @staticmethod
    # def set_video_720p_resolution():
    #     camera = cv2.VideoCapture(Camera.video_source)
    #     camera.set(3, 1280)
    #     camera.set(4, 720)
    # [1280, 720]

    @staticmethod
    def frames(resolution = [640, 480]):
        print(f"camera_opencv resolution: {resolution}")
        camera = cv2.VideoCapture(Camera.video_source)

        # https://www.codingforentrepreneurs.com/blog/open-cv-python-change-video-resolution-or-scale
        camera.set(3, resolution[0])
        camera.set(4, resolution[1])

        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()

