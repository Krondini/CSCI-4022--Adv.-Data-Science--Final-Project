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
from os import path, chdir
from json import loads

def formRow(username: str, games: np.ndarray, df: pd.DataFrame) -> pd.Series:

	dict_form = {"User": username}
	for game in games: #Iterate over user's games
		game_id = game[0]
		playtime = game[1]
		dict_form[game_id] = playtime

	df = df.append(dict_form, ignore_index=True).fillna(0)

	return df


# "76561198272988632"
def main():

	user_steamid = input("Please enter your Steam ID: ")
	game_df = pd.read_csv("data/steam.csv") # Read in data
	game_ids = game_df['appid'].to_numpy() # Obtain app-ids for later

	
	user_df = pd.DataFrame([], columns=["User"]+list(game_ids))
	firendsList = getUsers.getUserFriends(user_steamid) # Get friends starting from origin point


	users = getUsers.buildUserListFrom(user_steamid, 1000)
	
	if not path.exists("data/games.csv"):
		chdir('data')
		getUsers.getUserGames(users, "games.csv", True)
		chdir('..')

	if not path.exists("data/users_full.csv"):

		chdir('data')
		fo = open("games.csv")
		lines = fo.readlines()
		num_exec = len(lines)
		print("Executing {} total additions to DataFrame".format(num_exec))
		fo.close()
		for line in lines:

			if num_exec%10 == 0:
				print("{} additions remaining".format(num_exec))

			line = line.strip().split(', ', 1)
			games = np.array(loads(line[1]))
			user_df = formRow(line[0], games, user_df)
			num_exec -= 1
	
		user_df.to_csv("users_full.csv", index=False)
		chdir('..')

	user_df = pd.read_csv('data/users_full.csv')
	user_id = user_steamid
	this_user_games = getUsers.getUserSummary(user_id)[1]
	
	this_user_dict = {"User": user_id}
	for game in this_user_games:

		this_user_dict[game['appid']] = game['playtime_forever']
	
	user_df = user_df.append(this_user_dict, ignore_index=True).fillna(0)
	
	match = None
	match_df = None

	while match_df == None:
		match = findRecs.findBestMatch(user_df)
		match_df = getUsers.getUserSummary(str(match['User']))
		user_df = user_df[user_df['User'] != match['User']]


	compare_user_dict = {"User": str(match['User'])}
	for game in match_df[1]:

		compare_user_dict[game['appid']] = game['playtime_forever']

	my_df = pd.DataFrame([], columns=["User"]+list(game_ids))
	my_df = my_df.append(this_user_dict, ignore_index=True).fillna(0)
	them_df = pd.DataFrame([], columns=["User"]+list(game_ids))
	them_df = them_df.append(compare_user_dict, ignore_index=True)
	new_games = findRecs.findRecs(my_df, them_df)
	print("Based on your friends list, we recommend the following games:")
	for game in new_games:
		print('\t', end='')
		print('[{}]'.format(findRecs.findGameFromID(game, match['User'])))

if __name__ == '__main__':
	main()