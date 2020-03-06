```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
import json
from datetime import timedelta

```


```python
### Get the team ID's

teams = requests.get('https://statsapi.web.nhl.com/api/v1/teams')
teams = teams.json()
```


```python
###Creates dictionary for team name and team code
teams_dict = {}
for t in range(len(teams['teams'])):
    team_id = teams['teams'][t]['id']
    team_name = teams['teams'][t]['name']
    teams_dict[team_id] = team_name
```


```python
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
```


```python
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

```


```python
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="specify_your_app_name_here")
from geopy import distance
#from geopy.extra.rate_limiter import RateLimiter
#geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.5)
```


```python
###Creates list of all rinks
rinks_list = []
for key, value in rink.items():
    for r in value: 
        if r not in rinks_list:
            rinks_list.append(r)
```


```python
### Gets the coordinates of each rink
rink_coords_dict = {}
for r in rinks_list:
    locate = geolocator.geocode(r, timeout=60)
    rink_coords = list(locate)[-1]
    rink_coords_dict[r] = rink_coords
```


```python
###Assigns rink coordinates for each game
travel_coords = {}

for key, value in rink.items():
    arena = []
    for v in value:
        if v in rink_coords_dict.keys():
            arena.append(rink_coords_dict[v])
            travel_coords[key] = arena
```


```python
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
            
```


```python
### Converting team id to team name
team_travel_distance = {}

for key, value in total_dist.items():
    if key in teams_dict.keys():
        team_distance = total_dist[key]
        team_name = teams_dict[key]
        team_travel_distance[team_name] = team_distance
```


```python
team_travel_distance
```




    {'New Jersey Devils': 31787.94013781389,
     'New York Islanders': 36946.45243089054,
     'New York Rangers': 35512.80774258749,
     'Philadelphia Flyers': 40108.30710664535,
     'Pittsburgh Penguins': 34444.88609402692,
     'Boston Bruins': 40059.08042283014,
     'Buffalo Sabres': 42851.190984440225,
     'Montréal Canadiens': 36613.52896330472,
     'Ottawa Senators': 37952.23354120721,
     'Toronto Maple Leafs': 36885.00708879774,
     'Carolina Hurricanes': 36342.98867025408,
     'Florida Panthers': 41566.097024963594,
     'Tampa Bay Lightning': 47524.23261230233,
     'Washington Capitals': 35248.063484113816,
     'Chicago Blackhawks': 45783.25008311031,
     'Detroit Red Wings': 40551.944438616636,
     'Nashville Predators': 43341.36249178383,
     'St. Louis Blues': 41563.2050845988,
     'Calgary Flames': 47158.0550426138,
     'Colorado Avalanche': 43136.137921805595,
     'Edmonton Oilers': 49731.73522576439,
     'Vancouver Canucks': 48839.83990810983,
     'Anaheim Ducks': 46027.929108769225,
     'Dallas Stars': 43162.66594924533,
     'Los Angeles Kings': 43922.619381945435,
     'San Jose Sharks': 47336.96805509882,
     'Columbus Blue Jackets': 36980.93778612777,
     'Minnesota Wild': 43133.70097518137,
     'Winnipeg Jets': 42459.98192955597,
     'Arizona Coyotes': 47957.84771068749,
     'Vegas Golden Knights': 42417.55329783478}




```python
##Creating a formatted time dictionary
formatted_time = {}

for key, value in time.items():
    format_times = []
    for v in value:
        v = datetime.strptime(v, "%Y-%m-%d")
        format_times.append(v)
    formatted_time[key] = format_times
```


```python
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
    
```


```python
back_to_back
```




    {1: 22,
     2: 22,
     3: 19,
     4: 23,
     5: 19,
     6: 19,
     7: 21,
     8: 17,
     9: 17,
     10: 15,
     12: 24,
     13: 17,
     14: 16,
     15: 20,
     16: 24,
     17: 20,
     18: 16,
     19: 19,
     20: 15,
     21: 16,
     22: 14,
     23: 16,
     24: 18,
     25: 17,
     26: 16,
     28: 10,
     29: 18,
     30: 15,
     52: 20,
     53: 20,
     54: 13}




```python
### Converting team id to team name
team_back_to_back = {}

for key, value in back_to_back.items():
    if key in teams_dict.keys():
        total_count = back_to_back[key]
        team_name = teams_dict[key]
        team_back_to_back[team_name] = total_count
```


```python
team_back_to_back
```




    {'New Jersey Devils': 22,
     'New York Islanders': 22,
     'New York Rangers': 19,
     'Philadelphia Flyers': 23,
     'Pittsburgh Penguins': 19,
     'Boston Bruins': 19,
     'Buffalo Sabres': 21,
     'Montréal Canadiens': 17,
     'Ottawa Senators': 17,
     'Toronto Maple Leafs': 15,
     'Carolina Hurricanes': 24,
     'Florida Panthers': 17,
     'Tampa Bay Lightning': 16,
     'Washington Capitals': 20,
     'Chicago Blackhawks': 24,
     'Detroit Red Wings': 20,
     'Nashville Predators': 16,
     'St. Louis Blues': 19,
     'Calgary Flames': 15,
     'Colorado Avalanche': 16,
     'Edmonton Oilers': 14,
     'Vancouver Canucks': 16,
     'Anaheim Ducks': 18,
     'Dallas Stars': 17,
     'Los Angeles Kings': 16,
     'San Jose Sharks': 10,
     'Columbus Blue Jackets': 18,
     'Minnesota Wild': 15,
     'Winnipeg Jets': 20,
     'Arizona Coyotes': 20,
     'Vegas Golden Knights': 13}




