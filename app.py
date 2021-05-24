#!/usr/bin/env python
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

app = Flask(__name__)

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

interval_minutes = 60

@app.route('/')
def index():
    images = os.listdir('./images')
    """Video streaming home page."""
    return render_template('index.html', images=images)

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

# buttons, scheduler


def motor_position(position_in_degree):
    print(f"motor_position {position_in_degree}")
    # 4800 steps are 270°, 360 should never be possible since = 0°
    # degrees are divided by 90 and multiplied by 1600
    # only send int values to arduino!
    step_position_arduino = int(position_in_degree/90*1600)
    print(f"Sending: {step_position_arduino} steps")
    try:
        results = np.array(connect_to_arduino(comport,motor0_enable,motor0_direction,step_position_arduino,
            motor1_enable,motor1_direction,motor1_position,motor2_enable,motor2_direction,motor2_position,motor3_enable,motor3_direction,motor3_position))
        print(f"Received values: {results}")
    except:
        print("Microcontroller not found or not connected")
        return

@app.route('/move_deg')
def move_deg():
    degree = 0
    degree = int(request.args.get('degree'))
    if(degree >= 280):
        degree = 270
    if(degree <= -90):
        degree = -90
    print(f"Moving to {degree}°")
    motor_position(degree)
    return '''<h1>Moving to: {}</h1>'''.format(degree)
    # return ("nothing")

def motor_task_creator(task_id):
    print(f"start of motor task creator {task_id}")
    # creating motor task that runs every minute
    scheduler.add_job(func=motor_task, trigger='interval', minutes=interval_minutes, args=[task_id], id='move'+str(task_id))

def picture_task_creator(task_id):
    print(f"start of picture task creator {task_id}")
    # creating picture task that runs every minute
    scheduler.add_job(func=picture_task, trigger='interval', minutes=interval_minutes, args=[task_id], id='picture'+str(task_id))

def motor_task(task_id):
    # send to motor position
    print(f"task: moving to position {task_id}")
    motor_position(task_id)

def picture_task(task_position):
    # activate camera, this also generates a frame in gif_bytes_io
    # camera goes back to sleep after 10 s

    print("Setting higher resolution for automated pictures")
    new_resolution = [1280, 720]

    # this triggers the creation of a new thread, with old resolution setting
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    Camera().set_resolution(new_resolution)
    # Camera().resolution = new_resolution
    try:
        print(f"Resolution should be set to {Camera().resolution}")
        gen(Camera())
        # print("Camera generated")
        print(f"Resolution was set to {Camera().resolution}")
        # Camera get generated with high resolution?
    except:
        print("Could not generate camera")
        return

    print(f"task: start to take picture {task_position}")
    filename = f'images/position{task_position}_{datetime.now().strftime("%Y%m%d-%H%M%S")}.jpg'

    try:
        object_methods = [method_name for method_name in dir(Camera)
            if callable(getattr(Camera, method_name))]
        print(object_methods)
    except:
        print("could not find methods for object")

    frame = Camera().get_frame()

    # Camera().resolution = new_resolution
    # resolution = [640, 480]
    # Camera().set_resolution(resolution)

    video_frame_timepoint = (datetime.now().strftime("%Y%m%d-%H%M%S"))
    filename = f'images/position{task_position}_{video_frame_timepoint}.jpg'
    # # foldername = 'images\'
    # # filename = foldername+filename
    # print(filename)
    # # frame_bytes, frame = global_video_cam.get_frame()
    # # writing image
    gif_bytes_io = BytesIO()
    # store the gif bytes to the IO and open as image
    gif_bytes_io.write(frame)
    image = Image.open(gif_bytes_io)
    # # save as png through a stream
    # png_bytes_io = BytesIO() # or io.BytesIO()
    # image.save(png_bytes_io, format='PNG')
    # # print(png_bytes_io.getvalue()) # outputs the byte stream of the png
    # image.show()
    open_cv_image = np.array(image)
    # rgb channels are in wrong order since the image is from an raspberry camera
    RGB_img = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2RGB)
    cv2.imwrite(filename, RGB_img)
    print(f"image written {filename}")

    print("Setting lower resolution for webstream")
    new_resolution = [640, 480]
    Camera().set_resolution(new_resolution)


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

    # if Automatic On was sent and no jobs are scheduled
    if(current_status == 'Automatic Off') and not(scheduler.get_jobs()):
        print("Switching On")
        schedule_start = datetime.today()
        print(f"starting scheduling {schedule_start}")
        moving_time = 10
        print(f"moving time is assumed {moving_time} seconds") 
        task_seperation_increase = moving_time*2
        task_seperation = 1
        # instead, create a list - in this list the degrees where pics should be taken are stored
        # all positions: for degree in range(0, 360, 90)
        for degree in range(0, 90, 90): # starting angle, stop angle and step angle in degrees (180 = picture at 0 & 90, 270 = pic at 0,90,180)
            print(degree)
            schedule_time_movement = schedule_start + timedelta(seconds=task_seperation)
            schedule_time_picture = schedule_start + timedelta(seconds=moving_time+task_seperation)
            scheduler.add_job(func=motor_task_creator, trigger='date', run_date=schedule_time_movement, args=[degree], id='move_start'+str(degree))
            print(f"created moving job {degree} running at {schedule_time_movement}")
            scheduler.add_job(func=picture_task_creator, trigger='date', run_date=schedule_time_picture, args=[degree], id='picture_start'+str(degree))
            print(f"created picture job {degree} running at {schedule_time_picture}")
            task_seperation = task_seperation + task_seperation_increase
        print(scheduler.get_jobs())

    else:
        print("Switching Off")
        print(scheduler.get_jobs())
        print("Removing all scheduled jobs")
        # scheduler.remove_job(j0)
        scheduler.remove_all_jobs()
        print(scheduler.get_jobs())

    return 'Automatic On' if current_status == 'Automatic Off' else 'Automatic Off'

