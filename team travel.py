#!/usr/bin/env python
# coding: utf-8

# In[313]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
import json
from datetime import datetime
from datetime import timedelta
from pandas.io.json import json_normalize


# In[4]:


### Get the team ID's

teams = requests.get('https://statsapi.web.nhl.com/api/v1/teams')
teams = teams.json()


# In[19]:


###Creates dictionary for team name and team code
teams_dict = {}
for t in range(len(teams['teams'])):
    team_id = teams['teams'][t]['id']
    team_name = teams['teams'][t]['name']
    teams_dict[team_id] = team_name


# In[23]:


### Gather game codes for each team
codes_dict = {}

for key,value in teams_dict.items():
    url = 'https://statsapi.web.nhl.com/api/v1/schedule?season=20192020&teamId=' + str(key)
    game_codes = requests.get(url)
    game_codes= game_codes.json()
    
    
    code_list = []
    for g in range(len(game_codes['dates'])):
        if game_codes['dates'][g]['games'][0]['gameType'] == 'R':
            game_code = game_codes['dates'][g]['games'][0]['gamePk']
            code_list.append(game_code)
            codes_dict[key] = code_list


# In[46]:


### Gather rink and time data
rink = {}
city = {}
time = {}

for key,value in codes_dict.items():
    
    gametime_list = []
    game_location_list = []
    game_city_list = []
    
    for c in value: 
        url =  "https://statsapi.web.nhl.com/api/v1/game/" + str(c) + "/feed/live"
        game_info = requests.get(url)
        game_info = game_info.json()
        gametime = game_info['gameData']['datetime']['dateTime']
        gametime = gametime.split("T")[0]
        
        gametime_list.append(gametime)
        time[key] = gametime_list


        game_location = game_info['gameData']['venue']['name']        
        if game_location == 'NYCB Live/Nassau Coliseum':
            game_location = 'Nassau Coliseum'
        game_location_list.append(game_location)
        rink[key] = game_location_list


        game_city = game_info['gameData']['teams']['home']['locationName']
        game_city_list.append(game_city)
        city[key] = game_city_list


# In[132]:


from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="specify_your_app_name_here")
from geopy import distance
from geopy.extra.rate_limiter import RateLimiter
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.5)


# In[166]:


###Creates list of all rinks
rinks_list = []
for key, value in rink.items():
    for r in value: 
        if r not in rinks_list:
            rinks_list.append(r)


# In[169]:


### Gets the coordinates of each rink
rink_coords_dict = {}
for r in rinks_list:
    locate = geolocator.geocode(r, timeout=60)
    rink_coords = list(locate)[-1]
    rink_coords_dict[r] = rink_coords


# In[193]:


###Assigns rink coordinates for each game
travel_coords = {}

for key, value in rink.items():
    arena = []
    for v in value:
        if v in rink_coords_dict.keys():
            arena.append(rink_coords_dict[v])
            travel_coords[key] = arena


# In[194]:


travel_coords


# In[201]:


###Calculates total distance of each team
total_dist = {}
for key, value in travel_coords.items():
    start = 0
    stop = 1
    total_distance = 0 
    
    for v in value:
        if stop < len(value):
            game_one = value[start]
            game_two = value[stop]
            start += 1
            stop += 1
        travel_distance = (distance.distance(game_one,game_two).miles) 
        total_distance += travel_distance
            
    total_dist[key] = total_distance
            


# In[206]:


### Converting team id to team name
team_travel_distance = {}

for key, value in total_dist.items():
    if key in teams_dict.keys():
        team_distance = total_dist[key]
        team_name = teams_dict[key]
        team_travel_distance[team_name] = team_distance


# In[209]:


team_travel_distance


# In[272]:


formatted_time = {}

for key, value in time.items():
    format_times = []
    for v in value:
        v = datetime.strptime(v, "%Y-%m-%d")
        format_times.append(v)
    formatted_time[key] = format_times


# In[273]:


###Calculates the number of back to back games
back_to_back = {}


for key, value in formatted_time.items():
    start = 0
    stop = 1
    back_to_back_games = 0 
    
    for v in value:
        if stop < len(value):
            game_one = value[start]
            game_two = value[stop]
            start += 1
            stop += 1
            time_between = game_two - game_one
            time_between = str(time_between)
            if time_between == '1 day, 0:00:00':
                back_to_back_games +=1
    
    back_to_back[key] = back_to_back_games
    


# In[270]:


back_to_back


# In[274]:


### Converting team id to team name
team_back_to_back = {}

for key, value in back_to_back.items():
    if key in teams_dict.keys():
        total_count = back_to_back[key]
        team_name = teams_dict[key]
        team_back_to_back[team_name] = total_count


# In[275]:


team_back_to_back


# In[277]:


distances_traveled = pd.Series(team_travel_distance)
back_to_back_games = pd.Series(team_back_to_back)


# In[278]:


df = pd.concat([distances_traveled, back_to_back_games], axis=1)


# In[294]:


pd.options.display.float_format = '{:,.2f}'.format


# In[296]:


df.columns = ['Miles Traveled', 'Back to Back Games']


# In[301]:


df.sort_values(by='Miles Traveled', ascending = False, inplace=True)


# In[302]:


df


# In[ ]:





# In[ ]:




