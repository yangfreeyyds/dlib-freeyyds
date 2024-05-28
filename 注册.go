package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	_ "github.com/go-sql-driver/mysql"
)

// 数据库连接
var db *sql.DB

// 用户结构体
type User struct {
	Username string `json:"username"`
	Password string `json:"password"`
	Email    string `json:"email"`
}

func main() {
	// 连接到 MySQL 数据库
	var err error
	db, err = sql.Open("mysql", "root:123456@tcp(127.0.0.1:3306)/free")
	if err != nil {
		log.Fatal("Could not connect to the database:", err)
	}
	defer db.Close()

	// 初始化 Gin 引擎
	router := gin.Default()

	// 注册用户路由
	router.POST("/register", registerHandler)

	// 启动服务器
	router.Run(":8080")
}

// 注册用户处理函数
func registerHandler(c *gin.Context) {
	var user User
	if err := c.ShouldBindJSON(&user); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// 在这里执行用户注册逻辑
	if registerUser(user.Username, user.Password, user.Email) {
		c.JSON(http.StatusOK, gin.H{"message": "User registered successfully"})
	} else {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to register user"})
	}
}

// 用户注册函数
func registerUser(username, password, email string) bool {
	// 在这里执行用户注册的数据库操作，返回注册是否成功的结果
	_, err := db.Exec("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", username, password, email)
	if err != nil {
		fmt.Println("Failed to insert user into database:", err)
		return false
	}
	return true
}
