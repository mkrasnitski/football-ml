import requests
import operator
import pandas as pd
from bs4 import BeautifulSoup as bsoup, Comment, SoupStrainer
from AsyncRequests import async_get
from dataclasses import dataclass
from teams import teams

@dataclass(repr=False)
class Game:
	stats: pd.DataFrame()

	def __post_init__(self):
		self.tie = len(self.stats['Score'].unique()) == 1
		self.winner = None
		if not self.tie:
			self.winner = self.stats['Score'].idxmax()

	def __repr__(self):
		return f'Game(teams={list(map(str, self.stats.index))}, tie={self.tie}, winner={self.winner})'

year = 2018
base_url = 'https://www.pro-football-reference.com'
urls = [f'{base_url}/years/{year}/week_{w}.htm' for w in range(1, 18)]

game_urls = []

for response in async_get(urls, num_workers=17, verbose=1):
	soup = bsoup(response.content.decode('utf-8'), 'lxml')
	games = soup.findAll('div', 'game_summary')
	for game_table in games:
		game_urls.append(base_url + game_table.find('td', 'gamelink').find('a')['href'])

game_stats = []

for i, response in enumerate(async_get(game_urls[:10], verbose=1)):
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
	print(row_names)

	df = pd.DataFrame(index = list(map(teams.__getitem__, row_names)))
	for name, score in zip(names, scores):
		df.loc[teams[name], 'Score'] = score

	col_names = ['First Downs', 'Sacked-Yards', 'Total Yards', 'Turnovers', 'Third Down Conv.']
	for row in stats_table.find('tbody').findAll('tr'):
		col_name = row.find('th').text
		if col_name in col_names:
			df[col_name] = [cell.text for cell in row.findAll('td')]
	df.rename(columns={'Sacked-Yards': 'Sacks', 'Third Down Conv.': 'Third Down Rate'}, inplace=True)
	df['Sacks'] = list(reversed(df['Sacks'].str.split('-', expand=True)[0]))
	third_down = df['Third Down Rate'].str.split('-', expand=True).astype(int)
	df['Third Down Rate'] = third_down[0] / third_down[1]
	df[df.keys()[:-1]] = df[df.keys()[:-1]].astype(int)

	g = Game(df)
	game_stats.append(g.stats)

total_stats = pd.concat(game_stats)
for team in teams.values():
	print(team)
	print(total_stats.loc[team].to_string(index=False))
	# break