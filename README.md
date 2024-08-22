# Ollama Translator

Ollama Translator is a Python-based command-line tool designed to translate markdown files using a local model powered by the Ollama API. This tool is versatile, supporting multiple languages and capable of maintaining the formatting integrity of markdown documents during translation.

## Features

- **Language Support**: Translates markdown files between multiple languages while preserving the original markdown formatting.
- **API Integration**: Uses the Ollama API for accurate and reliable translations.
- **Recursive Directory Processing**: Capable of processing directories recursively to handle multiple files at once.
- **Flexible Output Options**: Allows users to save translated files in the same directory as the source files or in a specified output directory.

## Supported Languages

The following language codes can be used with this tool, corresponding to their full language names:

```plaintext
zh-CN: chinese_simplified
zh-TW: chinese_traditional
ru: russian
de: german
es: spanish
fr: french
ja: japanese
pt: portuguese
vi: vietnamese
ar: arabic
en: english
```

## Installation

Clone the repository:

```bash
git clone https://github.com/your-github-username/ollama-translator.git
cd ollama-translator
```

Ensure that Python 3 is installed on your system, and install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

To use Ollama Translator, navigate to the directory containing `ollama-translator.py` and run the following command:

```bash
python ollama-translator.py --base-lang [base_language_code] --target-lang [target_language_code] --input-dir [input_directory] [--output-dir [output_directory]]
```

### Command-Line Arguments

- `--base-lang`: The base language code of the markdown files to translate from. Default is 'en'.
- `--target-lang`: The target language code to translate to. This argument is required.
- `--input-dir`: The path to the directory containing the input markdown files. This does not recurse into subdirectories.
- `--input-dir-all`: The path to the directory containing the input markdown files. This recurses into subdirectories.
- `--output-dir`: The path to the directory where the output files will be saved. If not provided, files will be saved next to the originals.
- `--output-origin`: If set, saves the output files in the same directory as the source files.

## Example

Translate all markdown files from English to Spanish within a specific directory:

```bash
python ollama-translator.py --base-lang en --target-lang es --input-dir /path/to/input --output-dir /path/to/output
```

## Acknowledgments

This project is inspired by and forked from [GPT Translator](https://github.com/daqing/gpt-translator), a project dedicated to translating texts using GPT models.

## Contributing

Contributions are welcome! Please fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.


### Notes:
- Ensure that the repository URL (`https://github.com/wolfreka/ollama-translator.git`) is replaced with the actual URL of your GitHub repository.
- Modify any other specifics such as the `python` command if your environment requires a different interpreter like `python3`.
- `requirements.txt` file for managing dependencies.
