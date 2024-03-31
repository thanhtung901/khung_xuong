import cv2
import time, os
import math as m
import mediapipe as mp

import telebot
import yaml
import pyglet
from pyglet.gl import *
pyglet.options['audio'] = ('openal', 'directsound', 'silent')
def findDistance(x1, y1, x2, y2):
    dist = m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist

def findAngle(x1, y1, x2, y2):
    theta = m.acos((y2 - y1) * (-y1) / (m.sqrt(
        (x2 - x1) ** 2 + (y2 - y1) ** 2) * y1))
    degree = int(180 / m.pi) * theta
    return degree

def sendWarning(x):
    pass

font = cv2.FONT_HERSHEY_SIMPLEX

# Colors.
blue = (255, 127, 0)
red = (50, 50, 255)
green = (127, 255, 0)
dark_blue = (127, 20, 0)
light_green = (127, 233, 100)
yellow = (0, 255, 255)
pink = (255, 0, 255)

# Initialize mediapipe pose class.
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
# ===============================================================================================#
def play_audio(file_name):
    music = pyglet.resource.media(file_name)
    music.play()
if __name__ == "__main__":
    bot = telebot.TeleBot('6581858601:AAGG1ZRcQX5p41DfwvC1JqXxxE-oep1Dfss')
    with open("config.yaml", 'r') as yaml_file:
        data = yaml.safe_load(yaml_file)
    chat_id = data['chat_id']
    cap = cv2.VideoCapture(1)
    lm, lmPose = None, None
    b = 0 
    while cap.isOpened():
        a = time.time()
        success, images = cap.read()
        image = images.copy()
        if not success:
            print("Null.Frames")
            break
        h, w = image.shape[:2]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        keypoints = pose.process(image)

        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        lm = keypoints.pose_landmarks
        lmPose = mp_pose.PoseLandmark

        if lm is not None and lmPose is not None: 
            l_shldr_x = int(lm.landmark[lmPose.LEFT_SHOULDER].x * w)
            l_shldr_y = int(lm.landmark[lmPose.LEFT_SHOULDER].y * h)
            r_shldr_x = int(lm.landmark[lmPose.RIGHT_SHOULDER].x * w)
            r_shldr_y = int(lm.landmark[lmPose.RIGHT_SHOULDER].y * h)

            l_ear_x = int(lm.landmark[lmPose.LEFT_EAR].x * w)
            l_ear_y = int(lm.landmark[lmPose.LEFT_EAR].y * h)

            l_hip_x = int(lm.landmark[lmPose.LEFT_HIP].x * w)
            l_hip_y = int(lm.landmark[lmPose.LEFT_HIP].y * h)

            neck_inclination = findAngle(l_shldr_x, l_shldr_y, l_ear_x, l_ear_y)
            torso_inclination = findAngle(l_hip_x, l_hip_y, l_shldr_x, l_shldr_y)

            cv2.circle(image, (l_shldr_x, l_shldr_y), 7, yellow, -1)
            cv2.circle(image, (l_ear_x, l_ear_y), 7, yellow, -1)

            cv2.circle(image, (l_shldr_x, l_shldr_y - 100), 7, yellow, -1)
            cv2.circle(image, (r_shldr_x, r_shldr_y), 7, pink, -1)
            cv2.circle(image, (l_hip_x, l_hip_y), 7, yellow, -1)

            cv2.circle(image, (l_hip_x, l_hip_y - 100), 7, yellow, -1)
            # print('a===========', b)
            if neck_inclination < 40 and torso_inclination < 15:
                b=0
                cv2.putText(image, str(int(neck_inclination)), (l_shldr_x + 10, l_shldr_y), font, 0.9, light_green, 2)
                cv2.putText(image, str(int(torso_inclination)), (l_hip_x + 10, l_hip_y), font, 0.9, light_green, 2)

                cv2.line(image, (l_shldr_x, l_shldr_y), (l_ear_x, l_ear_y), green, 4)
                cv2.line(image, (l_shldr_x, l_shldr_y), (l_shldr_x, l_shldr_y - 100), green, 4)
                cv2.line(image, (l_hip_x, l_hip_y), (l_shldr_x, l_shldr_y), green, 4)
                cv2.line(image, (l_hip_x, l_hip_y), (l_hip_x, l_hip_y - 100), green, 4)

            else:
                b +=1
                cv2.putText(image, str(int(neck_inclination)), (l_shldr_x + 10, l_shldr_y), font, 0.9, red, 2)
                cv2.putText(image, str(int(torso_inclination)), (l_hip_x + 10, l_hip_y), font, 0.9, red, 2)

                # Join landmarks.
                cv2.line(image, (l_shldr_x, l_shldr_y), (l_ear_x, l_ear_y), red, 4)
                cv2.line(image, (l_shldr_x, l_shldr_y), (l_shldr_x, l_shldr_y - 100), red, 4)
                cv2.line(image, (l_hip_x, l_hip_y), (l_shldr_x, l_shldr_y), red, 4)
                cv2.line(image, (l_hip_x, l_hip_y), (l_hip_x, l_hip_y - 100), red, 4)
            if b==7:
                play_audio('example.mp3')
                filename ='images2.jpg'
                cv2.imwrite(filename, images)
                # print("written!")
                photo = open(filename, 'rb')
                bot.send_photo(chat_id, photo)
                photo.close()
                time.sleep(0.25)
                os.remove(filename)
                print("done!")
                time.sleep(0.25)
                play_audio('Example_Eng.mp3')
        else:
            pass

        cv2.imshow('MediaPipe Pose', image)
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
