"""RunnerModel，记录要执行的cmd"""
from subprocess import Popen,getstatusoutput
from collections import OrderedDict
import json
from pMonitorC import PMonitorC
import logging
import os

class JobModel:

  @classmethod
  def jobid2modelFromJsonpath(cls, jsonpath='jobs.json'):
    """读取jobs.json，返回jobid2model字典"""
    assert os.path.exists(jsonpath), f"jsonpath={jsonpath} not exists!"
    with open(jsonpath) as f:
      d = json.load(f)
    jobs_json = d['jobs']
    jobid2model = {}
    for jobDict in jobs_json:
      m = cls.fromDict(jobDict)
      jobid2model[m.jobid]=m
    return jobid2model

  def __init__(self):
    self.jobid = None #用于标记tab
    self.cmd = None
    self.autostart = False
    self.status = None #状态，str
    self.startAt = None #启动时间，str
    self.logpath = None #日志文件，str
    self.returncode = None
    self.actionResult = None #它不会记录进dictRepr

  @classmethod
  def fromDict(cls,d):
    """从json中读取时用到"""
    inst = cls()
    inst.jobid = d['jobid']
    inst.cmd = d['cmd']
    if 'autostart' in d: inst.autostart = d['autostart']
    inst.replaceWithDict(d)
    return inst

  def replaceWithDict(self,d):
    fields = ['status','logpath','returncode','startAt']
    for field in fields:
      if field in d:
        setattr(self,field,d[field])

  def dictRepr(self) ->dict:
    d = OrderedDict()
    d['jobid'] = self.jobid
    d['cmd'] = self.cmd
    d['status'] = self.status
    d['startAt'] = self.startAt
    d['logpath'] = self.logpath
    d['returncode'] = self.returncode
    return d

  def jsonRepr(self)->str:
    d = self.dictRepr()
    s = json.dumps(d,indent=4)
    return s

  def __str__(self):
    clsname = str(type(self))
    jsonstr = self.jsonRepr()
    s = f"{clsname}\n{jsonstr}"
    return s

  __repr__ = __str__


  def handlePayload(self,payload):
    """PMonitorC收到消息后，会调用此方法"""
    self.replaceWithDict(payload)

    action = payload['action']
    if action == 'start':
      logging.info(f'start返回{payload}')
      pass
    elif action == 'kill':
      #只看status
      logging.info(f'kill返回{payload}')
      pass

  def do_start(self):
    """返回后，model应该已经更新过了"""
    c = PMonitorC()
    c.handlePayload = self.handlePayload
    payload = self.dictRepr()
    payload['action'] = 'start'
    c.sendPayload(payload)
    c.handle_recv()
    return self.actionResult

  def do_kill(self):
    c = PMonitorC()
    c.handlePayload = self.handlePayload
    payload = self.dictRepr()
    payload['action'] = 'kill'
    c.sendPayload(payload)
    c.handle_recv()
    return self.actionResult


if __name__ == '__main__':
  jobs = JobModel.jobid2modelFromJsonpath()
  print(jobs)
  # a=getstatusoutput('ls -l')
  # print(a)