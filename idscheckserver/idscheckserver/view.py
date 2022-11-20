# -*- coding: utf-8 -*-
"""
User info management (login, register, check_login, etc)
"""
import socket
import random
import string
import calendar
import datetime
from urllib import request
from django.http import HttpResponse
import json
from functools import wraps
from bson import json_util
import subprocess
from prettytable import PrettyTable
from django.core.cache import cache
import socket
from threading import Timer
import sys
import os
import time
import re
import subprocess

# USERLISTS = []
try:
    from .dbconfig import *
    from .Mail import Sample
except:
    pass

print("当前路径:", os.getcwd())

try:
    with open('idscheck_servers.json', 'r') as f:
        USERLISTS = json.load(f)
        print("USERLISTS", USERLISTS)
        f.close()
except:
    with open('/home/techsupport/idscheckserver/idscheck_servers.json', 'r') as f: # for crontab, need to add path
        USERLISTS = json.load(f)
        print("USERLISTS", USERLISTS)
        f.close()

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

def record_log(info):
    print(info)
    with open('server.log', 'a') as f:
        f.write(info + '\n')
        f.close()


def find(arr, conditions):
    def func(x):
        for k, v in conditions.items():
            if x[k] != v:
                return False
        return True
    return list(filter(func, arr))

def generate_timestamp():
    current_GMT = time.gmtime()
    # ts stores timestamp
    ts = calendar.timegm(current_GMT)

    current_time = datetime.datetime.utcnow()
    convert_now = TimeUtil.convert_timezone(current_time, '+8')
    # print("current_time:    " + str(convert_now))
    return str(convert_now)


def run_cmd(_cmd, request=None):
    # print("USERLISTS:", USERLISTS)
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


def insert_log(request, command_name, output):
    username = "unknown"
    email = "982311099@qq.com"
    nickname = "unknown"
    # 获取本机计算机名称
    hostname = socket.gethostname()
    # try:
    #     username_info = list(idscheck_servers.find(
    #         {"ip": request.META['REMOTE_ADDR'],
    #             "hostname": hostname,
    #         }))[-1]
    # except:
    #     record_log("query_log: " + username + " " + hostname)
    username_info = find(USERLISTS, {"ip": request.META['REMOTE_ADDR'],
                                            "hostname": hostname,
                                            })[-1]
    try:
        username = username_info['username']
        nickname = username_info['nickname']
        email = username_info['email']
    except:
        username = "unknown"
        email = "982311099@qq.com"
        nickname = "unknown"
    try:
        idscheck_logs.insert_one({
            "username": username,
            "hostname": hostname,
            "ip": request.META['REMOTE_ADDR'],
            "cmd": command_name,
            "time": generate_timestamp(),
            "output": output,
        })
    except:
        record_log("insert_log: " + username + " " + hostname)
        with open('idscheck_logs.log', 'a') as f:
            f.write(json.dumps({
                "username": username,
                "hostname": hostname,
                "ip": request.META['REMOTE_ADDR'],
                "cmd": command_name,
                "time": generate_timestamp(),
            }))
            f.close()
    return email, nickname


def query(request):
    # hostname = socket.gethostname()
    # userlist = list(idscheck_servers.find({"hostname": hostname}))
    # output = PrettyTable(["Username", "Email Address"])
    # # output.align["Value"] = 'l'
    # for user in userlist:
    #     output.add_row([user['username'], user['email']])
    # insert_log(request, 'query', output.get_string().split("\n"))
    # # return HttpResponse(output.get_string()+"\n")
    return HttpResponse('Please contact: naibowang@comp.nus.edu.sg or idsychs@nus.edu.sg to get further help (such as you want someone to free their GPUs for you.)\n')


