"""JobFrame是一个tab，它显示
status:{} start/stop
cmd
 """

import tkinter as tk
import tkinter.ttk as ttk
from logFrame import LogFrame
from jobModel import JobModel
from constants import *
import os
from bus import EventBus



class JobFrame(tk.Frame):
  def __init__(self,master=None,model=None,cnf={}, **kw):
    """一个runnerFrame必须关联一个Model"""
    tk.Frame.__init__(self,master=master,cnf=cnf,**kw)
    assert model is not None
    self.model:JobModel =model
    self.addWidgets()
    self.refreshGUI()

    bus = EventBus.defaultBus()
    bus.add_event(func=self.refreshGUI,event=g_statusChangedEvent)

  def addWidgets(self):
    """detailLabel显示详情
    logF显示日志"""
    self.addRow0()
    self.addDetailLabel()
    self.logF = LogFrame(self)
    self.logF.pack(side=tk.TOP,fill=tk.BOTH,expand=True)

### row0 start
  def addRow0(self):
    """status start/stop按钮"""
    master = ttk.Frame(self)
    master.pack(side=tk.TOP,fill=tk.X)
    self.statusLabel = ttk.Label(master, text='status:')
    self.actionBtn = ttk.Button(master, text='start',command = self.actionBtnCommand)
    self.statusLabel.pack(side=tk.LEFT,padx=10)
    self.actionBtn.pack(side=tk.LEFT,padx=10)

    self.monitorLogCBVar = tk.IntVar(value=0) #CBVar是否已经勾选了CheckButton
    self.monitorLogCB = ttk.Checkbutton(master, text='monitor log',
                                        variable=self.monitorLogCBVar, command=self.monitorLogCBChanged)
    self.monitorLogCB.pack(side=tk.LEFT)

  def monitorLogCBChanged(self):
    monitorLogCBValue = self.monitorLogCBVar.get()
    if monitorLogCBValue:
      self.refreshLog()
      self.after(ms=1000, func=self.monitorLogCBChanged) #每1秒刷新一次，用于查看最新状态。如果要查看历史记录，需要打开文件
    else:
      pass

  def refreshLog(self):
    logpath = self.model.logpath
    if not isinstance(logpath,str):f"logpath应该是str，实际是{logpath}"
    assert os.path.exists(logpath),f'log文件不存在{logpath}'
    with open(logpath) as f:
      text = f.read()
      self.logF.setText(text)

  def setStatus(self,status):
    if status == JobStatusRunning:
      self.statusLabel['text'] = 'running'
      self.actionBtn['text'] = 'kill'
    elif status == JobStatusExited:
      self.statusLabel['text'] = 'exited'
      self.actionBtn['text'] = 'start'
    elif status == JobStatusNotExists:
      self.statusLabel['text'] = 'NotExistsInDaemon(never run)'
      self.actionBtn['text'] = 'start'

  def actionBtnCommand(self):
    text = self.actionBtn['text']
    if text == 'start':
      self.model.do_start()
    elif text == 'kill' :
      self.model.do_kill()
    else:
      raise NotImplemented
    self.refreshGUI()
### row0 end

  def addDetailLabel(self):
    master = tk.Frame(self)
    master.pack(side=tk.TOP,fill=tk.X)
    self.detailLabel = tk.Label(master, text='detail\n123',justify=tk.LEFT)
    self.detailLabel.pack(side=tk.LEFT)

  def refreshGUI(self):
    """detail就是把model的内容显示出来"""
    self.setStatus(self.model.status)
    jsonstr = self.model.jsonRepr()
    self.detailLabel['text'] = jsonstr
    if not self.model.logpath:
      self.monitorLogCB['state'] = tk.DISABLED
    else:
      self.monitorLogCB['state'] = tk.NORMAL


if __name__ == '__main__':
  root = tk.Tk()
  frame = JobFrame(root)
  frame.pack(expand=True,fill=tk.BOTH)
  tk.mainloop()
