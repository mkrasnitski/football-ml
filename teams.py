import pandas as pd
from dataclasses import dataclass

@dataclass
class Team:
	name: str
	stats: pd.DataFrame = pd.DataFrame()

	def __hash__(self):
		return hash(self.name)

	def __repr__(self):
		return f'Team(name={self.name})'

class TeamDictionary:
	team_names = {
		'ARI': 'Arizona Cardinals', 'ATL': 'Atlanta Falcons', 'BAL': 'Baltimore Ravens', 'BUF': 'Buffalo Bills',
		'CAR': 'Carolina Panthers', 'CHI': 'Chicago Bears', 'CIN': 'Cincinnati Bengals', 'CLE': 'Cleveland Browns',
		'DAL': 'Dallas Cowboys', 'DEN': 'Denver Broncos', 'DET': 'Detroit Lions', 'GB': 'Green Bay Packers',
		'HOU': 'Houston Texans', 'IND': 'Indianapolis Colts', 'JAX': 'Jacksonville Jaguars', 'KC': 'Kansas City Chiefs',
		'LAC': 'Los Angeles Chargers', 'LAR': 'Los Angeles Rams', 'MIA': 'Miami Dolphins', 'MIN': 'Minnesota Vikings',
		'NE': 'New England Patriots', 'NO': 'New Orleans Saints', 'NYG': 'New York Giants', 'NYJ': 'New York Jets',
		'OAK': 'Oakland Raiders', 'PHI': 'Philadelphia Eagles', 'PIT': 'Pittsburgh Steelers', 'SEA': 'Seattle Seahawks',
		'SF': 'San Francisco 49ers', 'TB': 'Tampa Bay Buccaneers', 'TEN': 'Tennessee Titans', 'WAS': 'Washington Redskins',
	}

	def __init__(self):
		self.teams = {}
		for team in self.team_names.values():
			self.teams[team] = Team(team)

	def __getitem__(self, value):
		if value in self.team_names.keys():
			return self.teams[self.team_names[value]]
		elif value in self.team_names.values():
			return self.teams[value]
		else:
			raise KeyError(f'KeyError: {value}')

teams = TeamDictionary()