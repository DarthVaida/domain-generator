#! /usr/bin/env python
versionRCS='$Id: visimilarity.py,v 1.18 2008/05/15 18:14:52 black Exp $'
#            *created  "Fri Dec 21 10:16:01 2007" *by "Paul E. Black"
versionMod=' *modified "Thu May 15 14:08:55 2008" *by "Paul E. Black"'

#------------------------------------------------------------------------
#
# Report the confusability scores for proposed new generic Top-Level
# Domain strings.  The default is to compare the command line string to
#  (1) any other proposed generic TLDs in this round,
#  (2) all current Top-Level Domains (TLDs), and
#  (3) the reserved strings.
# If two strings are given, they are compared to each other.
# If no string is given, strings in the pgTLD file are compared to
# all current Top-Level Domains (TLDs), and the reserved strings.
# --cross-check compares them just to each other.
#
programName='visimilarity'
usageMsg='Usage: '+programName+' [-vh] [--Test] [--other_gTLDs file] [--] [string [string2]]';
minOperands=0;
maxOperands=2;
#
# This software was developed at the National Institute of Standards
# and Technology by employees of the Federal Government in the course
# of their official duties.  Pursuant to title 17 Section 105 of the
# United States Code this software is not subject to copyright
# protection and is in the public domain.  This software is an
# experimental system.  NIST assumes no responsibility whatsoever for
# its use by other parties, and makes no guarantees, expressed or
# implied, about its quality, reliability, or any other
# characteristic.
#
# We would appreciate acknowledgment if this software is used.
#
# This software may be redistributed and/or modified freely provided
# that any modified versions bear some notice that they were modified.
#
# Paul E. Black  paul.black@nist.gov
#
#------------------------------------------------------------------------

import sys
import charSimilarity # just for its version info
import strSimilarity
import visimiCommon

default_propGTLDsFileName = 'propGenTLDs'
# name of file with the proposed generic top-level domain names
propGTLDsFileName = default_propGTLDsFileName

# standard output format: word1 word2 score%
oform = '%-7s %-7s %3d%%'

#------------------------------------------------------------------------------
#	chop: remove any trailing newlines
#------------------------------------------------------------------------------

def chop(string):
    """Remove trailing newlines."""
    return string.rstrip('\n')

def chop_try(testString, expectedString):
    """Check that chop() works in one instance."""
    resultString = chop(testString)
    if resultString != expectedString:
	print "chop failed built-in test."
	print "    It returned '" + resultString + "', and it should"
	print "  have returned '" + expectedString + "'"

def chop_selftest():
    """Built-in self test for chop()."""
    print '    running self test for chop ...'
    chop_try('', '')     # empty string
    chop_try('\n', '')   # just a newline
    # short strings with and without a trailing newline
    chop_try('a', 'a')
    chop_try('a\n', 'a')
    chop_try(' \n', ' ')
    # embedded, leading, doubled, etc. newlines
    chop_try('A city\nset on a hill',   'A city\nset on a hill')
    chop_try('A city\nset on a hill\n', 'A city\nset on a hill')
    chop_try('A city\nset on a hill\n\n', 'A city\nset on a hill')
    chop_try('\nA city set on a hill',   '\nA city set on a hill')
    chop_try('\nA city set on a hill\n\n', '\nA city set on a hill')
    chop_try('m\nss\nss\npp\n', 'm\nss\nss\npp')
    chop_try('m\nss\nss\npp\n\n', 'm\nss\nss\npp')
    # long strings with and without trailing newlines
    chop_try('We, the People of the United States, in order to form a more perfect union',  'We, the People of the United States, in order to form a more perfect union')
    chop_try('We, the People of the United States, in order to form a more perfect union\n', 'We, the People of the United States, in order to form a more perfect union')
    print '    self test for chop done.'

#------------------------------------------------------------------------------
#	matchesOption: true if string matches the option
#           * the string can begin with - or --, and
#	    * the string is a prefix of the option
#	    * at least N characters long (default=1)
#------------------------------------------------------------------------------

