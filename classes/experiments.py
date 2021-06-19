from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
import os
from classes.pyserial_connection_arduino import connect_to_arduino, list_available_ports
from classes.bifurcation_detection import prepare_and_analyze
from detect import detect

from classes.scientific_camera import take_raspicampic

class Experiment(object):
    def __init__(self, name, scheduler, image_path,
    Camera, experiment_positions = [], interval_minutes = 5):
        self.name = name
        self.experiment_positions = experiment_positions
        self.interval_minutes = interval_minutes
        self.current_position = self.planned_position = 0
        # list of experiment positions
        # created during the experiment
        self.saved_positions = []
        self.scheduler = scheduler
        self.image_path = image_path
        self.Camera = Camera
        # self.resolution = [1280, 720]
        # self.resolution = [4056, 3040]
        self.resolution = [2592, 1944]
        # self.resolution = [3280, 2464]
        self.experiment_running = False
        self.flag = False
        self.motor_comport = '/dev/ttyACM0'
        self.creation_time = datetime.today()
        self.exp_foldername = f'{self.image_path}/{self.name}'
        self.raw_dir = "het-cam-raw"
        self.skeleton_dir = "het-cam-skeleton"
        self.yolo_dir = "het-cam-yolo"
        self.img_variant_folders = [self.raw_dir,self.skeleton_dir,self.yolo_dir]
        self.create_directories()

    # def show_timeframe(self):
    #     print(f"Time between imaging in experiment {self.name} set to {self.time_between} minutes")

    def show_experiment_positions(self):
        print("These are all planned positions")
        print(self.experiment_positions)
    def remove_experiment_positions(self):
        print("Removing all planned positions")
        self.experiment_positions = []
    def add_experiment_positions(self, new_position):
        print(f"Adding new planned position {new_position}")
        self.experiment_positions.append(new_position)
        print("These are all planned positions")
        print(self.experiment_positions)

    def save_position(self):
        # gives Position the name of the experiment and the current position
        print("Save position")
        print(self.name, self.current_position)
        # should the Camera be given to the Position????????????????
        # self.saved_positions.append(Position(self.name, self.current_position, self.Camera))
        self.saved_positions.append(Position(self.name, self.current_position))
        # take image!!!!!!!!
    
    def show_saved_positions(self):
        print(f"Saved Positions: {self.saved_positions}")
    
    # tasking
    def start_experiment(self):
        print("Starting experiment")
        self.experiment_running = True
        try:
            self.Camera().set_resolution(self.resolution)
            print(f"Resolution set to {self.resolution} for automated pictures")
        except:
            print("Resolution could not be set for experiment")
        # for element in self.experiment_positions:
        #     self.saved_positions.append(Position(self.name, self.experiment_positions))
        schedule_start = datetime.today()
        moving_time = 10 # in seconds
        print(f"Moving time is assumed {moving_time} seconds") 
        task_seperation_increase = moving_time*2
        task_seperation = 1
        for degree in self.experiment_positions: 
            print(degree)
            schedule_time_movement = schedule_start + timedelta(seconds=task_seperation)
            schedule_time_picture = schedule_start + timedelta(seconds=moving_time+task_seperation)
            self.scheduler.add_job(func=self.motor_task_creator, trigger='date', run_date=schedule_time_movement, args=[degree], id='move_start'+str(degree))
            print(f"created moving job {degree} running at {schedule_time_movement}")
            self.scheduler.add_job(func=self.picture_task_creator, trigger='date', run_date=schedule_time_picture, args=[degree], id='picture_start'+str(degree))
            print(f"created picture job {degree} running at {schedule_time_picture}")
            task_seperation = task_seperation + task_seperation_increase

    def stop_experiment(self):
        print("Stopping experiment")
        print(self.scheduler.get_jobs())
        print("Removing all scheduled jobs")
        # self.scheduler.remove_job(j0)
        self.scheduler.remove_all_jobs()
        print(self.scheduler.get_jobs())
        print("Setting lower resolution for webstream")
        new_resolution = [640, 480]
        self.Camera().set_resolution(new_resolution)
        self.experiment_running = False

    def motor_task_creator(self, task_id):
        # creating motor task that runs every minute
        self.planned_position = task_id
        print(f"start of motor task creator {self.planned_position}")
        self.scheduler.add_job(func=self.motor_position, trigger='interval', minutes=self.interval_minutes, id='move'+str(task_id))

    def picture_task_creator(self, task_id):
        print(f"start of picture task creator {task_id}")
        # creating picture task that runs every minute
        self.scheduler.add_job(func=self.picture_task, trigger='interval', minutes=self.interval_minutes, id='picture'+str(task_id))

    def picture_task(self):
        print(f"task: start to take picture {self.current_position}")
        # use webcam?
        # frame = self.Camera().get_frame()
        video_frame_timepoint = (datetime.now().strftime("%Y%m%d-%H%M%S"))
        filename = f'position{self.current_position}_{video_frame_timepoint}.jpg'
        file_in_foldername = f'{self.image_path}/{self.name}/{self.raw_dir}/{filename}'
        # gif_bytes_io = BytesIO()
        # gif_bytes_io.write(frame)
        # image = Image.open(gif_bytes_io)
        # open_cv_image = np.array(image)
        # RGB_img = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2RGB)

        try:
            camera.close()
            print("camera closed")
        except:
            print("camera was not open")

        try:
            from picamera import PiCamera
            from picamera.array import PiRGBArray
            import time
            camera = PiCamera()
        except:
            print("camera was not closed last time or is still in use")
            #camera.close()
            #rawCapture.close()

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
        camera.capture(rawCapture, format="rgb")
        RGB_img = rawCapture.array
        camera.close()
        rawCapture.close() #is this even possible?
        # for testing only
        # cv2.imshow('image',RGB_img)
        # cv2.waitKey(0)
        cv2.imwrite(file_in_foldername, RGB_img)
        print(f"image written {file_in_foldername}")
        # self.Camera().set_resolution(new_resolution)
        # create new position with image
        self.saved_positions.append(Position(self.name, self.current_position,
        self.exp_foldername, self.raw_dir, self.skeleton_dir,
        self.yolo_dir, filename, RGB_img))

    def create_directories(self):
        for variant in self.img_variant_folders:
            foldername = f'{self.exp_foldername}/{variant}/'
            # Create target Directory if don't exist
            if not os.path.exists(foldername):
                os.makedirs(foldername) # also creates non-existant intermediaries
                print("Directory " , foldername ,  " Created ")
            else:    
                print("Directory " , foldername ,  " already exists")

    def motor_position(self):
        position_in_degree = self.planned_position
        print(f"motor_position {position_in_degree}")
        # 4800 steps are 270°, 360 should never be possible since = 0°
        # degrees are divided by 90 and multiplied by 1600
        # only send int values to arduino!
        step_position_arduino = int(position_in_degree/90*1600)
        print(f"Sending: {step_position_arduino} steps")
        try:
            # results = np.array(connect_to_arduino(comport = '/dev/ttyACM0',motor0_enable,motor0_direction,step_position_arduino,
            #     motor1_enable,motor1_direction,motor1_position,motor2_enable,motor2_direction,motor2_position,motor3_enable,motor3_direction,motor3_position))
            # enabled = 0, disabled = 1; 0 = counterclockwise 1 = clockwise
            results = np.array(connect_to_arduino(self.motor_comport, 0, 0, step_position_arduino))
            print(f"Received values: {results}")
            # this could be parsed and converted to degree
            # or just assume motor has moved to destination
            self.current_position = position_in_degree
        except:
            print("Microcontroller not found or not connected")
            return
