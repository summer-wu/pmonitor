"""Process Monitor """

import tkinter as tk
import tkinter.ttk as ttk

class PMonitorFrame(tk.Frame):
  def __init__(self,master=None, cnf={}, **kw):
    tk.Frame.__init__(self,master,cnf,**kw)
    self.nb:ttk.Notebook = None
    self.addNotebook()
    self.addTab0()
    self.addTab1()

  def addNotebook(self):
    self.nb = nb = ttk.Notebook(self)
    nb.pack(expand=True,fill=tk.BOTH)

  def addTab0(self):
    label = tk.Label(text='tab0')
    self.nb.add(label,text='tab0')

  def addTab1(self):
    label = tk.Label(text='tab1')
    self.nb.add(label,text='tab1')




if __name__ == '__main__':
  root = tk.Tk()
  frame = PMonitorFrame(root)
  frame.pack(expand=True,fill=tk.BOTH)
  tk.mainloop()
