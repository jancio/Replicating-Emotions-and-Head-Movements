#!/bin/bash
#######################################################################################################
# Author: Jan Ondras
# Institution: University of Cambridge
# Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
# Duration: October 2016 - May 2017
####################################################################################################### 
# Call AUDetector on each .avi file and produce detailed featureVectors
# format: " FPS | #Frames | array of (#Frames x 12 AUs) either 0 or 1"
#######################################################################################################

./compile.sh

START=$(date +%s)

# backup previous results
mv ./../_src/EmotionClassifier/data/rawFeaturesFromAU/featuresD_GEMEC.dat ./../_src/EmotionClassifier/data/rawFeaturesFromAU/featuresD_GEMEC_backup_${START}.dat

for f in ../Databases/FERA2011_GEMEP/videos/*; do 
	echo $f
	./LIVE ./data/configs/default.cfg ./${f} janko1pokus

	# collect the result into one file - append OR do it from C++ AUD directly
	END=$(date +%s)
	DIFF=$(($END - $START))
	echo "Total time sofar: " $DIFF " s = " $(($DIFF/60)) " min"
done

# manual: ./LIVE ./data/configs/default.cfg ./../_src/EmotionClassifier/data/videos/S005_001.avi janko1pokus