from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# 后端服务地址
backend_url = "http://localhost:8080"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # 发送注册请求到后端服务
        response = requests.post(f"{backend_url}/register", json={'username': username, 'password': password, 'email': email})

        if response.status_code == 200:
            print("User registered successfully")
            return redirect(url_for('login'))  # 注册成功后重定向到登录页面
        else:
            return 'Error: Registration failed.'

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 在这里处理用户登录逻辑
        pass

    return render_template('login.html')


if __name__ == '__main__':
    # create_user_table()  # 创建用户表，可以在 Go 后端中创建
    app.run(debug=True, port=5006)
