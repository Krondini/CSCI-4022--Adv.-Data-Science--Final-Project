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
def getUserSummary(steamid: str):

    key = '67651BAD4657CA147D02F2C879D4B287'
    userSummary = requests.get("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key="+key+"&steamids="+steamid).json()
    userName = userSummary['response']['players'][0]['personaname']

    # Collect all games ever played by user
    # Then sort by most play time, forever
    ownedGames = requests.get("http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key="+key+"&steamid="+steamid+"&format=json").json()['response']['games']
    ownedGames = sorted(ownedGames, key= lambda game: game["playtime_forever"], reverse=True)
    
    return (userName, ownedGames)


def getUserInfo(): 
    
    key = '67651BAD4657CA147D02F2C879D4B287' #API key
    cats_steam_id = "76561198272988632" #Cat's Steam ID, used as a starting point for useer gathering
    entry_link = "http://api.steampowered.com/ISteamUser/"
    
    friendslist = requests.get(entry_link+"GetFriendList/v0001/?key="+key+"&steamid="+cats_steam_id+"&relationship=friend")
    my_summary = requests.get(entry_link+"GetPlayerSummaries/v0002/?key="+key+"&steamids="+cats_steam_id)
    
    friend1 = friendslist.json()['friendslist']['friends'][0]
    friend1_id = friend1['steamid']
    userName, userGames = getUserSummary(friend1_id)
    return (userName, userGames)