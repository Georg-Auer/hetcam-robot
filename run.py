# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_migrate import Migrate
from os import environ
from sys import exit
from decouple import config
import logging

from config import config_dict
from app import create_app, db

#from old camera app-----------------------------------------------------------------

from importlib import import_module
import os
from flask import Flask, render_template, Response

# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

# for saving bytestream
# https://stackoverflow.com/questions/29330570/how-to-open-a-simple-image-using-streams-in-pillow-python
# https://stackoverflow.com/questions/14134892/convert-image-from-pil-to-opencv-format
from PIL import Image
from io import BytesIO

# classes experiment & position
from classes.experiments import Position, Experiment

# gallery
from flask import request, redirect, send_from_directory
from werkzeug.utils import secure_filename
# gallery end

# import old 
import time
import os
from pyserial_connection_arduino import connect_to_arduino, list_available_ports
import numpy as np
from flask_apscheduler import APScheduler
import cv2
from datetime import datetime, timedelta
# import old end
# https://stackoverflow.com/questions/6871016/adding-days-to-a-date-in-python
#-----------------------------------------------------------------------------------

# WARNING: Don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

try:
    # Load the configuration using the default values 
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app( app_config ) 
Migrate(app, db)

if DEBUG:
    app.logger.info('DEBUG       = ' + str(DEBUG)      )
    app.logger.info('Environment = ' + get_config_mode )
    app.logger.info('DBMS        = ' + app_config.SQLALCHEMY_DATABASE_URI )

# constant for saving images, used by camera and gallery
# IMAGEPATH = "app\\base\\static\\upload"
IMAGEPATH = "app/base/static/upload"

# scheduler set up:
class Config(object):
    SCHEDULER_API_ENABLED = True
app.config.from_object(Config())

scheduler = APScheduler()
# if you don't wanna use a config, you can set options here:
# scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()

# setting up variables for sending, needs to be fixed 
comport = '/dev/ttyACM0' # this should be set to the standard address of the microcontroller
motor0_enable = 0
motor0_direction = 0
motor0_position = 0
motor1_enable = 0
motor1_direction = 0
motor1_position = 0
motor2_enable = 0
motor2_direction = 0
motor2_position = 0
motor3_enable = 0
motor3_direction = 0
motor3_position = 0

INTERVAL = 1 # experiment time in minutes
EXPERIMENT_NAME = "default_experiment"
EXPERIMENT_POSITIONS = [0, 90, 180, 270]
DATABASE = []

@app.route('/')
def index():
    # images = os.listdir('./images')
    # print("List of found images in folder /images")
    # print(images)
    """Video streaming home page."""
    # return render_template('index.html', images=images)
    return render_template('index.html')

def gen(camera):
    """Video streaming generator function."""
    # global global_video_frame
    # global global_video_frame_timepoint
    while True:
        frame_enc = camera.get_frame()

        # global_video_frame = frame_enc
        # global_video_frame_timepoint = (datetime.now().strftime("%Y%m%d-%H%M%S"))
        # print(f"frame{global_video_frame_timepoint}")

        # object_methods = [method_name for method_name in dir(camera)
        #     if callable(getattr(camera, method_name))]
        # print(object_methods)

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_enc + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# buttons

@app.route('/move_deg')
def move_deg():
    degree = 0
    degree = int(request.args.get('degree'))
    if(degree >= 280):
        degree = 270
    if(degree <= -90):
        degree = -90
    print(f"Moving to {degree}°")
    recent_experiment = select_experiment()
    print(recent_experiment.name)
    recent_experiment.planned_position = degree
    recent_experiment.motor_position
    return '''<h1>Moving to: {}</h1>'''.format(degree)
    # return ("nothing")

#-------------------------------------------------------------------------------------

@app.route('/get_toggled_status') 
def toggled_status():
    current_status = request.args.get('status')
    # instead of if, create a list, send list and do for items in list
    # this way, only in activated positions are scheduled
    if(scheduler.get_jobs()):
        print(bool(scheduler.get_jobs()))
        print("jobs scheduled")
        # current_status = 'Automatic On'
    else:
        print(bool(scheduler.get_jobs()))
        print("no jobs scheduled")
    #     current_status = 'Automatic On'

    # create dummy experiment for now
    # new_experiment = Experiment(EXPERIMENT_NAME, scheduler, IMAGEPATH, Camera, [0, 90, 180, 270], INTERVAL)
    recent_experiment = select_experiment()
    # if Automatic On was sent and no jobs are scheduled
    if(current_status == 'Automatic Off') and not(scheduler.get_jobs()):
        print("Switching On")
        print(recent_experiment.experiment_positions)
        recent_experiment.show_experiment_positions()
        # start dummy experiment for now
        recent_experiment.start_experiment()
        if(recent_experiment.experiment_running):
            print("Experiment was started")
        else:
            print("Experiment could not be started")

    else:
        print("Switching Off")
        print(scheduler.get_jobs())
        print("Removing all scheduled jobs")
        recent_experiment.stop_experiment()
        if(recent_experiment.experiment_running == False):
            print("Experiment was stopped")
        else:
            print("Experiment could not be stopped")

    return 'Automatic On' if current_status == 'Automatic Off' else 'Automatic Off'

