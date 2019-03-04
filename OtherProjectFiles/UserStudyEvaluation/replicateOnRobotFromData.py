#######################################################################################################
# Author: Jan Ondras
# Institution: University of Cambridge
# Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
# Duration: October 2016 - May 2017
####################################################################################################### 
# Replicate on robot from logged data
# and automatically record the robot => generates robotVideos
# need to adjust timestep dt by measuring delays ...
#######################################################################################################

from naoqi import ALProxy
import numpy as np
from matplotlib import pyplot as plt
import time
import cv2

print time.time()

# OpenCV automatic video recording - initialisation
device_index = 0
fps = 25.0               # fps should be the minimum constant rate at which the camera can capture 
fourcc = "XVID"       
frameSize = (640,480) 
video_cap = cv2.VideoCapture(device_index)
video_writer = cv2.cv.CV_FOURCC(*fourcc)

# Load data
dataVideo = np.genfromtxt('./videoID_duration_frames_G2.dat', delimiter=',', dtype=str)		# video ID | DURATION (sec) | NUMBER OF FRAMES
dataAUD = np.genfromtxt('./AUD_data_G2.dat', delimiter=',', dtype=str)						# videoID | frame number | emotionNumber
dataHPD = np.genfromtxt('./HPD_data_filtered_G2.dat', delimiter=',', dtype=str)				# videoID | frame number | angleYaw | anglePitch | velocityYaw | velocityPitch

# Connect to robot 
#IP = '127.0.0.1'			# virtual
IP = '169.254.42.173'		# real
PORT = 9559
motionProxy = ALProxy("ALMotion", IP, PORT)
motionProxy.setStiffnesses("Head", 1.0)
proxyLED = ALProxy("ALLeds", IP, PORT)
proxyLED.createGroup("RedLeds", ['RightFaceLedsRed', 'LeftFaceLedsRed'])
proxyLED.createGroup("GreenLeds", ['RightFaceLedsGreen', 'LeftFaceLedsGreen'])
proxyLED.createGroup("BlueLeds", ['RightFaceLedsBlue', 'LeftFaceLedsBlue'])
# Colors -RBG
emotionColors = [(0.,0.,0.), 
				 (1.,0.,0.),
				 (0.,0.,1.),
				 (0.,1.,0.)
				]
# Reset to neutral
motionProxy.setAngles("HeadYaw", 0.0, 1.0)
motionProxy.setAngles("HeadPitch", 0.0, 1.0)
proxyLED.setIntensity("RedLeds", emotionColors[0][0])	
proxyLED.setIntensity("GreenLeds", emotionColors[0][1])
proxyLED.setIntensity("BlueLeds", emotionColors[0][2])
time.sleep(1.0)

timerStart = time.time()