def matchesOption(string, opt, minlen=1):
    """Return true if string matches the option."""
    assert(opt[0:2] == '--')

    # string must begin with at least one hyphen
    if string[0:1] != '-': return False
    # if it doesn't begin with two hyphens, stick one on
    if string[0:2] != '--': string = '-' + string

    if len(string) <= len(opt) and len(string) > 2 \
	and string == opt[:len(string)]: return True
    return False

def matchesOption_try(testString, testOption, expectedResult=True):
    """Check that matchesOption() works in one instance."""
    result = matchesOption(testString, testOption)
    if result != expectedResult:
	print 'matchesOption failed built-in test.'
	print '    It returned', result, 'instead of', expectedResult,
	print 'for', testString, 'and', testOption

def matchesOption_selftest():
    """Built-in self test for matchesOption()."""
    print '    running self test for matchesOption ...'
    # short strings
    matchesOption_try('a', '--a', False)
    matchesOption_try('b', '--a', False)
    matchesOption_try('b', '--ab', False)
    matchesOption_try('-C', '--C')
    matchesOption_try('--d', '--d')
    matchesOption_try('-E', '--Ef')
    matchesOption_try('--g', '--gH')
    matchesOption_try('-Ij', '--I', False)
    matchesOption_try('-', '--klock', False)
    matchesOption_try('--', '--klock', False)
    # long strings
    matchesOption_try('-We, the People of the United States, in order to fo',  '--We, the People of the United States, in order to form a more perfect union')
    matchesOption_try('--We, the People of the United States, it order to fo', '--We, the People of the United States, in order to form a more perfect union', False)
    print '    self test for matchesOption done.'

def main():
#------------------------------------------------------------------------------
#	Command line handling
#------------------------------------------------------------------------------

    global propGTLDsFileName

    runAllpgTLDs = False
    crossCheckOnly = False

    oprNo = 1 # skip invocation (program name)
    while oprNo < len(sys.argv):
        if matchesOption(sys.argv[oprNo], '--help'):
            print usageMsg
            print '''\
    where
        --version       Print versions and exit
        --help          Print this message and exit
        --Test          Run built-in self test(s)
        --other_gTLDs file Get other proposed generic TLDs from file
				default is''', propGTLDsFileName, '''
        --cross-check   Score strings in pgTLD file just to each other
        --              End of options (e.g., string begins with -)
report visual simularity of string to current TLDs, reserved words, and other proposed generic TLDs.  If there is no string, report similarity of all names in the pgTLDs file.'''
            return 0
        elif matchesOption(sys.argv[oprNo], '--version'):
            print programName
            print versionRCS
            print versionMod
	    print '    using'
	    print charSimilarity.versionRCS
	    print charSimilarity.versionMod
	    print strSimilarity.versionRCS
	    print strSimilarity.versionMod
	    print visimiCommon.versionRCS
	    print visimiCommon.versionMod
            return 0
        elif matchesOption(sys.argv[oprNo], '--Test'):
	    print 'running built-in self-tests ...'
	    chop_selftest()
	    matchesOption_selftest()
	    strSimilarity.howConfusableAre_selftest()
	    print 'done'
            return 0
        elif matchesOption(sys.argv[oprNo], '--cross-check'):
            crossCheckOnly = True
        elif matchesOption(sys.argv[oprNo], '--other_gTLDs'):
	    if oprNo+1 >= len(sys.argv):
		print 'Missing file name'
		print usageMsg
		return 1
	    oprNo += 1
	    propGTLDsFileName = sys.argv[oprNo]
        elif sys.argv[oprNo] == '--':
	    oprNo += 1
            break
        elif sys.argv[oprNo][0] == '-':
            print 'unknown option: ' + sys.argv[oprNo]
	    print 'use --help for more detail'
            print usageMsg
            return 1
        else:
	    # end of options
            break
        oprNo += 1

    #print 'len(sys.argv)', len(sys.argv), ' oprNo', oprNo, \
    #		 ' minOperands',  minOperands, ' maxOperands',  maxOperands

    if len(sys.argv)-oprNo < minOperands or len(sys.argv)-oprNo > maxOperands:
	print 'wrong number of operands'
        print usageMsg
        return 1

    if oprNo >= len(sys.argv):
        # no name to compare - run all the pgTLDs
	runAllpgTLDs = True
    else:
        # the first operand is the proposed generic Top-Level Domain string
        pgTLDst = sys.argv[oprNo]
        oprNo += 1

    if oprNo < len(sys.argv):
        # the second operand is the other string to compare
        string = sys.argv[oprNo]
        oprNo += 1
        levDist = strSimilarity.levenshtein(pgTLDst, string)
        score = strSimilarity.howConfusableAre(pgTLDst, string)
        print (oform+'  %s') % (pgTLDst, string, score*100+.5, levDist)
        return 0
    
