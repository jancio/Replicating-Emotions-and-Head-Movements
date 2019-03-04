#######################################################################################################
# Author: Jan Ondras
# Institution: University of Cambridge
# Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
# Duration: October 2016 - May 2017
####################################################################################################### 
# Compare my Kalman Filter implementation with FilterPy library
# Compare performance!
# only YAW angle & non-constrained
#######################################################################################################
# OK it gives same resutls !!!
# Speed up: cca 2.6 times
#######################################################################################################
# => Use mine because: can add constraints & it gives improved speed ! - important for real-time

import numpy as np
import time
from matplotlib import pyplot as plt
from KFClass import KFOnline
from filterpy.kalman import KalmanFilter

#############################################################################################
# 1.) Compare on one data file
#############################################################################################

inFile = "./../../../HeaPoseReplication/testData/hpData1.dat" # Test using test data, attached in specified folder
measurements = np.genfromtxt(inFile, usecols = (0, 1))
dt = 1.0/30
q = 0.5
r = 0.01

#########################
# My KF:
mykf_Y = KFOnline(dt=dt, q=q, r=r, init_P_post=np.matrix('1 0 0; 0 1 0; 0 0 1'), init_x_est_post=np.matrix('0; 0; 0'))
tStart = time.time()
#mykf_Y.updateAll(measurements[:,0])
for m in measurements[:,0]:
    mykf_Y.update(m)
print "Time mine: %f" %(time.time() - tStart)

#########################
# Compare with FilterPy
f = KalmanFilter (dim_x=3, dim_z=1)
f.x = np.array([0., 0., 0.])
f.F = np.array([[1., dt, dt*dt/2], [0., 1., dt], [0., 0., 1.]])
f.H = np.array([[1.,0.,0.]])
f.P = np.array([[1.,0.,0.], [0.,1.,0.], [0.,0.,1.]])
f.Q = np.array([[0.,0.,0.], [0.,0.,0.], [0.,0.,q]])
f.R = r
predictionsFilterpy = []

tStart = time.time()
for m in measurements[:,0]:
	f.predict()
	f.update(m)
	predictionsFilterpy.append(f.x[0])
print "Time Pykalman: %f" %(time.time() - tStart)

t = range(mykf_Y.n_iter)
plt.scatter(t, mykf_Y.measurements, c='red', marker='*', label='measured')	# measured
plt.plot(t, mykf_Y.getEstPositionAsArray(), 'x-', markersize=20, label='filtered mine')	# filtered mine
plt.plot(t, predictionsFilterpy, '+-', markersize=20, label='filtered Pykalman')			# filtered Pykalman
plt.xlabel('iteration')
plt.ylabel('angle (rad)')
plt.title('Yaw angle')
plt.legend()
plt.show()

# Difference
print np.sum(mykf_Y.getEstPositionAsArray() - predictionsFilterpy)

#############################################################################################
# 2.) Compare on whole UPNA
#############################################################################################
totalTimeMy = 0.
totalTimeFilterPy = 0.
dt = 1.0/30
q = 0.5
r = 0.01
numDatapoints = 0
sumErr = 0.

# Compare 10x12=120 videos:
for i in range(1, 11):
    for j in range(1, 13):
        path = "user_" + format(i, '02d') + "_video_" + format(j, '02d')
        dataTracked = np.genfromtxt("./../UPNAtrackedZeroed/" + path + ".dat", usecols = (0, 1))
        numDatapoints += len(dataTracked)

        # My KF
        r1 = []
        mykf_Y = KFOnline(dt=dt, q=q, r=r, init_P_post=np.matrix('1 0 0; 0 1 0; 0 0 1'), init_x_est_post=np.matrix('0; 0; 0'))
        tStart = time.time()
        for m in dataTracked[:,0]:
            x = mykf_Y.update(m)
            r1.append(x[0])
        totalTimeMy += time.time() - tStart

        # FilterPy
        r2 = []
        f = KalmanFilter (dim_x=3, dim_z=1)
        f.x = np.array([0., 0., 0.])
        f.F = np.array([[1., dt, dt*dt/2], [0., 1., dt], [0., 0., 1.]])
        f.H = np.array([[1.,0.,0.]])
        f.P = np.array([[1.,0.,0.], [0.,1.,0.], [0.,0.,1.]])
        f.Q = np.array([[0.,0.,0.], [0.,0.,0.], [0.,0.,q]])
        f.R = r
        tStart = time.time()
        for m in dataTracked[:,0]:
            f.predict()
            f.update(m)
            r2.append(f.x[0])
        totalTimeFilterPy += time.time() - tStart

        sumErr += np.sum(np.absolute(np.array(r1) - np.array(r2)))

print "Over 120 videos and %d datapoints:" %(numDatapoints)
print "My KF: %f" %(totalTimeMy)
print "FilterPy's KF: %f" %(totalTimeFilterPy)
print "Speed up ~ %0.2f-times" %(totalTimeFilterPy/totalTimeMy)
print "Average error of one estimate: %0.10f rad" %(sumErr/numDatapoints)