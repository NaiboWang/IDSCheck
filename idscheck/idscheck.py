import os
import sys
import socket


def get_ip():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    if ip[:2] != "10":
        return "172.17.0.1"
    else:
        return "10.10.0.1"


def cmd():
    args = sys.argv

    if len(args) == 1:
        status = os.system("curl http://"+get_ip()+":8080")
    elif args[-1] == "gpu":
        gpu()
    elif args[-1] == "top":
        status = os.system("curl http://"+get_ip()+":8080/top")
    elif args[-1] == "topall":
        status = os.system("curl http://"+get_ip()+":8080/top_all")
    elif args[-1] == "query":
        status = os.system("curl http://"+get_ip()+":8080/query")
    elif args[-1] == "notify":
        notify()
    else:
        print("Usage: ids [(Null)|top|topall|notify|query|gpu]")


def gpu():
    notify()

def notify():
    print("Do you really want to notify other users to free up GPU resources? (y/n): ", end="")
    ans = input()
    if ans == "y":
        status = os.system("curl http://"+get_ip()+":8080/gpu_notify")


def top():
    status = os.system("curl http://"+get_ip()+":8080/top")


def topall():
    status = os.system("curl http://"+get_ip()+":8080/top_all")


def query():
    status = os.system("curl http://"+get_ip()+":8080/query")

if __name__ == "__main__":
    cmd()