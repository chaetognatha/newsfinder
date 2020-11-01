#!/usr/bin/python3
"""
    Title: covid_news.py
    Date: 2020-11-01
    Author: Mattis Knulst
    Description:
        This program will scrape PDF files from folkhalsomyndigheten.se, it looks for new content every time it is run
        stores entries, and allows the user to view the current or old status updates, extracted from the first page of
        the PDF in either its original language or translated to english. Running without flags will just print the
        entire latest update in Swedish.
    List of functions:
        check_logs() : will see if there is a .txt log file and create it if it doesn't exist
        read_logs() : will read logs into memory
        write_logs() : will dump the logs from memory into files
        make_order() : a function that will take extracted entries and append it to database
        get_extract_pdf() : parses PDF files, opens the first page and extracts the information that is a status update
        stores extracted info in the database
        get_folkhalso_update() : scrapes the url for PDF files, downloads them if they are not already downloaded i.e.
        not in the download.txt, sends them to get_extract_pdf()
        display_update(): will show appropriate text in STDOUT
        write_log(): will write logs from memory


    List of non-standard modules:
        bs4: beautifulsoup and requests
        urllib.request
        PyPDF2
        googletrans

    Procedure:
        Take user input via argparse, look for new content, download new content, extract entries and add to log,
        print requested log entry to STDOUT


    Usage:
        python covid_news.py [-h] [-w W] [-c C] [-t]

    Comments:
        If printing a certain number of characters in the original language, the program will give a helpful
        error message if the number of characters given should exceed the total of the entry, this does not work
        with the translated text. However, if the given number of characters does exceed the max, it will just default
        to printing the entire entry.

"""
import os
from bs4 import BeautifulSoup
import requests
import urllib.request
import re
import PyPDF2
from googletrans import Translator
import argparse

parser = argparse.ArgumentParser("python covid_news.py")
parser.add_argument("-w", type=int, help="view an entry from this many weeks back")
parser.add_argument("-c", type=int, help="how many characters to view, e.g. 200")
parser.add_argument("-t", help="translate into English", action="store_true")
args = parser.parse_args()
status_updates = "status_updates.txt"
download_log = "downloads.txt"
slash_pat = re.compile(r"/.*/")
time_check = -1
my_run_list = []  # this list will store the database during the run
my_file_list = [] # this is a list of the pdf files that are already retrieved

if args.w:
    print(f"Retrieving entry from {args.w} weeks ago")
    if args.w > 0:
        time_check = - (args.w + 1)  # we will always be reading from the end of the file
if args.c:
    print(f"Displaying {args.c} characters:")
if args.t:
    print("Translating to English")
translator = Translator()

def read_log(log, my_list):
    if os.path.exists(log):
        with open(log, 'r') as f:
            for line in f:
                if line:
                    my_list.append(line.strip())

def check_logs(log):
    """
    :return: nothing, creates log file if not found in current folder
    """
    if not os.path.exists(log):
        with open(log, 'w') as f:
            print(f"creating {log}")


def make_order(entry):
    """
    :param entry: this is a one-line entry that is to be stored
    :return: nothing, the database is stored in memory during execution and the entry is added at index 0
    """
    if entry not in my_run_list:
        my_run_list.insert(0, entry.strip())


def get_extract_pdf(fh):
    """
    :param fh: the file name of a PDF
    :return: nothing, will send entries to make_order()
    """
    pdfFileObj = open(fh, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)  # creating a pdf reader object
    pageObj = pdfReader.getPage(0)  # creating a page object
    page_str = str(pageObj.extractText())  # extracting text from page
    page_lst = page_str.split("\n")
    my_extractor = []
    on_switch = False
    for item in page_lst:
        if item.startswith('Läget i Sverige'):
            on_switch = True
        if on_switch:
            my_extractor.append(item)
    if my_extractor != []:
        my_entry = ''.join(my_extractor)
        make_order(my_entry)
    pdfFileObj.close()


def get_folkhalso_update():
    """
    :return: nothing, looks for updates and sends pdfs to get_extract_pdf
    """
    url = "https://www.folkhalsomyndigheten.se/smittskydd-beredskap/utbrott/aktuella-utbrott/covid-19/statistik-och-analyser/veckorapporten-om-covid-19/"
    # Make a GET request to fetch the raw HTML content
    html_content = requests.get(url).text
    # Parse the html content
    soup = BeautifulSoup(html_content, "lxml")
    for link in soup.find_all('a'):
        current_link = link.get('href')
        if "veckorapport" and ".pdf" in current_link:
            # print(current_link)
            get_this_url = r"https://www.folkhalsomyndigheten.se" + current_link
            file_name = slash_pat.sub('', current_link)
            if file_name not in my_file_list:
                print("Hang on, retrieving new .pdfs")
                urllib.request.urlretrieve(get_this_url, file_name)
                get_extract_pdf(file_name)
                my_file_list.append(file_name)
            else:
                continue


def display_update():
    """
    :return: nothing, will print appropriate text from log
    """
    with open(status_updates, 'r') as f:
        my_entries = []
        for line in f:
            my_entries.append(line.replace('.', '.\n'))
        if args.t:
            print(translator.translate(my_entries[time_check][:args.c]).text)
        else:
            print(my_entries[time_check][:args.c])



def write_log(fh, my_list):
    """
    :return: nothing, will print the updated entry list to file
    """
    with open(fh, 'w') as f:
        for line in my_list:
            if line.strip() != '':
                print(line, file=f)

read_log(status_updates, my_run_list)
read_log(download_log, my_file_list)
check_logs(status_updates)
check_logs(download_log)
get_folkhalso_update()
write_log(status_updates, my_run_list)
write_log(download_log, my_file_list)
display_update()
