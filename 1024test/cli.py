"""1024test 客户端命令。

用法：
    1024test -m <user> <password>   创建用户
    1024test -l <user>              登录
    1024test -v                     查看版本
"""
import argparse
import socket
import sys

import config

VERSION = "1.0.0"


def connect(conf):
    return socket.create_connection(
        (conf.SERVER_HOST, conf.SERVER_PORT), timeout=5
    )


def send(sock, rfile, line):
    sock.sendall((line + "\n").encode("utf-8"))
    return rfile.readline().decode("utf-8").strip()


def main():
    parser = argparse.ArgumentParser(prog="1024test", description="1024test 客户端")
    parser.add_argument("-m", nargs=2, metavar=("USER", "PASSWORD"), help="创建用户")
    parser.add_argument("-l", nargs=1, metavar="USER", help="登录")
    parser.add_argument("-v", "--version", action="store_true", help="查看版本")
    args = parser.parse_args()

    conf = config.CONF
    try:
        sock = connect(conf)
    except OSError:
        print("无法执行")
        sys.exit(1)

    with sock:
        rfile = sock.makefile("rb")
        if args.m:
            username, password = args.m
            print(send(sock, rfile, f"REGISTER {username} {password}"))
        elif args.l:
            username = args.l[0]
            status = send(sock, rfile, f"CHECK {username}")
            if status == "EXISTS":
                print("password：", end="", flush=True)
                password = input()
                result = send(sock, rfile, f"LOGIN {username} {password}")
                print("logining" if result == "OK" else "密码错误")
            else:
                print("无该用户")
        elif args.v:
            resp = send(sock, rfile, "PING")
            print(f"1024test v{VERSION}" if resp == "PONG" else "无法执行")
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
