#!/usr/bin/env bash
#localhost:18443映射到 vu3:8443
server_host=localhost
server_port=18443
password=LDTf3jg667kD
timeout=60
encrypt_method=aes-256-cfb
local_address=0.0.0.0
local_port=1080
verbose=-v

ss-local \
 -s $server_host \
 -p $server_port \
 -k $password \
 -t $timeout \
 -m $encrypt_method \
 -b $local_address \
 -l $local_port \
 $verbose