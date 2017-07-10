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


# Check which characters have possible confusable replacements in the given domain name
def getPossibleChars():
	tmp = []
	map = []
	for i in charSimilarity.scsimtab:		
		tmp.append([i[0],i[1],charSimilarity.scsimtab[i[0],i[1]]])
	#testPossibleChars(tmp)
	
	# Can't use a dictionary here because of duplicate value mappings: i.e. 1 can be substituted with i,l,etc. 
	# Just do it nice and slow ..
	# Look for possible substitution candidates in the given string
	for i in domain:
		for j in tmp:
			# Don't bother with low values. Characters not very similar and will make the computation longer.
			# Decrease the minimumRating value if the script returns too few results
			if j[2] >= minimumRating:
				if 	(i == j[0]) & ([j[0],j[1],int(j[2]*scale)] not in map):
					map.append([j[0],j[1],int(j[2]*scale)])
				elif (i ==j[1]) & ([j[1],j[0],int(j[2]*scale)] not in map):
					# Swap the order
					map.append([j[1],j[0],int(j[2]*scale)])
			
	# Create a map in the following format:
	# [Character, Substitute, Similarity]
	# i.e. 
	# map = [
	# ['s', '$', 6],
	# ['i', '1', 7],	
	# ['o', '0', 8],
	# ['m', 'nn', 9]]

	# Sort the map
	map = sorted(map, key=lambda element: element[2])
	if Verbose :
		print "Initial map"
		for i in map:
			print i
 		print ""

 	# Need to make each rating value unique. Luckily, there is a limited number of characters allowed in domain names
 	# and not many of them are visually similar. See the scsimtab in charSimilarity.py .
 	# We will slightly adjust the last column of the map.
 	# Instead of having four entries with rating 50, we'll have 48,49,50 and 51.
 	# We need this for the algorithm to work !
 	# TO DO: assign ratings based on the position of the character in the string. Characters in the middle of a string are
 	# 		 much easiear to misread compared to the start or end of the string. 
 	#        I.E. microsoft -> icrosoft - you'll probably notice the missing 'm'
 	#		                -> micosoft - the missing 'f' is easier to overlook
 	
 	right = scale
 	left = 0
 	i = 1
 	while i < len(map)-1:
 		count = 0
 		left = 0 if i==1 else map[i-2][2]
 	
 		
 	
 		while (map[i+count][2] == map[i+count-1][2]):			
 			if count+i == len(map)-1:
 				break
 			else:
 				count+=1
 		
 		right = map[i+count][2]
 		c = count
 		while (map[i+count-1][2]>left) & (map[i+count-1][2]<right) & (count>=0):
  			map[i+count-1][2] += count - c/2
  			count-=1
  		i+= max(1,c+1)

  	if Verbose :
  		print "Map with unique values:"
  		for i in map:
			print i
	#used for testing
 	#nap = [
 	# ['s', '$', 6],
	# ['i', '1', 7],	
	# ['o', '0', 8],
	# ['m', 'nn', 9]]
	
	
# This must be sorted for the algorithm to work
	return map


def testPossibleChars(map):
	for i in map:
		if charSimilarity.scsimtab[i[0],i[1]]!=i[2]:
			print "Test failed",charSimilarity.scsimtab[i[0],i[1]],i[2]
	print "Test passed"


# Populate a matrix bottom up
# This algorithm is a variation of the coin changing problem:
# Original problem: Given a number of coin denominations, and a target sum, what is the minimum number of coins to obtain that sum.
# Solution: Classic Dynamic Programming  
# 	Create a 2D array (I will refer to it as a matrix):
#		- Rows correspond to coin denominations. 
#		- Columns correspond to increasing values, ending at the specified target.
#	Populate 

# Note that we obtain a very sparse matrix. 
# Could be implemented with a more space efficient data structure, i.e. hashmap/ table / dictionary / whatever fancy name you want
def populatematrix():	
	

	# Populate first row
	for i in range (1,m.shape[1]):
		if (i % chars[0][2] == 0) & (i / chars[0][2] < cutoff):
			m[0][i] = (i / chars[0][2])
			#memoTable[0,i] = chars[0][2]
			
	# Go through the rest of the matrix
	for i in range (1,m.shape[0]):
		for j in range (1,m.shape[1]):
			
			if j >= chars[i][2]:
				
				
				if j % chars[i][2] == 0 :
					tentativevalue = j / chars[i][2]
					#memoTable[i,j] = chars[i][2]

				elif (m[i][j-chars[i][2]] == 0) :
					tentativevalue = m[i-1][j]

				elif (m[i-1][j]==0):
					# We use the current letter in the substitution
					tentativevalue = 1+ m[i][j-chars[i][2]]
					# Memo it. This will help for reconstruction later
					#memoTable[i,j] = chars[i][2]
				else :
					# We use the current letter in the substitution
					tentativevalue = min(m[i-1][j], 1+ m[i][j-chars[i][2]])
					# Memo it. This will help for reconstruction later
					#if (m[i-1][j] >= 1+ m[i][j-chars[i][2]]):
						#memoTable[i,j] = chars[i][2]		
				if tentativevalue <= cutoff :
					m[i][j] = tentativevalue
			else :
				m[i][j] = m[i-1][j]

