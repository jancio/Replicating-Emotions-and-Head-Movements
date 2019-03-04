#######################################################################################################
# Author: Jan Ondras
# Institution: University of Cambridge
# Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
# Duration: October 2016 - May 2017
####################################################################################################### 
# This is the main component of Emotion Classifier:
# the functions of this file are called by AUD. 
# It establishes connection to the robot, 
# infers an emotion based on detected action units supplied from AUD
# then sends corresponding LED commands to the robot. 
#######################################################################################################

from naoqi import ALProxy
import numpy as np
from collections import deque
from matplotlib import pyplot as plt
from collections import Counter
import time

# Details about Nao robot LEDs
# http://doc.aldebaran.com/2-1/family/nao_h25/leds_h25.html#nao-h25-led
# http://doc.aldebaran.com/2-1/naoqi/sensors/alleds.html#alleds

# To measure the latency
latencyMeasurements = []
outFileLatency = "/home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/DisplayingModule/LatencyEvaluation/auStopTimes.dat"

# To record emotions inferred over the runtime
outFile = "./generatedData/auData_" + str(int(time.time())) + ".dat"
inferredEmotions = []

# 4 Colors (RBG) to represent 4 emotions 
emotionColors = [(0.,0.,0.), 
				 (1.,0.,0.),
				 (0.,0.,1.),
				 (0.,1.,0.)
				]
TARGET_CLASSES = ['Neutral', 'Disgust', 'Happiness', 'Surprise']		# in order of classes
#				   no color,  RED, 		 GREEN, 	  BLUE

emotion = 0		# current emotion = index into arrays TARGET_CLASSES and emotionColors

AUS = 7			# detected action units
q = deque()		# current window
inWeightsFile = "./weights.npz"		# load trained weights from here
weights = np.load(inWeightsFile)
WINDOW = weights['WINDOW']
z = np.zeros(len(weights['b1']))
#weights.close()


def initRobot(ipPort):
	""" 
	Connect to the robot
	
	Args:
	ipPort : string
		IP and PORT separated by :

	Returns:
	-	 				
	"""
	ip, port = ipPort.split(":")
	#global tts											# if you want robot to say the emotions
	global proxyLED
	#tts = ALProxy("ALTextToSpeech", ip, int(port))		# if you want robot to say the emotions
	proxyLED = ALProxy("ALLeds", ip, int(port))
	proxyLED.createGroup("RedLeds", ['RightFaceLedsRed', 'LeftFaceLedsRed'])
	proxyLED.createGroup("GreenLeds", ['RightFaceLedsGreen', 'LeftFaceLedsGreen'])
	proxyLED.createGroup("BlueLeds", ['RightFaceLedsBlue', 'LeftFaceLedsBlue'])


def updateEmotion(str):
	""" 
	Based on past W frames, infer emotion using trained weights and send corresponding LED command to the robot.
	
	Args:
	str : string
		string of length 7, contains indications which action units are active in currently processed frame (contains characters '0' and '1' only)

	Returns:
	-	 				
	"""
	global emotion

	if len(q) < WINDOW-1:	# window not full yet, so append
		q.append(np.array([float(x) for x in str]))
	else:
		q.append(np.array([float(x) for x in str]))			# add newest

		# Apply neural network:
		# IN: x
		# OUT: [0; 3] label
		# depending on strategy used, prepare input x:
		if weights['strategy'] == 'avg':					# AVG strategy
			x = np.mean(np.array(q), axis=0) 				# length = # of AUS
		else:												# CONCAT strategy
			x = np.array(q).flatten()						# length = WINDOW x # of AUS

		f = np.dot(np.maximum(z, np.dot(x, weights['w1']) + weights['b1']), weights['w2']) + weights['b2'] # relu activation
		# Softmax:
		s = np.exp(f) / np.sum(np.exp(f), axis=0)

		newEmotion = np.argmax(s)
		inferredEmotions.append(newEmotion)
		q.popleft()											# remove last/oldest feature from accumulated window

		# Commands are sent only if emotion has to be changed
		if(newEmotion != emotion):
			emotion = newEmotion
			#tts.say(TARGET_CLASSES[emotion])								# Say new emotion
			proxyLED.setIntensity("RedLeds", emotionColors[emotion][0])		# Set LEDs
			proxyLED.setIntensity("GreenLeds", emotionColors[emotion][1])
			proxyLED.setIntensity("BlueLeds", emotionColors[emotion][2])

	# Log latency
	latencyMeasurements.append(1000*time.time())

def finalize():
	""" 
	Called when AUD got signal to shutdown.
	Visualise the inferred emotions from the runtime 
	and optionally (need to specify manually at the end of this function) 
	save the data and latency measurements (NO by default). 
	
	Args:
	-
	Returns:
	-	 				
	"""
	# Determine the most frequently inferred emotion (majority vote)
	y = Counter(inferredEmotions)
	d = sorted(y.items())
	keys  = [x[0] for x in d]    # classes
	counts  = [x[1] for x in d]  # counts per class (in sorted order by keys)
	emotionMostInferred = max(d, key=lambda item: item[1])[0]
	print "Most frequently inferred emotion was: "
	print TARGET_CLASSES[emotionMostInferred]
	print emotionMostInferred

	# Plot emotions inferred over time:
	Yrange = range(len(TARGET_CLASSES))
	plt.figure()
	plt.plot(range(1, len(inferredEmotions) + 1), inferredEmotions, 'ro', markersize=16, label= 'Most frequent emotion: ' + TARGET_CLASSES[emotionMostInferred])
	plt.yticks(Yrange, TARGET_CLASSES) #, rotation='vertical'
	plt.xlabel('Frame #')
	plt.ylabel('Emotion')
	plt.ylim([-0.5, 3.5])
	plt.title('Emotions inferred over time')
	plt.legend(loc='best')

	# Plot histogram
	indexes = np.arange(len(TARGET_CLASSES))
	width = 0.5
	plt.figure()
	plt.bar(keys, counts, width, label= 'Most frequent: ' + TARGET_CLASSES[emotionMostInferred])
	plt.xticks(indexes + width * 0.5, TARGET_CLASSES)
	plt.xlabel('Emotion')
	plt.ylabel('# of inferences')
	plt.title('# of inferences per emotion')
	plt.legend(loc='best')
	plt.show()

	# # Save inferredEmotions
	# np.savetxt(outFile, np.array(inferredEmotions), delimiter = " ")

	# Save latency measurements
	#np.savetxt(outFileLatency, np.array(latencyMeasurements), delimiter = " ")


print "Python code loaded ..."