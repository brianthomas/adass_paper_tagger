# ADASS Paper Subject Tagger

## About
A quick and dirty subject tagger for ADASS papers using the ADASS dictionary

## Installation

This software requires Python 3 (built with 3.7). You should install a virtual environment 
such as 'virtualenv' and install the requirements.

NOTE: IF you have gcc8 or newer, then the cld2-cffi dependency will not install and you should 
set your CFLAGS environment variable to contain '-Wno-narrowing' 
(see issue https://github.com/GregBowyer/cld2-cffi/issues/21 for more details) 

bash```
> virtualenv -p python3 ./venv
> source venv/bin/activate
> set PYTHONPATH=`pwd`

```

## Usage

Note: you need to set PYTHONPATH to the top level directory (see above in Installation).

```bash

usage: subject_tagger.py [-h] [-d] [-t TEXT]

ADASS Conference Paper Subject Tagger

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug
  -t TEXT, --text TEXT  Text to find subject tags for, defaults to standard
                        input

```

I use standard input and detex to feed papers, for example:

```bash
> detex paper.tex | python bin/subject_tagger.py
```
