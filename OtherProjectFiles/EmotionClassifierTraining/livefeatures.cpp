/*
    Modified by: Jan Ondras
    Institution: University of Cambridge
    Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
    Duration: October 2016 - May 2017
    
    All my modifications are enclosed between '/////JO/////' and '//////////'.

    This is only for extracting features for Emotion Classifier training => need to replace the current livefeatures.cpp file in AUD folder

    NEED TO SPECIFY PATH WHERE TO PUT FEATURES (below)
*/

#include <opencv2/highgui/highgui.hpp>
#include <opencv2/video/tracking.hpp>

#include <opencv2/objdetect/objdetect.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/core/core_c.h>

#include <opencv2/ml/ml.hpp>

#include "QLZM3D.hpp"
#include <Image.hpp>
#include <GaborBank.hpp>
#include <string>
#include <chrono>

#include "Config.hpp"

#include "FaceUtils.hpp"
#include "AURecogniser.hpp"

#define VISUALISE


// Ctrl+C signal handler
#include  <signal.h>

sig_atomic_t interruptSignal;

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        std::cerr << "No config file was specified! The first argument in the command line needs to be the path to confg file.";
        return -1;
    }

    AURecogniser recogniser(argv[1]);

    if (recogniser.config.cameraId == -1) //! AU Recognition from video file
    {
        std::string tmp = argv[2];

        //! The video file to recognise the AUs from and the (optional) calibration file is
        //! provided as a single argument in the form of path-to-videofile.avi;path-to-calibvideofile.avi
        std::vector<std::string> paths = Config::splitStrings(tmp,  '-');

        std::string sessionName(""), calibfilePath("");
        if (argc >= 4)
            sessionName = argv[3];

        if (paths.size() > 1)
            calibfilePath = paths[1];

        recogniser.setRecordingPaths(sessionName, true);

        /////JO/////
        // open file here
        // GEMEP
        recogniser.AUresultsFile.open ("../_src/EmotionClassifier/data/rawFeaturesFromAU/featuresD_GEMEC.dat", std::ios::app);
        // CK+
        // recogniser.AUresultsFile.open ("../_src/EmotionClassifier/data/rawFeaturesFromAU/features.dat", std::ios::app);
        // print subject and sequence ID
        // CK+
        // recogniser.AUresultsFile << paths[0].substr(paths[0].length() - 11, 3) << "\t" << paths[0].substr(paths[0].length() - 7, 3) << "\t";
        //////////

        recogniser.recogniseFromVideoFile(paths[0], calibfilePath);

        /////JO///// close file here
        recogniser.AUresultsFile << "\n";
        recogniser.AUresultsFile.close();
        //////////
    }
    else //! AU Recognition from video stream
    {
        std::string sessionName("");
        if (argc >= 3)
            sessionName = argv[2];

        recogniser.setRecordingPaths(sessionName);

        bool parseCalibDataFromRecordings = false;
        if (argc >= 4 && std::string(argv[3]) == "1")
            parseCalibDataFromRecordings = true;


        if (argc >= 5 && std::string(argv[4]) == "1") {
            cv::VideoCapture cap(recogniser.config.cameraId);
            recogniser.calibration(cap);
            return 0;
        }

        recogniser.recogniseFromLiveStream(parseCalibDataFromRecordings);
    }


    return 0;
}
