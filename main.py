import models

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


if __name__ == '__main__':
    result = models.Teams.filter(
        yearId=2019,
        teamId='CIN',
    )
    team = result[0]
    votto = team.get_player(nameLast='Votto')
    stats = votto.get_fielding_stats()
    for stat in stats:
        print(stat.games_started)
        print(dir(stat))