for video in dataVideo:
	videoID = video[0]
	duration = float(video[1])
	#f1 = int(video[2])
	#f2 = len([x[0] for x in dataAUD if x[0] == videoID])
	f3 = len([x[0] for x in dataHPD if x[0] == videoID])
	frameCnt = f3	# frame count


	dt = duration / frameCnt		
	#dt -= 0.008			# might need to adjust the timestep or alternatively, later speedup the obtained robotVideos (if they are found to be shorter than humanVideos)

	emotions = [int(x[2]) for x in dataAUD if x[0] == videoID]
	anglesYaw_filtered = [float(x[2]) for x in dataHPD if x[0] == videoID]
	anglesPitch_filtered = [float(x[3]) for x in dataHPD if x[0] == videoID]
	velocitiesYaw_filtered = [float(x[4]) for x in dataHPD if x[0] == videoID]
	velocitiesPitch_filtered = [float(x[5]) for x in dataHPD if x[0] == videoID]


	# START REPLICATION
	startTime = time.time()
	print time.time()
	video_out = cv2.VideoWriter('/home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/videosRobot/Group2/' + videoID + '.avi', video_writer, fps, frameSize)

	for i in range(frameCnt):
		# Grab frame
		ret, video_frame = video_cap.read()
            if (ret==True):
                    video_out.write(video_frame)
            else:
                print "Problem --------------------------------------------"

		# Send commands to the robot
		motionProxy.setAngles("HeadYaw", anglesYaw_filtered[i], velocitiesYaw_filtered[i])
		motionProxy.setAngles("HeadPitch", anglesPitch_filtered[i], velocitiesPitch_filtered[i])

		proxyLED.setIntensity("RedLeds", emotionColors[emotions[i]][0])	
		proxyLED.setIntensity("GreenLeds", emotionColors[emotions[i]][1])
		proxyLED.setIntensity("BlueLeds", emotionColors[emotions[i]][2])
		# Sleep until next frame
		time.sleep(dt)

	# FINISHED REPLICATION
	video_out.release()
	print time.time()
	print (time.time() - startTime - duration )/frameCnt

	# Reset to neutral
	motionProxy.setAngles("HeadYaw", 0.0, 1.0)
	motionProxy.setAngles("HeadPitch", 0.0, 1.0)
	proxyLED.setIntensity("RedLeds", emotionColors[0][0])	
	proxyLED.setIntensity("GreenLeds", emotionColors[0][1])
	proxyLED.setIntensity("BlueLeds", emotionColors[0][2])

	time.sleep(1.0)


print "Measured time: "
print time.time() - timerStart

print "Cummulative true time: "
print np.sum(np.asfarray(dataVideo[:, 1]))

video_cap.release()
cv2.destroyAllWindows()






