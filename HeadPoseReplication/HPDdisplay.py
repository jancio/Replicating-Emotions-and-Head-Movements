#######################################################################################################
# Author: Jan Ondras
# Institution: University of Cambridge
# Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
# Duration: October 2016 - May 2017
####################################################################################################### 
# This is the main component of Head Pose Filter:
# the functions of this file are called by HPD. 
# It establishes connection to the robot, 
# given the measured head pose, applies Kalman filter,
# then sends corresponding head movement commands to the robot. 
#######################################################################################################

from naoqi import ALProxy
import numpy as np
from matplotlib import pyplot as plt
from KFClass import KFOnline
import time

# To measure the latency
latencyMeasurements = []
outFileLatency = "/home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/DisplayingModule/LatencyEvaluation/hpStopTimes.dat"

'''
Angular velocity constraints: determined from error messages: (not found in documentation ...)
Yaw: Max/Min velocity  : +/-8.26797 rad.s-1
Pitch: Max/Min velocity  : +/-7.19407 rad.s-1
'''
# To record measured and filtered data
outFile = "./generatedData/hpData_" + str(int(time.time())) + ".dat"
timeSteps = []	# to log time steps between consecutive frames
FPS = 40.0		# average from measurements of timeSteps
dt = 1.0/FPS	# default time step
qY = 1.79		# process noise for yaw rotations - for Kalman filter
qP = 0.63		# process noise for pitch rotations - for Kalman filter
rY = 8e-5		# measurement noise for yaw rotations - for Kalman filter
rP = 6e-5		# measurement noise for pitch rotations - for Kalman filter

# Constraints on Angle, Angular velocity; (in radians)
x_yaw_max = np.array([2.0857, 8.26797])
x_yaw_min = np.array([-2.0857, -8.26797])

x_pitch_max = np.array([0.200015, 7.19407])
x_pitch_min = np.array([-0.330041, -7.19407])

# Initialize 2 Kalman Filters; with constraints (optional); if without constraints => have to bound velocities to 1.0
mykf_Y = KFOnline(dt=dt, q=qY, r=rY, init_P_post=np.matrix('1 0 0; 0 1 0; 0 0 1'), init_x_est_post=np.matrix('0; 0; 0'), x_min=x_yaw_min, x_max=x_yaw_max)
mykf_P = KFOnline(dt=dt, q=qP, r=rP, init_P_post=np.matrix('1 0 0; 0 1 0; 0 0 1'), init_x_est_post=np.matrix('0; 0; 0'), x_min=x_pitch_min, x_max=x_pitch_max)

# Since the filtered velocity is not appropriate (usually too slow) to display directly, we do simple interpolation with the following parameters set empirically
K=0.6 	# parameter - interpolate between: MAX & FILTERED velocity
K2=0.5 	# if velocity is below K*MAX then interpolate btw: MIN=K*MAX & FILTERED

# Connect to robot
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
	global motionProxy
	motionProxy = ALProxy("ALMotion", ip, int(port))
	motionProxy.setStiffnesses("Head", 1.0)

