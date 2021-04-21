'''
Authors: Konlan Rondini & Gavin Zimmermann
File Purpose: Starting point for running recommendation system

Given a new user and their current Steam library, return a list of 
recommended games for the user to consider buying
'''

import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import SVD
import getUsers
import findRecs

def formRow(username: str, games: list, df: pd.DataFrame) -> pd.Series:

    row = pd.Series(np.zeros(len(df))) #Initialize row of playtime to be all zero

    for game in games: #Iterate over user's games
        game_id = game['appid']
        df_index = df.index[df['appid'] == game_id]
        if len(df_index) == 0: #Skip games with no info in dataset
            continue
        df_index = df_index[0] #Only one number in list at this point, just want it not the whole list
        row[df_index] = game['playtime_forever']

    return row

def main():
    game_df = pd.read_csv("data/steam.csv")
    game_ids = game_df['appid'].to_numpy()
    print("Head of data set:\n{}\n\n".format(game_df.head()))
    reduced_df = None
    # reduced_df = SVD.runSVD(df) #TODO: Implement Singular Value Decomposition to reduce cols in DataFrame
    if not reduced_df: #To be used while we work on the SVD implementation
        pass

    else: #To be used once the SVD implementation is finished
        pass

    userName, userGames = getUsers.getUserInfo()
    game1 = userGames[0]
    print(game1)
    user_df = pd.DataFrame([], columns=["User"]+list(game_ids))
    
    new_row = formRow(userName, userGames, game_df)
    minutes_total = np.sum(new_row)
    hours_total = minutes_total/60
    days_total = hours_total/24
    years_total = days_total/365
    print("User: \'{}\' has a total of: {} minutes of gaming on steam.".format(userName, minutes_total))
    print("This is equivalent to {} total hours of gaming.".format(hours_total))
    print("{:.2f} days of playing.".format(days_total))
    print("Or even {:.4f} years of playing... nerrrrrd!".format(years_total))

if __name__ == '__main__':
    main()