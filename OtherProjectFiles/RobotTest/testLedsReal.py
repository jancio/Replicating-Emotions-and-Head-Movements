#######################################################################################################
# Author: Jan Ondras
# Institution: University of Cambridge
# Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
# Duration: October 2016 - May 2017
####################################################################################################### 
# This is to do simple test of using robot's LEDs.
# This does not work on virtual because simulated robot does not show LEDs.
#######################################################################################################


from naoqi import ALProxy
import numpy as np
from collections import deque
from matplotlib import pyplot as plt
import time

# http://doc.aldebaran.com/2-1/family/nao_h25/leds_h25.html#nao-h25-led
# http://doc.aldebaran.com/2-1/naoqi/sensors/alleds.html#alleds

# connect to robot
tts = ALProxy("ALTextToSpeech", "169.254.42.173", 9559) # If you want it to tell the emotion
proxyLED = ALProxy("ALLeds", "169.254.42.173", 9559)

proxyLED.createGroup("RedLeds", ['RightFaceLedsRed', 'LeftFaceLedsRed'])
proxyLED.createGroup("GreenLeds", ['RightFaceLedsGreen', 'LeftFaceLedsGreen'])
proxyLED.createGroup("BlueLeds", ['RightFaceLedsBlue', 'LeftFaceLedsBlue'])


emotionColors = [(0.,0.,0.), 
				 (0.,75./255,0.),
				 (200./255,120./255,0.),
				 (255./255,255./255,0.)
				 ]

TARGET_CLASSES = ['Neutral', 'Disgust', 'Happiness', 'Surprise']		# in order of classes

for n in range(1):
	for i in range(4):

		emotion = i		# current emotion = index into TARGET_CLASSES and emotionColors

		#tts.say(TARGET_CLASSES[emotion])								# Say new emotion
		proxyLED.setIntensity("RedLeds", emotionColors[emotion][0])		# Set LEDs
		proxyLED.setIntensity("GreenLeds", emotionColors[emotion][1])
		proxyLED.setIntensity("BlueLeds", emotionColors[emotion][2])

		time.sleep(1.)

emotion = 0

proxyLED.setIntensity("RedLeds", emotionColors[emotion][0])
proxyLED.setIntensity("GreenLeds", emotionColors[emotion][1])
proxyLED.setIntensity("BlueLeds", emotionColors[emotion][2])

print emotionColors[emotion][1]

# proxyLED.setIntensity("RedLeds", 0.0)
# proxyLED.setIntensity("GreenLeds", 1.0)
# proxyLED.setIntensity("BlueLeds", 0.0)
#print proxyLED.listLEDs()
#print proxyLED.listGroups()
