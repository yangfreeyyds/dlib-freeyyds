from flask import Flask, render_template, Response, redirect, url_for, session, request
import cv2
from imutils import face_utils
import dlib
import numpy as np

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# 验证用户是否已登录
def is_user_authenticated():
    return 'username' in session

# 检查用户是否登录，如果没有登录，则重定向到登录页面
@app.before_request
def require_login():
    if not is_user_authenticated() and request.endpoint and request.endpoint != 'login':
        return redirect(url_for('login'))

def mouthAspectRatio(mouth):
    A = np.linalg.norm(mouth[2] - mouth[10])
    B = np.linalg.norm(mouth[4] - mouth[8])
    C = np.linalg.norm(mouth[0] - mouth[6])
    mar = (A + B) / (2.0 * C)
    return mar

thresh = 0.54
detect = dlib.get_frontal_face_detector()
predict = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")
(mouth_start, mouth_end) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

def detect_mouth(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detect(gray, 0)
    for face in faces:
        face_68_point = predict(gray, face)
        face_68_point = face_utils.shape_to_np(face_68_point)

        mouth = face_68_point[mouth_start:mouth_end]
        mar = mouthAspectRatio(mouth)

        left = mouth[0, 0]
        right = mouth[6, 0]
        top = mouth[3, 1]
        bottom = mouth[9, 1]

        cv2.rectangle(frame, (left-20, top-40), (right+20, bottom+20), (0, 255, 0), 3)

        if mar < thresh:
            cv2.putText(frame, "mouth close", (left, top-15),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "mouth open", (left, top-15),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2)

    return frame

def gen_frames():
    cap = cv2.VideoCapture(0)  # 使用摄像头进行实时检测
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            frame = detect_mouth(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/mouth')
def index():
    return render_template('mouth.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
