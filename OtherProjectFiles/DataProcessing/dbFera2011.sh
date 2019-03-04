#!/bin/bash
#######################################################################################################
# Author: Jan Ondras
# Institution: University of Cambridge
# Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
# Duration: October 2016 - May 2017
####################################################################################################### 
# This is for FERA 2011 data pre-processing
# (need to specify correct paths in this script)
#######################################################################################################


rm ../Databases/FERA2011_GEMEP/train_labels.dat
rm ../Databases/FERA2011_GEMEP/test_labels.dat
rm ../Databases/FERA2011_GEMEP/labels.dat
# concatenate files to get test labels
CNT=0
for f in ../Databases/FERA2011_GEMEP/test/labels/*; do 
	#echo $f
	cat $f >> ../Databases/FERA2011_GEMEP/test_labels.dat
	((CNT++))
done
echo "Total count of sequences: " $CNT

# concatenate files to get training labels
CNT=0
for f in ../Databases/FERA2011_GEMEP/training/*/*.dat; do 
	#echo $f
	cat $f >> ../Databases/FERA2011_GEMEP/train_labels.dat
	((CNT++))
done
echo "Total count of sequences: " $CNT

# combine them
cat ../Databases/FERA2011_GEMEP/test_labels.dat >> ../Databases/FERA2011_GEMEP/labels.dat
cat ../Databases/FERA2011_GEMEP/train_labels.dat >> ../Databases/FERA2011_GEMEP/labels.dat


# copy videos into 1 folder
# CNT=0
# for f in ../Databases/FERA2011_GEMEP/training/*/*.avi; do 
# 	#echo $f
# 	cp $f ../Databases/FERA2011_GEMEP/videos/
# 	((CNT++))
# done
# echo "Total count of sequences: " $CNT

# CNT=0
# for f in ../Databases/FERA2011_GEMEP/test/test/*/*.avi; do 
# 	#echo $f
# 	cp $f ../Databases/FERA2011_GEMEP/videos/
# 	((CNT++))
# done
# echo "Total count of sequences: " $CNT