#!/usr/bin/env python
# coding: utf-8

# # Webscraper

# ## Import Libraries

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests 
from bs4 import BeautifulSoup
import re
import itertools
import time


sns.set()


# ## Scrape Data

# In[2]:


tournament_url = 'https://www.vlr.gg/event/matches/1657/valorant-champions-2023/?series_id=all'


# In[3]:


def scrape_game(soup, game_id):
    """
    Scrapes game information from a BeautifulSoup object based on the provided game ID.

    Parameters:
    - soup (BeautifulSoup): A BeautifulSoup object containing the HTML content of a web page.
    - game_id (str): The unique identifier for the game being scraped.

    Returns:
    - tuple: A tuple containing two lists. The first list contains map titles, and the second list contains agent names.

    The function extracts information about a single Valorant game, including the map title and character names, based on the provided
    game ID from vlr.gg. It uses the BeautifulSoup library to parse HTML content and regular expressions for pattern matching.

    The map title is extracted from a <span> element with a specific style attribute within the game's HTML content.
    Character names are extracted from multiple <span> elements with a specific class attribute.

    Example:
    >>> from bs4 import BeautifulSoup
    >>> html_content = "<div class='vm-stats-game' data-game-id='123'>...</div>"
    >>> soup = BeautifulSoup(html_content, 'html.parser')
    >>> map_title, characters = scrape_game(soup, '123')
    >>> print(map_title)
    ['MapName', 'MapName', ...]
    >>> print(characters)
    ['Character1', 'Character2', ...]
    """
    game_soup = soup.find('div', {'class':'vm-stats-game', 'data-game-id':game_id})
    
    title_pattern = r'\b[A-Z][a-z]*\b'
    map_string = game_soup.find('span', {'style':'position: relative;'}).text
    map_title = re.findall(title_pattern, str(map_string))
    
    character_spans = game_soup.find_all('span', {'class':'stats-sq mod-agent small'})[:10]
    characters = [img['title'] for span in character_spans for img in span]
    
    map_title = map_title * len(characters)
    
    return map_title, characters


# In[4]:


def scrape_match(match_url):
    """
    Scrapes a list of game IDs from a given match URL from vlr.gg.

    Parameters:
    - match_url (str): The URL of the match page to be scraped.

    Returns:
    - tuple: A tuple containing a BeautifulSoup object representing the parsed HTML content of the match page,
      and a list of game IDs associated with the match.

    This function is designed to retrieve a list of game IDs from a match URL. It uses the requests library to fetch
    the HTML content of the specified URL and BeautifulSoup to parse the HTML. The game IDs are extracted from <div> elements
    with a specific class attribute in the HTML content.

    Example:
    >>> match_url = 'https://example.com/match/123'
    >>> soup, game_ids = scrape_match(match_url)
    >>> print(game_ids)
    ['game_id_1', 'game_id_2', ...]
    """

    html = requests.get(match_url)
    soup = BeautifulSoup(html.text, 'lxml')
    
    games = soup.find_all('div', {'class':'vm-stats-gamesnav-item js-map-switch'})
    game_ids = [game['data-game-id'] for game in games]
    
    return soup, game_ids


# In[5]:


def scrape_tournament(tournament_url):
    """
    Scrapes a list of match IDs from a given tournament URL from vlr.gg.

    Parameters:
    - tournament_url (str): The URL of the tournament page to be scraped.

    Returns:
    - list: A list of match IDs associated with the tournament.

    This function is designed to retrieve a list of match IDs from a tournament URL. It uses the requests library to fetch
    the HTML content of the specified URL and BeautifulSoup to parse the HTML. Match IDs are extracted from the <div> elements
    with specific class and style attributes. The function also utilizes regular expressions and itertools to process the data.

    Example:
    >>> tournament_url = 'https://example.com/tournament/456'
    >>> match_ids = scrape_tournament(tournament_url)
    >>> print(match_ids)
    ['123456', '789012', ...]
    """
    html = requests.get(tournament_url)
    soup = BeautifulSoup(html.text, 'lxml')
    
    tournament_pattern = r'href="/\d+/[^"]+"'
    matches = soup.find_all('div', {'class':'wf-card', 'style':'margin-bottom: 30px;'})
    
    links = [re.findall(tournament_pattern, str(strings)) for item in matches          for strings in item.children if re.findall(tournament_pattern, str(strings))]
    links = list(itertools.chain(*links))
    
    match_pattern = r'\b\d{6}\b'
    match_ids = [re.findall(match_pattern,string) for string in links]
    match_ids = list(itertools.chain(*match_ids))
    
    return match_ids


# In[6]:


