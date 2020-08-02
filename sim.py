import argparse
import models
import random
import time

"""
allstarfull
appearances
awardsmanagers
awardsplayers
awardssharemanagers
awardsshareplayers
batting
battingpost
collegeplaying
divisions
fielding
fieldingof
fieldingofsplit
fieldingpost
halloffame
homegames
leagues
managers
managershalf
parks
people
pitching
pitchingpost
salaries
schools
seriespost
teams
teamsfranchises
teamshalf
"""

FIRST_BASE = 0
SECOND_BASE = 1
THIRD_BASE = 2
HOME_RUN = 3


class Game(object):

    def __init__(self, home_team, away_team):
        self.home_team = home_team
        self.away_team = away_team
        self.home_lineup = models.Lineup(home_team)
        self.away_lineup = models.Lineup(away_team)

        self.outs = 0
        self.strikes = 0
        self.balls = 0

        self.home_pitcher = self.home_lineup.lineup['P']
        self.away_pitcher = self.away_lineup.lineup['P']

        self.stats = {
            'home': {
                'runs': 0,
                'batting_idx': 0,
                'hits': 0,
                'walks': 0,
                'errors': 0,
                'box_score': [],
            },
            'away': {
                'runs': 0,
                'batting_idx': 0,
                'hits': 0,
                'walks': 0,
                'errors': 0,
                'box_score': [{'runs': 0, 'hits': 0, 'errors': 0, }, ],
            },
        }
        self.stats['top'] = self.stats['away']
        self.stats['bottom'] = self.stats['home']

        self.inning = 1
        self.inning_half = 'top'

        self.bases = [None, None, None]
    
    def start_game(self):
        self.outs = 0
        self.strikes = 0
        self.balls = 0

        self.home_batting_idx = 0
        self.away_batting_idx = 0

        self.inning = 1
        self.inning_half = 'top'

        self.bases = [None, None, None]

    def advance_inning_half(self):
        self.outs = 0
        self.strikes = 0
        self.balls = 0

        if self.inning_half == 'bottom':
            self.inning += 1
            self.inning_half = 'top'
        else:
            self.inning_half = 'bottom'
        
        self.stats[self.inning_half]['box_score'].append(
            {'runs': 0, 'hits': 0, 'errors': 0, }
        )
        
        self.bases = [None, None, None]
    
    def advance_runners(self, amount, is_walk=False):
        while amount > 0:
            if self.bases[THIRD_BASE] and ((is_walk and self.bases[SECOND_BASE] and self.bases[FIRST_BASE]) or (not is_walk)):
                player = self.bases[THIRD_BASE]
                self.bases[THIRD_BASE] = None
                self.score_run(player)
            if self.bases[SECOND_BASE] and ((is_walk and self.bases[FIRST_BASE]) or (not is_walk)):
                player = self.bases[SECOND_BASE]
                self.bases[SECOND_BASE] = None
                self.bases[THIRD_BASE] = player
            if self.bases[FIRST_BASE]:
                player = self.bases[FIRST_BASE]
                self.bases[FIRST_BASE] = None
                self.bases[SECOND_BASE] = player
            amount -= 1

    def walk(self, batter, pitcher):
        self.advance_runners(1, is_walk=True)
        self.bases[FIRST_BASE] = batter
        self.stats[self.inning_half]['walks'] += 1
        print('{} walks {}'.format(pitcher.name, batter.name))

    def strikeout(self, batter, pitcher):
        self.outs += 1
        print('{} strikes-out {}'.format(pitcher.name, batter.name))

    def hit(self, batter, pitcher):
        batting_stats = batter.get_batting_stats()[0]
        probabilities = [
            (float(batting_stats.singles) / batting_stats.at_bats, FIRST_BASE),
            (float(batting_stats.doubles) / batting_stats.at_bats, SECOND_BASE),
            (float(batting_stats.triples) / batting_stats.at_bats, THIRD_BASE),
            (float(batting_stats.home_runs) / batting_stats.at_bats, HOME_RUN),
        ]
        rng = random.random()
        total_pct = 0
        hit_type = None
        for pct, outcome in probabilities:
            total_pct += pct
            if rng < total_pct:
                hit_type = outcome
                break
        
        if not hit_type:
            hit_type = FIRST_BASE
        
        self.advance_runners(hit_type + 1)

        if hit_type == HOME_RUN:
            self.score_run(batter)
        else:
            self.bases[hit_type] = batter

        self.stats[self.inning_half]['hits'] += 1
        self.stats[self.inning_half]['box_score'][self.inning - 1]['hits'] += 1

        hit_verbs = {
            FIRST_BASE: 'singles',
            SECOND_BASE: 'doubles',
            THIRD_BASE: 'triples',
            HOME_RUN: 'hits a home-run'
        }
        print('{} {} off {}'.format(batter.name, hit_verbs[hit_type], pitcher.name))

    def out(self, batter, pitcher):
        self.outs += 1
        hit_type = random.choice(['grounds-out', 'flies-out', ])
        print('{} {}'.format(batter.name, hit_type))
    
    def score_run(self, player):
        self.stats[self.inning_half]['runs'] += 1
        self.stats[self.inning_half]['box_score'][self.inning - 1]['runs'] += 1
        self.runs_per_outcome += 1
    
    def simulate_plate_appearance(self, batter, pitcher):
        # Pitcher
        pitcher_probability = {}
        pitching_stats = pitcher.get_pitching_stats()[0]
        pitcher_probability['walk_pct'] = float(pitching_stats.walks) / pitching_stats.batters_faced
        pitcher_probability['strikeout_pct'] = float(pitching_stats.strikeouts) / pitching_stats.batters_faced
        pitcher_probability['hit_pct'] = float(pitching_stats.hits) / pitching_stats.batters_faced

        # Batter
        batter_probability = {}
        batting_stats = batter.get_batting_stats()[0]
        batter_probability['walk_pct'] = float(batting_stats.walks) / batting_stats.at_bats
        batter_probability['strikeout_pct'] = float(batting_stats.strikeouts) / batting_stats.at_bats
        batter_probability['hit_pct'] = float(batting_stats.hits) / batting_stats.at_bats

        possible_outcomes = []

        # Walk
        rng = random.random()
        avg_prob = (batter_probability['walk_pct'] + pitcher_probability['walk_pct']) / 2
        # print('walk', avg_prob)
        if rng < avg_prob:
            possible_outcomes.append(self.walk)
        
        # Strikeout
        rng = random.random()
        avg_prob = (batter_probability['strikeout_pct'] + pitcher_probability['strikeout_pct']) / 2
        # print('strikeout', avg_prob)
        if rng < avg_prob:
            possible_outcomes.append(self.strikeout)
        
        # Hit
        rng = random.random()
        avg_prob = (batter_probability['hit_pct'] + pitcher_probability['hit_pct']) / 2
        # print('hit', avg_prob)
        if rng < avg_prob:
            possible_outcomes.append(self.hit)
        
        if possible_outcomes:
            outcome = random.choice(possible_outcomes)
        else:
            outcome = self.out
        
        self.runs_per_outcome = 0
        outcome(batter, pitcher)
        if self.runs_per_outcome:
            if self.runs_per_outcome == 1:
                print('1 run scores')
            else:
                print('{} runs score'.format(self.runs_per_outcome))
            print('{} {} - {} {}'.format(
                self.away_team.teamID,
                self.stats['away']['runs'],
                self.home_team.teamID,
                self.stats['home']['runs'],
            ))
        
        batting_idx = self.stats[self.inning_half]['batting_idx']
        self.stats[self.inning_half]['batting_idx'] = (batting_idx + 1) % 9

    def simulate_inning_half(self):
        print('\n-- {} of Inning {} --\n'.format(self.inning_half.title(), self.inning))
        pitcher = self.home_pitcher if self.inning_half == 'top' else self.away_pitcher
        lineup = self.away_lineup if self.inning_half == 'top' else self.home_lineup
        while self.outs < 3:
            batting_idx = self.stats[self.inning_half]['batting_idx']
            hitter = lineup.batting_order[batting_idx]
            self.simulate_plate_appearance(
                hitter,
                pitcher,
            )
            time.sleep(0.5)
    
    def simulate(self):
        self.start_game()
        while True:
            self.simulate_inning_half()
            if self.is_game_over():
                break
            else:
                self.advance_inning_half()

        self.print_box_score()
    
    def is_game_over(self):
        if self.inning < 9:
            return False

        home_score = self.stats['home']['runs']
        away_score = self.stats['away']['runs']

        if self.inning >= 9 and home_score > away_score and self.inning_half == 'top':
            self.stats['home']['box_score'].append({'runs': 'X'})
            return True

        if self.inning >= 9 and home_score != away_score and self.inning_half == 'bottom':
            return True

        return False
    
    def _print_team_line(self, team_id, team_type):
        per_inning_runs = ''.join(['{:>5}'.format(x['runs']) for x in self.stats[team_type]['box_score']])
        total_runs = self.stats[team_type]['runs']
        total_hits = self.stats[team_type]['hits']
        total_errors = self.stats[team_type]['errors']
        team_line = '{} {}{:>5}{:>5}{:>5}'.format(
            team_id,
            per_inning_runs,
            total_runs,
            total_hits,
            total_errors,
        )
        print(team_line)
    
    def print_box_score(self):
        home_score = self.stats['home']['runs']
        away_score = self.stats['away']['runs']
        winning_team = self.home_team.name if home_score > away_score else self.away_team.name
        print('\n{} win!\n'.format(winning_team))

        num_innings = len(self.stats['away']['box_score']) + 1
        print('Team    1    2    3    4    5    6    7    8    9{}    R    H    E'.format(''.join(['{:>5}'.format(i) for i in range(10, num_innings)])))
        self._print_team_line(self.away_team.teamID, 'away')
        self._print_team_line(self.home_team.teamID, 'home')


def sim_game(home_team, away_team):
    game = Game(home_team, away_team)
    game.simulate()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'home',
        action='store',
    )
    parser.add_argument(
        'home_year',
        action='store',
    )
    parser.add_argument(
        'away',
        action='store',
    )
    parser.add_argument(
        'away_year',
        action='store',
    )
    args = parser.parse_args()
    

    home = models.Teams.filter(
        yearId=args.home_year,
        teamId=args.home,
    )[0]

    away = models.Teams.filter(
        yearId=args.away_year,
        teamId=args.away,
    )[0]

    sim_game(home, away)
