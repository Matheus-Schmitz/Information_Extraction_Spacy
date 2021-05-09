#!/usr/bin/env python
# coding: utf-8

'''
Matheus Schmitz
DSCI 558 - Building Knowledge Graphs
Homework 2
'''

# Inputs 
# python Matheus_Schmitz_hw02_task_2_2.py Matheus_Schmitz_hw02_bios.csv hw2_task2_2.jl 1
import sys
input_csv = sys.argv[1]
output_jl = sys.argv[2]
extractor_number = int(sys.argv[3])

# Get the right spacy version for my code
import os
print('Installing spaCy 2.2.4')
os.system('pip install -q -q -q --force-reinstall spacy==2.2.4')

import re
import spacy
import en_core_web_sm
from spacy.matcher import Matcher
import csv
import json
from tqdm import tqdm


nlp = en_core_web_sm.load()


birthplace_lexical = [
    {'LOWER': 'born'},
    {'OP': '*'},
    {'LOWER': 'in'},
    {'TEXT': {'REGEX': '\s*'}, 'OP': '*'},
    {'IS_PUNCT': True, 'OP': '*'},
    {'TEXT': {'REGEX': '\s*'}, 'OP': '+'},
    {'IS_PUNCT': True, 'OP': '*'},
    ]

education_lexical = [
    {'TEXT': {'REGEX': '^(attend|attended|went|studied|University|College|trained|graduated)$'}},
    {'OP': '+'},
    ]

parents_lexical = [
    {'LOWER': {'REGEX': '^(born|son|daughter|parents)$'}},
    {'OP': '*'},
    {'LOWER': {'REGEX': '^(to|of|are)$'}},
    {'TEXT': {'REGEX': '\s*'}, 'OP': '*'},
    {'IS_PUNCT': True, 'OP': '*'},
    {'TEXT': {'REGEX': '\s*'}, 'OP': '+'},
    {'IS_PUNCT': True, 'OP': '*'},
    {'LOWER': 'and','OP': '?'},
    {'TEXT': {'REGEX': '\s*'}, 'OP': '*'},
    {'IS_PUNCT': True, 'OP': '*'},
    {'TEXT': {'REGEX': '\s*'}, 'OP': '+'},
    {'IS_PUNCT': True, 'OP': '*'},
    ]

awards_lexical = [
    {'LOWER': {'REGEX': '^(winner|recipient|won|awarded|award-winning|nominated|nominee|nomination)$'}},
    {'LOWER': {'REGEX': '^(of|the|on|for|as)$'}},
    {'OP': '+'}
    ]

performances_lexical = [
    {'LOWER': {'REGEX': '^(star|starred|known|appeared|appearing|appearances|debute|album|recorded|play|played|role)$'}},
    {'LOWER': {'REGEX': '^(in|for|on|for|as)$'}},
    {'OP': '+'},
    ]

colleagues_lexical = [
    {'IS_TITLE': '+', 'OP': '*'},
    {'LOWER': {'REGEX': '^(starring|collaborating|working|worked|partnering|sharing.*screen.*space|appears.*opposite|opposite)$'}},
    {'LOWER': {'REGEX': '^(with|alongside|to)$'}}, {'OP': '*'},
    {'OP': '*'},
    ]

birthplace_syntactic = [
    {'POS': 'VERB', 'ORTH': 'born'},
    {'OP': '*'},
    {'LOWER': 'in', 'POS': 'ADP'},
    {'ENT_TYPE': 'GPE', 'OP': '+'},
    {'IS_PUNCT': True, 'OP': '*'},
    {'ENT_TYPE': 'GPE', 'OP': '*'},
    {'IS_PUNCT': True, 'OP': '*'},
    ]

education_syntactic = [
    {'TEXT': {'REGEX': '^(attend|attended|went|studied|University|College|trained|graduated)$'}},
    {'ENT_TYPE': 'ORG', 'OP': '+'},
    ]

parents_syntactic = [
    {'LOWER': {'REGEX': '^(born|son|daughter|parents)$'}},
    {'OP': '*'},
    {'LOWER': {'REGEX': '^(to|of|are)$'}},
    {'TEXT': {'REGEX': '\s*'}, 'OP': '*'},
    {'IS_PUNCT': True, 'OP': '*'},
    {'ENT_TYPE': 'PERSON', 'TEXT': {'REGEX': '\s*'}, 'OP': '+'},
    {'IS_PUNCT': True, 'OP': '*'},
    {'LOWER': 'and','OP': '?'},
    {'TEXT': {'REGEX': '\s*'}, 'OP': '*'},
    {'IS_PUNCT': True, 'OP': '*'},
    {'ENT_TYPE': 'PERSON', 'TEXT': {'REGEX': '\s*'}, 'OP': '+'},
    {'IS_PUNCT': True, 'OP': '*'},
    ]

