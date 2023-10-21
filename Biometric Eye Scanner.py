import cv2
import time
import math

face_classifier = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_eye.xml"
)

timerOn = False
startTime = 0
breakTime = False
start = 0
timeString = ""
blinkingThresholdOn = False
eye = False

video = cv2.VideoCapture(0)

def detect_eyes(image):
    global eye, blinkingThresholdOn, start
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(grayscale, 1.1, 6, minSize = (40, 40))
    eye = not (len(faces) == 0)
    checkThres()
    if not eye and blinkingThresholdOn and (time.time() - start) > 0.5:
        return False
    return True

def checkThres():
    global eye, blinkingThresholdOn, start
    if not eye and not blinkingThresholdOn:
        start = time.time()
        blinkingThresholdOn = True
    elif eye:
        start = 0
        blinkingThresholdOn = False  

while True:
    result, frame = video.read()

    if not result:
        break
    
    eye = detect_eyes(frame)

    if not timerOn and not breakTime:
        startTime = time.time()
        timerOn = True
        
    if ((time.time()-startTime) > 10.1) and timerOn:
        startTime = time.time()
        timerOn = False
        breakTime = True
    elif ((time.time()-startTime) > 5.1) and not timerOn and breakTime:
        startTime = time.time()
        timerOn = True
        breakTime = False

    if breakTime and not eye:
        startTime = time.time()

    frame = cv2.putText(frame, str(eye), (50, 50) , cv2.FONT_HERSHEY_SIMPLEX , 1,(0, 255, 0), 2, cv2.LINE_AA)
    if (not breakTime):
        #timeString = "Work Time: " + str(math.floor((time.time()-startTime)/60)) + ":" + str(math.floor(time.time()-startTime)%60) + ":" + str(int(round((((time.time()-startTime)%60) - (math.floor(time.time()-startTime)%60))*100)))
        timeString = "Work Time: " + str(math.floor((time.time()-startTime)/60)) + ":" + str(math.floor(time.time()-startTime)%60)
        frame = cv2.putText(frame, timeString, (50, 100) , cv2.FONT_HERSHEY_SIMPLEX , 1,(0, 255, 0), 2, cv2.LINE_AA)
    elif breakTime:
        timeString = "Break Time: " + str(math.floor((time.time()-startTime)/60)) + ":" + str(math.floor(time.time()-startTime)%60)
        frame = cv2.putText(frame, timeString, (50, 100) , cv2.FONT_HERSHEY_SIMPLEX , 1,(0, 255, 0), 2, cv2.LINE_AA)
    cv2.imshow("Eye Detection", frame)

    k = cv2.waitKey(1) & 0xFF
    #esc
    if k == 27:
        break

video.release()
cv2.destroyAllWindows()
