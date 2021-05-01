'''
Authors: Konlan Rondini & Gavin Zimmermann
File Purpose: Once we have obtained our list of users
    and our list of games, we can now run the actual recommendation system
'''
import numpy as np
import pandas as pd
import requests as req
from getUsers import key

def findRecs(my_games: pd.DataFrame, their_games: pd.DataFrame) -> str:
    
    me_modified = my_games.drop("User", axis=1)
    them_modified = their_games.drop("User", axis=1)
    
    them_modified = them_modified.loc[:, (them_modified != 0).any(axis=0)]
    for col in them_modified: #Iterate over columns of DataFrame

        if col not in me_modified.columns:
            continue

        if me_modified[col].all() != 0: # Drop columns if I have hours on game, we want new titles
            them_modified = them_modified.drop(col, axis=1)
            me_modified = me_modified.drop(col, axis=1)
            

    them_modified = them_modified.sort_values(by=0, axis=1, ascending=False)
    num_games_to_rec = int(input("How many new games would you like to see: "))


    return them_modified.columns[0:num_games_to_rec].tolist()

def findBestMatch(df: pd.DataFrame) -> pd.DataFrame:
    
    def mag(x: np.ndarray):
        return np.sqrt(np.sum(x**2))

    def cosine_sim(x: np.ndarray, y: np.ndarray):
        return np.sum(x*y)/(mag(x)*mag(y))


    modified_df = df.loc[:, (df != 0).any(axis=0)] # Remove columns of all 0s, not getting info from that
    curr_user = modified_df.iloc[-1].to_numpy()
    modified_df = modified_df.drop(df.tail(1).index)

    closest_user_dist = 1000
    closest_user = None

    curr_user_games = curr_user[1:]
    for index, row in modified_df.iterrows():

        compare_user = row.to_numpy()[1:]
        user_dist = cosine_sim(curr_user_games, compare_user)
        if np.abs(user_dist - closest_user_dist) < closest_user_dist:

            closest_user_dist = user_dist
            closest_user = row
    return row


def findGameFromID(appid: int, steamid: int):
    games_lst = req.get("http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key="+key+"&steamid="+str(steamid)+"&include_appinfo=true&format=json").json()['response']['games']
    
    game_name = "this is returned"
    for game in games_lst:
        if game['appid'] == appid:
            game_name = game['name']
            break
    
    return game_name