awards_syntactic = [
    {'OP': '*'},
    {'POS': 'NOUN', 'IS_TITLE': '+', 'OP': '*'},
    {'LOWER': {'REGEX': '^(winner|recipient|won|awarded|award-winning|nominated|nominee|nomination)$'}},
    {'POS': 'ADP', 'TEXT': {'REGEX': '^(of|the|for)$'}, 'OP': '*'},
    {'POS': 'NOUN', 'IS_TITLE': '+', 'OP': '*'},
    {'OP': '*'},
    ]

performances_syntactic = [
    {'LOWER': {'REGEX': '^(star|starred|known|appeared|appearing|appearances|debute|album|recorded|play|played|role)$'}},
    {'POS': 'ADP', 'TEXT': {'REGEX': '^(in|of|the|for|as)$'}, 'OP': '+'},
    {'OP': '+'},
    ]

colleagues_syntactic = [
    {'OP': '*'},
    {'LOWER': {'REGEX': '^(starring|collaborating|working|worked|partnering|sharing.*screen.*space|appears.*opposite|opposite|joined)$'}},
    {'LOWER': {'REGEX': '^(with|alongside|to)$'}}, {'OP': '*'},
    {'ENT_TYPE': 'PERSON'},
    {'OP': '*'},
    ]


# Function to match and return results
def spacy_matcher(doc, pattern):
    output = []
    
    # Instantiate the spaCy Matcher
    matcher = Matcher(nlp.vocab) 
    matcher.add("matching", None, pattern)
    
    # Iterate throgh sentences
    for sent in doc.sents:

        # Match sentences to the pattern
        matches = matcher(nlp(sent.text)) 
        
        # If any matches were found, extract them and append to the list of matches for that pair of (document x pattern)
        if len(matches)>0:
            span = sent[matches[-1][1]:matches[-1][2]] 
            output.append(span.text)

    return output


def birthplace_filter(list_with_text):
    if len(list_with_text) > 0:
        # Convert to a single single
        joined = " ".join(list_with_text)        
        list_with_text = joined.rsplit("as")
        return [[' '.join(re.findall(r"\b(?:[A-Z][^\s]*\s?)+", list_with_text[i])) 
                 for i in range(len(list_with_text))][0]
                .strip(r'^January$|^February$|^March$|^April$|^May$|^June$|^July$|^August$|^September$|^October$|^November$|^December$|^USA$')][0]
    else:
        return ""       

def education_filter(list_with_text):
    if len(list_with_text) > 0:
        # Convert to a single single
        joined = ",".join(list_with_text)
        # Split the text considering punctions and other demarkings
        text_splits = re.split(",| and ", joined)
        # Keep only Titlecasewords and their punctuations
        titlecases = [' '.join(re.findall(r"\b(?:[A-Z][^\s]*\s?)+", [text_splits[i] for i in range(len(text_splits))][x])) for x in range(len(text_splits))]
        # Clear additional frequent nuisances
        output1 = [re.sub(r'^She$|^He$|^January$|^February$|^March$|^April$|^May$|^June$|^July$|^August$|^September$|^October$|^November$|^December$', '', titlecases[i]) for i in range(len(titlecases))]
        # Remove any empty strings generated
        output2 = [x for x in output1 if x.strip()]
        return output2
    else:
        return list_with_text        

def parents_filter(list_with_text):
    if len(list_with_text) > 0:
        # Convert to a single single
        joined = ",".join(list_with_text)
        # Split the text considering punctions and other demarkings
        text_splits = re.split(",| and ", joined)
        # Keep only Titlecasewords and their punctuations
        titlecases = [' '.join(re.findall(r"\b(?:[A-Z][^\s]*\s?)+", [text_splits[i] for i in range(len(text_splits))][x])) for x in range(len(text_splits))]
        # Clear additional frequent nuisances
        output1 = [re.sub(r'^She$|^He$|^January$|^February$|^March$|^April$|^May$|^June$|^July$|^August$|^September$|^October$|^November$|^December$', '', titlecases[i]) for i in range(len(titlecases))]
        # Remove any empty strings generated
        output2 = [x for x in output1 if x.strip()]
        return output2
    else:
        return list_with_text        

def awards_filter(list_with_text):
    if len(list_with_text) > 0:
        # Convert to a single single
        joined = ",".join(list_with_text)
        # Split the text considering punctions and other demarkings
        text_splits = re.split(",| and | for ", joined)
        # Keep only Titlecasewords and their punctuations
        titlecases = [' '.join(re.findall(r"\b(?:[A-Z][^\s]*\s?)+", [text_splits[i] for i in range(len(text_splits))][x])) for x in range(len(text_splits))]
        # Remove any empty strings generated
        output1 = [x for x in titlecases if x.strip()]
        return output1
    else:
        return list_with_text        

