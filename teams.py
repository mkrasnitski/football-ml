import pandas as pd
from dataclasses import dataclass

@dataclass
class Team:
	name: str

	def __post_init__(self):
		self.offence_lst = []
		self.defence_lst = []
		self.raw_offence = pd.DataFrame()
		self.raw_defence = pd.DataFrame()

	def calculate_stats(self):
		stats = pd.Series()
		for side in ['offence', 'defence']:
			raw = getattr(self, f'raw_{side}')
			stat_name = side[:3]
			stats[f'{stat_name}_Avg_Score'] = raw['Score'].mean()
			stats[f'{stat_name}_Max_Score'] = raw['Score'].max()
			stats[f'{stat_name}_Min_Score'] = raw['Score'].min()
			stats[f'{stat_name}_Avg_Yards'] = raw['Yards'].mean()
			stats[f'{stat_name}_Avg_Turnovers'] = raw['Turnovers'].mean()
			stats[f'{stat_name}_Avg_Sacks'] = raw['Sacks'].mean()
			stats[f'{stat_name}_Avg_TDCR'] = raw['Third Down Rate'].mean()
		return stats

	def __hash__(self):
		return hash(self.name)

	def __repr__(self):
		return f'Team(name={self.name})'

	def __str__(self):
		return self.name

class TeamDictionary:
	team_names = {
		'ARI': 'Arizona Cardinals', 'ATL': 'Atlanta Falcons', 'BAL': 'Baltimore Ravens', 'BUF': 'Buffalo Bills',
		'CAR': 'Carolina Panthers', 'CHI': 'Chicago Bears', 'CIN': 'Cincinnati Bengals', 'CLE': 'Cleveland Browns',
		'DAL': 'Dallas Cowboys', 'DEN': 'Denver Broncos', 'DET': 'Detroit Lions', 'GNB': 'Green Bay Packers',
		'HOU': 'Houston Texans', 'IND': 'Indianapolis Colts', 'JAX': 'Jacksonville Jaguars', 'KAN': 'Kansas City Chiefs',
		'LAC': 'Los Angeles Chargers', 'LAR': 'Los Angeles Rams', 'MIA': 'Miami Dolphins', 'MIN': 'Minnesota Vikings',
		'NWE': 'New England Patriots', 'NOR': 'New Orleans Saints', 'NYG': 'New York Giants', 'NYJ': 'New York Jets',
		'OAK': 'Oakland Raiders', 'PHI': 'Philadelphia Eagles', 'PIT': 'Pittsburgh Steelers', 'SEA': 'Seattle Seahawks',
		'SFO': 'San Francisco 49ers', 'TAM': 'Tampa Bay Buccaneers', 'TEN': 'Tennessee Titans', 'WAS': 'Washington Redskins',
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

	def values(self):
		return self.teams.values()

teams = TeamDictionary()