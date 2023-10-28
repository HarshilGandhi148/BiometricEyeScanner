import cv2
import time
import math
import eyetracker as et

#dataset to detect eyes
eye_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

#used to create timers for break, work, and blinking threshold
breakTimer = False
startBreak = time.time()
workTimerOn = False
startTime = 0
breakTime = False
startEyeThres = 0
timeString = ""
blinkingThresOn = False
eyeDetected = False

#constants
BLINK_THRESHOLD = 0.5
WORK_TIME = 20*60
BREAK_TIME = 20

video = cv2.VideoCapture(0)

#detects whether an eye is in frame or not
def detect_eyes(image):
    global eyeDetected, blinkingThresOn, startEyeThres
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    eyes = eye_classifier.detectMultiScale(grayscale, 1.1, 7, minSize = (40, 40))
    eyeDetected = not (len(eyes) == 0)
    
    #creates a threshold for blinkking
    checkThres()
    if not eyeDetected and blinkingThresOn and (time.time() - startEyeThres) > BLINK_THRESHOLD:
        return False
    return True

def create_eye_box(image):
    gray_scale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    eyes = eye_classifier.detectMultiScale(gray_scale, 1.1, 7, minSize = (40, 40))
    for (x, y, w, h) in eyes:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 4)
    return eyes

#used for the blinking threshold
def checkThres():
    global eyeDetected, blinkingThresOn, startEyeThres
    if not eyeDetected and not blinkingThresOn:
        startEyeThres = time.time()
        blinkingThresOn = True
    elif eyeDetected:
        startEyeThres = 0
        blinkingThresOn = False  

while True:
    result, frame = video.read()

    if not result:
        break
    
    eyeDetected = detect_eyes(frame)

    #turns the work timer on if not done so
    if not workTimerOn and not breakTime:
        startTime = time.time()
        workTimerOn = True
        
    #starts/ends work
    if ((time.time()-startTime) > WORK_TIME + 0.1) and workTimerOn:
        startTime = time.time()
        workTimerOn = False
        breakTime = True
    elif ((time.time()-startTime) > BREAK_TIME + 0.1) and not workTimerOn and breakTime:
        startTime = time.time()
        workTimerOn = True
        breakTime = False

    #used to reset/start break timer when needed
    if not breakTime and not eyeDetected and not breakTimer:
        breakTimer = True
        startBreak = time.time()
    elif breakTimer and not breakTime and eyeDetected:
        breakTimer = False
        
    if (time.time() - startBreak) > BREAK_TIME and breakTimer:
        startTime = time.time()
    
    if breakTime and eyeDetected:
        startTime = time.time()

    create_eye_box(frame)
    frame = et.detectEyes(frame)
    if (not breakTime):
        '''
        Used for milliseconds (if needed):
        timeString = "Work Time: " + str(math.floor((time.time()-startTime)/60)) + ":" + str(math.floor(time.time()-startTime)%60) + ":" + str(int(round((((time.time()-startTime)%60) - (math.floor(time.time()-startTime)%60))*100)))
        '''
        timeString = "Work - " + str(math.floor((time.time()-startTime)/60)) + ":" + str(math.floor(time.time()-startTime)%60)
        frame = cv2.putText(frame, timeString, (25, 50) , cv2.FONT_HERSHEY_DUPLEX , 1, (0, 0, 0), 2, cv2.LINE_AA)
    elif breakTime:
        timeString = "Break -" + str(math.floor((time.time()-startTime)/60)) + ":" + str(math.floor(time.time()-startTime)%60)
        frame = cv2.putText(frame, timeString, (25, 50) , cv2.FONT_HERSHEY_DUPLEX , 1, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.imshow("Eye Detection", frame)

    k = cv2.waitKey(1) & 0xFF
    
    #esc to end program
    if k == 27:
        break

video.release()
cv2.destroyAllWindows()
