#!/bin/bash
#######################################################################################################
# Author: Jan Ondras
# Institution: University of Cambridge
# Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
# Duration: October 2016 - May 2017
####################################################################################################### 
# This script runs the whole system.
# Specify the SETTINGS below.
###########################################################################################################
# AUD uses external camera, HPD uses built-in (first) camera

# OPTION 1:
#readonly DISPLAY_MODE=VIRTUAL 				# REAL or VIRTUAL robot
readonly DISPLAY_MODE=REAL
readonly IP_PORT_VIRTUAL=127.0.0.1:9559
readonly IP_PORT_REAL=169.254.42.173:9559

# OPTION 2:
#readonly REBUILD_AUD=true					# rebuild AUD
readonly REBUILD_AUD=false

# OPTION 3:
#readonly REBUILD_HPD=true					# rebuild HPD
readonly REBUILD_HPD=false

# OPTION 4:
readonly RUN_AUD=true						# run emotion replication
#readonly RUN_AUD=false

# OPTION 5:
readonly RUN_HPD=true						# run head pose replication
#readonly RUN_HPD=false

# OPTION 6:
readonly AUD_LIVE=true
#readonly AUD_LIVE=false					# from video file specified in VIDEO_IN_AUD
readonly VIDEO_IN_AUD=/home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/videosHumans/01_2_2.webm			# ~/Desktop/pokus2.webm

# OPTION 7:
readonly HPD_LIVE=true
#readonly HPD_LIVE=false					# from video file specified in VIDEO_IN_HPD
readonly VIDEO_IN_HPD=/home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/videosHumans/01_2_2.webm			# ~/Desktop/pokus22.webm


readonly NAOQI_PATH=/home/janciovec/naoqi/naoqi-sdk-2.1.4.13-linux64/naoqi						# path to NaoQi
readonly CHOREGRAPHE_PATH=/home/janciovec/choregraphe-suite-2.1.4.13-linux64/choregraphe			# path to Choregraphe

############################################################################################################
############################################################################################################










readonly DELAY_HPD=4.30						# To compensate the delay of starting up the AUD (AUD takes longer to start)

if [ $DISPLAY_MODE == "VIRTUAL" ]; then

	IP_PORT=$IP_PORT_VIRTUAL
	
	# Run the naoqi and choregraphe only if not already running
	if ! pgrep "naoqi" > /dev/null; then
		echo "Starting naoqi: "
		$NAOQI_PATH &> /dev/null &  # or ~/choregraphe-suite-2.1.4.13-linux64/bin/naoqi-bin
	fi
	if ! pgrep "choregraphe" > /dev/null; then
		echo "Starting Choregraphe: "
		$CHOREGRAPHE_PATH &> /dev/null &
	fi
	# Wait for user to manually connect to virtual robot in choreographe ...
	read -rsp $'After connecting to virtual robot in Choregraphe, press any key to continue...\n' -n1

else
	IP_PORT=$IP_PORT_REAL

	# Wait to connect
	read -rsp $'After connecting to real robot, press any key to continue...\n' -n1
fi

############################################################################################################

readonly CONFIG_LIVE=./data/configs/defaultLive.cfg
readonly CONFIG_FROM_VIDEO=./data/configs/defaultVideo.cfg
#readonly CONFIG_FROM_VIDEO=./data/configs/defaultVideoNotVisual.cfg # in case you want to supress visual output of AUD

cd ./EmotionReplication/
if [ $REBUILD_AUD == true ]; then
	make clean
	./compile.sh
fi
if [ $RUN_AUD == true ]; then
	if [ $AUD_LIVE == true ]; then
		echo "Running Action Units Detector (AUD) - live"
		./LIVE $CONFIG_LIVE $IP_PORT &
	else
		echo "Running Action Units Detector (AUD) - from video"
		./LIVE $CONFIG_FROM_VIDEO $VIDEO_IN_AUD $IP_PORT &
	fi
fi
cd ..

############################################################################################################

cd ./HeadPoseReplication/
if [ $REBUILD_HPD == true ]; then
	make clean
	make
fi
if [ $RUN_HPD == true ]; then
	sleep $DELAY_HPD
	if [ $HPD_LIVE == true ]; then
		echo "Running Head Pose Detector (HPD) - live"
		./DemoTracker LIVE x $IP_PORT
	else
		echo "Running Head Pose Detector (HPD) - from video"
		./DemoTracker $VIDEO_IN_HPD x $IP_PORT
	fi
fi
cd ..