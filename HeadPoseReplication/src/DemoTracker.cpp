///////////////////////////////////////////////////////////////////////////////////////////////////////
/// Citation: 
/// Xuehan Xiong, Fernando de la Torre, Supervised Descent Method and Its Application to Face Alignment. CVPR, 2013
///////////////////////////////////////////////////////////////////////////////////////////////////////

/*
    Modified by: Jan Ondras
    Institution: University of Cambridge
    Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
    Duration: October 2016 - May 2017
    
    All my modifications are enclosed between '/////JO/////' and '//////////'.
    The original file 'DemoTrackerORG.cpp' can be found in this directory.

    Main modifications:
        Call Python functions of Head Pose Filter (HPDdisplay.py) on each frame 
        and provide it with measured angles (yaw, pitch) of head pose and with time step between last 2 frames.  
        Replication latency measurements.
*/

#include <opencv2/core/core.hpp>
#include <opencv2/objdetect/objdetect.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <iostream>
#include <algorithm>
#include <string>
#include <vector>
#include <time.h>
#include <cmath>
#include <FaceAlignment.h>
#include <XXDescriptor.h>
#include <fstream>
/////JO///// Load library that allows C++/Python communication
#include <Python.h>
//////////

using namespace std;

bool compareRect(cv::Rect r1, cv::Rect r2) { return r1.height < r2.height; }

/////JO///// If first argument supplied to HPD is "LIVE" then use camera, otherwise use video file specified in first argument
// 2 modes: REALTIME,VIDEO
//#define REALTIME
//////////

void drawPose(cv::Mat& img, const cv::Mat& rot, float lineL)
{
	int loc[2] = {70, 70};
	int thickness = 2;
	int lineType  = 8;

	cv::Mat P = (cv::Mat_<float>(3,4) << 
		0, lineL, 0,  0,
		0, 0, -lineL, 0,
		0, 0, 0, -lineL);
	P = rot.rowRange(0,2)*P;
	P.row(0) += loc[0];
	P.row(1) += loc[1];
	cv::Point p0(P.at<float>(0,0),P.at<float>(1,0));

	line(img, p0, cv::Point(P.at<float>(0,1),P.at<float>(1,1)), cv::Scalar( 255, 0, 0 ), thickness, lineType);
    line(img, p0, cv::Point(P.at<float>(0,2),P.at<float>(1,2)), cv::Scalar( 0, 255, 0 ), thickness, lineType);
	line(img, p0, cv::Point(P.at<float>(0,3),P.at<float>(1,3)), cv::Scalar( 0, 0, 255 ), thickness, lineType);
}