def get_gpu_info():
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
    output_A = lines[1:id_startline-1]
    output_A.insert(0, generate_timestamp() + " GMT+8")
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
    # try:
    #     userlist = list(idscheck_servers.find({"hostname": hostname}))
    # except:
    #     record_log("get_gpu_info: " + hostname)
    userlist = find(USERLISTS, {"hostname": hostname})
    print("userlist", userlist)
    output = PrettyTable(["GPUID", "User", 
                         "Used GPU Memory", "Process Name", "PID"])
    output.align["GPUID"] = 'r'
    output.align["Used GPU Memory"] = 'r'
    GPUINFO = []
    GPU_REAl = []
    for line in processes:
        if line.find("No running") >= 0:
            return_results = "\n".join(output_A)+'\n\n'
            return return_results, GPU_REAl
        else:
            content = ' '.join(line.split())
        print("content", content)
        parameters = content.split(" ")
        GPUINFO.append([parameters[1], parameters[7],
                       parameters[6], parameters[4]])
        GPU_REAl.append([parameters[1], parameters[7],
                        parameters[6], parameters[4]])
        c, std, err = run_cmd(
            'ps -p ' + parameters[4] + ' -o user', request=request)
        print(c, std, err)
        username = std.decode("utf-8").split("\n")[1]
        # GPUINFO[-1].insert(1, username)
        for user in userlist:
            if user['username'] == username:
                GPUINFO[-1].insert(1, user['nickname'])
                GPU_REAl[-1].insert(1, user['nickname'])
                GPU_REAl[-1].insert(2, user['email'])
                GPU_REAl[-1].insert(3, username)
                break
    # print(GPUINFO)
    for info in GPUINFO:
        output.add_row(info)
    print(output)
    # code, stdout2, stderr = run_cmd(
    #     'top -b -n 1 | grep -v root', request=request)
    return_results = "\n".join(output_A)+'\n\n' + output.get_string() + '\n'
    return return_results, GPU_REAl

def hello(request):
    return_results, _ = get_gpu_info()
    insert_log(request, 'idscheck', return_results.split("\n"))
    # print('\nreturn:', code, '\nstdout:', stdout, '\nstderr:', stderr)
    return HttpResponse(return_results)

def real_gpu(request):
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
    output_A = lines[1:id_startline-1]
    output_A.insert(0, generate_timestamp() + " GMT+8")
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
    # try:
    #     userlist = list(idscheck_servers.find({"hostname": hostname}))
    # except:
    #     record_log("real_gpu: " + hostname)
    userlist = find(USERLISTS, {"hostname": hostname})
    output = PrettyTable(["GPUID", "User", "Email Address"
                         "Used GPU Memory", "Process Name", "PID"])
    output.align["GPUID"] = 'r'
    output.align["Used GPU Memory"] = 'r'
    GPUINFO = []
    for line in processes:
        content = ' '.join(line.split())
        parameters = content.split(" ")
        GPUINFO.append([parameters[1], parameters[7],
                       parameters[6], parameters[4]])
        c, std, err = run_cmd(
            'ps -p ' + parameters[4] + ' -o user', request=request)
        username = std.decode("utf-8").split("\n")[1]
        GPUINFO[-1].insert(1, username)
        for user in userlist:
            if user['username'] == username:
                GPUINFO[-1].insert(2, user['email'])
                break
    # print(GPUINFO)
    for info in GPUINFO:
        output.add_row(info)
    print(output)
    # code, stdout2, stderr = run_cmd(
    #     'top -b -n 1 | grep -v root', request=request)
    return_results = "\n".join(output_A)+'\n\n' + output.get_string() + '\n'
    insert_log(request, 'idscheck', return_results.split("\n"))
    # print('\nreturn:', code, '\nstdout:', stdout, '\nstderr:', stderr)
    return HttpResponse(return_results)

def gpu(request):
    return HttpResponse("Your tool is outdated, please update your tool to the latest version with the following command: \npip3 install idscheck --upgrade\n")

