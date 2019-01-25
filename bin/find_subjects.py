#!/usr/bin/env python

''' Find possible subject erms from text content in an ADASS Proceedings paper.
    The software will consider ADASS subject dicionary terms as well as suggest
    new terms which are missing.

    Input context is assumed to have had "detex" run on them already to remove
    TeX/LaTeX control characters/formatting.

    This program requires Python3
'''
import logging
from recommender.data import *

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger('subject_rec')
LOG.setLevel(logging.INFO)

MAX_BOT_TERMS = 30
MAX_SUGGESTED_KEYTERMS = 15

def find_terms (content:str, maxterms=MAX_SUGGESTED_KEYTERMS, ngrams_to_extract=(1,2,3))->list:
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

    # extract keyterms to make suggestions for new ADASS subject terms
    keyterms = textacy.keyterms.textrank(doc, normalize='lemma', n_keyterms=maxterms)
    LOG.debug(f'''KEYTERMS: %s''', keyterms)

    # We'll use the Bag of terms, ngrams by frequency, to find relevant matches with
    # existing terms in the ADASS dictionary
    bot = doc.to_bag_of_terms(ngrams=ngrams_to_extract, lemmatize=True, named_entities=True, weighting='count', as_strings=True)

    # For some reason we see stopwords in the BoT, so make another pass to clean out stopwords
    # and the empty string then print top 15 number of terms by occurance
    cleaned_bot = [(term, cnt) for term, cnt in bot.items() if term not in STOP_WORDS and term != '']
    sorted_cleaned_bot = sorted(cleaned_bot, key=lambda x: x[1], reverse=True)
    LOG.debug(f'''BAG of Terms (top, cleaned): %s''', sorted_cleaned_bot[:MAX_BOT_TERMS])

    return {'ngrams' : sorted_cleaned_bot, 'keyterms' : keyterms}

def find_subject_terms(text_to_search:str, max_terms:int) -> dict:

    # pull and then compare document terms
    # to what we have in the dictionary
    document_terms = find_terms(text_to_search, max_terms)

    possible_matches = {}
    strong_matches = {}

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

                # Split on the ':' in the keyword
                # to get ADASS keyword term/components
                adass_keyword_terms = adass_keyword.lower().split(":")
                first_term = adass_keyword_terms.pop()

                # check a particular ADASS Subject keyword in the group
                # and answer the question of whether all of the sub-components
                # of that keyword are present or not.

                is_a_match = True
                is_a_strong_match = False
                # check against lower terms
                for kw_comp in adass_keyword_terms:
                    if kw_comp not in doc_ngrams:
                        is_a_match = False

                if is_a_match and first_term in doc_ngrams:
                    is_a_strong_match = True

                if is_a_match:
                    # IF we get here in the loop then it looks like we
                    # have matched all of the terms
                    if adass_keyword not in possible_matches:
                        possible_matches[adass_keyword] = 0

                    # lets score by number of times ngram is found in text
                    possible_matches[adass_keyword] += 1

                if is_a_strong_match:
                    if adass_keyword not in strong_matches:
                        strong_matches[adass_keyword] = 0

                    strong_matches[adass_keyword] += 1

    # based on ranking, print back out possible matches
    strong_terms = []
    weak_terms = []
    for tup in possible_matches.items():
        # rule of thumb is if we have 3 or more occurances
        # in the term then its probably strongly suggested
        if tup[1] > 3:
            weak_terms.append(tup[0])

    for tup in strong_matches.items():
        if tup[1] > 3:
            strong_terms.append(tup[0])
        else:
            weak_terms.append(tup[0])

    return { 'adass_terms' : strong_terms, 'adass_weak_terms' : weak_terms, 'suggested_terms' : document_terms['keyterms']}

if __name__ == '__main__':
    import argparse
    import sys
    import json

    ap = argparse.ArgumentParser(description='ADASS Conference Paper Subject Tagger')
    ap.add_argument('-d', '--debug', default = False, action = 'store_true', help="Apply debuging output if used")
    ap.add_argument('-j', '--json_output', default = False, action = 'store_true', help="Use json output if used")
    ap.add_argument('-t', '--text', type=str, help= 'Text to find subject tags for, defaults to standard input', default=sys.stdin)
    ap.add_argument('-m', '--max_suggested_terms', type=int, default=MAX_SUGGESTED_KEYTERMS, help= 'Maximum number of suggested terms. Default is '+str(MAX_SUGGESTED_KEYTERMS))

    # parse argv
    opts = ap.parse_args()

    if opts.debug:
        logging.basicConfig(level=logging.DEBUG)
        LOG.setLevel(logging.DEBUG)

    subjects = find_subject_terms (opts.text, opts.max_suggested_terms)

    if (opts.json_output):
        print(json.dumps(subjects, indent=4, sort_keys=True))
    else:
        print (f'''Suggested ADASS Subjects:\n''', subjects['adass_terms'])
        print (f'''Weakly Suggested ADASS Subjects:\n''', subjects['adass_weak_terms'])
        print (f'''Suggested KeyTerms (to add to subjects) :\n''', subjects['suggested_terms'])

    # FIN
