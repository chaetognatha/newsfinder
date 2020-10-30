# importing the libraries
import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
import urllib.request
import re
import PyPDF2
status_updates = "status_updates.txt"
slash_pat = re.compile(r"/.*/")
def check_logs():
    if not os.path.exists(status_updates):
        with open(status_updates, 'w') as f:
            print("creating log file")


def get_extract_pdf(fh):
    # creating a pdf file object
    pdfFileObj = open(fh, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj) # creating a pdf reader object
    pageObj = pdfReader.getPage(0) # creating a page object
    page_str = str(pageObj.extractText()) # extracting text from page
    page_lst = page_str.split("\n")
    my_extractor = []
    on_switch = False
    for item in page_lst:
        if item.startswith('Läget i Sverige'):
            on_switch = True
        if on_switch:
            my_extractor.append(item)
    #stat_report.join(my_extractor)

    if my_extractor != []:
        with open(status_updates, 'a') as f:
            print(''.join(my_extractor), file=f)
    # closing the pdf file object
    pdfFileObj.close()


def get_folkhalso_update():
    url = "https://www.folkhalsomyndigheten.se/smittskydd-beredskap/utbrott/aktuella-utbrott/covid-19/statistik-och-analyser/veckorapporten-om-covid-19/"

    # Make a GET request to fetch the raw HTML content
    html_content = requests.get(url).text

    # Parse the html content
    soup = BeautifulSoup(html_content, "lxml")
    # print(soup.prettify()) # print the parsed data of html
    for link in soup.find_all('a'):
        current_link = link.get('href')
        if "veckorapport" and ".pdf" in current_link:
            # print(current_link)
            get_this_url = r"https://www.folkhalsomyndigheten.se" + current_link
            file_name = slash_pat.sub('', current_link)
            if not os.path.exists(file_name):
                print("Hang on, retrieving new .pdfs")
                urllib.request.urlretrieve(get_this_url, file_name)
                get_extract_pdf(file_name)
            else:
                continue
    with open(status_updates, 'r') as f:
        my_entries = []
        for line in f:
            my_entries.append(line.replace('.', '.\n'))
        print(my_entries[0])

def scan_local_news():
    url = r"https://www.lunduniversity.lu.se/about-lund-university/universitys-handling-coronavirus"
    html_content = requests.get(url).text
    soup = BeautifulSoup(html_content, "lxml")
    #print(soup.prettify())
    text = soup.find_all(text=True)
    print(set([t.parent.name for t in text]))
    output = ''
    blacklist = [
        '[document]',
        'noscript',
        'header',
        'html',
        'meta',
        'head',
        'input',
        'script',
        'button',
        'footer',
        'label',
        'script',

        # there may be more elements you don't want, such as "style", etc.
    ]

    for t in text:
        if t.parent.name not in blacklist:
            output += '{} '.format(t)
    my_index = output.find("for education:")
    print(output[my_index:my_index+3890].replace("\n", ""))


check_logs()
get_folkhalso_update()
scan_local_news()






