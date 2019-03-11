from tkinter.scrolledtext import ScrolledText
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont

c_FontSize=12
c_FontFamily='Monospace'

class LogFrame(tk.LabelFrame):
  def __init__(self, master=None, cnf={}, **kw):
    """会将生成的订单发送到delegate的onConfirmOrder方法"""
    super().__init__(master,cnf,text='log',**kw)
    self.addST()
    self.preConfigureTag()

  def preConfigureTag(self):
    #提前把tag定义好
    st = self.st
    normalTextFont = tkfont.Font(size=c_FontSize,family=c_FontFamily)
    boldTextFont = tkfont.Font(size=c_FontSize,family=c_FontFamily,weight=tkfont.BOLD)

    st.tag_configure('tag-INFO',foreground='black',font=normalTextFont)
    st.tag_configure('tag-WARNING',foreground='orange',font=normalTextFont)
    st.tag_configure('tag-ERROR',foreground='tomato',font=normalTextFont)
    st.tag_configure('tag-CRITICAL',foreground='red',font=boldTextFont)


  def addST(self):
    st = self.st = ScrolledText(self,height=100)
    st.pack(fill=tk.BOTH,expand=True)

  def destroy(self):
    """从屏幕移除"""
    super().destroy()

  def clearST(self):
    self.st.delete("0.0", "end")

  def setText(self,text):
    self.clearST()
    self.insertTextWithTag(text)
    self.st.see("end")

  def insertTextWithTag(self,text,tag='tag-INFO'):
    self.st.insert("end", text,tag)


if __name__ == '__main__':
  root = tk.Tk()
  frame = LogFrame(root)
  frame.pack(expand=True,fill=tk.BOTH)
  tk.mainloop()