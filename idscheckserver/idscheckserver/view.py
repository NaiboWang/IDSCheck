"""
User info management (login, register, check_login, etc)
"""
import socket
import random
import string
import os
import calendar
import datetime
from urllib import request
from django.http import HttpResponse
import json
from functools import wraps
from .dbconfig import *
from bson import json_util
import subprocess
from prettytable import PrettyTable
from django.core.cache import cache

import os


class TimeUtil(object):
    @classmethod
    def parse_timezone(cls, timezone):
        """
        解析时区表示
        :param timezone: str eg: +8
        :return: dict{symbol, offset}
        """
        result = re.match(r'(?P<symbol>[+-])(?P<offset>\d+)', timezone)
        symbol = result.groupdict()['symbol']
        offset = int(result.groupdict()['offset'])

        return {
            'symbol': symbol,
            'offset': offset
        }

    @classmethod
    def convert_timezone(cls, dt, timezone="+0"):
        """默认是utc时间，需要"""
        result = cls.parse_timezone(timezone)
        symbol = result['symbol']

        offset = result['offset']

        if symbol == '+':
            return dt + datetime.timedelta(hours=offset)
        elif symbol == '-':
            return dt - datetime.timedelta(hours=offset)
        else:
            raise Exception('dont parse timezone format')


def generate_timestamp():
    current_GMT = time.gmtime()
    # ts stores timestamp
    ts = calendar.timegm(current_GMT)

    current_time = datetime.datetime.utcnow()
    convert_now = TimeUtil.convert_timezone(current_time, '+8')
    # print("current_time:    " + str(convert_now))
    return str(convert_now)


def run_cmd(_cmd, request=None):
    """
    开启子进程，执行对应指令，控制台打印执行过程，然后返回子进程执行的状态码和执行返回的数据
    :param _cmd: 子进程命令
    :return: 子进程状态码和执行结果
    """
    p = subprocess.Popen(_cmd, shell=True, close_fds=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    _RunCmdStdout, _ColorStdout = [], '\033[1;35m{0}\033[0m'
    while p.poll() is None:
        line = p.stdout.readline().rstrip()
        if not line:
            continue
        _RunCmdStdout.append(line)
        print(_ColorStdout.format(line))
    last_line = p.stdout.read().rstrip()
    if last_line:
        _RunCmdStdout.append(last_line)
        print(_ColorStdout.format(last_line))
    _RunCmdReturn = p.wait()
    return _RunCmdReturn, b'\n'.join(_RunCmdStdout), p.stderr.read()


def insert_log(request, command_name):
    import socket
    # 获取本机计算机名称
    hostname = socket.gethostname()
    try:
        username = list(idscheck_servers.find(
            {"ip": request.META['REMOTE_ADDR'],
                "hostname": hostname,
             }))[-1]['username']
    except:
        username = "unknown"
    idscheck_logs.insert_one({
        "username": username,
        "hostname": hostname,
        "ip": request.META['REMOTE_ADDR'],
        "cmd": command_name,
        "time": generate_timestamp(),
    })


def query(request):
    hostname = socket.gethostname()
    userlist = list(idscheck_servers.find({"hostname": hostname}))
    output = PrettyTable(["Username", "Email Address"])
    # output.align["Value"] = 'l'
    for user in userlist:
        output.add_row([user['username'], user['email']])
    insert_log(request, 'query')
    return HttpResponse(output.get_string()+"\n")


def hello(request):
    code, stdout, stderr = run_cmd('nvidia-smi', request=request)
    # print('\nreturn:', code, '\nstdout:', stdout, '\nstderr:', stderr)
    lines = stdout.decode("utf-8") .split("\n")
    j = 0
    id_firstline = 0
    id_lastline = 0
    id_startline = 0
    for line in lines:
        if line.find("Processes:") >= 0:
            id_startline = j
            break
        j += 1
    print(id_startline)
    output_A = lines[:id_startline-1]
    lines = lines[id_startline:]
    j = 0
    for line in lines:
        if line.find("|=====") >= 0:
            print(j, line)
            id_firstline = j
        elif line.find("+----") >= 0:
            print(j, line)
            id_lastline = j
        j = j + 1
    print(id_firstline, id_lastline)
    processes = lines[id_firstline+1:id_lastline]
    hostname = socket.gethostname()
    userlist = list(idscheck_servers.find({"hostname": hostname}))
    output = PrettyTable(["GPUID", "PID", "Process Name",
                         "Used GPU Memory", "User", "Email Address"])
    output.align["GPUID"] = 'r'
    output.align["Used GPU Memory"] = 'r'
    GPUINFO = []
    for line in processes:
        content = ' '.join(line.split())
        parameters = content.split(" ")
        GPUINFO.append([parameters[1], parameters[4],
                       parameters[6], parameters[7]])
        c, std, err = run_cmd(
            'ps -p ' + parameters[4] + ' -o user', request=request)
        username = std.decode("utf-8").split("\n")[1]
        GPUINFO[-1].append(username)
        for user in userlist:
            if user['username'] == username:
                GPUINFO[-1].append(user['email'])
                break
    # print(GPUINFO)
    for info in GPUINFO:
        output.add_row(info)
    print(output)
    # code, stdout2, stderr = run_cmd(
    #     'top -b -n 1 | grep -v root', request=request)
    insert_log(request, 'idscheck')
    # print('\nreturn:', code, '\nstdout:', stdout, '\nstderr:', stderr)
    return HttpResponse("\n".join(output_A)+'\n\n' + output.get_string() + '\n')


def gpu(request):
    code, stdout, stderr = run_cmd('nvidia-smi', request=request)
    insert_log(request, 'gpu')
    # print('\nreturn:', code, '\nstdout:', stdout, '\nstderr:', stderr)
    return HttpResponse(stdout+b'\n')


def top_all(request):
    code, stdout, stderr = run_cmd('top -b -n 1', request=request)
    insert_log(request, 'top_all')
    # print('\nreturn:', code, '\nstdout:', stdout, '\nstderr:', stderr)
    return HttpResponse(b'Process Information:\nPID\tUSER\tPR\tNI\tVIRT\tRES\tSHR\tS\t%CPU\t%MEM\tTIME+\tCOMMAND\t\n' + stdout + b'\n')


def top(request):
    code, stdout, stderr = run_cmd(
        'top -b -n 1 | grep -v root', request=request)
    insert_log(request, 'top')
    # print('\nreturn:', code, '\nstdout:', stdout, '\nstderr:', stderr)
    return HttpResponse(b'Process Information:\nPID\tUSER\tPR\tNI\tVIRT\tRES\tSHR\tS\t%CPU\t%MEM\tTIME+\tCOMMAND\t\n' + stdout + b'\n')