def get_notify_users(request=None):
    hostname = socket.gethostname()
    if request is not None:
        print(request.META['REMOTE_ADDR'], hostname)
        # try:
        #     username_info = list(idscheck_servers.find(
        #                 {"ip": request.META['REMOTE_ADDR'],
        #                     "hostname": hostname,
        #                 }))[-1]
        # except:
        #     record_log("get_notify_users: " + hostname)
        username_info = find(USERLISTS, {"ip": request.META['REMOTE_ADDR'],
                                            "hostname": hostname})[-1]
        nickname = username_info['nickname']
    else:
        nickname = "unknown"
    _, GPU_REAl = get_gpu_info()
    # print(GPU_REAl)
    userList = {}
    all_occupied_gpus = []
    for userinfo in GPU_REAl:
        if float(userinfo[4].split("M")[0]) > 1000:
            all_occupied_gpus.append(int(userinfo[0]))
            if userinfo[1] not in userList:
                userList[userinfo[1]] = [userinfo]
            else:
                userList[userinfo[1]].append(userinfo)
    print(userList)
    all_occupied_gpus = list(set(all_occupied_gpus))

    user_GPU = {}
    
    for user in userList:
        user_GPU_info = userList[user]
        for gpu_info in user_GPU_info:
            if gpu_info[1] not in user_GPU:
                user_GPU[gpu_info[1]] = [gpu_info[0]]
            else:
                if gpu_info[0] not in user_GPU[gpu_info[1]]:
                    user_GPU[gpu_info[1]].append(gpu_info[0])
    print("user_GPU", user_GPU)
    notify_users = set()
    user_current_GPUS = set()
    for user in user_GPU:
        print(user, user_GPU[user])
        if len(user_GPU[user]) > 2:
            notify_users.add((userList[user][0][1], userList[user][0][2], userList[user][0][3]))
        if user == nickname:
            user_current_GPUS = set(user_GPU[user])
    
    print("notify_users", notify_users)
    print("user_current_GPUS", user_current_GPUS)

    if hostname.find("2") >=0:
        gpus = set([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])
    else:
        gpus = set([0,1,2,3,4,5,6,7])

    avaiable_gpus = list(gpus - set(all_occupied_gpus))

    print("all_occupied_gpus", all_occupied_gpus)
    print("avaiable_gpus", avaiable_gpus)
    if len(avaiable_gpus) + len(user_current_GPUS) < 2:
        notify = True
    else:
        notify = False
    # notify = False
    notify_users = list(notify_users)
    return notify, notify_users, avaiable_gpus

def gpu_notify(request):
    # code, stdout, stderr = run_cmd('nvidia-smi', request=request)
    # insert_log(request, 'gpu', stdout.decode("utf-8").split("\n"))
    hostname = socket.gethostname()
    bcc_email, bcc_nickname = insert_log(request, 'notify', 'notify')
    # print('\nreturn:', code, '\nstdout:', stdout, '\nstderr:', stderr)
    # return HttpResponse(stdout+b'\n')
    notify, notify_users, avaiable_gpus = get_notify_users(request)

    if notify:
        for notify_user in notify_users:
            print(notify_user[0], notify_user[1])    
            nickname = notify_user[0]
            server_address = hostname + ".d2.comp.nus.edu.sg"
            msg = """<p>(This is an automatically generated email by the program, <b>not Naibo himself</b> wants to kill your processes, but <b>some other user submit a request to the system that want you to free your resources</b>, please note. <b>You can reply to this email</b> if you have any questions.)</p><p>
            Dear {nickname} (your nickname, if you want to change it, just reply to this email),
            </p><p>
            We have detected that you are using more than 2 GPUs at server <b>{server_address}</b> which affects someone else to use the GPU resources. Thus, we have received other users' requests that need you to free your GPU resources for them to use.
            </p><p>
            Therefore, please close your processes within 24 hours to make sure that <b>you leave at least 2 GPUs for other users to use</b>, otherwise we <b>will kill all your processes after 24 hours</b>. 
            </p><p>
            You can use <b>"ids"</b> command to check the GPU utilization, use <b>"idstop"</b> command to check the CPU utilization, and use <b>"idsgpu"</b> or <b>"idsnotify"</b> command to notify all other user(s) who occupied more than 2 GPUs currently (if not installed, please install to use the commands: <b>pip3 install idscheck</b>).
            </p><p>
            These are the rules of IDS GPU usage:
            </p><p>
            1.	In principle, everyone can use <b>UP TO 2 GPUs (process which occupied more than 1GB GPU memory is considered a task of GPU usage) </b> at your server (such as idsd-2, idsd-3, idsd-4), and please <b>put all your processes into these 2 GPUs </b> if you have more than 2 tasks that need to use GPU and occupy GPU memory.
            </p><p>
            2.	However, you can use more than 2 GPUs if you found that some GPU(s) are empty (nobody is using it), but you should note that <b>as long as some other users need to use GPU but less than 2 GPUs available</b>, they have the right to use the "idsgpu" or "idsnotify" command to ask Sam/Naibo to <b>kill the additional processes you are running</b>.
            </p><p>
            3. If you really need to use more than 2 GPUs (such as <b>you are now meeting a paper deadline</b>), please <b>reply to this email</b> to contact Naibo to explain your situation and <b>tell us when will these GPUs be available</b> and we will let the user who also needs GPUs know your situation and we can then negotiate.
            </p><p>
            4.	If nobody uses more than 2 GPUs but you still can not get any GPUs, please contact Sam or Naibo for future help.
            <p>
            Thank you very much for your cooperation, if you have any questions, please contact <b>idsychs@nus.edu.sg (Sam)</b> or <b>naibowang@comp.nus.edu.sg (Naibo)</b>.
            </p><p>
            Sincerely,
            </p><p>
            Naibo Wang
            <br/>
            Ph.D. Student, Assistant Server Manager of Institute of Data Science
            <br/>
            National University of Singapore
            </p>
            """.format(nickname=nickname, server_address=server_address)
            email_address = notify_user[1]
            Sample.main("Please free your GPU resources at %s server for other users" % hostname, msg, email_address, bcc_email)
            idscheck_tasks.insert_one({"nickname": notify_user[0], "email": email_address, "bcc_nickname": bcc_nickname,"bcc_email": bcc_email, "server": hostname, "time": datetime.datetime.now(),  "final_handle_time": datetime.datetime.now() + datetime.timedelta(hours=24), "Status": "Pending"})
        return HttpResponse('Notification has already sent to all users occupied more than two GPUs and also Bcc you (they will not know that it is you who submit this request, don\'t worry).\n')
    else:
        if len(avaiable_gpus) < 2:
            return HttpResponse('You are already using at least two GPUs (or you are using one GPU and another one GPU is available) now, therefore no notification is needed.\n')
        else:
            return HttpResponse('Still at least two GPUs (ID: %s) available now, therefore no notification is needed.\n' % avaiable_gpus)

def top_all(request):
    code, stdout, stderr = run_cmd('top -b -n 1', request=request)
    # output = b'Process Information:\nPID\tUSER\tPR\tNI\tVIRT\tRES\tSHR\tS\t%CPU\t%MEM\tTIME+\tCOMMAND\t\n' + stdout + b'\n'
    # insert_log(request, 'top_all', output.decode("utf-8").split("\n"))
    output = b'Process Information:\nPID\tUSER\tPR\tNI\tVIRT\tRES\tSHR\tS\t%CPU\t%MEM\tTIME+\tCOMMAND\t\n' + stdout + b'\n'
    lines = stdout.decode("utf-8") .split("\n")
    j = 0
    id_firstline = 0
    id_lastline = 0
    id_startline = 0
    for line in lines:
        if line.find("PID USER") >= 0:
            id_startline = j
            break
        j += 1
    print(id_startline)
    output_A = lines[:id_startline-1]
    output_A.insert(0, generate_timestamp() + " GMT+8")
    lines = lines[id_startline:]
    output_B = ""
    j = 0
    for line in lines:
        parameters = line.split(" ")
        for i in range(len(parameters)):
            if parameters[i] != '':
                username = parameters[i+1]
                parameters[i+1] = "anynomous_user"
                break
        output = " ".join(parameters)
        print(output)
        output_B += output + "\n"
        
    return_results = "\n".join(output_A)+'\n' + output_B + '\n'
    insert_log(request, 'top_all', return_results)
    # print('\nreturn:', code, '\nstdout:', stdout, '\nstderr:', stderr)
    return HttpResponse(return_results)
    # print('\nreturn:', code, '\nstdout:', stdout, '\nstderr:', stderr)
    # return HttpResponse(output)


def top(request):
    code, stdout, stderr = run_cmd(
        'top -b -n 1 | grep -v root', request=request)
    output = b'Process Information:\nPID\tUSER\tPR\tNI\tVIRT\tRES\tSHR\tS\t%CPU\t%MEM\tTIME+\tCOMMAND\t\n' + stdout + b'\n'
    lines = stdout.decode("utf-8") .split("\n")
    j = 0
    id_firstline = 0
    id_lastline = 0
    id_startline = 0
    for line in lines:
        if line.find("PID USER") >= 0:
            id_startline = j
            break
        j += 1
    print(id_startline)
    output_A = lines[:id_startline-1]
    output_A.insert(0, generate_timestamp() + " GMT+8")
    lines = lines[id_startline:]
    output_B = ""
    j = 0
    for line in lines:
        parameters = line.split(" ")
        for i in range(len(parameters)):
            if parameters[i] != '':
                username = parameters[i+1]
                parameters[i+1] = "anynomous_user"
                break
        output = " ".join(parameters)
        print(output)
        output_B += output + "\n"
        
    return_results = "\n".join(output_A)+'\n' + output_B + '\n'
    insert_log(request, 'top', return_results)
    # print('\nreturn:', code, '\nstdout:', stdout, '\nstderr:', stderr)
    return HttpResponse(return_results)


