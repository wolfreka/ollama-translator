import os
import requests
import argparse
import time

# API configuration variables
API_URL = "http://localhost:11434"
API_KEY = os.getenv('OLLAMA_API_KEY', 'ollama')
API_MODEL = "qwen2:7b"
API_TEMPERATURE = 0.5
API_MAX_TOKENS = 1024
API_ENDPOINT = "/v1/chat/completions"

# Language dictionary for full language names
lang_dict = {
    "zh-CN": "chinese_simplified",
    "zh-TW": "chinese_traditional",
    "ru": "russian",
    "de": "german",
    "es": "spanish",
    "fr": "french",
    "ja": "japanese",
    "pt": "portuguese",
    "vi": "vietnamese",
    "ar": "arabic",
    "en": "english",
}

def initialize_api_client(api_key):
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {api_key}"})
    return session

def count_tokens(text):
    """Simplified token counting function."""
    return len(text) // 4

def split_text(text, max_tokens):
    """Split text into smaller chunks ensuring that each chunk ends at a sentence boundary."""
    lines = text.splitlines(True)  # Keep line breaks
    chunks = []
    current_chunk = ""
    current_tokens = 0

    total_lines = len(lines)
    print(f"Calculating splits: {total_lines} lines")

    for i, line in enumerate(lines):
        line_tokens = count_tokens(line)
        if current_tokens + line_tokens > max_tokens:
            chunks.append(current_chunk)
            current_chunk = line
            current_tokens = line_tokens
        else:
            current_chunk += line
            current_tokens += line_tokens

        # Show progress
        progress = (i + 1) / total_lines
        display_progress_bar(progress, prefix='Splitting')

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def display_progress_bar(progress, prefix='', length=40, suffix=''):
    """Display a simple progress bar."""
    block = int(round(length * progress))
    bar = '||' + '+' * block + '=' * (length - block) + '||'
    print(f'\r{prefix}: {bar} {int(progress * 100)}% {suffix}', end='', flush=True)

def translate_full(full_text, input_lang, target_lang, client):
    format = "markdown"
    input_lang_full = lang_dict.get(input_lang, input_lang)
    target_lang_full = lang_dict.get(target_lang, target_lang)

    system_prompt = f"You are a translation tool. You receive a text snippet from a file in the following format:\n{format}\n\n. The file is also written in the language:\n{input_lang_full}\n\n. As a translation tool, you will solely return the same string in {target_lang_full} without losing or amending the original formatting. Your translations are accurate, aiming not to deviate from the original structure, content, writing style and tone."
    code_prompt = "Make sure don't translate code blocks in markdown format, and don't translate image paths in :src field, and do translate the alt field from img tag"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": code_prompt},
        {"role": "user", "content": full_text}
    ]

    start_time = time.time()
    response = client.post(
        API_URL + API_ENDPOINT,
        json={
            "model": API_MODEL,
            "messages": messages,
            "temperature": API_TEMPERATURE,
            "max_tokens": API_MAX_TOKENS
        },
        timeout=30
    )
    elapsed_time = time.time() - start_time
    return response.json()["choices"][0]["message"]["content"], elapsed_time

def translate_file(input_path, output_path, base_lang, target_lang, client):
    print(f"Processing file: {input_path}")
    try:
        start_time = time.time()
        with open(input_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        elapsed_time = time.time() - start_time
        print(f"File read step: {elapsed_time:.2f} seconds")
    except FileNotFoundError:
        print(f"Input file not found: {input_path}")
        return
    except UnicodeDecodeError:
        print(f"Could not decode file {input_path} using utf-8 encoding.")
        return

    # Progress bar for simulation slice calculation
    simulate_progress_bar("Preparing to split text")

    start_time = time.time()
    chunks = split_text(file_content, API_MAX_TOKENS)
    elapsed_time = time.time() - start_time
    print(f"\nSplitting step: {elapsed_time:.2f} seconds")
    
    translated_chunks = []
    total_translation_time = 0

    for i, chunk in enumerate(chunks):
        progress = (i + 1) / len(chunks)
        suffix = f"{i+1}/{len(chunks)}"
        display_progress_bar(progress, prefix='Translating chunks', suffix=suffix)
        translated_chunk, translation_time = translate_full(chunk, base_lang, target_lang, client)
        translated_chunks.append(translated_chunk)
        total_translation_time += translation_time

    print(f"\nTotal translation time: {total_translation_time:.2f} seconds")

    translated_text = ''.join(translated_chunks)

    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        start_time = time.time()
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(translated_text)
        elapsed_time = time.time() - start_time
        print(f"File write step: {elapsed_time:.2f} seconds")
        print(f"Translation saved to {output_path}")
    except IOError:
        print(f"Cannot write to output file: {output_path}")

def simulate_progress_bar(description, duration=0.5):
    """Simulates a progress bar for a given duration."""
    print(description)
    for i in range(101):
        display_progress_bar(i / 100.0, prefix=description)
        time.sleep(duration / 100)
    print()

def scan_directory(input_dir):
    """Scan the directory and count the total number of markdown files."""
    all_files = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".md"):
                all_files.append(os.path.join(root, file))
    return all_files

def process_directory(input_dir, output_dir, base_lang, target_lang, recursive, client):
    # Scan folders and show the number of files
    
    print("Scanning directory for markdown files...")
    all_files = scan_directory(input_dir)
    
    total_files = len(all_files)
    print(f"Total markdown files found: {total_files}")

    for i, file_path in enumerate(all_files):
        progress = (i + 1) / total_files
        display_progress_bar(progress, prefix='Processing files')
        relative_path = os.path.relpath(file_path, input_dir)
        if output_dir:
            output_path = os.path.join(output_dir, relative_path.replace(".md", f".{target_lang}.md"))
        else:
            output_path = file_path.replace(".md", f".{target_lang}.md")
        translate_file(file_path, output_path, base_lang, target_lang, client)

    print("\nAll files processed.")

def main():
    parser = argparse.ArgumentParser(description="Translate markdown files using a local Ollama model. Supported languages are: " + ", ".join(f"{k}: {v}" for k, v in lang_dict.items()))

    parser.add_argument('--base-lang', metavar='base_lang', default="en", type=str, help='The base language to translate from. Choose from: ' + ', '.join(lang_dict.keys()))
    parser.add_argument('--target-lang', metavar='target_lang', type=str, required=True, help='The target language to translate to. Choose from: ' + ', '.join(lang_dict.keys()))
    parser.add_argument('--input-dir', metavar='input directory', type=str, required=True, help='Path to the directory containing input files, optionally recurses through subdirectories.')
    parser.add_argument('--recursive', action='store_true', help='If set, recurses through subdirectories within the input directory.')
    parser.add_argument('--output-dir', metavar='output directory', type=str, help='Path to the directory where output files will be saved')
    parser.add_argument('--output-origin', action='store_true', help='Save output files to the same directory as the source files')

    args = parser.parse_args()

    if args.target_lang not in lang_dict:
        print(f"Unsupported target language: {args.target_lang}")
        return

    client = initialize_api_client(API_KEY)

    output_dir = None if args.output_origin else args.output_dir

    if args.input_dir:
        process_directory(args.input_dir, output_dir, args.base_lang, args.target_lang, args.recursive, client)

if __name__ == '__main__':
    main()
