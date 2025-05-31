#!/usr/bin/env python
# coding: utf-8

import re
import os
import time
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from alive_progress import alive_bar
from common_functions import clean_text

def generate_name_text_local(path,text,bar,tokenizer,model):
    prompt = f"""For the given text, give me 100 words concise summary, focusing on key points.
    Summary:""" 
    inputs=tokenizer(prompt,return_tensors='pt').to(model.device)
    outputs=model.generate(
        **inputs,
        max_new_tokens=150,
        temperature=0.7,
        top_p=0.85
    )
    summary=tokenizer.decode(outputs[0],skip_special_tokens=True).split("Summary:")[-1].strip()
    bar()
    
    file_prompt =  f"""Based on the summary below, generate a specific and descriptive filename that captures the essence of the document.
    Limit the filename to a maximum of 3 words. Use nouns and avoid starting with verbs like 'depicts', 'shows', 'presents', etc.
    Do not include any data type words like 'text', 'document', 'pdf', etc. Use only letters and connect words with underscores.

    Summary: {summary}

    Examples:
    1. Summary: A research paper on the fundamentals of string theory.
       Filename: fundamentals_of_string_theory

    2. Summary: An article discussing the effects of climate change on polar bears.
       Filename: climate_change_polar_bears

    Now generate the filename.

    Output only the filename, without any additional text.

    Filename:"""
    inputs=tokenizer(file_prompt,return_tensors='pt').to(model.device)
    outputs=model.generate(
        **inputs,
        max_new_tokens=3,
    )
    filename=tokenizer.decode(outputs[0],skip_special_tokens=True).split("Filename:")[-1].strip()
    bar()
    folder_prompt=f"""Using the summary below, identify a broad category or theme that best represents the main topic of the document.
    - This will be used as a folder name.
    - Limit the category to 1 or 2 words.
    - Use only nouns—do not use verbs or phrases starting with action words.
    - Avoid specific details, words from the filename, or generic terms like 'untitled' or 'unknown'.
    Summary: {summary}
    Examples:
    1. Summary: A historical overview of the French Revolution and its global impact.
       Category: history
    2. Summary: A paper examining artificial intelligence applications in modern healthcare.
       Category: technology
    Now generate the category.
    Return only the category name with no extra text.
    Category:"""
    inputs=tokenizer(folder_prompt,return_tensors='pt').to(model.device)
    outputs=model.generate(
        **inputs,
        max_new_tokens=2,
        temperature=0.7,
        top_p=0.85
    )
    foldername=tokenizer.decode(outputs[0],skip_special_tokens=True).split("Category")[-1].strip()
    bar()
    #Todo- fix the commented
    
    # stop_words = set(stopwords.words('english'))
    # lemmatizer = WordNetLemmatizer()
    # filename=clean_text(filename,3)
    if not filename:
        filename='Untitled'
    # foldername=clean_text(foldername,3)
    if not foldername:
        foldername="Untitled"
    return (filename,foldername)

def process_file_text_local(path_text,tokenizer,model):
    path,text=path_text
    start=time.time()
    with alive_bar(3,title=f"Processing {os.path.basename(path)}") as bar:
        filename,foldername=generate_name_text_local(path,text,bar,tokenizer,model)
    end=time.time()

    print(f"File:{os.path.basename(path)}. Processing done in {end-start:.2f}")
    
    return {"path":path,"file_name":filename,"folder_name":foldername}

def process_files_text_local(path_text_files,tokenizer,model):
    result=[]
    for path_text in path_text_files:
        result.append(process_file_text_local(path_text,tokenizer,model))
    return result