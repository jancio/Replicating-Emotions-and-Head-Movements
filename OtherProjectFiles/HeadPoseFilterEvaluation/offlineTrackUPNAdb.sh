#!/bin/bash
#######################################################################################################
# Author: Jan Ondras
# Institution: University of Cambridge
# Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
# Duration: October 2016 - May 2017
####################################################################################################### 
# Run HPD on data from UPNA DB to log measured head poses
#######################################################################################################

cd ./../HPDetector/
for f  in ../../Databases/Head_Pose_Database_UPNA/videos/*.mp4; do
	# args = videoIN, dataOUT
	./DemoTracker ${f} ./UPNAtracked/${f: -20: -4}.dat
	#echo "${f: -20: -4}.dat";
done
