#!/bin/bash

pid=`ps | grep $1 | grep -v 'grep' | grep -v $0 | awk '{print $1}'`
top -n 1 | grep $pid | awk '{print $5,$6,$7}'