from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
# REMOVED: matplotlib imports for Android compatibility
# from kivy.garden.matplotlib import FigureCanvasKivyAgg
# import matplotlib.pyplot as plt
from kivy.core.window import Window
import sqlite3 as dbms

# Simple cricket classes without input() functions
class Batsman:
    def __init__(self, name="Player", striker=True):
        self.Name = name
        self.Runs = 0
        self.Balls = 0
        self.Fours = 0
        self.Sixes = 0
        self.Striker = striker

    @property
    def Sr(self):
        if self.Balls == 0:
            return 0.0
        return round(((self.Runs / self.Balls) * 100), 1)

    def bat_one(self, n):
        r = 0
        if n == 0:
            r = 0
        elif n == 1:
            r = 1
        elif n == 2:
            r = 2
        elif n == 3:
            r = 3
        elif n == 4:
            r = 4
            self.Fours += 1
        elif n == 5:
            r = 5
        elif n == 6:
            r = 6
            self.Sixes += 1
        elif str(n).lower() in ("wb", "nb"):
            r = 1

        self.Runs += r
        if str(n) not in ("wb", "nb"):  # Don't count balls for extras
            self.Balls += 1
        return r

class Bowler:
    def __init__(self, name="Bowler"):
        self.Name = name
        self.Runs = 0
        self.Overs = 0
        self.Wickets = 0

    @property
    def Er(self):
        if self.Overs == 0:
            return 0.0
        return round((self.Runs / self.Overs), 1)

    def bowl_one(self, n):
        r = 0
        if n in [0,1,2,3,4,5,6]:
            r = n
        elif str(n).lower() == "w":
            self.Wickets += 1
        elif str(n).lower() in ("wb", "nb"):
            r = 1
        
        self.Runs += r
        return r

class SimpleMatch:
    def __init__(self, team_name, total_overs=5):
        self.team_name = team_name
        self.total_overs = total_overs
        self.current_over = 1
        self.current_ball = 0
        self.total_runs = 0
        self.total_wickets = 0
        self.batsman1 = None
        self.batsman2 = None
        self.bowler = None
        self.over_runs = []

    def add_ball(self, ball_value):
        if not self.batsman1 or not self.bowler:
            return
        
        # Convert ball value
        try:
            ball_int = int(ball_value)
        except:
            ball_int = ball_value
        
        # Update bowler
        runs = self.bowler.bowl_one(ball_int)
        self.total_runs += runs
        
        # Update batsman (striker)
        striker = self.batsman1 if self.batsman1.Striker else self.batsman2
        striker.bat_one(ball_int)
        
        # Handle wicket
        if str(ball_value).lower() == "w":
            self.total_wickets += 1
        
        # Handle extras (don't increment ball count)
        if str(ball_value).lower() not in ("wb", "nb"):
            self.current_ball += 1
        
        # End of over
        if self.current_ball >= 6:
            self.over_runs.append(self.get_current_over_runs())
            self.current_over += 1
            self.current_ball = 0
        
        # Swap striker on odd runs
        if isinstance(ball_int, int) and ball_int % 2 == 1:
            self.swap_striker()
    
    def get_current_over_runs(self):
        # Simple calculation - could be improved
        return min(self.total_runs, 20)  # Cap at reasonable value
    
    def swap_striker(self):
        if self.batsman1 and self.batsman2:
            self.batsman1.Striker, self.batsman2.Striker = self.batsman2.Striker, self.batsman1.Striker

# Optional: set mobile-friendly window size
Window.size = (400, 700)

