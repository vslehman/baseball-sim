import tkinter as tk
from tkinter import ttk
from threading import Thread

from PIL import ImageTk, Image

import models

from sim import Game


class DataApi(object):

    @classmethod
    def get_team_options(cls):
        teams = models.Teams.filter(yearId=2019)
        return sorted([team.name for team in teams])

    @classmethod
    def get_team(cls, team_name, team_year):
        return models.Teams.get(name=team_name, yearId=team_year)


class TeamSelect(object):

    def __init__(self, canvas, team_type, row):
        self.text_label = tk.Label(canvas, text=f'{team_type}:')
        self.text_label.grid(column=0, row=row)

        self.team = tk.StringVar()
        self.team_label = tk.Label(canvas, text=self.team)
        self.team_label['textvariable'] = self.team
        self.team_label.grid(column=1, row=row)

        self.team_select = ttk.Combobox(canvas, textvariable=self.team)
        self.team_select.bind('<<ComboboxSelected>>', self.on_team_select)
        self.team_select['values'] = DataApi.get_team_options()
        self.team_select.grid(column=1, row=row + 1)

        self.year = tk.StringVar(value='2019')
        self.year.trace('w', self.on_year_change)
        self.year_select = ttk.Spinbox(
            canvas,
            from_=1950,
            to=2019,
            textvariable=self.year,
        )
        self.year_select.grid(column=0, row=row + 1)

    def on_team_select(self, event):
        pass

    def on_year_change(self, *args):
        pass


class ConfigView(object):

    def __init__(self, canvas, play_by_play):
        self.play_by_play = play_by_play
        self.away_select = TeamSelect(canvas, 'Away', 0)
        self.home_select = TeamSelect(canvas, 'Home', 2)
        self.start_button = ttk.Button(canvas, text='Play Ball', command=self.start_game)
        self.start_button.grid(column=1, row=5, columnspan=2)

    def get_team(self, team_select):
        team_name = team_select.team.get()
        team_year = team_select.year.get()
        return DataApi.get_team(team_name, team_year)

    def start_game(self):
        self.play_by_play.clear_console()
        self.game_thread = Thread(target=self._start_game)
        self.game_thread.start()

    def _start_game(self):
        home_team = self.get_team(self.home_select)
        away_team = self.get_team(self.away_select)
        time_step = 0.5
        self.game = Game(
            home_team,
            away_team,
            time_step,
            listener=self.play_by_play,
        )
        self.game.simulate()


class FieldView(object):

    def __init__(self, canvas):
        self.field_label = tk.Label(canvas)
        self.field_image = ImageTk.PhotoImage(Image.open('materials/field.png'))
        self.field_label['image'] = self.field_image
        self.field_label.grid(column=3, row=0, columnspan=20, rowspan=10)


class PlayByPlayView(object):

    def __init__(self, canvas):
        self.console_text = tk.Text(canvas)
        self.console_text.grid(column=0, row=6, columnspan=2, rowspan=5)
        self.console_text.config(state=tk.DISABLED)

    def on_event(self, event):
        self.console_text.config(state=tk.NORMAL)
        self.console_text.insert(tk.END, event + '\n')
        self.console_text.see(tk.END)
        self.console_text.config(state=tk.DISABLED)

    def clear_console(self):
        self.console_text.config(state=tk.NORMAL)
        self.console_text.delete(1.0, tk.END)
        self.console_text.config(state=tk.DISABLED)


if __name__ == '__main__':
    window = tk.Tk()

    canvas = ttk.Frame(window)
    play_by_play_view = PlayByPlayView(canvas)
    config_view = ConfigView(canvas, play_by_play_view)
    field_view = FieldView(canvas)

    canvas.grid(column=0, row=0)

    window.update()
    window.mainloop()
