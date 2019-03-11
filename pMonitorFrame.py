"""Process Monitor """

import tkinter as tk
import tkinter.ttk as ttk
from pMonitorC import PMonitorC
from jobModel import JobModel
from jobFrame import JobFrame
from statusPoller import StatusPoller

import logging
logging.debug('started')
logging.getLogger().setLevel(logging.INFO)

class PMonitorFrame(tk.Frame):

  def __init__(self,master=None, cnf={}, **kw):
    tk.Frame.__init__(self,master,cnf,**kw)
    self.nb:ttk.Notebook = None
    self.addNotebook()
    self.jobid2model = JobModel.jobid2modelFromJson()
    for jobid,model in self.jobid2model.items():
      f = JobFrame(master=None,model=model)
      tab_text = jobid
      self.nb.add(f,text=tab_text)

    #1秒后刷新状态
    self.statusPoller = StatusPoller(self.jobid2model)
    self.after(1000,func=lambda : self.statusPoller.poll_jobs(inThread=True))


  def addNotebook(self):
    """Frame内只有一个Notebook组件"""
    self.nb = nb = ttk.Notebook(self)
    nb.pack(expand=True,fill=tk.BOTH)

  def destroy(self):
    super()
    self.statusPoller.flagShouldStop()

if __name__ == '__main__':
  if not PMonitorC.daemonisRunning():
    print("pMonitorD is not running")
    exit(0)
  root = tk.Tk()
  frame = PMonitorFrame(root)
  frame.pack(expand=True,fill=tk.BOTH)
  root.wm_geometry("800x600")
  tk.mainloop()
