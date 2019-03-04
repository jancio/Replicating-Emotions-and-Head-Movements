#######################################################################################################
# Author: Jan Ondras
# Institution: University of Cambridge
# Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
# Duration: October 2016 - May 2017
####################################################################################################### 
# Kalman Filter Class Module:
# - based on constrained-state Kalman filter with minimum jerk model
#
# - http://academic.csuohio.edu/simond/pubs/IETKalman.pdf
# - https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20030018910.pdf
#
# used in real-time replication of head movements by HPDdisplay.py and for various evaluations.
# Usage: from KFClass import KFOnline
# Simple testing of this module at the end of this file.
#######################################################################################################

import time
import numpy as np
from cvxopt import matrix, solvers
import matplotlib.pyplot as plt



class KFOnline:
	'''
	Kalman Filter Class,
	state has dimension 3 (angle, angular velocity, angular acceleration),
	constraints on (angle, angular velocity) are optional - only if supplied,
	can filter iteratively or in batch,
	with built in plotting functions
	'''

	def __init__(self, dt, q, r, init_P_post, init_x_est_post, x_min=None, x_max=None):
		""" 
		Constructor

		Args:
		dt : double
			default timestep for filter
		q : double
			process noise parameter
		r : double
			measurement noise parameter
		init_P_post : numpy.matrix of doubles
			initial (3x3) covariance matrix
		init_x_est_post : numpy.matrix of doubles
			initial state, dimensions (3x1)
		x_min : numpy.array of doubles
			(optional)
			array (length 3) of state constraints - minima
		x_max : numpy.array of doubles
			(optional)
			array (length 3) of state constraints - maxima

		Returns:
		-	 				
		"""

		self.n_iter = 0								# iteration counter
		self.N = 3
		self.dt = dt
		self.x_sz = (self.N, 1)					# state vector dimensions
		self.P_sz = (self.N, self.N)

		self.x_min = x_min
		self.x_max = x_max

		self.x_est_prior = [] 
		self.x_est_post =  [] 
		self.P_prior = [] 
		self.P_post = [] 
		self.K = [] 
		self.measurements = []

		self.Q = np.matrix([[0,0,0], [0,0,0], [0,0,q]])					# process variance / noise matrix
		self.R = np.matrix([[r]])										# measurement/observation variance/noise matrix
		self.F = np.matrix([[1, dt, dt*dt/2], [0, 1, dt], [0, 0, 1]])	# transition matrix
		self.H = np.matrix('1 0 0')										# measurement matrix

		self.x_est_prior.append(np.zeros(self.x_sz))
		self.x_est_post.append(np.zeros(self.x_sz))
		self.P_prior.append(np.zeros(self.P_sz))
		self.P_post.append(np.zeros(self.P_sz))
		self.K.append(np.zeros(self.x_sz))								# Kalman gain

		self.P_post[0] = init_P_post 			#np.matrix('1 0 0; 0 1 0; 0 0 1')
		self.x_est_post[0] = init_x_est_post 	#np.matrix('0; 0; 0')

	def update(self, measurement, dt_new=None):
		""" 
		Update (both prediction and correction steps) of Kalman filter, when new measurement comes in.

		Args:
		measurement : double
			measured angle - yaw or pitch
		dt_new : double
			(optional)
			current time step to use, if not supplied then the default time step specified in constructor is used

		Returns:
			(a, av, aa)	: doubles
			tuple of new state estimate: angle (a), angular velocity (av), angular acceleration (aa)
		"""
		self.n_iter += 1 
		self.x_est_prior.append(np.zeros(self.x_sz))
		self.x_est_post.append(np.zeros(self.x_sz))
		self.P_prior.append(np.zeros(self.P_sz))
		self.P_post.append(np.zeros(self.P_sz))
		self.K.append(np.zeros(self.x_sz))
		self.measurements.append(measurement)		# log measurement
		if dt_new == None:
			F = self.F 																	# transition matrix as in previous step
		else:
			F = np.matrix([[1, dt_new, dt_new*dt_new/2], [0, 1, dt_new], [0, 0, 1]])	# new transition matrix

		# Time update (prediction)
		self.P_prior[self.n_iter] = F*self.P_post[self.n_iter-1]*F.T + self.Q 
		self.x_est_prior[self.n_iter] = F*self.x_est_post[self.n_iter-1]
		# Measurement update (correction)
		self.K[self.n_iter] = self.P_prior[self.n_iter]*self.H.T / (self.H*self.P_prior[self.n_iter]*self.H.T + self.R)[0,0]
		self.x_est_post[self.n_iter] = self.x_est_prior[self.n_iter] + self.K[self.n_iter]*(measurement - self.H*self.x_est_prior[self.n_iter])[0,0]
		self.P_post[self.n_iter] = (np.identity(self.N) - self.K[self.n_iter]*self.H)*self.P_prior[self.n_iter]

		# Constrain the position naively
		''' very simple without adjustment of velocity and acceleration
		if(self.x_min != None):	
			self.x_est_post[self.n_iter][0,0] = max(self.x_est_post[self.n_iter][0,0], self.x_min[0])

		if(self.x_max != None):
			self.x_est_post[self.n_iter][0,0] = min(self.x_est_post[self.n_iter][0,0], self.x_max[0])
		'''

		# Constrain the position and velocity - quadratic programming
		if self.x_min != None and self.x_max != None:	
			# inverse of state covariance matrix => max probability estimate subject to constraints
			W = self.P_post[self.n_iter].I

			P = 2*matrix(np.array(W, dtype='d'))	
			q = matrix(np.array( -2 * W.T * self.x_est_post[self.n_iter] , dtype='d'))
			# G = matrix(np.array([ [1,0,0], [-1,0,0] ], dtype='d'))						# if only position is constrained
			# h = matrix(np.array([self.x_max[0], -self.x_min[0]], dtype='d'))				# if only position is constrained
			G = matrix(np.array([ [1,0,0], [-1,0,0], [0,1,0], [0,-1,0] ], dtype='d'))							# if both position and velocity are constrained
			h = matrix(np.array([self.x_max[0], -self.x_min[0], self.x_max[1], -self.x_min[1]], dtype='d'))		# if both position and velocity are constrained

			# Suppressed output from QP solver
			solvers.options['show_progress'] = False
			sol = solvers.qp(P,q,G,h)
			# sol['x'] = x = argmin( x.T*W *x - 2*x_est_post.T*W*x )

			# If optimal solution was found, then adjust the state estimate x_est_post
			if sol['status'] == 'optimal':
				self.x_est_post[self.n_iter] = np.array(sol['x'])
			else:
				print "not optimal ... !"

		# Equivalent to call to getLastEstState():
		# Return new state estimate: angle, angular velocity, angular acceleration
		return (self.x_est_post[self.n_iter][0,0], self.x_est_post[self.n_iter][1,0], self.x_est_post[self.n_iter][2,0])

	def updateAll(self, measurements):
		""" 
		Update (both prediction and correction steps) in batch, when all the measurements are given. 
		Calls method update(m) for each measurement.

		Args:
		measurements : numpy.array of doubles
			array of measured angles - yaw or pitch

		Returns:
		-
		"""
		for m in measurements:
			self.update(m)

	def getEstStateAsArray(self):
		""" 
		Get all state estimates.

		Args:
		-

		Returns:
		arr : numpy.array of doubles
			(nx3) array of all sate estimates, 
			n = number of measurements so far, 
			3 elements of array along second dimension are: angle, angular velocity, angular acceleration
		"""
		if self.n_iter == 0:
			return np.empty(0)
		return np.asarray(self.x_est_post[1:])[:,:,0]

	def getEstPositionAsArray(self):
		""" 
		Get all estimates of angle.

		Args:
		-

		Returns:
		arr : numpy.array of doubles
			array (length = number of measurements so far) of all estimates of angle
		"""
		if self.n_iter == 0:
			return np.empty(0)
		return np.asarray(self.x_est_post[1:])[:,0,0]

	def getEstVelocityAsArray(self):
		""" 
		Get all estimates of angular velocity.

		Args:
		-

		Returns:
		arr : numpy.array of doubles
			array (length = number of measurements so far) of all estimates of angular velocity
		"""
		if self.n_iter == 0:
			return np.empty(0)
		return np.asarray(self.x_est_post[1:])[:,1,0]

	def getEstAccelerationAsArray(self):
		""" 
		Get all estimates of angular acceleration.

		Args:
		-

		Returns:
		arr : numpy.array of doubles
			array (length = number of measurements so far) of all estimates of angular acceleration
		"""
		if self.n_iter == 0:
			return np.empty(0)
		return np.asarray(self.x_est_post[1:])[:,2,0]

	def getLastEstState(self):
		""" 
		Get current state estimate.

		Args:
		-

		Returns:
		arr : numpy.array of doubles
			array (length 3) of current state estimate, 3 elements of array are: angle, angular velocity, angular acceleration
		"""
		return self.x_est_post[self.n_iter][:,0]

	def getLastEstPosition(self):
		""" 
		Get current estimate of position/angle.

		Args:
		-

		Returns:
		angle : double
			angle of current state estimate
		"""
		return self.x_est_post[self.n_iter][0,0]

	def getLastEstVelocity(self):
		""" 
		Get current estimate of angular velocity.

		Args:
		-

		Returns:
		angularVel : double
			angular velocity of current state estimate
		"""
		return self.x_est_post[self.n_iter][1,0]

	def getLastEstAcceleration(self):
		""" 
		Get current estimate of angular acceleration.

		Args:
		-

		Returns:
		angularAcc : double
			angular acceleration of current state estimate
		"""
		return self.x_est_post[self.n_iter][2,0]

	def plotResults(self, titles, ylabels, xlabel='iteration', show=True):
		""" 
		Plot results as filtered over time: measured, filtered and bounds (state constraints)

		Args:
		titles : numpy.array of strings
			titles for 3 plots (angle, angular veleocity, angular acceleration)
		ylabels : numpy.array of strings
			y-axis labels for 3 plots (angle, angular veleocity, angular acceleration)
		xlabel : string
			(optional)
			x-axis label common for all 3 plots (angle, angular veleocity, angular acceleration)
		show : boolean
			(optional)
			if True then display the graphs immediately

		Returns:
		-
		"""
		plt.figure()
		t = range(self.n_iter)

		for i in range(len(titles)):

			plt.subplot(len(titles), 1, i+1)
			if i == 0:
				plt.scatter(t, self.measurements, c='red', marker='+', label='measured')	# measured
			plt.plot(t, self.getEstStateAsArray()[:,i], 'x-', label='filtered')				# filtered
			if(self.x_min != None and i < len(self.x_min)):	
				plt.axhline(y=self.x_min[i], color='green', label='min/max constraints')	# constraints
			if(self.x_max != None and i < len(self.x_max)):	
				plt.axhline(y=self.x_max[i], color='green')
			plt.xlabel(xlabel)
			plt.ylabel(ylabels[i])
			plt.title(titles[i])
			plt.legend()
		if show:
			plt.show()

