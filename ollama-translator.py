import requests
import os
import argparse

# API configuration variables
API_URL = "http://localhost:11434"
API_KEY = os.getenv('OLLAMA_API_KEY', 'ollama')
API_MODEL = "qwen2:7b"
API_TEMPERATURE = 0.5
API_MAX_TOKENS = 4096
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

    completion = client.chat.completions.create(
        model="API_MODEL",
        messages=messages
    )

    return completion.choices[0].message.content

def translate_file(input_path, output_path, base_lang, target_lang, client):
    print(f"Processing file: {input_path}")
    try:
        with open(input_path, "r") as f:
            file_content = f.read()
    except FileNotFoundError:
        print(f"Input file not found: {input_path}")
        return

    print(f"Translating file {input_path} to {target_lang}...")
    try:
        translated_text = translate_full(file_content, base_lang, target_lang, client)
    except Exception as e:
        print(f"Error during translation: {e}")
        return

    try:
        with open(output_path, "w") as f:
            f.write(translated_text)
        print(f"Translation saved to {output_path}")
    except IOError:
        print(f"Cannot write to output file: {output_path}")

def process_directory(input_dir, output_dir, base_lang, target_lang, recursive, client):
    if recursive:
        for root, dirs, files in os.walk(input_dir):
            process_files(root, files, base_lang, target_lang, input_dir, output_dir, client)
    else:
        files = os.listdir(input_dir)
        process_files(input_dir, files, base_lang, target_lang, input_dir, output_dir, client)

def process_files(directory, files, base_lang, target_lang, input_dir, output_dir, client):
    for filename in files:
        if filename.endswith(".md"):
            input_path = os.path.join(directory, filename)
            if output_dir:
                relative_path = os.path.relpath(input_path, input_dir)
                output_path = os.path.join(output_dir, relative_path.replace(".md", f".{target_lang}.md"))
            else:
                output_path = input_path.replace(".md", f".{target_lang}.md")
            translate_file(input_path, output_path, base_lang, target_lang, client)
        else:
            print(f"Skipping non-markdown file: {filename}")

def main():
    parser = argparse.ArgumentParser(description="Translate markdown files using a local ollama model. Supported languages are: " + ", ".join(f"{k}: {v}" for k, v in lang_dict.items()))

    parser.add_argument('--base-lang', metavar='base_lang', default="en", type=str, help='The base language to translate from. Choose from: ' + ', '.join(lang_dict.keys()))
    parser.add_argument('--target-lang', metavar='target_lang', type=str, required=True, help='The target language to translate to. Choose from: ' + ', '.join(lang_dict.keys()))
    parser.add_argument('--input-dir', metavar='input directory', type=str, help='Path to the directory containing input files, optionally recurses through subdirectories.')
    parser.add_argument('--recursive', action='store_true', help='If set, recurses through subdirectories within the input directory.')
    parser.add_argument('--output-dir', metavar='output directory', type=str, help='Path to the directory where output files will be saved')
    parser.add_argument('--output-origin', action='store_true', help='Save output files to the same directory as the source files')
    parser.add_argument('--api-client', metavar='api_client', type=str, help='API client for making translation requests')

    args = parser.parse_args()

    # Here, you would initialize your API client based on args.api_client or another method.
    client = initialize_api_client(args.api_client)

    output_dir = None if args.output_origin else args.output_dir

    if args.input_dir:
        process_directory(args.input_dir, output_dir, args.base_lang, args.target_lang, args.recursive, client)

if __name__ == '__main__':
    main()

