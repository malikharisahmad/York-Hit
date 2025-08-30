import sqlite3 as dbms
from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label


class CricketMatchDisplay(TabbedPanel):
    def __init__(self, db1, db2, **kwargs):
        super().__init__(**kwargs)
        self.do_default_tab = False  # Disable default empty tab
        self.databases = [db1, db2]

        tables = self.get_tables_from_databases(self.databases)

        for table in tables:
            tab = TabbedPanelItem(text=f"Team {table.title()}")
            grid = GridLayout(cols=5, padding=5, spacing=5, size_hint_y=None)
            grid.bind(minimum_height=grid.setter('height'))

            self.display_data(grid, table)
            tab.add_widget(grid)
            self.add_widget(tab)

    def get_tables_from_databases(self, databases):
        all_tables = set()
        for db_name in databases:
            con = dbms.connect(db_name)
            cur = con.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cur.fetchall()
            all_tables.update(table[0] for table in tables)
            con.close()
        return list(all_tables)

    def display_data(self, layout, table):
        columns = self.get_columns_from_table(self.databases[0], table)

        # Add headers
        for col in columns:
            layout.add_widget(Label(text=col.title(), bold=True))

        team_runs = {db_name: 0 for db_name in self.databases}

        for db_index, db_name in enumerate(self.databases):
            con = dbms.connect(db_name)
            cur = con.cursor()
            cur.execute(f"SELECT * FROM {table}")
            data = cur.fetchall()

            # Add team name row
            layout.add_widget(Label(text=f"Team {db_name.rsplit('.', 1)[0]}", bold=True))
            for _ in range(len(columns) - 1):
                layout.add_widget(Label(text=""))

            # Add rows of data
            for row in data:
                for val in row:
                    layout.add_widget(Label(text=str(val)))
                team_runs[db_name] += int(row[1])  # Assuming column[1] is runs/overs

            con.close()

            # Totals row
            layout.add_widget(Label(text=f"Totals: {team_runs[db_name]}", bold=True))
            for _ in range(len(columns) - 1):
                layout.add_widget(Label(text=""))

            # Empty row between teams
            if db_index == 0 and len(self.databases) > 1:
                for _ in range(len(columns)):
                    layout.add_widget(Label(text=""))

        # Winner row
        winner = self.databases[0] if team_runs[self.databases[0]] > team_runs[self.databases[1]] else self.databases[1]
        winner_name = f"Team {winner.rsplit('.', 1)[0]} Wins!"

        layout.add_widget(Label(text=winner_name, bold=True))
        for _ in range(len(columns) - 1):
            layout.add_widget(Label(text=""))

    def get_columns_from_table(self, db_name, table):
        con = dbms.connect(db_name)
        cur = con.cursor()
        cur.execute(f"PRAGMA table_info({table})")
        columns = cur.fetchall()
        con.close()
        return [col[1] for col in columns]


class CricketApp(App):
    def build(self):
        return CricketMatchDisplay("team1.db", "team2.db")


if __name__ == "__main__":
    CricketApp().run()
