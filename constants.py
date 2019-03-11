"""记录status可选值，result可选值"""

g_sockpath = 'pMonitorD.sock'
g_statusChangedEvent = "g_statusChangedEvent"

JobStatusRunning = "JobStatusRunning"
JobStatusExited = "JobStatusExited"
JobStatusNotExists = "JobStatusNotExists" #这个Job不存在

JobStartResultSucc = "JobStartResultSucc"
JobStartResultFail = "JobStartResultFail"
