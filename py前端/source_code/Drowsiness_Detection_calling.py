from flask import Flask, render_template, Response, redirect, url_for, session, request
import cv2
import dlib
import numpy as np
from imutils import face_utils

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# 初始化dlib的面部检测器和面部地标预测器
detect = dlib.get_frontal_face_detector()
predict = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")

# 设置检测的灰度阈值
thresh = 125

# 验证用户是否已登录
def is_user_authenticated():
    return 'username' in session

# 检查用户是否登录，如果没有登录，则重定向到登录页面
@app.before_request
def require_login():
    if not is_user_authenticated() and request.endpoint and request.endpoint != 'login':
        return redirect(url_for('login'))

@app.route('/call')
def index():
    return render_template('call.html')

def detect_calling(frame):
    # 图像预处理
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    faces = detect(gray, 0)
    for face in faces:
        face_68_point = predict(gray, face)
        face_68_point = face_utils.shape_to_np(face_68_point)

        left_x = face_68_point[4, 0]
        left_y = face_68_point[4, 1]
        right_x = face_68_point[12, 0]
        right_y = face_68_point[12, 1]

        # 调整检测区域大小和位置
        k = 1.5
        length = 80
        top1 = max(0, left_y - length)
        bottom1 = min(gray.shape[0], left_y + length)
        left1 = max(0, left_x - int(k * length))
        right1 = min(gray.shape[1], left_x)

        top2 = max(0, right_y - length)
        bottom2 = min(gray.shape[0], right_y + length)
        left2 = max(0, right_x)
        right2 = min(gray.shape[1], right_x + int(k * length))

        region1 = gray[top1:bottom1, left1:right1]
        region2 = gray[top2:bottom2, left2:right2]

        mean_left = np.sum(region1) / (right1 - left1) / (bottom1 - top1)
        mean_right = np.sum(region2) / (right2 - left2) / (bottom2 - top2)

        if mean_left > thresh:
            cv2.rectangle(frame, (left1, top1), (right1, bottom1), (0, 255, 0), 3)
            cv2.putText(frame, "calling", (left1, top1 - 15), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2)
        elif mean_right > thresh:
            cv2.rectangle(frame, (left2, top2), (right2, bottom2), (0, 255, 0), 3)
            cv2.putText(frame, "calling", (left2, top2 - 15), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "not calling", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2)

    return frame

def gen_frames():
    cap = cv2.VideoCapture(0)  # 使用摄像头进行实时检测
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            frame = detect_calling(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True, port=5002)
