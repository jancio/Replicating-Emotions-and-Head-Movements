#!/bin/bash
#######################################################################################################
# Author: Jan Ondras
# Institution: University of Cambridge
# Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
# Duration: October 2016 - May 2017
####################################################################################################### 
# Merge videosHumans and videosRobot into videosMerged - (human-robot videos) created by putting human and robot videos side-by-side
#######################################################################################################




readonly jGROUP_ID=2	# only group 2
# CNT=0
# for f in /home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/videosHumans/Group$jGROUP_ID/*.webm; do 
	
# 	#echo $f
# 	#echo ${f: -11: -5}

# 	ffmpeg -i $f -i /home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/videosRobot/Group$jGROUP_ID/${f: -11: -5}.avi -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 /home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/videosMerged/Group$jGROUP_ID/${f: -11: -5}.mp4

# 	((CNT++))
# done
# echo "Total count: " $CNT

########################################################################################
# ALTERNATIVELY: used finally
# Speed up robot videos to match the length of human videos; (it is ok to speed up since it is equivalent to setting timestep dt precisely when replicating - which was difficult to estimate)
# then merge
CNT=0
for f in /home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/videosHumans/Group$jGROUP_ID/*.webm; do 
	
	#jDURATION_human="$(ffprobe -i $f -show_entries format=duration -v quiet -of csv="p=0"  | tail -n 1)"
	#jDURATION_robot="$(ffprobe -i /home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/videosRobot/Group$jGROUP_ID/${f: -11: -5}.avi -show_entries format=duration -v quiet -of csv="p=0"  | tail -n 1)"
	speedup=0.86
	newFPS=50

	ffmpeg -i /home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/videosRobot/Group2/${f: -11: -5}.avi -c:v h264 -an -r $newFPS -b:v 800k -filter:v "setpts=$speedup*PTS" /home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/videosRobot/Group2_faster/${f: -11: -5}.mp4

	ffmpeg -i $f -i /home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/videosRobot/Group2_faster/${f: -11: -5}.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 /home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/videosMerged/Group2_faster/${f: -11: -5}.mp4

	((CNT++))
done
echo "Total count: " $CNT


