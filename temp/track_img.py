import cv2
import numpy as np 
from random import randint as randint
import  time 


ix,iy = -1,-1
# mouse callback function
def point(event,x,y,flags,param):
    global ix,iy
    if event == cv2.EVENT_LBUTTONDOWN:
        ix,iy = x,y
cv2.namedWindow('image')
cv2.setMouseCallback('image',point)

cap = cv2.VideoCapture('t1_.mp4')

doing = False
while True:
    suc, frame = cap.read()
    if suc and not doing:
        bbox = cv2.selectROI('tracker', frame)
        tracker = cv2.TrackerCSRT_create()
        tracker.init(frame, bbox)
        doing = True
        cv2.destroyAllWindows()

    new_suc, newbox = tracker.update(frame)
    if new_suc:
        p1 = (int(newbox[0]), int(newbox[1]))
        p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
        temp1 = p1
        temp2 = p2
        temp = newbox
        cv2.rectangle(frame, p1, p2,(255,0,0), 2, 1)
        cv2.imshow('image',frame)
    else: 
        cv2.rectangle(frame, temp1, temp2,(255,0,0), 2, 1)
        # doing = False
        bbox = (temp1[0])
        tracker = cv2.TrackerCSRT_create()
        tracker.init(frame, newbox)
        cv2.putText(frame, 'Change box', (100,100), cv2.FONT_HERSHEY_SIMPLEX ,  
                   1, (0,255,0), 1, cv2.LINE_AA)
        cv2.imshow('image',frame)
        time.sleep(1)

   
    
    
   

    #quit
    key = cv2.waitKey(1)
    if key == ord('a'):
        break
 
  
cap.release()
cv2.destroyAllWindows()