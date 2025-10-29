#a few functions which are used by $add_inspo and ../events/sad_ears.py

import requests
import json
import os
import random

################################################
#add encouraging message to the list of options!
#use: 
#   $add_inspo [your encouraging message here]
################################################
        
#load list of encouragement keywords        
def load_encouragement_keywords():
    try:
        with open("keyword_lists/response_encouragement.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print('keyword_lists/response_encouragement.txt file not found; loading default list instead.')
        return ['Keep doing your worst.','Just keep swimming.','Breathe. Your brain lacks something, and it might be oxygen.',
                'Save those tears for your pillow.','Touch grass.','Absorb some sunshine.',
                'sarcasm']

def load_sad_keywords():
    try:
        with open("keyword_lists/sad_keywords.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print('keyword_lists/sad_keywords.txt file not found; loading default list instead.')
        return ['miserable','sad','unhappy','sadgams','angry','upset','depressed','infuriated','grumpy']

def sarcastify_word(word):
    if word=='D:':
        return word
    string=''
    for n in range(len(word)):
        string+=word[n].lower() if n%2==0 else word[n].upper()
    return string