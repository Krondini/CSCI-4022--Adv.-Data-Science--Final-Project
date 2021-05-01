'''
File Purpose: Use Steam API to get a set of users to be used in the item recommendation system
Suggested API: ISteamUser -> https://steamcommunity.com/dev
'''
import requests as req
import os
import numpy as np

import json
import pycurl
import time
from io import BytesIO

pyC = pycurl.Curl()
KEY = '67651BAD4657CA147D02F2C879D4B287'

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
    elif ("Server Error" in response):
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
    userSummary = req.get("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key="+key+"&steamids="+steamid).json()
    userName = userSummary['response']['players'][0]['personaname']
    print(userName)

    # Collect all games ever played by user
    # Then sort by most play time, forever
    res = req.get("http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key="+key+"&steamid="+steamid+"&format=json").json()['response']
    if not res:
        return None
    ownedGames = res['games']
    ownedGames = sorted(ownedGames, key= lambda game: game["playtime_forever"], reverse=True)
    
    return (userName, ownedGames)


'''
getUserFriends - Retrieves a user's friend list is user profile is public
'''
def getUserFriends(steamid: str): 
    friends_list = np.array([])
    
    friends_res = APICall("{}{}/?{}={}&{}={}&{}={}".format(
        'http://api.steampowered.com/ISteamUser/', 'GetFriendList/v0001', 
        'key', KEY,
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
filterPrivateUsers() - Will remove 
'''
def filterPrivateUsers(steamids: np.ndarray):
    publicids=np.array([])
    
    for i in range(0, len(steamids), 100):
        ids = steamids[i : min(len(steamids), i+100)]
        ids_format = ','.join(ids)
        res = APICall("{}{}/?{}={}&{}={}".format(
            'http://api.steampowered.com/ISteamUser/', 'GetPlayerSummaries/v0002', 
            'key', KEY,
            'steamids', ids_format)
        )
        
        # Bulk grab player stats
        if not ((res) and 
                ('response' in res) and 
                ('players' in res['response'])):
            print("Encountered error")
            continue
        
        # Iterate over players to parse public accounts
        for user in res['response']['players']:
            # Quick check on accounts visibility status
            if not ('communityvisibilitystate' in user and user['communityvisibilitystate']>1):
                continue
            
            # Check if they are actually a public account (not just friends-only)
            game_res = APICall("{}{}/?{}={}&{}={}&{}={}".format(
                'http://api.steampowered.com/IPlayerService/', 'GetOwnedGames/v0001', 
                'key', KEY,
                'steamid', user['steamid'],
                'include_played_free_games', '1')
            )
            if not ((game_res) and 
                    ('response' in game_res) and 
                    ('games' in game_res['response'])):
                continue
            
            # Save game data in cache if it exists; and count this user towards public users in list
            cached_game_data[user['steamid']] = game_res
            publicids = np.append(publicids, user['steamid'])
    
    return publicids
    

'''
buildUserListFrom - Develops a list of players 
    @ param steamids - Players to grab friend's list from to build a large list of users
    @ param n - Number of users to stop build at
    @ returns - List of Steam Ids which are public
'''
def buildUserListFrom(steamids: (str or np.ndarray), n: int = 1000):
    users = np.array([steamids]) if type(steamids)==str else np.array(steamids)
    #publicusers = filterPrivateUsers(users)
    
    user_count = 0 # A counter for which user additional users are grabbed from on an growing user stack
    
    # Iterates over users, filtering out those with accounts which are public and will return game lists
    while (user_count<len(users) and len(users)<n):
        new = getUserFriends(users[user_count])
        #publicusers = np.unique(np.append(publicusers, filterPrivateUsers(new)))
        
        users = np.unique(np.append(users, new))
        user_count+=1
        
    return users[:min(len(users),n)]
    #return publicusers[:min(len(publicusers),n)]
        


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
        
    gamesnum_data = np.array([])
    
    count, n, verb_chpt = 0, len(steamids), min(1000, max(100, int(.05*len(steamids))))
    for steamid in steamids:
        # Allow verbose comments to show progress on requests (since there are a lot)
        if verbose and count%verb_chpt==0 and count>0:
            print("Grabbed {}/{} users' libraries".format(count, n))
        
        # Make call; Grab from cache if available and remove from cache; or send API request
        res = APICall("{}{}/?{}={}&{}={}&{}={}".format(
            'http://api.steampowered.com/IPlayerService/', 'GetOwnedGames/v0001', 
            'key', KEY,
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
        
        # Prepare for next iteration
        count+=1