# should be integrated already
# @app.route('/automatic_stop')
# def automatic_stop():
#     # https://github.com/viniciuschiele/flask-apscheduler
#     # scheduler.pause()
#     print(scheduler.get_jobs())
#     print("Removing all jobs")
#     # scheduler.remove_job(j0)
#     scheduler.remove_all_jobs()
#     print(scheduler.get_jobs())
#     return ("nothing")

@app.route('/picture')
def picture():
    recent_experiment = select_experiment()
    recent_experiment.picture_task()
    print(f"Picture saved in Experiment: {recent_experiment.name}")
    print(f"There are {len(recent_experiment.saved_positions)} saved positions")
    print(f"Created at {recent_experiment.saved_positions[-1].timestamp}")
    return ("nothing")

@app.route('/settings')
def automatic():
    print("settings")
    return ("nothing")

# buttons, scheduler end

#code gallery

@app.route("/gallery")
def show_gallery():
    recent_experiment = select_experiment()
    print(recent_experiment.name)
    raw_image_foldername = f'{recent_experiment.image_path}/{recent_experiment.name}/het-cam-raw/'
    raw_image_list = os.listdir(raw_image_foldername)
    print(raw_image_list)
    return render_template("gallery.html", experiment_foldername = recent_experiment.name, images = raw_image_list)

@app.route("/gallery-skeleton")
def show_skeleton():
    raw_image_foldername = f'{IMAGEPATH}/het-cam-raw'
    raw_image_list = os.listdir(raw_image_foldername)
    skeleton_image_foldername = f'{IMAGEPATH}/het-cam-skeleton'
    skeleton_images = os.listdir(skeleton_image_foldername)
    # find skeleton only for images w/o skeleton
    unskeletized_raw_images = list(set(raw_image_list) - set(skeleton_images))

    from bifurcation_detection import prepare_and_analyze
    scale_percent = 40
    for image in unskeletized_raw_images:
        prepare_and_analyze(image, raw_image_foldername, skeleton_image_foldername, scale_percent)
    # include newly created images for gallery
    skeleton_images = os.listdir(skeleton_image_foldername)
    print(skeleton_images)
    return render_template("gallery-skeleton.html", images = raw_image_list, images_skeletonized = skeleton_images)

@app.route("/gallery-yolo")
def show_yolo():
    raw_image_foldername = f'{IMAGEPATH}/het-cam-raw'
    raw_image_list = os.listdir(raw_image_foldername)
    yolo_image_foldername = f'{IMAGEPATH}/het-cam-yolo'
    yolo_images = os.listdir(yolo_image_foldername)
    unyolonized_raw_images = list(set(raw_image_list) - set(yolo_images))

    from detect import detect
    # detect()
    # scale_percent = 40
    for image in unyolonized_raw_images:
        detect(image, raw_image_foldername, yolo_image_foldername)

    yolo_images = os.listdir(yolo_image_foldername)
    print(yolo_images)
    return render_template("gallery-yolo.html", images = raw_image_list, images_yolonized = yolo_images)

#gallery code end

def select_experiment():
    print(f"Current database lenght: {len(DATABASE)}")
    if(len(DATABASE) == 0):
        new_experiment = Experiment(EXPERIMENT_NAME, scheduler,
        IMAGEPATH, Camera, EXPERIMENT_POSITIONS, INTERVAL)
        DATABASE.append(new_experiment)
        return new_experiment
    else:
        try:
            print("Trying to select the first flagged experiment")
            for experiment in DATABASE:
                if(experiment.flag):
                    return experiment
            print("No flagged experiments")
            raise Exception 
        except:
            print("Trying to select the last experiment in DB")
            new_experiment = DATABASE[-1]
            return new_experiment

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, threaded=True)
    # app.run()
