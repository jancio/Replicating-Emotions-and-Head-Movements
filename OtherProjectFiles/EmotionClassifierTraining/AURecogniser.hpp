/*
    Modified by: Jan Ondras
    Institution: University of Cambridge
    Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
    Duration: October 2016 - May 2017
    
    All my modifications are enclosed between '/////JO/////' and '//////////'.

    This is only for extracting features for Emotion Classifier training => need to replace the current AURecogniser.hpp file in AUD folder
*/

#ifndef AURECOGNISER_H
#define AURECOGNISER_H

#include <tuple>
#include "Image.hpp"
#include "Config.hpp"
#include "ML.hpp"

using std::vector;
using std::tuple;
using cv::Mat;

class AURecogniser
{
public:
    AURecogniser(const std::string& configFilePath);
    ~AURecogniser();

    Config config;

    /////JO/////
        std::ofstream AUresultsFile;
    //////////

    //! Neutral faces collected during calibration
    vector<tuple<Mat, Mat, Mat> > neutralParts;
    vector<Mat> neutralPtCoords;
    vector<Mat> neutralNormalisedCoords;

    void calibration(cv::VideoCapture& cap, bool showMessage1 = true);

    void recogniseFromVideoCapture(cv::VideoCapture& cap);
    void recogniseFromLiveStream(bool parseCalibDataFromRecordings = false);
    void recogniseFromVideoFile(const std::string& videoFilePath, const std::string& calibVideoFile);

    void setRecordingPaths(std::string& sessionName, bool forceToCreatePaths = false);

    void parseCalibrationDataFromRecordingsFolder();



    bool isSessionBeingRecorded = false;

    std::string pathToAUResults;
    std::string pathToFrames;
    std::string pathToCalibData;

    std::map<std::string, std::vector<SVM2> > svms;

    std::set<std::string> getMatchedAUs(const cv::Mat& feats, std::vector<SVM2>& svms);

    std::vector<SVM2> getSvms(const std::string& featType);

};


#endif // AURECOGNISER_H
