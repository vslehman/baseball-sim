class InningEvent(object):

    def __init__(self, inning_half, inning_num):
        self.inning_half = inning_half
        self.inning_num = inning_num


class OutEvent(object):

    def __init__(self, num_outs):
        self.num_outs = num_outs


class ScoreEvent(object):

    def __init__(self, away_team, away_score, home_team, home_score):
        self.away_team = away_team
        self.away_score = away_score
        self.home_team = home_team
        self.home_score = home_score
