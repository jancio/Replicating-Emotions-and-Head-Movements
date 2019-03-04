#!/bin/bash
#######################################################################################################
# Author: Jan Ondras
# Institution: University of Cambridge
# Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
# Duration: October 2016 - May 2017
####################################################################################################### 
# Call AUD on each .avi file and produce detailed featureVectors
# format: "Subject | Seq# | FPS | #Frames | array of (#Frames x 12 AUs) either 0 or 1"
# In livefeatures.cpp - specify path where to save features.
#######################################################################################################

./compile.sh

START=$(date +%s)

# backup previous results
mv ./../_src/EmotionClassifier/data/rawFeaturesFromAU/featureVectors.dat ./../_src/EmotionClassifier/data/rawFeaturesFromAU/features_backup_${START}.dat

for f in ../_src/EmotionClassifier/data/videos/*; do 
	echo $f
	./LIVE ./data/configs/default.cfg ./${f} sessionName

	# collect the result into one file - append OR do it from C++ AUD directly
	END=$(date +%s)
	DIFF=$(($END - $START))
	echo "Total time sofar: " $DIFF " s = " $(($DIFF/60)) " min"
done

# manually: ./LIVE ./data/configs/default.cfg ./../_src/EmotionClassifier/data/videos/S005_001.avi janko1pokus