from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


# ---- Your Overs Class (unchanged) ----
class Overs:
    def __init__(self, overs):
        self.Runs = 0
        self.Wickets = 0
        self.Overs = overs
        self.Cur_over = 1

    @property
    def Runs(self):
        return self.__runs
    @Runs.setter
    def Runs(self, d):
        self.__runs = d
        return self.__runs

    @property
    def Wickets(self):
        return self.__wickets
    @Wickets.setter
    def Wickets(self, d):
        self.__wickets = d
        return self.__wickets

    @property
    def Overs(self):
        return self.__overs
    @Overs.setter
    def Overs(self, d):
        self.__overs = d
        return self.__overs

    @property
    def Cur_over(self):
        return self.__cur_over
    @Cur_over.setter
    def Cur_over(self, d):
        self.__cur_over = d
        return self.__cur_over

    def score_of_one_ball(self, n):
        runs = 0
        wickets = 0
        if n in (0, 1, 2, 3, 4, 5, 6):
            runs += n
        elif str(n).lower() == "w":
            wickets += 1
        elif str(n).lower() == "wb":
            runs += 1
        elif str(n).lower() == "nb":
            runs += 1

        self.Runs += runs
        self.Wickets += wickets


# ---- Kivy UI ----
class OversApp(App):
    def build(self):
        self.overs = Overs(20)  # Example: 20 overs

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Labels to display scores
        self.label_score = Label(text=self.get_score_text(), font_size=20)
        layout.add_widget(self.label_score)

        # Input box for ball result
        self.input_ball = TextInput(hint_text="Enter ball result (0-6, w, nb, wb)", multiline=False)
        layout.add_widget(self.input_ball)

        # Button to update score
        btn_update = Button(text="Add Ball Result")
        btn_update.bind(on_press=self.update_score)
        layout.add_widget(btn_update)

        return layout

    def get_score_text(self):
        return f"Overs: {self.overs.Cur_over}/{self.overs.Overs}\nRuns: {self.overs.Runs}\nWickets: {self.overs.Wickets}"

    def update_score(self, instance):
        ball = self.input_ball.text.strip()
        if ball:
            # Convert numeric input
            try:
                ball = int(ball)
            except ValueError:
                pass

            self.overs.score_of_one_ball(ball)
            # Increment current over if needed
            if self.overs.Runs % 6 == 0:  # simple example
                self.overs.Cur_over += 1

            self.label_score.text = self.get_score_text()
            self.input_ball.text = ""


if __name__ == "__main__":
    OversApp().run()
