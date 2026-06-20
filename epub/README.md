# epub-builder

`epub-builder` is a simple Python tool that converts web page URLs into text-only EPUB files (optimized for e-ink displays by removing images and media).

## Initialization

First, it is recommended to set up a virtual environment and install the required dependencies:

```bash
# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the required dependencies
pip install -r requirements.txt
```

## Usage

To use the tool, run `epub-builder.py` with the URL of the article you want to convert.

```bash
# Basic usage
python epub-builder.py <URL>

# Specify a custom output file name
python epub-builder.py <URL> --output custom_name.epub
```
