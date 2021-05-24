import time
import numpy as np
from pySerialTransfer import pySerialTransfer as txfer
# please make sure to pip install pySerialTransfer==1.2
# connection will not work with pySerialTransfer==2.0
# requirement: pip install pyserial (works with 3.4 and most likely newer but not much older versions)
# on teensy: include "SerialTransfer.h" Version 2.0
# updated: now works with current SerialTransfer.h, and pySerialTransfer (27.02.2021)
    
def connect_to_arduino(comport,motor0_enable,motor0_direction,motor0_position,
        motor1_enable,motor1_direction,motor1_position,motor2_enable,motor2_direction,motor2_position,motor3_enable,motor3_direction,motor3_position):
    try:
        print(f"Connecting to {comport}")
        link = txfer.SerialTransfer(comport)
        
        link.open()
        time.sleep(1) # allow some time for the Arduino to completely reset
        
        # reset send_size
        send_size = 0
        
        # Send a list
        list_ = [motor0_enable, motor0_direction, motor0_position, motor1_enable, motor1_direction,  motor1_position,
            motor2_enable, motor2_direction, motor2_position, motor3_enable, motor3_direction, motor3_position]
        list_size = link.tx_obj(list_)
        send_size += list_size
        
        # Transmit all the data to send in a single packet
        link.send(send_size)
        print("Message sent...")
        
        # Wait for a response and report any errors while receiving packets
        while not link.available():
            if link.status < 0:
                if link.status == -1:
                    print('ERROR: CRC_ERROR')
                elif link.status == -2:
                    print('ERROR: PAYLOAD_ERROR')
                elif link.status == -3:
                    print('ERROR: STOP_BYTE_ERROR')

        # Parse response list
        ###################################################################
        rec_list_  = link.rx_obj(obj_type=type(list_),
                                    obj_byte_size=list_size,
                                    list_format='i')
 
        print(f'SENT: {list_}')
        print(f'RCVD: {rec_list_}')

        link.close()
        return rec_list_

    except KeyboardInterrupt:
        link.close()

    except:
        import traceback
        traceback.print_exc()
        link.close()

def list_available_ports():
    ports = txfer.open_ports()
    print("Available ports:")
    print(ports)
    return ports

if __name__ == "__main__":
    list_available_ports()
    comport = '/dev/ttyACM0'
    # enable = 0, disable = 1
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
    try:
        results = np.array(connect_to_arduino(comport,motor0_enable,motor0_direction,motor0_position,
            motor1_enable,motor1_direction,motor1_position,motor2_enable,motor2_direction,motor2_position,motor3_enable,motor3_direction,motor3_position))
        print(results)
    except:
        print("Sending did not work, please check comport")