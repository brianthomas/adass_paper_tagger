#!/usr/bin/env python

''' Find possible tags from text content with ADASS subject tags
    Input context is assumed to have had "detex" run on them already to remove
    TeX/LaTeX control characters/formatting.

    This program requires Python3
'''
import logging
from tagger.data import *

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger('adass_subject_tagger')
LOG.setLevel(logging.INFO)

def find_terms (content:str, ngrams_to_extract=(1,2,3))->list:
    '''
    Find NGRAMS of significance in passed text
    will look for ngrams up to 3 words by default.
    Returns a list of (term, frequency) tuples sorted by frequency
    '''
    import textacy
    import textacy.keyterms
    import io
    from spacy.lang.en.stop_words import STOP_WORDS

    # if we used standard in, read the io.TextIOWrapper class
    # otherwise just accept as is
    if type(content) == io.TextIOWrapper:
        text = content.read()
    else:
        # its asumed to be str
        text = content

    LOG.debug(f'''content has %d chars''', len(text))

    # find tags here
    tags = []

    #lang_en = spacy.util.get_lang_class('en')
    doc = textacy.Doc(text)
    LOG.debug(doc)

    # ngrams = list(textacy.extract.ngrams(doc, 3, filter_stops=True, filter_punct=True, filter_nums=False))
    #LOG.debug(f'''NGRAMS: %s''', ngrams)

    # extract keyterms to make suggestions for new ADASS subject terms
    keyterms = textacy.keyterms.textrank(doc, normalize='lemma', n_keyterms=10)
    LOG.debug(f'''KEYTERMS: %s''', keyterms)

    # We'll use the Bag of terms, ngrams by frequency, to find relevant matches with
    # existing terms in the ADASS dictionary
    bot = doc.to_bag_of_terms(ngrams=ngrams_to_extract, named_entities=True, weighting='count', as_strings=True)

    # For some reason we see stopwords in the BoT, so make another pass to clean out stopwords
    # and the empty string then print top 15 number of terms by occurance
    cleaned_bot = [(term, cnt) for term, cnt in bot.items() if term not in STOP_WORDS and term != '']
    sorted_cleaned_bot = sorted(cleaned_bot, key=lambda x: x[1], reverse=True)
    LOG.debug(f'''BAG of Terms (top, cleaned): %s''', sorted_cleaned_bot[:30])

    return {'ngrams' : sorted_cleaned_bot, 'keyterms' : keyterms}

if __name__ == '__main__':
    import argparse
    import sys

    ap = argparse.ArgumentParser(description='ADASS Conference Paper Subject Tagger')
    ap.add_argument('-d', '--debug', default = False, action = 'store_true')
    ap.add_argument('-t', '--text', type=str, help= 'Text to find subject tags for, defaults to standard input', default=sys.stdin)

    # parse argv
    opts = ap.parse_args()

    if opts.debug:
        logging.basicConfig(level=logging.DEBUG)
        LOG.setLevel(logging.DEBUG)

    # WAY too verbose
    #LOG.debug(ADASS_Subjects.keywords())

    # pull and then compare document terms
    # to what we have in the dictionary
    document_terms = find_terms(opts.text)

    print (f'''Matching ADASS Keywords : ''')
    possible_matches = {}

    # TODO : Tech debt
    # make a set of ngrams
    doc_ngrams = { term.lower() for term, cnt in document_terms['ngrams'] }
    #LOG.debug(doc_ngrams)

    # go through list of ngrams. We generally want to see MOST
    # of the terms in the keyword present before suggestion
    for doc_ngram in document_terms['ngrams']:
        # do we have something which might match?
        # pull back a possible list of ADASS subject keywords
        # for 'significant' ngrams (e.g. more than a few occurances perhaps?)
        if doc_ngram[1] < 2:
            continue

        # now test if we have a match with any ADASS Subject keywords
        if doc_ngram[0] in ADASS_Subjects.keywords():
            LOG.debug(f'''Testing doc_ngram: %s''', str(doc_ngram[0]))

            # we have matched a grouping of keywords
            # but they may not perfectly align (hah!), so lets break apart
            # the ADASS Subject keyword grouping and see if all of the
            # component parts will match, and if so, then we probably have
            # a good choice
            adass_keyword_group = ADASS_Subjects.keywords()[doc_ngram[0]]
            for adass_keyword in adass_keyword_group:
                # check a particular ADASS Subject keyword in the group
                # and answer the question of whether all of the sub-components
                # of that keyword are present or not.
                # Split on the ':' in the keyword
                for kw_comp in adass_keyword.lower().split(":"):
                    if kw_comp not in doc_ngrams:
                        continue

                # IF we get here in the loop then it looks like we
                # have matched all of the terms
                if adass_keyword not in possible_matches:
                    possible_matches[adass_keyword] = 0

                # lets score by number of times ngram is found in text
                possible_matches[adass_keyword] += 1

    # based on ranking, print back out possible matches
    strong_terms = []
    weak_terms = []
    for tup in possible_matches.items():
        # rule of thumb is if we have more occurances as number of ':'
        # in the term then it *might* be a match

        if tup[1] > tup[0].count(":"):
            strong_terms.append(tup[0])
        elif tup[1] > tup[0].count(":")-1:
            weak_terms.append(tup[0])

    print (f'''Suggested ADASS Subjects:\n''', strong_terms)
    print (f'''Weakly Suggested ADASS Subjects:\n''', weak_terms)
    print (f'''Suggested KeyTerms (to add to subjects) :\n''', document_terms['keyterms'])

    # FIN
