from html.parser import HTMLParser
from urllib.request import urlopen
import re
from PyPDF2 import PdfReader
from io import BytesIO
import requests
from bs4 import BeautifulSoup
import os

# Regex pattern to match a URL
HTTP_URL_PATTERN = r'^http[s]*://.+'

# List of websites to scrape URLs from
entrypoints = [['https://www.realized1031.com/glossary',
                None,None,'glossary',None]]

# String to store all website text
output = ''


def remove_duplicate_newlines(s):
    return re.sub(r'(\n)+', r'\n', s)


# Obtains text content from body of an HTML page
def get_text(url):
    # Send a request to the URL and get the HTML content
    response = requests.get(url)
    html_content = response.content

    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Find the header and footer elements
    header = soup.find('header')
    footer = soup.find('footer')

    # Remove the header and footer content
    if header:
        header.extract()
    if footer:
        footer.extract()
    soup.prettify()

    # Find and return the remaining text on the webpage
    text = soup.get_text()
    text = remove_duplicate_newlines(text)
    return text


# Obtains text from URLs containing PDFs
def get_pdf_text(url):
    # Send a GET request to the URL and get the response object
    response = requests.get(url)

    # Read the content of the response object into a BytesIO object
    pdf_bytes = BytesIO(response.content)

    # Create a PdfReader object from the BytesIO object
    pdf_reader = PdfReader(pdf_bytes)

    # Extract the text from the PDF file
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    # Return the extracted text
    return text


# Tests to determine whether a URL is a PDF document
def is_pdf_url(url):
    try:
        response = requests.head(url)
        content_type = response.headers.get('Content-Type', '').lower()
        return 'application/pdf' in content_type
    except requests.exceptions.RequestException:
        return False


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href':
                    self.links.append(attr[1])


def get_links(url, pattern, alt_url, kword, avoided):
    response = urlopen(url)
    html = response.read()
    parser = LinkParser()
    parser.feed(html.decode())

    if alt_url is None:
        alt_url = url

    items = []

    if pattern:
        for url in parser.links:
            if re.search(pattern, url):
                items.append(alt_url + url)
    else:
        pattern = HTTP_URL_PATTERN
        for url in parser.links:
            if re.search(pattern, url):
                items.append(url)

    if kword:
        new_items = []
        for item in items:
            if kword in item:
                new_items.append(item)
        items = new_items

    if avoided:
        new_items = []
        for item in items:
            if avoided not in item:
                new_items.append(item)
        items = new_items

    return items


def scraper():
    links = []
    for site, urlpattern, alternate_url, keyword, avoid in entrypoints:
        if urlpattern:
            urlpattern = urlpattern.strip('"')
        newlinks = get_links(site, urlpattern, alternate_url, keyword, avoid)
        links = links + newlinks

    for link in links:
        site_content = ''

        if is_pdf_url(link):
            site_content = get_pdf_text(link)
        else:
            site_content = get_text(link)

        # Remove blank lines from the string
        lines = site_content.split('\n')
        non_empty_lines = [line for line in lines if line.strip() != ""]
        final_content = '\n'.join(non_empty_lines)

        # Open the file in write mode and save the output
        with open('text/' + link[12:].replace("/", "_").replace(".", "") + ".txt", "w") as f:
            f.write(final_content)

    print("Scraping complete")