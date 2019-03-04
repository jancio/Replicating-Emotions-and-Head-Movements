#!/bin/bash
#######################################################################################################
# Author: Jan Ondras
# Institution: University of Cambridge
# Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
# Duration: October 2016 - May 2017
####################################################################################################### 
###########################################################################################################
# Concatenate data from files from detectorsOutOnHumanVideos folder
# into 2 files AUD/HPD_data_G2.dat
###########################################################################################################

readonly jGROUP_ID=2	# only group 2

CNT=0
for f in /home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/detectorsOutOnHumanVideos/Group$jGROUP_ID/AUD_*.dat; do 
	cat $f >> AUD_data_G2x.dat
	((CNT++))
done
echo "Total count: " $CNT

CNT=0
for f in /home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/detectorsOutOnHumanVideos/Group$jGROUP_ID/HPD_*.dat; do 
	cat $f >> HPD_data_G2x.dat
	((CNT++))
done
echo "Total count: " $CNT

