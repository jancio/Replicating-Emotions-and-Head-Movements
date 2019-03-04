/*
    Modified by: Jan Ondras
    Institution: University of Cambridge
    Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
    Duration: October 2016 - May 2017
    
    All my modifications are enclosed between '/////JO/////' and '//////////'.
    The original file 'livefeaturesORG.cpp' can be found in this directory.

    Main modifications:
        when starting AUD allow to supply IP and PORT to connect to robot
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
            /////JO/////
            // When detecting from video file: the fourth argument supplied to AUD is "IP:PORT" instead of sessionName
            //sessionName = argv[3];
            recogniser.ipPort = argv[3];
            //////////

        if (paths.size() > 1)
            calibfilePath = paths[1];

        recogniser.setRecordingPaths(sessionName, true);

        recogniser.recogniseFromVideoFile(paths[0], calibfilePath);
    }
    else //! AU Recognition from video stream
    {
        std::string sessionName("");
        if (argc >= 3)
            /////JO/////
            // When detecting from video file: the third argument supplied to AUD is "IP:PORT" instead of sessionName
            //sessionName = argv[2];
            recogniser.ipPort = argv[2];
            //////////

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
