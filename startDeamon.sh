#!/usr/bin/env bash

function get_script_containing_dir {
    local script_fullpath=`realpath $0`
    local script_basename=`basename "$script_fullpath"`
    local script_containing_dir=`dirname "$script_fullpath"`
    #echo "$script_basename"
    echo "$script_containing_dir"
}
cd `get_script_containing_dir`

pythonBin=python3.7
jsonpath="jobs.json"

if `${pythonBin} ./pMonitorD.py canRun` ; then
    echo 'canRun'
    nohup $pythonBin ./pMonitorD.py $jsonpath >pMonitorD_stdout.log 2>&1 &
    echo 'nohup started'
else
    echo 'can not Run, will not start'
fi
