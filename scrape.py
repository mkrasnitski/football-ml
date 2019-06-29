import requests
import operator
import pandas as pd
from bs4 import BeautifulSoup as bsoup
from AsyncRequests import async_get
from dataclasses import dataclass
from teams import teams

@dataclass
class Game:
	score_info: dict
	winner: str = None
	tie: bool = False

	def __post_init__(self):
		self.tie = len(set(self.score_info.values())) == 1
		if not self.tie:
			self.winner = max(self.score_info, key=self.score_info.get)
		

year = 2018
base_url = 'https://www.pro-football-reference.com'
urls = [f'{base_url}/years/{year}/week_{w}.htm' for w in range(1, 18)]

game_urls = []

for response in async_get(urls, num_workers=17, verbose=0):
	soup = bsoup(response.content.decode('utf-8'), 'lxml')
	games = soup.findAll('div', 'game_summary')
	for game_table in games:
		game_urls.append(base_url + game_table.find('td', 'gamelink').find('a')['href'])
	break

for response in async_get(game_urls, verbose=0):
	soup = bsoup(response.content.decode('utf-8'), 'lxml')
	scorebox = soup.find('div', 'scorebox')
	names = []
	scores = []
	for name in scorebox.findAll('strong'):
		link = name.find('a')
		if link: 
			names.append(link.text)
	for score in scorebox.findAll('div', 'score'):
		scores.append(score.text)

	score_info = dict(zip(map(teams.get, names), scores))
	print(Game(score_info))