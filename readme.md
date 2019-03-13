# pMonitor
+ 因为vultr的ip被封了。改为直连hk0，结果hk0也被封ip了。
+ 无奈只能改为 ssh先连接ub0，ub0再连接hk0
+ 这需要开启3个进程。手动维护比较麻烦，所以改为用代码实现。

# 文件
+ pMonitorFrame.py，它是gui入口。它读取layout.json，然后创建布局。
+ pMonitorD.py，在后台执行


# 技术细节
+ pg：process group
+ setsid，开启一个新的session（也是一个新的pg）
+ kill只会关闭一个进程，要关闭一组进程需要用killpg
