"""它是Monitor的Client

使用方法：
c.handlePayload=aNewFunc
c.sendPayload(payload)
c.handle_recv()

"""
import socket
import threading
import json
import errno as errnoM
from constants import *
import logging

class PMonitorC:
  def __init__(self):
    self.data = bytearray()
    self.s:socket = None
    self.shouldBreak = False
    self.connect_to_uds(inThread=False)

  def __setattr__(self, key, value):
    if key == 'data' and hasattr(self,'data'):
      print('before data:',self.data)
      print('after data:',value)
    super(PMonitorC, self).__setattr__(key,value)


  @staticmethod
  def daemonisRunning():
    """通过连接socket，判断daemon是否在运行"""
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    errno = s.connect_ex(g_sockpath)
    s.close()
    if errno == 0:
      return True
    else:
      return False

  def connect_to_uds(self,inThread=False, server_address=g_sockpath):
    """如果inThread，则返回None。在当前线程 返回errno, errmsg。"""
    isMain = threading.current_thread() == threading.main_thread()
    if inThread and isMain:
      t = threading.Thread(target=self.connect_to_uds, args=[inThread,server_address])
      t.start()
      return
    if inThread:
      assert not isMain

    self.s = s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(0.5) #最多等待0.2秒

    errno = s.connect_ex(server_address)
    if errno == 0:
      logging.debug("connect_ex success")
      return (None,None)
    else:
      errmsg = errnoM.errorcode[errno]
      logging.debug("connect_ex fail,errno={},errmsg={}".format(errno, errmsg))
      return errno,errmsg

  def handle_recv(self):
    s = self.s
    try:
      while True:
        if self.shouldBreak:break
        data = s.recv(1024)
        if len(data)==0:
          s.close()
          return
        # print("received:", data)
        self.data.extend(data)
        if self.canParse(self.data):
          self.parseData()
          self.shouldBreak = True #只需要parseData一次
    finally:
      s.close()
      logging.debug("connection closed %s",s)

  @staticmethod
  def takeDataWithByteCount(data,bytecount):
    taken = data[:bytecount]
    remaining = data[bytecount:]
    return taken,remaining

  @classmethod
  def canParse(cls,data):
    """data是否足够长"""
    length, remaining = cls.takeDataWithByteCount(data, 4)
    length = int.from_bytes(length, byteorder='big')
    return len(remaining)>=length # remaining满足 需要的length

  def parseData(self):
    while len(self.data)>=5:
      length,remaining = self.takeDataWithByteCount(self.data,4)
      length = int.from_bytes(length,byteorder='big')
      assert len(remaining)>=length

      jsonBytes,remaining = self.takeDataWithByteCount(remaining,length)
      payload = json.loads(jsonBytes)
      # print("解析到payload:",payload)
      self.handlePayload(payload)
      self.data = remaining

  def handlePayload(self, payload:dict):
    """必须覆盖，可以通过 c.handlePayload=aFunc 覆盖"""
    raise NotImplemented('must override')


  def sendPayload(self, payload):
    """传入的payload是dict"""
    payload = json.dumps(payload).encode()
    length = len(payload)
    length = length.to_bytes(4, byteorder='big')
    data = length + payload
    self.s.sendall(data)


if __name__ == '__main__':
  c = PMonitorC()
  errNo,errMsg = c.connect_to_uds()
  print(errNo,errMsg)
  # payload = dict(action="tree")
  payload = dict(action="start",jobid="ls",cmd="ls -la",logpath="logdir/ls.txt")
  # payload = dict(action="kill", jobid="ping")
  c.sendPayload(payload)
  c.handle_recv()
  print('after handle_recv')
