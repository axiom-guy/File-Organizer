# #!/usr/bin/env python
# # coding: utf-8

# import os
# import time
# import re
# import nltk
# import base64
# # from text_processing_api import process_files_text_api
# from text_processing_local import process_files_text
# from transformers import AutoTokenizer, AutoModelForCausalLM
# from huggingface_hub import InferenceClient
# from read_data import read_docx,read_ppt, read_pdf
# # from image_processing_api import process_files_image_api
# from image_processing_local import process_files_image_local
# from tree_builder import tree_builder
# import torch
# from alive_progress import alive_bar
# from read_data import collect_file_path,seperate_files,read_file
# from llama_cpp import Llama
# from llama_cpp.llama_chat_format import MiniCPMv26ChatHandler


# llm_text = Llama.from_pretrained(
# 	repo_id="MaziyarPanahi/Meta-Llama-3-8B-Instruct-GGUF",
# 	filename="Meta-Llama-3-8B-Instruct.Q4_K_M.gguf",
#     n_ctx=4096,
#     n_gpu_layers=10,
#     verbose=False
# )

# chat_handler = MiniCPMv26ChatHandler.from_pretrained(
#     repo_id="openbmb/MiniCPM-V-2_6-gguf",
#     filename="*mmproj*",
#     verbose=False
# )
# # Load the vision-language model with the handler
# llm = Llama.from_pretrained(
#     repo_id="openbmb/MiniCPM-V-2_6-gguf",
#     filename="ggml-model-Q4_1.gguf",
#     chat_handler=chat_handler,
#     n_gpu_layers=10,
#     n_ctx=4096,
#     verbose=False
# )

# path="/Users/admin/Desktop/sample_data"
# x=collect_file_path(path)
# y=seperate_files(x)

# path_text=[]
# for i in y[1]:
#     z=read_file(i)
#     path_text.append((i,z))

# a=[]
# a.append(process_files_image_local(y[0],llm,llm_text))
# a.append(process_files_text(y[1],llm_text))

# print(a)

#!/usr/bin/env python
# coding: utf-8

import os
import sys
import warnings
import base64
import torch
import time
import re
import nltk

# ------------------------
# Silence all unnecessary logs
# ------------------------

# Reduce llama.cpp and Metal logs
os.environ["LLAMA_LOG_LEVEL"] = "ERROR"
os.environ["GGML_METAL_LOG_LEVEL"] = "NONE"

# Suppress Python warnings like PDF CropBox
warnings.filterwarnings("ignore", message="CropBox missing from /Page")

# ------------------------
# Optionally suppress all stderr output globally (comment out if debugging)
# ------------------------
# sys.stderr = open(os.devnull, 'w')


# ------------------------
# Import local modules
# ------------------------
from text_processing_local import process_files_text
from image_processing_local import process_files_image_local
from tree_builder import tree_builder
from read_data import (
    read_docx, read_ppt, read_pdf,
    collect_file_path, seperate_files, read_file
)

from llama_cpp import Llama
from llama_cpp.llama_chat_format import MiniCPMv26ChatHandler
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import InferenceClient
from alive_progress import alive_bar


# ------------------------
# Stderr suppressor (used only during model load)
# ------------------------
def suppress_stderr(func):
    def wrapper(*args, **kwargs):
        original_stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')
        try:
            return func(*args, **kwargs)
        finally:
            sys.stderr.close()
            sys.stderr = original_stderr
    return wrapper


# ------------------------
# Load models with clean logging
# ------------------------
@suppress_stderr
def load_llm_text():
    return Llama.from_pretrained(
        repo_id="MaziyarPanahi/Meta-Llama-3-8B-Instruct-GGUF",
        filename="Meta-Llama-3-8B-Instruct.Q4_K_M.gguf",
        n_ctx=4096,
        n_gpu_layers=10,
        verbose=False
    )


@suppress_stderr
def load_llm_image():
    handler = MiniCPMv26ChatHandler.from_pretrained(
        repo_id="openbmb/MiniCPM-V-2_6-gguf",
        filename="*mmproj*",
        verbose=False
    )
    return Llama.from_pretrained(
        repo_id="openbmb/MiniCPM-V-2_6-gguf",
        filename="ggml-model-Q4_1.gguf",
        chat_handler=handler,
        n_ctx=4096,
        n_gpu_layers=10,
        verbose=False
    )


# ------------------------
# Main pipeline
# ------------------------
def main():
    path=input("Enter the abs path of the directory, you what to organise.").strip()
    while not os.path.exists(path):
        print(f'Path {path} does not exist. Kindly enter a valid path.')
        path=input("Enter the abs path of the directory, you what to organise.").strip()
    print("Input path successfully recognised.")
    print(tree_builder(path))
    output_path=input(f"""Enter the abs output path for the arranged directory.(Default will be {os.path.join(os.path.dirname(path),'organized_dir')})""")
    if not output_path:
        output_path=os.path.join(os.path.dirname(path),'organized_dir')
    # Load models
    print("Loading models.....")
    llm_text = load_llm_text()
    llm_image = load_llm_image()
    print('Loading model complete......')
    # Collect file paths
    print("Accessing files......")
    all_files = collect_file_path(path)
    image_files, text_files = seperate_files(all_files)

    # Prepare text content
    path_text = [(file_path, read_file(file_path)) for file_path in text_files]
    print("Access files complete.....")
    # Process images and text
    print("Processing files.....")
    results = []
    results.append(process_files_image_local(image_files, llm_image, llm_text))
    results.append(process_files_text(path_text, llm_text))
    print("Processing files complete....")
    print(f"""
    
    
    
    """)
    print(results)
    


# ------------------------
# Run
# ------------------------
if __name__ == "__main__":
    main()
