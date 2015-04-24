#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright Â© 2014 He7d3r
# License: http://he7d3r.mit-license.org/
"""
Extermely under construction.
Some parts are copied from
https://gist.github.com/he7d3r/f99482f4f54f97895ccb/9205f3271fe8daa2f694f4ce3ba9b29213dbad6c
"""
from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import SnowballStemmer
import sys
from mw.lib import reverts
from pywikibot import xmlreader
import re

from bad_words_detection_system import Edit, Bot

tokenizer = RegexpTokenizer(
    '[a-zA-ZÃ¡Ã Ã¢Ã£Ã§Ã©ÃªÃ­Ã³Ã´ÃµÃºÃ¼ÃÃ€Ã‚ÃƒÃ‡Ã‰ÃŠÃÃ“Ã”Ã•Ãš]{3,}')
stemmer = SnowballStemmer('portuguese')
cache = {}


def page_info(dump, stemming=False):
    global tokenizer, stemmer
    c = 1
    di_old = []
    di = []
    for entry in dump.parse():
        if entry.ns != '0':
            continue
        if c != entry.id:
            if c != 1:
                di_old = di[:]
            di = []
            print('new page', entry.id)
            di.append(entry)
        else:
            di.append(entry)
            continue
        c = entry.id
        firstRev = True
        history = {}
        detector = reverts.Detector(radius=3)
        for revision in di_old:
            stems = set()
            gen = tokenizer.tokenize(revision.text)
            if not stemming:
                gen = re.split(r'\s', revision.text)
            for w in gen:
                if stemming:
                    if len(w) < 3:
                        continue
                    elif len(w) == 3:
                        stems.add(w.lower())
                        continue
                    else:
                        if w not in cache:
                            cache[w] = stemmer.stem(w)
                        stems.add(cache[w].lower())
                else:
                    stems.add(w)
            if firstRev:
                prevIntersection = stems
                firstRev = False
            added = stems - prevIntersection
            prevIntersection = stems
            history[revision.revisionid] = Edit(
                revision.revisionid, added, False)
            rev = detector.process(revision.text,
                                   {'rev_id': revision.revisionid})
            if rev:
                for reverted in rev.reverteds:
                    history[reverted['rev_id']].reverted = True

        yield history


def run(dumps):
    print(dumps[0])
    dump = xmlreader.XmlDump(dumps[0], True)
    bot = Bot()
    for case in page_info(dump):
        bot.parse_edits(case.values())
        #print(case)
        #return
    bot.parse_bad_edits(20)

if __name__ == "__main__":
    dumps = sys.argv[1:]
    run(dumps)