def performances_filter(list_with_text):
    if len(list_with_text) > 0:
        # Convert to a single single
        joined = ",".join(list_with_text)
        # Remove "known for"
        clean_1 = re.sub("known for", "", joined)
        # Split the text considering punctions and other demarkings
        text_splits = re.split(",| and ", clean_1)
        # Keep only Titlecasewords and their punctuations
        titlecases = [' '.join(re.findall(r"\b(?:[A-Z][^\s]*\s?)+", [text_splits[i] for i in range(len(text_splits))][x])) for x in range(len(text_splits))]
        # Remove any empty strings generated
        output1 = [x for x in titlecases if x.strip()]
        return output1
    else:
        return list_with_text        

def colleagues_filter(list_with_text):
    if len(list_with_text) > 0:
        # Remove double quotations " around some movie names
        unquoted = [x.strip("'") for x in list_with_text]
        # Split the text considering punctions and other demarkings
        text_splits = re.split(",| and | in", unquoted[0])
        # Keep only Titlecasewords and their punctuations
        titlecases = [' '.join(re.findall(r"\b(?:[A-Z][^\s]*\s?)+", [text_splits[i] for i in range(len(text_splits))][x])) for x in range(len(text_splits))]
        # Remove any empty strings generated
        output1 = [x for x in titlecases if x.strip()]
        return output1
    else:
        return list_with_text        


if __name__ == "__main__":

	# Lexical
    if extractor_number == 0:
        print('Applying lexical extractor.')
        # Open the jsonlines to be written
        with open(output_jl, 'w') as hw2_lexical:
            # Iterate through the csv with bios
            for url, bio in tqdm(csv.reader(open(input_csv, encoding='utf-8')), total=sum(1 for row in csv.reader(open(input_csv, encoding='utf-8')))):

                # Create dict to store the outputs of each row
                output = {}

                # Populate the outputs with spaCy's Matcher
                output["url"] = url
                output["birthplace"] = spacy_matcher(nlp(bio), birthplace_lexical)
                output["education"] = spacy_matcher(nlp(bio), education_lexical)
                output["parents"] = spacy_matcher(nlp(bio), parents_lexical)
                output["awards"] = spacy_matcher(nlp(bio), awards_lexical)        
                output["performances"] = spacy_matcher(nlp(bio), performances_lexical)
                output["colleagues"] = spacy_matcher(nlp(bio), colleagues_lexical)

                # Keep only nouns for certain outputs
                output["birthplace"] = birthplace_filter(output["birthplace"])
                output["education"] = education_filter(output["education"])
                output["parents"] = parents_filter(output["parents"])
                output["awards"] = awards_filter(output["awards"])
                output["performances"] = performances_filter(output["performances"])
                output["colleagues"] = colleagues_filter(output["colleagues"])

                # Write a csv row as a line in jsonlines 
                json.dump(output, hw2_lexical)
                hw2_lexical.write("\n")

            # Close the jsonlines file
            hw2_lexical.close()

	# Syntactic       
    elif extractor_number == 1:
        print('Applying syntactic extractor.')
        # Open the jsonlines to be written
        with open(output_jl, 'w') as hw2_syntactic:
            # Iterate through the csv with bios   
            for url, bio in tqdm(csv.reader(open(input_csv, encoding='utf-8')), total=sum(1 for row in csv.reader(open(input_csv, encoding='utf-8')))):

                # Create dict to store the outputs of each row
                output = {}

                # Populate the outputs with spaCy's Matcher
                output["url"] = url
                output["birthplace"] = spacy_matcher(nlp(bio), birthplace_syntactic)
                output["education"] = spacy_matcher(nlp(bio), education_syntactic)
                output["parents"] = spacy_matcher(nlp(bio), parents_syntactic)
                output["awards"] = spacy_matcher(nlp(bio), awards_syntactic)        
                output["performances"] = spacy_matcher(nlp(bio), performances_syntactic)
                output["colleagues"] = spacy_matcher(nlp(bio), colleagues_syntactic)
                                            
                # Keep only nouns for certain outputs
                output["birthplace"] = birthplace_filter(output["birthplace"])
                output["education"] = education_filter(output["education"])
                output["parents"] = parents_filter(output["parents"])
                output["awards"] = awards_filter(output["awards"])
                output["performances"] = performances_filter(output["performances"])
                output["colleagues"] = colleagues_filter(output["colleagues"])
                                            
                # Write a csv row as a line in jsonlines 
                json.dump(output, hw2_syntactic)
                hw2_syntactic.write("\n")

            # Close the jsonlines file
            hw2_syntactic.close()

    # Error    
    else:
        raise ValueError('Input either 0 for lexical patterns or 1 for syntactic patterns.')




