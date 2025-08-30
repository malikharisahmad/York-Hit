from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


# ---- Your Python Logic (unchanged) ----
class Bowler:
    def __init__(self, name, runs=0, dots=0.0, overs=0, wickets=0):
        self.Name = name
        self.Overs = overs + 1
        self.Dots = dots
        self.Runs = runs
        self.Wickets = wickets

    @property
    def Name(self):
        return self.__name
    @Name.setter
    def Name(self, s):
        self.__name = s
        return self.__name

    @property
    def Overs(self):
        return self.__overs
    @Overs.setter
    def Overs(self, s):
        self.__overs = s
        return self.__overs

    @property
    def Dots(self):
        return self.__dots
    @Dots.setter
    def Dots(self, s):
        self.__dots = s
        return self.__dots

    @property
    def Runs(self):
        return self.__runs
    @Runs.setter
    def Runs(self, s):
        self.__runs = s
        return self.__runs

    @property
    def Wickets(self):
        return self.__wickets
    @Wickets.setter
    def Wickets(self, s):
        self.__wickets = s
        return self.__wickets

    @property
    def Er(self):
        return round((self.Runs / self.Overs), 1)

    def bowl_one(self, n):
        r = 0
        w = 0
        nb = 0
        wb = 0
        if n == 0:
            r += 0
            self.Dots += 1
        elif n == 1:
            r += 1
        elif n == 2:
            r += 2
        elif n == 3:
            r += 3
        elif n == 4:
            r += 4
        elif n == 5:
            r += 5
        elif n == 6:
            r += 6
        elif n in ("w", "W"):
            w += 1
            self.Wickets += w
        elif n in ("wb", "WB", "wB", "Wb"):
            wb += 1
        elif n in ("nb", "NB", "nB", "Nb"):
            nb += 1
        self.Runs += (r + nb + wb)

        return (r, w, nb, wb)


# ---- Kivy UI Layer ----
class BowlerApp(App):
    def build(self):
        self.bowler = Bowler("Shaheen Afridi")  # Example bowler

        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Display labels
        self.label_name = Label(text=f"Bowler: {self.bowler.Name}")
        self.label_stats = Label(text=self.get_stats())

        # Input box for delivery result
        self.input_ball = TextInput(hint_text="Enter ball result (0-6, w, nb, wb)", multiline=False)

        # Button to update stats
        btn_update = Button(text="Update Ball")
        btn_update.bind(on_press=self.update_stats)

        # Add widgets to layout
        self.layout.add_widget(self.label_name)
        self.layout.add_widget(self.label_stats)
        self.layout.add_widget(self.input_ball)
        self.layout.add_widget(btn_update)

        return self.layout

    def get_stats(self):
        return f"Overs: {self.bowler.Overs} | Runs: {self.bowler.Runs} | Wickets: {self.bowler.Wickets} | Dots: {self.bowler.Dots} | ER: {self.bowler.Er}"

    def update_stats(self, instance):
        ball = self.input_ball.text.strip()
        if ball:
            # Handle numeric or string input safely
            try:
                ball = int(ball)
            except ValueError:
                pass
            self.bowler.bowl_one(ball)
            self.label_stats.text = self.get_stats()
            self.input_ball.text = ""


if __name__ == "__main__":
    BowlerApp().run()
