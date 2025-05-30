#!/usr/bin/env python
# coding: utf-8

# In[32]:


import re
import os
import time
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk.stem import WordNetLemmatizer
from alive_progress import alive_bar


# In[33]:


def clean_text(text,max_words):
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\d+', '', text)
    text = text.strip()
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


# In[34]:


def generate_name(path,text,bar,client,model):
    # summarizing
    prompt = f"""For the given text, give me 100 words concise summary, focusing on key points.
    Text: {text}
    Summary:""" 
    completion_summarize=client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": f"{prompt}"
            }
        ],
    )
    summary=completion_summarize.choices[0].message.content.strip()
    bar()

    # filename
    file_prompt=f"""Using the summary below, create a clear and descriptive filename that reflects the core subject of the document.
    - The filename should be no more than 3 words long.
    - Use only nouns or noun phrases—do not begin with verbs like 'shows', 'explains', or 'describes'.
    - Avoid generic terms such as 'document', 'pdf', or 'text'.
    - Use only lowercase letters and separate words with underscores.
    Summary: {summary}
    Examples:
    1. Summary: A detailed study on medieval architecture in Western Europe.
    Filename: medieval_architecture_europe
    2. Summary: A report analyzing global water scarcity trends.
    Filename: global_water_scarcity
    Now generate the filename.
    Only return the filename—no explanations or extra text.
    Filename:"""

    completion_filename=client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": f"{file_prompt}"
            }
        ],
    )
    filename=completion_filename.choices[0].message.content.strip()
    filename = re.sub(r'^Filename:\s*', '', filename, flags=re.IGNORECASE).strip()
    bar()

    #foldername
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

    completion_foldername=client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": f"{file_prompt}"
            }
        ],
    )
    foldername=completion_foldername.choices[0].message.content.strip()
    foldername=re.sub(r'^Category:\s*','',foldername,flags=re.IGNORECASE).strip()
    bar()

    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    filename=clean_text(filename,3)
    if not filename:
        filename='Untitled'
    foldername=clean_text(foldername,3)
    if not foldername:
        foldername="Untitled"
    return (filename,foldername)


# In[35]:


def process_file(path_text,client,model):
    path,text=path_text
    start=time.time()
    with alive_bar(3,title=f"Processing {os.path.basename(path)}") as bar:
        filename,foldername=generate_name(text,path,bar,client,model)
    end=time.time()

    print(f"File:{os.path.basename(path)}. Processing done in {end-start:.2f}")
    
    return {"path":path,"file_name":filename,"folder_name":foldername}


# In[36]:


def process_files(path_text_files,client,model):
    result=[]
    for path_text in path_text_files:
        result.append(process_file(path_text,client,model))
    return result

