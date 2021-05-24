from dearpygui import core, simple
from pyserial_connection_arduino import connect_to_arduino, list_available_ports
import numpy as np

# for saving variables
comport = '/dev/ttyACM0'
motor0_enable = 0
motor0_direction = 0
motor0_position = 0
motor1_enable = 1
motor1_direction = 0
motor1_position = 0
motor2_enable = 1
motor2_direction = 0
motor2_position = 0
motor3_enable = 1
motor3_direction = 0
motor3_position = 0

# callback
def retrieve_log(sender, callback):
    core.show_logger()
    for element in motor_count:
        core.log_info(core.get_value(f"motor {element}##inputtext"))

    # log_info(get_value("comport##inputtext")

# list all available exceptions
# print(dir(locals()['__builtins__']))

def motor0_pos0(sender, callback):
    comport = core.get_value("comport##inputtext")
    results = np.array(connect_to_arduino(comport,motor0_enable,motor0_direction,0,
        motor1_enable,motor1_direction,motor1_position,motor2_enable,motor2_direction,motor2_position,motor3_enable,motor3_direction,motor3_position))
    print(f"Received values: {results}")
    motorvalues = (results[2],results[5],results[8],results[11])
    print(motorvalues)
    nr_of_motor = 0
    for rcvd_value in motorvalues:
        print(rcvd_value)
        core.set_value(f"received value motor {nr_of_motor}", rcvd_value)
        nr_of_motor += 1
def motor0_pos90(sender, callback):
    comport = core.get_value("comport##inputtext")
    results = np.array(connect_to_arduino(comport,motor0_enable,motor0_direction,1600,
        motor1_enable,motor1_direction,motor1_position,motor2_enable,motor2_direction,motor2_position,motor3_enable,motor3_direction,motor3_position))
    print(f"Received values: {results}")
    motorvalues = (results[2],results[5],results[8],results[11])
    print(motorvalues)
    nr_of_motor = 0
    for rcvd_value in motorvalues:
        print(rcvd_value)
        core.set_value(f"received value motor {nr_of_motor}", rcvd_value)
        nr_of_motor += 1
def motor0_pos180(sender, callback):
    comport = core.get_value("comport##inputtext")
    results = np.array(connect_to_arduino(comport,motor0_enable,motor0_direction,3200,
        motor1_enable,motor1_direction,motor1_position,motor2_enable,motor2_direction,motor2_position,motor3_enable,motor3_direction,motor3_position))
    print(f"Received values: {results}")
    motorvalues = (results[2],results[5],results[8],results[11])
    print(motorvalues)
    nr_of_motor = 0
    for rcvd_value in motorvalues:
        print(rcvd_value)
        core.set_value(f"received value motor {nr_of_motor}", rcvd_value)
        nr_of_motor += 1
def motor0_pos270(sender, callback):
    comport = core.get_value("comport##inputtext")
    results = np.array(connect_to_arduino(comport,motor0_enable,motor0_direction,4800,
        motor1_enable,motor1_direction,motor1_position,motor2_enable,motor2_direction,motor2_position,motor3_enable,motor3_direction,motor3_position))
    print(f"Received values: {results}")
    motorvalues = (results[2],results[5],results[8],results[11])
    print(motorvalues)
    nr_of_motor = 0
    for rcvd_value in motorvalues:
        print(rcvd_value)
        core.set_value(f"received value motor {nr_of_motor}", rcvd_value)
        nr_of_motor += 1


def send_motor_values(sender, callback):

    # this should be generative code instead
    # nr_of_motors = 4
    value_list_to_send = []
    for element in motor_count:
        try:
            print(f"Printing value of motor {element}")
            print(core.get_value(f"motor {element}##inputtext"))
            # set comport to first found comport
            print(core.get_value(f"motor {0}##inputtext"))
            value_list_to_send.append(int(core.get_value(f"motor {element}##inputtext")))
        except ValueError:
            value_list_to_send.append(0)

    print(f"Values in the list: {value_list_to_send}")

    # this should be generative code instead
    motor0_position = value_list_to_send[0]
    motor1_position = value_list_to_send[1]
    motor2_position = value_list_to_send[2]
    motor3_position = value_list_to_send[3]

    comport = core.get_value("comport##inputtext")
    results = np.array(connect_to_arduino(comport,motor0_enable,motor0_direction,motor0_position,
        motor1_enable,motor1_direction,motor1_position,motor2_enable,motor2_direction,motor2_position,motor3_enable,motor3_direction,motor3_position))
    print(f"Received values: {results}")
    # take ony every thrid value, those are the motor values
    motorvalues = (results[2],results[5],results[8],results[11])
    print(motorvalues)
    nr_of_motor = 0
    for rcvd_value in motorvalues:
        print(rcvd_value)
        core.set_value(f"received value motor {nr_of_motor}", rcvd_value)
        nr_of_motor += 1

# def adjust_comport(sender, callback):
#     print(core.get_value("comport##inputtext"))
    # for some reason, this does not work:
    # comport = get_value("comport##inputtext")

def find_comports(sender, callback):
    #print(list_available_ports())
    comport_list = list_available_ports()
    core.set_value("Click button for new search", comport_list)
    # this takes the first found comport and puts it into the comport to connect
    # on Raspberry, this *should* enable a quick connection
    core.set_value("comport##inputtext", comport_list[0])

with simple.window("Motor Window"):

    core.add_text("To adjust the position of the motors, enter values and click on the respective send value.", wrap=500, bullet=True)
    core.add_text("Press the 'print-log' button to display all values in an log", wrap = 500, bullet=True)
    # button for listing all available COM ports
    core.add_button("Search COM Ports", callback=find_comports)
    core.add_label_text("Click button for new search")
    core.set_value("Click button for new search", "No values where received yet")

    core.add_text("Please choose the COM Port where the microcontroller is connected:")
    core.add_input_text("comport##inputtext", hint="enter port, e.g. COM0")
    # text input fields for all motors are created
    # for each value there is a button to send the entered value to the motor
    core.add_text("Please choose position for any/all motors:")
    motor_count = [0,1,2,3]
    for element in motor_count:
        core.add_input_text(f"motor {element}##inputtext", hint="enter position in ticks, 6400 ticks are 360°", decimal=True)
        core.add_label_text(f"received value motor {element}")
        core.set_value(f"received value motor {element}", "No values where received yet")
        #print(f"element name {element}")

    core.add_button("Go to position 0°", callback=motor0_pos0)
    core.add_same_line()
    core.add_button("Go to position 90°", callback=motor0_pos90)
    core.add_same_line()
    core.add_button("Go to position 180°", callback=motor0_pos180)
    core.add_same_line()
    core.add_button("Go to position 270°", callback=motor0_pos270)
    
    core.add_button("Go to numerically define positions", callback=send_motor_values)
    core.add_button("print-log", callback=retrieve_log)

    # set main window & size
    core.set_main_window_size(800, 550)
    core.set_primary_window("Motor Window", True)
    core.set_main_window_title("Motor Control")

    # edit button colors
    #https://github.com/hoffstadt/DearPyGui/discussions/615
    #simple.show_style_editor()

# this function starts the dearpygui
core.start_dearpygui()