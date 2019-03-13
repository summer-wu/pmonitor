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

filename.py canRun #测试是否可以执行，返回0表示可以，其他表示不可以运行，因为已经在运行了
nohup filename.py jsonpath #提供jsonpath并启动

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
from jobModel import JobModel
import signal
import traceback

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
      payload = getattr(self.server.launcher,f'do_{action}')(payload)
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
      print("connection from '{}'".format(client_address))
      ServerHandler(connection,self).handle_recv()



class Launcher:
  def __init__(self,logdir='logdir',jsonpath=None):
    self.id2popen = OrderedDict()
    self.logdir = logdir
    signal.signal(signal.SIGINT, self.sigHandler)
    signal.signal(signal.SIGTERM, self.sigHandler)
    if jsonpath:
      self.startJobsWithJsonpath(jsonpath)

  def startJobsWithJsonpath(self,jsonpath):
    jobid2model = JobModel.jobid2modelFromJsonpath(jsonpath)
    for jobid,model in jobid2model.items():
      if model.autostart:
        self.do_start(model.dictRepr())

  def logpathFromJobid(self,jobid):
    datepart = datetime.now().strftime("%Y%m%d_%H_%M_%S")
    filename = f"{jobid}_{datepart}.log"
    logpath = os.path.join(self.logdir,filename)
    return logpath

  def do_start(self, payload):
    cmd = payload['cmd']
    jobid = payload['jobid']
    print(f"will do_start jobid={jobid} cmd={cmd}")
    logpath = self.logpathFromJobid(jobid)
    assert cmd is not None and logpath is not None and jobid is not None

    f = open(logpath,'at')
    pobj = Popen(cmd,shell=True,stdout=f,stderr=f,bufsize=0,start_new_session=True)
    pobj.startAt = payload['startAt'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pobj.logpath = payload['logpath'] = logpath
    payload['status'] = JobStatusRunning
    payload['pid'] = pobj.pid
    payload['returncode'] = None
    print(f"started jobid={jobid} pid={pobj.pid}")
    self.id2popen[jobid] = pobj
    return payload

  def do_jobs(self, payload):
    print(f"will do_jobs")
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
    print(f"will do_kill {jobid}")
    if jobid not in self.id2popen:
      payload['status'] = JobStatusNotExists
      return payload

    pobj = self.id2popen[jobid]
    self.killPobj(pobj)
    if pobj.returncode is None:
      payload['status'] = JobStatusRunning
    else:
      payload['status'] = JobStatusExited
      payload['returncode'] = pobj.returncode

    return payload

  def killPobj(self,pobj):
    """父进程关闭，子进程可能仍然存活，这是不希望的！希望把整个进程组关闭，所以不能用pobj的terminate方法，应该killpg。"""
    pgid = os.getpgid(pobj.pid)
    try:
      os.killpg(pgid, signal.SIGTERM)
      returncode = pobj.wait(0.1)
      if returncode:
        print(f"SIGTERM成功，returncode={returncode},cmd={pobj.args}", flush=True)
        return returncode
    except:
      traceback.print_exc()

    try:
      os.killpg(pgid, signal.SIGKILL)
      returncode = pobj.wait(0.1)
      if returncode:
        print(f"SIGKILL成功，returncode={returncode},cmd={pobj.args}", flush=True)
        return returncode
    except:
      traceback.print_exc()

  def start_poll(self):
    """为了避免zombie"""
    time.sleep(1)
    for jobid,pobj in self.id2popen.items():
      pobj.poll()

  def sigHandler(self,signum, frame):
    if signum == signal.SIGINT or signum == signal.SIGTERM:
      print("收到信号{} will exit".format(signum))
      self.killAll()
      exit(0)
    else:
      print(f"不认识的信号{signum}")

  def killAll(self):
    for jobid,pobj in self.id2popen.items():
      self.killPobj(pobj)

def daemonisRunning():
  """通过连接socket，判断daemon是否在运行"""
  s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
  errno = s.connect_ex(g_sockpath)
  s.close()
  if errno == 0:
    return True
  else:
    return False

def testCanRunIfNeeded():
  """方便shell测试"""
  if len(sys.argv) == 2 and sys.argv[1] == 'canRun':
    if daemonisRunning():
      exit(-1)
    else:
      exit(0)

if __name__ == '__main__':
  testCanRunIfNeeded()

  print(f"==={datetime.now()}===")
  if daemonisRunning():
    print('already running')
    exit(-1)

  print(f"started pid={os.getpid()}")

  jsonpath = None
  if len(sys.argv)==2 and os.path.exists(sys.argv[1]):
    jsonpath = sys.argv[1]
  launcher = Launcher(jsonpath=jsonpath)
  a=UDS(launcher)
  a.start_server()
  a.start_accept_loop(inThread=True)
  launcher.start_poll()