# Reconstruct character replacement combinations
# ===============================================
# Rationale: Each non-zero element in the bottom row corresponds to a (non-unique) set of character substitutions.
# In other words: Every value that has propagated to the bottom of the matrix tells us there is a string similar to our domain. 
# 				  How similar? We don't know yet. All we know is that at each step, we tried to use as few characters as possible while looking 
#				  for the ones with the highest similarity ratings. The path that the algorithm has taken to create this value in the bottom row 
#				  gives us the set of characters that we can substitute in the domain name. Having found the sets of characters, we can change 
# 				  them for their substitutes and generate similar strings. 
# ===============================================

# Description of method:
# For each non-zero element in the bottom row walk up the matrix and find the path that produced its value
# We memo the values as we iterate through the row to avoid duplication.
#	
# This method produces a results map of proposed similar words and their rating.
# Note the rating is given by the product of individual character substitiution similarity. It is not an 'official' rating, 
# but is a good indicator of words that are likely to be similar to the given one. Based on this rating we will choose 
# which words to prioritize later for a validation against NIST's tool.
# 
# The values of character similarities are sub-unitary (<1). 
# 	-- The more substitutions we use, the smaller the rating. Intuitive.. you don't want to change too much
#	-- Substitutions of characters with small similarity will lead small ratings. Using several such characters will get you close to 0.
def reconstructCombinations():

	for i in range(m.shape[1]-1,-1,-1):
		if Verbose :
			print "\nStarting at ",m.shape[0]-1,i
		reconstruct(m.shape[0]-1,i,[])


# Reconstruct a single path that ends at m[i][j]
# i should always be the final row of the matrix when this method is called externally
# In essence we are printing all root-to-leaf paths of a binary tree with the root at m[i][j]
#
# Think of it as an upside down binary tree (in fact more like a Trie):
# Each node can have a left or up branch (or both)
#          
#		leaf - (o)	
#  				|  
#  leaf - (o)---o  (o) - leaf
#				|   |
#				o---o 
#					|
#  			   	   root

def reconstruct(i,j,listOfSubs):
	
	# Edge cases
	if m[i][j] == 0 :

		if Verbose :
			print "\t0 -- End of path"
			print "PATH: "
			for sub in listOfSubs:
					print sub[0]
			print getCombinationRating(listOfSubs)
			if len(listOfSubs) != 0 :
				print getWord(domain,listOfSubs)
				results[getWord(domain,listOfSubs)] = getCombinationRating(listOfSubs)
		else :
			if len(listOfSubs) != 0 :
				#print getWord(domain,listOfSubs),getCombinationRating(listOfSubs)
				results[getWord(domain,listOfSubs)] = getCombinationRating(listOfSubs)
		return

	if i==0 :
		for x in range (0,int(m[0][j]-1)+1):
			listOfSubs.append(chars[0])

		if Verbose :
			print "PATH: "
			for sub in listOfSubs:
					print sub[0]
			print getCombinationRating(listOfSubs)
			if len(listOfSubs) != 0 :
				print getWord(domain,listOfSubs)
				results[getWord(domain,listOfSubs)] = getCombinationRating(listOfSubs)
		else :
			if len(listOfSubs) != 0 :
				#print getWord(domain,listOfSubs),getCombinationRating(listOfSubs)
				results[getWord(domain,listOfSubs)] = getCombinationRating(listOfSubs)
		return


	# Reached the beginning of the sequence
	if m[i][j] == 1 :
		while ((m[i-1][j]== 1) & (i>0)):
			i=i-1
		# Reached the top row or zeroes above.
		# Found the first substitution.
		listOfSubs.append(chars[i])

		if Verbose :
			print "\t1 -- End of path",i,j,m[i-1][j],1+ m[i][j-chars[i][2]], chars[i][2]
			print "PATH: "
			for sub in listOfSubs:
					print sub[0]
			print getCombinationRating(listOfSubs)
			if len(listOfSubs) != 0 :
				print getWord(domain,listOfSubs)
				results[getWord(domain,listOfSubs)] = getCombinationRating(listOfSubs)
		else :
			if len(listOfSubs) != 0 :
				#print getWord(domain,listOfSubs),getCombinationRating(listOfSubs)
				results[getWord(domain,listOfSubs)] = getCombinationRating(listOfSubs)
		return

		# If the value above is 0, the path came from the left
		# Recurse left
	elif (m[i-1][j]==0) :
		listOfSubs.append(chars[i])
		if Verbose :
			print "\t2.1 -- Jump left ",i,j,m[i-1][j],1+ m[i][j-chars[i][2]], chars[i][2]
		reconstruct(i,j-chars[i][2],listOfSubs)

		# Value came from above
		# Recurse up
	elif (m[i][j-chars[i][2]]==0) :
		if Verbose:
			print "\t2.2 -- Jump up ",i,j,m[i-1][j],1+ m[i][j-chars[i][2]], chars[i][2]
		reconstruct(i-1,j,listOfSubs)

		# Value came from above
		# Recurse up
	elif (m[i-1][j] < 1+ m[i][j-chars[i][2]]):
		listOfSubs.append(chars[i])
		if Verbose :
			print "\t3.1 -- Jump up",i,j,m[i-1][j],1+ m[i][j-chars[i][2]]
		reconstruct(i-1,j,listOfSubs)
	
		# Value came from the left	
		# Recurse left
	elif (m[i-1][j] > 1+ m[i][j-chars[i][2]]) :
		listOfSubs.append(chars[i])
		if Verbose:
			print "\t3.2 -- Jump left",i,j,m[i-1][j],1+ m[i][j-chars[i][2]]
		reconstruct(i-1,j,listOfSubs)


		# Value can come from both directions.
		# Recurse both ways
	elif (m[i-1][j]) == (1+ m[i][j-chars[i][2]]):
		temp = copy.copy(listOfSubs)
		listOfSubs.append(chars[i])
		if Verbose:
			print "\t4 -- Jump both ways",i,j,m[i-1][j],1+ m[i][j-chars[i][2]]
		reconstruct(i,j-chars[i][2],listOfSubs)
		reconstruct(i-1,j,temp)

