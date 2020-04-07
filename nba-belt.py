import numpy as np
import pandas as pd
from bs4 import BeautifulSoup, SoupStrainer
import sys
import string
import requests
import datetime
from datetime import timedelta
import time
import os.path
from os import path


first_game = datetime.datetime.strptime('2019-10-22', "%Y-%m-%d")
last_game = datetime.datetime.strptime('2020-04-15', "%Y-%m-%d")
winning_team = 'Toronto'
pd.options.display.max_colwidth = 100

## web scraping
def soup(game_date=None, df=None, winning_team=str):
    while game_date < datetime.datetime.now() and datetime.datetime.now() <= last_game:
        d = game_date.day
        m = game_date.month
        y = game_date.year
        date_str = str(y) + '-' + str(m) + '-' + str(d)

        base_url = 'http://basketball-reference.com/boxscores/index.fcgi?month=' + str(m) + '&day=' +str(d)+'&year=' + str(y)
        page_response = requests.get(base_url, timeout=5)
        page_content = BeautifulSoup(page_response.content, "html.parser")


        scores = page_content.find_all('table', {'class': 'teams'}) ## gets each box score, puts it into list

        for games in scores: ## loop through them and check which box score contains the winner
            if winning_team in str(games):
                data = []
                champ_score = games

                winner = champ_score.find('tr', {'class':'winner'}) ## find row that has the winner
                winning_team = winner.find('a').string ## winning team name
                winning_score = winner.find('td', {'class':'right'}).string ## winning team score

                loser = champ_score.find('tr', {'class':'loser'}) ## find row that has the loser
                losing_team = loser.find('a').string ## losing team name
                losing_score = loser.find('td', {'class':'right'}).string ## losing team score

                final_score = winning_score + " - " + losing_score

                box_score_td = champ_score.find('td', {'class':['gamelink']}) ## find the box score link
                href = box_score_td.find('a')['href'] ## get the href from the anchor tag
                box_score_url = 'https://www.basketball-reference.com' + href
                # anchor_tag = href='https://www.basketball-reference.com" + href + "'>" + 'Link</a>'


                data.insert(0, {'Date': date_str,
                                'Winner': winning_team,
                                'Loser': losing_team,
                                'Final Score': final_score,
                                'Box Score': box_score_url})
                df = pd.concat([pd.DataFrame(data), df], ignore_index=True)
                break
            else:
                continue

        game_date = game_date + timedelta(days=1)

    columns = ['Date','Winner', 'Loser', 'Final Score', 'Box Score']
    df = df[columns] # reorder columns
    # df = df.set_index('date') # set index to date
    return(df)


def backfill():
    columns = ['Date','Winner', 'Loser', 'Final Score', 'Box Score'] ## create new dataFrame
    new_df = pd.DataFrame(columns = columns)

    df = soup(first_game, new_df, winning_team=winning_team)
    return(df)

def update():
    df = pd.read_csv("data/scores.csv")
    max_date = df['Date'][0]
    max_date = datetime.datetime.strptime(max_date, "%Y-%m-%d")
    max_date = max_date + timedelta(days=1)
    winner = df['Winner'][0]

    df = soup(max_date, df, winner)
    return(df)


def write_html(df=None):
    print('Writing HTML file.')
    html = df.to_html()
    html_file= open("data/game_data.html","w")
    html_file.write(html)
    html_file.close()

if path.exists("data/scores.csv") == True:
    print("Updating existing CSV")
    df = update()
    print("Done updating")
else:
    print("Creating dataframe from scratch")
    df = backfill()
    print("Created dataframe")

def write_winner(df=None):
    belt_holder = df['Winner'][0]
    if belt_holder == 'Atlanta':
        belt_holder = 'Atlanta Hawks'
    elif belt_holder == 'Boston':
        belt_holder = 'Boston Celtics'
    elif belt_holder == 'Brooklyn':
        belt_holder = 'Brooklyn Nets'
    elif belt_holder == 'Charlotte':
        belt_holder = 'Charlotte Hornets'
    elif belt_holder == 'Chicago':
        belt_holder = 'Chicago Bulls'
    elif belt_holder == 'Cleveland':
        belt_holder = 'Cleveland Cavaliers'
    elif belt_holder == 'Dallas':
        belt_holder = 'Dallas Mavericks'
    elif belt_holder == 'Denver':
        belt_holder = 'Denver Nuggets'
    elif belt_holder == 'Detroit':
        belt_holder = 'Detroit Pistons'
    elif belt_holder == 'Golden State':
        belt_holder = 'Golden State Warriors'
    elif belt_holder == 'Houston':
        belt_holder = 'Houston Rockets'
    elif belt_holder == 'Indiana':
        belt_holder = 'Indiana Pacers'
    elif belt_holder == 'LA Clippers':
        belt_holder = 'Los Angeles Clippers'
    elif belt_holder == 'LA Lakers':
        belt_holder = 'Los Angeles Lakers'
    elif belt_holder == 'Memphis':
        belt_holder = 'Memphis Grizzlies'
    elif belt_holder == 'Miami':
        belt_holder = 'Miami Heat'
    elif belt_holder == 'Milwaukee':
        belt_holder = 'Milwaukee Bucks'
    elif belt_holder == 'Minnesota':
        belt_holder = 'Minnesota Timberwolves'
    elif belt_holder == 'New Orleans':
        belt_holder = 'New Orleans Pelicans'
    elif belt_holder == 'New York':
        belt_holder = 'New York Knicks'
    elif belt_holder == 'Oklahoma City':
        belt_holder = 'Oklahoma City Thunder'
    elif belt_holder == 'Orlando':
        belt_holder = 'Orlando Magic'
    elif belt_holder == 'Philadelphia':
        belt_holder = 'Philadelphia Sixers'
    elif belt_holder == 'Phoenix':
        belt_holder = 'Phoenix Suns'
    elif belt_holder == 'Portland':
        belt_holder = 'Portland Trail Blazers'
    elif belt_holder == 'Sacramento':
        belt_holder = 'Sacramento Kings'
    elif belt_holder == 'San Antonio':
        belt_holder = 'San Antonio Spurs'
    elif belt_holder == 'Toronto':
        belt_holder = 'Toronto Raptors'
    elif belt_holder == 'Utah':
        belt_holder = 'Utah Jazz'
    elif belt_holder == 'Washington':
        belt_holder = 'Washington Wizards'
    else:
        belt_holder = belt_holder

    holder_text=open("data/current_holder.txt","w")
    holder_text.write(belt_holder)
    holder_text.close()
    return(belt_holder)

## write html
write_html(df)

##write csv
df.to_csv(r'data/scores.csv')

## find current belt holder
belt_holder = write_winner(df)
print("Current championship belt holder: " + belt_holder)

## find team with the most title defenses
## find team with the most title defenses
winner_count = df.groupby('Winner').count()[['Final Score']] ## get count of each games won while holding belt
winner_count = winner_count.sort_values('Final Score', axis=0, ascending=False, inplace=False, kind='quicksort', na_position='last') ## reorder by Winner Score
winner_count = winner_count.reset_index(drop=False) ## remove index so Winner header can be called
most_win_team = winner_count['Winner'][0]
most_wins = winner_count['Final Score'][0]


print("The team with the most title defenses: " + most_win_team)
print("They have " + str(most_wins) + " title defense wins.")
