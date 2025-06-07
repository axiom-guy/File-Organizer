#!/usr/bin/env python
# coding: utf-8

# In[1]:


import re
import os
import base64
import time
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from alive_progress import alive_bar


# In[2]:


def image_to_readable(path):
    with open(path, "rb") as f:
        encoded_image = base64.b64encode(f.read()).decode("utf-8")
        data_url = f"data:image/jpeg;base64,{encoded_image}"
    return data_url


# In[3]:


def generate_name_image(path,bar,client,model_image,model_text):
    #summarizing
    prompt = f"""Provide a concise summary for this image, try to keep focus on main points and other important details.
    Summary:""" 
    completion_summarize = client.chat.completions.create(
        model=model_image,
        messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt,
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_to_readable(path)
                    },
                }
            ],
        }
    ]
    )
    summary=completion_summarize.choices[0].message.content.strip()
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
    completion_filename=client.chat.completions.create(
        model=model_text,
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
        model=model_text,
        messages=[
            {
                "role": "user",
                "content": f"{folder_prompt}"
            }
        ],
    )
    foldername=completion_foldername.choices[0].message.content.strip()
    foldername=re.sub(r'^Category:\s*','',foldername,flags=re.IGNORECASE).strip()
    bar()

    #TODO- Fix the commented. 
    
    # stop_words = set(stopwords.words('english'))
    # lemmatizer = WordNetLemmatizer()
    # filename=clean_text(filename,3)
    if not filename:
        filename='Untitled'
    # foldername=clean_text(foldername,3)
    if not foldername:
        foldername="Untitled"
    return (filename,foldername)


# In[5]:


def process_file_image_api(path_text,client,model_image,model_text):
    path=path_text
    start=time.time()
    with alive_bar(3,title=f"Processing {os.path.basename(path)}") as bar:
        filename,foldername=generate_name_image(path,bar,client,model_image,model_text)
    end=time.time()

    print(f"File:{os.path.basename(path)}. Processing done in {end-start:.2f}")
    
    return {"path":path,"file_name":filename,"folder_name":foldername}

def process_files_image_api(path_text_files,client,model_image,model_text):
    result=[]
    for path_text in path_text_files:
        result.append(process_file_image_api(path_text,client,model_image,model_text))
    return result


# In[37]:


# from huggingface_hub import InferenceClient
# image_path = "/Users/admin/Desktop/IMG_20250401_183837595.jpg"

# with open(image_path, "rb") as f:
#     encoded_image = base64.b64encode(f.read()).decode("utf-8")

# # Step 2: Create the data URI
# data_url = f"data:image/jpeg;base64,{encoded_image}"  # Change MIME type if needed

# # Step 3: Initialize the client
# client = InferenceClient(
#     provider="nebius",
#     api_key="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",
# )
# prompt=f"""Provide a concise summary for this image, try to keep focus on main points and other important details.
#     Summary:"""

# description=completion.choices[0].message.content.strip()


# filename_prompt = f"""Based on the description below, generate a specific and descriptive filename for the image.
# Limit the filename to a maximum of 3 words, try fewer words if possible. Use nouns and avoid starting with verbs like 'depicts', 'shows', 'presents', etc.
# Do not include any data type words like 'image', 'jpg', 'png', etc. Use only letters and connect words with underscores.

# Description: {description}

# Example:
# Description: A group of penguins standing on ice near the ocean.
# Filename: penguins_on_ice

# Provide **only** the filename, with no extra explanation or punctuation.

# Filename:"""
# foldername_prompt = f"""Based on the description below, generate a general category or theme that best represents the main subject of this image.Try to  generalise that theme as much as possible
# This will be used as the folder name. Limit the category to a maximum of 2 words, if possible use fewer words. Use nouns and avoid verbs.
# Do not include specific details, words from the filename, or any generic terms like 'untitled' or 'unknown'.

# Description: {description}

# Examples:
# 1. Description: A photo of a sunset over the mountains.
#    Category: landscapes

# 2. Description: An image of a smartphone displaying a storage app with various icons and information.
#    Category: technology

# 3. Description: A close-up of a blooming red rose with dew drops.
#    Category: nature

# Now generate the category.

# Output only the category, without any additional text.

# Category:"""
# # Step 5: Make the API call
# completion = client.chat.completions.create(
#     model="google/gemma-3-27b-it",
#     messages=[
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "text",
#                     "text": prompt,
#                 },
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": data_url
#                     },
#                 }
#             ],
#         }
#     ]
# )

# completion_filename = client.chat.completions.create(
#     model="google/gemma-3-27b-it",
#     messages=[
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "text",
#                     "text": filename_prompt,
#                 },
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": data_url
#                     },
#                 }
#             ],
#         }
#     ]
# )
# completion_foldername=client.chat.completions.create(
#     model="google/gemma-3-27b-it",
#     messages=[
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "text",
#                     "text": foldername_prompt,
#                 },
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": data_url
#                     },
#                 }
#             ],
#         }
#     ]
# )
# filename=completion_filename.choices[0].message.content.strip()
# foldername=completion_foldername.choices[0].message.content.strip()
# print(description)
# print(filename)
# print(foldername)

