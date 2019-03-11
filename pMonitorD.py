"""
uds:unix domain socket server
传递的json格式。4字节长度，后面跟着json。
示例请求json：
{"action":"start",jobid:"idxxx","cmd":"ls -l"} #返回{"action":"start","cmd":"ls -l","result":"success/fail"}。启动时不需有id，因为一个任务可能会启动、停止、启动，会对应多个pid
{"action":"jobs"} #返回所有子进程的状态 {"action":"jobs","lists":[{"pid":2221,"cmd":xxxx,"status":"stoped","returncode":1}]}
{"action":"kill","jobid":idxxx}  #返回{"action":"start","cmd":"ls -l","status":"success/fail"}

Daemon只负责启动进程、关闭进程。我需要一个GUI、一个进程树（daemon）。
GUI连接到daemon，daemon负责start、stop process。
只是文件名以D结尾，实际并没有类叫这个名。

应该以nohup启动
"""
import socket
import sys
import os
import threading
import errno as errnoM
import time
import json
from subprocess import Popen,TimeoutExpired
from datetime import datetime
from collections import OrderedDict
from constants import *

class ServerHandler:
  """处理server的recv"""
  def __init__(self,connection,server):
    """connection就是socket实例"""
    self.connection = connection
    self.server = server
    self.data = bytearray()
    self.shouldBreak = False

  def handle_recv(self):
    connection = self.connection
    try:
      while True:
        if self.shouldBreak:break
        data = connection.recv(1024)
        if len(data)==0:
          connection.close()
          return
        # print("received:", data)
        self.data.extend(data)
        self.parseData()
    finally:
      connection.close()
      print("connection closed",connection)

  @staticmethod
  def takeDataWithByteCount(data,bytecount):
    taken = data[:bytecount]
    remaining = data[bytecount:]
    return taken,remaining

  def parseData(self):
    while len(self.data)>=5:
      length,remaining = self.takeDataWithByteCount(self.data,4)
      length = int.from_bytes(length,byteorder='big')
      if length<len(remaining):
        #不够长度，返回
        return
      jsonBytes,remaining = self.takeDataWithByteCount(remaining,length)
      payload = json.loads(jsonBytes)
      print("解析到payload:",payload)
      self.handlePayload(payload)
      self.data = remaining

  def send_payload(self,payload:dict):
    payload = json.dumps(payload).encode()
    length = len(payload)
    length = length.to_bytes(4, byteorder='big')
    data = length + payload

    try:
      self.connection.sendall(data)
      print("ServerHandler send_msg success",data)
    except:
      print(sys.exc_info())
      print("ServerHandler send_msg fail",data)

  def handlePayload(self, payload:dict):
    action = payload['action']
    if hasattr(self.server.launcher,f'do_{action}'):
      getattr(self.server.launcher,f'do_{action}')(payload)
    else:
      payload['status'] = 'not implemented'

    self.send_payload(payload)


class UDS:
  """这个类，既可以做server，也可以做client"""
  def __init__(self,launcher,server_address=g_sockpath):
    self.launcher = launcher
    self.server_address = server_address
    self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

  def start_server(self):
    """bind和listen"""
    if os.path.exists(self.server_address):
      os.unlink(self.server_address)
    self.sock.bind(self.server_address)
    self.sock.listen(0) #backlog是积压个数

  def start_accept_loop(self,inThread=True):
    """默认在子线程中启动"""
    isMain = threading.current_thread() == threading.main_thread()
    if inThread and isMain:
      t = threading.Thread(target=self.start_accept_loop,args=[inThread])
      t.start()
      return
    if inThread:
      assert not isMain
    sock = self.sock
    while True:
      print("waiting for a connection")
      connection,client_address = sock.accept() #connection是一个新的socket
      print("connection from {}".format(client_address))
      ServerHandler(connection,self).handle_recv()



class Launcher:
  def __init__(self,logdir='logdir'):
    self.id2popen = OrderedDict()
    self.logdir = logdir

  def logpathFromJobid(self,jobid):
    datepart = datetime.now().strftime("%Y%m%d_%H_%M_%S")
    filename = f"{jobid}_{datepart}.log"
    logpath = os.path.join(self.logdir,filename)
    return logpath

  def do_start(self, payload):
    cmd = payload['cmd']
    jobid = payload['jobid']
    logpath = self.logpathFromJobid(jobid)
    assert cmd is not None and logpath is not None and jobid is not None

    f = open(logpath,'at')
    pobj = Popen(cmd,shell=True,stdout=f,stderr=f,bufsize=0)
    pobj.startAt = payload['startAt'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pobj.logpath = payload['logpath'] = logpath
    pobj.poll()
    if pobj.returncode is None:
      payload['result'] = JobStartResultSucc
    else:
      payload['result'] = JobStartResultFail
    self.id2popen[jobid] = pobj

  def do_jobs(self, payload):
    jobs = []
    for jobid,pobj in self.id2popen.items():
      d = OrderedDict()
      d['jobid'] = jobid
      d['cmd'] = pobj.args
      d['startAt'] = pobj.startAt
      d['logpath'] = pobj.logpath
      pobj.poll()
      if pobj.returncode is None:
        d['status'] = JobStatusRunning
      else:
        d['status'] = JobStatusExited
        d['returncode'] = pobj.returncode
      jobs.append(d)
    payload['jobs'] = jobs
    return payload

  def do_kill(self, payload):
    """{"action":"kill","jobid":idxxx}  #返回{"action":"start","cmd":"ls -l","result":"success/fail"}"""
    jobid = payload['jobid']
    if jobid not in self.id2popen:
      payload['status'] = JobStatusNotExists
      return payload

    pobj = self.id2popen[jobid]

    try:
      pobj.terminate()
      pobj.wait(0.1)
    except TimeoutExpired:
      pass
    try:
      pobj.kill()
      pobj.wait(0.1)
    except TimeoutExpired:
      pass
    if pobj.returncode is None:
      payload['status'] = JobStatusRunning
    else:
      payload['status'] = JobStatusExited
      payload['returncode'] = pobj.returncode

    return payload

  def start_poll(self):
    """为了避免zombie"""
    time.sleep(0.1)
    for jobid,pobj in self.id2popen.items():
      pobj.poll()

if __name__ == '__main__':
  launcher = Launcher()
  a=UDS(launcher)
  a.start_server()
  a.start_accept_loop(inThread=True)
  launcher.start_poll()
