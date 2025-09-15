# Android-compatible version - NO input() functions
from overs_class import Overs
from batsman_class import Batsman
from bowler_class import Bowler
import sqlite3 as dbms

class CricketMatch:
    def __init__(self, team, total_overs, target=None, score=[]):
        self.Team = team
        self.Target = target
        self.Total_overs = total_overs
        self.Ov = Overs(total_overs)
        # Initialize with default players - can be set later via methods
        self.Bm1 = Batsman("Player 1", True)
        self.Bm2 = Batsman("Player 2", False)
        self.Bl = Bowler("Bowler 1")
        self.__score = score if score else []
        
    @property
    def Score(self):
        return sum(self.__score)
    
    @Score.setter
    def Score(self, s):
        self.__score.append(s)
        return self.__score
    
    # Method to set players (replaces input() calls)
    def set_batsmen(self, striker_name, non_striker_name):
        self.Bm1 = Batsman(striker_name, True)
        self.Bm2 = Batsman(non_striker_name, False)
    
    def set_bowler(self, bowler_name):
        # Check if bowler exists in database
        check_query = "SELECT Player, Runs, Dots, Overs, Wickets from Bowler WHERE Player = ?"
        self.create_tables(f'{self.Team}.db')
        try:
            con = dbms.connect(f'{self.Team}.db')
            cur = con.cursor()
            cur.execute(check_query, (bowler_name,))
            check = cur.fetchone()
            if check:
                self.Bl = Bowler(*check)
            else:
                self.Bl = Bowler(bowler_name)
            con.close()
        except:
            self.Bl = Bowler(bowler_name)
    
    # Rest of your properties remain the same
    @property
    def Team(self):
        return self.__team
    @Team.setter
    def Team(self, s):
        self.__team = s
        return self.__team
        
    @property
    def Target(self):
        return self.__target
    @Target.setter
    def Target(self, s):
        self.__target = s
        return self.__target
        
    @property
    def Total_overs(self):
        return self.__total_overs
    @Total_overs.setter
    def Total_overs(self, s):
        self.__total_overs = s
        return self.__total_overs
        
    @property
    def Bm1(self):
        return self.__bm1
    @Bm1.setter
    def Bm1(self, s):
        self.__bm1 = s
        return self.__bm1
        
    @property
    def Bm2(self):
        return self.__bm2
    @Bm2.setter
    def Bm2(self, s):
        self.__bm2 = s
        return self.__bm2
        
    @property
    def Bl(self):
        return self.__bl
    @Bl.setter
    def Bl(self, s):
        self.__bl = s
        return self.__bl
        
    @property
    def Ov(self):
        return self.__ov
    @Ov.setter
    def Ov(self, s):
        self.__ov = s
        return self.__ov
    
    def create_overs(self):
        ov = Overs(self.Total_overs)
        return ov
        
    def swap_striker(self, b1, b2):
        b1.Striker, b2.Striker = b2.Striker, b1.Striker
        return
        
    def one_ball(self, n):
        if str(n) in ('0','1','2','3','4','5','6'):
            self.Score = int(n)
            self.Bl.bowl_one(int(n))
            if self.Bm1.Striker:
                self.Bm1.bat_one(int(n))
                self.Bm1.Balls += 1
            elif self.Bm2.Striker:
                self.Bm2.bat_one(int(n))
                self.Bm2.Balls += 1
            self.Ov.score_of_one_ball(int(n))
            if int(n) % 2 != 0:
                self.swap_striker(self.Bm1, self.Bm2)
            
        elif str(n).lower() in ("wb", "nb"):
            self.Bl.bowl_one(n)
            self.Score = 1
            if self.Bm1.Striker:
                self.Bm1.bat_one(n)
                self.Bm1.Balls += 1
            elif self.Bm2.Striker:
                self.Bm2.bat_one(n)
                self.Bm2.Balls += 1
            self.Ov.score_of_one_ball(n)
            # For Android: assume extra ball is 0 runs (can be modified via UI)
            extra_runs = 0
            self.Bl.bowl_one(extra_runs)
            self.Score = extra_runs
            if self.Bm1.Striker:
                self.Bm1.bat_one(extra_runs)
            elif self.Bm2.Striker:
                self.Bm2.bat_one(extra_runs)
            if extra_runs % 2 != 0:
                self.swap_striker(self.Bm1, self.Bm2)
            self.Ov.score_of_one_ball(extra_runs)
        else:
            if str(n).lower() in ("w"):
                self.Bl.bowl_one(n)
                if self.Bm1.Striker:
                    self.Bm1.Balls += 1
                    self.add_batsman_to_db(self.Bm1)
                    # Create new batsman instead of input()
                    self.Bm1 = Batsman(f"New Batsman {len(self.__score)+1}", True)
                elif self.Bm2.Striker:
                    self.Bm2.Balls += 1
                    self.add_batsman_to_db(self.Bm2)
                    # Create new batsman instead of input()
                    self.Bm2 = Batsman(f"New Batsman {len(self.__score)+1}", False)
                self.Ov.score_of_one_ball(n)
                
    def one_over(self):
        if self.Target:
            for i in range(6):
                if self.Score > self.Target:
                    self.add_bowler_to_db(self.Bl)
                    self.add_over_to_db(self.Ov)
                    return
                # Ball input would come from UI, not input()
                # This method should be called from UI with ball value
                
        self.add_bowler_to_db(self.Bl)
        self.add_over_to_db(self.Ov)
        
    def all_overs(self):
        for i in range(self.Total_overs):
            self.Ov.Cur_over = i + 1
            self.one_over()
            if i < self.Total_overs - 1:
                # Create new bowler instead of input()
                self.Bl = Bowler(f"Bowler {i+2}")
                self.Ov = self.create_overs()
        self.add_batsman_to_db(self.Bm1)
        self.add_batsman_to_db(self.Bm2)
    
    # Database methods remain the same
    def add_bowler_to_db(self, b):
        player_ = f"{b.Name}"
        overs_ = f"{b.Overs}"
        dots_ = f"{b.Dots}"
        runs_ = f"{b.Runs}"
        wickets_ = f"{b.Wickets}"
        er_ = f"{b.Er}"
        check_query = "SELECT Player, Runs, Dots, Overs, Wickets, Economy_Rate from Bowler WHERE Player = ?"
        query = "INSERT INTO Bowler(Player, Runs, Dots, Overs, Wickets, Economy_Rate) VALUES (?, ?, ?, ?, ?, ?)"
        update_query = "UPDATE Bowler SET Runs = ?, Dots = ?, Overs = ?, Wickets = ?, Economy_Rate = ? WHERE Player = ?"
        self.create_tables(f'{self.Team}.db')
        try:
            con = dbms.connect(f'{self.Team}.db')
            cur = con.cursor()
            cur.execute(check_query, (player_,))
            check = cur.fetchone()
            if check:
                cur.execute(update_query, (runs_, dots_, overs_, wickets_, er_, player_))
            else:
                cur.execute(query, (player_, runs_, dots_, overs_, wickets_, er_))
            con.commit()
            cur.close()
            con.close()
        except Exception as e:
            print(f"Database error: {e}")
        
    def add_batsman_to_db(self, b):
        player_ = f"{b.Name}"
        balls_ = f"{b.Balls}"        
        runs_ = f"{b.Runs}"
        fours_ = f"{b.Fours}"
        sixes_ = f"{b.Sixes}"
        sr_ = f"{b.Sr}"
        query = "INSERT INTO Batsmen(player_name, runs, balls, fours, sixes, strike_rate) VALUES (?, ?, ?, ?, ?, ?)"
        self.create_tables(f'{self.Team}.db')
        try:
            con = dbms.connect(f'{self.Team}.db')
            cur = con.cursor()
            cur.execute(query, (player_, runs_, balls_, fours_, sixes_, sr_))
            con.commit()
            cur.close()
            con.close()
        except Exception as e:
            print(f"Database error: {e}")
        
    def add_over_to_db(self, o):
        over_ = f"Over {o.Cur_over}"       
        runs_ = f"{o.Runs}"
        wickets_ = f"{o.Wickets}"
        query = "INSERT INTO Overs(over, runs, wickets) VALUES (?, ?, ?)"
        self.create_tables(f'{self.Team}.db')
        try:
            con = dbms.connect(f'{self.Team}.db')
            cur = con.cursor()
            cur.execute(query, (over_, runs_, wickets_))
            con.commit()
            cur.close()
            con.close()
        except Exception as e:
            print(f"Database error: {e}")
        
    def create_tables(self, db_name):
        try:
            con = dbms.connect(db_name)
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS Bowler (Player TEXT, Runs REAL, Dots INT, Overs INT, Wickets INT, Economy_Rate REAL)")
            cur.execute("CREATE TABLE IF NOT EXISTS Batsmen (player_name TEXT,runs INT, balls INT,fours INT,sixes INT,strike_rate REAL)")
            cur.execute("CREATE TABLE IF NOT EXISTS Overs (over INT,runs INT,wickets INT)")
            con.commit()
            cur.close()
            con.close()
        except Exception as e:
            print(f"Database creation error: {e}")