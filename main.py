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


### TODO!!!
def addRowToDF(receiving_df: pd.DataFrame, giving_df: pd.DataFrame, friend) -> pd.DataFrame:

	userName, userId, userGames = friend
	new_row = formRow(userName, userGames, giving_df)
	if new_row['User'].isin(receiving_df):
		return receiving_df

	receiving_df = receiving_df.append(new_row, ignore_index=True)
	receiving_df['User'].iloc[-1] = userName
	
	minutes_total = np.sum(new_row[1:])
	hours_total = minutes_total/60
	days_total = hours_total/24
	years_total = days_total/365
	
	print("User: \'{}\' has a total of: {} minutes of gaming on steam.".format(userName, minutes_total))
	print("This is equivalent to {:.2f} total hours of gaming.".format(hours_total))
	print("{:.2f} days of playing.".format(days_total))
	print("Or even {:.4f} years of playing... nerrrrrd!".format(years_total))

	return receiving_df
### TODO!!!


def main():

	game_df = pd.read_csv("data/steam.csv") # Read in data
	game_ids = game_df['appid'].to_numpy() # Obtain app-ids for later

	# print("Head of data set:\n{}\n\n".format(game_df.head()))
	
	reduced_df = None
	
	# reduced_df = SVD.runSVD(df) #Later Task: Implement Singular Value Decomposition to reduce cols in DataFrame
	if not reduced_df: #To be used while we work on the SVD implementation
		pass

	else: #To be used once the SVD implementation is finished	
		pass

	# game1 = userGames[0]
	# print(game1)
	
	user_df = pd.DataFrame([], columns=["User"]+list(game_ids))
	firendsList = getUsers.getUserInfo()

	#-----------------Stopping Point------------------#

	user_df = addRowToDF(user_df, game_df, firendsList[0])
		


	# print(user_df.head())

	

if __name__ == '__main__':
	main()