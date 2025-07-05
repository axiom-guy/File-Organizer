#!/usr/bin/env python
# coding: utf-8

import os
import sys
import warnings
import base64
import torch
import time
import re



# ------------------------
# Silence all unnecessary logs
# ------------------------

# Reduce llama.cpp and Metal logs
os.environ["LLAMA_LOG_LEVEL"] = "ERROR"
os.environ["GGML_METAL_LOG_LEVEL"] = "NONE"

# Suppress Python warnings like PDF CropBox
warnings.filterwarnings("ignore", message="CropBox missing from /Page")

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
from common_functions import tree_built_preview,organise,suppress_stderr
from llama_cpp import Llama
from llama_cpp.llama_chat_format import MiniCPMv26ChatHandler
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import InferenceClient
from alive_progress import alive_bar


# ------------------------
# Stderr suppressor 
# ------------------------


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
@suppress_stderr
def main():
    path=input("Enter the abs path of the directory, you what to organise:  ").strip()
    while not os.path.exists(path):
        print(f'Path {path} does not exist. Kindly enter a valid path.')
        path=input("Enter the abs path of the directory, you what to organise.").strip()

    print(f"Input path successfully set to {path}")
    print(f"""
    
{path}""")
    print(tree_builder(path))
    output_path=input(f"""Enter the abs output path for the arranged directory.(Default will be {os.path.join(os.path.dirname(path),'organized_dir')}):  """)
    if not output_path:
        output_path=os.path.join(os.path.dirname(path),'organized_dir')
    print(f"""Output path successfully set to {output_path}
    
    
    """)
    # Load models
    print("Loading models.....")
    llm_text = load_llm_text()
    llm_image = load_llm_image()
    print('Loading models complete......')
    print("""
    
    
    """)
    # Collect file paths
    print("Accessing files......")
    all_files = collect_file_path(path)
    image_files, text_files = seperate_files(all_files)

    # Prepare text content
    path_text = [(file_path, read_file(file_path)) for file_path in text_files]
    print("Accessing files complete.....")
    # Process images and text
    print("""
    
    
    """)
    print("Processing files.....")
    
    result_image=process_files_image_local(image_files, llm_image, llm_text)
    result_text=process_files_text(path_text, llm_text)
    results=result_image+result_text
    print("Processing files complete....")
    print(f"""
    
    
    
    """)
    print(tree_built_preview(results,output_path))

    x=input(f"""
    
Do you want to make changes(y/n):""")
    if(x=='y' or x=='Y'):
        organise(results,output_path)
    else:
        return None
    


# ------------------------
# Run
# ------------------------
if __name__ == "__main__":
    main()