def kill_zombie_tasks():
    code, stdout, stderr = run_cmd('nvidia-smi', request=request)
    # print('\nreturn:', code, '\nstdout:', stdout, '\nstderr:', stderr)
    lines = stdout.decode("utf-8") .split("\n")
    j = 0
    id_firstline = 0
    id_lastline = 0
    id_startline = 0
    GPUINFO = []
    PROCESSINFO = []
    i = 0
    for line in lines:
        if line.find("N/A") >= 0 and line.find("W") >= 0:
            GPUINFO.append([i, int(line.split("MiB")[0].split(" ")[-1]), int(line.split("MiB")[1].split(" ")[-1])])
            i += 1
        elif line.find("N/A  N/A") >=0:
            content = ' '.join(line.split())
            memory = int(line.split(" ")[-2].split("MiB")[0])
            pid = int(content.split(" ")[4])
            gpuid = int(content.split(" ")[1])
            PROCESSINFO.append([gpuid, pid, memory])

    zombie_tasks = []
    zombie_GPUs = []
    for GPU in GPUINFO:
        displayed_memory = 0
        for process in PROCESSINFO:
            if GPU[0] == process[0]:
                displayed_memory += process[2]
        if GPU[1] - displayed_memory > 5000: # Find zombie processes
            print("find zombie processes at GPU %d" % GPU[0])
            zombie_GPUs.append(GPU[0])
    print("zombie_GPUs", zombie_GPUs)
    # zombie_GPUs = [0,1,2,3,4,5,6,7]
    for GPU in zombie_GPUs:
        code, stdout, stderr = run_cmd('fuser -v /dev/nvidia'+str(GPU), request=request)
        lines = stderr.decode("utf-8").split("\n")[1:] # Note that stderr is used here
        # print("lines", lines)
        lines_out = stdout.decode("utf-8")
        lines_out = lines_out.split()
        # print("lines_out", lines_out)
        # print("stderr", stderr)
        # r = os.popen('fuser -v /dev/nvidia'+str(GPU))  
        # lines = r.read()
        # print("lines", lines) 
        # r.close()
        i = -1
        for line in lines:
            if line == '':
                continue
            i += 1
            # print("line", line)
            # print("lines_out", lines_out[i])
            if line.find("root") >= 0 or line.find("nvidia") >= 0 or line.find("USER") >= 0:
                continue
            else:
                content = ' '.join(line.split())
                # print(content)
                user = content.split(" ")[-3]
                pid = int(lines_out[i])
                zombie_tasks.append([GPU, user, pid])
    print("zombie_tasks", zombie_tasks)
    for task in zombie_tasks:
        # code, stdout, stderr = run_cmd('kill -9 '+str(task[2]), request=request)
        idscheck_zombie.insert_one({"GPU": task[0], "user": task[1], "pid": task[2], "time": generate_timestamp(), "server": hostname})
        print("kill -9 "+str(task[2]))
    # print(PROCESSINFO)
    

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    print(SCRIPT_DIR)
    sys.path.append(os.path.dirname(SCRIPT_DIR))
    from dbconfig import *
    from Mail import Sample
    myclient = pymongo.MongoClient(
    dbc, connect=False)
    mydb = myclient['ids']
    idscheck_logs = mydb["idscheck_logs"]
    idscheck_servers = mydb["idscheck_servers"]
    idscheck_tasks = mydb["idscheck_tasks"]
    idscheck_zombie = mydb["idscheck_zombie"]
    hostname = socket.gethostname()
    try:
        print("hostname", hostname)
        userInfo = list(idscheck_servers.find({"hostname": hostname}))
        print("userInfo", userInfo)
        with open("/home/techsupport/idscheckserver/idscheck_servers.json", "w") as f:
            json.dump(json.loads(json_util.dumps(userInfo)), f)
            f.close()
    except:
        print("No server info found, use local info")
    kill_zombie_tasks()
    try:
        notify, notify_users, avaiable_gpus = get_notify_users()
        all_tasks = list(idscheck_tasks.find({"Status": "Pending", "server": hostname}))
        # print(all_tasks)
        for task in all_tasks:
            print(task)
            bcc_email = task["bcc_email"]
            bcc_nickname = task["bcc_nickname"]
            email_address = task["email"]
            nickname = task["nickname"]
            server = task["server"]
            final_handle_time = task["final_handle_time"]
            server_address = hostname + ".d2.comp.nus.edu.sg"
            if len(avaiable_gpus) >= 2:
                msg = """<p style="font-size:16px">
                Dear <b>{nickname}</b> (your nickname, if you want to change it, just reply to this email),
                </p><p>
                We have detected that now at least 2 GPUs are available at server <b>{server_address}</b>, maybe it's your efforts to free GPUs, so <b>thank you</b>! And if it is not you who killed your processes, <b>you don't need to kill your processes to release GPUs any more</b>. You can continue to use the GPUs as you wish.
                </p><p></p><p style="font-size:16px">
                Dear <b>{bcc_nickname}</b> (your nickname, if you want to change it, just reply to this email),
                </p><p>
                We have detected that now at least 2 GPUs are available at server <b>{server_address}</b>, therefore you can use them now. 
                </p><p>
                If you still find that no GPUs are available, it's likely that not only you but also other users who wants to use GPUs are waiting for GPUs and they received the same email as you, so that they occupied the GPUs before you. <b>Under this condition, please reuse the "idsgpu" or "idsnotify" command to notify all users who occupied more than 2 GPUs again.</b> 
                </p><p>
                And if nobody uses more than 2 GPUs but you still can not get any GPUs, please contact Sam or Naibo for future help.
                <p>
                Thank you very much for your cooperation, if you have any questions, please contact <b>idsychs@nus.edu.sg (Sam)</b> or <b>naibowang@comp.nus.edu.sg (Naibo)</b>.
                </p><p>
                Sincerely,
                </p><p>
                Naibo Wang
                <br/>
                Ph.D. Student, Assistant Server Manager of Institute of Data Science
                <br/>
                National University of Singapore
                </p>
                """.format(nickname=nickname, server_address=server_address, bcc_nickname=bcc_nickname)
                Sample.main("Now at least 2 GPUs available at %s server" % hostname, msg, email_address, bcc_email)
                idscheck_tasks.update_one({"_id": task["_id"]}, {"$set": {"Status": "Finished"}})
            else:
                if task["final_handle_time"] < datetime.datetime.now():
                    msg = """<p style="font-size:16px">
                Dear <b>{nickname}</b> (your nickname, if you want to change it, just reply to this email),
                </p><p>
                We have already killed all of your processes at server <b>{server_address}</b>, therefore you need to restart your processes again and make sure that you will not use more than 2 GPUs at the same time.
                </p><p></p><p style="font-size:16px">
                Dear <b>{bcc_nickname}</b> (your nickname, if you want to change it, just reply to this email),
                </p><p>
                Now you can use the GPUs at server <b>{server_address}</b>, but please make sure that you will not use more than 2 GPUs at the same time.
                </p><p>
                If you still find that no GPUs are available, it's likely that not only you but also other users who wants to use GPUs are waiting for GPUs and they received the same email as you, so that they occupied the GPUs before you. <b>Under this condition, please reuse the "idsgpu" or "idsnotify" command to notify all users who occupied more than 2 GPUs again.</b> 
                </p><p>
                And if nobody uses more than 2 GPUs but you still can not get any GPUs, please contact Sam or Naibo for future help.
                <p>
                Thank you very much for your cooperation, if you have any questions, please contact <b>idsychs@nus.edu.sg (Sam)</b> or <b>naibowang@comp.nus.edu.sg (Naibo)</b>.
                </p><p>
                Sincerely,
                </p><p>
                Naibo Wang
                <br/>
                Ph.D. Student, Assistant Server Manager of Institute of Data Science
                <br/>
                National University of Singapore
                </p>
                """.format(nickname=nickname, server_address=server_address, bcc_nickname=bcc_nickname)
                    Sample.main("Your processes has already been killed at server %s" % hostname, msg, email_address, bcc_email)
                    return_results, GPU_REAl = get_gpu_info()
                    # print(GPU_REAl)
                    for gpu in GPU_REAl:
                        if gpu[1] == nickname:
                            pid = gpu[-1]
                            # pid = "860165"
                            cmd = "kill -9 %s" % pid
                            print(cmd)
                            os.system(cmd)
                    idscheck_tasks.update_one({"_id": task["_id"]}, {"$set": {"Status": "Finished"}})
                else:
                    print("Not time yet")
    except:
        record_log("Cannot connect to database, therefore cannot check tasks automatically") 
        