int main(int argc, char* argv[])
{
	char detectionModel[] = "./models/DetectionModel-v1.5.bin";
	char trackingModel[]  = "./models/TrackingModel-v1.10.bin";
    string faceDetectionModel("./models/haarcascade_frontalface_alt2.xml");

    float sin_beta, beta, cos_beta;
    float sin_alpha, alpha;
    float sin_gamma, gamma;

	// initialize a XXDescriptor object
	INTRAFACE::XXDescriptor xxd(4);
	// initialize a FaceAlignment object
	INTRAFACE::FaceAlignment fa(detectionModel, trackingModel, &xxd);
	if (!fa.Initialized()) {
		cerr << "FaceAlignment cannot be initialized." << endl;
		return -1;
	}
	// load OpenCV face detector model
	cv::CascadeClassifier face_cascade;
	if( !face_cascade.load( faceDetectionModel ) )
	{ 
		cerr << "Error loading face detection model." << endl;
		return -1; 
	}
	
/////JO///// If first argument supplied to HPD is "LIVE" then use camera, otherwise use video file specified in first argument
	cv::VideoCapture cap;
	if(strcmp(argv[1], "LIVE") == 0)
		cap.open(0);
	else {
    	string filename(argv[1]);
		cap.open(filename); 
	}
	/*
#ifdef REALTIME
	// use the first camera it finds
	cv::VideoCapture cap(0); 
#endif 

#ifdef VIDEO
    //string filename("./data/vid.wmv");
    string filename(argv[1]);
	cv::VideoCapture cap(filename); 
#endif
	*/
//////////

    ofstream myfile;
    //myfile.open ("example.txt");
    myfile.open(argv[2]);

	if(!cap.isOpened())  
		return -1;

	int key = 0;
	bool isDetect = true;
	bool eof = false;
	float score, notFace = 0.3;
	cv::Mat X,X0;
	string winname("Demo IntraFace Tracker");

	cv::namedWindow(winname);
    int frame_number = 0;

	/////JO/////

    // For latency measurements - specify the file log measurements in "latencyLogFile"
    long long startTimeLatencyMeasur;
    struct timeval tp;
    ofstream latencyLogFile;
    latencyLogFile.open("/home/janciovec/Documents/jFiles/Skola/Cambridge/II/_Project/_src/DisplayingModule/LatencyEvaluation/hpStartTimes.dat");

    int frame_number_face_detected = 0;	// log number of frames where face was detected
    int timeStepsDetected = 0;			// number of frames for which timestep (between last 2 frames) was calculated - to calculate timestep need to be detected in current and in previous frame 
    bool prevFrameDetected = false;		// true if head pose data were detected in previous frame

    // To measure time:
    clock_t prevClk, diff = 0, diffSum = 0;

    // Import Python script
    PyObject *pName, *pModule, *pFunc, *pFunc2, *pFunc3, *pArgs, *pArgs2;
    Py_Initialize();
    pName = PyString_FromString("HPDdisplay");         			// name of python file
    //pName = PyString_FromString("HPDdisplayExperiment");      // name of python file FOR EVALUATION OF HUMAN EXPERIMENT
    pModule = PyImport_Import(pName);							// now everything is loaded from Python
    Py_DECREF(pName);

    // 3 Python functions called from C++
    pFunc = PyObject_GetAttrString(pModule, "initRobot");		// Supply IP and PORT to connect to robot
    pArgs = PyTuple_New(1);
    pFunc2 = PyObject_GetAttrString(pModule, "moveHead");		// For each frame, send measured angles of head pose and time step between last 2 frames
    pArgs2 = PyTuple_New(3);
    pFunc3 = PyObject_GetAttrString(pModule, "finalize");		// Call on shutdown, optionally display/save results

    // Call Python initRobot()
	PyTuple_SetItem(pArgs, 0, PyString_FromString(argv[3]));
	PyObject_CallObject(pFunc, pArgs);
    //////////

	while (key!=27) // Press Esc to quit
	{
		cv::Mat frame;
		cap >> frame; // get a new frame from camera
        frame_number++;
        /////JO///// Log start time: For latency measurements
		gettimeofday(&tp, NULL);
        startTimeLatencyMeasur = tp.tv_sec * 1000 + tp.tv_usec / 1000;
        //////////

		if (frame.rows == 0 || frame.cols == 0)
			break;

		if (isDetect)
		{
			// face detection
			vector<cv::Rect> faces;
			face_cascade.detectMultiScale(frame, faces, 1.2, 2, 0, cv::Size(50, 50));
			// if no face found, do nothing
			if (faces.empty()) {
				cv::imshow(winname,frame);
				key = cv::waitKey(5);
				continue ;
			}
			// facial feature detection on largest face found
			if (fa.Detect(frame,*max_element(faces.begin(),faces.end(),compareRect),X0,score) != INTRAFACE::IF_OK)
				break;
			isDetect = false;
		}
		else
		{
			// facial feature tracking
			if (fa.Track(frame,X0,X,score) != INTRAFACE::IF_OK)
				break;
			X0 = X;
		}
		if (score < notFace) { // detected face is not reliable
			isDetect = true;
			/////JO/////
			prevFrameDetected = false;
			//////////
		}
		else
		{
			// plot facial landmarks
            for (int i = 0 ; i < X0.cols ; i++) {
				cv::circle(frame,cv::Point((int)X0.at<float>(0,i), (int)X0.at<float>(1,i)), 1, cv::Scalar(0,255,0), -1);
                //myfile << cv::Point((int)X0.at<float>(0,i), (int)X0.at<float>(1,i)) << frame_number << endl;
            }
			// head pose estimation
			INTRAFACE::HeadPose hp;
			fa.EstimateHeadPose(X0,hp);

            // compute yaw pitch roll angles
            sin_beta = -hp.rot.at<float>(2,0);
            beta = asin(sin_beta); // YAW angle
            cos_beta = cos(beta);

            sin_alpha = hp.rot.at<float>(1,0)/cos_beta;
            alpha = asin(sin_alpha); // ROLL angle

            sin_gamma = hp.rot.at<float>(2,1)/cos_beta;
            gamma = asin(sin_gamma); // PITCH angle

            // beta = YAW
            // gamma = PITCH

            /////JO/////
            frame_number_face_detected++;
            
            // if HP data were not recorded in previous frame => don't calculate time step & start timer
            if(!prevFrameDetected) {
            	prevClk = clock();
            	diff = 0;
            }
            else {
            	timeStepsDetected++;
				diff = clock() - prevClk;
            	prevClk = clock();
            	diffSum += diff;
            	//cout << "Last time step (sec): " << (double)diff/CLOCKS_PER_SEC << "\t Average time step (sec): " << (double)diffSum/(CLOCKS_PER_SEC*timeStepsDetected) << endl;
            }
            prevFrameDetected = true;

            // Call Python function to filter head movement and move robot's head, send measured yaw and pitch angles and time step between last 2 frames
			PyTuple_SetItem(pArgs2, 0, PyFloat_FromDouble(-beta));	// YAW - it is flipped only on the robot (not for UPNA database)
			PyTuple_SetItem(pArgs2, 1, PyFloat_FromDouble(gamma));	// PITCH
			PyTuple_SetItem(pArgs2, 2, PyFloat_FromDouble((double)diff/CLOCKS_PER_SEC));	// last time step, not null iff prevFrameDetected
			PyObject_CallObject(pFunc2, pArgs2);

			// Save latency measurements
			latencyLogFile << startTimeLatencyMeasur << endl;

			// If you want to record something from C++ code then supply filename as second argument ! 
	        // run as: ./DemoTracker a hpData.dat
	        // Save measured data:
	        // myfile << beta << " " << gamma << " " << frame_number << endl;

            //////////

			// plot head pose
			drawPose(frame, hp.rot, 50);
		}
		cv::imshow(winname,frame);	
		key = cv::waitKey(5);
	}

	/////JO/////
	cout << "Total # of frames: " << frame_number << endl;
	cout << "Total # of frames where face was detected: " << frame_number_face_detected << endl;
	cout << "Average frame rate (FPS) for detected ones: " << (double)timeStepsDetected * CLOCKS_PER_SEC / diffSum << endl;

	// Call Python finalize()
	PyObject_CallObject(pFunc3, NULL);

	Py_XDECREF(pFunc);
    Py_XDECREF(pFunc2);
    Py_XDECREF(pFunc3);
    Py_DECREF(pModule);
	Py_Finalize();

	latencyLogFile.close();

	//////////

    myfile.close();
	return 0;

}






