import cv2
import time

face_classifier = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_eye.xml"
)

start = 0
timeOn = False
eye = False

video = cv2.VideoCapture(0)

def detect_eyes(image):
    global eye, timeOn, start
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray_image, 1.1, 5, minSize = (40, 40))
    eye = not (len(faces) == 0)
    checkThres()
    if not eye and timeOn and (time.time() - start) > 0.5:
        return False
    return True

def checkThres():
    global eye, timeOn, start
    if not eye and not timeOn:
        start = time.time()
        timeOn = True
    elif eye:
        start = 0
        timeOn = False  

while True:
    result, frame = video.read()

    if result is False:
        break
    
    eye = detect_eyes(frame)
    
    frame = cv2.putText(frame, str(eye), (50, 50) , cv2.FONT_HERSHEY_SIMPLEX , 1,(0, 255, 0), 2, cv2.LINE_AA) 
    cv2.imshow("Eye Detection", frame)

    k = cv2.waitKey(1) & 0xFF
    #esc
    if k == 27:
        break

video.release()
cv2.destroyAllWindows()
