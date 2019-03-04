#######################################################################################################
# Author: Jan Ondras
# Institution: University of Cambridge
# Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
# Duration: October 2016 - May 2017
###########################################################################################################
# Filter head pose data (generated from human videos)
# Input: from HPD_data_G2.dat 
# Output: HPD_data_filtered_G2.dat
# uses information about videos (durations, frame counts) from file videoID_duration_frames_G2.dat
###########################################################################################################
import numpy as np
from matplotlib import pyplot as plt
from KFClass import KFOnline
import time

# Load data
dataVideo = np.genfromtxt('./videoID_duration_frames_G2.dat', delimiter=',', dtype=str)		# video ID | DURATION (sec) | NUMBER OF FRAMES
dataHPD = np.genfromtxt('./HPD_data_G2.dat', delimiter=',', dtype=str)						# videoID | frame number | angleYaw | anglePitch
outFile = './HPD_data_filtered_G2.dat'														# videoID | filteredAngleYaw | filteredAnglePitch | filteredVelocityYaw | filteredVelocityPitch

# Initialisation
anglesYaw_filtered = []
anglesPitch_filtered = []
velocitiesYaw_filtered = []
velocitiesPitch_filtered = []
qY = 1.79
qP = 0.63
rY = 8e-5
rP = 6e-5
# Constraints on Angle, Angular velocity; (radians)
x_yaw_max = np.array([2.0857, 8.26797])
x_yaw_min = np.array([-2.0857, -8.26797])
x_pitch_max = np.array([0.200015, 7.19407])
x_pitch_min = np.array([-0.330041, -7.19407])
# Velocity interpolation coefficients
K = 0.6 # parameter - interpolate between: MAX & FILTERED velocity
K2 = 0.5 # if below K*MAX then interpolate btw: MIN=K*MAX & FILTERED


for video in dataVideo:
	videoID = video[0]
	duration = float(video[1])
	frameCnt = len([x[0] for x in dataHPD if x[0] == videoID])
	dt = duration / frameCnt

	measurementsY = [x[2] for x in dataHPD if x[0] == videoID]
	measurementsP = [x[3] for x in dataHPD if x[0] == videoID]

	# Initialize Kalman Filter; with constraints (optional); without constraints => have to bound velocities to 1.0
	mykf_Y = KFOnline(dt=dt, q=qY, r=rY, init_P_post=np.matrix('1 0 0; 0 1 0; 0 0 1'), init_x_est_post=np.matrix('0; 0; 0'), x_min=x_yaw_min, x_max=x_yaw_max)
	mykf_P = KFOnline(dt=dt, q=qP, r=rP, init_P_post=np.matrix('1 0 0; 0 1 0; 0 0 1'), init_x_est_post=np.matrix('0; 0; 0'), x_min=x_pitch_min, x_max=x_pitch_max)
	# Filter
	mykf_Y.updateAll(np.asfarray(measurementsY))
	mykf_P.updateAll(np.asfarray(measurementsP))

	# Log positions
	anglesYaw_filtered.extend(mykf_Y.getEstPositionAsArray().tolist())
	anglesPitch_filtered.extend(mykf_P.getEstPositionAsArray().tolist())

	velocitiesYaw_raw = mykf_Y.getEstVelocityAsArray()
	velocitiesPitch_raw = mykf_P.getEstVelocityAsArray()

	for i in range(len(velocitiesYaw_raw)):
		################################
		# OPTIONS TO SET VELOCITY
		################################

		# OPTION 1: - gives later responses -> but smoother
		# velocitiesYaw_raw[i] =  abs(velocitiesYaw_raw[i]) / x_yaw_max[1]
		# velocitiesPitch_raw[i] = abs(velocitiesPitch_raw[i]) / x_pitch_max[1]

		# Interpolation: 1
		# velocitiesYaw_raw[i] = K +  (abs(velocitiesYaw_raw[i])*(1.-K) / x_yaw_max[1])
		# velocitiesPitch_raw[i] = K + (abs(velocitiesPitch_raw[i])*(1.-K) / x_pitch_max[1])

		# Interpolation: 2
		# If more than minimal velocity then leave it; else interpolate btw filtered and max
		if abs(velocitiesYaw_raw[i]) > K*x_yaw_max[1]:
			velocitiesYaw_raw[i] = abs(velocitiesYaw_raw[i]) / x_yaw_max[1]
		else:
			velocitiesYaw_raw[i] = K2*K +  (abs(velocitiesYaw_raw[i])*(1.-K2) / x_yaw_max[1])

		if abs(velocitiesPitch_raw[i]) > K*x_pitch_max[1]:
			velocitiesPitch_raw[i] = abs(velocitiesPitch_raw[i]) / x_pitch_max[1]
		else:
			velocitiesPitch_raw[i] = K*K2 +  (abs(velocitiesPitch_raw[i])*(1.-K2) / x_pitch_max[1])

		# OPTION 2: maximum (fixed) - because always behind, but on real very bad - too jerky!
		# velocitiesYaw_raw[i] = 1.0
		# velocitiesPitch_raw[i] = 1.0

		# at this point the raw is actually filtered
		velocitiesYaw_filtered.append(velocitiesYaw_raw[i])
		velocitiesPitch_filtered.append(velocitiesPitch_raw[i])


dataOut = np.array([
	dataHPD[:, 0], 								# videoIDs
	dataHPD[:, 1],								# frame numbers
	anglesYaw_filtered,							# positions
	anglesPitch_filtered,
	velocitiesYaw_filtered,						# velocities
	velocitiesPitch_filtered
	])
np.savetxt(outFile, dataOut.T, delimiter = ",", fmt="%s")