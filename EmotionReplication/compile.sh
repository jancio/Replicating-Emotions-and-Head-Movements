#/usr/bin/bash
qmake AUDetector.pro -r -spec linux-g++-64 CONFIG+=debug CONFIG+=declarative_debug CONFIG+=qml_debug CONFIG+=configLive
make
