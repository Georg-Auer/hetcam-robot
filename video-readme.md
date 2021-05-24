hetcam-video-streaming

# SPOC lab CAM²: hetcam-webcam

start cam with 
sudo CAMERA=opencv python3 app.py
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

$ set CAMERA=opencv
$ python app.py