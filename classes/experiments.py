from datetime import datetime, timedelta

scheduler = APScheduler()
# if you don't wanna use a config, you can set options here:
# scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()

class Experiment(object):
    def __init__(self, name, planned_positions = [], time_between = [5]):
        self.name = name
        self.planned_positions = planned_positions
        self.time_between = time_between
        self.current_position = 0
        self.saved_positions = []
        self.experiment_status = "Off"
        # and a list of experiment positions
        # created during the experiment

    def show_timeframe(self):
        print(f"Time between imaging in experiment {self.name} set to {self.time_between} minutes")
    
    def go_to_xyz(self, position_in_degree):
        # note: xy is defined through degree,
        # z is always the same distance between object and camera
        motor_position(position_in_degree) # moves the arm
        self.current_position = position_in_degree

    def show_planned_positions(self):
        print("These are all planned positions")
        print(self.planned_positions)
    def remove_planned_positions(self):
        print("Removing all planned positions")
        self.planned_positions = []
    def add_planned_positions(self, new_position):
        print(f"Adding new planned position {new_position}")
        self.planned_positions.append(new_position)
        print("These are all planned positions")
        print(self.planned_positions)

    def save_position(self):
        # gives Position the name of the experiment and the current position
        print("saved poss")
        print(self.name, self.current_position)
        self.saved_positions.append(Position(self.name, self.current_position))
        # take image
    
    def show_saved_positions(self):
        print(f"Saved Positions: {self.saved_positions}")
    
    def start_experiment(self):
        print("Starting experiment")
        self.experiment_status = "On"
        # for element in self.planned_positions:
        #     self.saved_positions.append(Position(self.name, self.planned_positions))
        schedule_start = datetime.today()
        moving_time = 10 # in seconds
        print(f"Moving time is assumed {moving_time} seconds") 
        task_seperation_increase = moving_time*2
        task_seperation = 1
        for degree in self.planned_positions: # starting angle, stop angle and step angle in degrees (180 = picture at 0 & 90, 270 = pic at 0,90,180)
            print(degree)
            schedule_time_movement = schedule_start + timedelta(seconds=task_seperation)
            schedule_time_picture = schedule_start + timedelta(seconds=moving_time+task_seperation)
            scheduler.add_job(func=motor_task_creator, trigger='date', run_date=schedule_time_movement, args=[degree], id='move_start'+str(degree))
            print(f"created moving job {degree} running at {schedule_time_movement}")
            scheduler.add_job(func=picture_task_creator, trigger='date', run_date=schedule_time_picture, args=[degree], id='picture_start'+str(degree))
            print(f"created picture job {degree} running at {schedule_time_picture}")
            task_seperation = task_seperation + task_seperation_increase


        
    def stop_experiment(self):
        print("Stopping experiment")
        print(scheduler.get_jobs())
        print("Removing all scheduled jobs")
        # scheduler.remove_job(j0)
        scheduler.remove_all_jobs()
        print(scheduler.get_jobs())
        self.experiment_status = "Off"

    def toggle_experiment_status(self):
        if (self.experiment_status == "Off"):
            self.start_experiment()
        elif (self.experiment_status == "On"):
            self.stop_experiment()
        else:
            print("Experiment in unknown status, switching Off")
            self.stop_experiment()

class Position(object):
    # raw_image, skeletal_image,
    # feature_bifurcations, feature_endings, yolo_image, yolo_classes,
    # yolo_coordinates, yolo_poi_circles, features_bifurcations_poi, feature_endings_poi
    def __init__(self, name, xyz_position_in_degree):
        self.name = name
        self.position = xyz_position_in_degree # z stays the same in this robot
        self.timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        # should it take a starting image here?
        # video_frame_timepoint = (datetime.now().strftime("%Y%m%d-%H%M%S"))
        # filename = f'{IMAGEPATH}/het-cam-raw/position{task_position}_{video_frame_timepoint}.jpg'
    
    def take_raw_image(self):
        print(f"raw image should be taken")
        self.raw_image = take_image(self)
    def calculate_skeleton(self):
        print(f"raw image should be sent to analyze skeleton")
        self.skeletal_image = analyze_skeletal(self.raw)
    def calculate_yolo(self):
        print(f"raw image should be sent to analyze objects")
        self.yolo_image = analyze_yolo(self.raw)
        # self.yolo_classes = analyze_yolo(self.raw)
        # self.yolo_coordinates = analyze_yolo(self.raw)
        # self.yolo_classes = analyze_yolo(self.raw)

