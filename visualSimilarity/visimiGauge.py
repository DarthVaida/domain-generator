#! /usr/bin/env python
versionRCS='$Id: visimiGauge.py,v 1.4 2008/05/15 18:20:44 black Exp $'
#            *created  "Tue Mar 25 16:22:20 2008" *by "Paul E. Black"
versionMod=' *modified "Thu May 15 14:10:58 2008" *by "Paul E. Black"'

#------------------------------------------------------------------------
#
# Report the confusability scores for two domain names.
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
import sys
import strSimilarity
import visimiCommon

def main():

    # MIME type declaration
    print 'Content-Type: text/html'
    print

    # document preface
    print '''
<!DOCTYPE HTML PUBLIC "-//IETF//DTD W3 HTML 2.0//EN">
<HTML>
<HEAD>
<TITLE>Visual Similarity of Two Strings</TITLE>
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
Thu May 15 14:10:58 2008
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
#	Get form fields
#------------------------------------------------------------------------------

    form = cgi.FieldStorage()
    # this occurs if user doesn't put anything in the field
    if not (form.has_key("string1")):
        print '<p>Please enter something for String 1.</p>'
        standardWebPageTrailer()
        return

    if not (form.has_key("string2")):
        print '<p>Please enter something for String 2.</p>'
        standardWebPageTrailer()
        return

    string1 = form["string1"].value
    string2 = form["string2"].value

    # strip anything other than letters, digits, and hyphen
    string1 = filter(visimiCommon.allowedCharPred, string1)
    string2 = filter(visimiCommon.allowedCharPred, string2)

    if len(string1) < 1:
        print 'You did not enter any digits or letters in String 1.'
        standardWebPageTrailer()
        return

    if len(string2) < 1:
        print 'You did not enter any digits or letters in String 2.'
        standardWebPageTrailer()
        return

    # display entered string
    print '''
<p>
You entered
</p>
'''
    print '<p><strong>.%s</strong> and <strong>.%s</strong></p>' % (string1, string2)

#------------------------------------------------------------------------------
#	Compare the two strings.
#------------------------------------------------------------------------------

    # standard output format: word1 word2 score%
    htmloform = '<TR>\n  <TD>.%s</TD><TD>.%s</TD><TD align="right">%3d%%</TD>\n</TR>\n'

    score = strSimilarity.howConfusableAre(string1, string2)
    percentScore = int(score*100 + .5)
    comparisonResult = htmloform % (string1, string2, percentScore)

#------------------------------------------------------------------------------
#	Print result of comparison
#------------------------------------------------------------------------------

    tablePreamble = '''
<TABLE cellspacing="0" border>
<TR>
 <TH>String 1 &nbsp; </TH><TH>String 2 &nbsp; </TH><TH>% Score</TH>
</TR>
'''

    print tablePreamble
    print comparisonResult
    print '</TABLE>'

#------------------------------------------------------------------------------
#	Page trailer
#------------------------------------------------------------------------------

    standardWebPageTrailer()

if __name__ == '__main__':
    main()

# end of $Source: /home/black/GTLD/RCS/visimiGauge.py,v $
