import pymysql
import time
import socket
import os, sys
import re


# 打印登录界面
def dengLuJieMian():
    print("*" * 12 + "欢迎使用电子词典" + "*" * 12)
    print("*" * 17 + "1.登录" + "*" * 17)
    print("*" * 17 + "2.注册" + "*" * 17)
    print("*" * 17 + "3.退出" + "*" * 17)

# 注册
def singup(consfd):
    while True:
        user = input("请输入用户名<0返回主界面>：")
        if user == '0':
            return 0

        while True:
            password = input("请输入密码<0返回主界面>：")
            if password == '0':
                return 0
            password1 = input("请重复密码：")
            if password == password1:
                break
            else:
                continue

        data = "SINGUP " + user + " " + password
        consfd.send(data.encode())
        recvdata = consfd.recv(1024).decode()
        revcList = recvdata.split(" ")
        if revcList[0] == "0":
            print(revcList[1])
        elif revcList[0] == "1":
            print(revcList[1])
            return user

# 登录
def login(consfd):
    while True:
        user = input("请输入用户名<0返回主界面>：")
        if user == '0':
            return 0
        password = input("请输入密码<0返回主界面>:")
        if password == '0':
            return 0

        data = "LOGIN " + user + " " + password
        consfd.send(data.encode())
        recvdata = consfd.recv(1024).decode()
        revcList = recvdata.split(" ")
        print(recvdata)
        if revcList[0] == '0':
            print(revcList[1])
        elif revcList[0] == '1':
            print(revcList[1])
            return user

# 退出
def quit(consfd):
    consfd.send(b"QUIT")
    data = consfd.recv(1024).decode()
    if data == "OK":
        consfd.close()

# 查询界面
def lookupJieMian(consfd, user):
    print("*" * 12 + "欢迎您:%s" % user + "*" * 12)
    print("""输入"###"注销返回登录界面!""")
    consfd.send("HISTORY".encode())
    history = consfd.recv(1024).decode()
    print("查询历史：" + history)

# 查询单词
def lookup(consfd, word):
    data = "LOOKUP " + word
    consfd.send(data.encode())
    data = consfd.recv(1024).decode()
    print(word + ":" + data)

# 注销
def logout(consfd):
    data = "LOGOUT"
    consfd.send(data.encode())
    datarecv = consfd.recv(1024).decode()
    print("成功注销！返回登录界面！")


# 主函数
def main():
    addr = ('127.0.0.1', 8875)
    consfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    consfd.connect(addr)

    while True:
        dengLuJieMian()
        key = input("请选择：")
        if key == '1':
            user = login(consfd)
            if user == 0:
                continue
        elif key == '2':
            user = singup(consfd)
            if user == 0:
                continue
        elif key == "3":
            print("准备退出！")
            quit(consfd)
            os._exit(1)
        else:
            print("输入有误，请重新输入！")
            continue

        # 登录成功 开始查单词
        lookupJieMian(consfd, user)
        while True:
            word = input("输入查询的单词>>")
            if word == "###":
                logout(consfd)
                break
            else:
                lookup(consfd, word)





if __name__ == "__main__":
    main()