class Position(object):
    # raw_image, skeletal_image,
    # feature_bifurcations, feature_endings, yolo_image, yolo_classes,
    # yolo_coordinates, yolo_poi_circles, features_bifurcations_poi, feature_endings_poi
    def __init__(self, name, xyz_position_in_degree, exp_foldername, raw_dir, skeleton_dir, yolo_dir, filename, RGB_img):
        self.name = name
        self.position = xyz_position_in_degree # z stays the same in this robot
        self.timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.filename = filename
        self.raw_image = RGB_img
        self.exp_foldername = exp_foldername
        self.raw_dir = raw_dir
        self.skeleton_dir = skeleton_dir
        self.yolo_dir = yolo_dir
        # should it take a starting image here?
        # video_frame_timepoint = (datetime.now().strftime("%Y%m%d-%H%M%S"))
        # filename = f'{IMAGEPATH}/het-cam-raw/position{task_position}_{video_frame_timepoint}.jpg'
    
    # def take_raw_image(self):
    #     print(f"raw image should be taken")
    #     self.raw_image = take_image(self)
    def calculate_skeleton(self):
        print(f"raw image is sent to analyze skeleton")
        print(f"Calculating for position {self.name}")
        print(type(self.raw_image))
        self.skeletal_image, self.x_terminations, self.y_terminations, self.x_bifurcations, self.y_bifurcations = prepare_and_analyze(self.raw_image)
        print(self.skeletal_image,self.x_terminations, self.y_terminations, self.x_bifurcations, self.y_bifurcations)
        file_in_foldername = f"{self.exp_foldername}/{self.skeleton_dir}/{self.filename}"
        print(file_in_foldername)
        cv2.imwrite(file_in_foldername, self.skeletal_image)

    def calculate_yolo(self):
        print(f"raw image should be sent to analyze objects")
        print(f"Calculating for position {self.name}")
        print(type(self.raw_image))
        file_in_foldername = f"{self.exp_foldername}/{self.raw_dir}/{self.filename}"
        print(file_in_foldername)
        detect(file_in_foldername, self.exp_foldername, self.yolo_dir)
        # self.yolo_image = 
        # this should also get bounding boxes and found classes

if __name__ == '__main__':

    het2 = Experiment("Nr. 1", [0, 90, 180, 270], 5)
    print(het2.experiment_positions)

    het2.show_experiment_positions()
    het2.add_experiment_positions(45)
    het2.show_experiment_positions()
    het2.remove_experiment_positions()
    het2.show_experiment_positions()

    het2.start_experiment()
    print("was started")
    het2.stop_experiment()
    # test_position = Position("test", 270)
    # print(test_position.name)
    # print(test_position.timestamp)
#---------------------------------------------------------

