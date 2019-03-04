#######################################################################################################
# Author: Jan Ondras
# Institution: University of Cambridge
# Project: Replicating Human Facial Emotions and Head Movements on a Robot Avatar (Part II Project)
# Duration: October 2016 - May 2017
####################################################################################################### 
# Merge whole detailed features featuresD with labels
# 593 examples produced
#	in: featuresD.dat, labels.dat
#	out: exAll.dat, IDexAll.dat
#	match feature vectors with labels with or without subjectID: exAll.dat IDexAll.dat
#######################################################################################################

from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
import csv

inFeatures = './features/featuresD.dat'
inLabels = './labels/labels.dat'
outExamples = './examples/exAll1.dat'

labels = np.genfromtxt(inLabels, usecols = (0, 1, 3))	# take subjectID, sequenceID, label
examples = []
TOTAL_AUS = 12

with open(inFeatures, 'rb') as ff:
    for row in csv.reader(ff, delimiter='\t'):

		rowFloat = [np.float64(elem) for elem in row if elem is not '']

		# match corresponding label to feature
		l = 0.		# label
		for label in labels:
			if( (rowFloat[0] == label[0]) and (rowFloat[1] == label[1]) ):
				l = label[2]
				break

		example = rowFloat[4:]
		example.append(l)
		examples.append(example)

    ff.close()

f = open(outExamples, 'w')
np.savetxt(outExamples, examples, delimiter = ' ', fmt='%s')
f.close()
# need to manually delete "," and brackets!



################################################################################################################################
# same as above but with subjectID as a first field
'''
inFeatures = './features/featuresD.dat'
inLabels = './labels/labels.dat'
outExamples = './examples/IDexAll.dat'

labels = np.genfromtxt(inLabels, usecols = (0, 1, 3))	# take subjectID, sequenceID, label
examples = []
TOTAL_AUS = 12

with open(inFeatures, 'rb') as ff:
    for row in csv.reader(ff, delimiter='\t'):

		rowFloat = [np.float64(elem) for elem in row if elem is not '']

		# match corresponding label to feature
		l = 0.		# label
		for label in labels:
			if( (rowFloat[0] == label[0]) and (rowFloat[1] == label[1]) ):
				l = label[2]
				break

		example = [rowFloat[0]]				# add subjectID
		example.extend(rowFloat[4:])
		example.append(l)
		examples.append(example)

    ff.close()

f = open(outExamples, 'w')
np.savetxt(outExamples, examples, delimiter = ' ', fmt='%s')
f.close()
# need to delete "," and brackets!
'''