'''
# Alternative: Automatic video recording using threads, but problem with race conditions => not used

from naoqi import ALProxy
import numpy as np
from matplotlib import pyplot as plt
import time
import cv2
import threading

# Exclude 6 worst subjects ... later - excluded after recording
print time.time()

# OpenCV automatic video recording
class VideoRecorder():  
    # Video class based on openCV 
    def __init__(self):
    	self.device_index = 0
        self.fps = 25.0               # fps should be the minimum constant rate at which the camera can
        self.fourcc = "XVID"       
        self.frameSize = (640,480) 

        self.video_cap = cv2.VideoCapture(self.device_index)
        self.video_writer = cv2.cv.CV_FOURCC(*self.fourcc)

    # Video starts being recorded 
    def record(self):
        while(self.open==True):
            ret, video_frame = self.video_cap.read()
            if (ret==True):
                    self.video_out.write(video_frame)
            else:
                break
    # Finishes the video recording therefore the thread too
    def stop(self):
        if self.open==True:
            self.open=False
            self.video_out.release()

    # Launches the video recording function using a thread          
    def start(self, filename):
        self.video_out = cv2.VideoWriter(filename, self.video_writer, self.fps, self.frameSize)
        self.open = True

        video_thread = threading.Thread(target=self.record)
        video_thread.start()

    def close(self):
		self.video_cap.release()
		cv2.destroyAllWindows()

video_thread = VideoRecorder()

# Load data
dataVideo = np.genfromtxt('./videoID_duration_frames_G2.dat', delimiter=',', dtype=str)		# video ID | DURATION (sec) | NUMBER OF FRAMES
dataAUD = np.genfromtxt('./AUD_data_G2.dat', delimiter=',', dtype=str)						# videoID | frame number | emotionNumber
dataHPD = np.genfromtxt('./HPD_data_filtered_G2.dat', delimiter=',', dtype=str)				# videoID | frame number | angleYaw | anglePitch | velocityYaw | velocityPitch

# Connect to robot 
#IP = '127.0.0.1'			# virtual
IP = '169.254.42.173'		# real
PORT = 9559
motionProxy = ALProxy("ALMotion", IP, PORT)
motionProxy.setStiffnesses("Head", 1.0)
proxyLED = ALProxy("ALLeds", IP, PORT)
proxyLED.createGroup("RedLeds", ['RightFaceLedsRed', 'LeftFaceLedsRed'])
proxyLED.createGroup("GreenLeds", ['RightFaceLedsGreen', 'LeftFaceLedsGreen'])
proxyLED.createGroup("BlueLeds", ['RightFaceLedsBlue', 'LeftFaceLedsBlue'])
# Colors -RBG
emotionColors = [(0.,0.,0.), 
				 (1.,0.,0.),
				 (0.,0.,1.),
				 (0.,1.,0.)
				]
# Reset to neutral
motionProxy.setAngles("HeadYaw", 0.0, 1.0)
motionProxy.setAngles("HeadPitch", 0.0, 1.0)
proxyLED.setIntensity("RedLeds", emotionColors[0][0])	
proxyLED.setIntensity("GreenLeds", emotionColors[0][1])
proxyLED.setIntensity("BlueLeds", emotionColors[0][2])
time.sleep(1.0)

timerStart = time.time()

for video in dataVideo:
	videoID = video[0]
	if videoID[0:2] in ['13', '14', '15', '16', '17', '18', '19', '20', '21', '24', '23', '25', '26', '27', '28']:
		continue
	duration = float(video[1])
	#f1 = int(video[2])
	#f2 = len([x[0] for x in dataAUD if x[0] == videoID])
	f3 = len([x[0] for x in dataHPD if x[0] == videoID])

	# Compare number of frames - take minimum => cut off at the end (actually only 2 videos from subject 23), HPD has least #frames => f3 chosen
	frameCnt = f3
	# if f1 != f2 or f2 != f3 or f1 != f3:
	# 	print videoID, f1, f2, f3				# Gives: 23_0_2 377 377 373; 23_3_1 357 357 330
	# 	frameCnt = np.min([f1, f2, f3])

	dt = duration / frameCnt
	dt -= 0.008

	emotions = [int(x[2]) for x in dataAUD if x[0] == videoID]
	anglesYaw_filtered = [float(x[2]) for x in dataHPD if x[0] == videoID]
	anglesPitch_filtered = [float(x[3]) for x in dataHPD if x[0] == videoID]
	velocitiesYaw_filtered = [float(x[4]) for x in dataHPD if x[0] == videoID]
	velocitiesPitch_filtered = [float(x[5]) for x in dataHPD if x[0] == videoID]


	# if videoID == '13_2_1':
	# 	break
	# START REPLICATION
	startTime = time.time()
	print time.time()
	video_thread.start('/home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/HumanExperiment/videosRobot/Group2/' + videoID + '.avi')

	for i in range(frameCnt):
		# Send commands to the robot
		motionProxy.setAngles("HeadYaw", anglesYaw_filtered[i], velocitiesYaw_filtered[i])
		motionProxy.setAngles("HeadPitch", anglesPitch_filtered[i], velocitiesPitch_filtered[i])

		proxyLED.setIntensity("RedLeds", emotionColors[emotions[i]][0])	
		proxyLED.setIntensity("GreenLeds", emotionColors[emotions[i]][1])
		proxyLED.setIntensity("BlueLeds", emotionColors[emotions[i]][2])
		# Sleep until next frame
		time.sleep(dt)

	# FINISHED REPLICATION
	video_thread.stop()
	print time.time()
	print (time.time() - startTime - duration )/frameCnt

	# Reset to neutral
	motionProxy.setAngles("HeadYaw", 0.0, 1.0)
	motionProxy.setAngles("HeadPitch", 0.0, 1.0)
	proxyLED.setIntensity("RedLeds", emotionColors[0][0])	
	proxyLED.setIntensity("GreenLeds", emotionColors[0][1])
	proxyLED.setIntensity("BlueLeds", emotionColors[0][2])

	time.sleep(1.0)




print "Measured time: "
print time.time() - timerStart

print "Cummulative true time: "
print np.sum(np.asfarray(dataVideo[:, 1]))

video_thread.close() 

'''













