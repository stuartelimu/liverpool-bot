import os
import django
from django.conf import settings
from bs4 import BeautifulSoup
import requests
import time
import tweepy

os.environ['DJANGO_SETTINGS_MODULE'] = 'bot.settings'

url = 'https://www.sportinglife.com'

NLTK_DATA_PATH = settings.NLTK_DATA

def create_api():
    consumer_key = settings.CONSUMER_KEY
    consumer_secret = settings.CONSUMER_SECRET
    access_token = settings.ACCESS_TOKEN
    access_token_secret = settings.ACCESS_SECRET

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    try:
        api.verify_credentials()
    except Exception as e:
        print("Error creating api")
        raise e
    print("API created")
    return api

def scrape_team(team):
    """check if the game has started return a link to commentary else return appropriate message"""

    source = requests.get(f'{url}/football/live').text
    soup = BeautifulSoup(source, 'lxml')

    matches = soup.find_all('div', class_='footballMatchListItem')

    teams = []

    for match_item in matches:
        commentary_link = url + match_item.a['href']
        score_line = match_item.find('div', class_='scoreString').text # sometimes match has not started
        
        try:
            team_a = match_item.find('div', class_='teamA').span.span.text
            team_b = match_item.find('div', class_='teamB').span.span.text
           
        except AttributeError as e:
            team_a = match_item.find('div', class_='teamA').span.text
            team_b = match_item.find('div', class_='teamB').span.text

        if team_a == team or team_b == team:
            print(team)
            if score_line != 'v':
                live_score_min = match_item.find('div', class_='liveScoreMinutes').text
                tt = f'{commentary_link}, {team_a} {score_line} {team_b}'
                return tt

            else:
                return f'{team_a} v {team_b} \nMatch has not started'
        else:
            pass

    return "There are no games today"
        
                

def scrape_commentary(link):
    # match commentry, goals, subs etc...

    commentary_source = requests.get(link).text
    commentary_soup = BeautifulSoup(commentary_source, 'lxml')
    commentary = commentary_soup.find('ul', class_='commentary')

    events = []    
    # events = commentary.find_all('li', class_='event')

    event = commentary.find('li', class_='event')
    
    detail = event.find('div', class_='detail-col').text
    
    try:
        match_time = event.find('span', class_='match-time').text # current time
        # HT, goal, yellow card , red card or sub
        try:
            break_ = event.find('div', class_='type-col').svg.title.text
        except:
            break_ = event.find('div', class_='type-col').span.text
    except:
        # FT
        break_ = event.find('div', class_='type-col').span.text
        match_time = ''

    if break_ == 'Goal':
        break_ = '⚽'
        
    com = f'{match_time}  {break_} | {detail}' 

    # events.append(ccmm)
    return com

def main():

    api = create_api()
    
    while True:
        st = scrape_team("Liverpool")
        try:
            if st.startswith('https://'):
                score = st.split(', ')[1]
                commentary_link = st.split(', ')[0]
                commentary = scrape_commentary(commentary_link)
                status = f"{score} \n\n{commentary}"
                # print(status)
                api.update_status(status)
            else:
                print(st)
        except tweepy.TweepError as e:
            print(e.reason)

        time.sleep(30)

if __name__ == "__main__":  
    main()
