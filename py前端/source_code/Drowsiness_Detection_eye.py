import dlib
from flask import Flask, render_template, Response, redirect, url_for, session, request
import cv2
from imutils import face_utils
from scipy.spatial import distance
import mysqlconnectt

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

def eyeAspectRatio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# Threshold for eye closure
thresh = 0.25

# Load the face detector and facial landmark predictor
detect = dlib.get_frontal_face_detector()
predict = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")

# Define the indices for left and right eye
(l_eye_start, l_eye_end) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
(r_eye_start, r_eye_end) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]

# 验证用户是否已登录
def is_user_authenticated():
    return 'username' in session

# 检查用户是否登录，如果没有登录，则重定向到登录页面
@app.before_request
def require_login():
    if not is_user_authenticated() and request.endpoint and request.endpoint != 'login':
        return redirect(url_for('login'))

# Function to detect eyes
def detect_eyes():
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detect(gray, 0)

        for face in faces:
            # Detect facial landmarks
            face_68_point = predict(gray, face)
            face_68_point = face_utils.shape_to_np(face_68_point)

            # Extract left and right eye regions
            left_eye = face_68_point[l_eye_start:l_eye_end]
            right_eye = face_68_point[r_eye_start:r_eye_end]

            # Calculate eye aspect ratio for each eye
            left_EAR = eyeAspectRatio(left_eye)
            right_EAR = eyeAspectRatio(right_eye)
            ear = (left_EAR + right_EAR) / 2.0

            # Draw rectangle around face
            left = face.left()
            top = face.top()
            right = face.right()
            bottom = face.bottom()
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            # Determine if eyes are open or closed based on threshold
            if ear < thresh:
                cv2.putText(frame, "eye close", (left, top - 15), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2)
            else:
                cv2.putText(frame, "eye open", (left, top - 15), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2)

        # Convert frame to JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/eye')
def index():
    return render_template('eye.html')


@app.route('/video_feed')
def video_feed():
    return Response(detect_eyes(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)
