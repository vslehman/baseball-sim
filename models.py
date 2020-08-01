from tables import Table, QueryRow


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
    
    def __str__(self):
        return '{} {} {}/{}'.format(
            self.nameFirst,
            self.nameLast,
            self.bats,
            self.throws,
        )


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
    def total_bases(self):
        extra_base_hits = self.doubles + self.triples + self.home_runs
        singles = self.hits - extra_base_hits
        return sum([
            singles,
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
    
    def _get_players(self, player_ids, **kwargs):
        players_result = Players.filter(playerID__in=player_ids, **kwargs)
        for player in players_result:
            player.teamID = self.id
        return players_result
    
    def __str__(self):
        return '{} ({})'.format(self.name, self.year)


Teams = Table('teams', Team)