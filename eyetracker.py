import cv2
import dlib
import numpy as np

def idle(x):
    pass

def shapeToNPArray(shape, dtype="int"):
    coords = np.zeros((68, 2), dtype = dtype)
    for i in range(0, 68):
        coords[i] = (shape.part(i).x,shape.part(i).y)
    return(coords)

def maskEyes(mask,side,shape):
    points = [shape[i] for i in side]
    points = np.array(points, dtype = np.int32)
    mask = cv2.fillConvexPoly(mask, points, 255)
    return(mask)

def contour(thresh, mid, img, right = False):
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    try:
        cnt = max(cnts, key = cv2.contourArea)
        M = cv2.moments(cnt)
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        if right:
            cx += mid
            print(cx - rightMidX)
            print(cy - rightMidY)
        else:
            print(cx - leftMidX)
            print(cy - leftMidY)
        cv2.circle(img, (cx, cy), 4, (255, 255, 255), 2)
    except:
        idle(0)

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

left = [36, 37, 38, 39, 40, 41]
right = [42, 43, 44, 45, 46, 47]

leftXSum = 0
leftYSum = 0
rightXSum = 0
rightYSum = 0
leftMidX = 0
leftMidY = 0
rightMidX = 0
rightMidY = 0

cap = cv2.VideoCapture(0)
ret, img = cap.read()
thresh = img.copy()

kernel = np.ones((9, 9), np.uint8)

def detectEyes(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 1)
    for rect in rects:
        leftXSum = 0
        leftYSum = 0
        rightXSum = 0
        rightYSum = 0
        shape = predictor(gray, rect)
        shape = shapeToNPArray(shape)
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        mask = maskEyes(mask, left, shape)
        mask = maskEyes(mask, right, shape)
        mask = cv2.dilate(mask, kernel, 5)
        eyes = cv2.bitwise_and(img, img, mask=mask)
        mask = (eyes == [0, 0, 0]).all(axis=2)
        eyes[mask] = [255, 255, 255]
        mid = (shape[42][0] + shape[39][0]) // 2
        eyes_gray = cv2.cvtColor(eyes, cv2.COLOR_BGR2GRAY)
        threshold = 45#cv2.getTrackbarPos('threshold', 'image')
        _, thresh = cv2.threshold(eyes_gray, threshold, 255, cv2.THRESH_BINARY)
        thresh = cv2.erode(thresh, None, iterations=2)
        thresh = cv2.dilate(thresh, None, iterations=4)
        thresh = cv2.medianBlur(thresh, 3)
        thresh = cv2.bitwise_not(thresh)
        for (x, y) in shape[36:42]:
            cv2.circle(img, (x, y), 2, (0, 255, 0), -1)
            leftXSum += x
            leftYSum += y
        for (x, y) in shape[42:48]:
            cv2.circle(img, (x, y), 2, (0, 255, 0), -1)
            rightXSum += x
            rightYSum += y
        leftMidX = leftXSum / 6
        leftMidY = leftYSum / 6
        rightMidX = rightXSum / 6
        rightMidY = rightYSum / 6
        contour(thresh[:, 0:mid], mid, img)
        contour(thresh[:, mid:], mid, img, True)

    return(img)

while(True):
    ret, img = cap.read()
    img = detectEyes(img)
        
    cv2.imshow("eyes", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()

