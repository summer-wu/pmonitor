# pMonitor
+ 因为vultr的ip被封了。改为直连hk0，结果hk0也被封ip了。
+ 无奈只能改为 ssh先连接ub0，ub0再连接hk0
+ 这需要开启3个进程。手动维护比较麻烦，所以改为用代码实现。
+ 在设计上采用前后端分离，pMonitorD是后端最先启动。然后用pMonitorFrame连接后端，可以单独开启、关闭某个job。

# 文件
+ pMonitorD.py，它是后端（进程容器、进程树的根）。它是通过startDeamon.sh启动的
+ pMonitorFrame.py，它是gui入口（前端）。它读取layout.json，然后创建布局。
+ statusPoller.py 每秒刷新一次状态，由pMonitorFrame启动。
+ pMonitorC.py 用于连接uds（unix domain socket）
+ jobFrame.py 它是一个tab
+ jobs.json 定义要执行的命令


# 技术细节
+ pg：process group
+ setsid，开启一个新的session（也是一个新的pg）
+ kill只会关闭一个进程，要关闭一组进程需要用killpg
