#!/usr/bin/env bash
#将本地的 18443 转发到远程机器
#python中启动的ssh命令是没有继承stdin的(相当于-n)，所以必须执行命令。如果进入interactive，会立即退出，并打印mesg: ttyname failed: Inappropriate ioctl for device
#不能sleep太久，会导致kill process，改为read
#May 31 11:09:02 localhost kernel: [20737848.823621] Out of memory: Kill process 22891 (apache2) score 47 or sacrifice child
#May 31 11:09:02 localhost kernel: [20737848.826861] Killed process 22891 (apache2) total-vm:246164kB, anon-rss:4144kB, file-rss:19936kB

for (( i = 0; i < 99999999; i++ )); do
	ssh -v -L 18443:vu3:8443 -J root@ub0,root@hk0 root@vu3 sleep 86400 #通过ub0-hk0-vu3
#	ssh -v -L 18443:vu3:8443 -J root@hk0 root@vu3 sleep 86400 #hk0-vu3
#	ssh -v -D 1080 root@hk0 #直接通过hk0翻墙
#    ssh -v -L 18443:vu3:8443 root@vu3 sleep 86400 #直接vu3，让防火墙认为是ssh协议

	echo "disconnected will sleep"
	sleep 1
done