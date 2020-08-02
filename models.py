from collections import defaultdict

from tables import Table, QueryRow


POSITIONS = [
    'P',
    'C',
    '1B',
    '2B',
    '3B',
    'SS',
    'LF',
    'CF',
    'RF',
]


class Player(QueryRow):

    def __init__(self, data):
        super(Player, self).__init__(data)
    
    def get_batting_stats(self):
        return BattingStats.filter(playerID=self.playerID, team_ID=self.teamID)
    
    def get_fielding_stats(self):
        fielding = Table('fielding')
        return fielding.filter(playerID=self.playerID, team_ID=self.teamID)
    
    def get_pitching_stats(self):
        pitching = Table('pitching')
        return pitching.filter(playerID=self.playerID, team_ID=self.teamID)
    
    def get_plate_appearances(self):
        pitching = Table('appearances')
        return pitching.filter(playerID=self.playerID, team_ID=self.teamID)
    
    @property
    def name(self):
        return '{} {}'.format(self.nameFirst, self.nameLast)
    
    def __str__(self):
        return '{} {}/{}'.format(
            self.name,
            self.bats,
            self.throws,
        )
    
    def __repr__(self):
        return self.__str__()


Players = Table('people', Player)


class BattingStats(QueryRow):
    
    @property
    def avg(self):
        return float(self.hits) / self.at_bats
    
    @property
    def obp(self):
        numerator = float(self.hits) + self.walks + self.HBP
        denominator = self.at_bats + self.walks + self.HBP + self.sac_flies
        return numerator / denominator
    
    @property
    def ops(self):
        return self.obp + self.slugging

    @property
    def slugging(self):
        return float(self.total_bases) / self.at_bats

    @property
    def singles(self):
        extra_base_hits = self.doubles + self.triples + self.home_runs
        return self.hits - extra_base_hits

    @property
    def total_bases(self):
        return sum([
            self.singles,
            2 * self.doubles,
            3 * self.triples,
            4 * self.home_runs,
        ])
    
    def __str__(self):
        stats = [
            ('AB', 'at_bats'),
            ('R', 'runs'),
            ('H', 'hits'),
            ('HR', 'home_runs'),
            ('RBI', 'rbi'),
            ('SB', 'stolen_bases'),
            ('AVG', 'avg'),
            ('OBP', 'obp'),
            ('OPS', 'ops'),
        ]
        pairs = []
        for label, attr in stats:
            pairs.append('{}: {}'.format(label, getattr(self, attr)))
        return '\n'.join(pairs)


BattingStats = Table('batting', BattingStats)


class Team(QueryRow):

    def _get_player_ids(self):
        if not hasattr(self, '_player_ids'):
            through_result = BattingStats.filter(team_ID=self.id)
            self._player_ids = set(x.playerID for x in through_result)
        return self._player_ids

    def get_players(self):
        player_ids = self._get_player_ids()
        return self._get_players(player_ids)
    
    def get_player(self, **kwargs):
        player_ids = self._get_player_ids()
        player = self._get_players(player_ids, **kwargs)
        if len(player) > 1:
            raise RuntimeError('More than one player found!')
        elif len(player) == 0:
            raise RuntimeError('No player found!')
        else:
            return player[0]
    
    def get_starters(self):
        starts = defaultdict(list)
        for player in self.get_players():
            stats = player.get_fielding_stats()
            for stat in stats:
                starts[stat.position].append((stat.games_started, player))
        starters = {}
        infield = [
            'P',
            'C',
            '1B',
            '2B',
            '3B',
            'SS',
        ]
        for position in infield:
            starters[position] = sorted(starts[position], reverse=True)[0][1]
        outfielders = sorted(starts['OF'], reverse=True)[:3]
        for position in ['LF', 'CF', 'RF', ]:
            starters[position] = outfielders.pop()[1]
        return starters
    
    def _get_players(self, player_ids, **kwargs):
        players_result = Players.filter(playerID__in=player_ids, **kwargs)
        for player in players_result:
            player.teamID = self.id
        return players_result
    
    def __str__(self):
        return '{} ({})'.format(self.name, self.year)


Teams = Table('teams', Team)


class Lineup(object):

    def __init__(self, team):
        self.team = team
        self.lineup = team.get_starters()
        self.players = self.lineup.values()
        self.batting_order = []
    
        self.add_players(lambda x: x.get_batting_stats()[0].stolen_bases, 2)
        self.add_players(lambda x: x.get_batting_stats()[0].avg, 1)
        self.add_players(lambda x: x.get_batting_stats()[0].slugging, 1)
        self.add_players(lambda x: x.get_batting_stats()[0].avg, 5)
    
    def add_players(self, sort_key, num):
        sorted_players = sorted(self.players, key=sort_key, reverse=True)
        for i in range(num):
            player = sorted_players.pop(0)
            self.batting_order.append(player)
            self.players.remove(player)

    def __str__(self):
        lineup = []
        for idx, player in enumerate(self.batting_order, 1):
            lineup.append('{}. {}'.format(idx, player))
        return '\n'.join(lineup)