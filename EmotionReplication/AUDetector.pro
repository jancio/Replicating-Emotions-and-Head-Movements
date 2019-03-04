#
#    Modified by: Jan Ondras
#    Institution: University of Cambridge
#    Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
#    Duration: October 2016 - May 2017
#    
#    All my modifications are labelled as '# Modified by JO'.
#    The original file 'AUDetectorORG.pro' can be found in this directory.
#
#    Main modifications:
#        added libraries and INCLUDEPATH to allow for C++/Python communication
#

#-------------------------------------------------
#
# Project created by QtCreator 2013-10-27T14:20:38
#
#-------------------------------------------------

QT       += core

QT       -= gui


# TARGET = batch_qlzm_extractor
TARGET = 3dqlzm_extractor
TARGET = LIVE
TARGET = neutral_feature_extractor

#TARGET = LandmarkDetector
CONFIG   += console
CONFIG   -= app_bundle
# Modified by JO
CONFIG += warn_off

DEFINES += QT_COMPILING_QSTRING_COMPAT_CPP

TEMPLATE = app



INCLUDEPATH += /usr/include/
# Modified by JO
INCLUDEPATH += /usr/include/python2.7


#CONFIG += configTraining
CONFIG += configLive

SOURCES += QLZM.cpp \
           DbCreator.cpp \
    #neutral_feature_extractor.cpp \
    # 3dqlzmextractor.cpp \
    QLZM3D.cpp \
    ML.cpp \
    FaceUtils.cpp \
    FeatureExtractor.cpp \
    Image.cpp \ 
    Utility.cpp \ 
    GaborBank.cpp \
    Config.cpp \
    AURecogniser.cpp

configLive {
    TARGET = LIVE
    SOURCES +=  livefeatures.cpp
}



configTraining {
    TARGET = neutral_feature_extractor
    SOURCES += neutral_feature_extractor.cpp
}

# Modified by JO
# before: ../../include/FaceAlignment.h and ../../include/XXDescriptor.h
HEADERS  += QLZM.hpp \
            DbCreator.hpp \
    FaceAlignment.h \
    XXDescriptor.h \
    QLZM3D.hpp \
    Definitions.hpp \
    Experiments.hpp \
    FaceAlignment.h \
    FeatureExtractor.hpp \
    ML.hpp \
    Image.hpp \
    Utility.hpp \
    GaborBank.hpp \
    FaceUtils.hpp \
    Config.hpp \
    AURecogniser.hpp




#LIBS += -L/home/v/Documents/phd/code/SDM -lintraface
LIBS += -L. -lintraface



LIBS += -L/usr/lib/x86_64-linux-gnu
# Modified by JO
LIBS += -lopencv_core -lopencv_highgui -lopencv_video -lopencv_imgproc -lgomp -lopencv_objdetect  -lboost_regex -lboost_filesystem -lboost_system -lopencv_ml -lpython2.7
#QMAKE_CXXFLAGS += -fopenmp -std=c++0x
QMAKE_CXXFLAGS += -fopenmp -O3 -std=c++0x





