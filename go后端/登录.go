// backend.go

package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	_ "github.com/go-sql-driver/mysql"
)

// 数据库连接
var db *sql.DB

// 用户结构体
type User struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

func main() {
	// 连接到 MySQL 数据库
	var err error
	db, err = sql.Open("mysql", "root:123456@tcp(127.0.0.1:3306)/free")
	if err != nil {
		log.Fatal("Could not connect to the database:", err)
	}
	defer db.Close()

	// 初始化 HTTP 路由
	http.HandleFunc("/login", loginHandler)

	// 启动服务器
	log.Fatal(http.ListenAndServe(":5011", nil))
}

// 登录处理函数
func loginHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var user User
	err := json.NewDecoder(r.Body).Decode(&user)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	// 验证用户登录信息
	if authenticateUser(user.Username, user.Password) {
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, `{"message": "Login successful", "username": "%s"}`, user.Username)
	} else {
		w.WriteHeader(http.StatusUnauthorized)
		fmt.Fprint(w, `{"error": "Invalid username or password"}`)
	}
}

// 验证用户登录信息
func authenticateUser(username, password string) bool {
	var storedPassword string
	err := db.QueryRow("SELECT password FROM users WHERE username = ?", username).Scan(&storedPassword)
	if err != nil {
		if err == sql.ErrNoRows {
			return false // 用户不存在
		}
		log.Println("Error fetching password:", err)
		return false
	}

	// 验证密码
	return storedPassword == password
}
