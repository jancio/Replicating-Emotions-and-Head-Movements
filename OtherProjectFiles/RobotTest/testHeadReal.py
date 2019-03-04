#######################################################################################################
# Author: Jan Ondras
# Institution: University of Cambridge
# Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
# Duration: October 2016 - May 2017
####################################################################################################### 
# This is to do simple test of robot head movements.
#######################################################################################################


from naoqi import ALProxy
import numpy as np
from matplotlib import pyplot as plt
from KFClass import KFOnline
import time


inFile = "./../../HeadPoseReplication/testData/hpData1.dat"		# Test using test data, attached in specified folder
measurements = np.genfromtxt(inFile, usecols = (0, 1))

FPS = 40.0		# average from measurements of timeSteps
dt = 1.0/FPS 	# default time step

# Constraints on Angle, Angular velocity; (radians)
x_yaw_max = np.array([2.0857, 8.26797])
x_yaw_min = np.array([-2.0857, -8.26797])

x_pitch_max = np.array([0.200015, 7.19407])
x_pitch_min = np.array([-0.330041, -7.19407])

# Initialize Kalman Filter; with constraints (optional); without constraints => have to bound velocities to 1.0
# mykf_Y = KFOnline(dt=dt, q=0.5, r=0.01, init_P_post=np.matrix('1 0 0; 0 1 0; 0 0 1'), init_x_est_post=np.matrix('0; 0; 0')) 	# without constraints
# mykf_P = KFOnline(dt=dt, q=0.5, r=0.01, init_P_post=np.matrix('1 0 0; 0 1 0; 0 0 1'), init_x_est_post=np.matrix('0; 0; 0'))
mykf_Y = KFOnline(dt=dt, q=0.5, r=0.01, init_P_post=np.matrix('1 0 0; 0 1 0; 0 0 1'), init_x_est_post=np.matrix('0; 0; 0'), x_min=x_yaw_min, x_max=x_yaw_max) # with constraints
mykf_P = KFOnline(dt=dt, q=0.5, r=0.01, init_P_post=np.matrix('1 0 0; 0 1 0; 0 0 1'), init_x_est_post=np.matrix('0; 0; 0'), x_min=x_pitch_min, x_max=x_pitch_max)


# Connect to robot
#motionProxy = ALProxy("ALMotion", "127.0.0.1", 9559)			# Virtual robot
motionProxy = ALProxy("ALMotion", "169.254.42.173", 9559)		# Real robot

motionProxy.setStiffnesses("Head", 1.0)

for m in measurements:
	angleYaw_measured = m[0]
	anglePitch_measured = m[1]

	# Options to set timestep
	# OPTION 1: using default
	'''
	# Log the timestep only if HP was recognised in previous frame
	if timeStep != 0.0:
		timeSteps.append(timeStep)

		# Filter, get constrained estimates
		angleYaw_filtered, velocityYaw_filtered, _ = mykf_Y.update(angleYaw_measured, dt_new=timeStep)
		anglePitch_filtered, velocityPitch_filtered, _ = mykf_P.update(anglePitch_measured, dt_new=timeStep)
	else:
		# using predefined dt otherwise
		angleYaw_filtered, velocityYaw_filtered, _ = mykf_Y.update(angleYaw_measured)
		anglePitch_filtered, velocityPitch_filtered, _ = mykf_P.update(anglePitch_measured)
	'''
	'''
	# OPTION 2: using last timeStep if possible
	if timeStep != 0.0:
		timeSteps.append(timeStep)

		# Filter, get constrained estimates
		angleYaw_filtered, velocityYaw_filtered, _ = mykf_Y.update(angleYaw_measured, dt_new=timeStep)
		anglePitch_filtered, velocityPitch_filtered, _ = mykf_P.update(anglePitch_measured, dt_new=timeStep)

	elif len(timeSteps) != 0:
		angleYaw_filtered, velocityYaw_filtered, _ = mykf_Y.update(angleYaw_measured, dt_new=timeSteps[-1])
		anglePitch_filtered, velocityPitch_filtered, _ = mykf_P.update(anglePitch_measured, dt_new=timeSteps[-1])
	else:
		# using predefined dt otherwise = happens only once
		angleYaw_filtered, velocityYaw_filtered, _ = mykf_Y.update(angleYaw_measured)
		anglePitch_filtered, velocityPitch_filtered, _ = mykf_P.update(anglePitch_measured)
	
	# OPTION 3: using only default dt
	'''
	# Filter, get constrained estimates
	angleYaw_filtered, velocityYaw_filtered, _ = mykf_Y.update(angleYaw_measured)
	anglePitch_filtered, velocityPitch_filtered, _ = mykf_P.update(anglePitch_measured)
	# if timeStep != 0.0:
	# 	timeSteps.append(timeStep)
	


	# OPTIONS to set velocity:

	# OP 1 - According to filtered output from Kalman filter: gives very late responses
	# velocityYaw_filtered =  abs(velocityYaw_filtered) / x_yaw_max[1]
	# velocityPitch_filtered = abs(velocityPitch_filtered) / x_pitch_max[1]

	# OP 2 -  Fixed: on real ... too jerky
	velocityYaw_filtered = 1.0
	velocityPitch_filtered = 1.0

	# OP 3 - if constraints not in filter
	# Naively constrain velocity as fraction of max velocity
	#velocityYaw_filtered = min(abs(mykf_Y.getLastEstVelocity()) / x_yaw_max[1], 1.0)
	#velocityPitch_filtered = min(abs(mykf_P.getLastEstVelocity()) / x_pitch_max[1], 1.0)

	# Send commands to the robot, velocity as fraction of max velocity 
	motionProxy.setAngles("HeadYaw", angleYaw_filtered, velocityYaw_filtered)
	motionProxy.setAngles("HeadPitch", anglePitch_filtered, velocityPitch_filtered)
	time.sleep(dt)


motionProxy.setStiffnesses("Head", 0.0)