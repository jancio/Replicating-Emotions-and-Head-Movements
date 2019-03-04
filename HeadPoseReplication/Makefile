#
#    Modified by: Jan Ondras
#    Institution: University of Cambridge
#    Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
#    Duration: October 2016 - May 2017
#    
#    All my modifications are labelled as '# Added/Modified by JO'.
#    The original file 'MakefileORG' can be found in this directory.
#
#    Main modifications:
#        added libraries to allow for C++/Python communication
#

CC=g++
OPENCV_INC_DIR=/usr/local/include # or where you put OpenCV include folder
OPENCV_LIB_DIR=/usr/local/lib # or where you put OpenCV lib folder
OPENCV_LIBS=-lopencv_core -lopencv_objdetect -lopencv_imgproc -lopencv_highgui


IDIR=include
LDIR=lib
ODIR=obj
SDIR=src
INTRAFACE_LIB=$(LDIR)/libintraface.a
_DEPS=XXDescriptor.h FaceAlignment.h Marcos.h binary_model_file.h
DEPS=$(patsubst %,$(IDIR)/%,$(_DEPS)) 
_OBJ=DemoDetector.o DemoTracker.o binary_model_file.o
OBJ=$(patsubst %,$(ODIR)/%,$(_OBJ)) 

CFLAGS=-I$(OPENCV_INC_DIR) -I$(IDIR)
LDFLAGS=-L$(OPENCV_LIB_DIR)
# Added by JO
PY_CFLAGS=-I/usr/include/python2.7
# Added by JO
PY_LFLAGS=-lpython2.7

EXECUTABLE1=DemoDetector
EXECUTABLE2=DemoTracker
CLEAN=clean

all: $(EXECUTABLE1) $(EXECUTABLE2)
$(EXECUTABLE1): $(ODIR)/$(EXECUTABLE1).o $(ODIR)/binary_model_file.o $(INTRAFACE_LIB) 
	$(CC) -o $@ $^ $(LDFLAGS) $(OPENCV_LIBS)
$(EXECUTABLE2): $(ODIR)/$(EXECUTABLE2).o $(ODIR)/binary_model_file.o $(INTRAFACE_LIB) 
	$(CC) -o $@ $^ $(LDFLAGS) $(OPENCV_LIBS) $(PY_LFLAGS) # Modified by JO
$(ODIR)/%.o: $(SDIR)/%.cpp $(DEPS)
	$(CC) -c -O3 -o $@ $< $(CFLAGS) $(PY_CFLAGS) # Modified by JO
clean: 
	rm $(OBJ) $(EXECUTABLE1) $(EXECUTABLE2)


	
