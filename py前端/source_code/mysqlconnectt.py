import pymysql

def mysqlconn():
    # 连接到 MySQL 数据库
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="123456",
        database="free"
    )
    return conn

