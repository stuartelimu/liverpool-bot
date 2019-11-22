import random
import time

import nltk
import requests
from bs4 import BeautifulSoup

import tweepy
from commentary import create_api

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

def scrape_liverpool_echo():

    r = requests.get('https://www.liverpoolecho.co.uk/all-about/liverpool-fc', headers=HEADERS).text
    soup = BeautifulSoup(r, 'lxml')

    articles = soup.find(attrs={"data-group": "topStories", "data-group-index": 1})

    latest_articles = articles.find_all('div', class_='teaser')

    latest_article_links =  [latest_article.a['href'] for latest_article in latest_articles]

    for link in latest_article_links:
        r = requests.get(link, headers=HEADERS).text
        soup = BeautifulSoup(r, 'lxml')   

        paras_body = soup.find('div', class_='article-body')

        paras = paras_body.find_all('p')

        paras_text = [para.text for para in paras if para.text]

        para = random.choice(paras_text)

        para_tokenized = tokenizer.tokenize(para)

        text = extract_text(para_tokenized)

        if not text:
            continue

        yield f'{text} {link}'


def main():
    """Encompasses the main loop of the bot."""

    api = create_api()

    print('---Bot started---\n')
    news_funcs = ['scrape_the_athletic', 'scrape_liverpool_echo']
    news_iterators = []  
    for func in news_funcs:
        news_iterators.append(globals()[func]())
    while True:
        for i, iterator in enumerate(news_iterators):
            try:
                tweet = next(iterator)
                api.update_status(tweet)
                print(tweet, end='\n\n')
                time.sleep(1800)  
            except StopIteration:
                news_iterators[i] = globals()[newsfuncs[i]]()
            except tweepy.TweepError as e:
                print(e.reason)

if __name__ == "__main__":  
    main()
