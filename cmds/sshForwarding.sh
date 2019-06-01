#!/usr/bin/env bash
#将本地的 18443 转发到香港机器，从香港机器连接 vu3:8443

for (( i = 0; i < 99999999; i++ )); do
	#hk0也被封了，先连到ub0，再连到hk0，再连到vu3
	ssh -v -L 18443:vu3:8443 -J root@ub0,root@hk0 root@vu3 sleep 99999999 #通过ub0-hk0-vu3
#	ssh -v -L 18443:vu3:8443 -J root@hk0 root@vu3 sleep 99999999 #hk0-vu3
	echo "disconnected will sleep"
	sleep 1
done