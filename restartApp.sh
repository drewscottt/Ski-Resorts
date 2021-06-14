#!/bin/bash

# File: restartApp.sh
# Author: Drew Scott
# Description: Copies ~/flaskapp_parent/flaskapp directory to /var/www/flaskapp and restarts gunicorn on localhost:8000
# 		for the flaskapp

cur_dir=`pwd`

# copy the new state into the working state
sudo rm -r /var/www/flaskapp/*

cd ~/flaskapp_parent
sudo cp -r flaskapp/* /var/www/flaskapp

# kill the old state
workers=(`sudo lsof | grep localhost:8000`)
if [ ! -z "$workers" ]; then
	# workers running, so kill
	pid=${workers[1]}

	sudo kill $pid
fi 

# start new state
cd /var/www/flaskapp
sudo gunicorn --workers=3 --worker-class=gevent wsgi:app 1>~/flaskapp_parent/logs/log.out 2>~/flaskapp_parent/logs/log.err & 

# change back to the original directory
cd $cur_dir
