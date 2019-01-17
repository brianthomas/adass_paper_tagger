''' Find possible tags from text content with ADASS subject tags
    Input context is assumed to have had "detex" run on them already to remove
    TeX/LaTeX control characters/formatting.
'''
import logging

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

    # ngrams = list(textacy.extract.ngrams(doc, 4, filter_stops=True, filter_punct=True, filter_nums=False))
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

    terms = find_terms(opts.text)
    #LOG.info(terms['keyterms'])
    #LOG.info(terms['ngrams'])

    # TBD do something with these terms
