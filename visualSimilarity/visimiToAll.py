#! /usr/bin/env python
versionRCS='$Id: visimiToAll.py,v 1.7 2008/05/15 18:15:16 black Exp $'
#            *created  "Mon Mar 24 15:50:28 2008" *by "Paul E. Black"
versionMod=' *modified "Thu May 15 14:10:25 2008" *by "Paul E. Black"'

#------------------------------------------------------------------------
#
# Report the confusability scores for a proposed new generic Top
# Level Domain (TLD) string against
#  (1) any other proposed generic TLD in this round,
#  (2) all current Top-Level Domains (TLDs), and
#  (3) the reserved strings.
#
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

import cgi
# save exception info to a file in my home directory
#import cgitb; cgitb.enable(display=0, logdir="/export/home/black/ErrorReports")
import sys
import strSimilarity
import visimiCommon

default_propGTLDsFileName = 'propGenTLDs'
# name of file with the proposed generic top-level domain names
propGTLDsFileName = default_propGTLDsFileName

#------------------------------------------------------------------------------
#	chop: remove any trailing newlines
#------------------------------------------------------------------------------

def chop(string):
    """Remove trailing newlines."""
    return string.rstrip('\n')

def main():

    global propGTLDsFileName

    # MIME type declaration
    print 'Content-Type: text/html'
    print

    # document preface
    print '''
<!DOCTYPE HTML PUBLIC "-//IETF//DTD W3 HTML 2.0//EN">
<HTML>
<HEAD>
<TITLE>Visual Similarity of a String to Other TLDs, etc.</TITLE>
<!-- turn off Microsoft's added smart tags -->
<meta name="MSSmartTagsPreventParsing" content="TRUE">
</HEAD>
<BODY>
'''

    # return the standard trailer
    def standardWebPageTrailer():
        # standard Return to Home
        visimiCommon.catFile('webPageReturn')

        print '''
<HR>

<EM>Created Mon Mar 24 15:50:28 2008
</EM><ADDRESS>
by <a href="/~black/">Paul E. Black</a>
&nbsp;(<a href="mailto:paul.black@nist.gov">paul.black@nist.gov</a>)
</ADDRESS>
<EM>Updated
Thu May 15 14:10:25 2008
</EM><ADDRESS>
by <a href="http://hissa.nist.gov/~black/">Paul E. Black
</a>
&nbsp;(<a href="mailto:paul.black@nist.gov">paul.black@nist.gov</a>)
</ADDRESS>
'''

        # standard disclaimer, etc.
        visimiCommon.catFile('webPageTrailer')


    # standard (visible) "title"
    visimiCommon.catFile('webPageTitle')

#------------------------------------------------------------------------------
#	Get form field
#------------------------------------------------------------------------------

    form = cgi.FieldStorage()
    if len(sys.argv) > 1:
        # SKIMP use command line string
        pgTLDst = sys.argv[1]
    else:
        # this occurs if user doesn't put anything in the pgtld field
        if not (form.has_key('pgtld')):
            print 'Please put something in the field.'
	    standardWebPageTrailer()
            return

        pgTLDst = form['pgtld'].value

    # strip anything other than letters, digits, and hyphen
    pgTLDst = filter(visimiCommon.allowedCharPred, pgTLDst)

    # no alphanumeric characters
    if len(pgTLDst) < 1:
        print 'You did not enter any digits or letters.'
        standardWebPageTrailer()
        return

    # display entered string
    print '''
<p>
You entered
</p>
'''
    print '<H3>.%s</H3>\n' % pgTLDst

    # don't allow really long strings - takes too much time to compute
    if len(pgTLDst) > 63:
        print '<p>That is longer than the 63 characters in RFC 1035.</p>'
        standardWebPageTrailer()
        return

#------------------------------------------------------------------------------
#	Read other Top-Level Domains (TLDs)
#------------------------------------------------------------------------------

    #	Read other proposed generic Top-Level Domains (TLDs)
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

    #--------------------------------------------------------------------------
    #	Read current Top-Level Domains (TLDs)
    #--------------------------------------------------------------------------

    # True if str is not a comment line (does not start with #).
    def not_comment(str): return len(str) < 1 or str[0] != '#'

    tldsFile = open(visimiCommon.tldsFileName, 'r')
    tlds = filter(not_comment, map(chop, tldsFile.readlines()))

    #--------------------------------------------------------------------------
    #	Read reserved words
    #--------------------------------------------------------------------------

    reservedFile = open(visimiCommon.reservedNamesFileName, 'r')
    reservedNames = filter(not_comment, map(chop, reservedFile.readlines()))

