#!/usr/bin/env python
# coding: utf-8

import os
import time
import re
import nltk
from text_processing_api import process_files_text_api
from text_processing_local import process_files_text_local
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import InferenceClient
from read_data import read_docx

model="meta-llama/Llama-3.1-8B-Instruct"

start=time.time()
tokenizer=AutoTokenizer.from_pretrained(model)
model=AutoModelForCausalLM.from_pretrained(model,device_map='auto')
end=time.time()
print(f"Time Taken to load model:{end-start:.2f}s")

client = InferenceClient(
    provider="hf-inference",
    api_key="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",
)

path="/Users/admin/Downloads/12222_777.docx"
text=read_docx(path)
path_text=[(path,text)]

# locally
process_files_text_local(path_text,tokenizer,model)

# api
process_files_text_api(path_text,client,model)

