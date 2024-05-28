# frontend.py

from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# 后端服务地址
backend_url = "http://localhost:5011"  # 后端服务的地址和端口


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 向后端服务发送登录请求
        response = requests.post(f"{backend_url}/login", json={'username': username, 'password': password})

        if response.status_code == 200:
            session['username'] = username  # 将用户名存储在 session 中
            return redirect(url_for('home'))  # 登录成功后重定向到 home 页面
        else:
            return 'Invalid username or password. Please try again.'

    return render_template('login.html')


@app.route('/home')
def home():
    username = session.get('username')  # 从 session 中获取用户名
    return render_template('home.html', username=username)  # 将用户名传递给 home.html 页面显示


if __name__ == '__main__':
    app.run(debug=True, port=5005)
