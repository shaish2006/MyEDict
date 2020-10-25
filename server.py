import pymysql
import time
import socket
import os
import sys
import signal


# 执行mysql命令
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
        # print("数据库连接成功")
    except(Exception):
        print("数据库连接失败，2秒后重试")
        time.sleep(2)

    cursor = db.cursor()
    cursor.execute(sql)
    # col = cursor.description
    result = cursor.fetchall()
    # 将结果转化为dateFrame
    db.commit()
    db.close()
    return result

# 注册
def singup(c, user, password):
    sql = """select * from userInfo where name = "%s";""" % user
    result = execute_sql(sql)
    print(result)
    if len(result) >= 1:
        print(user + "用户名已存在！")
        c.send('0 用户名已存在！'.encode())
        return 0
    else:
        # 用户表中添加用户
        sql = """insert into userInfo (name,password) values("%s","%s");\
              """ % (user, password)
        execute_sql(sql)
        # 历史记录表格中增加用户
        sql = """insert into history (name,words) values("%s","");\
              """ % user
        execute_sql(sql)
        msg = '1 用户<%s>注册并登录成功！' % user
        c.send(msg.encode())
        return user

# 登录
def login(c, user, password):
    sql = """select * from userInfo where name = "%s" and password = "%s";"""\
        % (user, password)
    result = execute_sql(sql)
    if len(result) == 1:
        print("<%s>登录成功！" % user)
        c.send('1 登录成功！'.encode())
        return user
    else:
        print("<%s>登录失败！" % user)
        c.send('0 用户名或密码错误，请重试！'.encode())
        return 0

# 查询
def lookup(word):
    sql = """select * from dictionary where words = "%s";""" % word
    result = execute_sql(sql)
    if len(result) == 1:
        return result[0]
    else:
        return 0

# 用户查询
def clientLookUp(c, user, word):
    result = lookup(word)
    sendString = ""

    if result == 0:
        sendString = '未找到单词<%s>' % word
    else:
        sendString = word + ":" + result[1]
        insertHistory(user, word)

    c.send(sendString.encode())

# 插入历史记录
def insertHistory(user, word):
    sql = """select * from history where name = "%s";""" % user
    result = execute_sql(sql)
    if len(result) == 1:
        words = result[0][1]
        wordsList = words.split(' ')
        if word not in wordsList:
            sql = """delete from history where name = "%s";""" % user
            execute_sql(sql)
            words = words + " " + word
            sql = """insert into history (name,words) values("%s","%s");\
              """ % (user, words)
            execute_sql(sql)
    elif len(result) == 0:
        sql = """insert into history (name,words) values("%s","%s");\
              """ % (user, word)
        execute_sql(sql)
    else:
        print("数据库中存在重复用户名:%s，请核查数据库！" % user)

# 查询历史记录
def findHistory(c, user):
    sql = """select * from history where name = "%s";""" % user
    result = execute_sql(sql)
    if len(result) == 1:
        words = result[0][1]
        c.send(words.encode())
    elif len(result) == 0:
        c.send("暂无历史记录：".encode())
    else:
        c.send(("数据库中存在重复用户名:%s，请联系管理员核查数据库！" % user).encode())

# 退出
def userQuit(s):
    pass

# 前台接待用户
def qiantai(s):
    # user = {}
    while True:
        c, addr = s.accept()

        pid = os.fork()
        if pid < 0:
            print("创建子进程失败！")
        elif pid == 0:
            client(c, addr)

# 接待每个用户
def client(c,addr):
    # 处理用户登录或注册请求
    while True:
        data = c.recv(1024).decode()
        if not data:
            c.close()
            os._exit()
        dataList = data.split(' ')
        user = 0
        if dataList[0] == 'SINGUP':
            print("收到注册请求！")
            user = singup(c, dataList[1], dataList[2])
        elif dataList[0] == 'LOGIN':
            print("收到登录请求！")
            user = login(c, dataList[1], dataList[2])
        elif dataList[0] == 'QUIT':
            c.send(b"OK")
            print('主机<%s,%s>退出!' % addr)
            c.close()
            os._exit(1)
        else:
            print("E001未识别的用户操作！")

        if user == 0:
            print("用户注册或登录失败，等待用户重试")
            continue
        else:
            # 处理用户查单词或注销请求
            while True:
                data = c.recv(1024).decode()
                dataList = data.split(' ')
                if dataList[0] == 'LOOKUP':
                    clientLookUp(c, user, dataList[1])
                elif dataList[0] == 'HISTORY':
                    findHistory(c, user)
                elif dataList[0] == 'LOGOUT':
                    c.send(b"OK")
                    print('用户<%s>注销!' % user)
                    break

# 内测用
def test():
    while True:
        word = input("输入要查找的单词:")
        if word == """###""":
            return
        result = lookup(word)
        if result == 0:
            print("未找到该单词%s" % word)
        else:
            print(result[0] + ":" + result[1])


    # result = login("测试员1", "feng")
    # if result == 1:
    #     print("登录成功!")
    # else:
    #     print("登录失败！")

    insertHistory("测试员1", "love")

# 主函数
def main():
    addr = ("0.0.0.0", 8875)
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)

    pid = os.fork()
    if pid < 0:
        sys.exit("创建进程失败！")
    elif pid == 0:
        qiantai(s)
        # sys.exit(3)
    else:
        test()
        os.kill(pid, signal.SIGKILL)
        sys.exit(2)



if __name__ == "__main__":
    main()