#------------------------------------------------------------------------------
#	Read other proposed generic Top-Level Domains (TLDs)
#------------------------------------------------------------------------------

    try:
	opgtldsFile = open(propGTLDsFileName, 'r')
	opgtlds = map(chop, opgtldsFile.readlines())
    except IOError:
	# can't open file or something
	if propGTLDsFileName != default_propGTLDsFileName:
	    # file on command line - tell user we're not reading it
	    print 'Cannot read', propGTLDsFileName
	    return 1 # if user wants us to read a file but we can't, exit
	opgtlds = []

#------------------------------------------------------------------------------
#	Read current Top-Level Domains (TLDs)
#------------------------------------------------------------------------------

    # True if str is not a comment line (does not start with #).
    def not_comment(str): return len(str) < 1 or str[0] != '#'

    tldsFile = open(visimiCommon.tldsFileName, 'r')
    tlds = filter(not_comment, map(chop, tldsFile.readlines()))

#------------------------------------------------------------------------------
#	Read reserved words
#------------------------------------------------------------------------------

    reservedFile = open(visimiCommon.reservedNamesFileName, 'r')
    reservedNames = filter(not_comment, map(chop, reservedFile.readlines()))

#------------------------------------------------------------------------------
#	Compare the word (or all proposed gTLDs) to
#          - reserved names,
#	   - current Top-Level Domains, and
#	   - (other) proposed gTLDs
#	or only proposed gTLDs to each other
#------------------------------------------------------------------------------

    # develop the list of names to run
    if runAllpgTLDs:
        if not opgtlds:
	    print 'No proposed gTLDs read, so nothing to run!'
	    return 1
	nameList = opgtlds
    else:
        nameList = [pgTLDst]

    if crossCheckOnly:
        # cross check all pgTLDs with each other
        for index in range(len(nameList)):
            for otherIndex in range(index+1, len(nameList)):
                curWord = nameList[index]
                targetName = nameList[otherIndex]
                score = strSimilarity.howConfusableAre(curWord, targetName)
                if score > visimiCommon.defaultThreshold:
                    print oform % (curWord, targetName, score*100+.5)
        return

    # develop the list of names to run against
    if runAllpgTLDs:
        currentList = tlds + reservedNames
    else:
        currentList = tlds + reservedNames + opgtlds

    # run all the names
    for targetName in nameList:
        for curWord in currentList:
	    if targetName.lower() == curWord.lower():
	        if curWord in tlds:
		    source = 'current TLD'
	        elif curWord in reservedNames:
		    source = 'reserved name'
                else:
		    source = 'proposed generic TLD from '+propGTLDsFileName
	        print '"'+targetName+'" is a', source, 'and is not allowed'
	    score = strSimilarity.howConfusableAre(targetName, curWord)
	    # SKIMP contribute to global score
            if score > 0.1:
	        print oform % (curWord, targetName, score*100+.5)
	    # SKIMP It may be hard to figure out why a string gets scores it
            # does.  For instance, AD and aA get 27%.  It would be useful to 
	    # explain that d and a are similar in some fonts.  This gets
	    # more important when the strings have digraph matches, etc.


        # If targetName is highly confusable with many current TLD
        # strings, but not over the threshold for any one of them, the
        # algorithm should advise that it be failed.

if __name__ == '__main__':
    main()

# end of $Source: /home/black/GTLD/RCS/visimilarity.py,v $
