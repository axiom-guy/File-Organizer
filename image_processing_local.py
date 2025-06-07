#!/usr/bin/env python
# coding: utf-8

# In[1]:


import re
import os
from PIL import Image
import time
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from alive_progress import alive_bar


# In[2]:


def image_to_readable(path):
    image=Image.open(path).convert('RGB')
    return image


# In[3]:


def generate_name_image_local(path,token_image,token_text,model_image,model_text):
    prompt = f"""For the given image, describe the image, focusing on key points.
    Image:f'{image_to_readable(path)}'
    Summary:""" 
    inputs=token_image(prompt,return_tensors='pt').to(model_image.device)
    outputs=model_image.generate(
        **inputs,
        max_new_tokens=150,
        temperature=0.7,
        top_p=0.85
    )
    summary=token_image.decode(outputs[0],skip_special_tokens=True).split("Summary:")[-1].strip()
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
    inputs=token_text(file_prompt,return_tensors='pt').to(model_text.device)
    outputs=model_text.generate(
        **inputs,
        max_new_tokens=3,
    )
    filename=token_text.decode(outputs[0],skip_special_tokens=True).split("Filename:")[-1].strip()
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
    inputs=token_text(folder_prompt,return_tensors='pt').to(model_text.device)
    outputs=model_text.generate(
        **inputs,
        max_new_tokens=2,
        temperature=0.7,
        top_p=0.85
    )
    foldername=token_text.decode(outputs[0],skip_special_tokens=True).split("Category")[-1].strip()
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


# In[4]:


def process_file_image_local(path,token_image,token_text,model_image,model_text):
    path=path
    start=time.time()
    with alive_bar(3,title=f"Processing {os.path.basename(path)}") as bar:
        filename,foldername=generate_name_image_local(path,bar,token_image,token_text,model_image,model_text)
    end=time.time()

    print(f"File:{os.path.basename(path)}. Processing done in {end-start:.2f}")
    
    return {"path":path,"file_name":filename,"folder_name":foldername}

def process_files_image_local(path_files,token_image,token_text,model_image,model_text):
    result=[]
    for path in path_files:
        result.append(process_file_image_local(path,token_image,token_text,model_image,model_text))
    return result


# In[ ]:




