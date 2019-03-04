#######################################################################################################
# Author: Jan Ondras
# Institution: University of Cambridge
# Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
# Duration: October 2016 - May 2017
####################################################################################################### 
# Similar to AUDdisplay.py BUT used only for Whole system evaluation:
# It does not connect to the robot (instead of IP:PORT it receives videoID from AUD),
# - only logs the inferred emotions into file. 
# Need to specify paths!
# For this script to be called by AUD: replace "AUDdisplay" with "AUDdisplayExperiment" in /EmotionReplication/AURecognise.cpp 
#######################################################################################################

import numpy as np
from collections import deque
import time

# To record emotions inferred
outFile = "/home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/detectorsOutOnHumanVideos/Group2/"
inferredEmotions = []

videoID = ""
emotion = 0		# current emotion = index into TARGET_CLASSES and emotionColors

AUS = 7
q = deque()		# current window
inWeightsFile = "./weights.npz"
weights = np.load(inWeightsFile)
WINDOW = weights['WINDOW']
z = np.zeros(len(weights['b1']))

# Set output file
def initRobot(vID):
	global videoID
	videoID = vID

def updateEmotion(str):
	global emotion

	if len(q) < WINDOW-1:	# window not full yet
		q.append(np.array([float(x) for x in str]))
	else:
		q.append(np.array([float(x) for x in str]))			# add newest

		# get WINDOW x AUS matrix: np.array(q)
		# IN: x
		# OUT: [0; 3] label
		# depending on strategy used, prepare input x:
		if weights['strategy'] == 'avg':
			x = np.mean(np.array(q), axis=0) 				# length = # of AUS
		else:
			x = np.array(q).flatten()						# length = WINDOW x # of AUS

		f = np.dot(np.maximum(z, np.dot(x, weights['w1']) + weights['b1']), weights['w2']) + weights['b2'] # relu activation
		#f = np.dot(np.tanh(np.dot(x, weights['w1']) + weights['b1']), weights['w2']) + weights['b2']
		# Softmax:
		s = np.exp(f) / np.sum(np.exp(f), axis=0)

		emotion = np.argmax(s)
		q.popleft()											# remove last/oldest feature

	inferredEmotions.append(emotion)

def finalize():
	# Save data	
	dataOut = np.array([
		[videoID] * len(inferredEmotions), 					# videoIDs
		range(1, len(inferredEmotions) + 1), 				# frame numbers
		inferredEmotions									# emotions
		])
	np.savetxt(outFile + "AUD_" + videoID + ".dat", dataOut.T, delimiter = ",", fmt="%s")

#print "Python code loaded ..."