"""RunnerModel，记录要执行的cmd"""
from subprocess import Popen,getstatusoutput
from collections import OrderedDict
import json
class RunnerModel:
  def __init__(self):
    self.jobid = None #用于标记tab
    self.cmd = None
    self.status = None #状态，str
    self.startAt = None #启动时间，str
    self.logpath = None #日志文件，str
    self.returncode = None

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
    clsname = str(type(str))
    jsonstr = self.jsonRepr()
    s = f"<{clsname}>\n{jsonstr}"
    return s

  __repr__ = __str__


  @classmethod
  def fromDict(cls,d):
    inst = cls()
    inst.cmd = d['cmd']
    inst.tabid = d['jobid']
    if 'status'  in d:inst.status = d['status']
    if 'logpath' in d:inst.logpath = d['logpath']
    if 'returncode' in d:inst.returncode = d['returncode']
    return inst

  def run(self):
    process = Popen('ls -l',shell=True)
    print(process)

  def do_start(self):
    pass

  def do_kill(self):
    pass


if __name__ == '__main__':
  m = RunnerModel()
  print(m)
  # a=getstatusoutput('ls -l')
  # print(a)