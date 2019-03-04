/*
    Modified by: Jan Ondras
    Institution: University of Cambridge
    Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
    Duration: October 2016 - May 2017
    
    All my modifications are enclosed between '/////JO/////' and '//////////'.

    This is only for extracting features for Emotion Classifier training => need to replace the current AURecogniser.cpp file in AUD folder
*/

#include "AURecogniser.hpp"

#include <FaceAlignment.h>
#include <XXDescriptor.h>
#include <stdio.h>
#include <opencv2/objdetect/objdetect.hpp>

#include "ML.hpp"
#include "QLZM3D.hpp"


#include "FaceUtils.hpp"
#include "GaborBank.hpp"

//#include "Aligner.hpp"
#include <Image.hpp>


// Ctrl+C signal handler
#include  <signal.h>


#include <QDir>

extern sig_atomic_t interruptSignal;

using std::set;
using std::map;
using std::string;
using std::vector;
using cv::Mat;


AURecogniser::AURecogniser(const std::string &configFilePath)
    : config(configFilePath)
{

    isSessionBeingRecorded = config.storeAUresults || config.storeCalibrationData || config.storeDetailedAUresults
            || config.storeProcessedFrames || config.storeDetailedAUresults;
}


void AURecogniser::calibration(cv::VideoCapture& cap, bool showMessage1)
{
    if (!cap.isOpened()) {
        std::cerr << "Cannot open video file or stream for calibration!" << std::endl;
        return;
    }

    int64 t1 = cv::getTickCount();

    std::string detectionModel("./data/intrafacemodels/DetectionModel-v1.5.yml");
    std::string trackingModel("./data/intrafacemodels/TrackingModel-v1.10.yml");
    std::string faceDetectionModel("./data/intrafacemodels/haarcascade_frontalface_alt2.xml");

    INTRAFACE::XXDescriptor xxd(4);



    INTRAFACE::FaceAlignment fa(detectionModel, trackingModel, &xxd);
    if (!fa.Initialized()) {
        std::cerr << "FaceAlignment cannot be initialized." << std::endl;
        return;
    }
    // load OpenCV face detector model
    cv::CascadeClassifier face_cascade;
    if( !face_cascade.load( faceDetectionModel ) )
    {
        std::cerr << "Error loading face detection model." << std::endl;
        return;
    }



    //! ====================== Show Message 1 ======================
    int timeElapsed = 0;
    while (timeElapsed < 100 && showMessage1)
    {


        Mat messageFrame(520, 900, CV_8UC3, cv::Scalar::all(255));
        std::string line1 = "Please rotate your head slowly as shown in video";
        std::string line2 = "You can press <space> when you are ready to proceed";

        cv::putText(messageFrame, line1, cv::Point2f(80, 100), cv::FONT_HERSHEY_SIMPLEX, 0.8, cv::Scalar::all(0),2);
        cv::putText(messageFrame, line2, cv::Point2f(80, 140), cv::FONT_HERSHEY_SIMPLEX, 0.8, cv::Scalar::all(0),2);

        cv::imshow("Prepare for Calibration", messageFrame);
        char key = (char) cv::waitKey(20);

        if (key == ' ')
            showMessage1 = false;

        timeElapsed = (cv::getTickCount()-t1)/cv::getTickFrequency();
    }

    cv::destroyAllWindows();


    bool isDetect = true;
    bool isFace = false;
    int numWithoutFace = 0;
    Mat X,X0;
    float score, notFace = 0.3;



    Mat frame,framegray;


    bool continueCalibration = true;

    t1 = cv::getTickCount();
    timeElapsed = 0;
    int idx = 0;
    while (!interruptSignal && timeElapsed < 10 && continueCalibration)
    {
        timeElapsed = (cv::getTickCount()-t1)/cv::getTickFrequency();
        cap >> frame;



        if (!frame.cols)
            break;

        if (frame.rows > 600)
        {
            double resizeRatio = 600./frame.rows;
            cv::resize(frame, frame, cv::Size(), resizeRatio, resizeRatio);
        }



        if (frame.channels()>1)
            cv::cvtColor(frame, framegray, CV_RGB2GRAY);
        else
            framegray = frame.clone();

        idx++;



        // =================== DETECT LANDMARKS: START ===================
        vector<cv::Rect> faces;
        if (isDetect) {
            face_cascade.detectMultiScale(frame, faces, 1.2, 2, 0, cv::Size(100, 100));

            if (faces.size() == 0)
            {
                continue;
                if (fa.Track(frame, X0, X, score) != INTRAFACE::IF_OK)
                    continue;

                X0.copyTo(X);
                isDetect = true;
            }
            else
            {
                cv::Rect biggestFaceRect = *max_element(faces.begin(), faces.end(), cvip::compareRect);

                if (fa.Detect(frame, biggestFaceRect, X0, score) != INTRAFACE::IF_OK)
                    continue;
            }
        } else { // facial feature tracking
            if (fa.Track(frame,X0,X,score) != INTRAFACE::IF_OK)
                continue;

            X0 = X;
        }

        if (score < notFace) {
            isDetect = true;
            isFace = false;
            numWithoutFace++;
        } else {
            isDetect = false;
            isFace = true;
            numWithoutFace = 0;
        }

        Mat leye = framegray(imutil::rectFromLandmarks(X0, "leye", frame.size()).toCvStyle());
        Mat reye = framegray(imutil::rectFromLandmarks(X0, "reye", frame.size()).toCvStyle());
        Mat mouth = framegray(imutil::rectFromLandmarks(X0, "mouth", frame.size()).toCvStyle());

        imutil::rotateUpright(leye, X0);
        imutil::rotateUpright(reye, X0);
        imutil::rotateUpright(mouth, X0);

        double resizeRatio = (double)  (rfw::imWs["leye"]+15)/leye.cols;
        cv::resize(leye, leye, cv::Size(0,0), resizeRatio,resizeRatio);
        cv::resize(reye, reye, cv::Size(0,0), resizeRatio,resizeRatio);
        cv::resize(mouth, mouth, cv::Size(0,0), resizeRatio,resizeRatio);

        double dummy1, dummy2;
        Mat curPtCoords = FaceUtils::getYawPitchDev(X0, dummy1, dummy2);
        Mat normCoords  = FaceUtils::getNormalisedCoordinates(X0);

        neutralParts.push_back(std::make_tuple(leye,reye,mouth));
        neutralPtCoords.push_back(curPtCoords);
        neutralNormalisedCoords.push_back(normCoords);

        if (config.visualiseOutput)
            cv::imshow("frame", frame);

        char key = (char) cv::waitKey(15);


        if (key == ' ')
            continueCalibration = false;

        if (config.storeCalibrationData)
        {
            std::stringstream ss1,ss2,ss3,ss4,ss5,ss6;
            ss1 << pathToCalibData << '/' << std::setw(10) << std::setfill('0') << idx << ".ptCoords";
            ss2 << pathToCalibData << '/' << std::setw(10) << std::setfill('0') << idx << ".normalisedCoords";

            ss3 << pathToCalibData << '/' << std::setw(10) << std::setfill('0') << idx << ".png";
            ss4 << pathToCalibData << '/' << std::setw(10) << std::setfill('0') << idx << "_leye.png";
            ss5 << pathToCalibData << '/' << std::setw(10) << std::setfill('0') << idx << "_reye.png";
            ss6 << pathToCalibData << '/' << std::setw(10) << std::setfill('0') << idx << "_mouth.png";

            cvip::Image::writeToFile(curPtCoords, ss1.str());
            cvip::Image::writeToFile(normCoords,  ss2.str());

            cv::imwrite(ss3.str(), framegray);
            cv::imwrite(ss4.str(), leye);
            cv::imwrite(ss5.str(), reye);
            cv::imwrite(ss6.str(), mouth);
        }

        // if single-frame calibration, complete immediately
        if (config.calibration == 1)
            break;
    }

    cv::destroyAllWindows();
}