def take_image(self):
    print("taking image")
    # image = cv2-image(self.name, self.actualposition??)
    # return image

def analyze_skeletal(self):
    print("taking image")
    # image = cv2-image
    # return image, xy_coordinates

def analyze_yolo(self):
    print("taking image")
    # image = cv2-image
    # return image, object_bounding_box

if __name__ == '__main__':
    # het = Experiment("Nr. 1", [0, 90, 180, 270], 5)
    # het.show_timeframe()
    # print(het.planned_positions)  
    # het.experiment_status
    # het.toggle_experiment_status()
    # print(het.experiment_status)
    # het.toggle_experiment_status()
    # print(het.experiment_status)
    # print(f"Current pos: {het.current_position}")
    # het.save_position()
    # het.current_position = 90
    # het.save_position()
    # print(f"Current pos: {het.current_position}")
    # print(het.show_saved_positions())
    # for element in het.saved_positions:
    #     print(element.name)
    #     print(element.position)
    #     print(element.timestamp)

    het2 = Experiment("Nr. 1", [0, 90, 180, 270], 5)
    print(het2.planned_positions)

    het2.show_planned_positions()
    het2.add_planned_positions(45)
    het2.show_planned_positions()
    het2.remove_planned_positions()
    het2.show_planned_positions()

    het2.start_experiment()
    print("was started")
    het2.stop_experiment()
    # test_position = Position("test", 270)
    # print(test_position.name)
    # print(test_position.timestamp)
#---------------------------------------------------------
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

# @app.route('/move_deg')
# def move_deg():
#     degree = 0
#     degree = int(request.args.get('degree'))
#     if(degree >= 280):
#         degree = 270
#     if(degree <= -90):
#         degree = -90
#     print(f"Moving to {degree}°")
#     motor_position(degree)
#     return '''<h1>Moving to: {}</h1>'''.format(degree)
#     # return ("nothing")

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
    print("Setting higher resolution for automated pictures")
    new_resolution = [1280, 720]
    Camera().set_resolution(new_resolution)
    try:
        print(f"Resolution should be set to {Camera().resolution}")
        gen(Camera())
        print(f"Resolution was set to {Camera().resolution}")
    except:
        print("Could not generate camera")
        return
    print(f"task: start to take picture {task_position}")
    frame = Camera().get_frame()
    video_frame_timepoint = (datetime.now().strftime("%Y%m%d-%H%M%S"))
    filename = f'{IMAGEPATH}/het-cam-raw/position{task_position}_{video_frame_timepoint}.jpg'
    gif_bytes_io = BytesIO()
    gif_bytes_io.write(frame)
    image = Image.open(gif_bytes_io)
    open_cv_image = np.array(image)
    RGB_img = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2RGB)
    cv2.imwrite(filename, RGB_img)
    print(f"image written {filename}")
    print("Setting lower resolution for webstream")
    new_resolution = [640, 480]
    Camera().set_resolution(new_resolution)


# @app.route('/get_toggled_status') 
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
        moving_time = 10 # in seconds
        print(f"moving time is assumed {moving_time} seconds") 
        task_seperation_increase = moving_time*2
        task_seperation = 1
        # instead, create a list - in this list the degrees where pics should be taken are stored
        # all positions: for degree in range(0, 360, 90)
        for degree in range(0, 360, 90): # starting angle, stop angle and step angle in degrees (180 = picture at 0 & 90, 270 = pic at 0,90,180)
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

# @app.route('/automatic_stop')
def automatic_stop():
    # https://github.com/viniciuschiele/flask-apscheduler
    # scheduler.pause()
    print(scheduler.get_jobs())
    print("Removing all jobs")
    # scheduler.remove_job(j0)
    scheduler.remove_all_jobs()
    print(scheduler.get_jobs())
    return ("nothing")

# @app.route('/picture')
def picture(pos_name = "custom"):
    picture_task(pos_name)
    return ("nothing")

# @app.route('/settings')
def automatic():
    print("settings")
    return ("nothing")

# buttons, scheduler end
