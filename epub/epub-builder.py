import argparse
import requests
from readability import Document
from bs4 import BeautifulSoup
from ebooklib import epub
import os
import re

def clean_filename(title):
    # Remove invalid characters from title for filename
    clean_title = re.sub(r'[\\/*?:"<>|]', "", title)
    return clean_title.strip()

import urllib.parse

def build_epub(url, output_path=None):
    # Fetch page
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    print(f"Fetching URL: {url}")

    html_text = None
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_text = response.text
    except requests.exceptions.HTTPError as e:
        if response.status_code in [403, 503]:
            print(f"Encountered {response.status_code} Forbidden (likely Cloudflare or anti-bot protection).")
            print("Attempting to bypass using Google Web Cache...")

            # Using Google Web Cache as a fallback for Cloudflare blocks.
            # To avoid Google's own bot protection (enablejs redirect), we can strip the 'https://'
            # and format the cache URL properly.
            cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{url}"
            try:
                # Add a referer to seem more like a real user from Google search
                cache_headers = headers.copy()
                cache_headers['Referer'] = 'https://www.google.com/'

                cache_response = requests.get(cache_url, headers=cache_headers)
                cache_response.raise_for_status()

                if "httpservice/retry/enablejs" in cache_response.text:
                    print("Google Web Cache returned a JS challenge, falling back to Google Translate proxy...")
                    # Fallback to translate if cache is blocked by Google's bot protection
                    translate_url = f"https://translate.google.com/translate?hl=en&sl=auto&tl=zh-TW&u={urllib.parse.quote(url)}"
                    trans_response = requests.get(translate_url, headers=headers)
                    trans_response.raise_for_status()
                    html_text = trans_response.text
                    print("Successfully fetched content via Google Translate proxy.")
                else:
                    html_text = cache_response.text
                    print("Successfully fetched content via Google Web Cache.")
            except Exception as proxy_e:
                print(f"Error fetching URL via proxy/cache: {proxy_e}")
                return
        else:
            print(f"Error fetching URL: {e}")
            return
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return

    # Extract readable content
    print("Extracting content...")
    doc = Document(html_text)
    title = doc.title()
    content_html = doc.summary()

    # Clean HTML: remove images and keep it text only
    print("Cleaning HTML (removing images and media)...")
    soup = BeautifulSoup(content_html, 'html.parser')

    # Remove images, pictures, svgs, figures, video, audio, iframes
    for tag in soup(['img', 'picture', 'svg', 'figure', 'video', 'audio', 'iframe', 'source', 'track']):
        tag.decompose()

    # The cleaned content
    cleaned_html = str(soup)

    # Determine output filename
    if not output_path:
        filename = clean_filename(title)
        if not filename:
            filename = "output"
        output_path = f"{filename}.epub"

    print(f"Building EPUB: {output_path}")

    # Create EPUB
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier(url)
    book.set_title(title)
    book.set_language('en')
    book.add_author('epub-builder')

    # Create a chapter
    c1 = epub.EpubHtml(title=title, file_name='chap_01.xhtml', lang='en')
    c1.content = f'<h1>{title}</h1>\n{cleaned_html}'

    # Add chapter to book
    book.add_item(c1)

    # Define Table Of Contents
    book.toc = (epub.Link('chap_01.xhtml', title, 'chap_01'),)

    # Add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Basic spine
    book.spine = ['nav', c1]

    # Write epub file
    try:
        epub.write_epub(output_path, book, {})
        print(f"Successfully created: {output_path}")
    except Exception as e:
        print(f"Error writing EPUB file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a web page to an EPUB file.")
    parser.add_argument("url", help="The URL of the web page to convert.")
    parser.add_argument("--output", "-o", help="The output EPUB file name (optional).")

    args = parser.parse_args()

    build_epub(args.url, args.output)
