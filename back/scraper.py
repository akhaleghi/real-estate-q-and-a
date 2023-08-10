from html.parser import HTMLParser
from urllib.request import urlopen
import re
import csv
from PyPDF2 import PdfReader
from io import BytesIO
import requests
from bs4 import BeautifulSoup

HTTP_URL_PATTERN = r'^http[s]*://.+'  # Regex pattern to match a URL

entrypoints = [['https://placester.com/real-estate-marketing-academy/real-estate-definitions',None,None,None,'placester'],
               ['https://www.century21.com/glossary','^/glossary.+',None,None,None],
               ['https://www.dre.ca.gov/publications/referencebook.html','^/files/pdf/refbook.+','https://www.dre.ca.gov',None,None],
               ['https://www.realized1031.com/glossary',None,None,'glossary',None]]

othersites = ['https://placester.com/real-estate-marketing-academy/real-estate-definitions',
              'https://learn.g2.com/real-estate-terms',
              'https://listwithclever.com/real-estate-terms/',
              'https://theclose.com/real-estate-terms/',
              'https://www.homecity.com/blog/real-estate-terms/']


def remove_duplicate_newlines(s):
    return re.sub(r'(\n)+', r'\n', s)


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

    # Find the remaining text on the webpage
    text = soup.get_text()
    text = remove_duplicate_newlines(text)
    return(text)

def get_pdf_text():
    # Download the PDF file
    url = "https://www.dre.ca.gov/files/pdf/refbook/ref06.pdf"

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

    # Print the extracted text
    print(text)

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href':
                    # if re.search(HTTP_URL_PATTERN, attr[1]):
                    #    res = re.sub(r'\?.*', "", attr[1])
                    self.links.append(attr[1])


def get_links(url, pattern, alt_url,keyword,avoid):
    response = urlopen(url)
    html = response.read()
    parser = LinkParser()
    parser.feed(html.decode())
    if alt_url == None:
        alt_url = url
    items = []
    if pattern:
        for link in parser.links:
            if re.search(pattern, link):
                items.append(alt_url + link)
    else:
        pattern = HTTP_URL_PATTERN
        for link in parser.links:
            if re.search(pattern, link):
                items.append(link)
    if keyword:
        new_items = []
        for item in items:
            if keyword in item:
                new_items.append(item)
        items = new_items
    if avoid:
        new_items = []
        for item in items:
            if avoid not in item:
                new_items.append(item)
        items = new_items
    return items


# Usage
for site, pattern, alt_url, keyword, avoid in entrypoints:
    if pattern:
        pattern = pattern.strip('"')
    links = get_links(site, pattern, alt_url, keyword, avoid)
    print(links)

# print(f'Estimated embedding cost: ${1000000/ 0.75 / 1000 * 0.0004:.2f}')

#url = "https://www.dre.ca.gov/files/pdf/refbook/ref06.pdf"
#txt = get_text(url)
#text2 = get_pdf_text()
#print(text2)