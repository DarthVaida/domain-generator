# $Id: Makefile,v 1.4 2008/07/22 14:25:50 black Exp $
# *created  "Fri Dec 21 10:16:01 2007" *by "Paul E. Black"
# *modified "Tue Jul 22 10:24:05 2008" *by "Paul E. Black"

# source code for the web site
SOURCE=charSimilarity.py strSimilarity.py visimiCommon.py \
	visimiToAll.py visimiGauge.py
# support files for the web site
SUPPORT=topLevelDomains reservedNames visim_TresNames \
	webPage[RT]*[nre] warns_not_wams.jpg \
	tldVisualSimilarity.html

tldVisualSimilarity.html: webPageHeader webPageTitle tldVisualSimilarityBody webPageFooter
	cat $^ > $@

tar: visualSimilarity.tar
	echo done

visualSimilarity.tar: README Makefile ${SOURCE} ${SUPPORT} \
	visim_T[0-9A-Za-qs-z]*[a-z] visimilarity.py \
	webPageFooter webPageHeader tldVisualSimilarityBody
	tar -cvf $@ $^

GTLDwebsite.tar: ${SOURCE} ${SUPPORT} visualSimilarity.tar
	tar -cvf $@ $^

run:
	python -t -Wmodule visimilarity.py

clean:
	rm -f *.pyc *.out tldVisualSimilarity.html GTLDwebsite.tar

# end of $Source: /home/black/GTLD/RCS/Makefile,v $