void AURecogniser::setRecordingPaths(std::string& sessionName, bool forceToCreatePaths)
{
    //! if session name not provided set it to unix timestamp
    std::stringstream sstmp;
    sstmp << unix_timestamp();
    std::string tstamp = sstmp.str();

    if (sessionName == "")
        sessionName = sstmp.str();

    // Create the necessary directories etc. if session is being recorded
    if (isSessionBeingRecorded || forceToCreatePaths)
    {
        if (!QDir(config.RECORDINGS_PATH.c_str()).exists())
            QDir().mkdir(config.RECORDINGS_PATH.c_str());

        std::stringstream ss;
        ss << config.RECORDINGS_PATH << '/' << sessionName;

        QString pathToCurSession(ss.str().c_str());

        if (!QDir(pathToCurSession).exists())
            QDir().mkdir(pathToCurSession);

        pathToAUResults = pathToCurSession.toStdString() + '/' + config.AU_RESULTS_DIR;
        pathToFrames    = pathToCurSession.toStdString() + '/' + config.FRAMES_DIR;
        pathToCalibData = pathToCurSession.toStdString() + '/' + config.CALIB_DATA_DIR;


        if (config.storeAUresults || config.storeDetailedAUresults)
        {
            if (!QDir(pathToAUResults.c_str()).exists())
                QDir().mkdir(pathToAUResults.c_str());
        }


        if (config.storeRawFrames || config.storeProcessedFrames)
        {
            if (!QDir(pathToFrames.c_str()).exists())
                QDir().mkdir(pathToFrames.c_str());
        }


        if (config.storeCalibrationData)
        {
            if (!QDir(pathToCalibData.c_str()).exists())
                QDir().mkdir(pathToCalibData.c_str());
        }
    }
}