```python
distances_traveled = pd.Series(team_travel_distance)
back_to_back_games = pd.Series(team_back_to_back)
```


```python
df = pd.concat([distances_traveled, back_to_back_games], axis=1)
```


```python
pd.options.display.float_format = '{:,.2f}'.format
```


```python
df.columns = ['Miles Traveled', 'Back to Back Games']
```


```python
df.sort_values(by='Miles Traveled', ascending = False, inplace=True)
```


```python
df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Miles Traveled</th>
      <th>Back to Back Games</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Edmonton Oilers</td>
      <td>49,731.74</td>
      <td>14</td>
    </tr>
    <tr>
      <td>Vancouver Canucks</td>
      <td>48,839.84</td>
      <td>16</td>
    </tr>
    <tr>
      <td>Arizona Coyotes</td>
      <td>47,957.85</td>
      <td>20</td>
    </tr>
    <tr>
      <td>Tampa Bay Lightning</td>
      <td>47,524.23</td>
      <td>16</td>
    </tr>
    <tr>
      <td>San Jose Sharks</td>
      <td>47,336.97</td>
      <td>10</td>
    </tr>
    <tr>
      <td>Calgary Flames</td>
      <td>47,158.06</td>
      <td>15</td>
    </tr>
    <tr>
      <td>Anaheim Ducks</td>
      <td>46,027.93</td>
      <td>18</td>
    </tr>
    <tr>
      <td>Chicago Blackhawks</td>
      <td>45,783.25</td>
      <td>24</td>
    </tr>
    <tr>
      <td>Los Angeles Kings</td>
      <td>43,922.62</td>
      <td>16</td>
    </tr>
    <tr>
      <td>Nashville Predators</td>
      <td>43,341.36</td>
      <td>16</td>
    </tr>
    <tr>
      <td>Dallas Stars</td>
      <td>43,162.67</td>
      <td>17</td>
    </tr>
    <tr>
      <td>Colorado Avalanche</td>
      <td>43,136.14</td>
      <td>16</td>
    </tr>
    <tr>
      <td>Minnesota Wild</td>
      <td>43,133.70</td>
      <td>15</td>
    </tr>
    <tr>
      <td>Buffalo Sabres</td>
      <td>42,851.19</td>
      <td>21</td>
    </tr>
    <tr>
      <td>Winnipeg Jets</td>
      <td>42,459.98</td>
      <td>20</td>
    </tr>
    <tr>
      <td>Vegas Golden Knights</td>
      <td>42,417.55</td>
      <td>13</td>
    </tr>
    <tr>
      <td>Florida Panthers</td>
      <td>41,566.10</td>
      <td>17</td>
    </tr>
    <tr>
      <td>St. Louis Blues</td>
      <td>41,563.21</td>
      <td>19</td>
    </tr>
    <tr>
      <td>Detroit Red Wings</td>
      <td>40,551.94</td>
      <td>20</td>
    </tr>
    <tr>
      <td>Philadelphia Flyers</td>
      <td>40,108.31</td>
      <td>23</td>
    </tr>
    <tr>
      <td>Boston Bruins</td>
      <td>40,059.08</td>
      <td>19</td>
    </tr>
    <tr>
      <td>Ottawa Senators</td>
      <td>37,952.23</td>
      <td>17</td>
    </tr>
    <tr>
      <td>Columbus Blue Jackets</td>
      <td>36,980.94</td>
      <td>18</td>
    </tr>
    <tr>
      <td>New York Islanders</td>
      <td>36,946.45</td>
      <td>22</td>
    </tr>
    <tr>
      <td>Toronto Maple Leafs</td>
      <td>36,885.01</td>
      <td>15</td>
    </tr>
    <tr>
      <td>Montréal Canadiens</td>
      <td>36,613.53</td>
      <td>17</td>
    </tr>
    <tr>
      <td>Carolina Hurricanes</td>
      <td>36,342.99</td>
      <td>24</td>
    </tr>
    <tr>
      <td>New York Rangers</td>
      <td>35,512.81</td>
      <td>19</td>
    </tr>
    <tr>
      <td>Washington Capitals</td>
      <td>35,248.06</td>
      <td>20</td>
    </tr>
    <tr>
      <td>Pittsburgh Penguins</td>
      <td>34,444.89</td>
      <td>19</td>
    </tr>
    <tr>
      <td>New Jersey Devils</td>
      <td>31,787.94</td>
      <td>22</td>
    </tr>
  </tbody>
</table>
</div>




```python

```


```python

```