########################################################################################################################################
# Testing:
########################################################################################################################################
'''

########################################
# Test iterative updates:
inFile = "./testData/hpData1.dat"
measurements = np.genfromtxt(inFile, usecols = (0, 1))

mykf_Y = KFOnline(dt=1.0/30, q=0.5, r=0.01, init_P_post=np.matrix('1 0 0; 0 1 0; 0 0 1'), init_x_est_post=np.matrix('0; 0; 0'))
mykf_P = KFOnline(dt=1.0/30, q=0.5, r=0.01, init_P_post=np.matrix('1 0 0; 0 1 0; 0 0 1'), init_x_est_post=np.matrix('0; 0; 0'))
for i, m in enumerate(measurements, start=1):
	mykf_Y.update(m[0], 1.0/(i*10))				# to test changing dt over time
	mykf_P.update(m[1], 1.0/(i*10))
	# mykf_Y.update(m[0])
	# mykf_P.update(m[1])

xlabels = ['angle (rad)', 'angular velocity (rad.s-1)', 'angular acceleration (rad.s-2)']
mykf_Y.plotResults(['Yaw angle', 'Yaw angular velocity', 'Yaw angular acceleration'], xlabels, show=False)
mykf_P.plotResults(['Pitch angle', 'Pitch angular velocity', 'Pitch angular acceleration'], xlabels)
'''
########################################
# Test updateAll:
'''
mykf_Y = KFOnline(dt=1.0/30, q=0.5, r=0.01, init_P_post=np.matrix('1 0 0; 0 1 0; 0 0 1'), init_x_est_post=np.matrix('0; 0; 0'))
mykf_P = KFOnline(dt=1.0/30, q=0.5, r=0.01, init_P_post=np.matrix('1 0 0; 0 1 0; 0 0 1'), init_x_est_post=np.matrix('0; 0; 0'))
inFile = "./testData/hpData1.dat"
measurements = np.genfromtxt(inFile, usecols = (0, 1))
mykf_Y.updateAll(measurements[:,0])
mykf_P.updateAll(measurements[:,1])

xlabels = ['angle (rad)', 'angular velocity (rad.s-1)', 'angular acceleration (rad.s-2)']
mykf_Y.plotResults(['Yaw angle', 'Yaw angular velocity', 'Yaw angular acceleration'], xlabels, show=False)
mykf_P.plotResults(['Pitch angle', 'Pitch angular velocity', 'Pitch angular acceleration'], xlabels)
'''