void AURecogniser::parseCalibrationDataFromRecordingsFolder()
{
    QDir calibDir(pathToCalibData.c_str());
    calibDir.setNameFilters(QStringList()<<"*_leye.png");
    QStringList imsList = calibDir.entryList(QDir::Files);

    for (int i=0; i<imsList.size(); ++i){
        QString leyePath = calibDir.absoluteFilePath(imsList[i]);
        QString reyePath = QString(leyePath).replace("leye", "reye");
        QString mouthPath = QString(leyePath).replace("leye", "mouth");

        cv::Mat leye = cv::imread(leyePath.toStdString(), CV_LOAD_IMAGE_GRAYSCALE);
        cv::Mat reye = cv::imread(reyePath.toStdString(), CV_LOAD_IMAGE_GRAYSCALE);
        cv::Mat mouth = cv::imread(mouthPath.toStdString(), CV_LOAD_IMAGE_GRAYSCALE);

        neutralParts.push_back(std::make_tuple(leye,reye,mouth));

        std::string curPtCoordsPath = QString(leyePath).replace("_leye.png", ".ptCoords").toStdString();
        std::string normalisedCoordsPath = QString(leyePath).replace("_leye.png", ".normalisedCoords").toStdString();


        cv::Mat curPtCoords = cvip::Image::vectorToColumn(cvip::Image::readFileToVector(curPtCoordsPath));
        cv::Mat normCoords =  cvip::Image::vectorToColumn(cvip::Image::readFileToVector(normalisedCoordsPath));

        neutralNormalisedCoords.push_back(normCoords);
        neutralPtCoords.push_back(curPtCoords);
    }
}























void AURecogniser::recogniseFromVideoFile(const string &filePath, const std::string &calibVideoFile)
{

    if (calibVideoFile == "" && config.calibration == 1) {
        // do calibration from first image if no additional calib file is specified
        cv::VideoCapture cap(filePath);
        calibration(cap, false);
    } else if (calibVideoFile != "" && config.calibration > 0) {
        // do calibration from addtional file if provided
        cv::VideoCapture cap(calibVideoFile);
        calibration(cap, false);
    }

    cv::VideoCapture cap(filePath);
    recogniseFromVideoCapture(cap);
}





void AURecogniser::recogniseFromLiveStream(bool parseCalibDataFromRecordings)
{

    if (config.calibration > 0) {
        if (!parseCalibDataFromRecordings) {
            cv::VideoCapture cap(config.cameraId);
            calibration(cap, false);
        } else {
            parseCalibrationDataFromRecordingsFolder();
        }
    }


    cv::VideoCapture cap(config.cameraId);
    recogniseFromVideoCapture(cap);
}