def getCombinationRating(listOfSubs):
	if len(listOfSubs) == 0 :
		return 0
	rating = 1;
	for i in listOfSubs:
		rating *= (float(i[2])/float(scale))
	return rating

# Iteratively substitute each letter in @word, based on the @listOfSubs
def getWord(word,listOfSubs):
	similarWord = copy.copy(word)
	for i in listOfSubs:
		similarWord = similarWord.replace(i[0],i[1],1)
	return similarWord

# Validation
# Re-order the results according to NIST's tool
def validateResults():
	global domainResolution
	# Counter
	c = 0
	for i in sorted(results.items(),key=operator.itemgetter(1), reverse=True):
		#print i[0], i[1]

		line = os.popen("python visualSimilarity/visimilarity.py "+domain+" "+str(i[0])).read().split()
		validatedResults[line[1]] = int(line[2][:-1])

		c+=1
		if (c == maxResults) | (i[1] < minDisplayRating):
			break
	# We don't need the huge @results anymore
	# Hope for the best
	gc.collect()
	if domainResolution :
		checkAvailableDomains()

def checkAvailableDomains():
	try:
		for i in sorted(validatedResults.items(),key=operator.itemgetter(1), reverse=True):
			print checkAvailability(i[0]+".com"),str(i[1])+"%"
			print checkAvailability(i[0]+".co.uk"),str(i[1])+"%"
			print checkAvailability(i[0]+".uk"),str(i[1])+"%"	
	except KeyboardInterrupt:
		print "\nExiting script. Bye!" 

def checkAvailability(domain):
	whoisout = os.popen("whois "+domain).read()
	regex = re.compile("This domain name has not been registered.")
	if regex.search(whoisout):
		s = bcolors.OKGREEN+domain+"\t- available"+bcolors.ENDC
	else:
		s = bcolors.FAIL+domain+"\t- unavailable"+bcolors.ENDC
	time.sleep(1)
	return s



############################################################################
# Main method
############################################################################


def main():
	global results
	global validatedResults
	global maxResults
	global minDisplayRating
	global cutoff
	global Verbose
	global domain
	global domainResolution
	global scale
	global minimumRating
	global chars
	global target
	global m	


	results = {}
	validatedResults = {}
	# Maximum number of results to be displayed
	maxResults = 30
	# Minimum rating required for results to be displayed
	minDisplayRating = 0.2	
	# Defines the number of allowed substitutions
	cutoff = 2
	# Scale things up to apply coin changing algorithm
	scale = 100
	minimumRating = 0.2
	# Look for possible character substitutions in the provided domain
	target = 200




	# Param handling
	# ================================================================
	Verbose = False
	domainResolution = False
	domain = sys.argv[1]

	for i in range(2, len(sys.argv)):
		if sys.argv[i] == '-v':
			Verbose = True
			print "Verbose mode on."
		if sys.argv[i] == '-d':
			domainResolution = True


	
	chars = getPossibleChars()
	if Verbose:
		print chars

	m = (len(chars),target+1)
	m = np.zeros(m)


	populatematrix()
	if Verbose:
		print m
		print ""

	reconstructCombinations()
	print "The following visually similar strings were found:"
	
	validateResults()

	#checkAvailableDomains()



	#Testing
	#print "============================"
	#print m[numOfChars-4,90]
	#print m[numOfChars-3,90]
	#print m[numOfChars-2,90]
	#print m[numOfChars-1,90]
	#reconstruct(numOfChars-1,90,[])



	#TO DO 
	# smart whois & grep .com .uk etc
	# handle words with duplicate letters
	# multi letter substitution 
	# handle deletion & insertion 

if __name__ == '__main__':
    main()
