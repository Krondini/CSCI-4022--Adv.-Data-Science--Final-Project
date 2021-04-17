'''
File Purpose: Use Steam API to get a set of users to be used in the item recommendation system
Suggested API: ISteamUser -> https://steamcommunity.com/dev
'''
import requests

'''
Run API call to get list of users with their full game libraries
NOTE: We're using a static data set (steam.csv) along with a dynamically 
    obtained set of users. These two lists will undoubtedly have dimension mismatches.
    We will correct that in main.py
'''
def getUserInfo(): 
    
    key = '67651BAD4657CA147D02F2C879D4B287'
    cats_steam_id = "76561198272988632"
    entry_link = "http://api.steampowered.com/ISteamUser/"
    friendslist = requests.get(entry_link+"GetFriendList/v0001/?key="+key+"&steamid="+cats_steam_id+"&relationship=friend")
    # print(len(friendslist.json()['friendslist']["friends"]))
    my_summary = requests.get(entry_link+"GetPlayerSummaries/v0002/?key="+key+"&steamids="+cats_steam_id)
    print(my_summary.json())