void AURecogniser::recogniseFromVideoCapture(cv::VideoCapture& cap)
{

    if (!cap.isOpened()) {
        std::cerr << "Cannot open video file or stream for AU recognition!" << std::endl;
        return;
    }

    //! Read classifiers for each feature type defined in the config file
    for (auto p: config.featureTypes)
        svms.insert(std::pair<std::string, std::vector<SVM2> >(p, getSvms(p)));


    //! These classes are used for feature extraction
    GaborBank GB("2-4-4-01100-11111111-std-double");
    cvip::QLZM QLZMpart(4,4,7,7,2,2,18,cvip::LZMA_ONLY_L1,cvip::LZMA_ONLY_IMAGINARY);


    std::string detectionModel("./data/intrafacemodels/DetectionModel-v1.5.yml");
    std::string trackingModel("./data/intrafacemodels/TrackingModel-v1.10.yml");
    std::string faceDetectionModel("./data/intrafacemodels/haarcascade_frontalface_alt2.xml");

    INTRAFACE::XXDescriptor xxd(4);


    INTRAFACE::FaceAlignment fa(detectionModel, trackingModel, &xxd);
    if (!fa.Initialized()) {
        std::cerr << "FaceAlignment cannot be initialized." << std::endl;
        return;
    }
    // load OpenCV face detector model
    cv::CascadeClassifier face_cascade;
    if( !face_cascade.load( faceDetectionModel ) )
    {
        std::cerr << "Error loading face detection model." << std::endl;
        return;
    }


    bool isDetect = true;
    bool isFace = false;
    int numWithoutFace = 0;
    Mat X,X0;
    float score, notFace = 0.3;

    Mat frame,framegray;

    std::deque<double> devYaws, devPitchs;

    int FRAME_COUNT = cap.get(CV_CAP_PROP_FRAME_COUNT);

    int64 t1 = cv::getTickCount();
    int idx = 0;

    /////JO/////
    // SIMPLE DATA OUTPUT COMMENTED
    /*map<string, int> AUcounts;
    for (size_t i=0; i<config.AUlist.size(); ++i)
    {
        std::string AU = config.AUlist[i];
        // initialise counts to 0
        AUcounts[AU] = 0;
    }*/
    // Log FPS and FRAME COUNT
    AUresultsFile << cap.get(CV_CAP_PROP_FPS) << "\t" << FRAME_COUNT << "\t";
    //////////

    while (!interruptSignal)
    {
        try
        {
        cap >> frame;

        //! resize frame if it's too big to fit small screens
        if (frame.rows > 600)
        {
            double resizeRatio = 600./frame.rows;
            cv::resize(frame, frame, cv::Size(), resizeRatio, resizeRatio);
        }

        Mat frameRaw = frame.clone();

        if (!frame.cols) {
            break;
        }

        if (!cap.isOpened())
            break;

        if (FRAME_COUNT > -1 && idx >= FRAME_COUNT)
            break;


        if (frame.channels()>1)
            cv::cvtColor(frame, framegray, CV_RGB2GRAY);
        else
            framegray = frame.clone();

        int64 t1 = cv::getTickCount();

        idx++;

        // =================== DETECT LANDMARKS: START ===================
        vector<cv::Rect> faces;
        if (isDetect) {
            std::cout << "detecting.. ";
            face_cascade.detectMultiScale(frame, faces, 1.2, 2, 0, cv::Size(100, 100));

            if (faces.size() == 0)
            {
                if (!X0.cols)
                    continue;

                if (fa.Track(frame, X0, X, score) != INTRAFACE::IF_OK)
                    continue;

                X0.copyTo(X);
                isDetect = true;
            }
            else
            {
                cv::Rect biggestFaceRect = *max_element(faces.begin(), faces.end(), cvip::compareRect);

                if (fa.Detect(frame, biggestFaceRect, X0, score) != INTRAFACE::IF_OK)
                    continue;
            }
        } else { // facial feature tracking
            if (fa.Track(frame,X0,X,score) != INTRAFACE::IF_OK)
                continue;
            X0 = X;
        }

        if (score < notFace) {
            isDetect = true;
            isFace = false;
            numWithoutFace++;
        } else {
            isDetect = false;
            isFace = true;
            numWithoutFace = 0;
        }



        map<string, Mat> features;

        /*

        for (int i=0; i<X0.cols; ++i)
        {
            cv::Point2f pt(X0.at<float>(0,i), X0.at<float>(1,i));
            cv::circle(frame, pt,2, cv::Scalar::all(255), 2);
            std::stringstream ss;
            ss << i;
//            cv::putText(frame, ss.str(),pt, CV_FONT_HERSHEY_SIMPLEX,0.4, cv::Scalar::all(255));
        }
        cv::imshow("f", frame);
        cv::waitKey(0);
        */

        // =================== CROP FACIAL PARTS: START ===================
	//! Facial parts (i.e. left eye, right eye and mouht) are processed independently.
 	//! Here we crop each of those parts
        Mat leye = framegray(imutil::rectFromLandmarks(X0, "leye", frame.size()).toCvStyle());
        Mat reye = framegray(imutil::rectFromLandmarks(X0, "reye", frame.size()).toCvStyle());
        Mat mouth = framegray(imutil::rectFromLandmarks(X0, "mouth", frame.size()).toCvStyle());

        imutil::rotateUpright(leye, X0);
        imutil::rotateUpright(reye, X0);
        imutil::rotateUpright(mouth, X0);

        double resizeRatio = (double)  (rfw::imWs["leye"]+15)/leye.cols;
        cv::resize(leye, leye, cv::Size(0,0), resizeRatio,resizeRatio);
        cv::resize(reye, reye, cv::Size(0,0), resizeRatio,resizeRatio);
        cv::resize(mouth, mouth, cv::Size(0,0), resizeRatio,resizeRatio);
        // =================== CROP FACIAL PARTS: END ===================




   	//! Those values will be used to measure how much the head pose deviates from the frontal pose
	//! devYaw (devPitch) measures deviation from frontal yaw (pitch) angle 
        double devYaw, devPitch, rawDevYaw, rawDevPitch;
        if (!isFace)
        {
            //! Warn the user with red color when no face is detected
            devYaw = -1000;
            devPitch = -1000;
        }

	//! compute normalised facial landmark point coordinates
        Mat curPtCoords = FaceUtils::getYawPitchDev(X0, devPitch, devYaw);
        Mat shapeCurrent = FaceUtils::getNormalisedCoordinates(X0);
        features["shape"] = shapeCurrent;

        rawDevPitch = devPitch;
        rawDevYaw = devYaw;

	//! Compute QLZM features (i.e. appearance features) if defined in config file
        if (config.featureTypes.find("appearance") != config.featureTypes.end())
        {

            cv::Mat parts[3];
            int idx = 0;
            cv::Mat leyeqlzm = leye.clone();
            cv::Mat reyeqlzm = reye.clone();
            cv::Mat mouthqlzm = mouth.clone();
            cvip::Image::zNormalize(leyeqlzm);
            cvip::Image::zNormalize(reyeqlzm);
            cvip::Image::zNormalize(mouthqlzm);

            parts[idx++] = QLZMpart.computeHist(QLZMpart.extractFinePatterns(leye));
            parts[idx++] = QLZMpart.computeHist(QLZMpart.extractFinePatterns(reye));
            parts[idx++] = QLZMpart.computeHist(QLZMpart.extractFinePatterns(mouth));

            cv::Mat pfeatsqlzm;
            cv::hconcat(parts, 3, pfeatsqlzm);
            features["appearance"] = pfeatsqlzm;
        }

        //! Compute differential features if necessary
        if (config.isDiffFeatures)
        {
            int matchIdx = FaceUtils::matchNeutralFace(curPtCoords, neutralPtCoords);
            Mat leyeMatch =  std::get<0>(neutralParts[matchIdx]);
            Mat reyeMatch =  std::get<1>(neutralParts[matchIdx]);
            Mat mouthMatch = std::get<2>(neutralParts[matchIdx]);
            Mat shapeMatch = neutralNormalisedCoords[matchIdx];

            std::vector<Mat> matchedLeyes({leye.clone(),leyeMatch.clone()});
            std::vector<Mat> matchedReyes({reye.clone(),reyeMatch.clone()});
            std::vector<Mat> matchedMouths({mouth.clone(),mouthMatch.clone()});

            Mat shapeDiff = shapeCurrent-shapeMatch;

            features["ndiff-shape"] = shapeDiff;



            for (int i=0; i<matchedLeyes.size(); ++i)
            {
                matchedLeyes[i] = imutil::cropCore(matchedLeyes[i], rfw::imWs["part"]);
                matchedReyes[i] = imutil::cropCore(matchedReyes[i], rfw::imWs["part"]);
                matchedMouths[i] = imutil::cropCore(matchedMouths[i], rfw::imWs["part"]);
                cv::resize(matchedLeyes[i], matchedLeyes[i], cv::Size(32,32));
                cv::resize(matchedReyes[i], matchedReyes[i], cv::Size(32,32));
                cv::resize(matchedMouths[i], matchedMouths[i], cv::Size(32,32));
            }

            cvip::Mat3 leye3(matchedLeyes, true), reye3(matchedReyes, true), mouth3(matchedMouths, true);

            Mat parts[3], pfeats;

            parts[0] = cvip::Image::vectorToColumn(GB.computeFeatures(leye3));
            parts[1] = cvip::Image::vectorToColumn(GB.computeFeatures(reye3));
            parts[2] = cvip::Image::vectorToColumn(GB.computeFeatures(mouth3));

            cv::hconcat(parts, 3, pfeats);

            features["ndiff-appearance"] = pfeats;
        }




        //! ================= DRAW HEAD POSE INDICATORS =================
        //! We draw two rectangles (one on top and one on side) to indicate how much the user deviates from frontal pose
	//! If the user stands in frontal pose, the rectangles will take a green-ish color, otherwise they will turn to red
  	devYaw = fabs(devYaw)*fabs(devYaw);
        devPitch = fabs(devPitch)*fabs(devPitch);
        if (devYaws.size() > 10)
        {
            devYaws.pop_front();
            devPitchs.pop_front();
        }

        devPitch = std::min<double>(devPitch, 1);
        devYaw = std::min<double>(devYaw, 1);

        devYaws.push_back(devYaw);
        devPitchs.push_back(devPitch);

	//! Do some simple averaging over time so the colors don't change annoyingly
        double avgDevYaw = std::accumulate(devYaws.begin(), devYaws.end(), 0.)/devYaws.size();
        double avgDevPitch = std::accumulate(devPitchs.begin(), devPitchs.end(), 0.)/devPitchs.size();

        int thck = 80;
        cv::Rect topRect(0,0,frame.cols, thck);
        cv::Rect rightRect(frame.cols-thck,0,thck, frame.rows);

        cv::rectangle(frame, rightRect, CV_RGB(avgDevYaw*255, (1-avgDevYaw)*255,0), -1);
        cv::rectangle(frame, topRect, CV_RGB(avgDevPitch*255, (1-avgDevPitch)*255,0), -1);
        //! ================= END: DRAW HEAD POSE INDICATORS =================







        // =================== EXTRACT-3DQLZM & RESET SEQUENCE: END =================== //
        map<string, set<string> > detailedAUs;
        map<string, bool> AUdecisions;
        for (auto p : config.featureTypes)
        {
            set<string> curAUs =  getMatchedAUs(features[p], svms[p]);
            detailedAUs.insert(std::make_pair(p, curAUs));

            for (auto AU : config.AUlist) {
                if (AUdecisions.find(AU) == AUdecisions.end())
                    AUdecisions[AU] = true;

                // to accept an AU as detected, it must be verified through all classifiers
                AUdecisions[AU] = AUdecisions[AU] && (curAUs.find(AU) != curAUs.end());

            }
        }

        // the width of the panel depends on whether we are displaying DETEAILED resuts or not (i.e. individual classifier output)
        // if DETAILED reslts, then we need a wide panel (40 pixels per classifier)
        int panelWidth = 40;
        if (config.visualiseDetailed)
            panelWidth = 40*(1+config.featureTypes.size());

        cv::Rect leftPanel(0,0, panelWidth, frame.rows);
        cv::rectangle(frame, leftPanel, cv::Scalar(255,255,255), -1);

        for (size_t i=0; i<config.AUlist.size(); ++i)
        {
            std::string AU = config.AUlist[i];
            if (config.visualiseDetailed)
            {
                int idx=0;

                for (auto featureType : config.featureTypes) {

                    std::string shortTitle = "NS";
                    if (featureType == "ndiff-appearance")
                        shortTitle = "NA";
                    else if (featureType == "appearance")
                        shortTitle = "A";
                    else if (featureType == "shape")
                        shortTitle = "S";
                    else if (featureType == "shapespecial")
                        shortTitle = "SS";

                    cv::putText(frame, shortTitle, cv::Point(5+34*idx, 28),cv::FONT_HERSHEY_SIMPLEX|cv::FONT_ITALIC, 0.50, cv::Scalar(0,0,0), 1);


                    // a gray color will be shown when AU not detected
                    cv::Scalar theColor(200,200,200);

                    if (isFace) //! Perform AU detection only if face exists
                    {
                        if (detailedAUs[featureType].find(AU) != detailedAUs[featureType].end())
                            theColor = cv::Scalar(255,0,0);
                    }

                    cv::putText(frame, AU, cv::Point(5+34*idx, 28+28+28*i),cv::FONT_HERSHEY_SIMPLEX|cv::FONT_ITALIC, 0.80, theColor, 2);
                    idx++;
                }
            }

            cv::Scalar theColor(200,200,200);
            if (isFace) //! Perform AU detection only if face exists
            {
                if (AUdecisions[AU])
                    theColor = cv::Scalar(255,0,0);
            }

            int bufferLeft = 0;

            if (config.visualiseDetailed)
                bufferLeft = 34*config.featureTypes.size();

            cv::putText(frame, "C", cv::Point(5+bufferLeft, 28),cv::FONT_HERSHEY_SIMPLEX|cv::FONT_ITALIC, 0.50, cv::Scalar(0,0,0), 1);
            cv::putText(frame, AU, cv::Point(5+bufferLeft, 28+28+28*i),cv::FONT_HERSHEY_SIMPLEX|cv::FONT_ITALIC, 0.80, theColor, 2);

        }

        long curTimestamp = Config::getCurTs();


        //! Store frames -- if setting enabled in Config
        if (config.storeProcessedFrames || config.storeRawFrames) {
            if (config.storeProcessedFrames)
            {
                std::stringstream ss;
                ss << pathToFrames << '/' << curTimestamp << "-"<< std::setw(10) << std::setfill('0') << idx << "_appearance.png";
                cv::imwrite(ss.str(), frame);
            }

            if (config.storeRawFrames)
            {
                std::stringstream ss;
                ss << pathToFrames << '/' << curTimestamp << "-"<< std::setw(10) << std::setfill('0') << idx << "_raw.png";
                cv::imwrite(ss.str(), frameRaw);
            }
        }


        //! Store AU results -- if setting enabled in Config
        if (config.storeAUresults)
        {
            std::stringstream AUoutput;
            for (size_t i=0; i<config.AUlist.size(); ++i)
            {
                std::string AU = config.AUlist[i];

                /////JO/////
                if (AUdecisions[AU]) {
                    AUoutput << AU << "+";
                    // SIMPLE DATA OUTPUT COMMENTED
                    // AUcounts[AU]++;
                    // more detailed data - vector(12) of 0/1s per frame
                    AUresultsFile << "1" << "\t";       // 1 = AU detected
                }
                else {
                    AUresultsFile << "0" << "\t";       // 0 = AU not detected
                }
                //////////
            }

            std::stringstream ss, sy, sp;
            ss << pathToAUResults << '/' << curTimestamp << "-" << std::setw(10) << std::setfill('0') << idx << "_results.txt";
            sy << pathToAUResults << '/' << curTimestamp << "-" << std::setw(10) << std::setfill('0') << idx << "_headposeyaw.txt";
            sp << pathToAUResults << '/' << curTimestamp << "-" << std::setw(10) << std::setfill('0') << idx << "_headposepitch.txt";

            cv::Mat headPoseYawMat(1,1,CV_64FC1, cv::Scalar::all(0)), headPosePitchMat(1,1,CV_64FC1, cv::Scalar::all(0));
            headPosePitchMat.at<double>(0,0) = rawDevPitch; // 0.55
            headPoseYawMat.at<double>(0,0) = rawDevYaw; // 1.0

            rawDevPitch += 0.30;
            rawDevYaw -= 0.25;
//            std::cout     << rawDevPitch << '\t' << rawDevYaw << std::endl;
            cvip::Image::writeToFile(headPosePitchMat, sp.str());
            cvip::Image::writeToFile(headPoseYawMat, sy.str());

            std::ofstream fl(ss.str());

            // 
            fl << AUoutput.str();
            fl.close();
        }


        //! Store detailed AU results (i.e. performance of each feature independently) if enabled in Config
        if (config.storeDetailedAUresults)
        {
            for (auto featureType : config.featureTypes)
            {
                std::stringstream AUoutput;

                for (auto detectedAU : detailedAUs[featureType])
                    AUoutput << detectedAU << "+";

                std::stringstream fpath;
                fpath << pathToAUResults << '/' << curTimestamp << "-" << std::setw(10) << std::setfill('0') << idx << "_results_" << featureType << ".txt";

                std::ofstream fl(fpath.str());
                fl << AUoutput.str();
                fl.close();
            }
        }


        if (config.visualiseOutput)
            cv::imshow("frame", frame);
        int keyClicked = (char) cv::waitKey(10);
        if (keyClicked == 32)
            break;
        }
        catch (cv::Exception& e)
        {
            std::cout << "Exception!!" << e.what() << std::endl;
            std::cout << "Exception!!" << e.what() << std::endl;
            std::cout << "Exception!!" << e.what() << std::endl;
        }
    }

    /////JO/////
    // No longer needed:
    // SIMPLE DATA OUTPUT COMMENTED
    // normalise AUcounts and print (append) to file
    /*int sum = 0;
    for (size_t i=0; i<config.AUlist.size(); ++i)
    {
        std::string AU = config.AUlist[i];
            std::cout << AU << " appeared " << AUcounts[AU] << std::endl;
        sum += AUcounts[AU];
    }
        std::cout << "Sum to normalize: " << sum << std::endl;
    // print frame rate and frame count
    AUresultsFile << cap.get(CV_CAP_PROP_FPS) << "\t" << FRAME_COUNT << "\t";
    for (size_t i=0; i<config.AUlist.size(); ++i)
    {
        AUresultsFile << (double)AUcounts[config.AUlist[i]] / sum << "\t";
    }*/
    //////////
}




std::set<std::string> AURecogniser::getMatchedAUs(const Mat& feats, std::vector<SVM2>& svms)
{

    std::set<std::string> AUs;

    for (size_t si=0; si<svms.size(); ++si)
    {

        bool exists;

        if (config.use2stageClassification)
            exists = svms[si].predict2stage(feats);
        else
            exists = svms[si].predict(feats);

        if (exists)
            AUs.insert(svms[si].classLabel);

    }


    return AUs;
}



std::vector<SVM2> AURecogniser::getSvms(const std::string& featType)
{

    QDir modelDir(std::string("data/svm/"+featType).c_str());

    modelDir.setNameFilters(QStringList() << "AU*");

    QStringList dirs  = modelDir.entryList(QDir::Dirs | QDir::NoDotAndDotDot);

    std::vector<SVM2> svms;

    for (int i=0; i<dirs.size(); ++i)
    {
        std::stringstream ss;
        ss << modelDir.absoluteFilePath(dirs[i]).toStdString() << "/model";

        svms.push_back(SVM2(ss.str(), dirs[i].toStdString().substr(2)));

    }

    return svms;
}





AURecogniser::~AURecogniser()
{

}

