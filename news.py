import random
import time

import nltk
import requests
from bs4 import BeautifulSoup

url = 'https://theathletic.com'
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
                      ' AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'
        }

def extract_paratext(para_soup):
    
    para = para_soup.find('div', id='the_paywall').text
    return tokenizer.tokenize(para)

def extract_text(para_tokenized):
    """Returns a sufficiently-large random text from a tokenized paragraph,
    if such text exists. Otherwise, returns None."""

    for _ in range(10):
        text = random.choice(para_tokenized)
        if text and 60 < len(text) < 210:
            return text

    return None

def scrape_the_athletic():
    """Scrapes content from The Athletic blog."""

    r = requests.get(f'{url}/author/james-pearce/', headers=HEADERS).text
    soup = BeautifulSoup(r, 'lxml')

    latest_articles = soup.find_all(attrs={"data-object-type": "article", "class": "col-sm-3"})

    latest_article_links =  [latest_article.a['href'] for latest_article in latest_articles]


    for link in latest_article_links:
        link = f"{url}{link}"
        r = requests.get(link, headers=HEADERS).text
        soup = BeautifulSoup(r, 'lxml')

        para = extract_paratext(soup)
        text = extract_text(para)

        if not text:
            continue

        yield f'{text} {link}'


scrape_the_athletic()
