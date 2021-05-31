#!/bin/sh
python3 detect.py --weights weights/best.pt --img 416 --conf 0.4 --source het-cam-test2.jpg

#windows:
# py -3.7 detect.py --weights weights/best.pt --img 416 --conf 0.4 --source het-cam-test2.jpg
# py -3.7 detect.py --weights weights/best.pt --img 416 --conf 0.4 --project app/base/static/upload --exist-ok --name het-cam-yolo --source app/base/static/upload/het-cam-raw

# for webcam example
# python detect.py --weights weights/best.pt --img 416 --conf 0.4 --source 0