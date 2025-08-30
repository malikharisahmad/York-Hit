from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.garden.matplotlib import FigureCanvasKivyAgg
from kivy.core.window import Window
import matplotlib.pyplot as plt
from cricket_match_class import CricketMatch
import sqlite3 as dbms

# Optional: set mobile-friendly window size
Window.size = (400, 700)

class CricketApp(App):
    def build(self):
        self.title = "Cricket Scorecard App"
        self.root_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.total_overs = 5
        self.innings_index = 0
        self.matches = []
        self.target = None

        # Live scoreboard panel
        self.score_panel = BoxLayout(orientation='vertical', size_hint_y=None, height=120, padding=5, spacing=5)
        self.team_label = Label(text="", font_size=20, bold=True, color=(1, 1, 0, 1))
        self.runs_label = Label(text="", font_size=18, color=(0.5, 1, 0.5, 1))
        self.wickets_label = Label(text="", font_size=16, color=(1, 0.5, 0.5, 1))
        self.score_panel.add_widget(self.team_label)
        self.score_panel.add_widget(self.runs_label)
        self.score_panel.add_widget(self.wickets_label)
        self.root_layout.add_widget(self.score_panel)

        # Chart area
        self.chart_box = BoxLayout(size_hint_y=0.35)
        self.root_layout.add_widget(self.chart_box)

        self.get_team_names_popup()
        return self.root_layout

    # ---------------- Team names popup ----------------
    def get_team_names_popup(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.team1_input = TextInput(hint_text="Enter Team 1 Name", multiline=False)
        self.team2_input = TextInput(hint_text="Enter Team 2 Name", multiline=False)
        submit_btn = Button(text="Start Match", size_hint_y=None, height=40, background_color=(0.5,0.7,1,1))
        layout.add_widget(self.team1_input)
        layout.add_widget(self.team2_input)
        layout.add_widget(submit_btn)
        self.popup = Popup(title="Enter Team Names", content=layout, size_hint=(0.85, 0.5))
        submit_btn.bind(on_press=self.submit_team_names)
        self.popup.open()

    def submit_team_names(self, instance):
        self.team1 = self.team1_input.text.strip() or "Team 1"
        self.team2 = self.team2_input.text.strip() or "Team 2"
        self.popup.dismiss()
        self.setup_innings_screen()

    # ---------------- Setup innings screen ----------------
    def setup_innings_screen(self):
        self.root_layout.clear_widgets()
        self.root_layout.add_widget(self.score_panel)
        self.root_layout.add_widget(self.chart_box)

        team = self.team1 if self.innings_index == 0 else self.team2
        title = f"{team} is batting" if self.innings_index == 0 else f"{team} chasing target: {self.target}"
        self.root_layout.add_widget(Label(text=title, font_size=22, bold=True, color=(0.9, 0.5, 0.1, 1)))

        # Pop-up for first batsman and bowler names
        self.get_player_names_popup(team)

    # ---------------- Player names popup ----------------
    def get_player_names_popup(self, team):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.batsman1_input = TextInput(hint_text="Striker Name", multiline=False)
        self.batsman2_input = TextInput(hint_text="Non-Striker Name", multiline=False)
        self.bowler_input = TextInput(hint_text="Bowler Name", multiline=False)
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

        # Initialize match
        team = self.team1 if self.innings_index == 0 else self.team2
        self.match = CricketMatch(team, self.total_overs, self.target, [])
        self.matches.append(self.match)

        self.match.Bm1.Name = striker
        self.match.Bm2.Name = non_striker
        self.match.Bl.Name = bowler_name

        self.over_runs = []
        self.build_scoring_interface()
        self.update_live_scoreboard()
        self.update_chart()

    # ---------------- Scoring interface ----------------
    def build_scoring_interface(self):
        ball_buttons = GridLayout(cols=4, spacing=5, size_hint_y=None, height=220)
        for val in ['0','1','2','3','4','5','6','w','WB','NB']:
            color = (0.5, 0.5, 1,1) if val.isdigit() else (1,0.5,0.5,1)
            btn = Button(text=val, font_size=18, background_color=color)
            btn.bind(on_press=self.add_ball)
            ball_buttons.add_widget(btn)
        self.root_layout.add_widget(ball_buttons)

        # Control buttons
        controls = GridLayout(cols=2, spacing=5, size_hint_y=None, height=60)
        swap_btn = Button(text="Swap Striker", font_size=16, background_color=(0.7,0.7,1,1))
        swap_btn.bind(on_press=self.swap_striker)
        next_over_btn = Button(text="Next Over", font_size=16, background_color=(0.5,1,0.7,1))
        next_over_btn.bind(on_press=self.next_over)
        controls.add_widget(swap_btn)
        controls.add_widget(next_over_btn)
        self.root_layout.add_widget(controls)

        # Scrollable live score
        self.scroll_view = ScrollView(size_hint=(1,0.4))
        self.score_layout = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.score_layout.bind(minimum_height=self.score_layout.setter('height'))
        self.scroll_view.add_widget(self.score_layout)
        self.root_layout.add_widget(self.scroll_view)
        self.update_scoreboard("Innings started")

    # ---------------- Live scoreboard ----------------
    def update_live_scoreboard(self):
        self.team_label.text = f"[b]{self.match.Team}[/b]"
        self.runs_label.text = f"Runs: {self.match.Score}"
        self.wickets_label.text = f"Wickets: {self.match.Ov.Wickets} | Over: {self.match.Ov.Cur_over}/{self.match.Total_overs}"

    # ---------------- Add ball ----------------
    def add_ball(self, instance):
        ball = instance.text.strip()
        self.match.one_ball(ball)
        self.update_live_scoreboard()

        # Update runs per over chart
        if len(self.over_runs) < self.match.Ov.Cur_over:
            self.over_runs.append(self.match.Ov.Runs)
        else:
            self.over_runs[self.match.Ov.Cur_over-1] = self.match.Ov.Runs
        self.update_chart()

        # Check innings end
        if self.match.Ov.Cur_over > self.match.Total_overs:
            self.end_innings()
        elif self.innings_index == 1 and self.target is not None and self.match.Score >= self.target:
            self.end_innings()

    # ---------------- Chart ----------------
    def update_chart(self):
        self.chart_box.clear_widgets()
        if not self.over_runs: return
        fig, ax = plt.subplots()
        ax.bar(range(1,len(self.over_runs)+1), self.over_runs, color='skyblue')
        ax.set_title(f"{self.match.Team} Runs per Over")
        ax.set_xlabel("Over")
        ax.set_ylabel("Runs")
        ax.grid(True, linestyle='--', alpha=0.5)
        self.chart_box.add_widget(FigureCanvasKivyAgg(fig))

    # ---------------- Swap striker ----------------
    def swap_striker(self, instance):
        self.match.swap_striker(self.match.Bm1, self.match.Bm2)
        self.update_live_scoreboard()

    # ---------------- Next over ----------------
    def next_over(self, instance):
        self.match.Ov.Cur_over += 1
        self.match.Bl = self.match.create_bowler()
        self.match.Ov = self.match.create_overs()
        self.update_live_scoreboard()

    # ---------------- End innings & final scorecard ----------------
    def end_innings(self):
        self.match.add_bowler_to_db(self.match.Bl)
        self.match.add_over_to_db(self.match.Ov)

        if self.innings_index == 0:
            self.target = self.match.Score + 1
            self.innings_index = 1
            self.setup_innings_screen()
        else:
            self.show_final_scorecard()

    # ---------------- Final scorecard with tabs ----------------
    def show_final_scorecard(self):
        self.root_layout.clear_widgets()
        panel = TabbedPanel(do_default_tab=False)

        for match in self.matches:
            tab = TabbedPanelItem(text=match.Team)
            layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
            layout.bind(minimum_height=layout.setter('height'))
            scroll = ScrollView(size_hint=(1,1))
            scroll.add_widget(layout)

            con = dbms.connect(f"{match.Team}.db")
            cur = con.cursor()

            # Batsmen
            cur.execute("SELECT * FROM Batsmen")
            batsmen = cur.fetchall()
            layout.add_widget(Label(text="[b]Batsmen[/b]", markup=True, font_size=20))
            for idx,bm in enumerate(batsmen):
                color = (0.9,0.9,1,1) if idx%2==0 else (0.8,0.8,0.9,1)
                layout.add_widget(Label(text=f"{bm[0]} - Runs: {bm[1]}, Balls: {bm[2]}, Fours: {bm[3]}, Sixes: {bm[4]}, SR: {bm[5]}", 
                                        markup=False, size_hint_y=None, height=30, color=(0,0,0,1)))

            # Bowlers
            cur.execute("SELECT * FROM Bowler")
            bowlers = cur.fetchall()
            layout.add_widget(Label(text="[b]Bowlers[/b]", markup=True, font_size=20))
            for idx,bl in enumerate(bowlers):
                layout.add_widget(Label(text=f"{bl[0]} - Overs: {bl[3]}, Runs: {bl[1]}, Wickets: {bl[4]}, Dots: {bl[2]}, ER: {bl[5]}", size_hint_y=None, height=30))

            # Overs
            cur.execute("SELECT * FROM Overs")
            overs = cur.fetchall()
            layout.add_widget(Label(text="[b]Overs[/b]", markup=True, font_size=20))
            for o in overs:
                layout.add_widget(Label(text=f"{o[0]} - Runs: {o[1]}, Wickets: {o[2]}", size_hint_y=None, height=30))

            # Chart
            runs_per_over = [o[1] for o in overs] if overs else []
            if runs_per_over:
                fig, ax = plt.subplots()
                ax.bar(range(1,len(runs_per_over)+1), runs_per_over, color='skyblue')
                ax.set_title(f"{match.Team} Runs per Over")
                ax.set_xlabel("Over")
                ax.set_ylabel("Runs")
                layout.add_widget(FigureCanvasKivyAgg(fig))

            con.close()
            tab.add_widget(scroll)
            panel.add_widget(tab)

        self.root_layout.add_widget(panel)

if __name__ == "__main__":
    CricketApp().run()