###############################################
# Test with constraints:
'''
inFile = "./testData/hpData1.dat"
measurements = np.genfromtxt(inFile, usecols = (0, 1))

# Constraints on Angle, Angular velocity, Angular acceleration; (radians)
x_yaw_max = np.array([2.0857, 8.26797])
x_yaw_min = np.array([-2.0857, -8.26797])

x_pitch_max = np.array([0.200015, 7.19407, 100.])
x_pitch_min = np.array([-0.330041, -7.19407, -100.])


# Initialize Kalman Filter; with constraints (optional)
mykf_Y = KFOnline(dt=1.0/30, q=0.5, r=0.01, init_P_post=np.matrix('1 0 0; 0 1 0; 0 0 1'), init_x_est_post=np.matrix('0; 0; 0'), x_min=x_yaw_min, x_max=x_yaw_max)
mykf_P = KFOnline(dt=1.0/30, q=0.5, r=0.01, init_P_post=np.matrix('1 0 0; 0 1 0; 0 0 1'), init_x_est_post=np.matrix('0; 0; 0'), x_min=x_pitch_min, x_max=x_pitch_max)
mykf_P_noC= KFOnline(dt=1.0/30, q=0.5, r=0.01, init_P_post=np.matrix('1 0 0; 0 1 0; 0 0 1'), init_x_est_post=np.matrix('0; 0; 0'))

mykf_Y.updateAll(measurements[:,0])

tStart = time.time()
mykf_P_noC.updateAll(measurements[:,1])
print "Time without constraints: %f" %(time.time() - tStart)

tStart = time.time()
mykf_P.updateAll(measurements[:,1])
print "Time with constraints: %f" %(time.time() - tStart)		# cca 10 times slower !!!

xlabels = ['angle (rad)', 'angular velocity (rad.s-1)', 'angular acceleration (rad.s-2)']
mykf_Y.plotResults(['Yaw angle', 'Yaw angular velocity', 'Yaw angular acceleration'], xlabels, show=False)
mykf_P.plotResults(['Pitch angle', 'Pitch angular velocity', 'Pitch angular acceleration'], xlabels)
'''