# ADASS Paper Subject Tagger

## About
A quick and dirty subject tagger for ADASS papers using the ADASS dictionary. It will attempt
to match terms from the ADASS dictionary with those extracted from an ADASS proceedings paper.
It provides back output with 2 groupings of ADASS subject terms those which are 'weakly' suggested
and 'strongly' suggested terms. It makes this determination purely on the number of occurances 
of the terms within the document.

It also has the ability to suggest terms which should be added to the ADASS dictionary.

## Installation

This project has submodules, so you should be sure to use the '--recurse-submodules' flag
when cloning, e.x.

```bash
> git clone --recurse-submodules https://github.com/brianthomas/adass_subject_recommender.git  
``` 
This software requires Python 3 (built with 3.7). You should install a virtual environment 
such as 'virtualenv' and install the requirements (see below).

NOTE: IF you have gcc8 or newer, then the cld2-cffi dependency will not install and you should 
set your CFLAGS environment variable to contain '-Wno-narrowing' 
(see issue https://github.com/GregBowyer/cld2-cffi/issues/21 for more details) 

```bash
# create virtual environment
> virtualenv -p python3 ./venv

# activate virtual python environment
# (you may need different activate depending on your shell, the one below is for /bin/sh)
> source venv/bin/activate

# Optional need for those with gcc8 or higher
# (shell dependent, below command for bash)
set CFLAGS='-Wno-narrowing'

# install dependencies
> pip install -r requirements.txt

# install English language model 
> python -m spacy download en 

# IF you forgot to use '--recurse-submodules' flag when you cloned 
# then now lets initialize and checkout submodule contents
git submodule init
git submodule update

```

## Usage

Note: you need to set PYTHONPATH to the top level directory (see above in Installation).

Optional arguments include:

```bash
  -h, --help            show this help message and exit
  -d, --debug           Apply debuging output if used
  -j, --json_output     Use json output if used
  -t TEXT, --text TEXT  Text to find subject tags for, defaults to standard
                        input
  -m MAX_SUGGESTED_TERMS, --max_suggested_terms MAX_SUGGESTED_TERMS
                        Maximum number of suggested terms. Default is 15
```

I use standard input and detex to feed papers, for example:

```bash
> detex ../ADASSProceedings2018/papers/P1-6/P1-6.tex | python bin/find_subjects.py -j -m 5
{
    "adass_terms": [],
    "adass_weak_terms": [
        "classification:spectral",
        "data:analysis:spectral",
        "observatories",
        "classification"
    ],
    "suggested_terms": [
        [
            "center",
            0.03551498740312692
        ],
        [
            "spectra",
            0.03437843324160236
        ],
        [
            "spectral",
            0.031079214880180533
        ],
        [
            "type",
            0.028726251742502026
        ],
        [
            "lamost",
            0.028096893688419902
        ]
    ]
}

```

