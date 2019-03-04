#!/bin/bash
#######################################################################################################
# Author: Jan Ondras
# Institution: University of Cambridge
# Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
# Duration: October 2016 - May 2017
####################################################################################################### 
# Create .avi videos from image sequences in all subdirectories of CK+ database. 
# (need to specify correct paths in this script)
#######################################################################################################


CNT=0
for f in ../../Databases/CK+/cohn-kanade-images/*/*/; do 
	echo $f
	#echo ${f:36:4}_${f:41:3}
	cd $f
	ffmpeg -framerate 10 -pattern_type glob -i '*.png' -c:v libx264 ~/Documents/jFiles/Skola/Cambridge/II/_Project/_src/DBprocessing/CK+/videos/${f:36:4}_${f:41:3}.avi
	#cd ~/Documents/jFiles/Skola/Cambridge/II/_Project/_src
	((CNT++))
done

echo "Total count of sequences: " $CNT

#ffmpeg -r 10 -i folder/frames%06d.png  -c:v libx264 out.avi
#ffmpeg -framerate 1 -pattern_type glob -i '*.png' -c:v libx264 out.avi



