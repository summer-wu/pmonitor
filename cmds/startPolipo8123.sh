#!/usr/bin/env bash
#不应进入后台
# If logSyslog is false and logFile is empty, messages go to the error output of the process (normally the terminal).
polipo socksParentProxy="localhost:1080" socksProxyType="socks5" proxyAddress="0.0.0.0" logSyslog=false logFile="" proxyPort="8123"