def scrape_games_in_tournament():
    """
    Scrapes game data from multiple matches in a tournament from vlr.gg and returns it as a DataFrame.

    Returns:
    - pandas.DataFrame: A DataFrame containing scraped game data including map titles, character names,
      match IDs, and game IDs.

    This function orchestrates the scraping process by utilizing other functions (scrape_tournament, scrape_match,
    and scrape_game). It iterates through each match in a tournament, retrieves the relevant game and match information,
    and organizes it into a DataFrame. The scraping process involves fetching match IDs, match URLs, game IDs, map titles,
    and character names.

    Example:
    >>> scraped_data = scrape_games_in_tournament()
    >>> print(scraped_data.head())
         map         agents match_id game_id
    0    Map1    Character1  123456   789012
    1    Map1    Character2  123456   789012
    2    Map1    Character3  123456   789012
    ...  ...     ...         ...      ...
    """
    df = pd.DataFrame()
    
    match_ids = scrape_tournament(tournament_url)
    
    for n, match_id in enumerate(match_ids, start = 1):
        print(f'Scraping match {n} of {len(match_ids)}.')
        match_url = f'https://www.vlr.gg/{match_id}' 
        
        match_soup, game_ids = scrape_match(match_url)
        
        for game_id in game_ids:
            map_title, characters = scrape_game(match_soup, game_id)
            
            match_list = [match_id] * len(characters)
            game_list = [game_id] * len(characters)
    
            game_df = pd.DataFrame({'map': map_title, 'agents': characters, 'match_id': match_list, 'game_id': game_list})
            df = df.append(game_df)

        time.sleep(2)
    
    return df


# In[7]:


#tournament_df = scrape_games_in_tournament()


# In[8]:


#tournament_df.to_csv('valorant_champions_2023_agent_picks.csv')


# In[9]:


df = pd.read_csv('valorant_champions_2023_agent_picks.csv')


# In[10]:


df['match_id'] = df['match_id'].astype('str')
df['game_id'] = df['game_id'].astype('str')


# In[11]:


agent_colors = {'Viper':'#2A4334',
                'Breach':'#8B4C31',
                'Astra': '#7E24D6',
                'Neon': '#566AAF',
                'Sova': '#223773',
                'Killjoy': '#F5CE2C',
                'Raze': '#F8A83E',
                'Fade': '#1E1F2C',
                'Omen': '#7577AF',
                'Chamber': '#A77E58',
                'Skye': '#628C66',
                'Brimstone': '#7F3319',
                'Kayo': '#13208F',
                'Jett': '#B7D2DA',
                'Harbor': '#0C8C74',
                'Gekko': '#C2ED57',
                'Sage': '#D9CFD8',
                'Yoru': '#3D498D',
                'Cypher': '#9B664B',
                'Phoenix': '#E58B47',
                'Reyna': '#7B3675'}


# In[12]:


df['color'] = df['agents'].map(agent_colors)


# In[13]:


df.head()


# # Dashboard

# In[14]:


import plotly.graph_objects as go
import plotly.express as px
import plotly.offline as pyo
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output


# ## Styles

# In[15]:


SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '30%',
    'padding': '1rem 1rem 2rem',
    'background-color': '#0A0E13',
    'margin-right': '15px',
    'color': '#FFFFFF',
    'font-family': 'arial'
}

GRAPH_STYLE = {'width': '68.2%',  
               'position': 'fixed', 
               'height': '100%', 
               'top': 0, 
               'bottom': 0, 
               'right': 0
               }

PLOT_LAYOUT = go.Layout(title = dict(text = 'Valorant Champions 2023 - Agent Selection', font = dict(size = 20)),
                   xaxis = {'title': 'Agent Name', 'categoryorder': 'total descending'},
                   yaxis = {'title': 'Pick Count', 'gridcolor': '#FFFFFF'},
                   barmode = 'group',
                   plot_bgcolor = '#0A0E13',
                   paper_bgcolor = '#0A0E13',
                   font_color = '#FFFFFF',
                   font_family = 'Arial')


# ## Dashboard Components

# In[16]:


#Plotly Chart
data = [go.Histogram(x = df['agents'], y = df['game_id'])]
layout = go.Layout(title = 'Valorant Champions 2023 - Agent Pickrate',
                   xaxis = {'title': 'Agent Name', 'categoryorder': 'total descending'},
                   yaxis = {'title': 'Pick Count'},
                   barmode = 'group')


# In[17]:


map_options = [{'label': loc, 'value': loc} for loc in df['map'].unique()]
map_options.append({'label': 'All Maps', 'value': 'All Maps'})


# In[18]:


#Map Select
dropdown = dcc.Dropdown(id = 'map-picker', options = map_options, value = 'All Maps', style = {'color':'#000000'})


# In[19]:


#Image 
img = 'assets/valorant-logo_resized.png'


# In[20]:


#Sidebar
sidebar = html.Div([
    html.Img(src=img),
    html.H2('Filters'),
    html.Hr(),
    html.P('Select A Map:'),
    dbc.Nav(
        [dropdown],
        vertical = True,
        pills = True)
    ],
    style = SIDEBAR_STYLE
)


# ## Run Dashboard

# In[21]:


app = dash.Dash()


# In[22]:


app.layout = html.Div(children = [
                dbc.Row(
                    [dbc.Col(sidebar),
                    dbc.Col(dcc.Graph(id = 'bar', style = GRAPH_STYLE))
                    ])
    ]
)

if __name__ == '__main__':
    app.run_server(jupyter_mode = 'external', debug = 'True')


# In[23]:


@app.callback(Output('bar','figure'), [Input('map-picker','value')])
def update_map(selected_map):
    if selected_map == 'All Maps' or selected_map == None:
        data = [go.Histogram(x = df['agents'],
                            y = df['game_id'],
                            marker = {'color':'#FF4655'})]
                        
    else:
        filtered_df = df.loc[df['map'] == selected_map]
        data = [go.Histogram(x = filtered_df['agents'],
                        y = filtered_df['game_id'],
                            marker = {'color':'#FF4655'})]
        
    fig = {'data': data,
           'layout': PLOT_LAYOUT}
    
    return fig

