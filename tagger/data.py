

class Utility(object):

    def _find_file(pattern, path):
        import fnmatch
        import os

        result = []
        for root, dirs, files in os.walk(path):
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    result.append(os.path.join(root, name))
        return result

class ADASS_Subjects(object):

    import re

    _KEYWORDS = None
    _ACRONYM_PATTERN = re.compile("(.*)\s+\((\w+)\)\s*")

    def _get_keywords_from_file (keyword_file:str)->list:

        file_to_open = Utility._find_file(keyword_file, '.')
        print (file_to_open)

        # read and put subjects into order.
        # the format of the subjectKeywords.txt file is particularly gnarly,
        # it would seem that nobody in ADASS publishing has ever thought of using an
        # off-the-shelf format like YAML or JSON. *sigh*
        data = []
        with open (file_to_open[0], 'r') as f:
            for item in f.readlines():
                # lets capture the 'level' (level in the subject heirarchy)
                # based on the leading whitespace.
                level = (len(item) - len(item.lstrip())) / 4
                data.append((item.strip(), level))

        # now, using the order of the list and the level of the word, rebuild
        # to get actual keywords
        keywords = {}
        working_parents = []

        # pass 1: build dictionary of terms and potential matching ngrams
        for itup in data:
            content = itup[0]
            level = itup[1]

            # init to single term if level 0 (parent)
            if level == 0:
                working_parents = []
            else:
                if len(working_parents) > level:
                    # pop last item from list
                    working_parents.pop()

            new_keyword_list = working_parents + [content]
            new_keyword = ""
            for item in new_keyword_list:
                new_keyword += item + ":"
            new_keyword = new_keyword[:-1]

            for term in new_keyword_list:
                if term not in keywords:
                    keywords[term] = []
                keywords[term].append(new_keyword)

            # add current term "content" to our working parent list
            working_parents.append(content)

        # pass 2: Fix keywords to remove acronyms from term which might match
        # but then add them back to the dict as aliases
        fixed_keywords = {}
        for keyword in keywords:
            m = ADASS_Subjects._ACRONYM_PATTERN.match(keyword)
            if m:
                # we have an acronym, split off into 2 entries
                for grp in m.groups():
                    fixed_keywords[grp] = keywords[keyword]
            else:
                fixed_keywords[keyword] = keywords[keyword]

        return fixed_keywords

    def keywords(keyword_file:str ='subjectKeywords.txt') -> list:
        if ADASS_Subjects._KEYWORDS == None:
            ADASS_Subjects._KEYWORDS = ADASS_Subjects._get_keywords_from_file(keyword_file)

        return ADASS_Subjects._KEYWORDS