@app.route('/automatic_stop')
def automatic_stop():
    # https://github.com/viniciuschiele/flask-apscheduler
    # scheduler.pause()
    print(scheduler.get_jobs())
    print("Removing all jobs")
    # scheduler.remove_job(j0)
    scheduler.remove_all_jobs()
    print(scheduler.get_jobs())
    return ("nothing")

@app.route('/picture')
def picture(pos_name = "custom"):
    picture_task(pos_name)
    return ("nothing")

@app.route('/settings')
def automatic():
    print("settings")
    return ("nothing")

# buttons, scheduler end



#code gallery

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

@app.route("/gallery")
def gallery():
    images = os.listdir('./images')
    print(images)
    return render_template("gallery-index.html", images=images)

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["GET","POST"])
def upload_file():
    if request.method=="GET":
        return render_template('upload.html')
    target = os.path.join(APP_ROOT, 'images/')
    print(target)
    if not os.path.isdir(target):
        os.mkdir(target)
    for file in request.files.getlist("file"):
        print(file)
        filename = file.filename
        destination = "/".join([target, filename])
        print(destination)
        file.save(destination)
    return render_template("uploaded.html")

@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)

def send_image_for_filter(image):
    return render_template('filter.html', image=image)

@app.route("/filters")
def filter():
    return render_template('filters.html')

@app.url_defaults
def hashed_url_for_static_file(endpoint, values):
    if 'static' == endpoint or endpoint.endswith('.static'):
        filename = values.get('filename')
        if filename:
            if '.' in endpoint:  # has higher priority
                blueprint = endpoint.rsplit('.', 1)[0]
            else:
                blueprint = request.blueprint  # can be None too
            if blueprint:
                static_folder = app.blueprints[blueprint].static_folder
            else:
                static_folder = app.static_folder
            param_name = 'h'
            while param_name in values:
                param_name = '_' + param_name
            values[param_name] = static_file_hash(os.path.join(static_folder, filename))

def static_file_hash(filename):
    return int(os.stat(filename).st_mtime)

#gallery code end

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, threaded=True)
