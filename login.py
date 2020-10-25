import pymysql
import time


def execute_sql(sql):
    # 创建连接
    try:
        db = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='123456',
            db='EDict',
            charset='utf8')
        print("数据库连接成功")
    except(Exception):
        print("数据库连接失败，10秒后重试")
        time.sleep(1)

    cursor = db.cursor()
    cursor.execute(sql)
    col = cursor.description
    result = cursor.fetchall()
    # 将结果转化为dateFrame
    db.close()
    return result, col


# name = input("请输入用户名：")
name = "管理员"

sql = """select * from userInfo where name="%s";""" % name

result, col = execute_sql(sql)

if len(result) == 1:
    userInfo = result[0]
    print(userInfo[2])
    for i in range(5):
        password = input('请输入密码：')
        if password == userInfo[2]:
            print("登录成功!")
            break
        else:
            print('密码错误：')
    else:
        print("尝试次数过多，请稍后再试！")
        time.sleep(2)
else:
    print('用户名不存在，请重新输入！')

# password = input("请输入密码：")

# db2 = pymysql.connect(host='local',port=3306,name)

