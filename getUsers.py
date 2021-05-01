'''
File Purpose: Use Steam API to get a set of users to be used in the item recommendation system
Suggested API: ISteamUser -> https://steamcommunity.com/dev
'''
import requests
import os
import numpy as np

import json
import pycurl
import time
from io import BytesIO

pyC = pycurl.Curl()

key = '67651BAD4657CA147D02F2C879D4B287'

requests = 0
'''
APICALL - Wrapper Function for making API requests using pycurl and json libraries
'''
def APICall(url):
    global requests
    resbuff = BytesIO()
    pyC.setopt(pyC.WRITEDATA, resbuff)
    pyC.setopt(pyC.URL,url)
    pyC.perform()
    response = str(resbuff.getvalue().decode('utf-8'))
    if ("Bad Request" in response):
        return 0
    elif ("Error" in response):
        raise Exception('API call experienced error\nRequest:\n{}\n\nResponse:\n{}'.format(url, response))
    requests +=1
    return json.loads(response)
        
    

'''
Run API call to get list of users with their full game libraries
NOTE: We're using a static data set (steam.csv) along with a dynamically 
    obtained set of users. These two lists will undoubtedly have dimension mismatches.
    We will correct that in main.py
'''
def getUserSummary(steamid: str):
    userSummary = requests.get("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key="+key+"&steamids="+steamid).json()
    userName = userSummary['response']['players'][0]['personaname']

    # Collect all games ever played by user
    # Then sort by most play time, forever
    ownedGames = requests.get("http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key="+key+"&steamid="+steamid+"&format=json").json()['response']['games']
    ownedGames = sorted(ownedGames, key= lambda game: game["playtime_forever"], reverse=True)
    
    # os.system('clear')
    # print("User: {} (#{}) owns {} games".format(userName, steamid, len(ownedGames)))
    
    # input("> ")

    return (userName, ownedGames)


'''
getUserFriends - Retrieves a user's friend list is user profile is public
'''
def getUserFriends(steamid: str): 
    friends_list = np.array([])
    
    friends_res = APICall("{}{}/?{}={}&{}={}&{}={}".format(
        'http://api.steampowered.com/ISteamUser/', 'GetFriendList/v0001', 
        'key', key,
        'steamid', steamid,
        'relationship', 'all')
    )
    if not ((friends_res) and 
            ('friendslist' in friends_res) and 
            ('friends' in friends_res['friendslist'])):
        return friends_list
        
    for user in friends_res['friendslist']['friends']:
        if ('steamid' in user) and type(user['steamid']==str):
            friends_list = np.append(friends_list, user['steamid'])
    
    return friends_list
    

'''
buildUserListFrom - Develops a list of players 
    @ param streamids - Players to grab friend's list from to build a large list of users
    @ param n - Number of users to stop build at
    @ returns - List of Stream Ids
'''
def buildUserListFrom(steamids: (str or np.ndarray), n: int = 1000):
    users = np.array([steamids]) if type(steamids)==str else np.array(steamids)
    
    user_count = 0 # A counter for which user additional users are grabbed from on an growing user stack
    while (user_count<len(users) and len(users)<n):
        users = np.unique(np.append(users, getUserFriends(users[user_count])))
        user_count+=1
    
    return users[:min(len(users),n)]
        


'''
getUserGames - Performs bulk requests on a list of users, getting game relevant data
    @ param steamids - Steam ids to request game data on
    @ param verbose - Prints the current game data loaded
    @ return - Returns an array of tuples (game id, hours played)
'''

def getUserGames(steamids: np.ndarray, cacheto: str = None, verbose: bool = False):
    out = None
    if (cacheto):
        out = open(cacheto, 'w')
    else:
        out = {}
    
    count, n, verb_chpt = 0, len(steamids), max(100, int(.05*len(steamids)))
    for steamid in steamids:
        # Allow verbose comments to show progress on requests (since there are a lot)
        if verbose and count%verb_chpt==0 and count>0:
            print("Grabbed {}/{} users' libraries".format(count, n))
        
        # Make call
        res = APICall("{}{}/?{}={}&{}={}&{}={}".format(
            'http://api.steampowered.com/IPlayerService/', 'GetOwnedGames/v0001', 
            'key', key,
            'steamid', steamid,
            'include_played_free_games', '1')
        )
        
        # Error checking
        if not ((res) and 
                ('response' in res) and 
                ('games' in res['response'])):
            continue
        
        # Parse data for only relevant info
        game_data = []
        for game in res['response']['games']:
            app_time_tup = (game['appid'], game['playtime_forever'])
            game_data += [app_time_tup]
        
        if (cacheto):
            out.write("{}, {}\n".format(steamid, json.dumps(game_data)))
        else:
            out[steamid] = game_data
    
    if (cacheto):
        out.close()
    else:
        return out
    
