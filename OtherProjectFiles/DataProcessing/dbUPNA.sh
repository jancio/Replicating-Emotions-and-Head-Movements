#!/bin/bash
#######################################################################################################
# Author: Jan Ondras
# Institution: University of Cambridge
# Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
# Duration: October 2016 - May 2017
####################################################################################################### 
# This is for UPNA data pre-processing
# (need to specify correct paths in this script)
#######################################################################################################



# copy videos into 1 folder
CNT=0
for f in ../../Databases/Head_Pose_Database_UPNA/*/*.mp4; do 
	#echo $f
	cp $f ../../Databases/Head_Pose_Database_UPNA/videos/
	((CNT++))
done
echo "Total count of videos: " $CNT



# copy labels (ground-truths) into 1 folder
CNT=0
for f in ../../Databases/Head_Pose_Database_UPNA/*/*_groundtruth3D.txt; do 
	#echo $f
	cp $f ../../Databases/Head_Pose_Database_UPNA/labels/
	((CNT++))
done
echo "Total count of labels: " $CNT



# copy zeroed labels (ground-truths) into 1 folder
CNT=0
for f in ../../Databases/Head_Pose_Database_UPNA/*/*_groundtruth3D_zeroed.txt; do 
	#echo $f
	cp $f ../../Databases/Head_Pose_Database_UPNA/labelsZero/
	((CNT++))
done
echo "Total count of labelsZero: " $CNT
