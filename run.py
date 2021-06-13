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
    current_experiment = select_experiment()
    print(current_experiment.name)
    current_experiment.planned_position = degree
    current_experiment.motor_position()
    return '''<h1>Moving to: {}</h1>'''.format(degree)
    # return ("nothing")

#-------------------------------------------------------------------------------------

@app.route('/get_toggled_status') 
def toggled_status():
    current_status = request.args.get('status')
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
    current_experiment = select_experiment()
    # if Automatic On was sent and no jobs are scheduled
    if(current_status == 'Automatic Off') and not(scheduler.get_jobs()):
        print("Switching On")
        print(current_experiment.experiment_positions)
        current_experiment.show_experiment_positions()
        # start dummy experiment for now
        current_experiment.start_experiment()
        if(current_experiment.experiment_running):
            print("Experiment was started")
        else:
            print("Experiment could not be started")

    else:
        print("Switching Off")
        print(scheduler.get_jobs())
        print("Removing all scheduled jobs")
        current_experiment.stop_experiment()
        if(current_experiment.experiment_running == False):
            print("Experiment was stopped")
        else:
            print("Experiment could not be stopped")

    return 'Automatic On' if current_status == 'Automatic Off' else 'Automatic Off'

@app.route('/picture')
def picture():
    current_experiment = select_experiment()
    current_experiment.picture_task()
    print(f"Picture saved in Experiment: {current_experiment.name}")
    print(f"There are {len(current_experiment.saved_positions)} saved positions")
    print(f"Created at {current_experiment.saved_positions[-1].timestamp}")
    return ("nothing")

# buttons, scheduler end

#code gallery
# images could be sent directly:
# https://stackoverflow.com/questions/56946969/how-to-send-an-image-directly-from-flask-server-to-html

@app.route("/gallery")
def show_gallery():
    current_experiment = select_experiment()
    print(current_experiment.name)
    raw_image_foldername = f'{current_experiment.image_path}/{current_experiment.name}/{current_experiment.raw_dir}/'
    raw_image_list = os.listdir(raw_image_foldername)
    print(raw_image_list)
    foldername_gallery = f'{current_experiment.name}/{current_experiment.raw_dir}/'
    return render_template("gallery.html", experiment_name = current_experiment.name, 
    image_foldername = foldername_gallery, images = raw_image_list)

@app.route("/gallery-skeleton")
def show_gallery_skeleton():
    current_experiment = select_experiment()
    print(current_experiment.name)

    # this should be done via button or algorithm
    # in times where cpu load is low or after experiment
    # current_experiment.saved_positions.calculate_skeleton()
    for position in current_experiment.saved_positions:
        position.calculate_skeleton()
        # current_experiment.saved_positions[-1].timestamp

    skeleton_image_foldername = f'{current_experiment.image_path}/{current_experiment.name}/{current_experiment.skeleton_dir}/'
    print(f"skeleton img foldername: {skeleton_image_foldername}")
    skeleton_image_list = os.listdir(skeleton_image_foldername)
    print(skeleton_image_list)
    foldername_gallery = f'{current_experiment.name}/{current_experiment.skeleton_dir}/'
    return render_template("gallery.html", image_foldername = foldername_gallery,
    experiment_name = current_experiment.name, images = skeleton_image_list)

@app.route("/gallery-yolo")
def show_yolo():
    current_experiment = select_experiment()
    print(current_experiment.name)

    # this should be done via button or algorithm
    # in times where cpu load is low or after experiment
    # current_experiment.saved_positions.calculate_yolo()
    for position in current_experiment.saved_positions:
        position.calculate_yolo()
        # current_experiment.saved_positions[-1].timestamp

    yolo_image_foldername = f'{current_experiment.image_path}/{current_experiment.name}/{current_experiment.yolo_dir}/'
    print(f"yolo img foldername: {yolo_image_foldername}")
    yolo_image_list = os.listdir(yolo_image_foldername)
    print(yolo_image_list)
    foldername_gallery = f'{current_experiment.name}/{current_experiment.yolo_dir}/'
    return render_template("gallery.html", image_foldername = foldername_gallery,
    experiment_name = current_experiment.name, images = yolo_image_list)

@app.route('/experiments')
def experiments():
    print("experiments")
    print(DATABASE)
    experiment_name = request.args.get('experiment_name')
    print("experiment name:")
    print(experiment_name)
    # this cannto work for now !!!!!!!!!!!!!!!!!!!!!!
    # experiment_positions = request.args.get('experiment_positions')
    # interval = request.args.get('interval')
    # new_experiment = Experiment(experiment_name, scheduler,
    # IMAGEPATH, Camera, experiment_positions, interval)
    new_experiment = Experiment(experiment_name, scheduler,
    IMAGEPATH, Camera, EXPERIMENT_POSITIONS, INTERVAL)

    # unflag all experiments
    for experiment in DATABASE:
        if(experiment.flag):
            experiment.flag = False
    DATABASE.append(new_experiment)
    new_experiment.flag = True
    new_experiment.name = "GeorgsExperiment"
    # DATABASE.append(new_experiment)
    return render_template("experiments.html", experiment_name = new_experiment.name)

@app.route('/get_experiment_status') 
# @app.route('/experiments')
def experiment_status():
    current_experiment = request.args.get('status')
    print(current_experiment)
    current_experiment = select_experiment()

    return current_experiment.name


def select_experiment():
    print(f"Current database lenght: {len(DATABASE)}")
    if(len(DATABASE) == 0):
        print("No experiments found, creating default experiment")
        new_experiment = Experiment(EXPERIMENT_NAME, scheduler,
        IMAGEPATH, Camera, EXPERIMENT_POSITIONS, INTERVAL)
        DATABASE.append(new_experiment)
        return new_experiment
    else:
        # try to select experiment
        # return render_template("gallery.html", image_foldername = foldername_gallery)
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