'''
# Only time logging version, without automatic video recording

from naoqi import ALProxy
import numpy as np
from matplotlib import pyplot as plt
import time

# Exclude 6 worst subjects ... later - excluded after recording
print time.time()

# Load data
dataVideo = np.genfromtxt('./videoID_duration_frames_G2.dat', delimiter=',', dtype=str)		# video ID | DURATION (sec) | NUMBER OF FRAMES
dataAUD = np.genfromtxt('./AUD_data_G2.dat', delimiter=',', dtype=str)						# videoID | frame number | emotionNumber
dataHPD = np.genfromtxt('./HPD_data_filtered_G2.dat', delimiter=',', dtype=str)				# videoID | frame number | angleYaw | anglePitch | velocityYaw | velocityPitch

# Connect to robot 
IP = '127.0.0.1'			# virtual
#IP = '169.254.42.173'		# real
PORT = 9559
motionProxy = ALProxy("ALMotion", IP, PORT)
motionProxy.setStiffnesses("Head", 1.0)
proxyLED = ALProxy("ALLeds", IP, PORT)
proxyLED.createGroup("RedLeds", ['RightFaceLedsRed', 'LeftFaceLedsRed'])
proxyLED.createGroup("GreenLeds", ['RightFaceLedsGreen', 'LeftFaceLedsGreen'])
proxyLED.createGroup("BlueLeds", ['RightFaceLedsBlue', 'LeftFaceLedsBlue'])
# Colors -RBG
emotionColors = [(0.,0.,0.), 
				 (1.,0.,0.),
				 (0.,0.,1.),
				 (0.,1.,0.)
				]

timerStart = time.time()

for video in dataVideo:
	videoID = video[0]
	duration = float(video[1])
	#f1 = int(video[2])
	#f2 = len([x[0] for x in dataAUD if x[0] == videoID])
	f3 = len([x[0] for x in dataHPD if x[0] == videoID])

	# Compare number of frames - take minimum => cut off at the end (actually only 2 videos from subject 23), HPD has least #frames => f3 chosen
	frameCnt = f3
	# if f1 != f2 or f2 != f3 or f1 != f3:
	# 	print videoID, f1, f2, f3				# Gives: 23_0_2 377 377 373; 23_3_1 357 357 330
	# 	frameCnt = np.min([f1, f2, f3])

	dt = duration / frameCnt

	emotions = [int(x[2]) for x in dataAUD if x[0] == videoID]
	anglesYaw_filtered = [float(x[2]) for x in dataHPD if x[0] == videoID]
	anglesPitch_filtered = [float(x[3]) for x in dataHPD if x[0] == videoID]
	velocitiesYaw_filtered = [float(x[4]) for x in dataHPD if x[0] == videoID]
	velocitiesPitch_filtered = [float(x[5]) for x in dataHPD if x[0] == videoID]

	#midTimerStart = time.time()
	# START REPLICATION
	print time.time()

	for i in range(frameCnt):
		# Send commands to the robot
		motionProxy.setAngles("HeadYaw", anglesYaw_filtered[i], velocitiesYaw_filtered[i])
		motionProxy.setAngles("HeadPitch", anglesPitch_filtered[i], velocitiesPitch_filtered[i])

		proxyLED.setIntensity("RedLeds", emotionColors[emotions[i]][0])	
		proxyLED.setIntensity("GreenLeds", emotionColors[emotions[i]][1])
		proxyLED.setIntensity("BlueLeds", emotionColors[emotions[i]][2])
		# Sleep until next frame
		time.sleep(dt)

	# FINISHED REPLICATION
	print time.time()

	# Reset to neutral
	motionProxy.setAngles("HeadYaw", 0.0, 1.0)
	motionProxy.setAngles("HeadPitch", 0.0, 1.0)
	proxyLED.setIntensity("RedLeds", emotionColors[0][0])	
	proxyLED.setIntensity("GreenLeds", emotionColors[0][1])
	proxyLED.setIntensity("BlueLeds", emotionColors[0][2])

	time.sleep(1.0)

	# print time.time() - midTimerStart
	# print duration
	# print dt


print "Measured time: "
print time.time() - timerStart

print "Cummulative true time: "
print np.sum(np.asfarray(dataVideo[:, 1]))
'''