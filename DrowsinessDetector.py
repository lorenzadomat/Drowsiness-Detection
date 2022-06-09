# IMPORTING LIBRARIES
import cv2
import mediapipe as mp
from datetime import datetime
from DrowsinessMonitor import States
from DrowsinessMonitor import DrowsinessMonitor
import numpy as np
import tensorflow as tf


# INITIALIZING OBJECTS
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
IMG_SIZE = 100


class DrowsinessDetector:

    def __init__(self):
        self.monitor = DrowsinessMonitor.instance()
        pass

    def runWithFaceMap(self):
        timestamp = datetime.timestamp(datetime.now())

        cap = cv2.VideoCapture(0)
        with mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5) as face_mesh:
            while cap.isOpened():
                # calculating frames per second
                frame_duration = datetime.timestamp(datetime.now()) - timestamp
                self.monitor.setFPS(1 / frame_duration)
                timestamp = datetime.timestamp(datetime.now())

                success, image = cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    # If loading a video, use 'break' instead of 'continue'.
                    continue

                # To improve performance, optionally mark the image as not writeable to
                # pass by reference.
                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = face_mesh.process(image)

                # Draw the face mesh annotations on the image.
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                if results.multi_face_landmarks:
                    for face_landmarks in results.multi_face_landmarks:
                        self.updateStates(face_landmarks)

                        mp_drawing.draw_landmarks(
                            image=image,
                            landmark_list=face_landmarks,
                            connections=mp_face_mesh.FACEMESH_FACE_OVAL,
                            connection_drawing_spec=mp_drawing_styles
                                .get_default_face_mesh_tesselation_style())
                # Flip the image horizontally for a selfie-view display.
                cv2.imshow('MediaPipe Face Mesh', cv2.flip(image, 1))
                if cv2.waitKey(5) & 0xFF == 27:
                    break

        cap.release()

    def runWithCNN(self):
        timestamp = datetime.timestamp(datetime.now())
        model = tf.keras.models.load_model('drowsinessEyeCnn.model')
        cap = cv2.VideoCapture(0)
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        iCounter = 0
        while cap.isOpened():

            frame_duration = datetime.timestamp(datetime.now()) - timestamp
            self.monitor.setFPS(1 / frame_duration)
            timestamp = datetime.timestamp(datetime.now())

            success, image = cap.read()

            grayFrame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            eyes = eye_cascade.detectMultiScale(grayFrame, 1.3, 5)
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(image, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 5)
                eye = grayFrame[ey:ey + eh, ex:ex + ew]
                resized_eye = cv2.resize(eye, (IMG_SIZE, IMG_SIZE))
                cv2.imshow('Eye', resized_eye)
                reshaped_eye = np.array(resized_eye).reshape(-1, IMG_SIZE, IMG_SIZE, 1)
                pred = model.predict(reshaped_eye)

                if (pred[0, 0] > 0.9):
                    self.monitor.setLeftEyeState(States.CLOSED)
                    self.monitor.setRightEyeState(States.CLOSED)
                    print('eyes closed')
                elif iCounter > 10:
                    self.monitor.setLeftEyeState(States.OPEN)
                    self.monitor.setRightEyeState(States.OPEN)
                    iCounter = 0
                else:
                    iCounter += 1
            cv2.imshow('Video Stream', image)

            if cv2.waitKey(5) & 0xFF == 27:
                break

    def updateStates(self, landmarks):
        self.monitor.setLeftEyeState(self.getLeftEyeState(landmarks.landmark))
        self.monitor.setRightEyeState(self.getRightEyeState(landmarks.landmark))
        self.monitor.setMouthState(self.getMouthState(landmarks.landmark))

    # distance between 386 and 374
    def getLeftEyeState(self, landmarks):
        if landmarks[374].y - landmarks[386].y < 0.005:
            return States.CLOSED
        return States.OPEN

    # distance between 159 and 144
    def getRightEyeState(self, landmarks):
        if landmarks[144].y - landmarks[159].y < 0.005:
            return States.CLOSED
        return States.OPEN

    # distance between 81 and 87
    def getMouthState(self, landmarks):
        if landmarks[87].y - landmarks[81].y > 0.07:
            return States.OPEN
        return States.CLOSED
