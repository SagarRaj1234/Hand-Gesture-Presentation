import os
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np

#variables
width, height = 1280, 720
folderPath="Presenation"


#camera setup
cap =cv2.VideoCapture(0)
cap.set(3,width)
cap.set(4,height)

# Get the list of presentation images
pathImages = sorted(os.listdir(folderPath),key=len)
print(pathImages)

#Variables
imgNumber=0
hs , ws =int(120*2), int(213*2)
gestureThreshold = 300
buttonPressed = False
buttonCounter = 0
buttonDelay = 30
annotations = [[]]  #its a empty list of list
annotationNumber = 0
annotationStart =False

#Hand Detector
detector = HandDetector(detectionCon=0.8 , maxHands=1)# (its show if 80% sure its hand then detect it, no of hand)


while True:
    # import Images
    success, img=cap.read()
    # flip image
    img = cv2.flip(img,1) # 1 - for horizontal, 0-> vertical
    pathFullImage = os.path.join(folderPath,pathImages[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)

    hands,img=detector.findHands(img,flipType=False)
    # its shows the line bet image
    cv2.line(img,(0,gestureThreshold),(width, gestureThreshold),(0,255,0),10)
    print(annotationNumber)

    if hands and buttonPressed is False:
        hand = hands[0] # it a list but here i only want one hand
        fingers = detector.fingersUp(hand) # it is a list
        cx, cy = hand['center']
        lmList = hand['lmList'] # landmark list

        # constrain values for easier drawing
        #indexFinger = lmList[8][0], lmList[8][1] #// this is using whole page for pointer so will shit to next line
        # converting one range to another using numpy for width and height
        xVal = int(np.interp(lmList[8][0], [width //2 ,width],[0,width]))
        yVal = int(np.interp(lmList[8][1],[150,height-150],[0,height]))
        indexFinger = xVal, yVal

        fingers[0] =1- fingers[0] # for handle case of flip type false for hand.
        print(fingers)

        if cy <= gestureThreshold: # if hand is at height of the face
           annotationStart = False
           # Gesture 1- Left
           if fingers == [1, 0, 0, 0, 0]:
               annotationStart = False
               print("Left")
               if imgNumber > 0:
                   buttonPressed = True
                   annotations = [[]]  # its a empty list of list
                   annotationNumber = 0

                   imgNumber -= 1

           # Gesture 2- Right
           if fingers == [0, 0, 0, 0, 1]:
               annotationStart = False
               print("Right")
               if imgNumber <len(pathImages)-1:
                  buttonPressed = True
                  annotations = [[]]  # its a empty list of list
                  annotationNumber = 0
                  imgNumber += 1

        #Gesture 3 - show Pointer
        if fingers == [0, 1, 1, 0, 0]:
            cv2.circle(imgCurrent, indexFinger, 12, (0,0,255),cv2.FILLED)
            annotationStart = False

        # Gesture 4 - Draw Pointer
        if fingers == [0, 1, 0, 0, 0]:
            if annotationStart is False: # doing for break the rel of two fig
                annotationStart = True
                annotationNumber +=1
                annotations.append([]) # if not wrote this line, there will be no list to call gives error
            cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)
            annotations[annotationNumber].append(indexFinger)
        else:
            annotationStart =False

        # Gesture 5 - Erase
        if fingers == [0, 1, 1, 1, 0]:
            if annotations:
                if annotationNumber>= 0:
                    annotations.pop()
                    annotationNumber-=1
                    buttonPressed =True
    else:
        annotationStart = False



    # Button Pressed iterations
    if buttonPressed:
        buttonCounter +=1
        if buttonCounter > buttonDelay:
            buttonCounter = 0
            buttonPressed =False

    for i in range(len(annotations)):
        for j in range(len(annotations[i])):
            if j !=0:
               cv2.line(imgCurrent,annotations[i][j - 1], annotations[i][j], (0, 0, 200), 12)


    #Adding webcam image on the slides
    imgSmall = cv2.resize(img,(ws,hs))
    h,w,_= imgCurrent.shape # _ -> color channel but not in used
    imgCurrent[0:hs, w-ws:w]=imgSmall

    cv2.imshow("image",img)
    cv2.imshow("slides", imgCurrent)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break


