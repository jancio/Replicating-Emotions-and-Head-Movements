# Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
# Duration: October 2016 - May 2017
####################################################################################################### 
# Similar to HPDdisplay.py BUT used only for Whole system evaluation:
# It does not connect to the robot (instead of IP:PORT it receives videoID from HPD),
# - only logs the measured angles (yaw, pitch) into file. 
# Need to specify paths!
# For this script to be called by HPD: replace "HPDdisplay" with "HPDdisplayExperiment" in /HeadPoseReplication/src/DemoTracker.cpp 
#######################################################################################################


import numpy as np

outFile = "/home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/detectorsOutOnHumanVideos/Group2/"
videoID = ""
anglesYaw = []
anglesPitch = []


# Set output file
def initRobot(vID):
	global videoID
	videoID = vID

def moveHead(angleYaw_measured, anglePitch_measured, timeStep):
	anglesYaw.append(angleYaw_measured)
	anglesPitch.append(anglePitch_measured)

def finalize():
	# Save data
	dataOut = np.array([
		[videoID] * len(anglesYaw), 				# videoIDs
		range(1, len(anglesYaw) + 1), 				# frame numbers
		anglesYaw, 									# positions
		anglesPitch						
		])
	np.savetxt(outFile + "HPD_" + videoID + ".dat", dataOut.T, delimiter = ",", fmt="%s")

#print "Python code loaded ..."