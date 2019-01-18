''' Find possible tags from text content with ADASS subject tags
    Input context is assumed to have had "detex" run on them already to remove
    TeX/LaTeX control characters/formatting.
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
    LOG.debug(f'''BAG of Terms (top, cleaned): %s''', sorted_cleaned_bot[:15])

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

    # make a set of ngrams
    ngram_keys_present = ( term for term, cnt in document_terms['ngrams'] )
    
    # go through list of ngrams. We generally want to see MOST
    # of the terms in the keyword present before suggestion
    for doc_ngram in document_terms['ngrams']:
        # do we have something which might match?
        # pull back a possible list of ADASS subject keywords
        # for 'signifant' ngrams (e.g. more than 1 occurance perhaps?)
        if doc_ngram[1] < 2:
            continue

        if doc_ngram[0] in ADASS_Subjects.keywords():
            for adass_keyword in ADASS_Subjects.keywords()[doc_ngram[0]]:
                #check a particular keyword
                # answer the question of whether all of the components
                # are present or not
                for ngram_comp in adass_keyword.split(":"):
                    if ngram_comp not in ngram_keys_present:
                        continue

                # IF we get here in the loop then it looks like we
                # have matched all of the terms
                if adass_keyword not in possible_matches:
                    possible_matches[adass_keyword] = 0

                # lets score by number of times ngram is found in text
                possible_matches[adass_keyword] += 1

    # based on ranking, print back out possible matches
    for tup in possible_matches.items():
        # rule of thumb is if we have more occurances as number of ':'
        # in the term then it *might* be a match
        if tup[1] > tup[0].count(":"):
            print (tup)

    print (f'''Suggested Terms :\n''', document_terms['keyterms'])

    # FIN
