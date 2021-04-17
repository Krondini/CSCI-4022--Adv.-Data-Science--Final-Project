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

def main():
    df = pd.read_csv("data/steam.csv")
    game_names = df['name'].to_numpy()
    reduced_df = None
    # reduced_df = SVD.runSVD(df) #TODO: Implement Singular Value Decomposition to reduce cols in DataFrame
    if not reduced_df: #To be used while we work on the SVD implementation
        pass

    else: #To be used once the SVD implementation is finished
        pass

    getUsers.getUserInfo()


if __name__ == '__main__':
    main()