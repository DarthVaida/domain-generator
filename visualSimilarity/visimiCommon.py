#! /usr/bin/env python
versionRCS='$Id: visimiCommon.py,v 1.6 2008/05/15 18:21:07 black Exp $'
#            *created  "Tue Apr  1 16:38:25 2008" *by "Paul E. Black"
versionMod=' *modified "Thu May 15 14:11:41 2008" *by "Paul E. Black"'

#------------------------------------------------------------------------
#
# Common definitions, routines, etc. for visual similarity algorithm.
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

# The local file with current Top-Level Domains, including generic TLDs
# (gTLDs), such as ".COM", and country-code TLDs (ccTLDs), such as ".UK".
# Available at http://www.iana.org/domains/root/db/
tldsFileName = 'topLevelDomains'

# The name of the local file with the reserved names
reservedNamesFileName = 'reservedNames'

# Default threshold to report similarity.  That is, scores must be
# greater than this to be reported.
defaultThreshold = 0.10 # 10%

# return a file's content
def catFile(filename):
    # SKIMP no error handling
    fileHandle = open(filename, 'r')
    print ''.join(fileHandle.readlines())

# predicate to strip anything other than letters, digits, and hyphen
# see RFC 1035 2.3.1 http://www.faqs.org/rfcs/rfc1035.html
# typical usage is
#    string1 = filter(allowedCharPred, string1)
def allowedCharPred(ch): return ch.isalnum() or ch == '-'

# end of $Source: /home/black/GTLD/RCS/visimiCommon.py,v $
