import random
import time

import nltk
import requests
from bs4 import BeautifulSoup

url = 'https://theathletic.com/'
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

def scrape_the_athletic():
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
                      ' AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'
        }
    r = requests.get(f'{url}author/james-pearce/', headers=HEADERS).text
    soup = BeautifulSoup(r, 'lxml')

    latest_articles = soup.find_all(attrs={"data-object-type": "article", "class": "col-sm-3"})

    latest_article_links =  [latest_article.a['href'] for latest_article in latest_articles]

    # latest_article_link = f"{url}{latest_article}"

    for link in latest_article_links:
        r = requests.get(f'{url}{link}', headers=HEADERS).text
        soup = BeautifulSoup(r, 'lxml')

        para = soup.find('div', id='the_paywall').text

        para_tokenized = tokenizer.tokenize(para)

        for _ in range(10):
            text = random.choice(para_tokenized)
            if text and 60 < len(text) < 210:
                break
        else:
            return None
        return f'{text} {link}'



print(scrape_the_athletic())
