#!/bin/bash
#######################################################################################################
# Author: Jan Ondras
# Institution: University of Cambridge
# Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
# Duration: October 2016 - May 2017
###########################################################################################################
# Generate trueAndPredictedLabels*.dat by 
# 		runnuning AUD on videos in folder videosHumans to get predicted label
# 		and extracting the true label from the name of video file
# Format of human videos: AA_B_C.webm ......... AA = subject #, B = emotion/trueLabel, C = repetition (2 passes made)
###########################################################################################################
# INSTRUCTIONS:
# 1.) run runAll.sh with (naoqi must be running, choregraphe not needed) the following config
	 # DISPLAY_MODE=VIRTUAL
	 # IP_PORT_VIRTUAL=127.0.0.1:9559
	 # RUN_AUD=false
	 # RUN_HPD=false
	 # REBUILD_AUD=true					
	 # REBUILD_HPD=true					
# 2.) now execute this script
# Specify correct paths below

###########################################################################################################
# BELOW: CHOOSE GROUP NUMBER AND WHETHER TO USE CALIBRATION VIDEO !!!
#rm trueAndPredictedLabels.dat
CNT=0
readonly IP_PORT_VIRTUAL=127.0.0.1:9559
readonly CONFIG_FROM_VIDEO=./data/configs/defaultVideoNotVisual.cfg
readonly jGROUP_ID=2

cd ./../../EmotionReplication/

###########################################################################################################
# 1.) WITHOUT CALIBRATION
# for f in /home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/videosHumans/Group$jGROUP_ID/*.webm; do 

# 	TRUE_LABEL=${f: -8: -7}		# ${f: -8: -7} = This is just emotion label [0, 1, 2, 3] = ['Neutral', 'Disgust', 'Happiness', 'Surprise']
# 	PREDICTED_LABEL="$(./LIVE $CONFIG_FROM_VIDEO $f $IP_PORT_VIRTUAL | tail -n 1)"			# get last line from output of AUD

# 	echo $TRUE_LABEL, $PREDICTED_LABEL >> /home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/trueAndPredictedLabels/trueAndPredictedLabels_G$jGROUP_IDx.dat
# 	((CNT++))
# 	echo "Processed: " $CNT
# 	echo $f

# done
# echo "Total count of videos: " $CNT

###########################################################################################################
# 2.) WITH CALIBRATION
for f in /home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/videosHumans/Group$jGROUP_ID/*.webm; do 

	CALIBRATION_VIDEO=${f: 0: -9}_0_1.webm		#  reference video is netral expression, ${f: -11: -9} = subject ID
	TRUE_LABEL=${f: -8: -7}		# ${f: -8: -7} = This is just emotion label [0, 1, 2, 3] = ['Neutral', 'Disgust', 'Happiness', 'Surprise']
	PREDICTED_LABEL="$(./LIVE $CONFIG_FROM_VIDEO $f-$CALIBRATION_VIDEO $IP_PORT_VIRTUAL | tail -n 1)"			# get last line (most frequently inferred emotion over the video) from output of AUDdisplay.py

	# 
	echo $TRUE_LABEL, $PREDICTED_LABEL >> /home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/trueAndPredictedLabels/trueAndPredictedLabels_G$jGROUP_ID_withCalibrationx.dat
	((CNT++))
	echo "Processed: " $CNT
	#echo $f
	#echo $CALIBRATION_VIDEO

done
echo "Total count of videos: " $CNT