class CricketApp(App):
    def build(self):
        self.title = "York Hit - Cricket Scorecard"
        self.root_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.total_overs = 5
        self.innings_index = 0
        self.matches = []
        self.target = None
        self.current_match = None

        # Live scoreboard panel
        self.score_panel = BoxLayout(orientation='vertical', size_hint_y=None, height=120, padding=5, spacing=5)
        self.team_label = Label(text="York Hit Cricket", font_size=20, bold=True, color=(1, 1, 0, 1))
        self.runs_label = Label(text="Welcome!", font_size=18, color=(0.5, 1, 0.5, 1))
        self.wickets_label = Label(text="Start your match", font_size=16, color=(1, 0.5, 0.5, 1))
        self.score_panel.add_widget(self.team_label)
        self.score_panel.add_widget(self.runs_label)
        self.score_panel.add_widget(self.wickets_label)
        self.root_layout.add_widget(self.score_panel)

        # Chart area (simplified without matplotlib)
        self.chart_box = BoxLayout(size_hint_y=0.3)
        self.chart_label = Label(text="Runs per over will appear here", color=(0.7, 0.7, 0.7, 1))
        self.chart_box.add_widget(self.chart_label)
        self.root_layout.add_widget(self.chart_box)

        self.get_team_names_popup()
        return self.root_layout

    # ---------------- Team names popup ----------------
    def get_team_names_popup(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.team1_input = TextInput(hint_text="Enter Team 1 Name", multiline=False, text="Team A")
        self.team2_input = TextInput(hint_text="Enter Team 2 Name", multiline=False, text="Team B")
        submit_btn = Button(text="Start Match", size_hint_y=None, height=40, background_color=(0.5,0.7,1,1))
        layout.add_widget(self.team1_input)
        layout.add_widget(self.team2_input)
        layout.add_widget(submit_btn)
        self.popup = Popup(title="Enter Team Names", content=layout, size_hint=(0.85, 0.5))
        submit_btn.bind(on_press=self.submit_team_names)
        self.popup.open()

    def submit_team_names(self, instance):
        self.team1 = self.team1_input.text.strip() or "Team A"
        self.team2 = self.team2_input.text.strip() or "Team B"
        self.popup.dismiss()
        self.setup_innings_screen()

    # ---------------- Setup innings screen ----------------
    def setup_innings_screen(self):
        self.clear_scoring_interface()
        
        team = self.team1 if self.innings_index == 0 else self.team2
        title = f"{team} is batting" if self.innings_index == 0 else f"{team} chasing target: {self.target}"
        
        title_label = Label(text=title, font_size=18, bold=True, color=(0.9, 0.5, 0.1, 1), 
                           size_hint_y=None, height=40)
        self.root_layout.add_widget(title_label)

        # Create match
        self.current_match = SimpleMatch(team, self.total_overs)
        self.matches.append(self.current_match)

        self.get_player_names_popup(team)

    # ---------------- Player names popup ----------------
    def get_player_names_popup(self, team):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.batsman1_input = TextInput(hint_text="Striker Name", multiline=False, text="Batsman 1")
        self.batsman2_input = TextInput(hint_text="Non-Striker Name", multiline=False, text="Batsman 2")
        self.bowler_input = TextInput(hint_text="Bowler Name", multiline=False, text="Bowler 1")
        submit_btn = Button(text="Start Innings", size_hint_y=None, height=40, background_color=(0.5,1,0.5,1))
        layout.add_widget(self.batsman1_input)
        layout.add_widget(self.batsman2_input)
        layout.add_widget(self.bowler_input)
        layout.add_widget(submit_btn)
        self.popup = Popup(title=f"{team} Players", content=layout, size_hint=(0.85, 0.7))
        submit_btn.bind(on_press=self.submit_player_names)
        self.popup.open()

    def submit_player_names(self, instance):
        striker = self.batsman1_input.text.strip() or "Batsman 1"
        non_striker = self.batsman2_input.text.strip() or "Batsman 2"
        bowler_name = self.bowler_input.text.strip() or "Bowler 1"
        self.popup.dismiss()

        # Initialize players
        self.current_match.batsman1 = Batsman(striker, True)
        self.current_match.batsman2 = Batsman(non_striker, False)
        self.current_match.bowler = Bowler(bowler_name)

        self.build_scoring_interface()
        self.update_live_scoreboard()
        self.update_chart()

    def clear_scoring_interface(self):
        # Remove everything except the score panel and chart box
        children_to_remove = []
        for child in self.root_layout.children:
            if child != self.score_panel and child != self.chart_box:
                children_to_remove.append(child)
        
        for child in children_to_remove:
            self.root_layout.remove_widget(child)

    # ---------------- Scoring interface ----------------
    def build_scoring_interface(self):
        # Ball input buttons
        ball_buttons = GridLayout(cols=4, spacing=5, size_hint_y=None, height=200)
        for val in ['0','1','2','3','4','5','6','W','WB','NB']:
            if val.isdigit():
                color = (0.5, 0.5, 1, 1)
            elif val == 'W':
                color = (1, 0.3, 0.3, 1)
            else:
                color = (1, 0.7, 0.3, 1)
            
            btn = Button(text=val, font_size=16, background_color=color)
            btn.bind(on_press=self.add_ball)
            ball_buttons.add_widget(btn)
        self.root_layout.add_widget(ball_buttons)

        # Control buttons
        controls = GridLayout(cols=2, spacing=5, size_hint_y=None, height=50)
        swap_btn = Button(text="Swap Striker", font_size=14, background_color=(0.7,0.7,1,1))
        swap_btn.bind(on_press=self.swap_striker)
        next_over_btn = Button(text="Next Over", font_size=14, background_color=(0.5,1,0.7,1))
        next_over_btn.bind(on_press=self.next_over)
        controls.add_widget(swap_btn)
        controls.add_widget(next_over_btn)
        self.root_layout.add_widget(controls)

        # Live score display
        self.score_layout = GridLayout(cols=1, size_hint_y=None, height=100)
        self.score_details = Label(text="Match started!", size_hint_y=None, height=100)
        self.score_layout.add_widget(self.score_details)
        self.root_layout.add_widget(self.score_layout)

    # ---------------- Live scoreboard ----------------
    def update_live_scoreboard(self):
        if not self.current_match:
            return
            
        self.team_label.text = f"[b]{self.current_match.team_name}[/b]"
        self.runs_label.text = f"Runs: {self.current_match.total_runs}/{self.current_match.total_wickets}"
        self.wickets_label.text = f"Over: {self.current_match.current_over}/{self.current_match.total_overs} Ball: {self.current_match.current_ball}"
        
        # Update score details
        if self.current_match.batsman1 and self.current_match.batsman2:
            striker = self.current_match.batsman1 if self.current_match.batsman1.Striker else self.current_match.batsman2
            non_striker = self.current_match.batsman2 if self.current_match.batsman1.Striker else self.current_match.batsman1
            
            details = f"{striker.Name}*: {striker.Runs}({striker.Balls}) SR:{striker.Sr}\n"
            details += f"{non_striker.Name}: {non_striker.Runs}({non_striker.Balls}) SR:{non_striker.Sr}\n"
            details += f"Bowler: {self.current_match.bowler.Name} - {self.current_match.bowler.Runs} runs"
            self.score_details.text = details

    # ---------------- Add ball ----------------
    def add_ball(self, instance):
        if not self.current_match:
            return
            
        ball = instance.text.strip()
        self.current_match.add_ball(ball)
        self.update_live_scoreboard()
        self.update_chart()

        # Check innings end
        if self.current_match.current_over > self.current_match.total_overs:
            self.end_innings()
        elif self.innings_index == 1 and self.target and self.current_match.total_runs >= self.target:
            self.end_innings()

    # ---------------- Chart (simplified) ----------------
    def update_chart(self):
        if not self.current_match or not self.current_match.over_runs:
            self.chart_label.text = "No over data yet"
            return
            
        # Simple text-based chart
        chart_text = "Runs per over:\n"
        for i, runs in enumerate(self.current_match.over_runs):
            chart_text += f"Over {i+1}: {runs} runs\n"
        
        self.chart_label.text = chart_text

    # ---------------- Control functions ----------------
    def swap_striker(self, instance):
        if self.current_match:
            self.current_match.swap_striker()
            self.update_live_scoreboard()

    def next_over(self, instance):
        if self.current_match:
            self.current_match.current_over += 1
            self.current_match.current_ball = 0
            self.current_match.bowler = Bowler(f"Bowler {self.current_match.current_over}")
            self.update_live_scoreboard()

    def end_innings(self):
        if self.innings_index == 0:
            self.target = self.current_match.total_runs + 1
            self.innings_index = 1
            self.setup_innings_screen()
        else:
            self.show_final_scorecard()

    # ---------------- Final scorecard ----------------
    def show_final_scorecard(self):
        self.root_layout.clear_widgets()
        
        # Winner determination
        team1_score = self.matches[0].total_runs if len(self.matches) > 0 else 0
        team2_score = self.matches[1].total_runs if len(self.matches) > 1 else 0
        
        winner_text = f"🏆 MATCH RESULT 🏆\n\n"
        winner_text += f"{self.team1}: {team1_score} runs\n"
        winner_text += f"{self.team2}: {team2_score} runs\n\n"
        
        if team1_score > team2_score:
            winner_text += f"{self.team1} WINS! 🎉"
        elif team2_score > team1_score:
            winner_text += f"{self.team2} WINS! 🎉"
        else:
            winner_text += "IT'S A TIE! 🤝"

        winner_label = Label(text=winner_text, font_size=18, bold=True, 
                           color=(1, 0.8, 0, 1), text_size=(None, None))
        self.root_layout.add_widget(winner_label)

        # Simple scorecard
        scorecard = BoxLayout(orientation='vertical', spacing=10)
        
        for i, match in enumerate(self.matches):
            team_name = self.team1 if i == 0 else self.team2
            
            team_layout = BoxLayout(orientation='vertical', spacing=5)
            team_layout.add_widget(Label(text=f"\n--- {team_name} ---", font_size=16, bold=True))
            
            if match.batsman1:
                team_layout.add_widget(Label(text=f"{match.batsman1.Name}: {match.batsman1.Runs}({match.batsman1.Balls}) 4s:{match.batsman1.Fours} 6s:{match.batsman1.Sixes}"))
            if match.batsman2:
                team_layout.add_widget(Label(text=f"{match.batsman2.Name}: {match.batsman2.Runs}({match.batsman2.Balls}) 4s:{match.batsman2.Fours} 6s:{match.batsman2.Sixes}"))
            if match.bowler:
                team_layout.add_widget(Label(text=f"Bowled by: {match.bowler.Name} - {match.bowler.Runs} runs, {match.bowler.Wickets} wickets"))
            
            scorecard.add_widget(team_layout)
        
        scroll = ScrollView()
        scroll.add_widget(scorecard)
        self.root_layout.add_widget(scroll)

        # Play again button
        play_again_btn = Button(text="Play Again", size_hint_y=None, height=50, background_color=(0.2, 0.8, 0.2, 1))
        play_again_btn.bind(on_press=self.restart_app)
        self.root_layout.add_widget(play_again_btn)

    def restart_app(self, instance):
        self.innings_index = 0
        self.matches = []
        self.target = None
        self.current_match = None
        self.root_layout.clear_widgets()
        self.root_layout.add_widget(self.score_panel)
        self.root_layout.add_widget(self.chart_box)
        self.get_team_names_popup()

if __name__ == "__main__":
    CricketApp().run()