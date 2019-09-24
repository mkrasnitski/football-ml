import requests
import operator
import pickle
import os
import pandas as pd
from bs4 import BeautifulSoup as bsoup, Comment, SoupStrainer
from dataclasses import dataclass
from AsyncRequests import async_get
from teams import teams

@dataclass(repr=False)
class Game:
	stats: pd.DataFrame()

	def __init__(self, stats):
		self.stats = stats
		teamA, teamB = self.stats.index
		self.results = pd.DataFrame(data=[[teamA, teamB, 0, 0]], columns=['teamA', 'teamB', 'A_win', 'B_win'])
		if len(self.stats['Score'].unique()) != 1:
			winner = self.stats['Score'].idxmax()
			if winner == teamA:
				self.results['A_win'] = 1
			else:
				self.results['B_win'] = 1

	def __repr__(self):
		return f'Game(teams={list(map(str, self.stats.index))}, tie={self.tie}, winner={self.winner})'

def scrape(year, verbose=1):
	base_url = 'https://www.pro-football-reference.com'
	urls = [f'{base_url}/years/{year}/week_{w}.htm' for w in range(1, 18)]

	game_urls = []

	for response in async_get(urls, num_workers=17, verbose=verbose):
		soup = bsoup(response.content.decode('utf-8'), 'lxml')
		games = soup.findAll('div', 'game_summary')
		for game_table in games:
			game_urls.append(base_url + game_table.find('td', 'gamelink').find('a')['href'])

	game_stats = []
	game_results = []
	responses = async_get(game_urls, num_workers=256, verbose=verbose)

	for i, response in enumerate(responses):
		print(f'Processing {str(i + 1).rjust(len(str(len(responses))))}/{len(responses)}', end='\r', flush=True)
		page = response.content.decode('utf-8')
		scorebox = bsoup(page, 'lxml', parse_only=SoupStrainer('div', 'scorebox'))
		names = []
		scores = []
		for name in scorebox.findAll('strong'):
			link = name.find('a')
			if link: 
				names.append(link.text)
		for score in scorebox.findAll('div', 'score'):
			scores.append(score.text)

		comment = bsoup(page, 'lxml', parse_only=SoupStrainer('div', {'id': 'all_team_stats'}))
		stats_table = bsoup(comment.find(text = lambda text: isinstance(text, Comment)), 'lxml')
		row_names = [head.text for head in stats_table.find('thead').findAll('th')[1:]]

		df = pd.DataFrame(index = list(map(teams.__getitem__, row_names)))
		for name, score in zip(names, scores):
			df.loc[teams[name], 'Score'] = score

		col_names = ['First Downs', 'Sacked-Yards', 'Total Yards', 'Turnovers', 'Third Down Conv.']
		for row in stats_table.find('tbody').findAll('tr'):
			col_name = row.find('th').text
			if col_name in col_names:
				df[col_name] = [cell.text for cell in row.findAll('td')]
		df.rename(columns={'Sacked-Yards': 'Sacks', 'Third Down Conv.': 'Third Down Rate', 'Total Yards': 'Yards'}, inplace=True)
		df['Sacks'] = list(reversed(df['Sacks'].str.split('-', expand=True)[0]))
		third_down = df['Third Down Rate'].str.split('-', expand=True).astype(int)
		df['Third Down Rate'] = third_down[0] / third_down[1]
		df[df.keys()[:-1]] = df[df.keys()[:-1]].astype(int)

		g = Game(df)
		game_stats.append(g.stats)
		game_results.append(g.results)
	print()

	for game in game_stats:
		for i, team in enumerate(game.index):
			team.offence_lst.append(game.iloc[[i]])
			team.defence_lst.append(game.iloc[[1 - i]])

	for team in teams.values():
		if team.offence_lst != []:
			team.raw_offence = pd.concat(team.offence_lst, ignore_index=True)
		if team.defence_lst != []:
			team.raw_defence = pd.concat(team.defence_lst, ignore_index=True)

	team_stats = []

	for team in teams.values():
		team_stats.append(team.calculate_stats())

	total_stats = pd.concat(team_stats, axis=1).T
	total_stats.index = teams.values()
	total_results = pd.concat(game_results, ignore_index=True, axis=0)
	
	if not os.path.exists(f'{year}'):
		os.makedirs(f'{year}')
	total_stats.to_csv(f'{year}/{year}_stats.csv')
	total_results.to_csv(f'{year}/{year}_results.csv', index=False)