#!/usr/bin/python
import re
import time
import numpy as np
import copy as copy
import sys
from visualSimilarity import charSimilarity
import operator
import os as os
import gc as gc

#  ===========================================================================
#  Construct a list of strings that are visually similar to the given input 
#  Usage: generate.py string 												  
#  Options: -v = Verbose (it's probably too Verbose)
#           -d = Domain verification via whois
#  ===========================================================================

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def printmatrix(m,chars):
	file = open("matrix.csv","w")
	# Loop vertically
	for i in range (0,len(chars)):
		# Loop horizontally
		temp = str(chars[i]) 
		for j in range (m.shape[1]):
			temp = temp + ","+str(m[i][j])
		file.write(temp+"\n")



if __name__ == '__main__':
    main()
