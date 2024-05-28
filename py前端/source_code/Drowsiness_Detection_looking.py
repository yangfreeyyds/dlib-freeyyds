from flask import Flask, render_template, Response, redirect, url_for, session, request
from imutils import face_utils
from scipy.spatial import distance
import dlib
import cv2
import mysqlconnectt

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

detect = dlib.get_frontal_face_detector()
predict = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")

# 验证用户是否已登录
def is_user_authenticated():
    return 'username' in session

# 检查用户是否登录，如果没有登录，则重定向到登录页面
@app.before_request
def require_login():
    if not is_user_authenticated() and request.endpoint and request.endpoint != 'login':
        print(1)
        return redirect(url_for('login'))

# Function to detect eye movement
def detect_eye_movement(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detect(gray, 0)
    sum = int(0)
    if len(faces) == 0:
        return "looking around"
    else:
        for face in faces:
            face_68_point = predict(gray, face)
            face_68_point = face_utils.shape_to_np(face_68_point)
            dx_r = abs(face_68_point[39][0] - face_68_point[27][0])
            dx_l = abs(face_68_point[42][0] - face_68_point[27][0])
            sum = sum + 1
            if dx_r / dx_l < 0.7:
                return "looking around"
            else:
                return "not looking around"

# Generator function to process video stream
def video_stream():
    cap = cv2.VideoCapture(0)  # 使用摄像头进行实时检测
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        status = detect_eye_movement(frame)
        cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2)
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/look')
def index():
    return render_template('look.html')

@app.route('/video_feed')
def video_feed():
    return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True, port=5003)
