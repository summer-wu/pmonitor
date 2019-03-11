#!/usr/bin/env bash

#pMonitorD需要用nohup启动
nohup python3.7 ./pMonitorD.py 2>&1 > pMonitorD.log &
