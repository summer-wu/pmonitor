"""runner是一个tab，它显示
status:{} start/stop
cmd
 """

import tkinter as tk
import tkinter.ttk as ttk
from logFrame import LogFrame
from runnerModel import RunnerModel
from constants import *
import os

class RunnerFrame(tk.Frame):
  def __init__(self,master=None, cnf={}, **kw):
    """一个runnerFrame必须关联一个Model"""
    tk.Frame.__init__(self,master,cnf,**kw)
    self.addWidgets()
    self.model:RunnerModel = None

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
    master = tk.Frame(self)
    master.pack(side=tk.TOP,fill=tk.X)
    self.statusLabel = tk.Label(master, text='status:')
    self.actionBtn = ttk.Button(master, text='start',command = self.actionBtnCommand)
    self.statusLabel.pack(side=tk.LEFT)
    self.actionBtn.pack(side=tk.LEFT)

    self.monitorLogVar = tk.IntVar(value=0)
    self.monitorLogCB = ttk.Checkbutton(master,text='monitor log',
                                        variable=self.monitorLogVar,command=self.monitorLogChanged)
    self.monitorLogCB.pack(side=tk.LEFT)

  def monitorLogChanged(self):
    monitorLogValue = self.monitorLogVar.get()
    if monitorLogValue:
      self.refreshLog()
      self.after(ms=1000,func=self.monitorLogChanged)
    else:
      pass

  def refreshLog(self):
    logpath = self.model.logpath
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
### row0 end

  def addDetailLabel(self):
    master = tk.Frame(self)
    master.pack(side=tk.TOP,fill=tk.X)
    self.detailLabel = tk.Label(master, text='detail\n123',justify=tk.LEFT)
    self.detailLabel.pack(side=tk.LEFT)

  def refreshDetail(self):
    """detail就是把model的内容显示出来"""
    jsonstr = self.model.jsonRepr()
    self.detailLabel['text'] = jsonstr


if __name__ == '__main__':
  root = tk.Tk()
  frame = RunnerFrame(root)
  frame.pack(expand=True,fill=tk.BOTH)
  tk.mainloop()
