#!/usr/bin/env python
# coding: utf-8

import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


def clean_text(text,max_words):
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\d+', '', text)
    text = text.strip()
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    words = word_tokenize(text)
    words = [word.lower() for word in words if word.isalpha()]
    words = [lemmatizer.lemmatize(word) for word in words]
    filtered_words = []
    seen = set()
    for word in words:
        if word not in all_unwanted_words and word not in seen:
            filtered_words.append(word)
            seen.add(word)
    filtered_words = filtered_words[:max_words]
    return '_'.join(filtered_words)

