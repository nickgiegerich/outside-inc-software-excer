import hashlib
from typing import List
from urllib.error import HTTPError
import requests
import re
import concurrent.futures
import urllib.request

DOCUMENT_URL = 'https://outside-interview.herokuapp.com/document'

SPELL_CHECK_BASE_URL = 'https://outside-interview.herokuapp.com/spelling/'

MAX_THREAD_WORKERS = 5  # number of threads used in calls

SPECIAL_CHARS = r'[!,*)@#%(&$_?.^"]'  # special character regex

SPLIT_CHARS = r';|,\s|\s|-'  # regex for when we split words


def load_url(url: str, timeout: float) -> int:
    """
    Helper method to make a call to the passed url

    @param url - represenation of the url

    @param timeout - representation of the request timeout duration

    @returns a status code from the server 204, 404 etc
    """
    with urllib.request.urlopen(url, timeout=timeout) as conn:
        return conn.getcode()


def retrieve_document(document_url: str) -> str:
    """
    Creates a list of words from the original document

    @returns the document as one large string
    """
    # making the initial request to API for document
    original_document = requests.get(document_url)

    # getting the documents content and decoding from bytes to string
    document_content = original_document.content.decode("utf-8")

    return document_content


def parse_document(document_to_parse: str) -> List[str]:
    """ 
    Cleans the document string and splits it into a list of single words

    @param document_to_parse - the string to parse

    @returns a clean list of individual words 
    """
    # substitute special characters with empty space
    document_cleaned = re.sub(
        SPECIAL_CHARS, ' ', document_to_parse)

    # split words where space, comma, apostraphe, and dash exist
    document_split = re.split(SPLIT_CHARS, document_cleaned)

    # create a list of the words to iterate over
    # final list is made from filtering out empty strings
    document_final = list(filter(None, document_split))

    return document_final


def build_urls(word_list: List[str]) -> List[str]:
    """
    Creates a list of urls from each word that needs to be spell checked

    @param word_list - a list of words from the original document

    @returns a list of url strings
    """

    spell_check_urls: List[str] = []  # intital empty list
    for word in word_list:
        word_url_to_check = SPELL_CHECK_BASE_URL + word
        spell_check_urls.append(word_url_to_check)

    return spell_check_urls


def spell_check_all_urls(urls_to_check: List[str]) -> List[str]:
    """
    Runs all urls in the list against the API to check for spelling mistakes

    @param urls_to_check - a list of url strings

    @returns a list of misspelled words
    """

    misspelled_words: list[str] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREAD_WORKERS) as executor:

        # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(
            load_url, url, 60): url for url in urls_to_check}

        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                future.result()
            except HTTPError as err:  # if we get an exception check if it's a 404
                if err.code == 404:

                    misspelled_word: str = (
                        url[len(SPELL_CHECK_BASE_URL):])  # gets the word at the end of url string

                    misspelled_words.append(misspelled_word)

    return misspelled_words


def create_hex_digest(list_to_digest: List[str]) -> str:
    """
    Takes a list of words and creates a single hex digest string

    @param list_to_digest - a list of words that need to be digested

    @returns a single string of the digest
    """
    concated_list = ''.join(list_to_digest)
    encoded_list = hashlib.md5(concated_list.encode())
    return encoded_list.hexdigest()

# ------------------------ DRIVER CODE ------------------------


print(  # let users know we are running processes
    '\n'
    'processing...'
)

# start with processing the document
document_string = retrieve_document(DOCUMENT_URL)

# clean the long document string and split it
parsed_words = parse_document(document_string)

# then build urls to check
urls = build_urls(word_list=parsed_words)

# then run these urls and get misspelled words list
misspelled_words_list = spell_check_all_urls(urls)

# finally pass misspelled words to hex function
answer = create_hex_digest(misspelled_words_list)

# prints the final result to terminal
print(
    '\n' +
    answer + '@outsideinc.com'
)
