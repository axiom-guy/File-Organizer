# 🗂️ File Organiser

An intelligent file organization utility that automatically classifies, renames, and sorts files based on their **content**, not just file names or extensions. It uses modern AI techniques to process **text** and **image** files, generate meaningful metadata, and organize them into well-structured directories.

---

## ✨ Features

- 📁 **Content-Aware Organization**  
  Automatically sorts files into folders based on extracted metadata from text or images.

- 🧠 **AI-Powered Metadata Generation**  
  Uses LLMs (locally or via API) to summarize text, caption images, and infer context.

- 📝 **Smart Renaming**  
  Renames files using sanitized, structured, and human-readable titles.

- 🔍 **Image & Document Support**  
  Processes PDF, TXT, JPEG, PNG, and more.

---

## 🚀 Getting Started
### 1. Creating and activating virtual environment
```bash
#create and activate a virtual environment
python -m venv file-organiser
source file-organiser
```

### 2. Clone the Repository
```bash
git clone https://github.com/axiom-guy/File-Organizer.git
cd File-Organizer

```
### 3. Installing dependencies
```bash
pip install -r requirements.txt
```

### 4.Run the organiser.
```bash
python main.py
```

## 🧠 AI Models Used
Text Models: Meta-Llama-3-8B-Instruct-GGUF<br>
Image Models: MiniCPM-V-2_6-gguf



