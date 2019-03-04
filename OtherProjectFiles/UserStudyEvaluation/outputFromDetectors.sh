#!/bin/bash
#######################################################################################################
# Author: Jan Ondras
# Institution: University of Cambridge
# Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
# Duration: October 2016 - May 2017
####################################################################################################### 
# Run both detectors on collected human videos, to generate data (frame by frame) that will be then replicated on the robot
#
# Log output from detectors into files in detectorsOutOnHumanVideos folder 
# as {AUD,HPD}_videoID.dat
# Format: AUD: videoID | frame number | emotionNumber
# Format: HPD: videoID | frame number | angleYaw | anglePitch

###########################################################################################################
# INSTRUCTIONS:
# use AUD/HPDdisplayExperiment.py - commented connections to robot and just log the data
# instead of IP_PORT supply videoID as parameter so that Python can save it

# 1.) in /EmotionReplication/AURecognise.cpp replace "AUDdisplay" with "AUDdisplayExperiment"
# 2.) in /HeadPoseReplication/src/DemoTracker.cpp replace "HPDdisplay" with "HPDdisplayExperiment"
# 3.) REBUILD AUD & HPD using runAll.sh
# 4.) now execute this script
# Specify correct paths below

CNT=0
readonly CONFIG_FROM_VIDEO=./data/configs/defaultVideoNotVisual.cfg
readonly jGROUP_ID=2	# only group 2


###########################################################################################################
# WITH CALIBRATION VIDEO

# for all input videos of humans
for f in /home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/videosHumans/Group$jGROUP_ID/*.webm; do 

	###########################################################################################################
	# run AUD, which logs the data
	cd ./../AUDetectorRT/
	CALIBRATION_VIDEO=${f: 0: -9}_0_1.webm		#  reference video is netral expression, ${f: -11: -9} = subject ID
	./LIVE $CONFIG_FROM_VIDEO $f-$CALIBRATION_VIDEO ${f: -11: -5}

	###########################################################################################################
	# run HPD, which logs the data
	cd ./../HPDetector/
	./DemoTracker $f x ${f: -11: -5}

	((CNT++))
	echo "Processed: " $CNT
	#echo $f
	#echo $CALIBRATION_VIDEO

done
echo "Total count of videos: " $CNT