# Velocity is non-negative absolute value [] !
def moveHead(angleYaw_measured, anglePitch_measured, timeStep):
	""" 
	Given measured yaw and pitch angles (from HPD) for a given frame, 
	apply Kalman filter to get filtered estimates of these two angles and associated angular velocities. 
	Then send these as command to the robot to move the head to desired position with appropriate velocity.

	Args:
	angleYaw_measured : double
		head pose yaw angle measured by HPD 
	anglePitch_measured : double
		head pose pitch angle measured by HPD 
	timeStep : double
		time step between last two frames measured by HPD 

	Returns:
	-	 				
	"""
	
	###################################################
	# OPTIONS TO SET CURRENT TIMESTEP for Kalman filter
	###################################################
	# OPTION 1: average all previous timesteps (default timestep dt used only first time)
	# if (timeStep == 0.0) and (len(timeSteps) == 0):
	# 	angleYaw_filtered, velocityYaw_filtered, _ = mykf_Y.update(angleYaw_measured)
	# 	anglePitch_filtered, velocityPitch_filtered, _ = mykf_P.update(anglePitch_measured)
	# else:
	# 	if timeStep != 0.0:
	# 		timeSteps.append(timeStep)
	# 	# Precondition: timeSteps must have non-zero length
	# 	angleYaw_filtered, velocityYaw_filtered, _ = mykf_Y.update(angleYaw_measured, dt_new=np.mean(timeSteps))
	# 	anglePitch_filtered, velocityPitch_filtered, _ = mykf_P.update(anglePitch_measured, dt_new=np.mean(timeSteps))

	# OPTION 2: use last timeStep (default timestep dt used only first time)
	# This is most sensible option
	if (timeStep == 0.0) and (len(timeSteps) == 0):
		angleYaw_filtered, velocityYaw_filtered, _ = mykf_Y.update(angleYaw_measured)
		anglePitch_filtered, velocityPitch_filtered, _ = mykf_P.update(anglePitch_measured)
	else:
		if timeStep != 0.0:
			timeSteps.append(timeStep)
		# Precondition: timeSteps must have non-zero length
		angleYaw_filtered, velocityYaw_filtered, _ = mykf_Y.update(angleYaw_measured, dt_new=timeSteps[-1])
		anglePitch_filtered, velocityPitch_filtered, _ = mykf_P.update(anglePitch_measured, dt_new=timeSteps[-1])

	# OPTION 3: using only default dt all the time	
	# Filter, get constrained estimates
	# angleYaw_filtered, velocityYaw_filtered, _ = mykf_Y.update(angleYaw_measured)
	# anglePitch_filtered, velocityPitch_filtered, _ = mykf_P.update(anglePitch_measured)
	# if timeStep != 0.0:
	# 	timeSteps.append(timeStep)
	

	################################################################################################
	# OPTIONS TO SET VELOCITY based on filtered estimate from Kalman filter
	################################################################################################

	# OPTION 1: - gives later responses -> but smoother
	# velocityYaw_filtered =  abs(velocityYaw_filtered) / x_yaw_max[1]
	# velocityPitch_filtered = abs(velocityPitch_filtered) / x_pitch_max[1]

	# Interpolation: 1
	# velocityYaw_filtered = K +  (abs(velocityYaw_filtered)*(1.-K) / x_yaw_max[1])
	# velocityPitch_filtered = K + (abs(velocityPitch_filtered)*(1.-K) / x_pitch_max[1])

	# Interpolation: 2
	# If more than minimal velocity then leave it; else interpolate btw filtered and max
	if abs(velocityYaw_filtered) > K*x_yaw_max[1]:
		velocityYaw_filtered = abs(velocityYaw_filtered) / x_yaw_max[1]
	else:
		velocityYaw_filtered = K2*K +  (abs(velocityYaw_filtered)*(1.-K2) / x_yaw_max[1])

	if abs(velocityPitch_filtered) > K*x_pitch_max[1]:
		velocityPitch_filtered = abs(velocityPitch_filtered) / x_pitch_max[1]
	else:
		velocityPitch_filtered = K*K2 +  (abs(velocityPitch_filtered)*(1.-K2) / x_pitch_max[1])

	# OPTION 2: maximum (fixed) - but on real robot very bad - too jerky!
	# velocityYaw_filtered = 1.0
	# velocityPitch_filtered = 1.0

	# Send commands to the robot, velocity as a fraction of max velocity 
	motionProxy.setAngles("HeadYaw", angleYaw_filtered, velocityYaw_filtered)
	motionProxy.setAngles("HeadPitch", anglePitch_filtered, velocityPitch_filtered)

	# Log latency measurements
	latencyMeasurements.append(1000*time.time())


def finalize():
	""" 
	Called when HPD got signal to shutdown.
	Visualise the measured and filtered head pose (namely, angle, angular velocity, angular acceleration) from the runtime 
	and optionally (need to specify manually at the end of this function) 
	save the data and latency measurements (NO by default). 
	
	Args:
	-
	Returns:
	-	 				
	"""
	motionProxy.setStiffnesses("Head", 0.0)

	# Plot results:
	xlabels = ['angle (rad)', 'angular velocity (rad.s-1)', 'angular acceleration (rad.s-2)']
	mykf_Y.plotResults(['Yaw angle', 'Yaw angular velocity', 'Yaw angular acceleration'], xlabels, show=False)
	mykf_P.plotResults(['Pitch angle', 'Pitch angular velocity', 'Pitch angular acceleration'], xlabels, show=False)

	# Plot time steps
	avg = np.mean(timeSteps)
	std = np.std(timeSteps)
	plt.figure()
	plt.plot(range(1, len(timeSteps) + 1), timeSteps, 'rx', label='measured time steps')	# measured
	plt.axhline(y=avg, label='average: ' + str(avg) + ' +/- ' + str(std) + ' (' + str(100.0*std/avg) + '%)')
	plt.xlabel('iteration')
	plt.ylabel('time step (sec)')
	plt.title('Measured time step vs. iteration')
	plt.legend(loc='best')
	plt.show()

	# # Save measured and filtered data: in format: YawMeasured|PitchMeasured|YawFiltered|PitchFiltered
	# data = np.array([mykf_Y.measurements, mykf_P.measurements, mykf_Y.getEstPositionAsArray(), mykf_P.getEstPositionAsArray()])
	# np.savetxt(outFile, data.T, delimiter = " ")

	# Save latency measurements
	#np.savetxt(outFileLatency, np.array(latencyMeasurements), delimiter = " ")

print "Python code loaded ..."