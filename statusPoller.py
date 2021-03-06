"""每秒询问Daemon一遍状态，避免daemon状态修改了GUI仍没变化"""

from bus import EventBus
import threading
import time
from pMonitorC import PMonitorC
from jobModel import JobModel
from constants import g_statusChangedEvent
import logging

class StatusPoller:
  def __init__(self,jobid2model,interval=1):
    """默认interval 1秒"""
    assert jobid2model is not None
    self.jobid2model = jobid2model
    self.interval = 1
    self.shouldStop = False

  def flagShouldStop(self):
    """由pMonitorFrame调用，用于停止poll_jobs中的while循环"""
    self.shouldStop = True

  def poll_jobs(self,inThread=True):
    """每1秒刷新一次jobs状态。因为状态改变只能client请求，无法实现server推送"""
    isMain = threading.current_thread() == threading.main_thread()
    if inThread and isMain:
      t = threading.Thread(target=self.poll_jobs, args=[inThread])
      t.start()
      return
    if inThread:
      assert not isMain

    while True:
      if self.shouldStop:break
      self.poll_once()
      time.sleep(self.interval)

  def handlePayload(self, payload:dict):
    jobs = payload['jobs']
    jobDict:dict
    model:JobModel
    for jobDict in jobs:
      jobid = jobDict['jobid']
      if jobid in self.jobid2model:
        model = self.jobid2model[jobid]
      else:
        print(f'{jobid}已经从配置中删除了')
        continue
      oldstatus = model.status
      model.replaceWithDict(jobDict)
      newstatus = model.status
      if oldstatus != newstatus:
        logging.debug(f'jobid={jobid} status changed')
        EventBus.defaultBus().emit(g_statusChangedEvent)
      else:
        logging.debug(f'jobid={jobid} status not changed')

  def poll_once(self):
    c=PMonitorC()
    payload = {"action":"jobs"}
    c.handlePayload = self.handlePayload
    c.sendPayload(payload)
    c.handle_recv()



