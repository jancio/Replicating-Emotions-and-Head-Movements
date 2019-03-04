#!/bin/bash
#######################################################################################################
# Author: Jan Ondras
# Institution: University of Cambridge
# Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
# Duration: October 2016 - May 2017
####################################################################################################### 
# Generate information about videos from folder videosHumans: 
# Output: videoID_duration_frames_GX.dat
# Format: video ID | DURATION (sec) | NUMBER OF FRAMES
###########################################################################################################
# INSTRUCTIONS: choose group and specify paths
readonly jGROUP_ID=2


#rm videoID_duration_frames_G$jGROUP_ID.dat
for f in /home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/videosHumans/Group$jGROUP_ID/*.webm; do 
#for f in /home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/videosRobot/Group$jGROUP_ID/*.avi; do 


	#jFRAMES="$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of default=nokey=1:noprint_wrappers=1 $f | tail -n 1)"
	jDURATION="$(ffprobe -i $f -show_entries format=duration -v quiet -of csv="p=0"  | tail -n 1)"

	#echo ${f: -11: -5}, $jDURATION, $jFRAMES

	echo ${f: -11: -5},$jDURATION,$jFRAMES >> /home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/videoID_duration_frames_G$jGROUP_ID.dat
	#echo ${f: -10: -4},$jDURATION,$jFRAMES >> /home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/robot_videoID_duration_frames_G$jGROUP_ID.dat
	echo $jDURATION
	#echo ${f: -11: -5}
	((CNT++))
	#echo "Processed: " $CNT
	#echo $f

done
echo "Total count of videos: " $CNT