hetcam-video-streaming

# SPOC lab CAM²: het-cam-dashboard


How to make the script run on startup:
sudo nano /etc/rc.local

start cam with 
sudo CAMERA=opencv python3 run.py
to open on restricted port 80




How to make the script run on startup:
sudo nano /etc/rc.local
insert:
sudo CAMERA=opencv python3 app.py &

or for additional logging:
sudo CAMERA=opencv python3 app.py & > /home/pi/Desktop/log.txt 2>&1


https://blog.miguelgrinberg.com/post/flask-video-streaming-revisited

to start an OpenCV session from bash, you can do this:

$ CAMERA=opencv python app.py

From a Windows command prompt you can do the same as follows:

on windows run:
$ python run.py CAMERA=opencv

or:
$ set CAMERA=opencv
$ python run.py