#------------------------------------------------------------------------------
#	Compare the word to
#          - reserved names,
#	   - current Top-Level Domains, and
#	   - (other) proposed gTLDs
#	Save matches, strings above threshold, etc.
#------------------------------------------------------------------------------

    exactMatch = ''
    aboveThreshold = False # no string is too similar
    verySimilarStrings = ''
    # don't save 0 scores.  0% may be the highest score for really long
    # strings, and all the current TLDs get 0%!
    mostSimilarScore = 0.1 
    mostSimilarStrings = '' # all strings getting mostSimilarScore

    # (this reassignment is for consistency with command line version)
    targetName = pgTLDst

    # standard output format: word1 word2 score%
    htmloform = '<TR>\n  <TD>.%s</TD><TD>.%s</TD><TD align="right">%3d%%</TD>\n</TR>\n'

    for curWord in tlds + reservedNames + opgtlds:
        if targetName.lower() == curWord.lower():
            if curWord in tlds:
                source = 'current TLD'
            elif curWord in reservedNames:
	        source = 'reserved name'
            else:
		# don't report self-matches
		# SKIMP: matching pgTLDs are NOT reported
		if runAllpgTLDs: continue
                source = 'proposed generic TLD from '+propGTLDsFileName
            exactMatch = '<p>.'+targetName+' is a '+source+' and is not allowed</p>\n'

        score = strSimilarity.howConfusableAre(targetName, curWord)
        percentScore = int(score*100 + .5)
        if score > 0.75:
            aboveThreshold = True
        # save strings above a similarity threshold
        if score > visimiCommon.defaultThreshold:
            verySimilarStrings = verySimilarStrings +\
                    htmloform % (targetName, curWord, percentScore)
        # save most similar string(s)
        if percentScore > mostSimilarScore:
            mostSimilarScore = percentScore
            # start over with a new list of most similar strings
            mostSimilarStrings = ''
        if percentScore == mostSimilarScore:
            mostSimilarStrings = mostSimilarStrings +\
                    htmloform % (targetName, curWord, percentScore)

#------------------------------------------------------------------------------
#	Print result of comparisons
#------------------------------------------------------------------------------

    tablePreamble = '''
<TABLE cellspacing="0" border>
<TR>
 <TH>Applicant String</TH><TH>Indexed String</TH><TH>% Score</TH>
</TR>
'''

    #--------------------------------------------------------------------------
    #	Very similar strings (and an exact match)
    #--------------------------------------------------------------------------

    if verySimilarStrings or exactMatch:
        print '<H2>Quite Similar String(s)</H2>\n'
        print '<p>Following are the proposed and existing Top-Level Domains and reserved words that are visually quite similar to .'+pgTLDst, '</p>\n'
        if exactMatch:
            print exactMatch
        elif aboveThreshold:
            print '<p>Because .'+pgTLDst, 'is too similar to one or more of the following strings, it is unlikely to be accepted.</p>\n'

        print tablePreamble
        print verySimilarStrings
        print '</TABLE>'

    #--------------------------------------------------------------------------
    #	Most similar strings if none are very similar
    #--------------------------------------------------------------------------

    elif mostSimilarStrings:
        print '<H2>Most Similar String(s)</H2>\n'
        print '<p>Following are the proposed and existing Top-Level Domains and reserved words most similar to .'+pgTLDst, '</p>\n'
        
        print tablePreamble
        print mostSimilarStrings
        print '</TABLE>'

    #--------------------------------------------------------------------------
    #	If no strings are similar (really long submission)
    #--------------------------------------------------------------------------

    else:
        print '<p>No existing Top-Level Domain or reserved word is similar.</p>'

#------------------------------------------------------------------------------
#	Page trailer
#------------------------------------------------------------------------------
    standardWebPageTrailer()

if __name__ == '__main__':
    main()

# end of $Source: /home/black/GTLD/RCS/visimiToAll.py,v $
