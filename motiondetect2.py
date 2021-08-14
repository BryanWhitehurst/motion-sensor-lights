import cv2
import imutils
import numpy as np
import requests
import json
from time import time as time1, strftime, localtime
import time
import keys

#turn lighs on when motion is detected

def toggle(turnOn):
    data = json.dumps({"on": turnOn})
    requests.put('http://'+keys.IP_ADDR+'/api/'+keys.API_KEY()+'/groups/1/action', data=data)


cap = cv2.VideoCapture(0) #use default webcam
if (not(cap.isOpened())): print("failed to open webcam")

#let cam adjust to lighting
for i in range(10): frame = cap.read()

state = "off"
firstFrame = None
t0= time1()

while True:
    #if webcam was closed because of detected motion, reopen recording
    if (not(cap.isOpened())): 
        cap = cv2.VideoCapture(0)
        #let cam adjust to lighting
        for i in range(10): frame = cap.read()

    frame = cap.read()
    if frame is None:
	    break

    #resize image and convert to gray
    frame = imutils.resize(frame[1], width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if firstFrame is None:
	    firstFrame = gray
	    continue

    diff = time1() - t0
    if(diff > 500):
        firstFrame = gray


    #if it has been 5 mins since motion has been detected, turn lights off
    #and then reset first frame
    if(state == "on" and diff > 30): 
        print("No motion detected for 30 seconds, turn off")
        toggle(False)
        state = "off"
        firstFrame = gray
        t0 = time1() 
        continue 
        
    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)  

    # loop over the contours
    for c in cnts:
		# if the contour is too small, ignore it
        if cv2.contourArea(c) < 500:  #FIX ME
            continue
        else:
            #We have a hit: stop recording temporarily
            cap.release()
            firstFrame = None #force reset of base-line frame
            data = ""
            if(state == "off"): 
                print("motion detected! Turning Lights on")
                toggle(True)
                state = "on"
                
            else: print("motion detected! Lights are on, reset time")


            t0 = time1() #reset timer everytime motion is detected
            time.sleep(5) #5 second cooldown before checking for motion again
            break 
